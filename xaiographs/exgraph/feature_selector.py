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


from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.special import rel_entr

from xaiographs.common.constants import FEATURE, RANK, TARGET
from xaiographs.common.utils import TargetInfo, xgprint

# CONSTANTS
DISTANCE = 'distance'

# Warning message
WARN_MSG = 'WARNING: {} is empty, because nothing has been processed. Execute explain() function to get results.'


class FeatureSelector(object):
    """
    This class implements the functionality of selecting the top k most relevant features
    """

    def __init__(self, df: pd.DataFrame, feature_cols: List[str], target_info: TargetInfo, number_of_features: int,
                 verbose: int = 0):
        """
        Constructor method for FeatureSelector class.
        - Property `top_features_by_target` has been included so that the FeatureSelector object can be
        inspected after method `select_topk` is invoked. This will provide distance and rank information for each
        feature and target value, so that results can be understood
        - Property `top_features_` has been included. After invoking method `select_topk`, this property will provide
        a list with the all the original features ranked

        :param df:                  Pandas DataFrame, containing the whole dataset
        :param feature_cols:        List of strings, containing the column names for the features
        :param target_info:         NamedTuple, containing a numpy array listing the top1 target for each DataFrame row,
                                    another numpy array listing a probability for each possible target value and a third
                                    numpy array showing the top1 targets indexes
        :param number_of_features:  Integer, representing the number of features to be selected
        :param verbose:             Verbosity level, where any value greater than 0 means the message is printed
        """
        self.__df = df[feature_cols].copy()
        self.__df[TARGET] = target_info.top1_targets
        self.__feature_cols = feature_cols
        self.__k = number_of_features
        self.__target_values = target_info.target_columns
        self.__top_features_by_target = dict()
        self.__top_features = []
        self.__verbose = verbose
        xgprint(self.__verbose, 'INFO: Instantiating FeatureSelector to select the top {} features:'.format(self.__k))

    @property
    def top_features(self):
        """
        Property that returns all the features ranked by the `FeatureSelector`. Prior to invoking this property, the
        `select_topk()` method from the `FeatureSelector` class must have been invoked

        :return: pd.DataFrame, with all the features ranked by the `FeatureSelector`
        """
        if len(self.__top_features):
            df_top_features = pd.DataFrame(zip(self.__top_features, list(range(1, len(self.__top_features) + 1))),
                                           columns=[FEATURE, RANK])
            df_top_features[RANK] = pd.to_numeric(df_top_features[RANK], downcast="unsigned")
            return df_top_features
        else:
            return None

    @property
    def top_features_by_target(self):
        """
        Property that returns, for each target value, all the features ranked by the `FeatureSelector`. This property is
        provided as a way to undestand the feature selection process. For each target value the distance and rank for
        each feature is returned
        Prior to invoking this property, the `select_topk()` method from the `FeatureSelector` class must have been
        invoked

        :return: pd.DataFrame, with all the features ranked by the `FeatureSelector`
        """
        if len(self.__top_features_by_target):
            df_top_features_by_target = pd.DataFrame(
                [[target] + list(fd) for target, feat_dist in self.__top_features_by_target.items() for fd in
                 feat_dist], columns=[TARGET, FEATURE, DISTANCE])
            df_top_features_by_target[DISTANCE] = pd.to_numeric(df_top_features_by_target[DISTANCE],
                                                                downcast="float")
            return df_top_features_by_target
        else:
            return None

    @staticmethod
    def __compute_jensen_shannon(dist1: np.ndarray, dist2: np.ndarray, axis: int = 0, keepdims=True) -> np.ndarray:
        """
        This is an alternative version of the Jensen Shannon distance,
        (https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html)
        Multiple aggregation functions are used to balance their individual pros and cons

        :param dist1:     Numpy array, containing a probability distribution
        :param dist2:     Numpy array, containing another probability distribution
        :param axis:      Integer, representing the axis along which the Jensen-Shannon distances are computed
                          (default 0)
        :param keepdims:  Boolean, if set to True, the reduced axes are left in the result as dimensions with size
                          one. With this option, the result will broadcast correctly against the input array.
                          (default False)

        :return:          Float or np.ndarray, (depending on the input shape) containing the calculated statistics
        """
        dist1 = dist1 if isinstance(dist1, np.ndarray) else np.asarray(dist1)
        dist2 = dist2 if isinstance(dist2, np.ndarray) else np.asarray(dist2)
        dist1 = dist1 / np.sum(dist1, axis=axis, keepdims=keepdims)
        dist2 = dist2 / np.sum(dist2, axis=axis, keepdims=keepdims)
        m = (dist1 + dist2) / 2.0
        left = rel_entr(dist1, m)
        right = rel_entr(dist2, m)
        js_msa = (left + right) / 2.0

        return np.array([np.sqrt(np.median(js_msa)),
                         np.sqrt(np.mean(js_msa)),
                         np.sqrt(np.max(js_msa)),
                         np.sqrt(np.sum(js_msa))])

    @staticmethod
    def __compute_probabilities(feature_by_target: pd.Series, unique_values: np.ndarray) -> np.ndarray:
        """
        This function computes the probability distribution for a given feature unique values and a given target

        :param feature_by_target: Pandas series, resulting from filtering by target the pandas DataFrame and selecting
                                  a feature
        :param unique_values:     Numpy array, containing the unique values for the selected feature
        :return:                  Numpy array, with a probability for each feature unique value
        """
        return np.array([np.sum(feature_by_target.values == value) for value in unique_values]) / len(feature_by_target)

    def __get_feature_unique_values(self) -> Dict[str, np.ndarray]:
        """
        This function retrieves for each feature col, its unique values

        :return: Dictionary containing a numpy array of unique values for each feature column
        """
        return {feature_col: np.unique(self.__df[feature_col].values) for feature_col in self.__feature_cols}

    def select_topk(self):
        """
        This method orchestrates the following steps:
        - For each target_value and for all the features, two histograms are calculated per feature. The first one
        considering the DataFrame filtered by target_value and the second one considering the opposite (DataFrame
        filtered by no target_value)
        - Modified Jensen Shannon distance is calculated between the resulting two distributions
        - Once all distances have been computed for all the features for a given target_value, they're ranked, so that
        the larger the distance, the higher the rank
        - Finally, for each feature, its ranks for all of the targets are taken into account so that the feature with
        the largest aggregated rank will rank the first in the topk features (note that when talking about ranks,
        1 is greater than 2)

        :return: List of strings, containing the selected top K features where K equals the number_of_features parameter
                 provided to the constructor
        """
        feature_ranks = []
        distance_rank_info = {}

        # For each feature, its unique values are retrieved
        unique_values = self.__get_feature_unique_values()
        for target_value in self.__target_values:
            unorm_stats_by_feature = []

            # For each feature, unique values are retrieved to compute probabilities
            for feature_col in self.__feature_cols:
                # Probability distribution is computed for feature feature_col when TARGET equals target_value
                probs_feature_target = FeatureSelector.__compute_probabilities(
                    self.__df.loc[self.__df[TARGET] == target_value][feature_col], unique_values[feature_col])

                # Probability distribution is computed for feature feature_col when TARGET doesn't equal target_value
                probs_feature_no_target = FeatureSelector.__compute_probabilities(
                    self.__df.loc[self.__df[TARGET] != target_value][feature_col], unique_values[feature_col])

                # Modified Jensen-Shannon distance is computed between the two distributions
                unorm_stats_by_feature.append(FeatureSelector.__compute_jensen_shannon(probs_feature_target,
                                                                                       probs_feature_no_target))

            # Statistics (mean, median, max and sum) are computed by feature
            unorm_stats_by_feature = np.stack(unorm_stats_by_feature)

            # Statistics for each feature are normalized
            norm_stats_by_feature = unorm_stats_by_feature/unorm_stats_by_feature.sum(axis=0)

            # Normalized statistics are added for each feature
            unorm_distance_by_feature = np.sum(norm_stats_by_feature, axis=1)

            # The addition results are normalized
            norm_distance_by_feature = unorm_distance_by_feature/np.sum(unorm_distance_by_feature)

            # A dictionary (feature: distance) is built
            distance_by_feature = dict(zip(self.__feature_cols, norm_distance_by_feature))

            # Once distance has been computed for all the features related to a given target value, features are
            # ranked so that the larger the distance, the higher the rank (1 is greater than 2 in rank terms)
            distance_rank_info[target_value] = sorted(distance_by_feature.items(), key=lambda d: d[1], reverse=True)
            feature_ranks.extend([info[0] for info in distance_rank_info[target_value]])

            # For a binary problem, there'll be only two values for the target, so that their distances are symmetrical
            # there's no need to compute distances for the two values, one is enough. The trivial distances will be
            # kept just for information consistency purposes
            if len(self.__target_values) == 2:
                trivial_target_value = (
                    self.__target_values[0] if self.__target_values[0] != target_value else self.__target_values[1])
                distance_rank_info[trivial_target_value] = next(iter(distance_rank_info.values()))
                break

        self.__top_features_by_target = distance_rank_info

        # Finally, all obtained ranks for the different target values are aggregated for each feature. The largest rank
        # will cause that feature to be the first of the topk (note that, when talking about ranks, 1 is greater than 2)
        topk_features = {}
        for feature_col in self.__feature_cols:
            topk_features[feature_col] = sum(
                [rank for rank, feature in enumerate(feature_ranks) if feature == feature_col])
        self.__top_features = sorted(topk_features, key=topk_features.get)
        xgprint(self.__verbose,
                'INFO:     FeatureSelector top {} features selected: {}'.format(self.__k,
                                                                                self.__top_features[:self.__k]))
        xgprint(self.__verbose,
                'INFO:     FeatureSelector global feature rank: {}'.format(self.__top_features))
        xgprint(self.__verbose,
                'INFO:     FeatureSelector feature rank by target: {}'.format(self.__top_features_by_target))

        return self.__top_features[:self.__k]
