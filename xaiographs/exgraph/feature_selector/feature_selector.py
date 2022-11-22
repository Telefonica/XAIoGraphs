from typing import List

import numpy as np
import pandas as pd
from scipy.special import rel_entr

from xaiographs.common.constants import TARGET
from xaiographs.common.utils import TargetInfo


class FeatureSelector(object):
    """
    This class implements the functionality of selecting the top k most relevant features
    """

    def __init__(self, df: pd.DataFrame, feature_cols: List[str], target_info: TargetInfo, number_of_features: int):
        self.df = df[feature_cols].copy()
        self.df[TARGET] = target_info.top1_targets
        self.feature_cols = feature_cols
        self.k = number_of_features
        self.target_values = target_info.target_columns

    @staticmethod
    def __compute_jensen_shannon(dist1: np.ndarray, dist2: np.ndarray, axis: int = 0, keepdims=True,
                                 agg_function='median'):
        """
        This is an alternative version of the Jensen Shannon distance,
        (https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html)
        An aggregation function is used to prevent those categorical features with high cardinality, to "eclipse"
        others just because their high cardinality

        :param dist1:           Numpy array containing a probability distribution
        :param dist2:           Numpy array containing another probability distribution
        :param axis:            Integer representing the axis along which the Jensen-Shannon distances are computed
                                (default 0)
        :param keepdims:        Boolean, if set to True, the reduced axes are left in the result as dimensions with size
                                one. With this option, the result will broadcast correctly against the input array.
                                (default False)

        :param agg_function:    The function used to aggregate the averaged distances before applying square root to the
                                final result
        :return:                Float or np.ndarray (depending on the input shape) containing the calculated distance/s
        """
        dist1 = dist1 if isinstance(dist1, np.ndarray) else np.asarray(dist1)
        dist2 = dist2 if isinstance(dist2, np.ndarray) else np.asarray(dist2)
        dist1 = dist1 / np.sum(dist1, axis=axis, keepdims=keepdims)
        dist2 = dist2 / np.sum(dist2, axis=axis, keepdims=keepdims)
        m = (dist1 + dist2) / 2.0
        left = rel_entr(dist1, m)
        right = rel_entr(dist2, m)
        js_msa = (left + right) / 2.0
        if agg_function == 'median':
            res = np.median(js_msa)
        elif agg_function == 'mean':
            res = np.mean(agg_function)
        else:
            res = np.sum(js_msa)
        return np.sqrt(res)

    @staticmethod
    def __compute_probabilities(feature_by_target: pd.Series, unique_values: np.ndarray) -> np.ndarray:
        return np.array([np.sum(feature_by_target.values == value) for value in unique_values]) / len(feature_by_target)

    def select_topk(self):
        for feature_col in self.feature_cols:
            distance_by_target = []

            # For each feature, unique values are retrieved to compute probabilities
            unique_values = np.unique(self.df[feature_col].values)
            for target_value in self.target_values:

                # Probability distribution is computed for feature feature_col when TARGET equals target_value
                probs_feature_target = FeatureSelector.__compute_probabilities(
                    self.df.loc[self.df[TARGET] == target_value][feature_col],
                    unique_values)

                # Probability distribution is computed for feature feature_col when TARGET doesn't equal target_value
                probs_feature_no_target = FeatureSelector.__compute_probabilities(
                    self.df.loc[self.df[TARGET] != target_value][feature_col],
                    unique_values)
                distance_by_target.append(
                    FeatureSelector.__compute_jensen_shannon(probs_feature_target, probs_feature_no_target))
