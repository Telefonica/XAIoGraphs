import os
from typing import List, Tuple, Union

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


class Fairness(object):
    """
    # TODO
    """

    def __init__(self, destination_path: str):
        self.__destination_path = destination_path
        self.__target_values = None
        self.__confusion_matrix = None
        self.__correlation_matrix = None
        self.__highest_correlation_features = None
        self.__fairness_info = list()
        self.__global_scores_info = list()

    @property
    def target_values(self):
        return self.__target_values

    @property
    def confusion_matrix(self):
        return self.__confusion_matrix

    @property
    def correlation_matrix(self):
        return self.__correlation_matrix

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
    def fairness_info(self):
        return pd.DataFrame(self.__fairness_info)[FAIRNESS_INFO_COLS]

    @property
    def independence_info(self):
        return pd.DataFrame(self.__fairness_info)[FAIRNESS_INDEPENDENCE_COLS]

    @property
    def separation_info(self):
        return pd.DataFrame(self.__fairness_info)[FAIRNESS_SEPARATION_COLS]

    @property
    def sufficiency_info(self):
        return pd.DataFrame(self.__fairness_info)[FAIRNESS_SUFFICIENCY_COLS]

    @property
    def fairness_global_info(self):
        return pd.DataFrame(self.__global_scores_info)[FAIRNESS_GLOBAL_SCORES_COLS]

    def independence(self, df: pd.DataFrame, sensitive_col: str, predict_col: str, target_label: str,
                     sensitive_value: str) -> float:
        """ TODO

        A-> Sensitive Feature
        Y-> y_predict (Prediction)
        independence = | P(Y=y∣A=a) - P(Y=y∣A=b) |

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

    def separation(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str, target_label: str,
                   sensitive_value: str) -> float:
        """ TODO

        A-> Sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        separation = | P(Y=1∣T=1,A=a) - P(Y=1∣T=1,A=b) |

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

    def sufficiency(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str, target_label: str,
                    sensitive_value: str) -> float:
        """ TODO

        A-> Sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        sufficiency = | P(T=1∣Y=1,A=a) - P(T=1∣Y=1,A=b) |

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

    def fairness_metrics(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str,
                         target_label: str, sensitive_value: str) -> Tuple[float, float, float]:
        """ TODO
        Tested: fit_fairness_metrics_unit_test

        :param df:
        :param sensitive_col:
        :param target_col:
        :param predict_col:
        :param target_label:
        :param sensitive_value:
        :return:
        """
        independence = self.independence(df=df,
                                         sensitive_col=sensitive_col,
                                         predict_col=predict_col,
                                         target_label=target_label,
                                         sensitive_value=sensitive_value)
        separation = self.separation(df=df,
                                     sensitive_col=sensitive_col,
                                     target_col=target_col,
                                     predict_col=predict_col,
                                     target_label=target_label,
                                     sensitive_value=sensitive_value)
        sufficiency = self.sufficiency(df=df,
                                       sensitive_col=sensitive_col,
                                       target_col=target_col,
                                       predict_col=predict_col,
                                       target_label=target_label,
                                       sensitive_value=sensitive_value)

        return independence, separation, sufficiency

    @staticmethod
    def __score_weight(df: pd.DataFrame, sensitive_col: str, sensitive_value: str, predict_col: str,
                       target_label: str, groupby_cols: List[str]) -> float:
        """ TODO: Función para calcular el porcentaje (peso) que supone el cálculo de algún criterio respecto se su
        predicción y variable sensible
        TESTED: score_weight_unit_test

        :param df:
        :param sensitive_col:
        :param sensitive_value:
        :param predict_col:
        :param target_label:
        :param groupby_cols:
        :return:
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
        """TODO: Función que devuelve una categorías (A+, A, B, C, D, E) en función del score de un criterio
        de fairness
        Tested: get_fairness_category_unit_test

        :param score:
        :return:
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
        """ TODO

        :param df:
        :param sensitive_cols:
        :param target_col:
        :param predict_col:
        :return:
        """
        self.__pre_processing(df=df, sensitive_cols=sensitive_cols, target_col=target_col, predict_col=predict_col)
        self.__in_processing(df=df, sensitive_cols=sensitive_cols, target_col=target_col, predict_col=predict_col)
        self.__post_processing()

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
        """ TODO
        TESTED: in_processing_unit_test

        :param df:
        :param sensitive_cols:
        :param target_col:
        :param predict_col:
        :return:
        """
        for sensitive_col in sensitive_cols:
            sensitive_values = df[sensitive_col].unique()
            for target_label in self.target_values:
                pbar = tqdm(sensitive_values)
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
        """

        :return:
        """

        # Escribe los scores globales para cada una de las variables sensibles
        self.__global_scores()

        # Writing CSVs for the web interface
        if not os.path.exists(self.__destination_path):
            os.mkdir(self.__destination_path)

        # 1.- Matriz de confusión "fairness_confusion_matrix.csv"
        self.confusion_matrix.to_csv(os.path.join(self.__destination_path, FAIRNESS_CONFUSION_MATRIX_FILE),
                                     index=True, header=True)

        # 2.- Tabla resumen:
        #     Por cada uno de los criterios y variables -> Score - Category_Score "fairness_sumarize_criterias.csv"
        self.fairness_global_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_SUMARIZE_CRITERIAS_FILE),
                                         index=False, header=True)

        # 3.- Tabla criterio de independencia:
        #     Por cada Valor de las variables & Targets -> Score - Category_Score "fairness_independence.csv"
        self.independence_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_INDEPENDENCE_FILE),
                                      index=False, header=True)

        # 4.- Tabla criterio de separación:
        #     Por cada Valor de las variables & Targets -> Score - Category_Score "fairness_separation.csv"
        self.separation_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_SEPARATION_FILE),
                                    index=False, header=True)

        # 5.- Tabla criterio de suficiencia:
        #     Por cada Valor de las variables & Targets -> Score - Category_Score "fairness_sufficiency.csv"
        self.sufficiency_info.to_csv(os.path.join(self.__destination_path, FAIRNESS_SUFFICIENCY_FILE),
                                     index=False, header=True)

        # 6.- Listado con pares de variables altamente correladas "fairness_highest_correlation.csv"
        self.highest_correlation_features.to_csv(
            os.path.join(self.__destination_path, FAIRNESS_HIGHEST_CORRELATION_FILE), index=False, header=True)

    def __fit_correlation_features(self, df: pd.DataFrame) -> None:
        """ TODO Función que calcule la matriz de correlaciones
        TESTEADO: fit_correlation_features_unit_test

        :param df:
        :return:
        """
        df = self.__encoder_dataset(df=df)
        df_corr = df.corr(method='pearson').abs()
        self.__correlation_matrix = df_corr.where(np.triu(np.ones(df_corr.shape), k=1).astype(np.bool))

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

    def __process_sensitive_column(self, df: pd.DataFrame, sensitive_col: str, target_col: str, predict_col: str,
                                   target_label: str, sensitive_value: Union[str, List[str]],
                                   is_sensitive_col_binary: bool) -> None:
        """TODO: Función que tiene que escribir en los atributos de la clase correspondientes los diferentes valores de
        los criterios para cada par de valores "valorVariable-valorTarget"

        :param df:
        :param sensitive_col:
        :param target_col:
        :param predict_col:
        :param target_label:
        :param sensitive_value:
        :param is_sensitive_col_binary:
        :return:
        """
        sensitive_val = (sensitive_value[0] if is_sensitive_col_binary else sensitive_value)
        independence, separation, sufficiency = self.fairness_metrics(df=df,
                                                                      sensitive_col=sensitive_col,
                                                                      target_col=target_col,
                                                                      predict_col=predict_col,
                                                                      target_label=target_label,
                                                                      sensitive_value=sensitive_val)

        # Cálculo de los pesos que tienen cada uno de los Scores
        group_by_predict_cols = [predict_col] if is_sensitive_col_binary else [sensitive_col, predict_col]
        group_by_taget_cols = [target_col] if is_sensitive_col_binary else [sensitive_col, target_col]

        # Cálculo del peso (porcentaje) que tiene la etiqueta predict_label frente a la varible sensible
        score_predict_weight = self.__score_weight(df=df,
                                                   groupby_cols=group_by_predict_cols,
                                                   sensitive_col=sensitive_col,
                                                   sensitive_value=sensitive_val,
                                                   predict_col=predict_col,
                                                   target_label=target_label)

        # Calculo del peso (porcentaje) que tiene la etiqueta target_label frente a la varible sensible
        score_target_weight = self.__score_weight(df=df,
                                                  groupby_cols=group_by_taget_cols,
                                                  sensitive_col=sensitive_col,
                                                  sensitive_value=sensitive_val,
                                                  predict_col=target_col,
                                                  target_label=target_label)

        result_dict = {SENSITIVE_FEATURE: sensitive_col,
                       SENSITIVE_VALUE: (" | ".join(sensitive_value) if is_sensitive_col_binary
                                         else sensitive_value[0]),
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
        """Función que dados los scores de los criterios de fairness con sus respectivos pesos, calcula para
        cada criterio su score (global) ponderado

        :return:
        """
        sensitive_cols = self.fairness_info[SENSITIVE_FEATURE].unique()
        pbar = tqdm(sensitive_cols)
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