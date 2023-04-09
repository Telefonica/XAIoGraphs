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
    This class is intended to provide an abstract layer which encapsulates everything related to the explanation process
    from statistics calculation, importance calculation (using the engine chosen by the user) and information export for
    visualization tasks.

    Parameters
    ----------
    dataset : pandas.DataFrame
        The structure containing the whole dataset.

    importance_engine : str
        The name of the method use to compute feature importance.

        .. important::
           LIDE is the available option for version 0.0.2

    destination_path : str, default='./xaioweb_files'
        The path where output files will be stored.

    number_of_features : int
        The number of top relevant features to be selected for importance calculation.

    verbose : int, default=0
        Verbosity level.

        .. hint::
           Any value greater than 0 means verbosity is on.

    """

    def __init__(self, dataset: pd.DataFrame, importance_engine: str, destination_path: str = './xaioweb_files',
                 number_of_features: int = 8, verbose: int = 0):
        self.__global_explainability = None
        self.__global_frequency_feature_value = None
        self.__global_target_feature_value_explainability = None
        self.__global_target_explainability = None
        self.__importance_values = None
        self.__local_dataset_reliability = None
        self.__local_feature_value_explainability = None
        self.__sample_ids_to_display = list()
        self.__top_features = None
        self.__top_features_by_target = None
        self.__df = dataset
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

                - **feature:** feature name.
                - **importance:** feature importance considering all possible target values and all the samples.
                - **rank:** position of the feature when sorted by its importance. The lower the rank the higher the \
                importance.

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.global_explainability
                    feature  importance  rank
            0        gender    0.124936     1
            1         title    0.122790     2
            2         class    0.089931     3
            3  ticket_price    0.062145     4
            7           age    0.059930     5
            4      embarked    0.059490     6
            5   family_size    0.042980     7
            6      is_alone    0.031692     8

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

                - **feature_value:** feature name together with each of its possible values.
                - **frequency:** total number of occurrences for each feature name-value pairs.

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.global_frequency_feature_value
                    feature_value  frequency
            28     family_size_>5         35
            8       age_>60_years         33
            32        gender_male        843
            44           title_Mr        818
            30      gender_female        466
            46          title_Mrs        457
            6       age_<12_years         98
            14            class_3        709
            40   ticket_price_Low        433
            48         title_rare         34
            10            class_1        323
            0     age_12_18_years        105
            26    family_size_3-5         90
            16         embarked_C        270
            18         embarked_Q        123
            20         embarked_S        916
            24      family_size_2        159
            12            class_2        277
            4     age_30_60_years        522
            42   ticket_price_Mid        399
            2     age_18_30_years        551
            38  ticket_price_High        477
            22      family_size_1       1025
            36         is_alone_1       1025
            34         is_alone_0        284

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

                - **target:** each of the possible target values
                - **feature:** feature name
                - **importance:** feature importance with respect to each possible target values
                - **rank:** position of the feature when sorted by its importance. The lower the rank the higher the \
                importance

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.global_target_explainability
                     target       feature  importance  rank
            0   NO_SURVIVED        gender    0.108512     1
            1   NO_SURVIVED         title    0.107290     2
            2   NO_SURVIVED         class    0.074033     3
            3   NO_SURVIVED  ticket_price    0.056893     4
            7   NO_SURVIVED           age    0.052081     5
            4   NO_SURVIVED      embarked    0.050245     6
            5   NO_SURVIVED   family_size    0.037737     7
            6   NO_SURVIVED      is_alone    0.027281     8
            8      SURVIVED        gender    0.151681     1
            9      SURVIVED         title    0.148033     2
            10     SURVIVED         class    0.115822     3
            12     SURVIVED      embarked    0.074544     4
            15     SURVIVED           age    0.072711     5
            11     SURVIVED  ticket_price    0.070697     6
            13     SURVIVED   family_size    0.051519     7
            14     SURVIVED      is_alone    0.038876     8

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

                - **target:** each of the possible target values
                - **feature_value:** feature name together with each of its possible values.
                - **importance:** feature importance with respect to each possible target values
                - **rank:** position of the feature for each target value when sorted by its importance. The lower \
                 the rank the higher the importance

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.global_target_feature_value_explainability
                    target      feature_value  importance  rank
            28  NO_SURVIVED     family_size_>5    0.190344     1
            8   NO_SURVIVED      age_>60_years    0.189757     2
            32  NO_SURVIVED        gender_male    0.109828     3
            44  NO_SURVIVED           title_Mr    0.109525     4
            30  NO_SURVIVED      gender_female    0.100472     5
            46  NO_SURVIVED          title_Mrs    0.099421     6
            6   NO_SURVIVED      age_<12_years    0.090704     7
            14  NO_SURVIVED            class_3    0.083974     8
            40  NO_SURVIVED   ticket_price_Low    0.076323     9
            48  NO_SURVIVED         title_rare    0.074205    10
            10  NO_SURVIVED            class_1    0.067447    11
            0   NO_SURVIVED    age_12_18_years    0.063259    12
            26  NO_SURVIVED    family_size_3-5    0.059982    13
            16  NO_SURVIVED         embarked_C    0.057053    14
            18  NO_SURVIVED         embarked_Q    0.052446    15
            20  NO_SURVIVED         embarked_S    0.048659    16
            24  NO_SURVIVED      family_size_2    0.047822    17
            12  NO_SURVIVED            class_2    0.046022    18
            4   NO_SURVIVED    age_30_60_years    0.045329    19
            42  NO_SURVIVED   ticket_price_Mid    0.043899    20
            2   NO_SURVIVED    age_18_30_years    0.042602    21
            38  NO_SURVIVED  ticket_price_High    0.042125    22
            22  NO_SURVIVED      family_size_1    0.027983    23
            36  NO_SURVIVED         is_alone_1    0.027983    23
            34  NO_SURVIVED         is_alone_0    0.024083    24
            7      SURVIVED      age_<12_years    0.253344     1
            31     SURVIVED      gender_female    0.195549     2
            47     SURVIVED          title_Mrs    0.191031     3
            11     SURVIVED            class_1    0.145615     4
            13     SURVIVED            class_2    0.143814     5
            17     SURVIVED         embarked_C    0.136277     6
            19     SURVIVED         embarked_Q    0.121356     7
            49     SURVIVED         title_rare    0.118885     8
            25     SURVIVED      family_size_2    0.114187     9
            9      SURVIVED      age_>60_years    0.112574    10
            1      SURVIVED    age_12_18_years    0.099684    11
            39     SURVIVED  ticket_price_High    0.096772    12
            29     SURVIVED     family_size_>5    0.091483    13
            15     SURVIVED            class_3    0.064828    14
            33     SURVIVED        gender_male    0.045918    15
            3      SURVIVED    age_18_30_years    0.045671    16
            45     SURVIVED           title_Mr    0.044766    17
            35     SURVIVED         is_alone_0    0.043574    18
            41     SURVIVED   ticket_price_Low    0.042836    19
            43     SURVIVED   ticket_price_Mid    0.042553    20
            5      SURVIVED    age_30_60_years    0.037263    21
            23     SURVIVED      family_size_1    0.037075    22
            37     SURVIVED         is_alone_1    0.037075    22
            21     SURVIVED         embarked_S    0.036138    23
            27     SURVIVED    family_size_3-5    0.032299    24

        """
        if self.__global_target_feature_value_explainability is None:
            print(WARN_MSG.format('\"global_target_feature_value_explainability\"'))
        else:
            return self.__global_target_feature_value_explainability

    @property
    def importance_values(self):
        """Property that returns the computed importance values.

        .. caution::
           If the method :meth:`local_explain` from an :class:`ImportanceCalculator` child class has not been \
           executed, it will return a warning message.

        Returns
        -------
        importance_values : numpy.array, shape (n_samples, n_features, n_target_values)
            Structure containing containing for each sample, feature and target value, the computed importance values

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.importance_values
            [[[ 0.19102919 -0.19102919]
              [ 0.18931973 -0.18931973]
              [ 0.14710146 -0.14710146]
              ...
              [ 0.0049198  -0.0049198 ]
              [ 0.0049198  -0.0049198 ]
              [ 0.00861183 -0.00861183]]
              ...
             [[-0.05596649  0.05596649]
              [-0.05863524  0.05863524]
              [ 0.38645767 -0.38645767]
              ...
              [-0.01077448  0.01077448]
              [ 0.0291813  -0.0291813 ]
              [ 0.31177627 -0.31177627]]
              ...
             [[ 0.04319279 -0.04319279]
              [ 0.04255799 -0.04255799]
              [-0.09668253  0.09668253]
              ...
              [-0.02768731  0.02768731]
              [ 0.00612063 -0.00612063]
              [-0.34010499  0.34010499]]
              ...
             [[-0.09110644  0.09110644]
              [-0.09225141  0.09225141]
              [-0.06639871  0.06639871]
              ...
              [-0.02507825  0.02507825]
              [-0.02507825  0.02507825]
              [-0.03583761  0.03583761]]
              ...
             [[-0.09110644  0.09110644]
              [-0.09225141  0.09225141]
              [-0.06639871  0.06639871]
              ...
              [-0.02507825  0.02507825]
              [-0.02507825  0.02507825]
              [-0.03583761  0.03583761]]
              ...
             [[-0.08246317  0.08246317]
              [-0.08290531  0.08290531]
              [-0.04468906  0.04468906]
              ...
              [-0.02018317  0.02018317]
              [-0.02018317  0.02018317]
              [-0.02992086  0.02992086]]]

        """
        if self.__importance_values is None:
            print(WARN_MSG.format('\"importance_values\"'))
        else:
            return self.__importance_values

    @property
    def local_dataset_reliability(self):
        """Property that, for each sample, returns its top1 target and the reliability value associated to that target.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        local_dataset_reliability :  pandas.DataFrame
            Structure containing for each sample its top1 target and the reliability value associated to that target. \
            It contains the following columns:

                - **id:** identifier for each sample.
                - **target:** each of the possible target values.
                - **reliability:** associated reliability value.

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.local_dataset_reliability
                    id       target  reliability
            0        0     SURVIVED         1.00
            1        1     SURVIVED         1.00
            2        2  NO_SURVIVED         1.00
            3        3  NO_SURVIVED         1.00
            4        4  NO_SURVIVED         0.20
            ...    ...          ...          ...
            1304  1304  NO_SURVIVED         0.60
            1305  1305  NO_SURVIVED         1.00
            1306  1306  NO_SURVIVED         0.87
            1307  1307  NO_SURVIVED         0.87
            1308  1308  NO_SURVIVED         0.89
            [1309 rows x 3 columns]

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

                - **id:** identifier for each sample.
                - **feature_value:** feature name together with each of its possible values.
                - **importance:** feature importance for each feature_value pair and the top1 target.
                - **rank:** position of the feature_value pair for each sample when sorted by its importance. The \
                lower the rank the higher the importance

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.local_feature_value_explainability
                     id      feature_value  importance  rank
            0         0      gender_female    0.191029     1
            1         0          title_Mrs    0.189320     2
            2         0            class_1    0.147101     3
            3         0  ticket_price_High    0.101550     4
            4         0         embarked_S   -0.027895     8
            ...     ...                ...         ...   ...
            10467  1308   ticket_price_Low    0.065827     3
            10468  1308         embarked_S    0.034272     5
            10469  1308      family_size_1    0.020183     7
            10470  1308         is_alone_1    0.020183     7
            10471  1308    age_18_30_years    0.029921     6
            [10472 rows x 4 columns]

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
        """Property that retrieves the sample ids which will be used to build the interactive visualization.

        .. caution::
           If the method :meth:`fit` from the :class:`Explainer` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        local_feature_value_explainability : pandas.Series
            Structure containing the ids for the chosen samples.

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.sample_ids_to_display
            0     519
            1     998
            2     493
            3     614
            4     951
                 ...
            94      5
            95    647
            96    120
            97    350
            98    293
            Name: id, Length: 99, dtype: uint16

        """
        if self.__sample_ids_to_display is None:
            print(WARN_MSG.format('\"sample_ids_to_display\"'))
        else:
            return pd.to_numeric(pd.Series(self.__sample_ids_to_display, name=ID), downcast="unsigned")

    @property
    def top_features(self):
        """Property that returns all the features ranked by the ``FeatureSelector``. Ranking is calculated as follows:

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

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.top_features
                    feature  rank
            0        gender     1
            1         title     2
            2         class     3
            3  ticket_price     4
            4      embarked     5
            5   family_size     6
            6      is_alone     7
            7           age     8

        """
        if self.__top_features is None:
            print(WARN_MSG.format('\"top_features\"'))
        else:
            return self.__top_features

    @property
    def top_features_by_target(self):
        """Property that returns all the features ranked by the ``FeatureSelector``.

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
            Furthermore, the distance for each feature and target value, is provided along with its rank

        Example
        -------
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> explainer = Explainer(dataset=df_titanic, importance_engine='LIDE', verbose=1)
            >>> explainer.fit(feature_cols=feature_cols, target_cols=target_cols)
            >>> explainer.top_features_by_target
                    target       feature  distance
            0  NO_SURVIVED        gender  0.262507
            1  NO_SURVIVED         title  0.241172
            2  NO_SURVIVED         class  0.128430
            3  NO_SURVIVED  ticket_price  0.117809
            4  NO_SURVIVED      embarked  0.076622
            5  NO_SURVIVED   family_size  0.069195
            6  NO_SURVIVED      is_alone  0.053045
            7  NO_SURVIVED           age  0.051220

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

    def fit(self, feature_cols: List[str], target_cols: List[str], num_samples_local_expl: int = 100,
            num_samples_global_expl: int = 50000, batch_size_expl: int = 5000, train_stratify: bool = True):
        """It coordinates all the steps of the explanation process which consists of the following parts:

        - Feature selection, takes care of determining which are top K most relevant features. K is defined by the \
        parameter ``number_of_features`` in the constructor of the :class:`Explainer` class.
        - Importance calculation, takes care of computing importance for the remaining features from the previous step \
        and the possible target values
        - Stats calculation, takes care of computing different counts and ratios which are particularly important to \
        feed those files used for visualization purposes
        - Exporter, generates all those files realated to the Explanation process which will be used for visualization \
        purposes

        Parameters
        ----------
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
