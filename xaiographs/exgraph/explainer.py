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
WARN_MSG = 'WARNING: {} is empty, because nothing has been processed. Execute fit() function to get results.'


class Explainer(object):
    """
    The Explainer class provides an abstract layer which encapsulates everything related to the explanation process
    from statistics calculation, importance calculation (using the engine chosen by the user) and information export for
    visualization tasks.

    Read more in the :ref:`Explainability <user_guide/explainability>` User Guide

    Parameters
    ----------
    importance_engine : str
        The name of the method use to compute feature importance.

        .. important::
           LIDE is the available option for version 0.0.2

    destination_path : str, default='./xaioweb_files'
        The path where output XAIoWeb files will be stored.

    number_of_features : int
        The number of top relevant features to be selected for importance calculation.

    verbose : int, default=0
        Verbosity level.

        .. hint::
           Any value greater than 0 means verbosity is on.

    """

    def __init__(self, importance_engine: str, destination_path: str = './xaioweb_files',
                 number_of_features: int = 8, verbose: int = 0):
        self.__global_explainability = None
        self.__global_frequency_feature_value = None
        self.__global_target_feature_value_explainability = None
        self.__global_target_explainability = None
        self.__importance_values = None
        self.__local_reliability = None
        self.__local_feature_value_explainability = None
        self.__sample_ids_to_display = list()
        self.__top_features = None
        self.__top_features_by_target = None
        self.__destination_path = destination_path
        self.__engine = importance_engine
        self.__number_of_features = number_of_features
        self.__verbose = verbose

    @property
    def global_explainability(self):
        """Property containing each feature ranked by its global importance. This property is computed in two steps:

        - The mean of each feature importance for each target is computed.
        - The mean of each feature importance is now computed throughout all the targets.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        global_explainability : pandas.DataFrame
            Structure containing each feature ranked by its global importance. It contains the following columns:

            +---------------+----------------------------------------------------------------------------------------------------+
            |Column         |Description                                                                                         |
            +===============+====================================================================================================+
            |**feature**    |feature name.                                                                                       |
            +---------------+----------------------------------------------------------------------------------------------------+
            |**importance** |feature importance considering all possible target values and all the samples.                      |
            +---------------+----------------------------------------------------------------------------------------------------+
            |**rank**       |position of the feature when sorted by its importance. The lower the rank the higher the importance.|
            +---------------+----------------------------------------------------------------------------------------------------+

        """
        if self.__global_explainability is None:
            print(WARN_MSG.format('\"global_explainability\"'))
        else:
            return self.__global_explainability

    @property
    def global_frequency_feature_value(self):
        """Property that returns the number of occurrences for each feature-value pair. This is computed by adding up
        each feature-value pair occurrence.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        global_frequency_feature_value : pandas.DataFrame
            Structure containing the number of times each feature-value occurs. It contains the following columns:

            +------------------+---------------------------------------------------------------+
            |Column            |Description                                                    |
            +==================+===============================================================+
            |**feature_value** |feature name together with each of its possible values.        |
            +------------------+---------------------------------------------------------------+
            |**frequency**     |total number of occurrences for each feature name-value pairs. |
            +------------------+---------------------------------------------------------------+


        """
        if self.__global_frequency_feature_value is None:
            print(WARN_MSG.format('\"global_frequency_feature_value\"'))
        else:
            return self.__global_frequency_feature_value

    @property
    def global_target_explainability(self):
        """Property that returns all the features to be explained, ranked by their global importance by target value. \
        This is achieved by computing the mean of each feature importance for each target value.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        global_target_explainability : pandas.DataFrame
            Structure containing all the features to be explained, ranked by their global importance by target value. \
            It contains the following columns:

            +---------------+----------------------------------------------------------------------------------------------------+
            |Column         |Description                                                                                         |
            +===============+====================================================================================================+
            |**target**     |each of the possible target values.                                                                 |
            +---------------+----------------------------------------------------------------------------------------------------+
            |**feature**    |feature name.                                                                                       |
            +---------------+----------------------------------------------------------------------------------------------------+
            |**importance** |feature importance with respect to each possible target values.                                     |
            +---------------+----------------------------------------------------------------------------------------------------+
            |**rank**       |position of the feature when sorted by its importance. The lower the rank the higher the importance.|
            +---------------+----------------------------------------------------------------------------------------------------+


        """
        if self.__global_target_explainability is None:
            print(WARN_MSG.format('\"global_target_explainability\"'))
        else:
            return self.__global_target_explainability

    @property
    def global_target_feature_value_explainability(self):
        """Property that, for each target value, returns all the pairs feature-value ranked by their global \
         importance. This is achieved by computing the mean of the importance/s of each feature-value pair linked to \
         the target value being processed.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        global_target_feature_value_explainability : pandas.DataFrame
            Structure containing for each target value all the pairs feature-value ranked by their global importance. \
            It contains the following columns:

            +------------------+--------------------------------------------------------------------------------------------------------------------------+
            |Column            |Description                                                                                                               |
            +==================+==========================================================================================================================+
            |**target**        |each of the possible target values.                                                                                       |
            +------------------+--------------------------------------------------------------------------------------------------------------------------+
            |**feature_value** |feature name together with each of its possible values.                                                                   |
            +------------------+--------------------------------------------------------------------------------------------------------------------------+
            |**importance**    |feature importance with respect to each possible target values.                                                           |
            +------------------+--------------------------------------------------------------------------------------------------------------------------+
            |**rank**          |position of the feature for each target value when sorted by its importance. The lower the rank the higher the importance.|
            +------------------+--------------------------------------------------------------------------------------------------------------------------+

        """
        if self.__global_target_feature_value_explainability is None:
            print(WARN_MSG.format('\"global_target_feature_value_explainability\"'))
        else:
            return self.__global_target_feature_value_explainability

    @property
    def importance_values(self):
        """Property returns the computed importance values.

        .. caution::
           If the method :meth:`local_explain` from an :class:`ImportanceCalculator` child class has not been \
           executed, it will return a warning message.

        Returns
        -------
        importance_values : numpy.array, shape (n_samples, n_features, n_target_values)
            Structure containing for each sample, feature and target value, the computed importance values


        """
        if self.__importance_values is None:
            print(WARN_MSG.format('\"importance_values\"'))
        else:
            return self.__importance_values

    @property
    def local_reliability(self):
        """Property that, for each sample, returns its top1 target and the reliability value associated to that target.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        local_dataset_reliability :  pandas.DataFrame
            Structure containing for each sample its top1 target and the reliability value associated to that target. \
            It contains the following columns:

            +---------------+------------------------------------+
            |Column         |Description                         |
            +===============+====================================+
            |**id**         |identifier for each sample.         |
            +---------------+------------------------------------+
            |**target**     |each of the possible target values. |
            +---------------+------------------------------------+
            |**reliability**|associated reliability value.       |
            +---------------+------------------------------------+

        """
        if self.__local_reliability is None:
            print(WARN_MSG.format('\"global_target_feature_value_explainability\"'))
        else:
            df_local_dataset_reliability = pd.DataFrame(self.__local_reliability, columns=[ID, TARGET, RELIABILITY])
            df_local_dataset_reliability[ID] = pd.to_numeric(df_local_dataset_reliability[ID], downcast="unsigned")
            df_local_dataset_reliability[RELIABILITY] = pd.to_numeric(df_local_dataset_reliability[RELIABILITY],
                                                                      downcast="float")
            return df_local_dataset_reliability

    @property
    def local_feature_value_explainability(self):
        """Property that, for each sample, returns as many rows as feature-value pairs, together with their calculated
        importance.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        local_feature_value_explainability : pandas.DataFrame
            Structure containing for each sample all its feature-value pairs together with their importance. It \
            contains the following columns:

            +------------------+-------------------------------------------------------------------------------------------------------------------------------+
            |Column            |Description                                                                                                                    |
            +==================+===============================================================================================================================+
            |**id**            |identifier for each sample.                                                                                                    |
            +------------------+-------------------------------------------------------------------------------------------------------------------------------+
            |**feature_value** |feature name together with each of its possible values.                                                                        |
            +------------------+-------------------------------------------------------------------------------------------------------------------------------+
            |**importance**    |feature importance for each feature_value pair and the top1 target.                                                            |
            +------------------+-------------------------------------------------------------------------------------------------------------------------------+
            |**rank**          |position of the feature_value pair for each sample when sorted by its importance. The lower the rank the higher the importance.|
            +------------------+-------------------------------------------------------------------------------------------------------------------------------+


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
    def sample_ids_to_display(self):
        """Property retrieves the sample ids which will be used to build the interactive visualization.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        local_feature_value_explainability : pandas.Series
            Structure containing the ids for the chosen samples.


        """
        if self.__sample_ids_to_display is None:
            print(WARN_MSG.format('\"sample_ids_to_display\"'))
        else:
            return pd.to_numeric(pd.Series(self.__sample_ids_to_display, name=ID), downcast="unsigned")

    @property
    def top_features(self):
        """Property returns all the features ranked by the ``FeatureSelector``. Ranking is calculated as follows:

        - For each target value and for all the features, two histograms are calculated per feature. The first one \
        considering the input pandas DataFrame filtered by the target value and the second one considering the \
        opposite (DataFrame filtered by the absence of target value).
        - Modified Jensen Shannon distance (see below for details) is calculated between the resulting two \
        distributions.
        - Once all distances have been computed for all the features for a given target value, they're ranked, so \
        that the larger the distance, the higher the rank.
        - Finally, for each feature, its ranks for all of the targets are taken into account so that the feature with \
        the largest aggregated rank will rank the first in the top K features (note that when talking about ranks, \
        1 is greater than 2).

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Modified Jensen Shannon distance calculation:

        - The formula can be found
          `here <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html>`_.
        - However the used formula is a modified version which returns a four element numpy array:
             - First element replaces the square root by the square root of the median.
             - Second element replaces the square root by the square root of the mean.
             - Third element replaces the square root by the square root of the max.
             - Fourth element replaces the square root by the square root of the sum.
        - An numpy array as explained above will be returned per feature and all of them stacked up becoming a \
        matrix of shape (number_of_features, 4).
        - Each element of the matrix is normalized by dividing it by the sum of the elements of its corresponding \
        column.
        - For each feature (each matrix row), its normalized statistics are added, as a result the matrix becomes a \
        vector containing one element per feature.
        - Finally each element is normalized by dividing it by the sum of all the elements. These are the distances \
        taken into account to compute the rank so that the higher the distance the more discriminative the feature \
        is considered, thus, the more interesting from the predictive point of view. The feature with the highest \
        distance will be ranked first while the feature with the smallest distance will be ranked last.
        - A vector like the one described in the step above will be obtained for each target value, this means that \
        a ranking will be obtained for each target value.
        - In order to obtain a final ranking, partial ranks per target value are added for each feature, so that, \
        the higher the rank sum for each feature, the less relevant it will be considered.

        Returns
        -------
        top_features : pd.DataFrame
            Structure containing with all the features ranked by the ``FeatureSelector``.


        """
        if self.__top_features is None:
            print(WARN_MSG.format('\"top_features\"'))
        else:
            return self.__top_features

    @property
    def top_features_by_target(self):
        """Property returns all the features ranked by the ``FeatureSelector``.

        .. seealso::
           For further information about how the selection process works, please refer to :attr:`top_features` from \
           the :class:`Explainer` class.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        top_features : pd.DataFrame
            Structure providing for each feature its rank per target calculated by the ``FeatureSelector``. \
            Furthermore, the distance for each feature and target value, is provided along with its rank.


        """
        if self.__top_features_by_target is None:
            print(WARN_MSG.format('\"top_features_by_target\"'))
        else:
            return self.__top_features_by_target

    @staticmethod
    def __get_common_info(df: pd.DataFrame, feature_cols: List[str], target_cols: List[str]) -> Tuple[FeaturesInfo,
                                                                                                      TargetInfo]:
        """
        This function orchestrates the generation of both, features columns information and target information

        :param df:           Pandas DataFrame, containing the dataset for which the required information will be
                             retrieved
        :param feature_cols: List of strings, containing the column names for the features
        :param target_cols:  List of strings, containing the possible targets
        :return:             NamedTuple, containing all the feature column names lists which will be used all through
                             the execution flow and another NamedTuple containing target related info
        """

        features_info = get_features_info(df=df, feature_cols=feature_cols, target_cols=target_cols)
        target_info = get_target_info(df=df, target_cols=target_cols)

        return features_info, target_info

    def fit(self, df: pd.DataFrame, feature_cols: List[str], target_cols: List[str], num_samples_local_expl: int = 100,
            num_samples_global_expl: int = 50000, batch_size_expl: int = 5000, train_stratify: bool = True):
        """It coordinates all the steps of the explanation process which consists of the following parts:

        - Feature selection, takes care of determining which are top K most relevant features. K is defined by the \
        parameter ``number_of_features`` in the constructor of the :class:`Explainer` class.
        - Importance calculation, takes care of computing importance for the remaining features from the previous step \
        and the possible target values.
        - Stats calculation, takes care of computing different counts and ratios which are particularly important to \
        feed those files used for visualization purposes.
        - Exporter, generates all those files related to the Explanation process which will be used for visualization \
        purposes.

        Parameters
        ----------
        df : pandas.DataFrame
            Structure containing the whole dataset.

        feature_cols : List[str]
            List containing the names of those columns representing features within the dataset DataFrame.

        target_cols : List[str]
            List containing the names of those columns representing the target values within the dataset DataFrame.

        num_samples_local_expl : int, default=100
            Number of samples to be taken into account for local explainability.

        num_samples_global_expl : int, default=50000
            Number of samples to be taken into account for global explainability.

            .. hint::
               Set up this parameter in case your dataset to be explained is too big. Global explanation will only \
               take into account a number of samples equal to this parameter.

        batch_size_expl: int, default=5000
            Batch size to be used when computing the importance.

        train_stratify: bool, default=True
            When ``train_size`` is different from 0.0, this parameter can be set to True so that the train/test split \
            will keep the target ratio in both of the resulting dataset partitions.

        """
        if num_samples_global_expl < num_samples_local_expl:
            print('ERROR: num_samples_global_expl ({}) < num_samples_local_exp ({}): Number of samples for global '
                  'explainability must be larger than the number of samples for local explainability'
                  .format(num_samples_global_expl, num_samples_local_expl))

        # This section is intended to retrieve information which will be used throughout the execution flow:
        #   Feature related information: different features columns names lists
        #   Target related information: top1_targets (ground truths) for each row, target_probs (probability for each
        #   target), top1_argmax (the indexes version of the top1_targets) and target columns names
        features_info, target_info = Explainer.__get_common_info(df=df, feature_cols=feature_cols,
                                                                 target_cols=target_cols)

        # Feature selector is instantiated
        selector = FeatureSelector(df=df, feature_cols=features_info.feature_columns, target_info=target_info,
                                   number_of_features=self.__number_of_features, verbose=self.__verbose)

        # Then it's used to select the top K features
        topk_features = selector.select_topk()
        self.__top_features = selector.top_features
        self.__top_features_by_target = selector.top_features_by_target

        # Dataset must be rebuilt by selecting the topk features, the ID and the target columns
        df = df[[ID] + topk_features + target_cols]

        # Since feature columns have changed, information related to features must be generated again
        features_info = get_features_info(df=df, feature_cols=topk_features, target_cols=target_cols)

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
            importance_calculator.calculate_importance(df=df, features_info=features_info,
                                                       num_samples=num_samples_global_expl, batch_size=batch_size_expl))
        self.__importance_values = importance_calculator.importance_values

        # Here, the row IDs to be sampled for local explanation are generated. A sample ids mask will be used for id
        # filtering, (the list of sample ids is retrieved too to perform consistency checks)
        target_info = get_target_info(df=df_explanation_global, target_cols=target_cols)
        sample_ids_mask, sample_ids = sample_by_target(ids=df_explanation_global[ID].values,
                                                       top1_targets=target_info.top1_targets,
                                                       num_samples=num_samples_local_expl,
                                                       target_probs=target_info.target_probs,
                                                       target_cols=target_info.target_columns)
        self.__sample_ids_to_display = sample_ids

        # local_dataset_reliability property is computed
        self.__local_reliability = np.concatenate((df_explanation_global[ID].values.reshape(-1, 1),
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
