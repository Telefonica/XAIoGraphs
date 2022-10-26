from abc import ABCMeta, abstractmethod
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from absl import logging

from xaiographs.common.constants import ID, MEAN, NODE_NAME, NODE_WEIGHT, RANK, SHAP_SUFFIX, TARGET


class Explainer(metaclass=ABCMeta):
    _DEFAULT_TARGET_COLS = ['target']
    _DF_EXPLANATION = 'df_explanation'
    _EPS_ERROR = 0.000001
    _PHI0 = 'phi0'
    _QUALITY_MEASURE = 'quality_measure'
    _SHAPLEY_VALUES = 'shapley_values'
    _TOP1_TARGET = 'top1_target'

    @abstractmethod
    def train(self, df: pd.DataFrame, target_cols: List[str]):
        raise NotImplementedError

    def local_explain(self, df_2_explain: pd.DataFrame, target_cols: List[str],
                      **params) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        """
        This function encapsulates the whole process of local explainability: it starts by aggregating features on the
        DataFrame to explain, then calculates Shapley Values and then dissagregation is done so that prediction
        quality can be calculated on the original data

        :param: df_2_explain:   Pandas DataFrame to be explained. Its data has been previously discretized.
        :param: target_cols:    List of strings with all column names identified as target
        :return: Tuple[pd.Dataframe, ]:
        """
        df_aggregated = Explainer.__aggregate(df_2_explain=df_2_explain, target_cols=target_cols)

        shapley_dict = self.calculate_shapley_values(df_aggregated=df_aggregated,
                                                     target_cols=target_cols,
                                                     **params)
        return Explainer.__disaggregate(phi0=shapley_dict[Explainer._PHI0],
                                        shapley_values=shapley_dict[Explainer._SHAPLEY_VALUES],
                                        df_2_explain=df_2_explain,
                                        df_aggregated=df_aggregated,
                                        target_cols=target_cols)

    @abstractmethod
    def global_explain(self, **params):
        raise NotImplementedError

    @staticmethod
    def __aggregate(df_2_explain: pd.DataFrame, target_cols: List[str]) -> pd.DataFrame:
        """
        This function processes the DataFrame provided as parameter so that all its features but the ones in
        target_cols parameter, are aggregated and the means of those in target_cols are computed. Columns are renamed
        accordingly

        :param: df_2_explain: Pandas DataFrame to which the operations described above will be applied
        :param: target_cols:  List of strings with all column names identified as target
        :return:              Pandas DataFrame resulting after applying aforementioned transformations
        """
        df_aggregated = (df_2_explain.groupby([c for c in list(df_2_explain.columns) if c not in target_cols]).agg(
            {c: [MEAN] for c in target_cols}).reset_index())
        df_aggregated.columns = ['_'.join(col).strip() if col[1] != '' else col[0] for col in
                                 df_aggregated.columns]
        return df_aggregated.rename(columns={'_'.join([c, MEAN]): c for c in target_cols})

    @abstractmethod
    def calculate_shapley_values(self, df_aggregated: pd.DataFrame, target_cols: List[str], **params) -> Dict:
        raise NotImplementedError

    @staticmethod
    def sanity_check(ground_truth: np.ndarray, prediction: np.ndarray, target_cols: List[str], scope: str):
        error = np.abs(ground_truth - prediction) > Explainer._EPS_ERROR
        for i, target_col in enumerate(target_cols):
            logging.info('Number of detected discrepancies (original model prediction != SHAP prediction) '
                         'for target {} in the {} dataset: {}'.format(target_col, scope, sum(error[:, i])))

    @staticmethod
    def __disaggregate(phi0: np.ndarray, shapley_values: np.ndarray, df_2_explain: pd.DataFrame,
                       df_aggregated: pd.DataFrame, target_cols: List[str]) -> Dict[str, Union[pd.DataFrame,
                                                                                               np.ndarray]]:
        """
        This function takes care of propagating the calculated Shapley Values to the DataFrame to be explained (the
        disaggregated DataFrame). A quality measure featuring the divergence between the ground truth and the Shapley
        based prediction is included in the DataFrame to explain too.

        :param: phi0:           Numpy array containing the baseline (prediction when no features are provided) for each
                                target
        :param: shapley_values: Numpy matrix containing the Shapley Values calculated for each aggregated DataFrame row
                                for each feature and for each target. Shape (n_rows x n_features x n_targets)
        :param: df_2_explain:   Pandas DataFrame to be explained
        :param: df_aggregated:  Pandas DataFrame whose features have been aggregated and its targets have been averaged
        :param: target_cols:    List of strings with all column names identified as target
        :return:                Dictionary with two elements: the DataFrame to explain, containing the Shapley values
                                and the quality measure. The second elements are the adapted Shapley values which are
                                calculated by taking into account the quality measure
        """

        # For each feature column and target column pair a new column is generated to store the corresponding
        # Shapley value
        c_shap_columns = []
        for i, c in enumerate(df_aggregated.columns):
            if c not in target_cols:
                for j, target_col in enumerate(target_cols):
                    df_aggregated['{}_{}{}'.format(target_col, c, SHAP_SUFFIX)] = shapley_values[:, i, j]
                    c_shap_columns.append('{}_{}{}'.format(target_col, c, SHAP_SUFFIX))

        # DataFrame to be explained is left joined with the normalized DataFrame (already containing columns with the
        # computed Shapley values). The join is on the features of the DataFrame to be explained
        df_aggregated_features = df_aggregated.drop(target_cols, axis=1)
        column_names = [c for c in df_2_explain.columns if c not in target_cols]
        df_explanation = pd.merge(df_2_explain, df_aggregated_features, on=column_names, how='left')

        # Normalization trick:
        #   Ground truth values are retrieved from df_explanation
        y = df_explanation[target_cols].values

        #   Columns containing shapley values are reshaped: number of rows x number of features x number of targets
        calculated_shapley = df_explanation[c_shap_columns].values.reshape(y.shape[0],
                                                                           shapley_values.shape[1],
                                                                           shapley_values.shape[2])

        #   Predictions calculated as baseline plus the summation of the calculated Shapley values
        y_hat: np.ndarray = phi0 + np.sum(calculated_shapley, axis=1)

        # Difference between ground truth and predictions
        quality_measure: np.ndarray = (y - y_hat)

        # Adapted Shapley results from adding the calculated shapley plus the quality measure divided by the number
        # of features
        adapted_shapley: np.ndarray = calculated_shapley + np.expand_dims(quality_measure / calculated_shapley.shape[1],
                                                                          axis=1)
        reshaped_adapted_shapley = np.transpose(adapted_shapley, (0, 2, 1)).reshape(adapted_shapley.shape[0], -1)
        for i, c in enumerate(c_shap_columns):
            df_explanation[c] = reshaped_adapted_shapley[:, i]

        quality_measure_columns = []
        adapted_shapley_mask = {}
        for j, target_col in enumerate(target_cols):
            quality_measure_column = '{}_{}'.format(target_col, Explainer._QUALITY_MEASURE)
            df_explanation[quality_measure_column] = quality_measure[:, j]
            quality_measure_columns.append(quality_measure_column)
            target_mask = []
            for c_shap_col in c_shap_columns:
                if not c_shap_col.startswith(target_col):
                    target_mask.append(False)
                else:
                    target_mask.append(True)
            adapted_shapley_mask[target_col] = target_mask

        # Data is formatted for the sanity check
        y = df_explanation[target_cols].values
        y_hat_reduced = phi0 + np.sum(np.transpose(
            df_explanation[c_shap_columns].values.reshape(-1, adapted_shapley.shape[2], adapted_shapley.shape[1]),
            (0, 2, 1)), axis=1)
        Explainer.sanity_check(ground_truth=y, prediction=y_hat_reduced, target_cols=target_cols, scope='original')

        df_explanation.to_pickle('/home/cx02747/Utils/df_explanation.pkl')
        # If local_dataset_reliability.csv must be generated the following steps must be followed
        top1_argmax = np.argmax(df_explanation[target_cols].values, axis=1)
        top1_target = np.array([target_cols[am] for am in top1_argmax])
        float_features = df_explanation[column_names].select_dtypes('float')
        df_local_feature_values = df_explanation[column_names].reset_index().values
        # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
        #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con valores de
        #  ese tipo
        for i, feature_col in enumerate(column_names):
            if feature_col in float_features:
                df_local_feature_values[:, i+1] = np.around(df_local_feature_values[:, i+1].astype('float'), decimals=2)

        df_local_quality_measure_values = df_explanation[quality_measure_columns].values
        pd.DataFrame(np.concatenate((df_local_feature_values,
                                     top1_target.reshape(-1, 1),
                                     df_local_quality_measure_values[
                                         np.arange(df_local_quality_measure_values.shape[0]), top1_argmax].reshape(-1,
                                                                                                                   1)),
                                    axis=1),
                     columns=[ID] + column_names + [TARGET] + [
                         Explainer._QUALITY_MEASURE]).to_csv('/home/cx02747/Utils/df3.csv', sep=',', index=False)

        # If local_explainability.csv must be generated the following steps must be followed
        adapted_shapley_by_target = []
        for target_value in top1_target:
            adapted_shapley_by_target.append(adapted_shapley_mask[target_value])
        pd.DataFrame(np.concatenate((df_explanation.reset_index().index.values.reshape(-1, 1),
                                     df_explanation[c_shap_columns].values[
                                         np.array(adapted_shapley_by_target)].reshape(len(df_explanation), -1),
                                     top1_target.reshape(-1, 1)),
                                    axis=1), columns=[ID] + column_names + [TARGET]).to_csv(
            '/home/cx02747/Utils/df4.csv', sep=',', index=False)

        # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
        #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con valores de
        #  ese tipo
        # if local_explainability_graph_nodes_weights.csv must be generated the following steps must be followed
        all_columns = list(df_explanation.reset_index().columns)
        df_explanation_values = df_explanation.reset_index().values
        graph_nodes_values = []
        for i, row in enumerate(df_explanation_values):
            for feature_col in column_names:
                feature_value_raw = row[all_columns.index(feature_col)]
                if feature_col in float_features:
                    feature_value = '_'.join([feature_col, "{:.02f}".format(feature_value_raw)])
                else:
                    feature_value = '_'.join([feature_col, feature_value_raw])
                feature_target_shap_col = '{}_{}{}'.format(top1_target[i], feature_col, SHAP_SUFFIX)
                graph_nodes_values.append([row[0], feature_value, row[all_columns.index(feature_target_shap_col)],
                                           top1_target[i]])

        df_graph_nodes = pd.DataFrame(graph_nodes_values, columns=[ID, NODE_NAME, NODE_WEIGHT, TARGET])
        df_graph_nodes[RANK] = df_graph_nodes.groupby(ID)[NODE_WEIGHT].rank(method='dense',
                                                                            ascending=False).astype(int)
        df_graph_nodes.sort_values(by=[ID, RANK]).to_csv('/home/cx02747/Utils/df5.csv',
                                                         columns=[ID, NODE_NAME, NODE_WEIGHT,
                                                                  RANK, TARGET], sep=',', index=False)

        # if global_explainability_graph_nodes_weights.csv must be generated the following steps must be followed
        node_names = []
        for row in df_explanation[column_names].values:
            for i, feature_col in enumerate(column_names):
                feature_value_raw = row[i]
                if feature_col in float_features:
                    feature_value = '_'.join([feature_col, "{:.02f}".format(feature_value_raw)])
                else:
                    feature_value = '_'.join([feature_col, feature_value_raw])
                node_names.append(feature_value)

        df_global_graph_nodes = pd.DataFrame(
            np.concatenate((np.tile(np.array(target_cols), len(df_explanation) * len(column_names)).reshape(-1, 1),
                            np.repeat(np.array(node_names), len(target_cols)).reshape(-1, 1),
                            np.abs(df_explanation[c_shap_columns].values).reshape(-1, 1)), axis=1),
            columns=[TARGET, NODE_NAME, NODE_WEIGHT])
        df_global_graph_nodes[NODE_WEIGHT] = pd.to_numeric(df_global_graph_nodes[NODE_WEIGHT]).abs()
        df_global_graph_nodes_aggregated = df_global_graph_nodes.groupby([TARGET, NODE_NAME]).mean().reset_index()
        df_global_graph_nodes_aggregated[RANK] = df_global_graph_nodes_aggregated.groupby([TARGET])[NODE_WEIGHT].rank(
            method='dense', ascending=False).astype(int)
        df_global_graph_nodes_aggregated.sort_values(by=[TARGET, RANK]).to_csv('/home/cx02747/Utils/df6.csv',
                                                                               sep=',', index=False)

        return {
            Explainer._DF_EXPLANATION: df_explanation,
            Explainer._SHAPLEY_VALUES: adapted_shapley,
            Explainer._TOP1_TARGET: top1_target
        }
