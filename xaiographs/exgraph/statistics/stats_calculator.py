import itertools
from typing import Any, List, NamedTuple, Tuple

import numpy as np
import pandas as pd

from xaiographs.common.constants import COUNT, FEATURE_NAME, ID, NODE_1, NODE_2, NODE_COUNT, NODE_NAME, \
    NODE_NAME_RATIO, NODE_NAME_RATIO_RANK, TARGET, TOTAL_COUNT
from xaiographs.common.utils import filter_by_ids


class StatsResults(NamedTuple):
    """StatsResults provides the structure to store both, global and local calculated statistics
    """
    global_stats: pd.DataFrame
    local_stats: pd.DataFrame


class StatsCalculator(object):
    """
    This class is intended to take care of everything related to frequency calculations, counting, etc. This isn't the
    place to look for importance calculation or references
    """
    def __init__(self, df: pd.DataFrame, top1_targets: np.ndarray, feature_cols: List[str],
                 float_feature_cols: List[str],  target_cols: List[str], sample_ids_mask: np.ndarray,
                 sample_ids: List[Any]):
        """
        Constructor method for StatsCalculator

        :param df:                  Pandas DataFrame containing the provided dataset
        :param top1_targets:        Numpy array containing the top1_target for each row
        :param feature_cols:        List of strings containing the column names for the features
        :param float_feature_cols:  List of strings containing the column names for the float type features
        :param sample_ids_mask:     Numpy array containing boolean values which will be used to filter any given
                                    DataFrame
        :param target_cols:         List of strings containing the column names for the target/s
        :param sample_ids:          List of ids which will be part of the sample
        """
        self.df = df
        self.top1_targets = top1_targets
        self.feature_cols = feature_cols
        self.float_feature_cols = float_feature_cols
        self.target_cols = target_cols
        self.sample_ids_mask = sample_ids_mask
        self.sample_ids = sample_ids

    def __calculate_edges_stats(self) -> StatsResults:
        """
        This method computes the local and global edges statistics for a given pandas DataFrame. These calculations
        consist on the number of appearances of each edge for each top1 target in the global case which are, then,
        propagated to the local case. Bear in mind that, for the local edges, a sample ids mask will be applied so that
        only certain ids will be taken into account

        :return:    StatsResult object comprising both, the local and the global information related to the graph edges
        """
        # A copy is done to avoid mutation side effects
        df_example = self.df.copy()

        # First, edges global stats are computed. For each feature column name, all feature_value node names are
        # generated (float feature values require special treatment)
        for feature_col in self.feature_cols:
            if feature_col in self.float_feature_cols:
                # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
                #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con
                #  valores de ese tipo
                df_example[feature_col] = feature_col + '_' + df_example[feature_col].apply(
                    "{:.02f}".format).map(str)
            else:
                df_example[feature_col] = feature_col + '_' + df_example[feature_col].map(str)

        # Now all possible feature_value combinations (order doesn't matter) are generated
        df_example[TARGET] = self.top1_targets
        feature_cols_combinations = itertools.combinations(self.feature_cols, 2)
        df_global_graph_edges_list = []
        df_local_graph_edges_list = []
        for feature_cols_tuple in feature_cols_combinations:
            feature_cols_pair = list(feature_cols_tuple)

            # Same loop is used to generate local and global parts: ID is taken into account for the local part
            # top1_target is taken into account for the global part in which counting is done
            df_local_graph_edges_list.append(df_example[[ID, TARGET] + feature_cols_pair].rename(
                columns={feature_cols_pair[0]: NODE_1, feature_cols_pair[1]: NODE_2}))
            df_global_graph_edges_list.append(
                df_example[[TARGET] + feature_cols_pair].value_counts().reset_index(name=COUNT).rename(
                    columns={feature_cols_pair[0]: NODE_1, feature_cols_pair[1]: NODE_2}))

        df_global_graph_edges = pd.concat(df_global_graph_edges_list).sort_values(
            by=[TARGET, NODE_1, NODE_2]).reset_index(drop=True)

        # Once global stats are ready, local examples can be joined on those, so that the global count can be applied
        # to them
        df_local_graph_edges_raw = pd.concat(df_local_graph_edges_list).sort_values(
            by=[ID, NODE_1, NODE_2]).reset_index(drop=True)

        # Sample ids mask is applied
        df_local_graph_edges_sample_raw = filter_by_ids(df=df_local_graph_edges_raw,
                                                        sample_id_mask=self.sample_ids_mask,
                                                        n_repetitions=int(len(df_local_graph_edges_raw)/len(self.df)))

        # IDs present in resulting sample must match te sample ids
        assert np.array_equal(np.unique(np.sort(df_local_graph_edges_sample_raw[ID].astype('str').values)),
                              np.sort(self.sample_ids)), "Something went wrong when sampling local edges"
        df_local_graph_edges_sample = df_local_graph_edges_sample_raw.merge(df_global_graph_edges, how='left',
                                                                            on=[TARGET, NODE_1, NODE_2])
        return StatsResults(global_stats=df_global_graph_edges, local_stats=df_local_graph_edges_sample)

    def __calculate_nodes_stats(self) -> StatsResults:
        """
        This method computes the local and global nodes statistics. For the moment there's no actual aggregation to
        compute for the local case, but only a table containing feature_value pairs for each ID, together with their
        top1 target and feature. From here some counts and aggregations will be done in order to obtain the frequency
        for each feature_value pair, this will become the global case. Bear in mind that, for the local nodes, a sample
        ids mask will be applied so only certain ids will be taken into account

        :return:    StatsResult object comprising both, the local and the global information related to the graph nodes
        """
        all_columns = list(self.df.columns)
        df_values = self.df.values
        graph_nodes_info = []

        # First, for each feature column name, all feature_value node names are generated (float feature values require
        # special treatment)
        for i, row in enumerate(df_values):
            for feature_col in self.feature_cols:
                feature_value_raw = row[all_columns.index(feature_col)]
                if feature_col in self.float_feature_cols:
                    # TODO: Para ciertos float, la representación puede dispararse en cuanto a número de decimales
                    #  Habría que ver una manera de especificar el tope de precisión a garantizar para las features con
                    #  valores de ese tipo
                    feature_value = '_'.join([feature_col, "{:.02f}".format(feature_value_raw)])
                else:
                    feature_value = '_'.join([feature_col, feature_value_raw])

                graph_nodes_info.append([row[0], feature_value, feature_col, self.top1_targets[i]])

        # For the moment this is all the information for the local graph nodes statistics. This will be used later,
        # combined with the Importance calculation part
        df_local_graph_nodes = pd.DataFrame(graph_nodes_info, columns=[ID, NODE_NAME, FEATURE_NAME, TARGET])
        print("df_local_graph_nodes.shape")
        print(df_local_graph_nodes.shape)

        # For the global part, feature_value frequencies are computed. Note that thw whole local nodes information is
        # taken into account
        df_global_graph_nodes = df_local_graph_nodes.groupby(NODE_NAME)[NODE_NAME].count().reset_index(name=NODE_COUNT)
        df_global_graph_nodes[TOTAL_COUNT] = len(self.df)
        df_global_graph_nodes[NODE_NAME_RATIO] = df_global_graph_nodes[NODE_COUNT] / df_global_graph_nodes[TOTAL_COUNT]
        df_global_graph_nodes[NODE_NAME_RATIO_RANK] = (
            df_global_graph_nodes[NODE_NAME_RATIO].rank(method='dense', ascending=False).astype(int))

        # Sample ids mask is applied to the local nodes before returning the information
        df_local_graph_nodes_sample = filter_by_ids(df=df_local_graph_nodes,
                                                    sample_id_mask=self.sample_ids_mask,
                                                    n_repetitions=int(len(df_local_graph_nodes) / len(self.df)))

        # IDs present in resulting sample must match te sample ids
        assert np.array_equal(np.unique(np.sort(df_local_graph_nodes_sample[ID].astype('str').values)),
                              np.sort(self.sample_ids)), "Something went wrong when sampling local nodes"

        return StatsResults(global_stats=df_global_graph_nodes, local_stats=df_local_graph_nodes_sample)

    def __calculate_global_target_distribution(self) -> pd.DataFrame:
        """
        This method counts the appearances of each possible target value

        :return: Pandas DataFrame containing the count for each possible target value
        """
        return pd.DataFrame(np.concatenate((np.array(self.target_cols).reshape(-1, 1),
                                            np.sum(self.df[self.target_cols].values, axis=0).reshape(-1, 1)), axis=1),
                            columns=[TARGET, COUNT])

    def calculate_stats(self) -> Tuple[StatsResults, StatsResults, pd.DataFrame]:
        """
        This method is intended to orchestrate the execution of nodes, edges and targets statistics. It's meant to be
        an abstraction layer over those atomic methods

        :return: Tuple containing a StatsResults object to store edges statistics, another StatsResults object to store
                 nodes statistics and a pandas DataFrame to store target values counts
        """
        edges_stats = self.__calculate_edges_stats()
        nodes_stats = self.__calculate_nodes_stats()
        target_distribution = self.__calculate_global_target_distribution()

        return edges_stats, nodes_stats, target_distribution