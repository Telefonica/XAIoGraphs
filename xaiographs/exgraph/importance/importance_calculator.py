from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from xaiographs.common.constants import FEATURE_IMPORTANCE, FEATURE_NAME, ID, IMPORTANCE_SUFFIX, MEAN, \
    NODE_IMPORTANCE, NODE_NAME, RANK, TARGET
from xaiographs.common.utils import FeaturesInfo, TargetInfo, filter_by_ids


class ImportanceCalculator(metaclass=ABCMeta):
    """
    This class is intended to be a template to develop different implementations for importance calculation. Some
    methods are abstract, so that they must be implemented depending on the strategy used to calculate importance and
    some other are given, representing those tasks which stay always the same, independently of the strategy
    """
    _DEFAULT_TARGET_COLS = ['target']
    _DF_EXPLANATION = 'df_explanation'
    _EPS_ERROR = 0.000001
    _PHI0 = 'phi0'
    _QUALITY_MEASURE = 'quality_measure'
    _IMPORTANCE_VALUES = 'importance_values'
    _TOP1_TARGET = 'top1_target'

    def __init__(self, df: pd.DataFrame, sample_ids_mask_2_explain: np.ndarray, feature_cols: List[str],
                 target_cols: List[str], train_size: float, train_stratify: bool):
        """
        Constructor method for ImportanceCalculator

        :param df:                          Pandas DataFrame used to "train" the calculator
        :param sample_ids_mask_2_explain:   Numpy array mask, which will be applied to the explanation pandas DataFrame
                                            right after global explanation is computed
        :param feature_cols:                List of strings containing the column names for the features
        :param target_cols:                 List of strings containing all column names identified as target
        :param train_size:                  Float indicating the percentage of the pandas DataFrame that will be used
                                            to train the calculator
        :param train_stratify:              Boolean indicating whether target columns proportions will be taken into
                                            account when splitting the data (if train_size > 0.0)
        """
        print("INFO: Instantiating ImportanceCalculator:")
        if train_size > 0.0:
            print("INFO:    train_size: {}".format(train_size))
            if train_stratify:
                print("INFO:    stratifying on target: {}".format(target_cols))
                df_train, _ = train_test_split(df, train_size=train_size, stratify=df[target_cols])
            else:
                df_train, _ = train_test_split(df, train_size=train_size)

            self.df_train = df_train.copy()
        else:
            print("INFO:    the whole dataset will be used to train")
            self.df_train = df.copy()
        self.df_train.drop(ID, axis=1, inplace=True)
        self.df_2_explain = df
        self.feature_cols = feature_cols
        self.sample_ids_mask_2_explain = sample_ids_mask_2_explain
        self.target_cols = target_cols

    @abstractmethod
    def calculate_importance_values(self, df_aggregated: pd.DataFrame, target_cols: List[str], **params) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def train(self):
        raise NotImplementedError

    @staticmethod
    def __compute_global_explainability(global_target_explainability: pd.DataFrame, feature_cols: List[str],
                                        target_cols: List[str], top1_targets: np.ndarray) -> pd.DataFrame:
        """
        This function computes the mean of each feature importance throughout all the targets

        :param global_target_explainability: Pandas DataFrame containing the mean of each feature importance for each
                                             target
        :param feature_cols:                 List of strings containing the column names for the features
        :param target_cols:                  List of strings containing the column names for the target/s
        :param top1_targets:                 Numpy array containing the top1_target for each row
        :return:                             Pandas DataFrame containing the mean of each feature importance throughout
                                             all the targets
        """
        # To generate global_explainability.csv, the targets probabilities are computed and each of the rows of the
        # previous DataFrame is multiplied by the corresponding probability. Finally, mean is computed for the resulting
        # columns
        target_probs = np.array([top1_targets.tolist().count(target) for target in target_cols]) / len(
            top1_targets)

        return pd.DataFrame(np.concatenate((np.array(feature_cols).reshape(-1, 1),
                                            (target_probs.reshape(-1,
                                                                  1) * global_target_explainability.drop(
                                                TARGET, axis=1).values).mean(axis=0).reshape(
                                                -1, 1)), axis=1),
                            columns=[FEATURE_NAME, FEATURE_IMPORTANCE]).sort_values(
            by=[FEATURE_IMPORTANCE], ascending=False)

    @staticmethod
    def __compute_global_graph_nodes_importance(df_explained: pd.DataFrame, feature_cols: List[str],
                                                float_features: List[str], top1_targets: np.ndarray) -> pd.DataFrame:
        """
        This function computes the global graph nodes information related to the calculation of the features importance

        :param df_explained:    Pandas DataFrame which has been explained
        :param feature_cols:    List of strings containing the column names for the features
        :param float_features:  List of strings containing the column names for the float type features
        :param top1_targets:    Numpy array containing the top1_target for each row
        :return:                Pandas DataFrame containing the graph nodes global information, related to the
                                importance calculation
        """
        all_columns = list(df_explained.columns)
        df_explanation_values = df_explained.values
        graph_nodes_values = []

        # Each feature_value pair is computed (NODE_NAME) and the importance value associated to its top1 target is
        # retrieved as the NODE_IMPORTANCE
        for i, row in enumerate(df_explanation_values):
            for feature_col in feature_cols:
                feature_value_raw = row[all_columns.index(feature_col)]
                if feature_col in float_features:
                    feature_value = '_'.join([feature_col, "{:.02f}".format(feature_value_raw)])
                else:
                    feature_value = '_'.join([feature_col, feature_value_raw])
                feature_target_shap_col = '{}_{}{}'.format(top1_targets[i], feature_col, IMPORTANCE_SUFFIX)
                graph_nodes_values.append([row[0], feature_value, row[all_columns.index(feature_target_shap_col)],
                                           top1_targets[i]])

        graph_nodes = pd.DataFrame(graph_nodes_values, columns=[ID, NODE_NAME, NODE_IMPORTANCE, TARGET])
        graph_nodes[NODE_IMPORTANCE] = graph_nodes[NODE_IMPORTANCE].abs()
        global_graph_nodes = graph_nodes[[TARGET, NODE_NAME, NODE_IMPORTANCE]].groupby(
            [TARGET, NODE_NAME]).mean().reset_index()

        # Rank is calculated based on NODE_IMPORTANCE and grouping by TARGET
        global_graph_nodes[RANK] = (
            global_graph_nodes.groupby([TARGET])[NODE_IMPORTANCE].rank(method='dense', ascending=False).astype(int))

        return global_graph_nodes

    @staticmethod
    def __compute_global_target_explainability(df_importance_values: pd.DataFrame, feature_cols: List[str],
                                               target_cols: List[str], top1_targets: np.ndarray) -> pd.DataFrame:
        """
        This function computes the mean of each feature importance for each target

        :param df_importance_values:    Pandas DataFrame containing (among others) the importance columns
        :param feature_cols:            List of strings containing the column names for the features
        :param target_cols:             List of strings containing the column names for the target/s
        :param top1_targets:            Numpy array containing the top1_target for each row
        :return:                        Pandas DataFrame containing the mean of each feature importance for each target
        """
        # A boolean mask is generated from the top1_targets, this mask is then applied to the importance values
        # DataFrame so that only those values related to each top1 target, are taken into account. The resulting matrix
        # does have as many rows as observations and as many columns as features
        target_mask = np.repeat(pd.get_dummies(pd.Series(top1_targets)).values,
                                len(feature_cols), axis=0).reshape(-1, len(feature_cols),
                                                                   len(target_cols)).astype('bool')
        top1_importance = df_importance_values[target_mask].reshape(-1, len(feature_cols))

        # Pandas DataFrame is built from the matrix and an additional column with the target names is prepended
        top1_importance_features = pd.DataFrame(np.concatenate((top1_targets.reshape(-1, 1), top1_importance), axis=1),
                                                columns=[TARGET] + feature_cols)

        # Column mean is calculated groping by target. The result does have as many rows as targets and as many columns
        # as features
        return top1_importance_features.apply(pd.to_numeric, errors='ignore').groupby(TARGET).mean().reset_index()

    @staticmethod
    def __aggregate(df_2_explain: pd.DataFrame, target_cols: List[str]) -> pd.DataFrame:
        """
        This function processes the DataFrame provided as parameter so that all its features but the ones in
        target_cols parameter, are aggregated and the means of those in target_cols are computed. Columns are renamed
        accordingly

        :param df_2_explain: Pandas DataFrame to which the operations described above will be applied
        :param target_cols:  List of strings with all column names identified as target
        :return:              Pandas DataFrame resulting after applying aforementioned transformations
        """
        df_aggregated = (df_2_explain.groupby([c for c in list(df_2_explain.columns) if c not in target_cols]).agg(
            {c: [MEAN] for c in target_cols}).reset_index())
        df_aggregated.columns = ['_'.join(col).strip() if col[1] != '' else col[0] for col in
                                 df_aggregated.columns]
        return df_aggregated.rename(columns={'_'.join([c, MEAN]): c for c in target_cols})

    @staticmethod
    def __disaggregate(phi0: np.ndarray, importance_values: np.ndarray, df_2_explain: pd.DataFrame,
                       df_aggregated: pd.DataFrame, feature_cols: List[str],
                       target_cols: List[str]) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        """
        This function takes care of propagating the calculated importance values to the DataFrame to be explained (the
        disaggregated DataFrame). A quality measure featuring the divergence between the ground truth and the importance
        based prediction is included in the DataFrame to explain too.

        :param phi0:               Numpy array containing the baseline (prediction when no features are provided) for
                                   each target
        :param importance_values:  Numpy matrix containing the importance values calculated for each aggregated
                                   DataFrame row, for each feature and for each target. Shape (n_rows x n_features x
                                    n_targets)
        :param df_2_explain:       Pandas DataFrame to be explained
        :param df_aggregated:      Pandas DataFrame whose features have been aggregated and its targets have been
                                   averaged
        :param feature_cols:       List of strings containing the column names for the features
        :param target_cols:        List of strings with all column names identified as target
        :return:                   Dictionary with two elements: the DataFrame to explain, containing the importance
                                   values and the quality measure. The second elements are the adapted importance values
                                    which are calculated by taking into account the quality measure
        """
        # For each feature column and target column pair a new column is generated to store the corresponding
        # importance value
        importance_columns = []
        for i, c in enumerate(df_aggregated.columns):
            if c in feature_cols:
                for j, target_col in enumerate(target_cols):
                    df_aggregated['{}_{}{}'.format(target_col, c, IMPORTANCE_SUFFIX)] = importance_values[:, i, j]
                    importance_columns.append('{}_{}{}'.format(target_col, c, IMPORTANCE_SUFFIX))

        # DataFrame to be explained is left joined with the normalized DataFrame (already containing columns with the
        # computed importance values). The join is on the features of the DataFrame to be explained
        df_aggregated_features = df_aggregated.drop(target_cols, axis=1)
        df_explanation = pd.merge(df_2_explain, df_aggregated_features, on=feature_cols, how='left')

        # Normalization trick:
        #   Ground truth values are retrieved from df_explanation
        y = df_explanation[target_cols].values

        #   Columns containing importance values are reshaped: number of rows x number of features x number of targets
        calculated_importance = df_explanation[importance_columns].values.reshape(y.shape[0],
                                                                                  importance_values.shape[1],
                                                                                  importance_values.shape[2])

        #   Predictions calculated as baseline plus the summation of the calculated importance values
        y_hat: np.ndarray = phi0 + np.sum(calculated_importance, axis=1)

        # Difference between ground truth and predictions
        quality_measure: np.ndarray = (y - y_hat)

        # Adapted importance results from adding the calculated importance plus the quality measure divided by the
        # number of features
        adapted_importance: np.ndarray = calculated_importance + np.expand_dims(
            quality_measure / calculated_importance.shape[1], axis=1)
        reshaped_adapted_importance = adapted_importance.reshape(adapted_importance.shape[0], -1)

        # TODO: Chequear para el target top1 que PHI0 + adapted shapley es mayor que 0 para cada ID
        for i, c in enumerate(importance_columns):
            df_explanation[c] = reshaped_adapted_importance[:, i]

        for j, target_col in enumerate(target_cols):
            quality_measure_column = '{}_{}'.format(target_col, ImportanceCalculator._QUALITY_MEASURE)
            df_explanation[quality_measure_column] = quality_measure[:, j]

        # Data is formatted for the sanity check
        y = df_explanation[target_cols].values
        y_hat_reduced = phi0 + np.sum(df_explanation[importance_columns].values.reshape(-1, adapted_importance.shape[1],
                                                                                        adapted_importance.shape[2]),
                                      axis=1)
        ImportanceCalculator.sanity_check(ground_truth=y, prediction=y_hat_reduced, target_cols=target_cols,
                                          scope='original')

        return {
            ImportanceCalculator._DF_EXPLANATION: df_explanation,
            ImportanceCalculator._IMPORTANCE_VALUES: adapted_importance
        }

    @staticmethod
    def sanity_check(ground_truth: np.ndarray, prediction: np.ndarray, target_cols: List[str], scope: str):
        """
        This function checks the consistency between each row ground truth and the prediction based on importance
        calculation

        :param ground_truth:    Numpy array containing the ground truth for each row
        :param prediction:      Numpy array containing the importance based prediction for each row
        :param target_cols:     List of strings with all column names identified as target
        :param scope:           String representing the sanity check scope (original/aggregated), only used to format
                                the output message
        """
        error = np.abs(ground_truth - prediction) > ImportanceCalculator._EPS_ERROR
        for i, target_col in enumerate(target_cols):
            print('Number of detected discrepancies (original model prediction != SHAP prediction) '
                  'for target {} in the {} dataset: {}'.format(target_col, scope, sum(error[:, i])))

    def __global_explain(self, float_features: List[str], top1_targets: np.ndarray,
                         **params) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        This function computes the global explanation. This is made of several pandas DataFrames:
        - Pandas DataFrame, containing the mean of each feature importance for each target
        - Pandas DataFrame, containing the mean of each feature importance throughout all the targets
        - Pandas DataFrame, containing the global graph nodes information related to the calculation of the features
        importance

        :param float_features:  List of strings containing the column names for the float type features
        :param top1_targets:    Numpy array containing the top1_target for each row
        :param params:          Dictionary containing the output of the local explanation
        :return:                Tuple containing a pandas DataFrame, containing the mean of each feature importance for
                                each target, a pandas DataFrame, containing the mean of each feature importance
                                 throughout all the targets and a pandas DataFrame, containing the global graph nodes
                                  information related to the calculation of the features
        """
        top1_importance_features = ImportanceCalculator.__compute_global_target_explainability(
            df_importance_values=params[ImportanceCalculator._IMPORTANCE_VALUES],
            feature_cols=self.feature_cols,
            target_cols=self.target_cols,
            top1_targets=top1_targets)

        global_explainability = ImportanceCalculator.__compute_global_explainability(
            global_target_explainability=top1_importance_features,
            feature_cols=self.feature_cols,
            target_cols=self.target_cols,
            top1_targets=top1_targets)

        global_graph_nodes = ImportanceCalculator.__compute_global_graph_nodes_importance(
            df_explained=params[ImportanceCalculator._DF_EXPLANATION],
            feature_cols=self.feature_cols,
            float_features=float_features,
            top1_targets=top1_targets)

        return top1_importance_features, global_explainability, global_graph_nodes

    def __local_explain(self, **params) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        """
        This function encapsulates the whole process of local explainability: it starts by aggregating features on the
        DataFrame to explain, then calculates importance values and then dissagregation is done so that prediction
        quality can be calculated on the original data

        :param params:  Dictionary containing information which will be used to calculate importance values
        :return:        Dict[str, Union[pd.DataFrame, np.ndarray]]
        """
        df_aggregated = ImportanceCalculator.__aggregate(df_2_explain=self.df_2_explain.drop(ID, axis=1),
                                                         target_cols=self.target_cols)

        importance_dict = self.calculate_importance_values(df_aggregated=df_aggregated, **params)

        return ImportanceCalculator.__disaggregate(phi0=importance_dict[ImportanceCalculator._PHI0],
                                                   importance_values=importance_dict[
                                                       ImportanceCalculator._IMPORTANCE_VALUES],
                                                   df_2_explain=self.df_2_explain,
                                                   df_aggregated=df_aggregated,
                                                   feature_cols=self.feature_cols,
                                                   target_cols=self.target_cols)

    def __sample_explanation(self, **params) -> pd.DataFrame:
        """
        This function filters the pandas DataFrame which has been explained according to the previously calculated
        sample mask

        :param params:  Dictionary containing the pandas DataFrame which has been explained
        :return:        Pandas DataFrame which has been filtered according to the previously calculated sample mask
        """
        return filter_by_ids(df=params[ImportanceCalculator._DF_EXPLANATION],
                             sample_id_mask=self.sample_ids_mask_2_explain)

    def calculate_importance(self, features_info: FeaturesInfo, target_info: TargetInfo) -> Tuple[pd.DataFrame,
                                                                                                  pd.DataFrame,
                                                                                                  pd.DataFrame,
                                                                                                  pd.DataFrame]:
        """
        This method orchestrates all the steps related to importance calculation: from training, to local and global
        explanation and, finally, local explanation sampling

        :param features_info:   NamedTuple containing all the feature column names lists which will be used all through
                                the execution flow
        :param target_info:     NamedTuple containing a numpy array listing the top1 target for each DataFrame row,
                                another numpy array listing a probability for each possible target value and a third
                                numpy array showing the top1 targets indexes
        :return:                Tuple of pandas DataFrame containing:
                                - Pandas DataFrame, containing the mean of each feature importance for each target
                                - Pandas DataFrame, containing the mean of each feature importance throughout all the
                                targets
                                - Pandas DataFrame, containing the global graph nodes information related to the
                                calculation of the features importance
                                - Pandas DataFrame which has been filtered according to the previously calculated sample
                                 mask

        """
        #   ImportanceCalculator is trained here. Just like in Machine Learning, the dataset must accurately represent
        #   the problem domain to obtain valid results
        importance_calculator_trained = self.train()

        #   Once trained, the ImportanceCalculator is used to provide local explainability
        local_importance = self.__local_explain(**importance_calculator_trained)

        #   StatsCalculator results such as the explained DataFrame are used to compute information related to global
        #   explanation
        top1_importance_features, global_explainability, global_nodes_importance = self.__global_explain(
            float_features=features_info.float_feature_columns, top1_targets=target_info.top1_targets,
            **local_importance)

        # Once global explanation related information is calculated. The explanation DataFrame is sampled, so that only
        # some rows will be taken into account when generating the local output for visualization
        df_explanation_sample = self.__sample_explanation(**local_importance)

        return top1_importance_features, global_explainability, global_nodes_importance, df_explanation_sample
