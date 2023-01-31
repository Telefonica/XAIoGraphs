from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.special import rel_entr

from xaiographs.common.constants import TARGET
from xaiographs.common.utils import TargetInfo, xgprint


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

        :param df:                  Pandas DataFrame containing the whole dataset
        :param feature_cols:        List of strings containing the column names for the features
        :param target_info:         NamedTuple containing a numpy array listing the top1 target for each DataFrame row,
                                    another numpy array listing a probability for each possible target value and a third
                                    numpy array showing the top1 targets indexes
        :param number_of_features:  Integer representing the number of features to be selected
        :param verbose:             Verbosity level, where any value greater than 0 means the message is printed
        """
        self.df = df[feature_cols].copy()
        self.df[TARGET] = target_info.top1_targets
        self.feature_cols = feature_cols
        self.k = number_of_features
        self.target_values = target_info.target_columns
        self.top_features_by_target = dict()
        self.top_features = []
        self.verbose = verbose
        xgprint(self.verbose, 'INFO: Instantiating FeatureSelector to select the top {} features:'.format(self.k))

    @staticmethod
    def __compute_jensen_shannon(dist1: np.ndarray, dist2: np.ndarray, axis: int = 0, keepdims=True) -> np.ndarray:
        """
        This is an alternative version of the Jensen Shannon distance,
        (https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html)
        Multiple aggregation functions are used to balance their individual pros and cons

        :param dist1:     Numpy array containing a probability distribution
        :param dist2:     Numpy array containing another probability distribution
        :param axis:      Integer representing the axis along which the Jensen-Shannon distances are computed
                          (default 0)
        :param keepdims:  Boolean, if set to True, the reduced axes are left in the result as dimensions with size
                          one. With this option, the result will broadcast correctly against the input array.
                          (default False)

        :return:          Float or np.ndarray (depending on the input shape) containing the calculated statistics
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

        :param feature_by_target: Pandas series resulting from filtering by target the pandas DataFrame and selecting
                                  a feature
        :param unique_values:     Numpy array containing the unique values for the selected feature
        :return:                  Numpy array with a probability for each feature unique value
        """
        return np.array([np.sum(feature_by_target.values == value) for value in unique_values]) / len(feature_by_target)

    def get_feature_unique_values(self) -> Dict[str, np.ndarray]:
        """
        This function retrieves for each feature col, its unique values

        :return: Dictionary containing a numpy array of unique values for each feature column
        """
        return {feature_col: np.unique(self.df[feature_col].values) for feature_col in self.feature_cols}

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

        :return:
        """
        feature_ranks = []
        distance_rank_info = {}

        # For each feature, its unique values are retrieved
        unique_values = self.get_feature_unique_values()
        for target_value in self.target_values:
            unorm_stats_by_feature = []

            # For each feature, unique values are retrieved to compute probabilities
            for feature_col in self.feature_cols:
                # Probability distribution is computed for feature feature_col when TARGET equals target_value
                probs_feature_target = FeatureSelector.__compute_probabilities(
                    self.df.loc[self.df[TARGET] == target_value][feature_col], unique_values[feature_col])

                # Probability distribution is computed for feature feature_col when TARGET doesn't equal target_value
                probs_feature_no_target = FeatureSelector.__compute_probabilities(
                    self.df.loc[self.df[TARGET] != target_value][feature_col], unique_values[feature_col])

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
            distance_by_feature = dict(zip(self.feature_cols, norm_distance_by_feature))

            # Once distance has been computed for all the features related to a given target value, features are
            # ranked so that the larger the distance, the higher the rank (1 is greater than 2 in rank terms)
            distance_rank_info[target_value] = sorted(distance_by_feature.items(), key=lambda d: d[1], reverse=True)
            feature_ranks.extend([info[0] for info in distance_rank_info[target_value]])

            # For a binary problem, there'll be only two values for the target, so that their distances are symmetrical
            # there's no need to compute distances for the two values, one is enough
            if len(self.target_values) == 2:
                break
        self.top_features_by_target = distance_rank_info

        # Finally, all obtained ranks for the different target values are aggregated for each feature. The largest rank
        # will cause that feature to be the first of the topk (note that, when talking about ranks, 1 is greater than 2)
        topk_features = {}
        for feature_col in self.feature_cols:
            topk_features[feature_col] = sum(
                [rank for rank, feature in enumerate(feature_ranks) if feature == feature_col])
        self.top_features = sorted(topk_features, key=topk_features.get)
        xgprint(self.verbose,
                'INFO:     FeatureSelector top {} features selected: {}'.format(self.k, self.top_features[:self.k]))
        xgprint(self.verbose,
                'INFO:     FeatureSelector global feature rank: {}'.format(self.top_features))
        xgprint(self.verbose,
                'INFO:     FeatureSelector feature rank by target: {}'.format(self.top_features_by_target))

        return self.top_features[:self.k]
