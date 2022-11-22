import time
from itertools import combinations
from typing import Dict, List, Union

import numpy as np
import pandas as pd
import scipy
from tqdm import tqdm

from xaiographs.common.constants import COUNT, MEAN
from xaiographs.exgraph.importance.importance_calculator import ImportanceCalculator


class TefShap(ImportanceCalculator):
    """
    This class implements ImportanceCalculator based on the mathematical Shapley values formula
    """
    _COALITIONS = 'coalitions'
    _COALITIONS_WEIGHTS = 'coalitions_weights'
    _MODEL = 'model'
    _RES_DICT = 'res_dict'

    def __init__(self, explainer_params: Dict, df: pd.DataFrame, sample_ids_mask_2_explain: np.ndarray,
                 feature_cols: List[str], target_cols: List[str], train_size: float = 0.0,
                 train_stratify: bool = False):
        """
        Constructor method for TefShap ImportanceCalculator

        :param explainer_params:            Dictionary containing potentially useful information for this importance
                                            calculator
        :param df:                          Pandas DataFrame used to "train" the calculator
        :param sample_ids_mask_2_explain:   Numpy array mask, which will be applied to the explanation pandas DataFrame
                                            right after global explanation is computed
        :param feature_cols:                List of strings containing the column names for the features
        :param target_cols:                 List of strings containing all column names identified as target
        :param train_size:                  Float indicating the percentage of the pandas DataFrame that will be used
                                            to train the calculator
        :param train_stratify:              Boolean indicating whether target columns proportions will be taken into
                                            account when splitting the data (if train_size > 0.0)
        """
        super(TefShap, self).__init__(df=df, sample_ids_mask_2_explain=sample_ids_mask_2_explain,
                                      feature_cols=feature_cols, target_cols=target_cols, train_size=train_size,
                                      train_stratify=train_stratify)
        self.explainer_params: Dict = explainer_params

    def train(self) -> Dict[str, Dict[str, Union[Dict, Union[np.ndarray, List[List[str]], List[float]]]]]:
        """
        This function trains a model by kind of "memorizing" dataset examples, for this reason, df parameter (which
        represents the dataset) must accurately represent the problem domain. It also takes care of generating the list
         of possible coalitions and computing the corresponding weight for each

        :return:               Dictionary with the following structure and keys:
                               - model: Dictionary with the model column names as keys and the feature values as values
                               - coalitions: Dictionary with the column names as keys and their corresponding lists of
                               coalitions as values
                               - coalitions_weight: Dictionary with the column names as keys and their corresponding
                               list of weights for the list of coalitions associated to that column, as value
                               - res_dict: Empty dictionary, representing the empty coalition
        """
        start = time.time()

        if self.target_cols is None:
            target_cols = ImportanceCalculator._DEFAULT_TARGET_COLS
        else:
            target_cols = self.target_cols

        # The given DataFrame is grouped by its features, COUNT is calculated on the first of the targets in order to
        # know the number of different feature combinations. MEAN is computed on each of the targets
        model_df = (self.df_train.groupby([c for c in list(self.df_train.columns) if c not in target_cols])
                    .agg(
            {c: ([COUNT, MEAN] if i == 0 else [MEAN]) for i, c in enumerate(target_cols)})
                    .reset_index())

        # Pandas hierarchical indexing messes up the header...
        model_df.columns = ['_'.join(col).strip() if col[1] != '' else col[0] for col in model_df.columns]
        model_df = model_df.rename(columns={'_'.join([target_cols[0], MEAN]): target_cols[0],
                                            '_'.join([target_cols[0], COUNT]): COUNT})
        if len(target_cols) > 1:
            model_df = model_df.rename(columns={'_'.join([c, MEAN]): c for c in target_cols[1:]})

        # The resulting model is stored into a str/ndarray dictionary for later calculations
        model = {}
        for c in model_df.columns:
            model[c] = model_df[c].values

        # Now coalitions are computed
        coalitions = {}
        coalitions_weights = {}
        cols_names = self.df_train.columns
        n_cols = len(cols_names)

        # To compute coalitions, only features are taken into account
        for c in [tmp_c for tmp_c in self.df_train.columns if tmp_c not in target_cols]:

            # In order to compute every possible coalition, for each feature, only the remaining features are taken
            # into account
            coalitions[c] = TefShap.__get_coalitions(columns=[feature for feature in cols_names if feature not in [c] +
                                                              target_cols])
            # Weights for the calculated coalitions are computed
            coalitions_weights[c] = [1 / (scipy.special.comb(n_cols - 1 - len(target_cols), len(coalition)) * (
                    n_cols - len(target_cols))) for coalition in coalitions[c]]

        print('Training time: {}'.format(time.time() - start))

        return {
            self._MODEL: model,
            self._COALITIONS: coalitions,
            self._COALITIONS_WEIGHTS: coalitions_weights,
            self._RES_DICT: {}
        }

    def calculate_importance_values(self, df_aggregated: pd.DataFrame, **params) -> Dict[str, np.ndarray]:
        """
        This function takes care of calculating the Shapley values. Note that it will do it locally. This means that
        for every row in the aggregated DataFrame, it will calculate the Shapley Values for each of its features.
        There will be as many values as targets per feature

        :params: df_aggregated: Pandas DataFrame for which Shapley Values will be locally computed
        :params: target_cols:   List of strings with all column names identified as target
        :params: res_dict:      Dictionary with the following structure and keys:
                                - phi0: Dictionary containing the empty coalition as key and the baseline as value
                                - shapley_value:
        :return:
        """

        if self.target_cols is None:
            target_cols = ImportanceCalculator._DEFAULT_TARGET_COLS
        else:
            target_cols = self.target_cols
        res_dict = params[self._RES_DICT]

        start = time.time()

        shap_values_list = []
        n_rows = df_aggregated.shape[0]
        feature_columns = [col for col in df_aggregated.columns if col not in target_cols]

        # For each of the aggregated DataFrame rows
        pbar = tqdm(range(n_rows))
        for i in pbar:
            if (i > 0) and (i % 100 == 0):
                pbar.set_description('Progress: row {}'.format(i))

            # For each row, Shapley values are computed for the i-th row
            x = df_aggregated.iloc[i]

            # Shapley for each of the features for the i-th row are computed
            shap_values = []
            for col in feature_columns:

                # Shapley value for i-th row and col feature
                shap_value = np.sum(
                    np.array([TefShap.__coalition_contribution(x=x, col=col, coalition=coalition, weight=weight,
                                                               model=params[self._MODEL], res_dict=res_dict,
                                                               target_cols=target_cols)
                              for coalition, weight in zip(params[self._COALITIONS][col],
                                                           params[self._COALITIONS_WEIGHTS][col])]), axis=0)

                # Shapley values for each row
                shap_values.append(shap_value)

            # Shapley values for all the rows
            shap_values_list.append(shap_values)

        print('Computation time: {}'.format(time.time() - start))

        shapley_values = np.array(shap_values_list)

        # TODO: Con un dataset con sus targets desbalanceados, la frecuencia de dichos targets puede influir en las
        #  explicaciones y el baseline obtenido para cada uno de ellos ¿podría haber que hacer la media
        #  de los Shapley Values para los targets?

        # Data is formatted for the sanity check
        y_hat_reduced = res_dict[str({})] + np.sum(shapley_values, axis=1)
        y = df_aggregated[target_cols].values
        ImportanceCalculator.sanity_check(ground_truth=y, prediction=y_hat_reduced, target_cols=target_cols,
                                          scope='aggregated')

        return {
            TefShap._PHI0: res_dict[str({})],
            TefShap._IMPORTANCE_VALUES: shapley_values,
        }

    @staticmethod
    def __get_coalitions(columns: List[str]) -> List[List[str]]:
        """
        This function computes the list of all possible coalitions (combinations) for the given list of columns

        :param: columns: List of columns for which all possible coalitions will be generated
        :return:         List of coalitions so that each coalition is itself a list
        """
        coalitions_list = []
        for n_features in range(len(columns) + 1):
            for coalition in combinations(columns, n_features):
                coalitions_list.append(list(coalition))
        return coalitions_list

    @staticmethod
    def __get_worth(coalition_features: Dict, model: Dict, target_cols: List[str]) -> np.ndarray:
        """
        This function takes care of computing the coalition worth (\nu(S))

        :param: coalition_features: Dictionary with the coalition features for which "worth" will be estimated. For each
                                    element, the key represents the column name and the value...the corresponding value
        :param: model:              Dictionary representing model to use for the coalition "worth" estimation. For each
                                    element, the key is the feature name and the value, the corresponding numpy array
                                    of values for that feature
        :param: targets_col:        List of strings containing the names of the target columns, by default ['target']

        :return:                    Numpy array containing the "worth" of the current coalition for each target
        """

        cond = np.ones_like(list(model.values())[0], dtype=np.bool8)
        for k, v in coalition_features.items():
            if isinstance(v, str):
                cond = (cond & (model[k] == v))
            else:
                cond = (cond & (np.abs(model[k] - v) < 10 ** -6))

        # TODO si cond es False no se puede calcular el promedio del target, habría que tomar la probabilidad a priori
        #  del target (probabilidad del target sobre el dataset). ¿Sería mejor hacer un blend que tenga en cuenta el
        #  a priori y el a posterori? Esto cubriría todas las casuísticas
        counts = model[COUNT][cond]
        np.seterr('raise')
        return np.array([np.sum(counts * model[target_col][cond]) / np.sum(counts) for target_col in target_cols])

    @staticmethod
    def __coalition_worth(x: pd.Series, coalition: List[str], model: Dict, res_dict: Dict,
                          target_cols: List[str]) -> np.ndarray:
        """
        This function takes care of invoking the computation of the coalition worth and keeping the results into a
        dictionary so some computations can be retrieved from that dictionary

        :param x:               Pandas Series containing the features to be used to specialize the coalition template
        :param: coalition:      List of strings containing the features coalition for which the "worth" is being
                                computed
        :param model:           Dictionary representing model to use for the coalition "worth" estimation. For each
                                element, the key is the feature name and the value, the corresponding numpy array
                                of values for that feature
        :param res_dict:        Dictionary containing the coalitions worth already computed. For each element, the key
                                is a string representing the coalition and the value, a float representing the worth
        :param: targets_col:    List of strings containing the names of the target columns, by default ['target']

        :return:                Numpy array containing the "worth" of the current coalition for each target
        """
        # TODO Reducir tamaño clave (hashear de la manera más ligera posible)
        coalition_features: Dict = {c: x[c] if isinstance(x[c], str) else float(x[c]) for c in sorted(coalition)}
        str_cf: str = str(coalition_features)
        if res_dict.get(str_cf, None) is not None:
            return res_dict[str_cf]

        to_ret = TefShap.__get_worth(coalition_features=coalition_features, model=model, target_cols=target_cols)
        # TODO Solucionar mutabilidad diccionario res_dict = res_dict.copy()
        res_dict.update({str_cf: to_ret})

        return to_ret

    @staticmethod
    def __coalition_contribution(x: pd.Series, col: str, coalition: List[str], weight: float, model: Dict,
                                 res_dict: Dict, target_cols: List[str]) -> np.ndarray:
        """
        This functions computes the contribution of the current coalition to the Shapley value of the col column

        :param: x            Pandas Series representing the row for which Shapley values are being computed
        :param: coalition:   List of strings containing the features coalition for which the contribution is being
                             computed
        :param: weight:      Float representing the coalition contribution weight (combinatorial weight)
        :param: model:       Dictionary of numpy arrays containing the model to use for the coalition worth estimation.
                             In this dictionary, key represents the column name and value, a numpy array of values
        :param: res_dict:    Dictionary containing the coalitions worth already computed. Here, key is a string which
                             univocally represents a coalition and value a float representing the coalition worth
        :param: target_cols: String representing the name of the target column

        :return:             Numpy arrau representing the contribution to the Shapley Value of the current coalition
        """
        return weight * (TefShap.__coalition_worth(x=x, coalition=coalition + [col], model=model, res_dict=res_dict,
                                                   target_cols=target_cols) -
                         TefShap.__coalition_worth(x=x, coalition=coalition, model=model, res_dict=res_dict,
                                                   target_cols=target_cols))
