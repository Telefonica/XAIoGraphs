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
FAIRNESS_CONFUSION_MATRIX_FILE = 'fairness_confusion_matrix.csv'
FAIRNESS_HIGHEST_CORRELATION_FILE = 'fairness_highest_correlation.csv'
FAIRNESS_INDEPENDENCE_FILE = 'fairness_independence.csv'
FAIRNESS_SEPARATION_FILE = 'fairness_separation.csv'
FAIRNESS_SUFFICIENCY_FILE = 'fairness_sufficiency.csv'
FAIRNESS_SUMARIZE_CRITERIAS_FILE = 'fairness_sumarize_criterias.csv'

# Warning message
WARN_MSG = 'WARNING: {} is empty, because nothing has been processed. Execute fit_fairness() function to get results.'


class Fairness(object):
    """The Fairness class offers functionalities to explain how fair or unfair are the classifications made by a \
    (Deep) Machine Learning model on a set of features that we consider sensitive (gender, \
    ethnic group, religion, age, etc.).

    These explanations are based on the 3 fairness criteria (Independence, Separation, and Sufficiency) to assess if \
    a classification model is fair. It will be considered fair if its predictions are not influenced by any \
    of the sensitive features.

    Based on definitions of each fairness criteria, fairness Scores and Categories are calculated in order to \
    explain and identify what class and what value of the sensitive feature is committing a possible \
    injustice in classification.

    To be able to carry out these calculations, the dataset (pandas DataFrame) with features, target (y_true) and \
    predictions (y_predict) of the model are mandatory. From a list with sensitive features to be evaluated, \
    the fairness calculations are made. Here is a simple example of using this class:

    Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN', 'MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                   columns=['gender', 'y_true', 'y_predict'])
            >>> df
              gender y_true y_predict
            0    MEN    YES       YES
            1    MEN    YES       YES
            2  WOMAN     NO        NO
            3    MEN     NO       YES
            4  WOMAN    YES        NO
            5    MEN    YES        NO
            6    MEN    YES       YES
            7  WOMAN    YES       YES
            8    MEN     NO        NO
            9  WOMAN     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            >>> f.fairness_global_info
              sensitive_feature  independence_global_score independence_category  separation_global_score separation_category  sufficiency_global_score sufficiency_category
            0            gender                   0.416667                     E                    0.375                   E                  0.216667                    D
            <BLANKLINE>
    """

    def __init__(self, destination_path: str = './xaiographs_web_files', verbose: int = 0):
        """

        :param destination_path: String, representing the path where output files will be stored
        :param verbose:          Verbosity level, where any value greater than 0 means the message is printed
        """
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
        """Property that returns a list with the different values of the target of the dataset. \
        If the main method "fit_fairness()" has not been executed, it will return a warning message.

        :return: List[str], with target values

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN', 'MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                   columns=['gender', 'y_true', 'y_predict'])
            >>> df
              gender y_true y_predict
            0    MEN    YES       YES
            1    MEN    YES       YES
            2  WOMAN     NO        NO
            3    MEN     NO       YES
            4  WOMAN    YES        NO
            5    MEN    YES        NO
            6    MEN    YES       YES
            7  WOMAN    YES       YES
            8    MEN     NO        NO
            9  WOMAN     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            >>> f.target_values
            array(['YES', 'NO'], dtype=object)
        """
        if self.__target_values is None:
            print(WARN_MSG.format('\"target_values\"'))
        else:
            return self.__target_values

    @property
    def confusion_matrix(self):
        """Property that returns a confusion matrix. \
        If the main method "fit_fairness()" has not been executed, it will return a warning message.

        :return: pd.DataFrame, with Confusion Matrix

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN', 'MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                   columns=['gender', 'y_true', 'y_predict'])
            >>> df
              gender y_true y_predict
            0    MEN    YES       YES
            1    MEN    YES       YES
            2  WOMAN     NO        NO
            3    MEN     NO       YES
            4  WOMAN    YES        NO
            5    MEN    YES        NO
            6    MEN    YES       YES
            7  WOMAN    YES       YES
            8    MEN     NO        NO
            9  WOMAN     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            >>> f.confusion_matrix
            y_predict  NO  YES
            y_true
            NO          3    1
            YES         2    4
        """
        if self.__confusion_matrix is None:
            print(WARN_MSG.format('\"confusion_matrix\"'))
        else:
            return self.__confusion_matrix

    @property
    def correlation_matrix(self):
        """Property that returns correlation matrix (pearson correlation) between features. \
        If the main method "fit_fairness()" has not been executed, it will return a warning message.

        :return: pd.DataFrame, with correlation matrix

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'gender2': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'RED', 'RED', 'RED', 'RED'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                  columns=['gender', 'gender2', 'color', 'y_true', 'y_predict'])
            >>> df
              gender gender2  color y_true y_predict
            0    MAN     MAN   BLUE    YES       YES
            1    MAN     MAN   BLUE    YES       YES
            2  WOMAN   WOMAN  GREEN     NO        NO
            3    MAN     MAN   BLUE     NO       YES
            4  WOMAN   WOMAN   BLUE    YES        NO
            5    MAN     MAN  GREEN    YES        NO
            6    MAN     MAN    RED    YES       YES
            7  WOMAN   WOMAN    RED    YES       YES
            8    MAN     MAN    RED     NO        NO
            9  WOMAN   WOMAN    RED     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            >>> f.correlation_matrix
                     gender  gender2     color
            gender      NaN      1.0  0.228218
            gender2     NaN      NaN  0.228218
            color       NaN      NaN       NaN
        """
        if self.__correlation_matrix is None:
            print(WARN_MSG.format('\"correlation_matrix\"'))
        else:
            return self.__correlation_matrix

    @property
    def highest_correlation_features(self):
        """Property that returns the pairs of features that have a pearson correlation value above a threshold (0.9). \
        If one of these features is a sensitive features, it will be marked with a flag. In the event that there are \
        no highly correlated features, an empty DataFrame will be returned. \
        If the main method "fit_fairness()" has not been executed, it will return a warning message.

        :return: pd.DataFrame, with highest correlation features

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'gender2': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'RED', 'RED', 'RED', 'RED'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                  columns=['gender', 'gender2', 'color', 'y_true', 'y_predict'])
            >>> df
              gender gender2  color y_true y_predict
            0    MAN     MAN   BLUE    YES       YES
            1    MAN     MAN   BLUE    YES       YES
            2  WOMAN   WOMAN  GREEN     NO        NO
            3    MAN     MAN   BLUE     NO       YES
            4  WOMAN   WOMAN   BLUE    YES        NO
            5    MAN     MAN  GREEN    YES        NO
            6    MAN     MAN    RED    YES       YES
            7  WOMAN   WOMAN    RED    YES       YES
            8    MAN     MAN    RED     NO        NO
            9  WOMAN   WOMAN    RED     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            >>> f.highest_correlation_features
              feature_1 feature_2  correlation_value  is_correlation_sensible
            0   gender2    gender                1.0                     True
        """
        if self.__highest_correlation_features is None:
            print(WARN_MSG.format('\"highest_correlation_features\"'))
        else:
            return (pd.DataFrame.from_dict(self.__highest_correlation_features)[FAIRNESS_CORRELATIONS_COLS]
                    if len(self.__highest_correlation_features) > 0
                    else pd.DataFrame(columns=FAIRNESS_CORRELATIONS_COLS))

    @property
    def fairness_categories_score(self):
        """Property that returns a DataFrame with the categories that are assigned to the Fairness criteria based \
        on their score. The categories and ranges of scores are the following:

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

        :return: pd.DataFrame, with categories based on scores

        Example:
            >>> from xaiographs import Fairness
            >>> Fairness().fairness_categories_score
              category  limit_score_pct
            0       A+             0.02
            1        A             0.05
            2        B             0.08
            3        C             0.15
            4        D             0.25
            5        E             1.00
        """
        return pd.DataFrame({'category': FAIRNESS_CATEGORIES_SCORE.keys(),
                             'limit_score_pct': FAIRNESS_CATEGORIES_SCORE.values()})

    @property
    def fairness_info(self):
        """Returns a DataFrame with all information of fairness criterias. For each sensitive feature, for each \
        value of the sensitive feature and for each value of the target, returns (for each fairness criterion) \
        its Score, its Category and its Weight (percentage of the value of the variable and the value target). \
        The datadrame contains the following columns:

            + **sensitive_feature:** sensitive feature name
            + **sensitive_value:** value of sensitive feature
            + **is_binary_sensitive_feature:** indicates whether or not the sensitive feature is binary \
            (if it has two values or more)
            + **target_label:** value of prediction (y_predict)
            + **independence_score:** Independence criterion score
            + **independence_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Independence \
             criterion score
            + **independence_score_weight:** Percentage (sensitive_value & predict_label)/all_rows_dataset
            + **separation_score:** Separation criterion score
            + **separation_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Separation \
            criterion score
            + **separation_score_weight:** Percentage (sensitive_value & predict_label)/all_rows_dataset
            + **sufficiency_score:** Sufficiency criterion score
            + **sufficiency_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Sufficiency \
            criterion score
            + **sufficiency_score_weight:** Percentage (sensitive_value & target_label)/all_rows_dataset

        :return: pd.DataFrame, with all information of fairness criterias

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'RED', 'RED', 'RED', 'RED'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                  columns=['gender', 'color', 'y_true', 'y_predict'])
            >>> df
              gender  color y_true y_predict
            0    MAN   BLUE    YES       YES
            1    MAN   BLUE    YES       YES
            2  WOMAN  GREEN     NO        NO
            3    MAN   BLUE     NO       YES
            4  WOMAN   BLUE    YES        NO
            5    MAN  GREEN    YES        NO
            6    MAN    RED    YES       YES
            7  WOMAN    RED    YES       YES
            8    MAN    RED     NO        NO
            9  WOMAN    RED     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender', 'color'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            WARNING: Probability P(T=YES|Y=YES, A=GREEN) result is Zero, because ZeroDivisionError
            >>> f.fairness_info
              sensitive_feature sensitive_value  is_binary_sensitive_feature target_label  independence_score  ... separation_category  separation_score_weight  sufficiency_score sufficiency_category  sufficiency_score_weight
            0            gender     MAN | WOMAN                         True          YES            0.416667  ...                   D                      0.5           0.250000                    D                       0.6
            1            gender     MAN | WOMAN                         True           NO            0.416667  ...                   E                      0.5           0.166667                    D                       0.4
            2             color            BLUE                        False          YES            0.416667  ...                  A+                      0.3           0.333333                    E                       0.3
            3             color           GREEN                        False          YES            0.625000  ...                   E                      0.0           0.800000                    E                       0.1
            4             color             RED                        False          YES            0.000000  ...                   E                      0.2           0.333333                    E                       0.2
            5             color            BLUE                        False           NO            0.416667  ...                   E                      0.1           0.750000                    E                       0.1
            6             color           GREEN                        False           NO            0.625000  ...                   E                      0.2           0.166667                    D                       0.1
            7             color             RED                        False           NO            0.000000  ...                   E                      0.2           0.666667                    E                       0.2
            <BLANKLINE>
        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"fairness_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_INFO_COLS]

    @property
    def independence_info(self):
        """Returns a DataFrame with all information of Independence criterion. For each sensitive feature, for each \
        value of the sensitive feature and for each value of the target, returns (for Independence criterion) \
        its Score and its Category. The datadrame contains the following columns:

            + **sensitive_feature:** sensitive feature name
            + **sensitive_value:** value of sensitive feature
            + **target_label:** value of prediction (y_predict)
            + **independence_score:** Independence criterion score
            + **independence_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Independence \
             criterion score

        :return: pd.DataFrame, with all information of Independence criterion

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'RED', 'RED', 'RED', 'RED'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                  columns=['gender', 'color', 'y_true', 'y_predict'])
            >>> df
              gender  color y_true y_predict
            0    MAN   BLUE    YES       YES
            1    MAN   BLUE    YES       YES
            2  WOMAN  GREEN     NO        NO
            3    MAN   BLUE     NO       YES
            4  WOMAN   BLUE    YES        NO
            5    MAN  GREEN    YES        NO
            6    MAN    RED    YES       YES
            7  WOMAN    RED    YES       YES
            8    MAN    RED     NO        NO
            9  WOMAN    RED     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender', 'color'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            WARNING: Probability P(T=YES|Y=YES, A=GREEN) result is Zero, because ZeroDivisionError
            >>> f.independence_info
              sensitive_feature sensitive_value target_label  independence_score independence_category
            0            gender     MAN | WOMAN          YES            0.416667                     E
            1            gender     MAN | WOMAN           NO            0.416667                     E
            2             color            BLUE          YES            0.416667                     E
            3             color           GREEN          YES            0.625000                     E
            4             color             RED          YES            0.000000                    A+
            5             color            BLUE           NO            0.416667                     E
            6             color           GREEN           NO            0.625000                     E
            7             color             RED           NO            0.000000                    A+
            <BLANKLINE>
        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"independence_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_INDEPENDENCE_COLS]

    @property
    def separation_info(self):
        """Returns a DataFrame with all information of Separation criterion. For each sensitive feature, for each \
        value of the sensitive feature and for each value of the target, returns (for Separation criterion) \
        its Score and its Category. The datadrame contains the following columns:

            + **sensitive_feature:** sensitive feature name
            + **sensitive_value:** value of sensitive feature
            + **target_label:** value of prediction (y_predict)
            + **separation_score:** Separation criterion score
            + **separation_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Separation \
            criterion score

        :return: pd.DataFrame, with all information of Separation criterion

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'RED', 'RED', 'RED', 'RED'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                  columns=['gender', 'color', 'y_true', 'y_predict'])
            >>> df
              gender  color y_true y_predict
            0    MAN   BLUE    YES       YES
            1    MAN   BLUE    YES       YES
            2  WOMAN  GREEN     NO        NO
            3    MAN   BLUE     NO       YES
            4  WOMAN   BLUE    YES        NO
            5    MAN  GREEN    YES        NO
            6    MAN    RED    YES       YES
            7  WOMAN    RED    YES       YES
            8    MAN    RED     NO        NO
            9  WOMAN    RED     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender', 'color'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            WARNING: Probability P(T=YES|Y=YES, A=GREEN) result is Zero, because ZeroDivisionError
            >>> f.separation_info
              sensitive_feature sensitive_value target_label  separation_score separation_category
            0            gender     MAN | WOMAN          YES          0.250000                   D
            1            gender     MAN | WOMAN           NO          0.500000                   E
            2             color            BLUE          YES          0.000000                  A+
            3             color           GREEN          YES          0.800000                   E
            4             color             RED          YES          0.500000                   E
            5             color            BLUE           NO          1.000000                   E
            6             color           GREEN           NO          0.333333                   E
            7             color             RED           NO          0.500000                   E
            <BLANKLINE>
        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"separation_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_SEPARATION_COLS]

    @property
    def sufficiency_info(self):
        """Returns a DataFrame with all information of Sufficiency criterion. For each sensitive feature, for each \
        value of the sensitive feature and for each value of the target, returns (for Sufficiency criterion) \
        its Score and its Category. The datadrame contains the following columns:

            + **sensitive_feature:** sensitive feature name
            + **sensitive_value:** value of sensitive feature
            + **target_label:** value of prediction (y_predict)
            + **sufficiency_score:** Sufficiency criterion score
            + **sufficiency_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Sufficiency \
            criterion score

        :return: pd.DataFrame, with all information of Sufficiency criterion

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'RED', 'RED', 'RED', 'RED'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                  columns=['gender', 'color', 'y_true', 'y_predict'])
            >>> df
              gender  color y_true y_predict
            0    MAN   BLUE    YES       YES
            1    MAN   BLUE    YES       YES
            2  WOMAN  GREEN     NO        NO
            3    MAN   BLUE     NO       YES
            4  WOMAN   BLUE    YES        NO
            5    MAN  GREEN    YES        NO
            6    MAN    RED    YES       YES
            7  WOMAN    RED    YES       YES
            8    MAN    RED     NO        NO
            9  WOMAN    RED     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender', 'color'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            WARNING: Probability P(T=YES|Y=YES, A=GREEN) result is Zero, because ZeroDivisionError
            >>> f.sufficiency_info
              sensitive_feature sensitive_value target_label  sufficiency_score sufficiency_category
            0            gender     MAN | WOMAN          YES           0.250000                    D
            1            gender     MAN | WOMAN           NO           0.166667                    D
            2             color            BLUE          YES           0.333333                    E
            3             color           GREEN          YES           0.800000                    E
            4             color             RED          YES           0.333333                    E
            5             color            BLUE           NO           0.750000                    E
            6             color           GREEN           NO           0.166667                    D
            7             color             RED           NO           0.666667                    E
            <BLANKLINE>
        """
        if len(self.__fairness_info) == 0:
            print(WARN_MSG.format('\"sufficiency_info\"'))
        else:
            return pd.DataFrame(self.__fairness_info)[FAIRNESS_SUFFICIENCY_COLS]

    @property
    def fairness_global_info(self):
        """Returns a DataFrame with "Global Scores" (weighted aggregation of the scores for each fairness criteria) \
        for each sensitive feature and assigns it a category *{A+, A, B, C, D, E}*. \
        The datadrame contains the following columns:

            + **sensitive_feature:** sensitive feature name
            + **independence_global_score:** Independence global criterion score
            + **independence_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Independence global \
             criterion score
            + **separation_global_score:** Separation global criterion score
            + **separation_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Separation global \
            criterion score
            + **sufficiency_global_score:** Sufficiency global criterion score
            + **sufficiency_category:** Category *{A+, A, B, C, D, E}* assigned to the value of Sufficiency global \
            criterion score

        :return: pd.DataFrame, with "Global Scores"

        Example:
            >>> import pandas as pd
            >>> pd.set_option('display.max_columns', None)
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'RED', 'RED', 'RED', 'RED'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                  columns=['gender', 'color', 'y_true', 'y_predict'])
            >>> df
              gender  color y_true y_predict
            0    MAN   BLUE    YES       YES
            1    MAN   BLUE    YES       YES
            2  WOMAN  GREEN     NO        NO
            3    MAN   BLUE     NO       YES
            4  WOMAN   BLUE    YES        NO
            5    MAN  GREEN    YES        NO
            6    MAN    RED    YES       YES
            7  WOMAN    RED    YES       YES
            8    MAN    RED     NO        NO
            9  WOMAN    RED     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fit_fairness(df=df,
            ...                sensitive_cols=['gender', 'color'],
            ...                target_col='y_true',
            ...                predict_col='y_predict')
            WARNING: Probability P(T=YES|Y=YES, A=GREEN) result is Zero, because ZeroDivisionError
            >>> f.fairness_global_info
              sensitive_feature  independence_global_score independence_category  \
            0            gender                   0.416667                     E
            1             color                   0.291667                     E
            <BLANKLINE>
               separation_global_score separation_category  sufficiency_global_score  \
            0                 0.375000                   E                  0.216667
            1                 0.366667                   E                  0.471667
            <BLANKLINE>
        """
        if len(self.__global_scores_info) == 0:
            print(WARN_MSG.format('\"fairness_global_info\"'))
        else:
            return pd.DataFrame(self.__global_scores_info)[FAIRNESS_GLOBAL_SCORES_COLS]

    def independence_score(self, df: pd.DataFrame, sensitive_col: str, predict_col: str, target_label: str,
                           sensitive_value: str) -> float:
        """This function returns a score for the independence criterion.
        We say that the random variables (Y, A) satisfy independence if the sensitive feature 'A'
        are statistically independent of the prediction 'Y'. We define the score as the difference (in absolute value)
        of the probabilities:

        .. math::
            independence\ score = | P(Y=y∣A=a) - P(Y=y∣A=b) |

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_col: str, Name of the dataframe (df) column with the sensitive feature
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the dataframe column (df) that contains target (ground truth or y_real) \
        of each element
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :return: float, independence score value

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                   columns=['gender', 'y_true', 'y_predict'])
            >>> df
              gender y_true y_predict
            0    MAN    YES       YES
            1    MAN    YES       YES
            2  WOMAN     NO        NO
            3    MAN     NO       YES
            4  WOMAN    YES        NO
            5    MAN    YES        NO
            6    MAN    YES       YES
            7  WOMAN    YES       YES
            8    MAN     NO        NO
            9  WOMAN     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.independence_score(df=df,
            ...                      sensitive_col='gender',
            ...                      predict_col='y_predict',
            ...                      target_label='YES',
            ...                      sensitive_value='MAN')
            0.41666666666666663
        Detail calculations:

        .. math::
            P(Y = 'YES' | A = 'MEN') = 4 / 6 = 0.66
        .. math::
            P(Y = 'YES' | A = 'WOMAN') = 1 / 4 = 0.25
        .. math::
            independence\ score = |0.66 - 0.25| = 0.41
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
        """This function returns a score for the separation criterion.
        We say the random variables (Y, A, T) satisfy separation if the sensitive characteristics 'A' are
        statistically independent of the prediction 'Y' given the target value 'T'. We define the score as the
        difference (in absolute value) of the probabilities:

        .. math::
            separation\ score = | P(Y=y∣T=t,A=a) - P(Y=y∣T=t,A=b) |

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_col: str, Name of the dataframe (df) column with the sensitive feature
        :param target_col: str, Name of the dataframe (df) that contains target (ground truth or y_real)
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the dataframe column (df) that contains target (ground truth or y_real) \
        of each element
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :return: float, separation score value

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                   columns=['gender', 'y_true', 'y_predict'])
            >>> df
              gender y_true y_predict
            0    MAN    YES       YES
            1    MAN    YES       YES
            2  WOMAN     NO        NO
            3    MAN     NO       YES
            4  WOMAN    YES        NO
            5    MAN    YES        NO
            6    MAN    YES       YES
            7  WOMAN    YES       YES
            8    MAN     NO        NO
            9  WOMAN     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.separation_score(df=df,
            ...                    sensitive_col='gender',
            ...                    target_col='y_true',
            ...                    predict_col='y_predict',
            ...                    target_label='YES',
            ...                    sensitive_value='MAN')
            0.25
        Detail calculations:

        .. math::
            P(Y = 'YES' | T = 'YES', A = 'MAN') = 3 / 4 = 0.75
        .. math::
            P(Y = 'YES' | T = 'YES', A = 'WOMAN') = 1 / 2 = 0.5
        .. math::
            separation\ score = |0.75 - 0.5| = 0.25
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
        """This function returns a score for the sufficiency criterion.
        We say the random variables (Y,A,T) satisfy sufficiency if the sensitive characteristics 'A' are
        statistically independent of the target value 'T' given the prediction 'Y'. We define the score as the
        difference (in absolute value) of the probabilities:

        .. math::
            sufficiency\ score = | P(T=t∣Y=y,A=a) - P(T=t∣Y=y,A=b) |

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_col: str, Name of the dataframe (df) column with the sensitive feature
        :param target_col: str, Name of the dataframe (df) that contains target (ground truth or y_real)
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the dataframe column (df) that contains target (ground truth or y_real) \
        of each element
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :return: float, sufficiency score value

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                   columns=['gender', 'y_true', 'y_predict'])
            >>> df
              gender y_true y_predict
            0    MAN    YES       YES
            1    MAN    YES       YES
            2  WOMAN     NO        NO
            3    MAN     NO       YES
            4  WOMAN    YES        NO
            5    MAN    YES        NO
            6    MAN    YES       YES
            7  WOMAN    YES       YES
            8    MAN     NO        NO
            9  WOMAN     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.sufficiency_score(df=df,
            ...                     sensitive_col='gender',
            ...                     target_col='y_true',
            ...                     predict_col='y_predict',
            ...                     target_label='YES',
            ...                     sensitive_value='MAN')
            0.25
        Detail calculations:

        .. math::
            P(T = 'YES' | Y = 'YES', A = 'MAN') = 3 / 4 = 0.75
        .. math::
            P(T = 'YES' | Y = 'YES', A = 'WOMAN') = 1 / 1 = 1.0
        .. math::
            sufficiency\ score = |0.75 - 1.0| = 0.25
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
        """This function returns the scores for the criteria of independence, separation and sufficiency. Being 'A'
        the sensitive variable, 'Y' the prediction and 'T' the real target, these criteria are calculated:

        .. math::
            independence\ score = | P(Y=y∣A=a) - P(Y=y∣A=b) |
        .. math::
            separation\ score = | P(Y=y∣T=t,A=a) - P(Y=y∣T=t,A=b) |
        .. math::
            sufficiency\ score = | P(T=1∣Y=1,A=a) - P(T=1∣Y=1,A=b) |

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_col: str, Name of the dataframe (df) column with the sensitive feature
        :param target_col: str, Name of the dataframe (df) that contains target (ground truth or y_real)
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the dataframe column (df) that contains target (ground truth or y_real) \
        of each element
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :return: Tuple[float, float, float], fairness score metrics (independence score, separation score, \
        sufficiency score)

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
            ...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
            ...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            ...                   columns=['gender', 'y_true', 'y_predict'])
            >>> df
              gender y_true y_predict
            0    MAN    YES       YES
            1    MAN    YES       YES
            2  WOMAN     NO        NO
            3    MAN     NO       YES
            4  WOMAN    YES        NO
            5    MAN    YES        NO
            6    MAN    YES       YES
            7  WOMAN    YES       YES
            8    MAN     NO        NO
            9  WOMAN     NO        NO
            >>> from xaiographs import Fairness
            >>> f = Fairness()
            >>> f.fairness_metrics(df=df,
            ...                    sensitive_col='gender',
            ...                    target_col='y_true',
            ...                    predict_col='y_predict',
            ...                    target_label='YES',
            ...                    sensitive_value='MAN')
            (0.41666666666666663, 0.25, 0.25)
        Detail calculations of each metrics in "independece_score()", "separation_score()" and "sufficiency_score()"
        functions.

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
        :param sensitive_col: str, Name of the dataframe (df) column with the sensitive feature
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the dataframe column (df) that contains target (ground truth or y_real) \
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
        """Given a Score for any Fairness criteria, it assigns a Category to it. The relationship between \
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

        :param score: float, value of the score of the Fairness criterion
        :return: str, category assigned to the score
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

    def fit_fairness(self, df: pd.DataFrame, sensitive_cols: List[str], target_col: str, predict_col: str) -> None:
        """Main function that performs all the calculations of the Fairness class. The calculated results are \
        accessible via the **property** functions of the class.

        :param df: pd.DataFrame, with dataset to process. The dataset must have: *N feature columns*, \
        a *real target* column and *prediction* column.
        :param sensitive_cols: List[str], with the sensitive features (df column names) to evaluate the \
        Fairness criteria
        :param target_col: str, Name of the dataframe (df) that contains target (ground truth or y_real)
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
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
        :param sensitive_col: str, Name of the dataframe (df) column with the sensitive feature
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the dataframe column (df) that contains target (ground truth or y_real) \
        of each element
        :param sensitive_value: str, Value of the sensitive feature for the score calculation
        :return: None
        """
        # Check if sensitive_col, predict_col or target_col column is in dataframe
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
        :param target_col: str, Name of the dataframe (df) that contains target (ground truth or y_real)
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
        :param target_col: str, Name of the dataframe (df) that contains target (ground truth or y_real)
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

        # Writing CSVs for the web interface
        if not os.path.exists(self.__destination_path):
            os.mkdir(self.__destination_path)

        # 1.- Confusion matrix "fairness_confusion_matrix.csv"
        self.confusion_matrix.to_csv(os.path.join(self.__destination_path, FAIRNESS_CONFUSION_MATRIX_FILE),
                                     index=True, header=True)

        # 2.- Summary table:
        #     For each of the criteria and features -> Score - Category_Score "fairness_sumarize_criterias.csv"
        self.fairness_global_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_SUMARIZE_CRITERIAS_FILE),
                                         index=False, header=True)

        # 3.- Independence criteria table:
        #     For each Value of the features & targets -> Score - Category_Score "fairness_independence.csv"
        self.independence_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_INDEPENDENCE_FILE),
                                      index=False, header=True)

        # 4.- Separation criteria table:
        #     For each Value of the features & targets -> Score - Category_Score "fairness_separation.csv"
        self.separation_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_SEPARATION_FILE),
                                    index=False, header=True)

        # 5.- Sufficiency criteria table:
        #     For each Value of the features & targets -> Score - Category_Score "fairness_sufficiency.csv"
        self.sufficiency_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_SUFFICIENCY_FILE),
                                     index=False, header=True)

        # 6.- List with pairs of highly correlated variables "fairness_highest_correlation.csv"
        self.highest_correlation_features.to_csv(
            os.path.join(self.__destination_path, FAIRNESS_HIGHEST_CORRELATION_FILE), index=False, header=True)

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
        :param sensitive_col: str, Name of the dataframe (df) column with the sensitive feature
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param predict_col: str, Name of the column of the data frame (df) that contains predictions of each element
        :param target_label: str, Name of the dataframe column (df) that contains target (ground truth or y_real) \
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
