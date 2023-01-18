import os

import numpy as np
import pandas as pd

from xaiographs.common.constants import BIN_WIDTH_EDGE_WEIGHT, BIN_WIDTH_FEATURE_WEIGHT, BIN_WIDTH_NODE_WEIGHT, \
    COMMA_SEP, COUNT, EDGE_WEIGHT, FEATURE_IMPORTANCE, FEATURE_NAME, FEATURE_WEIGHT, ID, IMPORTANCE_FEATURE, \
    IMPORTANCE_SUFFIX, MAX_EDGE_WEIGHT, MAX_FEATURE_WEIGHT, MIN_EDGE_WEIGHT, MIN_FEATURE_WEIGHT, MAX_NODE_WEIGHT, \
    MIN_NODE_WEIGHT, N_BINS_EDGE_WEIGHT, N_BINS_FEATURE_WEIGHT, N_BINS_NODE_WEIGHT, NODE_COUNT, NODE_IMPORTANCE, \
    NODE_NAME, NODE_NAME_RATIO, NODE_NAME_RATIO_RANK, NODE_NAME_RATIO_WEIGHT, NODE_WEIGHT, NUM_FEATURES, \
    RELIABILITY, RANK, TARGET, TOTAL_COUNT
from xaiographs.common.utils import FeaturesInfo, TargetInfo, xgprint
from xaiographs.exgraph.statistics.stats_calculator import StatsResults


class Exporter(object):
    """
    This class is intended to encapsulate everything related to build those files which will be later used for
    information visualization. These tasks include

    - Combining the computed statistics with the computed importance values when needed
    - Format information to conform the expected output
    - Create additional columns related to graphical representation (like weight in pixels for each row) when needed
    """

    def __init__(self, df_explanation_sample: pd.DataFrame, path: str, sep: str = COMMA_SEP, keep_index: bool = False,
                 verbose: int = 0):
        """
        Constructor method for Exporter

        :param df_explanation_sample: Pandas DataFrame containing a sample of the explained pandas DataFrame
        :param path:                  String representing the path where data will be persisted
        :param sep:                   String representing the field separator (default ',')
        :param keep_index:            Boolean representing whether index must be stored or not
        :param verbose:               Verbosity level, where any value greater than 0 means the message is printed

        """
        self.df_explanation_sample = df_explanation_sample
        self.path = path
        self.sep = sep
        self.keep_index = keep_index
        self.verbose = verbose
        xgprint(self.verbose, 'INFO: Instantiating Exporter:')

    def __export_edges(self, df_stats: pd.DataFrame, filename: str):
        """
        This function calculates each edge weight in pixels and persists the information. This function handles local
        and global edge data

        :param df_stats:        Pandas DataFrame containing previously calculated edge statistics
        :param filename:        String representing the name of the file used to persist the information
        """
        df_stats[EDGE_WEIGHT] = pd.cut(df_stats[COUNT], bins=N_BINS_EDGE_WEIGHT,
                                       labels=range(MIN_EDGE_WEIGHT,
                                                    MAX_EDGE_WEIGHT + BIN_WIDTH_EDGE_WEIGHT))
        df_stats.to_csv(path_or_buf=os.path.join(self.path, filename), sep=self.sep, index=self.keep_index)

    def __export_global_description(self, df_global_nodes_info: pd.DataFrame,
                                    filename: str = 'global_graph_description.csv'):
        """
        This function calculates the number of different feature - value pairs associated to each target value. It
        persist the resulting information

        :param df_global_nodes_info:    Pandas DataFrame containing the node global info resulting from combining the
                                        calculated statistics and the calculated importance
        :param filename:                String representing the name of the file used to persist the information
        """
        df_global_nodes_info[[TARGET, RANK]].drop_duplicates(subset=[TARGET], keep='last').rename(
            columns={RANK: NUM_FEATURES}).to_csv(path_or_buf=os.path.join(self.path, filename),
                                                 columns=[TARGET, NUM_FEATURES], sep=COMMA_SEP, index=False)

    def __export_global_explainability(self, df_importance: pd.DataFrame, filename: str = 'global_explainability.csv'):
        """
        This function calculates the weight in pixels of each feature importance and persists the global explainability
        information

        :param df_importance:   Pandas DataFrame containing the mean of each feature importance throughout all the
                                targets
        :param filename:        String representing the name of the file used to persist the information
        """
        df_importance[FEATURE_WEIGHT] = pd.cut(df_importance[FEATURE_IMPORTANCE].astype('float'),
                                               bins=N_BINS_FEATURE_WEIGHT,
                                               labels=list(range(
                                                   MIN_FEATURE_WEIGHT,
                                                   MAX_FEATURE_WEIGHT + BIN_WIDTH_FEATURE_WEIGHT,
                                                   BIN_WIDTH_FEATURE_WEIGHT)))
        df_importance.to_csv(path_or_buf=os.path.join(self.path, filename), sep=self.sep, index=self.keep_index)

    def __export_global_nodes(self, df_stats: pd.DataFrame, df_importance: pd.DataFrame,
                              filename='global_graph_nodes.csv') -> pd.DataFrame:
        """
        This function combines the global node information resulting from statistic calculation and from importance
        calculation. It also calculates weights in pixels for the nodes importance and for the nodes frequency and
        persists the information

        :param df_stats:        Pandas DataFrame containing previously calculated nodes global statistics
        :param df_importance:   Pandas DataFrame containing previously calculated nodes global importance
        :param filename:        String representing the name of the file used to persist the information
        :return:                Pandas DataFrame containing the node global info resulting from combining the
                                calculated statistics and the calculated importance
        """
        global_node_info = df_importance.merge(df_stats, how="right", on=NODE_NAME)
        global_node_info[NODE_NAME_RATIO_WEIGHT] = pd.cut(global_node_info[NODE_NAME_RATIO],
                                                          bins=N_BINS_NODE_WEIGHT,
                                                          labels=list(range(
                                                              MIN_NODE_WEIGHT,
                                                              MAX_NODE_WEIGHT + BIN_WIDTH_NODE_WEIGHT,
                                                              BIN_WIDTH_NODE_WEIGHT)))
        global_node_info[NODE_WEIGHT] = pd.cut(global_node_info[NODE_IMPORTANCE],
                                               bins=N_BINS_NODE_WEIGHT,
                                               labels=list(range(
                                                   MIN_NODE_WEIGHT,
                                                   MAX_NODE_WEIGHT + BIN_WIDTH_NODE_WEIGHT,
                                                   BIN_WIDTH_NODE_WEIGHT)))
        global_node_info.sort_values(by=[TARGET, RANK], inplace=True)
        global_node_info.to_csv(path_or_buf=os.path.join(self.path, filename),
                                columns=[TARGET, NODE_NAME, NODE_IMPORTANCE, NODE_WEIGHT,
                                         RANK, NODE_COUNT, TOTAL_COUNT,
                                         NODE_NAME_RATIO, NODE_NAME_RATIO_WEIGHT,
                                         NODE_NAME_RATIO_RANK], sep=self.sep,
                                index=self.keep_index)

        return global_node_info

    def __export_global_target_distribution(self, df_global_target_distribution: pd.DataFrame,
                                            filename='global_target_distribution.csv'):
        """
        This function persists the information related to the number of appearances of each possible target value

        :param df_global_target_distribution:   Pandas DataFrame containing the information related to the number of
                                                appearances of each possible target value
        :param filename:                        String representing the name of the file used to persist the information
        """
        df_global_target_distribution.to_csv(path_or_buf=os.path.join(self.path, filename), sep=self.sep,
                                             index=self.keep_index)

    def __export_global_target_explainability(self, df_importance: pd.DataFrame,
                                              filename: str = 'deprecated_global_target_explainability.csv'):
        """
        This function persists the global target explainability information. Note that his file will be deprecated

        :param df_importance:   Pandas DataFrame containing the mean of each feature importance for each target
        :param filename:        String representing the name of the file used to persist the information
        """
        df_importance.to_csv(path_or_buf=os.path.join(self.path, filename), sep=self.sep, index=self.keep_index)

    def __export_local_dataset_reliability(self, features_info: FeaturesInfo, target_info: TargetInfo,
                                           sample_ids_mask: np.ndarray,
                                           filename: str = 'local_dataset_reliability.csv'):
        """
        This function collects the reliability for each row and for its correspondent top1 target, then, information
        is persisted

        :param features_info:       NamedTuple containing all the feature column names lists which will be used all
                                    through the execution flow
        :param target_info:         NamedTuple containing a numpy array listing the top1 target for each DataFrame row,
                                    another numpy array listing a probability for each possible target value and a third
                                    numpy array showing the top1 targets indexes
        :param sample_ids_mask:     Numpy array containing boolean values which will be used to filter any given
                                    DataFrame
        :param filename:            String representing the name of the file used to persist the information
        """
        df_local_feature_values = self.df_explanation_sample[[ID] + features_info.feature_columns].values
        # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
        #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con valores de
        #  ese tipo
        for i, feature_col in enumerate(features_info.feature_columns):
            if feature_col in features_info.float_feature_columns:
                df_local_feature_values[:, i + 1] = np.around(df_local_feature_values[:, i + 1].astype('float'),
                                                              decimals=2)

        df_local_reliability_values = self.df_explanation_sample[features_info.reliability_columns].values
        pd.DataFrame(np.concatenate((df_local_feature_values, target_info.top1_targets[sample_ids_mask].reshape(-1, 1),
                                     np.abs(1 - np.round(df_local_reliability_values[
                                                             np.arange(
                                                                 df_local_reliability_values.shape[
                                                                     0]), target_info.top1_argmax[sample_ids_mask]],
                                                         decimals=2)).reshape(-1, 1)), axis=1),
                     columns=[ID] + features_info.feature_columns + [TARGET] + [RELIABILITY]).to_csv(
            path_or_buf=os.path.join(self.path, filename),
            sep=self.sep, index=self.keep_index)

    def __export_local_explainability(self, features_info: FeaturesInfo, target_info: TargetInfo,
                                      sample_ids_mask: np.ndarray, filename: str = 'local_explainability.csv'):
        """
        This function collects for each row the importance for each feature and for the top1 target. Then, this
        information is persisted

        :param features_info:       NamedTuple containing all the feature column names lists which will be used all
                                    through the execution flow
        :param target_info:         NamedTuple containing a numpy array listing the top1 target for each DataFrame row,
                                    another numpy array listing a probability for each possible target value and a third
                                    numpy array showing the top1 targets indexes
        :param sample_ids_mask:     Numpy array containing boolean values which will be used to filter any given
                                    DataFrame
        :param filename:            String representing the name of the file used to persist the information
        """
        # First, a dictionary with as many elements as target values so that each mask value consists of a list of
        # boolean values set to True for those importance features associated to that target and False for the rest, is
        # built
        adapted_importance_mask = {}
        for target_col in target_info.target_columns:
            target_mask = []
            for importance_col in features_info.importance_columns:
                if not importance_col.startswith(target_col):
                    target_mask.append(False)
                else:
                    target_mask.append(True)
            adapted_importance_mask[target_col] = target_mask

        # For each row, its corresponding adated_importance_mask is retrieved. It will depend on the top1 target
        top1_targets = target_info.top1_targets[sample_ids_mask]
        adapted_importance_by_target = []
        for target_value in top1_targets:
            adapted_importance_by_target.append(adapted_importance_mask[target_value])

        pd.DataFrame(np.concatenate((self.df_explanation_sample[ID].values.reshape(-1, 1),
                                     self.df_explanation_sample[features_info.importance_columns].values[
                                         np.array(adapted_importance_by_target)].reshape(
                                         len(self.df_explanation_sample), -1),
                                     top1_targets.reshape(-1, 1)), axis=1),
                     columns=[ID] + features_info.feature_columns + [TARGET]).to_csv(
            path_or_buf=os.path.join(self.path, filename),
            sep=self.sep, index=self.keep_index)

    def __export_local_nodes(self, df_stats: pd.DataFrame, features_info: FeaturesInfo,
                             filename='local_graph_nodes.csv'):
        """
        This function combines the previously calculated local statistics for the nodes, with the calculated importance.
        It calculates the weight in pixels for the node importance too and, finally, persists the resulting information

        :param df_stats:        Pandas DataFrame containing previously calculated nodes local statistics
        :param features_info:   NamedTuple containing all the feature column names lists which will be used all through
                                the execution flow
        :param filename:        String representing the name of the file used to persist the information
        """
        importance_values = np.repeat(self.df_explanation_sample.values, len(features_info.feature_columns), axis=0)
        df_stats[IMPORTANCE_FEATURE] = df_stats[TARGET] + '_' + df_stats[FEATURE_NAME] + IMPORTANCE_SUFFIX
        importance_mask = (
                    df_stats[IMPORTANCE_FEATURE].values.reshape(-1, 1) == np.array(self.df_explanation_sample.columns))
        node_importance = importance_values[importance_mask]
        df_stats[NODE_IMPORTANCE] = node_importance
        local_nodes_info = df_stats[[ID, NODE_NAME, NODE_IMPORTANCE, TARGET]].copy()
        local_nodes_info[RANK] = local_nodes_info.groupby(ID)[NODE_IMPORTANCE].rank(method='dense',
                                                                                    ascending=False).astype(int)
        local_nodes_info.to_csv(path_or_buf=os.path.join(self.path, filename), sep=self.sep, index=self.keep_index)
        local_nodes_info[NODE_WEIGHT] = pd.cut(local_nodes_info[NODE_IMPORTANCE].abs(),
                                               bins=N_BINS_NODE_WEIGHT,
                                               labels=list(range(
                                                   MIN_NODE_WEIGHT,
                                                   MAX_NODE_WEIGHT + BIN_WIDTH_NODE_WEIGHT,
                                                   BIN_WIDTH_NODE_WEIGHT)))
        local_nodes_info.sort_values(by=[ID, RANK]).to_csv(path_or_buf=os.path.join(self.path, filename),
                                                           columns=[ID, NODE_NAME, NODE_IMPORTANCE, NODE_WEIGHT, RANK,
                                                                    TARGET], sep=self.sep, index=self.keep_index)

    def __export_reason_why(self, df_why: pd.DataFrame, filename: str = 'local_reason_why.csv'):
        """
        This function persists the previously sampled reason why file. It's a temporary workaround until the 'why'
        module is available

        :param df_why:          PandasDataFrame containing a number of Loren Ipsum excerpts
        :param filename:        String representing the name of the file used to persist the information
        """
        df_why.to_csv(path_or_buf=os.path.join(self.path, filename), sep=self.sep, index=self.keep_index)

    def export(self, features_info: FeaturesInfo, target_info: TargetInfo, sample_ids_mask: np.ndarray,
               global_target_explainability: pd.DataFrame, global_explainability: pd.DataFrame,
               global_nodes_importance: pd.DataFrame, nodes_info: StatsResults, edges_info: StatsResults,
               target_distribution: pd.DataFrame, reason_why: pd.DataFrame):

        xgprint(self.verbose, 'INFO:     Exporting data in CSV format to {}'.format(self.path))
        self.__export_local_explainability(features_info=features_info, target_info=target_info,
                                           sample_ids_mask=sample_ids_mask)

        self.__export_local_dataset_reliability(features_info=features_info, target_info=target_info,
                                                sample_ids_mask=sample_ids_mask)

        self.__export_local_nodes(df_stats=nodes_info.local_stats, features_info=features_info)

        self.__export_edges(df_stats=edges_info.local_stats, filename='local_graph_edges.csv')

        self.__export_global_target_explainability(df_importance=global_target_explainability)

        self.__export_global_explainability(df_importance=global_explainability)

        global_nodes_info = self.__export_global_nodes(df_stats=nodes_info.global_stats,
                                                       df_importance=global_nodes_importance)

        self.__export_global_description(df_global_nodes_info=global_nodes_info)

        self.__export_global_target_distribution(df_global_target_distribution=target_distribution)

        self.__export_edges(df_stats=edges_info.global_stats, filename='global_graph_edges.csv')

        self.__export_reason_why(df_why=reason_why)
