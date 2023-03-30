# -*- coding: utf-8 -*-

u"""
© 2023 Telefónica Digital España S.L.
This file is part of XAIoGraphs.

XAIoGraphs is free software: you can redistribute it and/or modify it under the terms of the Affero GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

XAIoGraphs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Affero GNU General Public License
for more details.

You should have received a copy of the Affero GNU General Public License along with XAIoGraphs. If not,
see https://www.gnu.org/licenses/."""


from itertools import combinations
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import scipy
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from xaiographs.common.constants import ID, IMPORTANCE_SUFFIX, RELIABILITY
from xaiographs.common.utils import TargetInfo, xgprint
from xaiographs.exgraph.importance.importance_calculator import ImportanceCalculator


class LIDE(ImportanceCalculator):
    """
    This class implements ImportanceCalculator based on the mathematical Shapley values formula
    """
    _COALITIONS = 'coalitions'
    _COALITION_NAME_SEP = '_'
    _COALITIONS_WEIGHTS = 'coalitions_weights'
    _COALITIONS_WORTH = 'coalitions_worth'
    _DF_TO_EXPLAIN = 'df_to_explain'
    _E = 'E'
    _EDGES = 'edges'
    _MODEL = 'model'
    _RES_DICT = 'res_dict'
    _WEIGHTS = 'weights'

    def __init__(self, explainer_params: Dict, feature_cols: List[str], target_info: TargetInfo,
                 train_size: float = 0.0, train_stratify: bool = False, verbose: int = 0):
        """
        Constructor method for LIDE ImportanceCalculator

        :param explainer_params:            Dictionary, containing potentially useful information for this importance
                                            calculator
        :param feature_cols:                List of strings, containing the column names for the features
        :param target_info:                 NamedTuple, containing a numpy array listing the top1 target for each
                                            DataFrame row, another numpy array listing a probability for each possible
                                            target value and a third numpy array showing the top1 targets indexes
        :param train_size:                  Float, indicating the percentage of the pandas DataFrame that will be used
                                            to train the calculator
        :param train_stratify:              Boolean, indicating whether target columns proportions will be taken into
                                            account when splitting the data (if train_size > 0.0)
        :param verbose:                     Verbosity level, where any value greater than 0 means the message is printed
        """
        super(LIDE, self).__init__(feature_cols=feature_cols, target_info=target_info, train_size=train_size,
                                   train_stratify=train_stratify, verbose=verbose)
        self.explainer_params: Dict = explainer_params

    @staticmethod
    def __build_coalitions_graph(num_features: int, verbose: int) -> Tuple[List[str], List[int], List[List[int]]]:
        """
        This method is intended to build the so-called coalitions template which consists of: a list containing the
        coalitions names, another list containing the coalitions identifiers (an integer which univocally identifies
        each coalition) and a third structure which is a list of lists so that all the coalitions ids contained in each
        sublist, belong to coalitions of the same length

        :param num_features: Integer, representing the number of features for which coalitions will be built
        :param verbose:      Verbosity level, where any value greater than 0 means the message is printed
        :return:             Three structures:
                             - List of strings, containing the coalitions names
                             - List of integers, containing the coalitions ids
                             - List of lists, so that all the coalitions ids contained in each sublist, belong to
                             coalitions of the same length
        """
        # A list containing an integer to identify each coalition, they'll be sequentially generated
        coalition_ids = []

        # A list of lists. Each sublist contains all the ids of those coalitions of a given length. The first sublist
        # the ids of those coalitions with length 0 (the empty coalition), the second the ids of those coalitions with
        # length 1 and so forth
        coalition_lengths = []

        # A list containing the coalition names in terms of: 'E': empty coalition, '0': feature 0, '1': feature 1 ...
        coalition_names = []
        coalition_id = 0

        # Features are listed by their position: from 0 to feature_num - 1
        feature_list = [j for j in range(num_features)]

        pbar = tqdm(range(num_features + 1), disable=not verbose)
        pbar.set_description('INFO:     Coalitions template')
        for i in pbar:
            coalition_ids_by_length = []

            # For all possible combinations of i features (from 0 to num_features)
            for combination in list(combinations(feature_list, i)):
                coalition_name = [LIDE._E]
                for el in combination:
                    coalition_name.append(str(el))
                coalition_names.append(LIDE._COALITION_NAME_SEP.join(coalition_name))
                coalition_ids_by_length.append(coalition_id)
                coalition_ids.append(coalition_id)
                coalition_id += 1
            coalition_lengths.append(coalition_ids_by_length)

        return coalition_names, coalition_ids, coalition_lengths

    @staticmethod
    def __build_computational_graph(features_num: int,
                                    coalition_names: List[str],
                                    coalition_lengths: List[List[int]],
                                    verbose: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """
        This method builds the computational graph for each feature. It requires the list of coalition names and the
        lists of coalitions ids grouped by their length in order to calculate the graph edges.

        :param features_num:        Integer, representing the number of features
        :param coalition_names:     List of strings, containing the coalitions names
        :param coalition_lengths:   List of lists of integers, containing for each possible coalition length, the
                                    coalitions ids for those coalitions with the given length
        :param verbose:             Verbosity level, where any value greater than 0 means the message is printed
        :return:                    Tuple of numpy arrays in returned:
                                    - Numpy array, containing the edges for each feature. Edges are represented by a
                                    list of output nodes and a list of input nodes (both per feature)
                                    - Numpy array, containing the result of dividing the weights for each coalition by
                                    the computed degree for the input coalitions
        """
        # A weight is computed for each coalition
        weights = np.expand_dims(np.expand_dims([1 if j == 0
                                                 else 1 / (scipy.special.comb(features_num - 1,
                                                                              len(name.split(
                                                                                  LIDE._COALITION_NAME_SEP)) - 2) * (
                                                               features_num)) for j, name in
                                                 enumerate(coalition_names)], axis=0), axis=2)
        edges_list = []
        weights_list = []
        pbar = tqdm(range(features_num), disable=not verbose)
        pbar.set_description('INFO:     Computational graph')
        for pi in pbar:
            f = str(pi)
            edges = [[], []]
            for i in range(1, len(coalition_lengths)):

                # A list of the output (origin) nodes and another list with their corresponding input (destination)
                # nodes are obtained for all the coalitions of the given length `i` and involving the given feature `f`
                # For every output/input coalition pair, the output coalition won't contain the given feature `f` but
                # the input coalition will
                input_nodes, output_nodes = LIDE.__compute_edges(coalition_lengths=coalition_lengths,
                                                                    coalition_names=coalition_names,
                                                                    coalition_length=i, feature=f)
                if len(input_nodes):
                    edges[1].extend(input_nodes)
                if len(output_nodes):
                    edges[0].extend(output_nodes)
            edges_list.append(edges)

            # Weights are stored for the input nodes
            weights_list.append(weights.squeeze()[edges[1]].tolist())
        edges = np.array(edges_list)

        degrees = []

        # Degrees are computed for the input nodes
        for i in range(edges.shape[0]):
            degrees.append(LIDE.__get_degree(edges[i, 1, :]))
        degrees = np.stack(degrees, axis=0)
        filtered_degrees = []
        for i in range(edges.shape[0]):
            filtered_degrees.append(degrees[i, edges[i, 1, :]])
        filtered_degrees = np.stack(filtered_degrees, axis=0)
        return edges, np.array(weights_list)/filtered_degrees

    @staticmethod
    def __build_features_graph(df_2_explain: pd.DataFrame, df_train: pd.DataFrame,
                               target_cols: List[str], coalition_names: List[str], verbose: int = 0) -> np.ndarray:
        """
        This method computes for each coalitions features a target aggregation (averaging) by previously grouping by
        those features in the train DataFrame. The result is propagated to those samples to be explained whose features
         values match the grouped features. This way the coalitions worth are computed

        :param df_2_explain:    Pandas DataFrame, containing the samples to be explained
        :param df_train:        Pandas DataFrame, containing the training dataset
        :param target_cols:     List of strings, containing the possible targets
        :param coalition_names: List of strings, containing the coalitions names
        :param verbose:         Verbosity level, where any value greater than 0 means the message is printed
        :return:                Numpy matrix, containing the coalitions worth. For each sample to be explained a worth is
                                calculated per coalition and per target (n_samples x n_coalitions x n_target_cols)
        """
        coalitions_worth = []
        pbar = tqdm(range(len(coalition_names)), disable=not verbose)
        pbar.set_description('INFO:     Coalition features')

        # For each coalition its name will be processed
        for i in pbar:
            coalition_name = coalition_names[i]
            coalition_features = coalition_name.split(LIDE._COALITION_NAME_SEP)

            # Features list for that coalition are obtained
            coalition_features.remove(LIDE._E)
            if len(coalition_features) > 0:

                # Aggregated targets are computed by grouping and averaging the coalition features on the
                # train DataFrame. Then the DataFrame to be explained is joined on those features so that aggregated
                # target is spread out to the samples to be explained
                # coalition worths consists only of those aggregated targets
                coalitions_worth.append(pd.merge(df_2_explain[[ID] + coalition_features],
                                                 df_train.groupby(coalition_features)[target_cols].mean().reset_index(),
                                                 on=coalition_features,
                                                 how='inner').sort_values(by=[ID])[target_cols].values)
            else:

                # If the coalition being processed is the empty coalition (phi0), the target is aggregated throughout
                # the whole train DataFrame
                tmp = df_train[target_cols].mean().values
                coalitions_worth.append(np.stack([tmp for _ in range(len(df_2_explain))], axis=0))
        coalitions_worth = np.stack(coalitions_worth, axis=0).transpose(1, 0, 2)

        return coalitions_worth

    @staticmethod
    def __compute_edges(coalition_lengths: List[List[int]], coalition_names: List[str], coalition_length: int,
                        feature: str) -> Tuple[List[int], List[int]]:
        """
        This method computes all possible edges for a given feature and a given coalition length. The rule to be
        observed is that for the given feature, the output node for a valid edge can't contain the feature and the
        input (destination) node, must contain it. Furthermore, the features conforming the output node coalition name
         must be a subset of the features conforming the input node coalition name.
         For example, for feature 0, these are valid edges (output_node -> input_node): E -> E_0, E_1 -> E_1_0,
          E_2 -> E_2_0, E_1_2 -> E_0_1_2 ...

        :param coalition_lengths:   List of lists of integers, containing for each possible coalition length, the
                                    coalitions ids for those coalitions with the given length
        :param coalition_names:     List of strings, containing the coalitions names
        :param coalition_length:    Integer, representing the coalition length being processed
        :param feature:             String, representing the feature being processed
        :return:                    Tuple of two lists, representing edges:
                                    - List of integers, containing the ids of the coalitions being a valid output node
                                     for an edge.
                                    - List of integers, containing the ids of the coalitions being a valid input node for
                                    an edge
        """
        input_nodes = []
        output_nodes = []
        for output_node in coalition_lengths[coalition_length - 1]:

            # For an output node to be valid to be part of an edge, the processed feature can't be contained on its name
            if feature in coalition_names[output_node].split(LIDE._COALITION_NAME_SEP):
                continue
            for input_node in coalition_lengths[coalition_length]:

                # For an input node to be valid to be part of an edge, the processed feature must be contained on its
                # name
                if feature not in coalition_names[input_node].split(LIDE._COALITION_NAME_SEP):
                    continue
                if set(coalition_names[output_node].split(LIDE._COALITION_NAME_SEP)).issubset(
                        set(coalition_names[input_node].split(LIDE._COALITION_NAME_SEP))):
                    input_nodes.append(input_node)
                    output_nodes.append(output_node)

        return input_nodes, output_nodes

    @staticmethod
    def __get_degree(a: np.ndarray) -> np.ndarray:
        """
        This method computes the degrees for each element of the given numpy array of integers. The degree is actually
        a count of each element appearances, absent elements will have a degree of 0. For instance, given the numpy
        array [4, 2, 2, 2, 1] the degrees array will be [0, 1, 3, 0, 1]. Those numbers not present and less than the
        maximum (4) are taken into account to compute the degrees (their degree is 0)

        :param a:   Numpy array of integers, for which degrees will be computed
        :return:    Numpy array of integers, containing the computed degrees for each of the integers of the given
                    array, but also for those absent whose value is less than the maximum of the present elements
        """
        values, counts = np.unique(a, return_counts=True)
        degrees = np.zeros(np.max(a) + 1)
        np.put(degrees, values, counts)
        return degrees

    @staticmethod
    def __graph_importance(features: np.ndarray,
                           graph_edges: np.ndarray,
                           weights: np.ndarray,
                           batch_size: int,
                           verbose: int) -> np.ndarray:
        """
        This method takes care of computing the importance. It uses a graph neural network for this purpose

        :param features:    Numpy matrix, containing the coalitions worth. For each sample to be explained a worth is
                            calculated per coalition and per target
        :param graph_edges: Numpy array, containing the edges for each feature. Edges are represented by a list of
                            output nodes and a list of input nodes (both per feature)
        :param weights:     Numpy array, containing the weights for each coalition
        :param batch_size:  Integer, representing the batch size to be used during importance calculation
        :param verbose:     Verbosity level, where any value greater than 0 means the message is printed
        :return:            Numpy matrix, containing the calculated importance. For each row of the DataFrame to explain
                            an importance value per feature and per target is computed
        """
        tot_shap_values = []

        # Number of batches is calculated
        batch_num = features.shape[0] // batch_size
        if features.shape[0] % batch_size > 0:
            batch_num += 1
        pbar = tqdm(range(batch_num), disable=not verbose)
        pbar.set_description('Explanation')
        for n_batch in pbar:
            shap_values = []
            for f in range(weights.shape[0]):
                # Batch shape is (batch_size x number of coalitions x number of target values)
                batch = features[batch_size * n_batch:batch_size * (n_batch + 1), :, :]

                # Shap value shape is (batch_size x number of target values)
                shap_value = ((batch[:, graph_edges[f, 1, :], :] - batch[:, graph_edges[f, 0, :], :])
                              * np.expand_dims(np.expand_dims(weights[f, :], axis=0), axis=2)).sum(axis=1)
                shap_values.append(shap_value)

            # Shap values shape is (batch_size x number of features to explain x number of target values)
            shap_values = np.stack(shap_values, axis=0).transpose(1, 0, 2)
            tot_shap_values.append(shap_values)

        # Tot shap values shape is (num_samples_global_expl x number of features to explain x number of target values)
        return np.concatenate(tot_shap_values, axis=0)

    def local_explain(self, batch_size: int, **params) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        """
        This method takes care of computing importance for the dataset to be explained (sampled during the train
        process). The core of importance calculation is the `__graph_importance` method. The calculated importance
        obtained from it, is adjusted to the ground truth, obtaining the so-called reliability. This sort of error
        called reliability, is distributed among the considered features and added to the calculated importance
        resulting in the adapted importance which will populate the importance columns of the "explained" DataFrame .
         The reliability is stored in the reliability columns of the "explained" DataFrame too.
        There will be an importance column per feature and per target and a reliability column per target.

        :param batch_size:  Integer, representing the size of the batches (chunks) on which importance will be
                            calculated
        :param params:      Dictionary, containing four elements:
                            - df_to_explain:    Pandas DataFrame, consisting of a sample of the train pandas DataFrame
                            - coalitions_worth: Numpy matrix, containing the coalitions worth. For each sample to be
                                                explained a worth is calculated per coalition and per target
                                                (n_samples x n_coalitions x n_target_cols)
                            - edges:            Numpy array, containing the edges for each feature. Edges are
                                                represented by a list of output nodes and a list of input nodes (both
                                                 per feature)
                            - weights:          Numpy array, containing the result of dividing the weights for each
                                                coalition by the computed degree for the input coalitions (nodes)

        :return:            Dictionary containing two elements:
                            - df_explanation:    Pandas DataFrame, which has been explained
                            - importance_values: Numpy matrix, containing for each sample the importance of each feature
                                                 associated to each target value
        """
        # Fifth step (continuing from train method), in this step importance is calculated. The result does have the
        # following shape (rows to explain x features x targets)
        calculated_importance = self.__graph_importance(features=params[LIDE._COALITIONS_WORTH],
                                                        graph_edges=params[LIDE._EDGES],
                                                        weights=params[LIDE._WEIGHTS],
                                                        batch_size=batch_size,
                                                        verbose=self._verbose)

        # In this sixth step, a consistency check is performed on local accuracy
        #    a) coalitions_worth[:, 0, :] --> phi0 = E(targets | empty coalition)
        phi0 = params[LIDE._COALITIONS_WORTH][:, 0, :]

        #    b) coalitions_worth[:, -1, :] --> ground truth = E(targets | coalition to be justified)
        y_hat: np.ndarray = phi0 + calculated_importance.sum(axis=1)
        ImportanceCalculator._sanity_check(ground_truth=params[LIDE._COALITIONS_WORTH][:, -1, :],
                                           prediction=y_hat,
                                           target_cols=self._target_info.target_columns,
                                           scope='aggregated')

        # Ground truth is retrieved
        y: np.ndarray = params[LIDE._DF_TO_EXPLAIN][self._target_info.target_columns].values

        # Difference between ground truth and predictions
        reliability: np.ndarray = (y - y_hat)

        # Adapted importance results from adding the calculated importance plus the reliability divided by the
        # number of features
        adapted_importance: np.ndarray = calculated_importance + np.expand_dims(reliability /
                                                                                calculated_importance.shape[1], axis=1)
        reshaped_adapted_importance = adapted_importance.reshape(adapted_importance.shape[0], -1)

        df_explanation = params[LIDE._DF_TO_EXPLAIN].rename(columns={str(k): v for k, v in
                                                                        enumerate(self._feature_cols)})
        del params[LIDE._DF_TO_EXPLAIN]

        importance_columns = []
        for c in self._feature_cols:
            for target_col in self._target_info.target_columns:
                importance_columns.append('{}_{}{}'.format(target_col, c, IMPORTANCE_SUFFIX))

        # TODO: Chequear para el target top1 que PHI0 + adapted shapley es mayor que 0 para cada ID
        for i, c in enumerate(importance_columns):
            df_explanation[c] = reshaped_adapted_importance[:, i]

        for j, target_col in enumerate(self._target_info.target_columns):
            reliability_column = '{}_{}'.format(target_col, RELIABILITY)
            df_explanation[reliability_column] = reliability[:, j]

        # Data is formatted for the sanity check
        y_hat_reduced = phi0 + np.sum(df_explanation[importance_columns].values.reshape(-1, adapted_importance.shape[1],
                                                                                        adapted_importance.shape[2]),
                                      axis=1)
        ImportanceCalculator._sanity_check(ground_truth=y, prediction=y_hat_reduced,
                                           target_cols=self._target_info.target_columns, scope='original')
        return {
           ImportanceCalculator._DF_EXPLANATION_IC: df_explanation,
           ImportanceCalculator._IMPORTANCE_VALUES_IC: adapted_importance
        }

    def train(self, df: pd.DataFrame,
              num_samples_to_explain: int) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        """
        This method takes care of the train part which ends up in the coalitions worth being calculated. Before this,
        the coalitions template and the computational graph are built.

        :param df:                      Pandas DataFrame, containing the loaded dataset with the selected features
        :param num_samples_to_explain:  Integer, representing the number of samples to be (globally) explained

        :return:                        Dictionary containing four elements:
                                        - df_to_explain:    Pandas DataFrame, consisting of a sample of the train pandas
                                                            DataFrame
                                        - coalitions_worth: Numpy matrix, containing the coalitions worth. For each
                                                            sample to be explained a worth is calculated per coalition
                                                             and per target (n_samples x n_coalitions x n_target_cols)
                                        - edges:            Numpy array, containing the edges for each feature. Edges
                                                            are represented by a list of output nodes and a list of
                                                            input nodes (both per feature)
                                        - weights:          Numpy array, containing the weights for each coalition
        """
        if self._train_size > 0.0:
            xgprint(self._verbose, 'INFO:          train_size: {}'.format(self._train_size))
            if self._train_stratify:
                xgprint(self._verbose, 'INFO:          stratifying on target: {}'.
                        format(self._target_info.target_columns))
                df_train, _ = train_test_split(df, train_size=self._train_size,
                                               stratify=df[self._target_info.target_columns])
            else:
                df_train, _ = train_test_split(df, train_size=self._train_size)
        else:
            xgprint(self._verbose, 'INFO:          the whole dataset will be used to train')
            df_train = df.copy()
        df_train.drop(ID, axis=1, inplace=True)

        # First step consists of retrieving the number of samples to be globally explained
        xgprint(self._verbose, 'INFO:          sampling the dataset to be globally explained: {} samples will be '
                               'used ...'.
                format(num_samples_to_explain))
        df_2_explain = ImportanceCalculator.sample_global(df=df.copy(), top1_targets=self._target_info.top1_targets,
                                                          num_samples=num_samples_to_explain,
                                                          target_probs=self._target_info.target_probs,
                                                          target_cols=self._target_info.target_columns)
        del df

        # Second step is to build the coalitions template and setup an order
        num_features = len(self._feature_cols)
        coalition_names, coalition_ids, coalition_lengths = self.__build_coalitions_graph(num_features, self._verbose)

        # Third step is to build computational graphs, there'll be one per feature
        # node_names = E, E_0, E_1, E_2, E_0_1, E_0_2, E_1_2, E_0_1_2
        # shapley var = 0 --> [[E, E_1, E_2, E_1_2], [E_0, E_0_1, E_0_2, E_0_1_2]]
        # shapley var = 1 --> [[E, E_0, E_2, E_0_2], [E_1, E_0_1, E_1_2, E_0_1_2]]
        # shapley var = 2 --> [[E, E_0, E_1, E_1_2], [E_2, E_0_2, E_1_2, E_0_1_2]]
        # edges = [ [[E, E_1, E_2, E_1_2], [E_0, E_0_1, E_0_2, E_0_1_2]],
        #           [[E, E_0, E_2, E_0_2], [E_1, E_0_1, E_1_2, E_0_1_2]],
        #           [[E, E_0, E_1, E_1_2], [E_2, E_0_2, E_1_2, E_0_1_2]]]
        edges, weights = self.__build_computational_graph(num_features, coalition_names, coalition_lengths,
                                                          self._verbose)

        # Fourth step consists of computing the coalitions worth
        df_train = df_train.rename(columns={v: str(k) for k, v in enumerate(self._feature_cols)})
        df_2_explain = df_2_explain.rename(columns={v: str(k) for k, v in enumerate(self._feature_cols)})
        coalitions_worth = self.__build_features_graph(df_2_explain, df_train, self._target_info.target_columns,
                                                       coalition_names, self._verbose)

        return {
            LIDE._DF_TO_EXPLAIN: df_2_explain,
            LIDE._COALITIONS_WORTH: coalitions_worth,
            LIDE._EDGES: edges,
            LIDE._WEIGHTS: weights
        }
