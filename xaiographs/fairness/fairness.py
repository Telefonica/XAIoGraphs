import os
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from copy import deepcopy
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

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
FAIRNESS_METRICS_COLS = [SENSITIVE_FEATURE, SENSITIVE_VALUE, IS_BINARY_SENSITIVE_FEATURE, TARGET_LABEL,
                         INDEPENDENCE_SCORE, INDEPENDENCE_CATEGORY, INDEPENDENCE_SCORE_WEIGHT, SEPARATION_SCORE,
                         SEPARATION_CATEGORY, SEPARATION_SCORE_WEIGHT, SUFFICIENCY_SCORE, SUFFICIENCY_CATEGORY,
                         SUFFICIENCY_SCORE_WEIGHT]
FAIRNESS_GLOBAL_SCORES_COLS = [SENSITIVE_VALUE, INDEPENDENCE_GLOBAL_SCORE, INDEPENDENCE_CATEGORY,
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


class Fairness(object):
    """
    # TODO
    """

    def __init__(self, destination_path: str):
        self.destination_path = destination_path
        self.__target_values = None
        self.__confusion_matrix = None
        self.__correlation_matrix = None
        self.__highest_correlation_features = None
        self.__fairness_metrics = list()
        self.__independence_info = list()
        self.__separation_info = list()
        self.__sufficiency_info = list()
        self.__global_scores = list()
        self.__independence_score = list()
        self.__separation_score = list()
        self.__sufficiency_score = list()

    @property
    def target_values(self):
        return self.__target_values

    @property
    def confusion_matrix(self):
        return None

    @property
    def correlation_matrix(self):
        return None

    @property
    def highest_correlation_features(self):
        """TODO: devuelve un dataframe vacio con cabecera, en caso de que no haya variables altamente correladas

        :return:
        """
        return (pd.DataFrame.from_dict(self.__highest_correlation_features)[FAIRNESS_CORRELATIONS_COLS]
                if len(self.__highest_correlation_features) > 0
                else pd.DataFrame(columns=FAIRNESS_CORRELATIONS_COLS))

    @property
    def fairness_categories_score(self):
        return pd.DataFrame({'category': FAIRNESS_CATEGORIES_SCORE.keys(),
                             'limit_score_pct': FAIRNESS_CATEGORIES_SCORE.values()})

    @property
    def fairness_metrics(self):
        return None

    @property
    def independence_info(self):
        return None

    @property
    def separation_info(self):
        return None

    @property
    def sufficiency_info(self):
        return None

    @property
    def global_scores(self):
        return None

    @property
    def independence_score(self):
        return None

    @property
    def separation_score(self):
        return None

    @property
    def sufficiency_score(self):
        return None

    def fit_independence(self, df: pd.DataFrame, sensitive_col: str, predict_col: str, target_label: str,
                         sensitive_value: str) -> float:
        """

        A-> Sensitive Feature
        Y-> y_predict (Prediction)
        independence score = | P(Y=y∣A=a) - P(Y=y∣A=b) |

        :param df:
        :param sensitive_col:
        :param predict_col:
        :param target_label:
        :param sensitive_value:
        :return:
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

    def fit_separation(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str, target_label: str,
                       sensitive_value: str) -> float:
        """

        A-> Sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        separation score = | P(Y=1∣T=1,A=a) - P(Y=1∣T=1,A=b) |

        :param df:
        :param sensitive_col:
        :param target_col:
        :param predict_col:
        :param target_label:
        :param sensitive_value:
        :return:
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

    def fit_sufficiency(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str,
                        target_label: str, sensitive_value: str) -> float:
        """

        A-> Sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        sufficiency score = | P(T=1∣Y=1,A=a) - P(T=1∣Y=1,A=b) |

        :param df:
        :param sensitive_col:
        :param target_col:
        :param predict_col:
        :param target_label:
        :param sensitive_value:
        :return:
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

    def fit_fairness(self, df: pd.DataFrame, sensitive_cols: List[str], target_col: str, predict_col: str) -> None:
        """

        :param df:
        :param sensitive_cols:
        :param target_col:
        :param predict_col:
        :return:
        """
        self.__pre_processing(df=df,
                              sensitive_cols=sensitive_cols,
                              target_col=target_col,
                              predict_col=predict_col)

        self.__in_processing(df=df,
                             sensitive_cols=sensitive_cols,
                             target_col=target_col,
                             predict_col=predict_col)

        self.__post_processing(df=df,
                               sensitive_cols=sensitive_cols,
                               target_col=target_col,
                               predict_col=predict_col)

    @staticmethod
    def __check_dataset_values(df: pd.DataFrame, sensitive_col: str, target_col: Union[str, None], predict_col: str,
                               target_label: str, sensitive_value: str) -> None:
        """ TODO

        :param df:
        :param sensitive_col:
        :param predict_col:
        :param target_label:
        :param sensitive_value:
        :return:
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
        """ TODO: Función que realiza los procesamientos de datos previos a los cálculos "core" de la clase

        :param df:
        :param sensitive_cols:
        :param target_col:
        :param predict_col:
        :return:
        """
        # Obtain distinct target values
        self.target_values = df[predict_col].unique()

        # Confusion Matrix: Target in rows and predictions in columns
        self.__confusion_matrix = pd.crosstab(df[target_col],
                                              df[predict_col],
                                              rownames=[target_col],
                                              colnames=[predict_col])

        # Features Correlation Matrix
        df_process = deepcopy(df[[feature for feature in df.columns if feature not in [target_col, predict_col]]])
        self.__correlation_matrix = self.__fit_correlation_features(df_dataset=df_process)

        # Search for highly correlated features
        self.__highest_correlation_features = self.__find_highest_correlation_features(
            df_correlations=self.__correlation_matrix,
            threshold=0.9,
            sensitive_cols=sensitive_cols)

    def __in_processing(self, df: pd.DataFrame, sensitive_cols: List[str], target_col: str, predict_col: str) -> None:
        """ TODO

        :param df:
        :param sensitive_cols:
        :param target_col:
        :param predict_col:
        :return:
        """
        pass

    def __post_processing(self, df: pd.DataFrame, sensitive_cols: List[str], target_col: str, predict_col: str) -> None:
        """ TODO

        :param df:
        :param sensitive_cols:
        :param target_col:
        :param predict_col:
        :return:
        """
        pass

    def __fit_correlation_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """ TODO Función que calcule la matriz de correlaciones
        TESTEADO: fit_correlation_features_unit_test

        :param df:
        :return:
        """
        # Eliminamos del Dataset las columnas de target y predicción
        # df_process = deepcopy(
        #     df_dataset[[feature for feature in df_dataset.columns if feature not in [target_col, predict_col]]])
        df = self.__encoder_dataset(df=df)
        df_corr = df.corr(method='pearson').abs()
        return df_corr.where(np.triu(np.ones(df_corr.shape), k=1).astype(np.bool))

    @staticmethod
    def __encoder_dataset(df: pd.DataFrame) -> pd.DataFrame:
        """ TODO: Función que dado un dataFrame, pase todas sus columnas no numéricas a labelEncoder
        TESTEADO: encoder_dataset_unit_test

        :param df:
        :return:
        """
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        all_columns = df.columns.tolist()
        pbar = tqdm(all_columns)
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
        pairs of variables that have a correlation greater than a threshold
        TESTEADO: find_highest_correlation_features_unit_test

        :param df_correlations:
        :param threshold:
        :param sensitive_cols:
        :return:
        """
        correlations_list = list()
        pbar = tqdm(df_correlations.columns)
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
            print('There are no correlated variables above the {} threshold'.format(threshold))
        else:
            print('Highly correlated variables above the {} Threshold'.format(threshold))
            print(self.highest_correlation_features)
