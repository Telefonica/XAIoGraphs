from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
from absl import logging

from xaiographs.common.constants import ID, MEAN, SHAP_SUFFIX
from xaiographs.common.data_access import persist_sample, save_graph_nodes_info, save_local_explainability_info, \
    save_local_dataset_reliability


class Explainer(metaclass=ABCMeta):
    _DEFAULT_TARGET_COLS = ['target']
    _DF_EXPLANATION = 'df_explanation'
    _EPS_ERROR = 0.000001
    _PHI0 = 'phi0'
    _QUALITY_MEASURE = 'quality_measure'
    _SHAPLEY_VALUES = 'shapley_values'
    _TOP1_TARGET = 'top1_target'

    @abstractmethod
    def train(self, df: pd.DataFrame, target_cols: List[str]):
        raise NotImplementedError

    def local_explain(self, df_2_explain: pd.DataFrame, target_cols: List[str], sample_ids: List[Any],
                      **params) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        """
        This function encapsulates the whole process of local explainability: it starts by aggregating features on the
        DataFrame to explain, then calculates Shapley Values and then dissagregation is done so that prediction
        quality can be calculated on the original data

        :param: df_2_explain:   Pandas DataFrame to be explained. Its data has been previously discretized.
        :param: target_cols:    List of strings with all column names identified as target
        :return: Tuple[pd.Dataframe, ]:
        """
        df_aggregated = Explainer.__aggregate(df_2_explain=df_2_explain.drop(ID, axis=1), target_cols=target_cols)

        shapley_dict = self.calculate_shapley_values(df_aggregated=df_aggregated,
                                                     target_cols=target_cols,
                                                     **params)

        return Explainer.__disaggregate(phi0=shapley_dict[Explainer._PHI0],
                                        shapley_values=shapley_dict[Explainer._SHAPLEY_VALUES],
                                        df_2_explain=df_2_explain,
                                        df_aggregated=df_aggregated,
                                        target_cols=target_cols,
                                        sample_ids=sample_ids)

    @abstractmethod
    def global_explain(self, **params):
        raise NotImplementedError

    @staticmethod
    def __aggregate(df_2_explain: pd.DataFrame, target_cols: List[str]) -> pd.DataFrame:
        """
        This function processes the DataFrame provided as parameter so that all its features but the ones in
        target_cols parameter, are aggregated and the means of those in target_cols are computed. Columns are renamed
        accordingly

        :param: df_2_explain: Pandas DataFrame to which the operations described above will be applied
        :param: target_cols:  List of strings with all column names identified as target
        :return:              Pandas DataFrame resulting after applying aforementioned transformations
        """
        df_aggregated = (df_2_explain.groupby([c for c in list(df_2_explain.columns) if c not in target_cols]).agg(
            {c: [MEAN] for c in target_cols}).reset_index())
        df_aggregated.columns = ['_'.join(col).strip() if col[1] != '' else col[0] for col in
                                 df_aggregated.columns]
        return df_aggregated.rename(columns={'_'.join([c, MEAN]): c for c in target_cols})

    @abstractmethod
    def calculate_shapley_values(self, df_aggregated: pd.DataFrame, target_cols: List[str], **params) -> Dict:
        raise NotImplementedError

    @staticmethod
    def sanity_check(ground_truth: np.ndarray, prediction: np.ndarray, target_cols: List[str], scope: str):
        error = np.abs(ground_truth - prediction) > Explainer._EPS_ERROR
        for i, target_col in enumerate(target_cols):
            logging.info('Number of detected discrepancies (original model prediction != SHAP prediction) '
                         'for target {} in the {} dataset: {}'.format(target_col, scope, sum(error[:, i])))

    @staticmethod
    def __disaggregate(phi0: np.ndarray, shapley_values: np.ndarray, df_2_explain: pd.DataFrame,
                       df_aggregated: pd.DataFrame, target_cols: List[str],
                       sample_ids: List[Any]) -> Dict[str, Union[pd.DataFrame, np.ndarray]]:
        """
        This function takes care of propagating the calculated Shapley Values to the DataFrame to be explained (the
        disaggregated DataFrame). A quality measure featuring the divergence between the ground truth and the Shapley
        based prediction is included in the DataFrame to explain too.

        :param: phi0:           Numpy array containing the baseline (prediction when no features are provided) for each
                                target
        :param: shapley_values: Numpy matrix containing the Shapley Values calculated for each aggregated DataFrame row
                                for each feature and for each target. Shape (n_rows x n_features x n_targets)
        :param: df_2_explain:   Pandas DataFrame to be explained
        :param: df_aggregated:  Pandas DataFrame whose features have been aggregated and its targets have been averaged
        :param: target_cols:    List of strings with all column names identified as target
        :return:                Dictionary with two elements: the DataFrame to explain, containing the Shapley values
                                and the quality measure. The second elements are the adapted Shapley values which are
                                calculated by taking into account the quality measure
        """

        # For each feature column and target column pair a new column is generated to store the corresponding
        # Shapley value
        feature_cols = [c for c in df_2_explain.columns if c not in target_cols + [ID]]
        c_shap_columns = []
        for i, c in enumerate(df_aggregated.columns):
            if c in feature_cols:
                for j, target_col in enumerate(target_cols):
                    df_aggregated['{}_{}{}'.format(target_col, c, SHAP_SUFFIX)] = shapley_values[:, i, j]
                    c_shap_columns.append('{}_{}{}'.format(target_col, c, SHAP_SUFFIX))

        # DataFrame to be explained is left joined with the normalized DataFrame (already containing columns with the
        # computed Shapley values). The join is on the features of the DataFrame to be explained
        df_aggregated_features = df_aggregated.drop(target_cols, axis=1)
        df_explanation = pd.merge(df_2_explain, df_aggregated_features, on=feature_cols, how='left')

        # Normalization trick:
        #   Ground truth values are retrieved from df_explanation
        y = df_explanation[target_cols].values

        #   Columns containing shapley values are reshaped: number of rows x number of features x number of targets
        calculated_shapley = df_explanation[c_shap_columns].values.reshape(y.shape[0],
                                                                           shapley_values.shape[1],
                                                                           shapley_values.shape[2])

        #   Predictions calculated as baseline plus the summation of the calculated Shapley values
        y_hat: np.ndarray = phi0 + np.sum(calculated_shapley, axis=1)

        # Difference between ground truth and predictions
        quality_measure: np.ndarray = (y - y_hat)

        # Adapted Shapley results from adding the calculated shapley plus the quality measure divided by the number
        # of features
        adapted_shapley: np.ndarray = calculated_shapley + np.expand_dims(quality_measure / calculated_shapley.shape[1],
                                                                          axis=1)
        # np.save('/home/cx02747/Utils/ad_shapley.npy', adapted_shapley)
        reshaped_adapted_shapley = adapted_shapley.reshape(adapted_shapley.shape[0], -1)
        # TODO: Chequear para el target top1 que PHI0 + adapted shapley es mayor que 0 para cada ID
        # np.save('/home/cx02747/Utils/rad_shapley.npy', reshaped_adapted_shapley)
        for i, c in enumerate(c_shap_columns):
            df_explanation[c] = reshaped_adapted_shapley[:, i]

        quality_measure_columns = []
        adapted_shapley_mask = {}
        for j, target_col in enumerate(target_cols):
            quality_measure_column = '{}_{}'.format(target_col, Explainer._QUALITY_MEASURE)
            df_explanation[quality_measure_column] = quality_measure[:, j]
            quality_measure_columns.append(quality_measure_column)
            target_mask = []
            for c_shap_col in c_shap_columns:
                if not c_shap_col.startswith(target_col):
                    target_mask.append(False)
                else:
                    target_mask.append(True)
            adapted_shapley_mask[target_col] = target_mask

        # Data is formatted for the sanity check
        y = df_explanation[target_cols].values
        y_hat_reduced = phi0 + np.sum(df_explanation[c_shap_columns].values.reshape(-1, adapted_shapley.shape[1],
                                                                                    adapted_shapley.shape[2]), axis=1)
        Explainer.sanity_check(ground_truth=y, prediction=y_hat_reduced, target_cols=target_cols, scope='original')

        ####################################################################################################
        top1_argmax = np.argmax(df_explanation[target_cols].values, axis=1)
        top1_target = np.array([target_cols[am] for am in top1_argmax])
        float_features = df_explanation[feature_cols].select_dtypes('float')

        save_local_dataset_reliability(df_explained=df_explanation, feature_cols=feature_cols,
                                       float_features=float_features, quality_measure_columns=quality_measure_columns,
                                       top1_targets=top1_target, top1_argmax=top1_argmax, sample_ids=sample_ids)

        save_local_explainability_info(df_explained=df_explanation, feature_cols=feature_cols,
                                       c_shap_columns=c_shap_columns, top1_targets=top1_target,
                                       adapted_shapley_mask=adapted_shapley_mask, sample_ids=sample_ids)

        save_graph_nodes_info(df_explained=df_explanation, feature_cols=feature_cols, float_features=float_features,
                              top1_targets=top1_target, sample_ids=sample_ids)

        # if local_reason_why.csv must be generated the following steps must be followed
        persist_sample(pd.read_csv(filepath_or_buffer='/home/cx02747/Utils/reason_why.csv'), sample_ids=sample_ids,
                       path='/home/cx02747/Utils/local_reason_why.csv')
        ####################################################################################################
        return {
            Explainer._DF_EXPLANATION: df_explanation,
            Explainer._SHAPLEY_VALUES: adapted_shapley,
            Explainer._TOP1_TARGET: top1_target
        }
