from abc import ABCMeta, abstractmethod
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd

DF_EXPLANATION = 'df_explanation'
PHI0 = 'phi0'
QUALITY_MEASURE = 'quality_measure'
SHAPLEY_VALUES = 'shapley_values'


class Explainer(metaclass=ABCMeta):
    NAME = 'name'

    @abstractmethod
    def train(self, dataframe, target_cols: List[str], **params):
        raise NotImplementedError

    def local_explain(self, df_discretized: pd.DataFrame, target_cols: List[str], **params) \
            -> Tuple[pd.DataFrame, List[float]]:
        """

        :params: df_discretized: pd.DataFrame to explain with data previously discretized.
        :params: target_cols: List['str'] with all column names identified as target.
        :return: Tuple[pd.Dataframe, ]:
        """
        df_normalized = Explainer.__normalize(df_2_normalize=df_discretized, target_cols=target_cols)

        shapley_dict = self.calculate_shapley_values(df_discretized=df_discretized,
                                                     df_normalized=df_normalized,
                                                     target_cols=target_cols,
                                                     **params)
        return Explainer.__denormalize(phi0=shapley_dict[PHI0],
                                       shapley_values=shapley_dict[SHAPLEY_VALUES],
                                       df_2_explain=df_discretized,
                                       df_normalized=df_normalized,
                                       target_cols=target_cols)

    @abstractmethod
    def global_explain(self, **params):
        raise NotImplementedError

    @staticmethod
    def __normalize(df_2_normalize: pd.DataFrame, target_cols: List[str]) -> pd.DataFrame:
        """
        :params: df_2_normalize: pd.DataFrame to normalized
        :params: target_cols: List['str'] with all column names identified as target.
        :return: pd.Dataframe after normalized the source pd.Dataframe.
        """
        df_2_normalize_aux: pd.DataFrame = (df_2_normalize
                                            .groupby([c for c in list(df_2_normalize.columns) if c not in target_cols])
                                            .agg({c: ['mean'] for c in target_cols})
                                            .reset_index())
        df_2_normalize_aux.columns = ['_'.join(col).strip() if col[1] != '' else col[0] for col in
                                      df_2_normalize_aux.columns.values]
        return df_2_normalize_aux.rename(columns={'_'.join([c, 'mean']): c for c in target_cols})

    @abstractmethod
    def calculate_shapley_values(self, df_discretized: pd.DataFrame, df_normalized: pd.DataFrame,
                                 target_cols: List[str], **params) -> Dict:
        raise NotImplementedError

    @staticmethod
    def __denormalize(phi0, shapley_values, df_2_explain: pd.DataFrame, df_normalized: pd.DataFrame,
                      target_cols: List[str]) -> Dict:
        """
        [pd.DataFrame, List[float]]


        """



        # Trasladamos la explicación al dataset original
        c_shap_columns = []
        for i, c in enumerate(df_normalized.columns):
            if c not in target_cols:
                for j, tar in enumerate(target_cols):
                    df_normalized['{}_{}_shap'.format(tar, c)] = shapley_values[:, i, j]
                    c_shap_columns.append('{}_{}_shap'.format(tar, c))

        column_names = [c for c in df_2_explain.columns if c not in target_cols]

        df_normalized_drop = df_normalized.drop(target_cols, axis=1)

        df_explanation = pd.merge(df_2_explain, df_normalized_drop, on=column_names, how='left')

        # Normalization trick
        y = df_explanation[target_cols].values
        calculated_shapley = df_explanation[c_shap_columns].values.reshape(y.shape[0],
                                                                           shapley_values.shape[1],
                                                                           shapley_values.shape[2])
        y_hat = phi0 + np.sum(calculated_shapley, axis=1)
        quality_measure = (y - y_hat)
        adapted_shapley = calculated_shapley + np.expand_dims(quality_measure / calculated_shapley.shape[1], axis=1)
        for i, c in enumerate(c_shap_columns):
            df_explanation[c] = adapted_shapley[:, i]
        df_explanation[QUALITY_MEASURE] = quality_measure
        # END: Trasladamos la explicación al dataset original

        # Chequeo del Accuracy local sobre el dataset original
        eps_error = 0.000001
        count_original_ds = [0 for _ in range(len(target_cols))]
        for index in range(len(df_explanation)):
            for j, tar in enumerate(target_cols):
                if abs(sum(df_explanation[
                               c_shap_columns[j * shapley_values.shape[1]: (j + 1) * shapley_values.shape[1]]].values[
                           index, :]) + phi0[j] - df_explanation[tar].values[index]) > eps_error:
                    count_original_ds[j] += 1
                    value_message = df_explanation[c_shap_columns[
                                                   j * shapley_values.shape[1]: (j + 1) * shapley_values.shape[
                                                       1]]].values[index, :]
                    print(' VALUE: {}'.format(value_message))
                    sum_message = sum(df_explanation[c_shap_columns[
                                                     j * shapley_values.shape[1]: (j + 1) * shapley_values.shape[
                                                         1]]].values[index, :]) + phi0[j]
                    print('   SUM: {}'.format(sum_message))
                    print('TARGET: {}'.format(df_explanation[tar].values[index]))

                    print('Shapely : {}'.format(calculated_shapley[index, :, j]))
                    print('SUM_Shap: {}'.format(sum(calculated_shapley[index, :, j]) + phi0[j]))

        original_local_accuracy_message = 'Discrepancias (predicción modelo original != predicción SHAP) detectadas ' \
                                          'DATASET ORIGINAL {}: {}'
        for j, tar in enumerate(target_cols):
            print(original_local_accuracy_message.format(tar, count_original_ds[j]))

        return {
            DF_EXPLANATION: df_explanation,
            SHAPLEY_VALUES: adapted_shapley
        }
