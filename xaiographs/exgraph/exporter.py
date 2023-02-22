import os

import numpy as np
import pandas as pd

from xaiographs.common.constants import COUNT, FEATURE, FEATURE_IMPORTANCE, FEATURE_NAME, ID, IMPORTANCE, \
    IMPORTANCE_SUFFIX, FEATURE_VALUE, NODE_COUNT, NODE_IMPORTANCE, NODE_NAME, NODE_NAME_RATIO, RELIABILITY, RANK, TARGET
from xaiographs.common.utils import FeaturesInfo, TargetInfo, xgprint
from xaiographs.exgraph.stats_calculator import StatsResults

# CONSTANTS
BIN_WIDTH_EDGE_WEIGHT = 1
BIN_WIDTH_FEATURE_WEIGHT = 1
BIN_WIDTH_NODE_WEIGHT = 5
EDGE_WEIGHT = 'edge_weight'
FEATURE_WEIGHT = 'feature_weight'
FREQUENCY = 'frequency'
IMPORTANCE_FEATURE = 'importance_feature'
MAX_EDGE_WEIGHT = 10
MAX_FEATURE_WEIGHT = 5
MAX_NODE_WEIGHT = 50
MEAN = 'mean'
MIN_EDGE_WEIGHT = 1
MIN_FEATURE_WEIGHT = 1
MIN_NODE_WEIGHT = 10
N_BINS_EDGE_WEIGHT = 10
N_BINS_FEATURE_WEIGHT = 5
N_BINS_NODE_WEIGHT = 9
NODE_NAME_RATIO_WEIGHT = 'node_name_ratio_weight'
NODE_WEIGHT = 'node_weight'
NUM_FEATURES = 'num_features'
TARGET_FEATURE_COUNT = 'target_feature_count'

# FILE CONSTANTS
EXPLAINER_GLOBAL_GRAPH_DESCRIPTION_FILE = 'global_graph_description.json'
EXPLAINER_GLOBAL_EXPLAINABILITY_FILE = 'global_explainability.json'
EXPLAINER_GLOBAL_GRAPH_NODES_FILE = 'global_graph_nodes.json'
EXPLAINER_GLOBAL_TARGET_DISTRIBUTION_FILE = 'global_target_distribution.json'
EXPLAINER_GLOBAL_TARGET_EXPLAINABILITY_FILE = 'global_target_explainability.json'
EXPLAINER_LOCAL_DATASET_RELIABILITY_FILE = 'local_dataset_reliability.json'
EXPLAINER_LOCAL_EXPLAINABILITY_FILE = 'local_explainability.json'
EXPLAINER_LOCAL_GRAPH_NODES_FILE = 'local_graph_nodes.json'
EXPLAINER_LOCAL_GRAPH_EDGES_FILE = 'local_graph_edges.json'
EXPLAINER_GLOBAL_GRAPH_EDGES_FILE = 'global_graph_edges.json'
EXPLAINER_GLOBAL_HEATMAP_FILE = 'global_heatmap_feat_val.json'


class Exporter(object):
    """
    This class is intended to encapsulate everything related to build those files which will be later used for
    information visualization. These tasks include

    - Combining the computed statistics with the computed importance values when needed
    - Format information to conform the expected output
    - Create additional columns related to graphical representation (like weight in pixels for each row) when needed
    """

    def __init__(self, df_explanation_sample: pd.DataFrame, destination_path: str, verbose: int = 0):
        """
        Constructor method for Exporter

        :param df_explanation_sample: Pandas DataFrame, containing a sample of the explained pandas DataFrame
        :param destination_path:      String, representing the path where data will be persisted
        :param verbose:               Verbosity level, where any value greater than 0 means the message is printed

        """
        self.__df_explanation_sample = df_explanation_sample
        self.__global_explainability = None
        self.__global_nodes_info = None
        self.__global_target_explainability = None
        self.__destination_path = destination_path
        self.__verbose = verbose
        xgprint(self.__verbose, 'INFO: Instantiating Exporter:')

    @property
    def global_explainability(self):
        """
        Property that returns all the features to be explained, ranked by their global importance. Prior to invoking
        this property, the`export()` method from the `Exporter` class must have been invoked

        :return: pd.DataFrame, containing each feature ranked by its global importance
        """
        if self.__global_explainability is not None:
            self.__global_explainability[RANK] = pd.to_numeric(
                self.__global_explainability[FEATURE_IMPORTANCE].rank(ascending=False).astype('int'),
                downcast="unsigned")
            self.__global_explainability[FEATURE_IMPORTANCE] = pd.to_numeric(
                self.__global_explainability[FEATURE_IMPORTANCE], downcast="float")
            return self.__global_explainability[[FEATURE_NAME, FEATURE_IMPORTANCE, RANK]].rename(
                columns={FEATURE_NAME: FEATURE, FEATURE_IMPORTANCE: IMPORTANCE})
        else:
            return None

    @property
    def global_frequency_feature_value(self):
        """
        Property that returns for each feature-value pair the number of its occurrences

        :return: pd.DataFrame, containing the number of times each feature-value occurs
        """
        if self.__global_nodes_info is not None:
            self.__global_nodes_info[NODE_COUNT] = pd.to_numeric(self.__global_nodes_info[NODE_COUNT],
                                                                 downcast="unsigned")
            return self.__global_nodes_info[[NODE_NAME, NODE_COUNT]].drop_duplicates(subset=[NODE_NAME]).rename(
                columns={NODE_NAME: FEATURE_VALUE, NODE_COUNT: FREQUENCY})
        else:
            return None

    @property
    def global_target_explainability(self):
        """
        Property that returns all the features to be explained, ranked by their global importance by target value. Prior
         to invoking this property, the`export()` method from the `Exporter` class must have been invoked

        :return: pd.DataFrame, containing each feature ranked by its global importance by target value
        """
        if self.__global_target_explainability is not None:
            df_rows = list()
            for _, v in self.__global_target_explainability.iterrows():
                target_val = ''
                for i, val in enumerate(v):
                    if isinstance(val, str):
                        target_val = val
                        continue
                    df_rows.append([target_val, self.__global_target_explainability.columns[i], val])
            df_global_target_explainability = pd.DataFrame(df_rows, columns=[TARGET, FEATURE, IMPORTANCE])
            df_global_target_explainability[RANK] = pd.to_numeric(
                df_global_target_explainability.groupby(TARGET)[IMPORTANCE].rank(ascending=False).astype('int'),
                downcast="unsigned")
            df_global_target_explainability[IMPORTANCE] = pd.to_numeric(df_global_target_explainability[IMPORTANCE],
                                                                        downcast="float")
            return df_global_target_explainability.sort_values(by=[TARGET, RANK])
        else:
            return None

    @property
    def global_target_feature_value_explainability(self):
        """
        Property that, for each target value, returns all the pairs feature-value ranked by their global importance.
        Prior to invoking this property, the`export()` method from the `Exporter` class must have been invoked

        :return: pd.DataFrame, containing for each target value all the feature-value pairs appearing in all those
                 samples whose top1 target is equal to the target value being processed. Feature-value pair importance
                 is computed by averaging the importance of all the occurrences of that feature-value pair linked to
                 the target value being processed
        """
        if self.__global_nodes_info is not None:
            self.__global_nodes_info[NODE_IMPORTANCE] = pd.to_numeric(self.__global_nodes_info[NODE_IMPORTANCE],
                                                                      downcast="float")
            self.__global_nodes_info[RANK] = pd.to_numeric(self.__global_nodes_info[RANK], downcast="unsigned")
            return self.__global_nodes_info[[TARGET, NODE_NAME, NODE_IMPORTANCE, RANK]].rename(
                columns={NODE_NAME: FEATURE_VALUE, NODE_IMPORTANCE: IMPORTANCE})
        else:
            return None

    def __export_edges(self, df_stats: pd.DataFrame, filename: str):
        """
        This function calculates each edge weight in pixels and persists the information. This function handles local
        and global edge data

        :param df_stats:        Pandas DataFrame, containing previously calculated edge statistics
        :param filename:        String, representing the name of the file used to persist the information
        """
        df_stats[EDGE_WEIGHT] = pd.cut(df_stats[COUNT], bins=N_BINS_EDGE_WEIGHT,
                                       labels=range(MIN_EDGE_WEIGHT,
                                                    MAX_EDGE_WEIGHT + BIN_WIDTH_EDGE_WEIGHT))
        df_stats.to_json(path_or_buf=os.path.join(self.__destination_path, filename), orient='records')

    def __export_global_description(self, df_global_nodes_info: pd.DataFrame,
                                    filename: str = EXPLAINER_GLOBAL_GRAPH_DESCRIPTION_FILE):
        """
        This function calculates the number of different feature - value pairs associated to each target value. It
        persist the resulting information

        :param df_global_nodes_info:    Pandas DataFrame, containing the node global info resulting from combining the
                                        calculated statistics and the calculated importance
        :param filename:                String, representing the name of the file used to persist the information
        """
        df_global_nodes_info[[TARGET, RANK]].drop_duplicates(subset=[TARGET], keep='last').rename(
            columns={RANK: NUM_FEATURES}).to_json(path_or_buf=os.path.join(self.__destination_path, filename),
                                                  orient='records')

    def __export_global_explainability(self, df_importance: pd.DataFrame,
                                       filename: str = EXPLAINER_GLOBAL_EXPLAINABILITY_FILE) -> pd.DataFrame:
        """
        This function calculates the weight in pixels of each feature importance and persists the global explainability
        information

        :param df_importance:   Pandas DataFrame, containing the mean of each feature importance throughout all the
                                targets
        :param filename:        String, representing the name of the file used to persist the information
        :return:                Pandas Dataframe, containing the features importance values
        """
        df_importance[FEATURE_WEIGHT] = pd.cut(df_importance[FEATURE_IMPORTANCE].astype('float'),
                                               bins=N_BINS_FEATURE_WEIGHT,
                                               labels=list(range(
                                                   MIN_FEATURE_WEIGHT,
                                                   MAX_FEATURE_WEIGHT + BIN_WIDTH_FEATURE_WEIGHT,
                                                   BIN_WIDTH_FEATURE_WEIGHT)))

        df_importance.to_json(path_or_buf=os.path.join(self.__destination_path, filename), orient='records')
        return df_importance

    def __export_global_nodes_heatmap_info(self, df_local_nodes: pd.DataFrame, features_info: FeaturesInfo,
                                           target_info: TargetInfo, filename: str = EXPLAINER_GLOBAL_HEATMAP_FILE):
        """
        This function takes as main input the importance for each of the individual feature-value pair (node) and its
        corresponding target for each individual sample of the local sample. From here it generates the following
        statistics for each node (feature-value) and target pair: the frequency and the mean of the importance values

        :param features_info:  NamedTuple containing all the feature column names lists which will be used all
                               through the execution flow
        :param target_info:    NamedTuple containing a numpy array listing the top1 target for each DataFrame row,
                               another numpy array listing a probability for each possible target value and a third
                               numpy array showing the top1 targets indexes
        :param df_local_nodes: Pandas DataFrame providing the importance calculated for each individual node from the
                               local sample
        :param filename:       String, representing the name of the file used to persist the information
        """
        # Target values are count and divided by the number of features. This result will be used as the divisor to
        # compute each target-node frequency
        for t in target_info.target_columns:
            df_local_nodes.loc[df_local_nodes[TARGET] == t, TARGET_FEATURE_COUNT] = (
                        len(df_local_nodes[df_local_nodes[TARGET] == t]) / len(features_info.feature_columns))

        # The count for each target-node pairs is calculated together with the mean of their importance values. Count
        # will be divided by the previous result to compute target-node frequency
        df_local_nodes = df_local_nodes.groupby([TARGET, NODE_NAME, TARGET_FEATURE_COUNT])[NODE_IMPORTANCE].agg(
            ['count', 'mean']).reset_index()
        df_local_nodes[FREQUENCY] = df_local_nodes[COUNT] / df_local_nodes[TARGET_FEATURE_COUNT]
        df_local_nodes.rename(columns={MEAN: IMPORTANCE}, inplace=True)

        # Feature name and feature value are extracted from each node name
        for f in features_info.feature_columns:
            df_local_nodes.loc[df_local_nodes[NODE_NAME].str.startswith(f), FEATURE_NAME] = f
        df_local_nodes[FEATURE_VALUE] = df_local_nodes.apply(lambda x: x[NODE_NAME][len(x[FEATURE_NAME]) + 1:], axis=1)

        df_local_nodes[[TARGET, FEATURE_NAME, FEATURE_VALUE, IMPORTANCE, FREQUENCY]].sort_values(
            by=[TARGET, FEATURE_NAME, FEATURE_VALUE], ascending=False).to_json(
            path_or_buf=os.path.join(self.__destination_path, filename), orient='records')

    def __export_global_nodes(self, df_stats: pd.DataFrame, df_importance: pd.DataFrame,
                              filename=EXPLAINER_GLOBAL_GRAPH_NODES_FILE) -> pd.DataFrame:
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
        global_node_info.to_json(path_or_buf=os.path.join(self.__destination_path, filename), orient='records')

        return global_node_info

    def __export_global_target_distribution(self, df_global_target_distribution: pd.DataFrame,
                                            filename=EXPLAINER_GLOBAL_TARGET_DISTRIBUTION_FILE):
        """
        This function persists the information related to the number of appearances of each possible target value

        :param df_global_target_distribution:   Pandas DataFrame containing the information related to the number of
                                                appearances of each possible target value
        :param filename:                        String representing the name of the file used to persist the information
        """
        df_global_target_distribution.to_json(path_or_buf=os.path.join(self.__destination_path, filename),
                                              orient='records')

    def __export_global_target_explainability(self, df_importance: pd.DataFrame,
                                              filename: str = EXPLAINER_GLOBAL_TARGET_EXPLAINABILITY_FILE):
        """
        This function persists the global target explainability information. Note that his file will be deprecated

        :param df_importance:   Pandas DataFrame containing the mean of each feature importance for each target
        :param filename:        String representing the name of the file used to persist the information
        """
        df_importance.to_json(path_or_buf=os.path.join(self.__destination_path, filename), orient='records')

    def __export_local_dataset_reliability(self, features_info: FeaturesInfo, target_info: TargetInfo,
                                           sample_ids_mask: np.ndarray,
                                           filename: str = EXPLAINER_LOCAL_DATASET_RELIABILITY_FILE):
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
        df_local_feature_values = self.__df_explanation_sample[[ID] + features_info.feature_columns].values
        # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
        #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con valores de
        #  ese tipo
        for i, feature_col in enumerate(features_info.feature_columns):
            if feature_col in features_info.float_feature_columns:
                df_local_feature_values[:, i + 1] = np.around(df_local_feature_values[:, i + 1].astype('float'),
                                                              decimals=2)

        df_local_reliability_values = self.__df_explanation_sample[features_info.reliability_columns].values
        pd.DataFrame(np.concatenate((df_local_feature_values, target_info.top1_targets[sample_ids_mask].reshape(-1, 1),
                                     np.abs(1 - np.round(df_local_reliability_values[
                                                             np.arange(
                                                                 df_local_reliability_values.shape[
                                                                     0]), target_info.top1_argmax[sample_ids_mask]],
                                                         decimals=2)).reshape(-1, 1)), axis=1),
                     columns=[ID] + features_info.feature_columns + [TARGET] + [RELIABILITY]).to_json(
            path_or_buf=os.path.join(self.__destination_path, filename), orient='records')

        pd.DataFrame(np.concatenate((df_local_feature_values, target_info.top1_targets[sample_ids_mask].reshape(-1, 1),
                                     np.abs(1 - np.round(df_local_reliability_values[
                                                             np.arange(
                                                                 df_local_reliability_values.shape[
                                                                     0]), target_info.top1_argmax[sample_ids_mask]],
                                                         decimals=2)).reshape(-1, 1)), axis=1),
                     columns=[ID] + features_info.feature_columns + [TARGET] + [RELIABILITY]).to_json(
            path_or_buf=os.path.join(self.__destination_path, filename), orient='records')

    def __export_local_explainability(self, features_info: FeaturesInfo, target_info: TargetInfo,
                                      sample_ids_mask: np.ndarray, filename: str = EXPLAINER_LOCAL_EXPLAINABILITY_FILE):
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

        pd.DataFrame(np.concatenate((self.__df_explanation_sample[ID].values.reshape(-1, 1),
                                     self.__df_explanation_sample[features_info.importance_columns].values[
                                         np.array(adapted_importance_by_target)].reshape(
                                         len(self.__df_explanation_sample), -1),
                                     top1_targets.reshape(-1, 1)), axis=1),
                     columns=[ID] + features_info.feature_columns + [TARGET]).to_json(
            path_or_buf=os.path.join(self.__destination_path, filename), orient='records')

    def __export_local_nodes(self, df_stats: pd.DataFrame, features_info: FeaturesInfo,
                             filename=EXPLAINER_LOCAL_GRAPH_NODES_FILE) -> pd.DataFrame:
        """
        This function combines the previously calculated local statistics for the nodes, with the calculated importance.
        It calculates the weight in pixels for the node importance too and, finally, persists the resulting information

        :param df_stats:        Pandas DataFrame containing previously calculated nodes local statistics
        :param features_info:   NamedTuple containing all the feature column names lists which will be used all through
                                the execution flow
        :param filename:        String representing the name of the file used to persist the information

        :return:                Pandas DataFrame providing the importance calculated for each individual node from the
                                local sample, needed to generate another file to export to display a heatmap
                                visualization
        """
        importance_values = np.repeat(self.__df_explanation_sample.values, len(features_info.feature_columns), axis=0)
        df_stats[IMPORTANCE_FEATURE] = df_stats[TARGET] + '_' + df_stats[FEATURE_NAME] + IMPORTANCE_SUFFIX
        importance_mask = (df_stats[IMPORTANCE_FEATURE].values.reshape(-1, 1) ==
                           np.array(self.__df_explanation_sample.columns))
        node_importance = importance_values[importance_mask]
        df_stats[NODE_IMPORTANCE] = node_importance
        local_nodes_info = df_stats[[ID, NODE_NAME, NODE_IMPORTANCE, TARGET]].copy()
        local_nodes_info[RANK] = local_nodes_info.groupby(ID)[NODE_IMPORTANCE].rank(method='dense',
                                                                                    ascending=False).astype(int)
        local_nodes_info[NODE_WEIGHT] = pd.cut(local_nodes_info[NODE_IMPORTANCE].abs(),
                                               bins=N_BINS_NODE_WEIGHT,
                                               labels=list(range(
                                                   MIN_NODE_WEIGHT,
                                                   MAX_NODE_WEIGHT + BIN_WIDTH_NODE_WEIGHT,
                                                   BIN_WIDTH_NODE_WEIGHT)))
        local_nodes_info.sort_values(by=[ID, RANK]).to_json(path_or_buf=os.path.join(self.__destination_path, filename),
                                                            orient='records')
        return local_nodes_info.drop([NODE_WEIGHT, RANK], axis=1)

    def export(self, features_info: FeaturesInfo, target_info: TargetInfo, sample_ids_mask: np.ndarray,
               global_target_explainability: pd.DataFrame, global_explainability: pd.DataFrame,
               global_nodes_importance: pd.DataFrame, nodes_info: StatsResults, edges_info: StatsResults,
               target_distribution: pd.DataFrame):
        self.__global_target_explainability = global_target_explainability
        xgprint(self.__verbose, 'INFO:     Exporting data to {}'.format(self.__destination_path))
        if not os.path.exists(self.__destination_path):
            os.mkdir(self.__destination_path)

        self.__export_local_explainability(features_info=features_info, target_info=target_info,
                                           sample_ids_mask=sample_ids_mask)

        self.__export_local_dataset_reliability(features_info=features_info, target_info=target_info,
                                                sample_ids_mask=sample_ids_mask)

        local_nodes_info = self.__export_local_nodes(df_stats=nodes_info.local_stats, features_info=features_info)

        self.__export_global_nodes_heatmap_info(df_local_nodes=local_nodes_info, features_info=features_info,
                                                target_info=target_info)

        self.__export_edges(df_stats=edges_info.local_stats, filename=EXPLAINER_LOCAL_GRAPH_EDGES_FILE)

        self.__export_global_target_explainability(df_importance=global_target_explainability)

        self.__global_explainability = self.__export_global_explainability(df_importance=global_explainability)

        self.__global_nodes_info = self.__export_global_nodes(df_stats=nodes_info.global_stats,
                                                              df_importance=global_nodes_importance)

        self.__export_global_description(df_global_nodes_info=self.__global_nodes_info)

        self.__export_global_target_distribution(df_global_target_distribution=target_distribution)

        self.__export_edges(df_stats=edges_info.global_stats, filename=EXPLAINER_GLOBAL_GRAPH_EDGES_FILE)
