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


import os
from typing import List, Tuple, Union

import numpy as np
import pandas as pd

from copy import deepcopy
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

from xaiographs.common.utils import xgprint

# CONSTANTS
BINARY = 2
CORRELATION_VALUE = 'correlation_value'
FAIRNESS_CATEGORIES_SCORE = {'A+': 0.02, 'A': 0.05, 'B': 0.08, 'C': 0.15, 'D': 0.25, 'E': 1.0}
FEATURE_1 = 'feature_1'
FEATURE_2 = 'feature_2'
INDEPENDENCE_CATEGORY = 'independence_category'
INDEPENDENCE_GLOBAL_SCORE = 'independence_global_score'
INDEPENDENCE_SCORE = 'independence_score'
INDEPENDENCE_SCORE_WEIGHT = 'independence_score_weight'
IS_BINARY_SENSITIVE_FEATURE = 'is_binary_sensitive_feature'
IS_CORRELATION_SENSIBLE = 'is_correlation_sensible'
OTHER = '_other'
SENSITIVE_FEATURE = 'sensitive_feature'
SENSITIVE_VALUE = 'sensitive_value'
SEPARATION_CATEGORY = 'separation_category'
SEPARATION_GLOBAL_SCORE = 'separation_global_score'
SEPARATION_SCORE = 'separation_score'
SEPARATION_SCORE_WEIGHT = 'separation_score_weight'
SUFFICIENCY_CATEGORY = 'sufficiency_category'
SUFFICIENCY_GLOBAL_SCORE = 'sufficiency_global_score'
SUFFICIENCY_SCORE = 'sufficiency_score'
SUFFICIENCY_SCORE_WEIGHT = 'sufficiency_score_weight'
TARGET_LABEL = 'target_label'

# COLUMNS CONSTANTS
FAIRNESS_INFO_COLS = [SENSITIVE_FEATURE, SENSITIVE_VALUE, IS_BINARY_SENSITIVE_FEATURE, TARGET_LABEL,
                      INDEPENDENCE_SCORE, INDEPENDENCE_CATEGORY, INDEPENDENCE_SCORE_WEIGHT, SEPARATION_SCORE,
                      SEPARATION_CATEGORY, SEPARATION_SCORE_WEIGHT, SUFFICIENCY_SCORE, SUFFICIENCY_CATEGORY,
                      SUFFICIENCY_SCORE_WEIGHT]
FAIRNESS_GLOBAL_SCORES_COLS = [SENSITIVE_FEATURE, INDEPENDENCE_GLOBAL_SCORE, INDEPENDENCE_CATEGORY,
                               SEPARATION_GLOBAL_SCORE, SEPARATION_CATEGORY, SUFFICIENCY_GLOBAL_SCORE,
                               SUFFICIENCY_CATEGORY]
FAIRNESS_INDEPENDENCE_COLS = [SENSITIVE_FEATURE, SENSITIVE_VALUE, TARGET_LABEL, INDEPENDENCE_SCORE,
                              INDEPENDENCE_CATEGORY]
FAIRNESS_SEPARATION_COLS = [SENSITIVE_FEATURE, SENSITIVE_VALUE, TARGET_LABEL, SEPARATION_SCORE, SEPARATION_CATEGORY]
FAIRNESS_SUFFICIENCY_COLS = [SENSITIVE_FEATURE, SENSITIVE_VALUE, TARGET_LABEL, SUFFICIENCY_SCORE, SUFFICIENCY_CATEGORY]
FAIRNESS_CORRELATIONS_COLS = [FEATURE_1, FEATURE_2, CORRELATION_VALUE, IS_CORRELATION_SENSIBLE]

# FILE CONSTANTS
FAIRNESS_CONFUSION_MATRIX_FILE = 'fairness_confusion_matrix.json'
FAIRNESS_HIGHEST_CORRELATION_FILE = 'fairness_highest_correlation.json'
FAIRNESS_INDEPENDENCE_FILE = 'fairness_independence.json'
FAIRNESS_SEPARATION_FILE = 'fairness_separation.json'
FAIRNESS_SUFFICIENCY_FILE = 'fairness_sufficiency.json'
FAIRNESS_SUMARIZE_CRITERIAS_FILE = 'fairness_sumarize_criterias.json'

# Warning message
WARN_MSG = 'WARNING: {} is empty, because nothing has been processed. Execute fit() function to get results.'


class Fairness(object):
    """The Fairness class offers functionalities to explain how fair or unfair are the classifications made by a \
    (Deep) Machine Learning model on a set of features that we consider sensitive (gender, ethnic group, religion, \
    age, etc.).

    Read more in the :ref:`Fairness <user_guide/fairness>` User Guide


    Parameters
    ----------
    destination_path : str, default='./xaioweb_files'
        Path where output XAIoWeb files will be stored.

    verbose : int, default=0
        Verbosity level.

        .. hint::
           Any value greater than 0 means verbosity is on.


    """

    def __init__(self, destination_path: str = './xaioweb_files', verbose: int = 0):
        self.__destination_path = destination_path
        self.__target_values = None
        self.__confusion_matrix = None
        self.__correlation_matrix = None
        self.__highest_correlation_features = None
        self.__fairness_info = list()
        self.__global_scores_info = list()
        self.verbose = verbose

    @property
    def target_values(self):
        """List with the different target values of dataset.\


        Returns
        -------
        target_values : List[str]
            List containing the target values.


        .. caution::
           If the method :meth:`fit` from the :class:`Fairness` class has not been executed, it will return a warning \
           message.

        """
        if self.__target_values is None:
            print(WARN_MSG.format('\"target_values\"'))
        else:
            return self.__target_values

    @property
    def confusion_matrix(self):
        """Confusion matrix.


        Returns
        -------
        confusion_matrix : pandas.DataFrame
            Structure representing the Confusion Matrix.


        .. caution::
           If the method :meth:`fit` from the :class:`Fairness` class has not been executed, it will return a warning \
           message.

        """
        if self.__confusion_matrix is None:
            print(WARN_MSG.format('\"confusion_matrix\"'))
        else:
            return self.__confusion_matrix

    @property
    def correlation_matrix(self):
        """Correlation matrix (pearson correlation) between features. \


        Returns
        -------
        correlation_matrix : pandas.DataFrame
            Structure representing the correlation matrix.


        .. caution::
           If the method :meth:`fit` from the :class:`Fairness` class has not been executed, it will return a warning \
           message.

        """
        if self.__correlation_matrix is None:
            print(WARN_MSG.format('\"correlation_matrix\"'))
        else:
            return self.__correlation_matrix

    @property
    def highest_correlation_features(self):
        """DataFrame with pairs of features that have a pearson correlation value above a threshold (0.9). \
        If one of these features is a sensitive features, it will be marked with a flag. In the event that there are \
        no highly correlated features, an empty DataFrame will be returned.


        Returns
        -------
        highest_correlation_features :  pandas.DataFrame
            Structure containing the most highly correlated features.


        .. caution::
           If the method :meth:`fit` from the :class:`Fairness` class has not been executed, it will return a warning \
           message.

        """
        if self.__highest_correlation_features is None:
            print(WARN_MSG.format('\"highest_correlation_features\"'))
        else:
            return (pd.DataFrame.from_dict(self.__highest_correlation_features)[FAIRNESS_CORRELATIONS_COLS]
                    if len(self.__highest_correlation_features) > 0
                    else pd.DataFrame(columns=FAIRNESS_CORRELATIONS_COLS))

    @property
    def fairness_categories_score(self):
        """DataFrame with the categories that are assigned to the Fairness criteria based on their score.\
        The categories and ranges of scores are the following:

        +--------+--------------------+
        |Category|Range Score         |
        +========+====================+
        |A+      |0.0 <= score <= 0.02|
        +--------+--------------------+
        |A       |0.02 < score <= 0.05|
        +--------+--------------------+
        |B       |0.05 < score <= 0.08|
        +--------+--------------------+
        |C       |0.08 < score <= 0.15|
        +--------+--------------------+
        |D       |0.15 < score <= 0.25|
        +--------+--------------------+
        |E       |0.25 < score <= 1.0 |
        +--------+--------------------+

        Returns
        -------
        fairness_categories_score : pandas.DataFrame
            Structure containing the categories based on scores.


        """
        return pd.DataFrame({'category': FAIRNESS_CATEGORIES_SCORE.keys(),
                             'limit_score_pct': FAIRNESS_CATEGORIES_SCORE.values()})

    @property
    def fairness_info(self):
        """DataFrame with all information of fairness criteria. For each sensitive feature, \
        for each value of the sensitive feature and for each value of the target, returns (for each fairness \
        criterion) its Score, its Category and its Weight (percentage of the value of the variable and the value \
        target). The DataFrame contains the following columns:

        +-------------------------------+-----------------------------------------------------------------------------------+
        |Column                         |Description                                                                        |
        +===============================+===================================================================================+
        |**sensitive_feature**          |Sensitive feature name.                                                            |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sensitive_value**            |value of sensitive feature.                                                        |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**is_binary_sensitive_feature**|indicates whether or not the sensitive feature is binary.                          |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**target_label**               |value of prediction (``y_predict``).                                               |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**independence_score**         |Independence criterion score.                                                      |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**independence_category**      |Category {A+, A, B, C, D, E} assigned to the value of Independence criterion score.|
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**independence_score_weight**  |Percentage (sensitive_value & predict_label)/all_rows_dataset                      |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**separation_score**           |Separation criterion score.                                                        |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**separation_category**        |Category {A+, A, B, C, D, E} assigned to the value of Separation criterion score.  |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**separation_score_weight**    |Percentage (sensitive_value & predict_label)/all_rows_dataset.                     |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sufficiency_score**          |Sufficiency criterion score.                                                       |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sufficiency_category**       |Category {A+, A, B, C, D, E} assigned to the value of Sufficiency criterion score. |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sufficiency_score_weight**   |Percentage (sensitive_value & target_label)/all_rows_dataset.                      |
        +-------------------------------+-----------------------------------------------------------------------------------+


        Returns
        -------
        fairness_info : pandas.DataFrame
            Structure, with all information of fairness criteria.


        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"fairness_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_INFO_COLS]

    @property
    def independence_info(self):
        """DataFrame with all information of Independence criterion. For each sensitive \
        feature, for each value of the sensitive feature and for each value of the target, returns (for Independence \
        criterion) its Score and its Category. The DataFrame contains the following columns:

        +-------------------------------+-----------------------------------------------------------------------------------+
        |Column                         |Description                                                                        |
        +===============================+===================================================================================+
        |**sensitive_feature**          |Sensitive feature name.                                                            |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sensitive_value**            |value of sensitive feature.                                                        |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**target_label**               |value of prediction (``y_predict``).                                               |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**independence_score**         |Independence criterion score.                                                      |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**independence_category**      |Category {A+, A, B, C, D, E} assigned to the value of Independence criterion score.|
        +-------------------------------+-----------------------------------------------------------------------------------+


        Returns
        -------
        independence_info : pandas.DataFrame
            Structure with all information of Independence criterion.


        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"independence_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_INDEPENDENCE_COLS]

    @property
    def separation_info(self):
        """DataFrame with all information of Separation criterion. For each sensitive feature, \
        for each value of the sensitive feature and for each value of the target, returns (for Separation criterion) \
        its Score and its Category. The DataFrame contains the following columns:

        +-------------------------------+-----------------------------------------------------------------------------------+
        |Column                         |Description                                                                        |
        +===============================+===================================================================================+
        |**sensitive_feature**          |Sensitive feature name.                                                            |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sensitive_value**            |value of sensitive feature.                                                        |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**target_label**               |value of prediction (``y_predict``).                                               |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**separation_score**           |Separation criterion score.                                                        |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**separation_category**        |Category {A+, A, B, C, D, E} assigned to the value of Separation criterion score.  |
        +-------------------------------+-----------------------------------------------------------------------------------+

        Returns
        -------
        separation_info : pandas.DataFrame
            Structure with all information of Separation criterion.


        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"separation_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_SEPARATION_COLS]

    @property
    def sufficiency_info(self):
        """DataFrame with all information of Sufficiency criterion. For each sensitive feature, for each value of \
        the sensitive feature and for each value of the target, returns (for Sufficiency criterion) its \
        Score and its Category. The DataFrame contains the following columns:

        +-------------------------------+-----------------------------------------------------------------------------------+
        |Column                         |Description                                                                        |
        +===============================+===================================================================================+
        |**sensitive_feature**          |Sensitive feature name.                                                            |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sensitive_value**            |value of sensitive feature.                                                        |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**target_label**               |value of prediction (``y_predict``).                                               |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sufficiency_score**          |Sufficiency criterion score.                                                       |
        +-------------------------------+-----------------------------------------------------------------------------------+
        |**sufficiency_category**       |Category {A+, A, B, C, D, E} assigned to the value of Sufficiency criterion score. |
        +-------------------------------+-----------------------------------------------------------------------------------+

        Returns
        -------
        sufficiency_info : pandas.DataFrame
            Structure with all information of Sufficiency criterion.


        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"sufficiency_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_SUFFICIENCY_COLS]

    @property
    def fairness_global_info(self):
        """DataFrame with "Global Scores" (weighted aggregation of the scores for each fairness criteria) \
        for each sensitive feature and assigns it a category *{A+, A, B, C, D, E}*. \
        The DataFrame contains the following columns:

        +------------------------------+------------------------------------------------------------------------------------------+
        |Column                        |Description                                                                               |
        +==============================+==========================================================================================+
        |**sensitive_feature**         |Sensitive feature name.                                                                   |
        +------------------------------+------------------------------------------------------------------------------------------+
        |**independence_global_score** |Independence global criterion score.                                                      |
        +------------------------------+------------------------------------------------------------------------------------------+
        |**independence_category**     |Category {A+, A, B, C, D, E} assigned to the value of Independence global criterion score.|
        +------------------------------+------------------------------------------------------------------------------------------+
        |**separation_global_score**   |Separation global criterion score.                                                         |
        +------------------------------+------------------------------------------------------------------------------------------+
        |**separation_category**       |Category {A+, A, B, C, D, E} assigned to the value of Separation global criterion score.   |
        +------------------------------+------------------------------------------------------------------------------------------+
        |**sufficiency_global_score**  |Sufficiency global criterion score.                                                        |
        +------------------------------+------------------------------------------------------------------------------------------+
        |**sufficiency_category**      |Category {A+, A, B, C, D, E} assigned to the value of Sufficiency global criterion score.  |
        +------------------------------+------------------------------------------------------------------------------------------+

        Returns
        -------
        fairness_global_info : pandas.DataFrame
            Structure with "Global Scores".


        """
        if len(self.__global_scores_info) == 0:
            print(WARN_MSG.format('\"fairness_global_info\"'))
        else:
            return pd.DataFrame(self.__global_scores_info)[FAIRNESS_GLOBAL_SCORES_COLS]

    def independence_score(self, df: pd.DataFrame, sensitive_col: str, predict_col: str, target_label: str,
                           sensitive_value: str) -> float:
        """Calculate independence criterion's score.
        We say that the random variables (Y, A) satisfy independence if the sensitive feature 'A'
        are statistically independent of the prediction 'Y'. We define the score as the difference (in absolute value)
        of the probabilities:

        .. math::
            independence\ score = | P(Y=y∣A=a) - P(Y=y∣A=b) |

        Parameters
        ----------
        df : pandas.DataFrame
            Structure containing the dataset to process. The dataset must have: *N feature columns*, a *real target* \
             column and *prediction* column.

        sensitive_col : str
            Name of the DataFrame (df) column with the sensitive feature.

        predict_col : str
            Name of the column of the DataFrame (df) that contains predictions of each element.

        target_label : str
            Name of the DataFrame column (df) that contains target (ground truth or ``y_real``) of each element.

        sensitive_value : str
            Value of the sensitive feature for the score calculation.

        Returns
        -------
        independence_score : float
            independence score value.

        Raises
        ------
        ZeroDivisionError
            One of the conditional probabilities equals zero, this leads to a division by zero.


        """
        self.__check_dataset_values(df=df,
                                    sensitive_col=sensitive_col,
                                    target_col=None,
                                    predict_col=predict_col,
                                    target_label=target_label,
                                    sensitive_value=sensitive_value)

        try:
            prob_a = ((df[(df[sensitive_col] == sensitive_value) & (df[predict_col] == target_label)].shape[0]) /
                      (df[df[sensitive_col] == sensitive_value].shape[0]))
        except ZeroDivisionError:
            prob_a = 0
            print('WARNING: Probability P(Y={}|A={}) result is Zero, because ZeroDivisionError'
                  .format(target_label, sensitive_value))

        try:
            prob_b = ((df[(df[sensitive_col] != sensitive_value) & (df[predict_col] == target_label)].shape[0]) /
                      (df[df[sensitive_col] != sensitive_value].shape[0]))
        except ZeroDivisionError:
            prob_b = 0
            print('WARNING: Probability P(Y={}|A=not {}) result is Zero, because ZeroDivisionError'
                  .format(target_label, sensitive_value))

        return abs(prob_a - prob_b)

    def separation_score(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str,
                         target_label: str, sensitive_value: str) -> float:
        """Calculate separation criterion's score.
        We say the random variables (Y, A, T) satisfy separation if the sensitive characteristics 'A' are
        statistically independent of the prediction 'Y' given the target value 'T'. We define the score as the
        difference (in absolute value) of the probabilities:

        .. math::
            separation\ score = | P(Y=y∣T=t,A=a) - P(Y=y∣T=t,A=b) |

        Parameters
        ----------
        df : pandas.DataFrame
            Structure with dataset to process. The dataset must have: *N feature columns*, a *real target* column and *prediction* column.

        sensitive_col : str
            Name of the DataFrame (df) column with the sensitive feature.

        target_col : str
            Name of the DataFrame (df) that contains target (ground truth or ``y_real``).

        predict_col : str
            Name of the column of the DataFrame (df) that contains predictions of each element.

        target_label : str
            Name of the DataFrame column (df) that contains target (ground truth or ``y_real``) of each element.

        sensitive_value : str
            Value of the sensitive feature for the score calculation.

        Returns
        -------
        separation_score : float
            Separation score value.

        Raises
        ------
        ZeroDivisionError
            One of the conditional probabilities equals zero, this leads to a division by zero.


        """
        self.__check_dataset_values(df=df,
                                    sensitive_col=sensitive_col,
                                    target_col=target_col,
                                    predict_col=predict_col,
                                    target_label=target_label,
                                    sensitive_value=sensitive_value)

        try:
            prob_a = ((df[(df[sensitive_col] == sensitive_value) & (df[target_col] == target_label) &
                          (df[predict_col] == target_label)]).shape[0] /
                      (df[(df[sensitive_col] == sensitive_value) & (df[target_col] == target_label)]).shape[0])
        except ZeroDivisionError:
            prob_a = 0
            print('WARNING: Probability P(Y={}|T={}, A={}) result is Zero, because ZeroDivisionError'
                  .format(target_label, target_label, sensitive_value))

        try:
            prob_b = ((df[(df[sensitive_col] != sensitive_value) & (df[target_col] == target_label) &
                          (df[predict_col] == target_label)]).shape[0] /
                      (df[(df[sensitive_col] != sensitive_value) & (df[target_col] == target_label)]).shape[0])
        except ZeroDivisionError:
            prob_b = 0
            print('WARNING: Probability P(Y={}|T={}, A=not {}) result is Zero, because ZeroDivisionError'
                  .format(target_label, target_label, sensitive_value))

        return abs(prob_a - prob_b)

    def sufficiency_score(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str,
                          target_label: str, sensitive_value: str) -> float:
        """Calculate sufficiency criterion's score.
        We say the random variables (Y,A,T) satisfy sufficiency if the sensitive characteristics 'A' are
        statistically independent of the target value 'T' given the prediction 'Y'. We define the score as the
        difference (in absolute value) of the probabilities:

        .. math::
            sufficiency\ score = | P(T=t∣Y=y,A=a) - P(T=t∣Y=y,A=b) |

        Parameters
        ----------
        df : pandas.DataFrame
            Structure with the dataset to process. The dataset must have: *N feature columns*, a *real target* column and *prediction* column.

        sensitive_col : str
            Name of the DataFrame (df) column with the sensitive feature.

        target_col : str
            Name of the DataFrame (df) that contains target (ground truth or ``y_real``).

        predict_col : str
            Name of the column of the DataFrame (df) that contains predictions of each element.

        target_label : str
            Name of the DataFrame column (df) that contains target (ground truth or ``y_real``) of each element.

        sensitive_value : str
            Value of the sensitive feature for the score calculation.

        Returns
        -------
        sufficiency_score : float
            Sufficiency score value.

        Raises
        ------
        ZeroDivisionError
            One of the conditional probabilities equals zero, this leads to a division by zero.

        """
        self.__check_dataset_values(df=df,
                                    sensitive_col=sensitive_col,
                                    target_col=target_col,
                                    predict_col=predict_col,
                                    target_label=target_label,
                                    sensitive_value=sensitive_value)

        try:
            prob_a = ((df[(df[sensitive_col] == sensitive_value) & (df[target_col] == target_label) &
                          (df[predict_col] == target_label)]).shape[0] /
                      (df[(df[sensitive_col] == sensitive_value) & (df[predict_col] == target_label)]).shape[0])
        except ZeroDivisionError:
            prob_a = 0
            print('WARNING: Probability P(T={}|Y={}, A={}) result is Zero, because ZeroDivisionError'
                  .format(target_label, target_label, sensitive_value))

        try:
            prob_b = ((df[(df[sensitive_col] != sensitive_value) & (df[target_col] == target_label) &
                          (df[predict_col] == target_label)]).shape[0] /
                      (df[(df[sensitive_col] != sensitive_value) & (df[predict_col] == target_label)]).shape[0])
        except ZeroDivisionError:
            prob_b = 0
            print('WARNING: Probability P(T={}|Y={}, A=not {}) result is Zero, because ZeroDivisionError'
                  .format(target_label, target_label, sensitive_value))

        return abs(prob_a - prob_b)

    def fairness_metrics(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str,
                         target_label: str, sensitive_value: str) -> Tuple[float, float, float]:
        """Calculate scores for the criteria of :meth:`independence_score`, :meth:`separation_score` \
        and :meth:`sufficiency_score`. Being 'A' the sensitive feature, 'Y' the prediction and 'T' the \
        real target, these criteria are calculated:


        Parameters
        ----------
        df : pd.DataFrame
            Structure with dataset to process. The dataset must have: *N feature columns*, a *real target* column and *prediction* column.

        sensitive_col : str
            Name of the DataFrame (df) column with the sensitive feature.

        target_col : str
            Name of the DataFrame (df) that contains target (ground truth or ``y_real``).

        predict_col : str
            Name of the column of the DataFrame (df) that contains predictions of each element.

        target_label : str
            Name of the DataFrame column (df) that contains target (ground truth or ``y_real``) of each element.

        sensitive_value : str
            Value of the sensitive feature for the score calculation.

        Returns
        -------
        fairness_metrics : Tuple[float, float, float]
            Fairness score metrics (independence score, separation score, sufficiency score).


        .. seealso::
           For detailed calculations of each metrics, please refer to :meth:`independence_score`, \
           :meth:`separation_score` and :meth:`sufficiency_score` from the :class:`Fairness` class.

        """
        independence = self.independence_score(df=df,
                                               sensitive_col=sensitive_col,
                                               predict_col=predict_col,
                                               target_label=target_label,
                                               sensitive_value=sensitive_value)
        separation = self.separation_score(df=df,
                                           sensitive_col=sensitive_col,
                                           target_col=target_col,
                                           predict_col=predict_col,
                                           target_label=target_label,
                                           sensitive_value=sensitive_value)
        sufficiency = self.sufficiency_score(df=df,
                                             sensitive_col=sensitive_col,
                                             target_col=target_col,
                                             predict_col=predict_col,
                                             target_label=target_label,
                                             sensitive_value=sensitive_value)

        return independence, separation, sufficiency

    @staticmethod
    def __score_weight(df: pd.DataFrame, sensitive_col: str, sensitive_value: str, predict_col: str,
                       target_label: str, groupby_cols: List[str]) -> float:
        """Function to calculate the percentage (weight) that the calculation of some criterion supposes with
        respect to its prediction or target and sensitive variable

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_col: str, Name of the DataFrame (df) column with the sensitive feature
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the DataFrame column (df) that contains target (ground truth or y_real) \
        of each element
        :param groupby_cols: List[str], with columns to aggregate
        :return: float
        """
        dfp = df.groupby(groupby_cols)[sensitive_col].agg(count='count').reset_index()
        dfp['pct'] = dfp['count'] / dfp['count'].sum()
        if sensitive_col in dfp.columns:
            try:
                return dfp[(dfp[predict_col] == target_label)
                           & (dfp[sensitive_col] == sensitive_value)]['pct'].iloc[0]
            except IndexError:
                return 0.0
        else:
            try:
                return dfp[dfp[predict_col] == target_label]['pct'].iloc[0]
            except IndexError:
                return 0.0

    @staticmethod
    def get_fairness_category(score: float) -> str:
        """It assigns a Category to any Fairness criterion given a Score. The relationship between \
        Score and Category is shown in the following table:

        +--------+--------------------+
        |Category|Range Score         |
        +========+====================+
        |A+      |0.0 <= score <= 0.02|
        +--------+--------------------+
        |A       |0.02 < score <= 0.05|
        +--------+--------------------+
        |B       |0.05 < score <= 0.08|
        +--------+--------------------+
        |C       |0.08 < score <= 0.15|
        +--------+--------------------+
        |D       |0.15 < score <= 0.25|
        +--------+--------------------+
        |E       |0.25 < score <= 1.0 |
        +--------+--------------------+

        Parameters
        ----------
        score : float
            Value of the score of the Fairness criterion.

        Returns
        -------
        category : str
            Category assigned to the score.

        """
        fairness_category_score = sorted(FAIRNESS_CATEGORIES_SCORE.items(),
                                         key=lambda item: item[1],
                                         reverse=False)

        category = fairness_category_score[-1][0]
        if float(fairness_category_score[-1][1]) < score:
            print('ERROR: The score passed by parameters is greater than the maximum value. '
                  'The highest category \"{}\" is returned by default'.format(fairness_category_score[-1][0]))
            return category
        else:
            for i in fairness_category_score:
                if score <= float(i[1]):
                    category = i[0]
                    break
            return category

    def fit(self, df: pd.DataFrame, sensitive_cols: List[str], target_col: str, predict_col: str) -> None:
        """Main function that performs all the calculations of the Fairness class. The calculated results are \
        accessible via the **property** functions of the class.

        Parameters
        ----------
        df : pandas.DataFrame
            Structure with dataset to process. The dataset must have: *N feature columns*, a *real target* column and \
            *prediction* column.

        sensitive_cols : List[str]
            List with the sensitive features (df column names) to evaluate the Fairness criteria.

        target_col : str
            Column of DataFrame that contains target (ground truth or ``y_real``).

        predict_col : str
            Column of DataFrame that contains predictions (``y_predict``) of each element.

        """
        self.__pre_processing(df=df, sensitive_cols=sensitive_cols, target_col=target_col, predict_col=predict_col)
        self.__in_processing(df=df, sensitive_cols=sensitive_cols, target_col=target_col, predict_col=predict_col)
        self.__post_processing()

    @staticmethod
    def __check_dataset_values(df: pd.DataFrame, sensitive_col: str, target_col: Union[str, None], predict_col: str,
                               target_label: str, sensitive_value: str) -> None:
        """Method that verifies:

            + if sensitive value exists in column dataset
            + if sensitive value exists in column dataset
            + if sensitive value exists in column dataset

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_col: str, Name of the DataFrame (df) column with the sensitive feature
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the DataFrame column (df) that contains target (ground truth or y_real) \
        of each element
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :return: None
        """
        # Check if sensitive_col, predict_col or target_col column is in DataFrame
        columns_df = df.columns
        columns_2_check = ({sensitive_col, predict_col} if target_col is None
                           else {sensitive_col, predict_col, target_col})
        if not columns_2_check.issubset(columns_df):
            raise AttributeError('Column {} does not exist in pandas Dataframe. The possible name of columns are: {}'
                                 .format(sensitive_col, columns_df))

        # Check if sensitive value exists in column dataset
        target_uniques = df[predict_col].unique()
        if target_label not in target_uniques:
            raise KeyError('Target {} does not exist in \"{}\" column. The possible values of target_labels parameter '
                           'can take are: {}'.format(target_label, predict_col, target_uniques))

        # Check if sensitive value exists in column dataset
        sensitive_uniques = df[sensitive_col].unique()
        if sensitive_value not in sensitive_uniques:
            raise KeyError('The value {} does not exist in \"{}\" column. The possible values that the sensitive_value '
                           'parameter can take are: {}'.format(sensitive_value, sensitive_col, sensitive_uniques))

    def __pre_processing(self, df: pd.DataFrame, sensitive_cols: List[str], target_col: str, predict_col: str) -> None:
        """Function that performs the data processing prior to the "core" calculations of the class

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_cols: List[str], with the sensitive features (df column names) to evaluate the \
        Fairness criteria
        :param target_col: str, Name of the DataFrame (df) that contains target (ground truth or y_real)
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :return: None
        """
        # Obtain distinct target values
        self.__target_values = df[predict_col].unique()

        # Confusion Matrix: Target in rows and predictions in columns
        self.__confusion_matrix = pd.crosstab(df[target_col],
                                              df[predict_col],
                                              rownames=[target_col],
                                              colnames=[predict_col])

        # Features Correlation Matrix
        df_process = deepcopy(df[[feature for feature in df.columns if feature not in [target_col, predict_col]]])
        self.__fit_correlation_features(df=df_process)

        # Search for highly correlated features
        self.__find_highest_correlation_features(df_correlations=self.__correlation_matrix,
                                                 threshold=0.9,
                                                 sensitive_cols=sensitive_cols)

    def __in_processing(self, df: pd.DataFrame, sensitive_cols: List[str], target_col: str, predict_col: str) -> None:
        """Function that performs the "core" processing of the class

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_cols: List[str], with the sensitive features (df column names) to evaluate the \
        Fairness criteria
        :param target_col: str, Name of the DataFrame (df) that contains target (ground truth or y_real)
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :return: None
        """
        for sensitive_col in sensitive_cols:
            sensitive_values = df[sensitive_col].unique()
            for target_label in self.target_values:
                pbar = tqdm(sensitive_values, disable=not self.verbose)
                for sensitive_value in pbar:
                    pbar.set_description('Processing: sensitive_col={}, sensitive_value={}, target_label={} '
                                         .format(sensitive_col, sensitive_value, target_label))
                    pbar.refresh()
                    self.__process_sensitive_column(df=df,
                                                    sensitive_col=sensitive_col,
                                                    target_col=target_col,
                                                    predict_col=predict_col,
                                                    target_label=target_label,
                                                    sensitive_value=(sensitive_values if len(sensitive_values) == BINARY
                                                                     else sensitive_value),
                                                    is_sensitive_col_binary=len(sensitive_values) == BINARY)
                    if len(sensitive_values) == BINARY:
                        break

    def __post_processing(self) -> None:
        """Function that performs the procedures after the "core" calculations of the class

        :return: None
        """
        # Write the global scores for each of the sensitive variables
        self.__global_scores()

        # Writing files for the web interface
        if not os.path.exists(self.__destination_path):
            os.mkdir(self.__destination_path)

        # 1.- Confusion matrix "fairness_confusion_matrix.json"
        self.confusion_matrix.to_json(os.path.join(self.__destination_path, FAIRNESS_CONFUSION_MATRIX_FILE), 
                                      orient='records')

        # 2.- Summary table:
        #     For each of the criteria and features -> Score - Category_Score "fairness_sumarize_criterias.json"
        self.fairness_global_info.to_json(os.path.join(self.__destination_path, FAIRNESS_SUMARIZE_CRITERIAS_FILE),
                                          orient='records')

        # 3.- Independence criteria table:
        #     For each Value of the features & targets -> Score - Category_Score "fairness_independence.json"
        self.independence_info.to_json(os.path.join(self.__destination_path, FAIRNESS_INDEPENDENCE_FILE),
                                       orient='records')

        # 4.- Separation criteria table:
        #     For each Value of the features & targets -> Score - Category_Score "fairness_separation.json"
        self.separation_info.to_json(os.path.join(self.__destination_path, FAIRNESS_SEPARATION_FILE), orient='records')

        # 5.- Sufficiency criteria table:
        #     For each Value of the features & targets -> Score - Category_Score "fairness_sufficiency.json"
        self.sufficiency_info.to_json(os.path.join(self.__destination_path, FAIRNESS_SUFFICIENCY_FILE),
                                      orient='records')

        # 6.- List with pairs of highly correlated variables "fairness_highest_correlation.json"
        self.highest_correlation_features.to_json(os.path.join(self.__destination_path,
                                                               FAIRNESS_HIGHEST_CORRELATION_FILE), orient='records')

    def __fit_correlation_features(self, df: pd.DataFrame) -> None:
        """Function that calculates the correlation matrix. Set this information in "__correlation_matrix" attribute.

        :param df: DataFrame with Features, to calculate the Pearson correlation between pairs of Features
        :return: None
        """
        df = self.__encoder_dataset(df=df)
        df_corr = df.corr(method='pearson').abs()
        self.__correlation_matrix = df_corr.where(np.triu(np.ones(df_corr.shape), k=1).astype(np.bool))

    def __encoder_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Function that given a DataFrame, pass all its non-numeric columns to the labelEncoder

        :param df: pd.DataFrame, with dataset to labelEncoder non-numeric columns
        :return: pd.DataFrame, with non-numeric columns encoders
        """
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        all_columns = df.columns.tolist()
        pbar = tqdm(all_columns, disable=not self.verbose)
        for column in pbar:
            if column not in numeric_columns:
                pbar.set_description('Enconding \"{}\" column'.format(column))
                pbar.refresh()
                le = LabelEncoder()
                df[column] = le.fit_transform(df[column])

        return df

    def __find_highest_correlation_features(self, df_correlations: pd.DataFrame, threshold: float,
                                            sensitive_cols: List[str]) -> None:
        """ Given a correlation matrix, a threshold, and a list of sensitive variables; are looking for,
        pairs of variables that have a correlation greater than a threshold. Set this information in
        "__highest_correlation_features" attribute.

        :param df_correlations: pd.DataFrame. Matrix with the value of correlations between pairs of features.
        :param threshold: float, with the threshold (pearson correlation) that considers a pair of highly
        correlated features
        :param sensitive_cols: List[str], with the sensitive features (df column names) to evaluate the
        Fairness criteria
        :return: None
        """
        correlations_list = list()
        pbar = tqdm(df_correlations.columns, disable=not self.verbose)
        for column in pbar:
            pbar.set_description('Checking \"{}\" column'.format(column))
            pbar.refresh()
            if len(df_correlations[df_correlations[column] > threshold].index) > 0:
                for row in df_correlations[df_correlations[column] > threshold].index:
                    correlations_list.append({FEATURE_1: column,
                                              FEATURE_2: row,
                                              CORRELATION_VALUE: df_correlations[column][row],
                                              IS_CORRELATION_SENSIBLE: any(
                                                  item in [column, row] for item in sensitive_cols)})

        # Set attribute
        self.__highest_correlation_features = correlations_list

        if len(correlations_list) == 0:
            xgprint(self.verbose, 'There are no correlated variables above the {} threshold'.format(threshold))
        else:
            xgprint(self.verbose, 'Highly correlated variables above the {} Threshold'.format(threshold))
            xgprint(self.verbose, self.highest_correlation_features)

    def __process_sensitive_column(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str,
                                   target_label: str, sensitive_value: Union[str, List[str]],
                                   is_sensitive_col_binary: bool) -> None:
        """Function that has to write in the attributes of the class the different values of the criteria for each
        pair of values "Value_feature - Value_target"

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_col: str, Name of the DataFrame (df) column with the sensitive feature
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the DataFrame column (df) that contains target (ground truth or y_real) \
        of each element
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :param is_sensitive_col_binary: bool, indicates whether the sensitive feature is binary or not
        :return: None
        """
        sensitive_val = (sensitive_value[0] if is_sensitive_col_binary else sensitive_value)
        independence, separation, sufficiency = self.fairness_metrics(df=df,
                                                                      sensitive_col=sensitive_col,
                                                                      target_col=target_col,
                                                                      predict_col=predict_col,
                                                                      target_label=target_label,
                                                                      sensitive_value=sensitive_val)

        # Calculation of the weights of each of the Scores
        group_by_predict_cols = [predict_col] if is_sensitive_col_binary else [sensitive_col, predict_col]
        group_by_taget_cols = [target_col] if is_sensitive_col_binary else [sensitive_col, target_col]

        # Calculation of the weight (percentage) that the predict_label has against the sensitive feature
        score_predict_weight = self.__score_weight(df=df,
                                                   groupby_cols=group_by_predict_cols,
                                                   sensitive_col=sensitive_col,
                                                   sensitive_value=sensitive_val,
                                                   predict_col=predict_col,
                                                   target_label=target_label)

        # Calculation of the weight (percentage) that the target_label has against the sensitive feature
        score_target_weight = self.__score_weight(df=df,
                                                  groupby_cols=group_by_taget_cols,
                                                  sensitive_col=sensitive_col,
                                                  sensitive_value=sensitive_val,
                                                  predict_col=target_col,
                                                  target_label=target_label)

        result_dict = {SENSITIVE_FEATURE: sensitive_col,
                       SENSITIVE_VALUE: (" | ".join(sensitive_value) if is_sensitive_col_binary
                                         else sensitive_value),
                       IS_BINARY_SENSITIVE_FEATURE: is_sensitive_col_binary,
                       TARGET_LABEL: target_label,
                       INDEPENDENCE_SCORE: independence,
                       INDEPENDENCE_SCORE_WEIGHT: score_predict_weight,
                       INDEPENDENCE_CATEGORY: self.get_fairness_category(score=independence),
                       SEPARATION_SCORE: separation,
                       SEPARATION_SCORE_WEIGHT: score_predict_weight,
                       SEPARATION_CATEGORY: self.get_fairness_category(score=separation),
                       SUFFICIENCY_SCORE: sufficiency,
                       SUFFICIENCY_SCORE_WEIGHT: score_target_weight,
                       SUFFICIENCY_CATEGORY: self.get_fairness_category(score=sufficiency)
                       }

        self.__fairness_info.append(result_dict)

    def __global_scores(self) -> None:
        """Function that receives the scores of the fairness criteria and their weights with respect to the target
        and calculates its weighted "global score" for each criterion. These calculations are assigned to the
        attribute of the class "__global_scores_info".

        :return: None
        """
        sensitive_cols = self.fairness_info[SENSITIVE_FEATURE].unique()
        pbar = tqdm(sensitive_cols, disable=not self.verbose)
        for sensitive_feature in pbar:
            pbar.set_description('Processing Global Score \"{}\" Feature'.format(sensitive_feature))
            pbar.refresh()
            df = self.fairness_info[self.fairness_info[SENSITIVE_FEATURE] == sensitive_feature]
            independence_score = np.average(a=df[INDEPENDENCE_SCORE], weights=df[INDEPENDENCE_SCORE_WEIGHT])
            separation_score = np.average(a=df[SEPARATION_SCORE], weights=df[SEPARATION_SCORE_WEIGHT])
            sufficiency_score = np.average(a=df[SUFFICIENCY_SCORE], weights=df[SUFFICIENCY_SCORE_WEIGHT])

            result_dict = {SENSITIVE_FEATURE: sensitive_feature,
                           INDEPENDENCE_GLOBAL_SCORE: independence_score,
                           INDEPENDENCE_CATEGORY: self.get_fairness_category(score=independence_score),
                           SEPARATION_GLOBAL_SCORE: separation_score,
                           SEPARATION_CATEGORY: self.get_fairness_category(score=separation_score),
                           SUFFICIENCY_GLOBAL_SCORE: sufficiency_score,
                           SUFFICIENCY_CATEGORY: self.get_fairness_category(score=sufficiency_score)}

            self.__global_scores_info.append(result_dict)
