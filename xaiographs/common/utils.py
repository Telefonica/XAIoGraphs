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


from typing import Any, List, NamedTuple, Tuple

import numpy as np
import pandas as pd

from xaiographs.common.constants import ID, IMPORTANCE_SUFFIX, RELIABILITY, TARGET


class FeaturesInfo(NamedTuple):
    """FeaturesInfo provides the structure to store the column names of different features families: features columns
    names, float type features columns names, importance related features columns names and reliability features
    columns names
    """
    feature_columns: List[str]
    float_feature_columns: List[str]
    importance_columns: List[str]
    reliability_columns: List[str]


class TargetInfo(NamedTuple):
    """TargetInfo provides the structure to store relevant information about the dataset target, such as the target
    columns names, the top1 target for each row, each target value probability and the top1 target indices
    """
    target_columns: List[str]
    target_probs: np.ndarray
    top1_argmax: np.ndarray
    top1_targets: np.ndarray


def filter_by_ids(df: pd.DataFrame, sample_id_mask: np.ndarray, n_repetitions: int = 0):
    """
    This function indexes the given pandas DataFrame by applying the previously generated sample ids mask. This
    mask assumes ids appear only once in the DataFrame to be indexed. However, this is not always the case since several
    rows may appear for each id a n_repetitions parameter is provided to take this into account

    :param df:              Pandas DataFrame to be indexed
    :param sample_id_mask:  Numpy array of boolean values used as sample id mask
    :param n_repetitions:   Integer representing the number of repetitions for each ID, this will be useful for those
                            DataFrames for which, for instance, there is a row per id and feature_value pair
    :return:                Pandas DataFrame containing only those rows filtered by the sample id mask
    """
    if n_repetitions == 0:
        return df[sample_id_mask]
    else:
        return df[np.repeat(sample_id_mask, n_repetitions)]


def get_features_info(df: pd.DataFrame, feature_cols: List[str], target_cols: List[str]) -> FeaturesInfo:
    """
    This function gathers all the necessary lists of feature columns names that will be used all through the execution
    flow

    :param df:              Pandas DataFrame containing the given dataset
    :param feature_cols:    List of strings containing the column names for the features
    :param target_cols:     List of strings containing the possible targets
    :return:                NamedTuple containing all the feature column names lists which will be used all through the
                            execution flow
    """
    #   List of strings containing the reliability columns names
    reliability_columns = get_reliability_columns(target_cols=target_cols)

    #   List of strings containing the importance columns names
    importance_columns = get_importance_columns(feature_cols=feature_cols, target_cols=target_cols)

    #   List of strings names with float type is necessary since a special preprocessing is required in order
    # to generate there associated 'feature_value' node names
    float_feature_cols = list(df[feature_cols].select_dtypes(include='float').columns)

    return FeaturesInfo(feature_columns=feature_cols, float_feature_columns=float_feature_cols,
                        importance_columns=importance_columns, reliability_columns=reliability_columns)


def get_importance_columns(feature_cols: List[str], target_cols: List[str]) -> List[str]:
    """
    This function builds the names of those columns containing the importance values for each feature - target pair

    :param feature_cols:    List of strings containing the column names for the features
    :param target_cols:     List of strings containing the possible targets
    :return:                List of strings containing the importance columns names
    """
    return ['{}_{}{}'.format(target_col, feature_col, IMPORTANCE_SUFFIX) for feature_col in feature_cols for target_col
            in target_cols]


def get_reliability_columns(target_cols: List[str]) -> List[str]:
    """
    This function builds the names of those columns containing the reliability values for all possible targets

    :param target_cols:     List of strings containing the possible targets
    :return:                List of strings containing the reliability columns names
    """
    return ['{}_{}'.format(target_col, RELIABILITY) for target_col in target_cols]


def get_target_info(df: pd.DataFrame, target_cols: List[str]) -> TargetInfo:
    """
    This function calculates some information of interest referring to some DataFrame target. This information consists
    of the top1 targets for each DataFrame row, the probability of each possible target value being True and also the
    index version of the top1 targets information. Please, bear in mind this is only intended for one-hot formatted
    targets. Even binary problems must be formatted this way

    :param df:              Pandas DataFrame whose targets will be processed
    :param target_cols:     List of strings containing the possible targets
    :return:                NamedTuple containing a numpy array listing the top1 target for each DataFrame row, another
                            numpy array listing a probability for each possible target value and a third numpy array
                            showing the top1 targets indexes
    """
    top1_argmax = np.argmax(df[target_cols].values, axis=1)
    top1_targets = np.array([target_cols[am] for am in top1_argmax])
    target_unique_values, target_unique_counts = np.unique(top1_targets, return_counts=True)
    target_probs_dict = dict(zip(target_unique_values, target_unique_counts / len(df)))
    target_probs = np.array([target_probs_dict[t] for t in target_cols])

    return TargetInfo(target_columns=target_cols, target_probs=target_probs, top1_argmax=top1_argmax,
                      top1_targets=top1_targets)


def sample_by_target(ids: np.ndarray, top1_targets: np.ndarray, num_samples: int, target_probs: np.ndarray,
                     target_cols: List[str], target_col: str = TARGET) -> Tuple[np.ndarray, List[Any]]:
    """
    This function generates a list of ids which will be used to limit the number of rows which will be used for the
    local explainability. From this list, a boolean array will be created and used as a mask to filter the requested
    number of samples

    :param ids:             Numpy array consisting of the Pandas DataFrame columns values containing the id on which
                            samples will be computed
    :param top1_targets:    Numpy array containing the top1 target for each row. Sampling will be calculated so
                            that the target ratio will be kept, this parameter allows filtering by target
    :param num_samples:     Integer representing the number of samples which will be calculated
    :param target_probs:    Numpy array containing the probability for each target. It's used to calculate the ratio
                            for each target
    :param target_cols:     List of strings containing the possible targets
    :param target_col:      String representing the target col name (default: 'target')
    :return:                Tuple containing both, a numpy array containing boolean values which will be used to
                            filter any given DataFrame and a list containing the ids used as sample
    """
    # Before proceeding, the requested sample size can't be greater nor equal than the size of the DataFrame from which
    # samples will be taken
    assert len(ids) > num_samples, "requested local sample size can't be greater nor equal than the global size"

    # A Pandas DataFrame containing a first column representing the id and a second column with the top1 target for that
    # row
    df_ids_target = pd.DataFrame(np.concatenate((ids.reshape(-1, 1), top1_targets.reshape(-1, 1)), axis=1),
                                 columns=[ID, target_col])

    # For each possible target, rows are filtered by that target and the number of ids to retrieve is computed by using
    # the target probability and the number of requested samples
    sample_ids = []
    for target_prob, target_col_value in zip(target_probs, target_cols):
        n_samples_by_target = int(num_samples * target_prob)
        sample_ids += df_ids_target[df_ids_target[target_col] == target_col_value][ID].sample(
            n=n_samples_by_target, random_state=42).values.tolist()

    # IDs which will be used as sample are turned into a boolean mask
    sample_ids_mask = np.isin(df_ids_target[ID].values, sample_ids)

    return sample_ids_mask, sample_ids


def xgprint(verbose: int = 0, *args, **kwargs) -> None:
    """
    Wrapper for the builtin `print` function

    :param verbose: Verbosity level, where any value greater than 0 means the message is printed
    :param args: Positional arguments of the builtin `print` function
    :param kwargs: Named arguments of the builtin `print` function
    """
    if verbose > 0:
        print(*args, **kwargs)
