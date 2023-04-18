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


import os
import random
from string import Template
from typing import Any, List, Optional, Tuple, Union

import pandas as pd

from xaiographs.common.constants import ID, FEATURE_VALUE, LANG_EN, LANG_ES, IMPORTANCE, RELIABILITY, RANK, TARGET
from xaiographs.common.utils import xgprint

# Warning message
WARN_MSG = 'WARNING: {} is empty, because nothing has been processed. Execute fit() function to get results.'

# CONSTANTS
COMMA_SEP = ','
RAND = 'rand'
REASON = 'reason'

# FILE CONSTANTS
WHY_XAIOWEB_FILE = 'local_reason_why.json'
WHY_GLOBAL_SEMANTICS_TEMPLATE = 'global_semantics.csv'
WHY_TARGET_SEMANTICS_TEMPLATE = 'target_semantics.csv'


class Why(object):
    """
    This class is intended to provide an explanation on why a given case has been assigned a certain label
    (target value), combining the local reason (case-specific), the global reason (model-specific) and the target
    itself.

    Read more in the :ref:`Reason Why <user_guide/why>` User Guide

    Parameters
    ----------
    language : str
        Language identifier.

        .. important::
           Spanish (*'es'*) and English (*'en'*) are the available options for version 0.0.2

    local_reliability : pandas.DataFrame
        Structure containing, for each sample, its top1 target and the reliability value associated to that target.

    local_feat_val_expl : pandas.DataFrame
        Structure containing, for each sample, as many rows as feature-value pairs, together with their calculated \
        importance.

    why_elements : pandas.DataFrame
        Structure containing the natural language explanation of the nodes to be used.

    why_target : pandas.DataFrame
        Structure containing the natural language explanation of the nodes we want to be used per target value.

    why_templates : pandas.DataFrame
        Structure containing the templates (following \
        `Python template module <https://docs.python.org/3.7/library/string.html#template-strings>`_) of the sentences
        with the explanation.

    n_local_features : int, default=2
        Number of local features to take into account for the explanation.

    n_global_features : int, default=2
        Number of global features to take into account for the explanation.

    min_reliability : float, default=0.0
        Minimum reliability value to give an explanation; for the cases with an associated reliability below this \
        value, a default sentence will be provided.

    destination_path : str, default='./xaioweb_files'
        The path where output XAIoWeb files will be stored.

    sample_ids_to_export : List[int], default=None
        Ids of those samples for which their explanation will be displayed in an interactive environment.

    verbose : int, default=0
        Verbosity level.

        .. hint::
           Any value greater than 0 means verbosity is on.

    Raises
    ------
    NameError
        Exception when the chosen language is not available.


    """

    _LOCAL = 'local'
    _GLOBAL = 'global'
    _SEP_LAST = {
        LANG_ES: ' y ',
        LANG_EN: ' and '
    }

    def __init__(self, language: str, local_reliability: pd.DataFrame, local_feat_val_expl: pd.DataFrame,
                 why_elements: pd.DataFrame, why_target: pd.DataFrame, why_templates: pd.DataFrame,
                 n_local_features: int = 2, n_global_features: int = 2, min_reliability: float = 0.0,
                 destination_path: str = './xaioweb_files', sample_ids_to_export: Optional[List[int]] = None,
                 verbose: int = 0):
        self.__df_why = None
        self.__language = language
        if self.__language not in self._SEP_LAST.keys():
            raise NameError('Language {} not supported'.format(self.__language))
        self.__local_reliability = local_reliability
        self.__local_feat_val_expl = local_feat_val_expl
        self.__why_elements = why_elements
        self.__why_target = why_target
        self.__why_templates = why_templates
        self.__n_local_features = n_local_features
        self.__n_global_features = n_global_features
        self.__min_reliability = min_reliability
        self.__destination_path = destination_path
        self.__rng = random.SystemRandom()
        self.__sample_ids_to_export = sample_ids_to_export
        self.__verbose = verbose
        xgprint(self.__verbose, 'INFO: Instantiating Why. Language has been set to: {}'.format(self.__language))

    @property
    def why_explanation(self):
        """Property that returns the explanation provided by the :class:`Why` module for either all samples or one of \
        the user's choice.

        .. caution::
           If the method :meth:`fit` from the :class:`Why` class has not been executed, it will return a warning \
           message.

        Returns
        -------
        why_explanation : pandas.DataFrame
            Structure containing a column indicating the sample ID and another column containing the verbal explanation

        """
        if self.__df_why is None:
            print(WARN_MSG.format('\"why_explanation\"'))
        else:
            return self.__df_why

    def __build_template(self, items: Union[List, Tuple]) -> str:
        """
        Build template for a list (or tuple) of variable names as an enumeration in natural language

        :param items: List of variable names (e.g. ['v_local_0', 'v_local_1', 'v_local_2'])
        :return: String with the Python template (e.g. '$v_local_0, $v_local_1 y $v_local_2')
        """
        sep_last = self._SEP_LAST[self.__language]
        i_list = [Template.delimiter + i for i in (items if isinstance(items, list) else list(items))]
        return (COMMA_SEP.join(i_list[:-1]) + sep_last + i_list[-1]) if len(i_list) > 1 else i_list[0]

    def fit(self, sample_id_column: str = ID, sample_id_value: Any = None, template_index: Union[str, int] = RAND):
        """Depending on the value of ``sample_id_value`` parameter, this method proceeds as follows:

        - If the mentioned parameter is None then builds a DataFrame with the sentences of the reason why each \
        case has been assigned a label.
        - Otherwise, simply gets the sentence with the reason why a given case has been assigned a label

        Parameters
        ----------
        sample_id_column : str, default=ID
            Name of the column that holds the primary key

        sample_id_value : Any, default=None
            Value to select from the column specified in argument ``sample_id_column``

        template_index : str or int, default=RAND
            Index of the template to be used to build the final sentence amongst the ones available in \
            ``why_templates`` attribute; please note that:

            - Index 0 is reserved for the default template.
            - If the requested index is greater than the last available one, the latter will be provided.

        Raises
        ------
        ValueError
            Exception either when the requested key does not exist or when there are more than one row for the \
            requested key.


        """
        xgprint(self.__verbose,
                'INFO:     Why instance fitted with "{}" selected as primary key'.format(sample_id_column))
        # Check case existence if a single case is requested
        if sample_id_value is None:
            local_expl = self.__local_reliability
            xgprint(self.__verbose, 'INFO:     Explanation for all samples has been requested')
        else:
            local_expl = self.__local_reliability[self.__local_reliability[sample_id_column] == sample_id_value]
            xgprint(self.__verbose,
                    'INFO:     Explanation for a single case ({}) has been requested'.format(sample_id_value))
            if local_expl.shape[0] == 0:
                raise ValueError("Value {} does not exist in column \'{}\'".format(sample_id_value, sample_id_column))
            elif local_expl.shape[0] > 1:
                raise ValueError("More than one row with value {} in column \'{}\'".format(sample_id_value,
                                                                                           sample_id_column))

        # Build a DataFrame with all the case information
        df = (local_expl[[sample_id_column, RELIABILITY, TARGET]]
              .merge(self.__local_feat_val_expl[[sample_id_column, FEATURE_VALUE, IMPORTANCE]], on=sample_id_column,
                     how='inner')
              .merge(self.__why_elements, on=FEATURE_VALUE, how='inner')
              .merge(self.__why_target, on=[TARGET, FEATURE_VALUE], how='inner',
                     suffixes=['_' + self._LOCAL, '_' + self._GLOBAL]))
        df[RANK] = df.groupby(sample_id_column)[IMPORTANCE].rank(method='dense', ascending=False).astype(int)

        max_n_features = max(self.__n_local_features, self.__n_global_features)
        df_rank = df[df[RANK] <= max_n_features]

        def __get_single_why(df_single: pd.DataFrame) -> str:
            """
            Builds a sentence with the reason why a single case has been assigned a label

            :param df_single: Pandas DataFrame with the nodes associated to the selected case
            :return: String with the final sentence for the requested case
            """
            # Check the reliability of the explainability values
            r = df_single.head(1)
            reliability = r[RELIABILITY].values[0]
            if reliability < self.__min_reliability:
                return self.__why_templates.iloc[0, 0]

            # Build why sentence
            kw_local = dict([('v_' + self._LOCAL + '_' + str(i), v) for i, v in
                             enumerate(df_single[REASON + '_' + self._LOCAL].iloc[:self.__n_local_features])])
            kw_global = dict([('v_' + self._GLOBAL + '_' + str(i), v) for i, v in
                              enumerate(df_single[REASON + '_' + self._GLOBAL].iloc[:self.__n_global_features])])
            temp_local_explain = self.__build_template(items=list(kw_local))
            temp_global_explain = self.__build_template(items=list(kw_global))

            temp_idx_max = self.__why_templates.shape[0] - 1
            temp_idx = self.__rng.randint(1, temp_idx_max) if template_index == RAND else min(template_index,
                                                                                              temp_idx_max)
            temp_why_str = (Template(Template(self.__why_templates.iloc[temp_idx, 0])
                                     .substitute(temp_local_explain=temp_local_explain,
                                                 temp_global_explain=temp_global_explain,
                                                 target=df_single[TARGET].iloc[0]))
                            .substitute(**kw_local, **kw_global)
                            .capitalize())
            return temp_why_str

        df_final = df_rank.groupby(sample_id_column).apply(__get_single_why).to_frame(REASON).reset_index()

        # Writing files for the web interface
        if self.__sample_ids_to_export is not None:
            if not os.path.exists(self.__destination_path):
                os.mkdir(self.__destination_path)
            xgprint(self.__verbose,
                    'INFO:     Exporting explanation for the given sample ids to {}'.format(self.__destination_path))
            df_final.merge(self.__sample_ids_to_export, left_on=sample_id_column, right_on=ID, how='inner').to_json(
                path_or_buf=os.path.join(self.__destination_path, WHY_XAIOWEB_FILE), orient='records')
        else:
            xgprint(self.__verbose, 'WARN:     Explanation wont be exported since sample ids have not been provided'
                                    ' through `sample_ids_to_export` Why constructor parameter ')

        self.__df_why = df_final

    @staticmethod
    def build_semantic_templates(global_feat_val_expl: pd.DataFrame, destination_template_path: Optional[str] = None,
                                 verbose: int = 0) -> List[pd.DataFrame]:
        """Builds and saves (when requested) the template files for semantic information; the resulting files must be
        filled up by the user and moved to the corresponding language folder.

        Parameters
        ----------
        global_feat_val_expl : pandas.DataFrame
            Structure containing, for each feature value and target pairs, its importance and rank. The rank \
            represents the importance of that feature value pair for the given target value

        destination_template_path : str
            Path to save both: the element (feature-value) template file and the target template file in CSV format

        verbose : int, default=0
            Verbosity level.

            .. hint::
               Any value greater than 0 means verbosity is on.

        Returns
        -------
        [df_element, df_target] : List of two pandas.DataFrames
            Being the first one the element template data and the second one the target template data


        """
        xgprint(verbose,
                'INFO:     Why instance: building semantic templates for feature-value pairs and target values...')

        # Build element template DataFrame
        df_element = (global_feat_val_expl[[FEATURE_VALUE]]
                      .drop_duplicates()
                      .sort_values(by=FEATURE_VALUE))
        df_element[REASON] = ''

        # Build target template DataFrame
        df_target = (global_feat_val_expl[[TARGET]]
                     .drop_duplicates()
                     .merge(df_element, how='cross')
                     .sort_values(by=[TARGET, FEATURE_VALUE]))

        # Save to CSV if requested
        if destination_template_path is not None:
            if not os.path.exists(destination_template_path):
                os.mkdir(destination_template_path)
            xgprint(verbose,
                    'INFO:          Why instance: saving feature-value pairs semantic template ({}) to {}'.format(
                        WHY_GLOBAL_SEMANTICS_TEMPLATE, destination_template_path))
            df_element.to_csv(path_or_buf=os.path.join(destination_template_path, WHY_GLOBAL_SEMANTICS_TEMPLATE),
                              index=False, sep=COMMA_SEP)
            xgprint(verbose,
                    'INFO:          Why instance: saving target values semantic template ({}) to {}'.format(
                        WHY_TARGET_SEMANTICS_TEMPLATE, destination_template_path))
            df_target.to_csv(path_or_buf=os.path.join(destination_template_path, WHY_TARGET_SEMANTICS_TEMPLATE),
                             index=False, sep=COMMA_SEP)
        else:
            xgprint(verbose,
                    'WARN:          Why instance: unable to save neither feature-value pairs nor target semantic '
                    'templates. A path through `destination_template_path` parameter must be provided')
        return [df_element, df_target]
