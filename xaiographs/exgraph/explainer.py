from typing import List, Tuple

import numpy as np
import pandas as pd

from xaiographs.common.constants import FEATURE_VALUE, ID, IMPORTANCE, RANK, TARGET, RELIABILITY
from xaiographs.common.utils import FeaturesInfo, TargetInfo, get_features_info, get_target_info, sample_by_target, \
    xgprint
from xaiographs.exgraph.exporter import Exporter
from xaiographs.exgraph.feature_selector import FeatureSelector
from xaiographs.exgraph.importance.importance_calculator import ImportanceCalculator
from xaiographs.exgraph.importance.importance_calculator_factory import ImportanceCalculatorFactory
from xaiographs.exgraph.stats_calculator import StatsCalculator

# Warning message
WARN_MSG = 'WARNING: {} is empty, because nothing has been processed. Execute explain() function to get results.'


class Explainer(object):
    """
    This class is intended to provide an abstract layer which encapsulates everything related to the explanation process
    from statistics calculation, importance calculation (using the engine chosen by the user) and information export for
    visualization tasks
    """

    def __init__(self, dataset: pd.DataFrame, importance_engine: str, destination_path: str = './xaioweb_files',
                 number_of_features: int = 8, verbose: int = 0):
        """
        Constructor method for Explainer.
        - Property `__top_features` provides a list with the all the original features ranked
        - Property `__top_features_by_target` provides distance and rank information for each feature and target value,
         so that results can be understood

        :param dataset:                  Pandas DataFrame, containing the whole dataset
        :param importance_engine:        String, representing the name of the method use to compute feature importance
        :param destination_path:         String, representing the path where output files will be stored
        :param number_of_features:       Integer, representing the number of features to be selected
        :param verbose:                  Verbosity level, where any value greater than 0 means the message is printed

        """
        self.__global_explainability = None
        self.__global_frequency_feature_value = None
        self.__global_target_feature_value_explainability = None
        self.__global_target_explainability = None
        self.__local_dataset_reliability = None
        self.__local_feature_value_explainability = None
        self.__top_features = None
        self.__top_features_by_target = None
        self.__df = dataset
        self.__destination_path = destination_path
        self.__engine = importance_engine
        self.__number_of_features = number_of_features
        self.__verbose = verbose

    @property
    def global_explainability(self):
        """
        Property that returns all the features to be explained, ranked by their global importance. Prior to this,
        the mean of each feature importance for each target is computed. Then the targets probabilities are computed
        and each of the importance values previously obtained, are multiplied by their corresponding probability for
        each target. Finally, the resulting values for each feature (one value per target) are averaged, so a single
        number representing each feature importance is obtained.
        If the method `explain()` from the `Explainer` class has not been executed, it will return a warning message.


        :return: pd.DataFrame, containing each feature ranked by its global importance
        """
        if self.__global_explainability is None:
            print(WARN_MSG.format('\"global_explainability\"'))
        else:
            return self.__global_explainability

    @property
    def global_frequency_feature_value(self):
        """
        Property that returns the number of occurrences for each feature-value pair. This is computed by adding up each
         feature-value pair occurrence.
        If the method `explain()` from the `Explainer` class has not been executed, it will return a warning message.

        :return: pd.DataFrame, containing the number of times each feature-value occurs
        """
        if self.__global_frequency_feature_value is None:
            print(WARN_MSG.format('\"global_frequency_feature_value\"'))
        else:
            return self.__global_frequency_feature_value

    @property
    def global_target_explainability(self):
        """
        Property that returns all the features to be explained, ranked by their global importance by target value. This
        is achieved by computing the mean of each feature importance for each of the top1 targets.
        If the method `explain()` from the `Explainer` class has not been executed, it will return a warning message.


        :return: pd.DataFrame, containing each feature ranked by its global importance by target value
        """
        if self.__global_target_explainability is None:
            print(WARN_MSG.format('\"global_target_explainability\"'))
        else:
            return self.__global_target_explainability

    @property
    def global_target_feature_value_explainability(self):
        """
        Property that, for each target value, returns all the pairs feature-value ranked by their global importance.
        This is achieved by computing the mean of the importance/s of each feature-value pair for all those samples
        whose top1 target matches the target value being processed. Again, it's important to remark that this is done
        for each possible target value.
        If the method `explain()` from the `Explainer` class has not been executed, it will return a warning message.

        :return: pd.DataFrame, containing for each target value all the feature-value pairs occurring in all those
                 samples whose top1 target is equal to the target value being processed. Feature-value pair importance
                 is computed by averaging the importance of all the occurrences of that feature-value pair linked to
                 the target value being processed
        """
        if self.__global_target_feature_value_explainability is None:
            print(WARN_MSG.format('\"global_target_feature_value_explainability\"'))
        else:
            return self.__global_target_feature_value_explainability

    @property
    def local_dataset_reliability(self):
        """
        Property that, for each sample, returns its top1 target and the reliability value associated to that target
        If the method `explain()` from the `Explainer` class has not been executed, it will return a warning message.

        :return: pd.DataFrame, containing for each sample all its feature-value pairs together with their importance
        """
        if self.__local_dataset_reliability is None:
            print(WARN_MSG.format('\"global_target_feature_value_explainability\"'))
        else:
            df_local_dataset_reliability = pd.DataFrame(self.__local_dataset_reliability, columns=[ID, TARGET,
                                                                                                   RELIABILITY])
            df_local_dataset_reliability[ID] = pd.to_numeric(df_local_dataset_reliability[ID], downcast="unsigned")
            df_local_dataset_reliability[RELIABILITY] = pd.to_numeric(df_local_dataset_reliability[RELIABILITY],
                                                                      downcast="float")
            return df_local_dataset_reliability

    @property
    def local_feature_value_explainability(self):
        """
        Property that, for each sample, returns as many rows as feature-value pairs, together with their calculated
        importance. In order to achieve this, the column name where the right importance value will be found must be
        compounded. This is done by joining together the top1 target for that sample, the feature-value pair and the
        suffix '_imp'
        If the method `explain()` from the `Explainer` class has not been executed, it will return a warning message.

        :return: pd.DataFrame, containing for each sample all its feature-value pairs together with their importance
        """

        if self.__local_feature_value_explainability is None:
            print(WARN_MSG.format('\"local_feature_value_explainability\"'))
        else:
            df_local_feature_value_explainability = pd.DataFrame(self.__local_feature_value_explainability,
                                                                 columns=[ID, FEATURE_VALUE, IMPORTANCE])
            df_local_feature_value_explainability[ID] = pd.to_numeric(df_local_feature_value_explainability[ID],
                                                                      downcast="unsigned")
            df_local_feature_value_explainability[IMPORTANCE] = pd.to_numeric(
                df_local_feature_value_explainability[IMPORTANCE], downcast="float")
            df_local_feature_value_explainability[RANK] = pd.to_numeric(
                df_local_feature_value_explainability.groupby(ID)[IMPORTANCE].rank(ascending=False).astype('int'),
                downcast="unsigned")
            return df_local_feature_value_explainability

    @property
    def top_features(self):
        """
        Property that returns all the features ranked by the `FeatureSelector`. Ranking is calculated as follows:

         - For each target value and for all the features, two histograms are calculated per feature. The first one
         considering the input pandas DataFrame filtered by the target value and the second one considering the opposite
        (DataFrame filtered by the absence of target value)
         - Modified Jensen Shannon distance (see below for details) is calculated between the resulting two
         distributions
         - Once all distances have been computed for all the features for a given target value, they're ranked, so that
         the larger the distance, the higher the rank
         - Finally, for each feature, its ranks for all of the targets are taken into account so that the feature with
         the largest aggregated rank will rank the first in the top K features (note that when talking about ranks,
         1 is greater than 2)
         If the method `explain()` from the `Explainer` class has not been executed, it will return a warning message.

        Modified Jensen Shannon distance calculation:
         - The formula can be found
        `here <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html>`_
         - However the used formula is a modified version which returns a four element numpy array:
             + First element replaces the square root by the square root of the median
             + Second element replaces the square root by the square root of the mean
             + Third element replaces the square root by the square root of the max
             + Fourth element replaces the square root by the square root of the sum
         - An numpy array as explained above will be returned per feature and all of them stacked up becoming a
        `number_of_features x 4` matrix
         - Each element of the matrix is normalized by dividing it by the sum of the elements of its corresponding
         column
         - For each feature (each matrix row), its normalized statistics are added, as a result the matrix becomes a
         vector containing one element per feature
         - Finally each element is normalized by dividing it by the sum of all the elements. These are the distances
         taken into account to compute the rank so that the higher the distance the more discriminative the feature
         is considered, thus, the more interesting from the predictive point of view. The feature with the highest
         distance will be ranked first while the feature with the smallest distance will be ranked last
         - A vector like the one described in the step above will be obtained for each target value, this means that
         a ranking will be obtained for each target value
         - In order to obtain a final ranking, partial ranks per target value are added for each feature, so that,
         the higher the rank sum for each feature, the less relevant it will be considered

        :return: pd.DataFrame, with all the features ranked by the `FeatureSelector`
        """
        if self.__top_features is None:
            print(WARN_MSG.format('\"top_features\"'))
        else:
            return self.__top_features

    @property
    def top_features_by_target(self):
        """
        Property that returns all the features ranked by the "FeatureSelector". Ranking is calculated as follows:

         - For each target value and for all the features, two histograms are calculated per feature. The first one
         considering the input pandas DataFrame filtered by the target value and the second one considering the opposite
        (DataFrame filtered by the absence of target value)
         - Modified Jensen Shannon distance (see below for details) is calculated between the resulting two
         distributions
         - Once all distances have been computed for all the features for a given target value, they're ranked, so that
         the larger the distance, the higher the rank
         - Finally, for each feature, its ranks for all of the targets are taken into account so that the feature with
         the largest aggregated rank will rank the first in the top K features (note that when talking about ranks,
         1 is greater than 2)
         If the method "explain()" from the "Explainer" class has not been executed, it will return a warning message.

        Modified Jensen Shannon distance calculation:
         - The formula can be found
        `here <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html>`_
         - However the used formula is a modified version which returns a four element numpy array:
             + First element replaces the square root by the square root of the median
             + Second element replaces the square root by the square root of the mean
             + Third element replaces the square root by the square root of the max
             + Fourth element replaces the square root by the square root of the sum
         - An numpy array as explained above will be returned per feature and all of them stacked up becoming a
        `number_of_features x 4` matrix
         - Each element of the matrix is normalized by dividing it by the sum of the elements of its corresponding
         column
         - For each feature (each matrix row), its normalized statistics are added, as a result the matrix becomes a
         vector containing one element per feature
         - Finally each element is normalized by dividing it by the sum of all the elements. These are the distances
         taken into account to compute the rank so that the higher the distance the more discriminative the feature
         is considered, thus, the more interesting from the predictive point of view. The feature with the highest
         distance will be ranked first while the feature with the smallest distance will be ranked last
         - A vector like the one described in the step above will be obtained for each target value, this means that
         a ranking will be obtained for each target value


        :return: pd.DataFrame, providing for each feature its rank per target calculated by the "FeatureSelector".
                 Furthermore, the distance for each feature and target value, is provided along with its rank
        """
        if self.__top_features_by_target is None:
            print(WARN_MSG.format('\"top_features_by_target\"'))
        else:
            return self.__top_features_by_target

    def __get_common_info(self, feature_cols: List[str], target_cols: List[str]) -> Tuple[FeaturesInfo, TargetInfo]:
        """
        This function orchestrates the generation of both, features columns information and target information

        :param feature_cols: List of strings, containing the column names for the features
        :param target_cols:  List of strings, containing the possible targets
        :return:             NamedTuple, containing all the feature column names lists which will be used all through
                             the execution flow and another NamedTuple containing target related info
        """

        features_info = get_features_info(df=self.__df, feature_cols=feature_cols, target_cols=target_cols)
        target_info = get_target_info(df=self.__df, target_cols=target_cols)

        return features_info, target_info

    def explain(self, feature_cols: List[str], target_cols: List[str], num_samples_local_expl: int = 100,
                num_samples_global_expl: int = 50000, batch_size_expl: int = 5000, train_stratify: bool = True):
        if num_samples_global_expl < num_samples_local_expl:
            print('ERROR: num_samples_global_expl ({}) < num_samples_local_exp ({}): Number of samples for global '
                  'explainability must be larger than the number of samples for local explainability'
                  .format(num_samples_global_expl, num_samples_local_expl))

        # This section is intended to retrieve information which will be used throughout the execution flow:
        #   Feature related information: different features columns names lists
        #   Target related information: top1_targets (ground truths) for each row, target_probs (probability for each
        #   target), top1_argmax (the indexes version of the top1_targets) and target columns names
        features_info, target_info = self.__get_common_info(feature_cols=feature_cols, target_cols=target_cols)

        # Feature selector is instantiated
        selector = FeatureSelector(df=self.__df, feature_cols=features_info.feature_columns, target_info=target_info,
                                   number_of_features=self.__number_of_features, verbose=self.__verbose)

        # Then it's used to select the top K features
        topk_features = selector.select_topk()
        self.__top_features = selector.top_features
        self.__top_features_by_target = selector.top_features_by_target

        # Dataset must be rebuilt by selecting the topk features, the ID and the target columns
        self.__df = self.__df[[ID] + topk_features + target_cols]

        # Since feature columns have changed, information related to features must be generated again
        features_info = get_features_info(df=self.__df, feature_cols=topk_features, target_cols=target_cols)

        # Computations have been split in two types: statistics calculation and importance calculation
        #   An ImportanceCalculator object is used to compute importance values
        imp_calc_factory = ImportanceCalculatorFactory()
        importance_calculator = imp_calc_factory.build_importance_calculator(name=self.__engine,
                                                                             explainer_params={},
                                                                             feature_cols=features_info.feature_columns,
                                                                             target_info=target_info,
                                                                             train_stratify=train_stratify,
                                                                             verbose=self.__verbose)
        top1_importance_features, global_explainability, global_nodes_importance, df_explanation_global = (
            importance_calculator.calculate_importance(df=self.__df, features_info=features_info,
                                                       num_samples=num_samples_global_expl, batch_size=batch_size_expl))

        # Here, the row IDs to be sampled for local explanation are generated. A sample ids mask will be used for id
        # filtering, (the list of sample ids is retrieved too to perform consistency checks)
        target_info = get_target_info(df=df_explanation_global, target_cols=target_cols)
        sample_ids_mask, sample_ids = sample_by_target(ids=df_explanation_global[ID].values,
                                                       top1_targets=target_info.top1_targets,
                                                       num_samples=num_samples_local_expl,
                                                       target_probs=target_info.target_probs,
                                                       target_cols=target_info.target_columns)

        # local_dataset_reliability property is computed
        self.__local_dataset_reliability = np.concatenate((df_explanation_global[ID].values.reshape(-1, 1),
                                                           target_info.top1_targets.reshape(-1, 1),
                                                           np.abs(1 - np.round(df_explanation_global[
                                                               features_info.reliability_columns].values[
                                                               np.arange(len(df_explanation_global)),
                                                               target_info.top1_argmax].reshape(-1, 1), decimals=2))),
                                                          axis=1)

        # Once global explanation related information is calculated. The explanation DataFrame is sampled, so that only
        # some rows will be taken into account when generating the local output for visualization
        xgprint(self.__verbose, 'INFO:     Sampling the dataset to be locally explained: {} samples will be used ...'.
                format(num_samples_local_expl))
        df_explanation_sample = ImportanceCalculator.sample_explanation(df_explanation=df_explanation_global,
                                                                        sample_ids_mask_2_explain=sample_ids_mask)

        # StatsCalculator takes care of everything related to frequency calculation, counting...
        stats = StatsCalculator(df=df_explanation_global[[ID] + features_info.feature_columns + target_cols],
                                top1_targets=target_info.top1_targets,
                                feature_cols=features_info.feature_columns,
                                float_feature_cols=features_info.float_feature_columns,
                                target_cols=target_info.target_columns,
                                sample_ids_mask=sample_ids_mask, sample_ids=sample_ids, verbose=self.__verbose)
        edges_stats, nodes_stats, target_distribution, importance_col_stats = stats.calculate_stats()

        # local_feature_value_explainability property is computed
        feature_value_expl = np.array([df_explanation_global[id_imp_row[2]].to_numpy()[
                                           df_explanation_global[ID].to_numpy() == int(id_imp_row[0])].item() for
                                       id_imp_row in importance_col_stats])
        self.__local_feature_value_explainability = np.concatenate((np.delete(importance_col_stats, 2, axis=1),
                                                                    feature_value_expl.reshape(-1, 1)), axis=1)

        # Exporter takes care of the following tasks:
        #   Mixing calculated statistics and calculated importance when needed
        #   Calculating weights in pixels
        #   Persisting results
        # TODO: Al igual que un hipotético fichero con IDs, o un número de samples...habría que meter como parámetro
        #  el path donde se quieren guardar los ficheros
        exporter = Exporter(df_explanation_sample=df_explanation_sample, destination_path=self.__destination_path,
                            verbose=self.__verbose)
        exporter.export(features_info=features_info, target_info=target_info, sample_ids_mask=sample_ids_mask,
                        global_target_explainability=top1_importance_features,
                        global_explainability=global_explainability, global_nodes_importance=global_nodes_importance,
                        edges_info=edges_stats, nodes_info=nodes_stats, target_distribution=target_distribution)

        # Properties from Exporter module are retrieved
        self.__global_explainability = exporter.global_explainability
        self.__global_frequency_feature_value = exporter.global_frequency_feature_value
        self.__global_target_feature_value_explainability = exporter.global_target_feature_value_explainability
        self.__global_target_explainability = exporter.global_target_explainability
