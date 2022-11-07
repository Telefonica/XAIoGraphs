from typing import Any, Dict, List

import numpy as np
import pandas as pd

from xaiographs.common.constants import BIN_WIDTH_FEATURE_WEIGHT, BIN_WIDTH_NODE_WEIGHT, COMMA_SEP, FEATURE_IMPORTANCE,\
    FEATURE_NAME, FEATURE_WEIGHT, ID, MAX_FEATURE_WEIGHT, MAX_NODE_WEIGHT, MIN_FEATURE_WEIGHT, MIN_NODE_WEIGHT, \
    N_BINS_FEATURE_WEIGHT, N_BINS_NODE_WEIGHT, NODE_IMPORTANCE, NODE_NAME, NODE_WEIGHT, NUM_FEATURES, QUALITY_MEASURE,\
    RANK, SHAP_SUFFIX, TARGET


def save_global_target_explained_info(df_shapley_values: pd.DataFrame, feature_cols: List[str],
                                      target_cols: List[str], top1_targets: List[str]):
    """
    This functions performs the necessary transformations on the resulting Shapley values so that the following files
    are generated: global_target_explainability.csv (deprecated) and global_explainability.csv

    :param df_shapley_values: Pandas DataFrame containing the calculated Shapley values
    :param feature_cols:      List of strings containing the column names for the features
    :param target_cols:       List of strings containing the column names for the target/s
    :param top1_targets:      List of strings containing the top1_target for each row
    """

    # A boolean mask is generated from the top1_targets, this mask is then applied to the Shapley values DataFrame so
    # that only those values related to each top1 target, are taken into account. The resulting matrix does have as
    # many rows as observations and as many columns as features
    target_mask = np.repeat(pd.get_dummies(pd.Series(top1_targets)).values, len(feature_cols), axis=0).reshape(-1, len(
        feature_cols), len(target_cols)).astype('bool')
    top1_shapley = df_shapley_values[target_mask].reshape(-1, len(feature_cols))

    # Pandas DataFrame is built from the matrix and an additional column with the target names is prepended
    top1_shapley_features = pd.DataFrame(np.concatenate((np.array(top1_targets).reshape(-1, 1), top1_shapley), axis=1),
                                         columns=[TARGET] + feature_cols)

    # Column mean is calculated groping by target. The result does have as many rows as targets and as many columns as
    # features
    top1_shapley_features = top1_shapley_features.apply(pd.to_numeric, errors='ignore').groupby(
        TARGET).mean().reset_index()
    top1_shapley_features.to_csv(path_or_buf='/home/cx02747/Utils/deprecated_global_target_explainability.csv',
                                 sep=COMMA_SEP, index=False)

    # To generate global_explainability.csv, the targets probabilities are computed and each of the rows of the previous
    # DataFrame is multiplied by the corresponding probability. Finally, mean is computed for the resulting columns
    target_probs = np.array([top1_targets.count(target) for target in target_cols]) / len(top1_targets)
    df_global_explainability = pd.DataFrame(np.concatenate((np.array(feature_cols).reshape(-1, 1),
                                                            (target_probs.reshape(-1, 1) * top1_shapley_features.drop(
                                                                'target', axis=1).values).mean(axis=0).reshape(
                                                                -1, 1)), axis=1),
                                            columns=[FEATURE_NAME, FEATURE_IMPORTANCE]).sort_values(
        by=[FEATURE_IMPORTANCE], ascending=False)

    # From the previous results (FEATURE_IMPORTANCE), the FEATURE_WEIGHT (the equivalence in pixels) are calculated
    df_global_explainability[FEATURE_WEIGHT] = pd.cut(df_global_explainability[FEATURE_IMPORTANCE].astype('float'),
                                                      bins=N_BINS_FEATURE_WEIGHT,
                                                      labels=list(range(
                                                          MIN_FEATURE_WEIGHT,
                                                          MAX_FEATURE_WEIGHT + BIN_WIDTH_FEATURE_WEIGHT,
                                                          BIN_WIDTH_FEATURE_WEIGHT)))
    df_global_explainability.to_csv(path_or_buf='/home/cx02747/Utils/global_explainability.csv', sep=COMMA_SEP,
                                    index=False)


def save_graph_nodes_info(df_explained: pd.DataFrame, feature_cols: List[str], float_features: List[str],
                          top1_targets: np.ndarray, sample_ids: List[Any]):
    """
    This function is intended to compute the information related to the graph nodes

    :param df_explained:    Pandas DataFrame containing the DataFrame to be explained including the calculated
                            Shapley values
    :param feature_cols:    List of strings containing the column names for the features
    :param float_features:  List of strings containing the column names for the float type features
    :param top1_targets:    List of strings containing the top1_target for each row
    :param sample_ids:      List of ids which will be part of the sample
    """
    # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
    #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con valores de
    #  ese tipo
    all_columns = list(df_explained.columns)
    df_explanation_values = df_explained.values
    graph_nodes_values = []

    # Each feature_value pair is computed (NODE_NAME) and the Shapley value associated to its top1 target is retrieved
    # as the NODE_IMPORTANCE
    for i, row in enumerate(df_explanation_values):
        for feature_col in feature_cols:
            feature_value_raw = row[all_columns.index(feature_col)]
            if feature_col in float_features:
                feature_value = '_'.join([feature_col, "{:.02f}".format(feature_value_raw)])
            else:
                feature_value = '_'.join([feature_col, feature_value_raw])
            feature_target_shap_col = '{}_{}{}'.format(top1_targets[i], feature_col, SHAP_SUFFIX)
            graph_nodes_values.append([row[0], feature_value, row[all_columns.index(feature_target_shap_col)],
                                       top1_targets[i]])

    df_local_graph_nodes = pd.DataFrame(graph_nodes_values, columns=[ID, NODE_NAME, NODE_IMPORTANCE, TARGET])

    # Rank is calculated based on NODE_IMPORTANCE and grouping by ID
    df_local_graph_nodes[RANK] = df_local_graph_nodes.groupby(ID)[NODE_IMPORTANCE].rank(method='dense',
                                                                                        ascending=False).astype(int)

    # From the previous results (NODE_IMPORTANCE), the NODE_WEIGHT (the equivalence in pixels) are calculated
    df_local_graph_nodes[NODE_WEIGHT] = pd.cut(df_local_graph_nodes[NODE_IMPORTANCE].abs(),
                                               bins=N_BINS_NODE_WEIGHT,
                                               labels=list(range(
                                                   MIN_NODE_WEIGHT,
                                                   MAX_NODE_WEIGHT + BIN_WIDTH_NODE_WEIGHT,
                                                   BIN_WIDTH_NODE_WEIGHT)))
    persist_sample(df_local_graph_nodes.sort_values(by=[ID, RANK]), sample_ids=sample_ids,
                   path='/home/cx02747/Utils/local_graph_nodes.csv',
                   columns=[ID, NODE_NAME, NODE_IMPORTANCE, NODE_WEIGHT, RANK, TARGET])

    # To generate global_graph_nodes.csv, local graph nodes NODE_IMPORTANCE is averaged grouping by TARGET and NODE_NAME
    df_local_graph_nodes[NODE_IMPORTANCE] = df_local_graph_nodes[NODE_IMPORTANCE].abs()
    df_global_graph_nodes_aggregated = df_local_graph_nodes[[TARGET, NODE_NAME, NODE_IMPORTANCE]].groupby(
        [TARGET, NODE_NAME]).mean().reset_index()

    # Rank is calculated based on NODE_IMPORTANCE and grouping by TARGET
    df_global_graph_nodes_aggregated[RANK] = df_global_graph_nodes_aggregated.groupby([TARGET])[
        NODE_IMPORTANCE].rank(method='dense', ascending=False).astype(int)

    # From the previous results (NODE_IMPORTANCE), the NODE_WEIGHT (the equivalence in pixels) are calculated
    df_global_graph_nodes_aggregated[NODE_WEIGHT] = pd.cut(df_global_graph_nodes_aggregated[NODE_IMPORTANCE],
                                                           bins=N_BINS_NODE_WEIGHT,
                                                           labels=list(range(
                                                               MIN_NODE_WEIGHT,
                                                               MAX_NODE_WEIGHT + BIN_WIDTH_NODE_WEIGHT,
                                                               BIN_WIDTH_NODE_WEIGHT)))

    # Results are sorted by TARGET and RANK
    df_global_graph_nodes_aggregated.sort_values(by=[TARGET, RANK], inplace=True)
    df_global_graph_nodes_aggregated.to_csv(path_or_buf='/home/cx02747/Utils/global_graph_nodes.csv',
                                            columns=[TARGET, NODE_NAME, NODE_IMPORTANCE, NODE_WEIGHT, RANK],
                                            sep=',', index=False)
    df_global_graph_nodes_aggregated[[TARGET, RANK]].drop_duplicates(subset=[TARGET], keep='last').rename(
        columns={RANK: NUM_FEATURES}).to_csv(path_or_buf='/home/cx02747/Utils/global_graph_description.csv',
                                             columns=[TARGET, NUM_FEATURES], sep=',', index=False)


def save_local_explainability_info(df_explained: pd.DataFrame, feature_cols: List[str], c_shap_columns: List[str],
                                   top1_targets: np.ndarray, adapted_shapley_mask: Dict[str, List[bool]],
                                   sample_ids: List[Any]):
    """


    :param df_explained:            Pandas DataFrame containing the DataFrame to be explained including the calculated
                                    Shapley values
    :param feature_cols:            List of strings containing the column names for the features
    :param c_shap_columns:          List of strings containing the column names for the Shapley values (there'll be
                                    one column per feature_target)
    :param top1_targets:            List of strings containing the top1_target for each row
    :param adapted_shapley_mask:    List of boolean masks in order to pick up the adapted Shapley values for each target
    :param sample_ids:              List of ids which will be part of the sample
    """
    adapted_shapley_by_target = []
    for target_value in top1_targets:
        adapted_shapley_by_target.append(adapted_shapley_mask[target_value])
    persist_sample(pd.DataFrame(np.concatenate((df_explained[ID].values.reshape(-1, 1),
                                                df_explained[c_shap_columns].values[
                                                    np.array(adapted_shapley_by_target)].reshape(
                                                    len(df_explained), -1),
                                                top1_targets.reshape(-1, 1)), axis=1),
                                columns=[ID] + feature_cols + [TARGET]), sample_ids=sample_ids,
                   path='/home/cx02747/Utils/local_explainability.csv')


def save_local_dataset_reliability(df_explained: pd.DataFrame, feature_cols: List[str], float_features: List[str],
                                   quality_measure_columns: List[str], top1_targets: np.ndarray,
                                   top1_argmax: np.ndarray, sample_ids: List[Any]):
    """


    :param df_explained:            Pandas DataFrame containing the DataFrame to be explained including the calculated
                                    Shapley values
    :param feature_cols:            List of strings containing the column names for the features
    :param float_features:          List of strings containing the column names for the float type features
    :param quality_measure_columns: List of strings containing the column names (one per target) providing the
                                    difference between the ground truth and the Shapley based prediction
    :param top1_targets:            List of strings containing the top1_target for each row
    :param top1_argmax:             Numpy array containing the indices representing the top1 target for each row
    :param sample_ids:              List of ids which will be part of the sample
    """
    df_local_feature_values = df_explained[[ID] + feature_cols].values
    # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
    #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con valores de
    #  ese tipo
    for i, feature_col in enumerate(feature_cols):
        if feature_col in float_features:
            df_local_feature_values[:, i + 1] = np.around(df_local_feature_values[:, i + 1].astype('float'), decimals=2)

    df_local_quality_measure_values = df_explained[quality_measure_columns].values
    persist_sample(pd.DataFrame(np.concatenate((df_local_feature_values, top1_targets.reshape(-1, 1),
                                                np.round(df_local_quality_measure_values[
                                                             np.arange(
                                                                 df_local_quality_measure_values.shape[
                                                                     0]), top1_argmax],
                                                         decimals=2).reshape(-1, 1)), axis=1),
                                columns=[ID] + feature_cols + [TARGET] + [QUALITY_MEASURE]),
                   sample_ids=sample_ids, path='/home/cx02747/Utils/local_dataset_reliability.csv')


def sample_by_target(ids: np.ndarray, top1_targets: np.ndarray, num_samples: int, target_probs: List[float],
                     target_cols: List[str], target_col: str = TARGET) -> List[Any]:
    """
    This function generates a list of ids which will be used to limit the number of rows which will be persisted

    :param ids:             Numpy array consisting of the Pandas DataFrame columns values containing the id on which
                            samples will be computed
    :param top1_targets:    List of strings containing the top1 target for each row. Sampling will be calculated so
                            that the target ratio will be kept, this parameter allows filtering by target
    :param num_samples:     Integer representing the number of samples which will be calculated
    :param target_probs:    List of float containing the probability for each target. It's used to calculate the ratio
                            for each target
    :param target_cols:     List of strings containing the possible targets
    :param target_col:      String representing the target col name (default: 'target')
    :return:
    """

    # A Pandas DataFrame containing a first column representing the id and a second column with the top1 target for that
    # row
    df_ids_target = pd.DataFrame(np.concatenate((ids.reshape(-1, 1), top1_targets.reshape(-1, 1)), axis=1),
                                 columns=[ID, target_col])

    # For each possible target, rows are filtered by that target and the number of ids to retrieve is computed by using
    # the target probability and the number of requested samples
    sample_ids = []
    for target_prob, target_col_value in zip(target_probs, target_cols):
        n_samples_by_target = int(num_samples * target_prob)
        sample_ids += df_ids_target[df_ids_target[target_col] == target_col_value][ID].sample(
            n=n_samples_by_target).values.tolist()

    return sample_ids


def persist_sample(df: pd.DataFrame, sample_ids: List[Any], path: str, columns: List[str] = None, sep: str = COMMA_SEP,
                   keep_index: bool = False, id_type: str = 'str'):
    """
    This function takes care of sampling data and then persisting the resulting sample

    :param df:          Pandas DataFrame from which the sample is taken
    :param sample_ids:  List of ids which will be part of the sample
    :param path:        String representing the path where the data will be persisted
    :param columns:     List of strings containing the names of the columns to be persisted (default: None, all columns
                        are persisted)
    :param sep:         String representing the separator used in the CSV file used to persist data (default: ',')
    :param keep_index:  Boolean indicating whether DataFrame index must be persisted or not (default: False)
    :param id_type:     String indicating the type of the sample ids (default: str)
    :return:
    """
    columns = df.columns if columns is None else columns
    df[df[ID].astype(id_type).isin(sample_ids)].to_csv(path_or_buf=path, columns=columns, sep=sep, index=keep_index)
