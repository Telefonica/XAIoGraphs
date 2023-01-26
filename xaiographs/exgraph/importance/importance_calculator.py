from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd

from xaiographs.common.constants import FEATURE_IMPORTANCE, FEATURE_NAME, ID, IMPORTANCE_SUFFIX, NODE_IMPORTANCE, \
    NODE_NAME, RANK, TARGET
from xaiographs.common.utils import FeaturesInfo, TargetInfo, filter_by_ids, get_target_info, xgprint


class ImportanceCalculator(metaclass=ABCMeta):
    """
    This class is intended to be a template to develop different implementations for importance calculation. Some
    methods are abstract, so that they must be implemented depending on the strategy used to calculate importance and
    some other are given, representing those tasks which stay always the same, independently of the strategy
    """
    _DF_EXPLANATION = 'df_explanation'
    _EPS_ERROR = 0.000001
    _PHI0 = 'phi0'
    _IMPORTANCE_VALUES = 'importance_values'
    _TOP1_TARGET = 'top1_target'

    def __init__(self, feature_cols: List[str], target_info: TargetInfo, train_size: float, train_stratify: bool,
                 verbose: int = 0):
        """
        Constructor method for ImportanceCalculator

        :param feature_cols:                List of strings containing the column names for the features
        :param target_info:                 NamedTuple containing a numpy array listing the top1 target for each
                                            DataFrame row, another numpy array listing a probability for each possible
                                            target value and a third numpy array showing the top1 targets indexes

        :param train_size:                  Float indicating the percentage of the pandas DataFrame that will be used
                                            to train the calculator
        :param train_stratify:              Boolean indicating whether target columns proportions will be taken into
                                            account when splitting the data (if train_size > 0.0)
        :param verbose:                     Verbosity level, where any value greater than 0 means the message is printed

        """
        self.feature_cols = feature_cols
        self.target_info = target_info
        self.train_size = train_size
        self.train_stratify = train_stratify
        self.verbose = verbose
        xgprint(self.verbose, 'INFO:     Instantiating ImportanceCalculator:')

    @abstractmethod
    def local_explain(self, batch_size: int, **params) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        raise NotImplementedError

    @abstractmethod
    def train(self, df: pd.DataFrame, num_samples_to_explain: int):
        raise NotImplementedError

    @staticmethod
    def __compute_global_explainability(global_target_explainability: pd.DataFrame, feature_cols: List[str],
                                        top1_targets: np.ndarray) -> pd.DataFrame:
        """
        This function computes the mean of each feature importance throughout all the targets

        :param global_target_explainability: Pandas DataFrame containing the mean of each feature importance for each
                                             target
        :param feature_cols:                 List of strings containing the column names for the features
        :param top1_targets:                 Numpy array containing the top1_target for each row
        :return:                             Pandas DataFrame containing the mean of each feature importance throughout
                                             all the targets
        """
        # To generate global_explainability.csv, the targets probabilities are computed and each of the rows of the
        # previous DataFrame is multiplied by the corresponding probability. Finally, mean is computed for the resulting
        # columns
        target_probs = np.array([top1_targets.tolist().count(target) for target in
                                 global_target_explainability[TARGET].values]) / len(top1_targets)

        return pd.DataFrame(np.concatenate((np.array(feature_cols).reshape(-1, 1),
                                            (target_probs.reshape(-1, 1) * global_target_explainability.drop(
                                                TARGET, axis=1).values).sum(axis=0).reshape(-1, 1)), axis=1),
                            columns=[FEATURE_NAME, FEATURE_IMPORTANCE]).sort_values(by=[FEATURE_IMPORTANCE],
                                                                                    ascending=False)

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
                    feature_value = '_'.join([feature_col, str(feature_value_raw)])
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
        top1_importance = np.abs(df_importance_values[target_mask]).reshape(-1, len(feature_cols))

        # Pandas DataFrame is built from the matrix and an additional column with the target names is prepended
        top1_importance_features = pd.DataFrame(np.concatenate((top1_targets.reshape(-1, 1), top1_importance), axis=1),
                                                columns=[TARGET] + feature_cols)

        # Column mean is calculated groping by target. The result does have as many rows as targets and as many columns
        # as features
        return top1_importance_features.apply(pd.to_numeric, errors='ignore').groupby(TARGET).mean().reset_index()

    @staticmethod
    def sample_explanation(df_explanation: pd.DataFrame, sample_ids_mask_2_explain: np.ndarray) -> pd.DataFrame:
        """
        This function filters the pandas DataFrame which has been explained according to the previously calculated
        sample mask

        :param df_explanation:              Pandas DataFrame which has been explained
        :param sample_ids_mask_2_explain:   Numpy array mask, which will be applied to the explanation pandas DataFrame
                                            right after global explanation is computed
        :return:                            Pandas DataFrame which has been filtered according to the previously
                                            calculated sample mask
        """
        return filter_by_ids(df=df_explanation, sample_id_mask=sample_ids_mask_2_explain)

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
            print('INFO:     ImportanceCalculator: Number of detected discrepancies (original model prediction != SHAP '
                  'prediction) for target {} in the {} dataset: {}'.format(target_col, scope, sum(error[:, i])))

    @staticmethod
    def sample_global(df: pd.DataFrame, top1_targets: np.ndarray, num_samples: int,
                      target_probs: np.ndarray, target_cols: List[str], target_col: str = TARGET) -> pd.DataFrame:
        """
        This method extracts a number of samples from a given DataFrame so that the sampling method will respect the
        given target ratios

        :param df:              Pandas DataFrame from which the samples will be extracted
        :param top1_targets:    Numpy array containing the top1 target for each row. Sampling will be calculated so
                                that the target ratio will be kept, this parameter allows filtering by target
        :param num_samples:     Integer representing the number of samples which will be calculated
        :param target_probs:    Numpy array containing the probability for each target. It's used to calculate the ratio
                                for each target
        :param target_cols:     List of strings containing the possible targets
        :param target_col:      String representing the target col name (default: 'target')
        :return:                Pandas DataFrame containing the requested number of samples
        """
        # If the number of samples to be globally explained is greater or equal than the dataset size, there's no need
        # for sampling, the whole dataset is taken into account
        if num_samples >= len(df):
            print('WARN:               requested number of samples for global explanation ({}) is greater than dataset'
                  ' size ({}) ...'.format(num_samples, len(df)))
            print('INFO:               the whole dataset will taken as dataset to be explained')
            return df

        # A target column is included in the given pandas DataFrame, this column will contain the top1 target
        # for each row
        df[target_col] = top1_targets

        # For each possible target, rows are filtered by that target and the number of rows per target to retrieve is
        # computed by using the target probability and the number of requested samples
        df_agg_per_target = []
        for target_prob, target_col_value in zip(target_probs, target_cols):
            n_samples_by_target = int(num_samples * target_prob)
            df_agg_per_target.append(df[df[target_col] == target_col_value].sample(
                n=n_samples_by_target, random_state=42))

        return pd.concat(df_agg_per_target).drop(target_col, axis=1).sort_values(by=[ID])

    def __global_explain(self, float_features: List[str], target_cols: List[str],
                         **params) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        This function computes the global explanation. This is made of several pandas DataFrames:
        - Pandas DataFrame, containing the mean of each feature importance for each target
        - Pandas DataFrame, containing the mean of each feature importance throughout all the targets
        - Pandas DataFrame, containing the global graph nodes information related to the calculation of the features
        importance

        :param float_features:  List of strings containing the column names for the float type features
        :param target_cols:     List of strings containing the possible targets
        :param params:          Dictionary containing the output of the local explanation
        :return:                Tuple containing a pandas DataFrame, containing the mean of each feature importance for
                                each target, a pandas DataFrame, containing the mean of each feature importance
                                 throughout all the targets and a pandas DataFrame, containing the global graph nodes
                                  information related to the calculation of the features
        """
        target_info = get_target_info(df=params[ImportanceCalculator._DF_EXPLANATION], target_cols=target_cols)
        top1_importance_features = ImportanceCalculator.__compute_global_target_explainability(
            df_importance_values=params[ImportanceCalculator._IMPORTANCE_VALUES],
            feature_cols=self.feature_cols,
            target_cols=target_cols,
            top1_targets=target_info.top1_targets)

        global_explainability = ImportanceCalculator.__compute_global_explainability(
            global_target_explainability=top1_importance_features,
            feature_cols=self.feature_cols,
            top1_targets=target_info.top1_targets)

        global_graph_nodes = ImportanceCalculator.__compute_global_graph_nodes_importance(
            df_explained=params[ImportanceCalculator._DF_EXPLANATION],
            feature_cols=self.feature_cols,
            float_features=float_features,
            top1_targets=target_info.top1_targets)

        return top1_importance_features, global_explainability, global_graph_nodes

    def calculate_importance(self, df: pd.DataFrame, features_info: FeaturesInfo, num_samples: int,
                             batch_size: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        This method orchestrates all the steps related to importance calculation: from training, to local and global
        explanation and, finally, local explanation sampling

        :param df:              Pandas DataFrame containing the loaded dataset with the selected features
        :param features_info:   NamedTuple containing all the feature column names lists which will be used all through
                                the execution flow
        :param num_samples:     Integer representing the number of samples to be (globally) explained
        :param batch_size:      Integer representing the size of the batches (chunks) on which importance will be
                                calculated
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
        importance_calculator_trained = self.train(df=df, num_samples_to_explain=num_samples)

        #   Once trained, the ImportanceCalculator is used to provide local explainability
        local_importance = self.local_explain(batch_size=batch_size, **importance_calculator_trained)

        #   StatsCalculator results such as the explained DataFrame are used to compute information related to global
        #   explanation
        top1_importance_features, global_explainability, global_nodes_importance = self.__global_explain(
            float_features=features_info.float_feature_columns, target_cols=self.target_info.target_columns,
            **local_importance)
        return top1_importance_features, global_explainability, global_nodes_importance, local_importance[
            ImportanceCalculator._DF_EXPLANATION].sort_values(by=[ID])
