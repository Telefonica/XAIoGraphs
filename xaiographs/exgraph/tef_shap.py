import time
from itertools import combinations
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import scipy
from numpy import ndarray

from xaiographs.exgraph.explainer import Explainer

COALITIONS = 'coalitions'
COALITIONS_WEIGHTS = 'coalitions_weights'
DEFAULT_TARGET_COLS = ['target']
DF_EXPLANATION = 'df_explanation'
MODEL = 'model'
PHI0 = 'phi0'
QUALITY_MEASURE = 'quality_measure'
SHAPLEY_VALUES = 'shapley_values'


class TefShap(Explainer):

    def __init__(self, explainer_params: Dict):
        self.explainer_params: Dict = explainer_params

    def train(self, dataframe: pd.DataFrame, target_cols: List[str], count_col: Optional[str] = 'count') -> Dict:
        """
        In this function, starting from a properly formatted dataframe, we generate a training model, the list of
        possible coalitions and the weight of each of these coalitions.

        :params: dataframe: pd.DataFrame used as importance stimator.
        :params: target_cols: List['str'] with all column names identified as target.
        :params: count_col: Optional[str] used to count the targets concurrences.
        :return: Dict. with the following structure and keys:
                - model: Dict:
                - coalitions: Dict: with all possible coalitions based on features
                - coalitions_weight: Dict: weight of each coalition
        """
        start = time.time()

        if target_cols is None:
            target_cols = DEFAULT_TARGET_COLS

        model_df: pd.DataFrame = (dataframe.groupby([c for c in list(dataframe.columns) if c not in target_cols])
                                  .agg(
            {c: (['count', 'mean'] if i == 0 else ['mean']) for i, c in enumerate(target_cols)})
                                  .reset_index())
        model_df.columns = ['_'.join(col).strip() if col[1] != '' else col[0] for col in model_df.columns.values]
        model_df = model_df.rename(columns={'_'.join([target_cols[0], 'mean']): target_cols[0],
                                            '_'.join([target_cols[0], 'count']): count_col})
        if len(target_cols) > 1:
            model_df = model_df.rename(columns={'_'.join([c, 'mean']): c for c in target_cols[1:]})

        model: Dict = {}
        for c in model_df.columns:
            model[c] = model_df[c].values

        coalitions: Dict = {}
        coalitions_weights: Dict = {}
        cols_names: List = dataframe.columns
        len_names: int = len(cols_names)
        for c in [tmp_c for tmp_c in dataframe.columns if tmp_c not in target_cols]:
            coalitions[c] = TefShap.__get_coalitions(cols_names, c, target_cols)
            coalitions_weights[c] = [1 / (scipy.special.comb(len_names - 1 - len(target_cols), len(coalition)) * (
                    len_names - len(target_cols))) for coalition in coalitions[c]]

        print('Training time: {}'.format(time.time() - start))

        return {
            MODEL: model,
            COALITIONS: coalitions,
            COALITIONS_WEIGHTS: coalitions_weights
        }

    def calculate_shapley_values(self, df_discretized: pd.DataFrame, df_normalized: pd.DataFrame,
                                 target_cols: List[str], count_col: Optional[str] = 'count',
                                 res_dict=None, **params) -> Dict:
        """

        :params: df_discretized: pd.DataFrame
        :params: df_normalized: pd.DataFrame
        :params: target_cols: List['str'] with all column names identified as target.
        :params: count_col: Optional[str] used to count the targets concurrences.
        :params: res_dict: Dict
        :return:
        """

        if target_cols is None:
            target_cols = DEFAULT_TARGET_COLS

        if res_dict is None:
            res_dict = dict()

        start = time.time()

        shap_values_list: List = []
        for i in range(df_normalized.shape[0]):
            # Only for trace/log
            if (i > 0) and (i % 100 == 0):
                print('Progress: row {}'.format(i))

            # XAI: para cada fila, calculo de los shapley value
            x = df_normalized.iloc[i]
            shap_values: List = []
            for col in df_normalized.columns:
                # For sobre las columnas: hay que calcular un shapley value para cada columna
                if col in target_cols:
                    continue
                shap_value = np.sum(
                    np.array([TefShap.__coalition_contribution(x, col, coalition, weight, params['model'],
                                                                    res_dict, target_cols, count_col)
                              for coalition, weight in
                              zip(params['coalitions'][col], params['coalitions_weights'][col])]),
                    axis=0)
                shap_values.append(shap_value)
            shap_values_list.append(shap_values)

        print('Computation time: {}'.format(time.time() - start))

        shapley_values = np.array(shap_values_list)

        y_hat_reduced = res_dict[str({})] + np.sum(shapley_values, axis=1)
        counts = [0 for _ in range(len(target_cols))]
        eps_error = 0.000001
        for i in range(len(df_normalized)):
            for j, tar in enumerate(target_cols):
                if abs(y_hat_reduced[i, j] - df_normalized.iloc[i][tar]) > eps_error:
                    counts[j] += 1
                    print(i, tar, y_hat_reduced[i, j], df_normalized.iloc[i][tar])
        local_accuracy_message = 'Discrepancias (predicción modelo original != predicción SHAP) detectadas {}: {}'
        for j, tar in enumerate(target_cols):
            print(local_accuracy_message.format(tar, counts[j]))

        return {
            PHI0: res_dict[str({})],
            SHAPLEY_VALUES: shapley_values,
        }

    def global_explain(self, **params):
        return np.abs(params[SHAPLEY_VALUES]).mean(axis=0)

    @staticmethod
    def __get_coalitions(columns: List[str], col: str, target_cols: List[str]) -> List[List[str]]:
        """
        Given the list of dataframe columns, compute the list of coalitions of columns compatible with the column
        specified in the parameter col.
        :param: columns: List of columns from which build the coalitions.
        :param: col: str, Name of the column to exclude from the coalitions.
        :param: target_cols: str, name of the column target. By default = 'target'.
        :return: A list of coalitions compatible with the column col. Each coalition is itself a List.
        """
        remaining_features: List[str] = [feature for feature in columns if feature not in [col] + target_cols]
        coalitions_list: List = []
        for feature in range(len(remaining_features) + 1):
            for coalition in combinations(remaining_features, feature):
                coalitions_list.append(list(coalition))
        return coalitions_list

    @staticmethod
    def __get_worth(coalition_features: Dict, model: Dict, target_cols: List[str],
                    count_col: Optional[str] = 'count') -> ndarray:
        """
        Compute the coalition worth (\nu(S))

        :param: coalition_features: Dict with features of the coalition for which the "worth" has be estimated.
                                   key: column name
                                   value: value
        :param: model: Dict, model to use for the coalition "worth" estimation.
            Key: column name
            Value: numpy array of values
        :param: targets_col: List[str], list containing the names of the target columns, by default ['target']
        :param: count_col: str, name of the count column, by default 'count'

        :return: np.Array, the "worth" of the current coalition for each target
        """

        cond: np.array = np.ones_like(list(model.values())[0], dtype=np.bool8)
        for k, v in coalition_features.items():
            if isinstance(v, str):
                cond = (cond & (model[k] == v))
            else:
                cond = (cond & (np.abs(model[k] - v) < 10 ** -6))
        counts: np.array = model[count_col][cond]
        return np.array([np.sum(counts * model[target_col][cond]) / np.sum(counts) for target_col in target_cols])

    @staticmethod
    def __coalition_worth(x, coalition: List[str], model: Dict, res_dict: Dict,
                          target_cols: List[str], count_col: Optional[str] = 'count') -> ndarray:
        """Return the coalition worth (\nu(S))

        :param x: Features to use for specialize the coalition template
        :param model: Dict, model to use for the coalition "worth" estimation.
            Key: column name
            Value: numpy array of values
        :param res_dict: Dict, containing the coalition worth already computed.
            Key: str associated to the coalition
            Value: float
        :param: targets_col: List[str], list containing the names of the target columns, by default ['target']
        :param count_col: str, name of the count column, by default 'count'

        :return: float, the "worth" of the current coalition
        """
        coalition_features: Dict = {c: x[c] if isinstance(x[c], str) else float(x[c]) for c in sorted(coalition)}
        str_cf: str = str(coalition_features)
        if res_dict.get(str_cf, None) is not None:
            return res_dict[str_cf]

        to_ret: ndarray = TefShap.__get_worth(coalition_features, model, target_cols, count_col)
        res_dict.update({str_cf: to_ret})
        return to_ret

    @staticmethod
    def __coalition_contribution(x, col: str, coalition: List[str], weight: float, model: Dict, res_dict: Dict,
                                 target_cols: List[str], count_col: Optional[str] = 'count') -> ndarray:
        """
        Compute the contribution of the current coalition to the Shapley value of the column  "col".

        :param: x: Features to use for specialize the coalition template.
        :param: coalition: List, coalition for which the contribution has to be computed.
        :param: weight: float, coalition contribution weight (combinatorial weight)
        :param: model: Dict, model to use for the coalition "worth" estimation.
            key: column name
            value: numpy array of values
        :param: res_dict: Dict, containing the coalition worth already computed.
            key: str associated to the coalition
            value: float
        :param: target_col: str, name of the target column, by default 'target'
        :param: count_col: str, name of the count column, by default 'count'

        :return: float the current coalition contribution to the Shapley Value
        """

        return weight * (TefShap.__coalition_worth(x, coalition + [col], model, res_dict, target_cols, count_col) -
                         TefShap.__coalition_worth(x, coalition, model, res_dict, target_cols, count_col))
