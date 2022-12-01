import pandas as pd
import random
from string import Template
from typing import Any, List, Tuple, Union

from xaiographs.common.constants import FEATURE, LANG_EN, LANG_ES, NODE_IMPORTANCE, NODE_NAME, QUALITY_MEASURE, RAND
from xaiographs.common.constants import RANK, REASON, TARGET


class Why(object):
    """
    Main class to provide an explanation on why a given case has been assigned a label (target value), combining
    the local reason (case-specific), the global reason (model-specific) and the target itself
    """

    _LOCAL = 'local'
    _GLOBAL = 'global'
    _SEP_LAST = {
        LANG_ES: ' y ',
        LANG_EN: ' and '
    }

    def __init__(self, language: str, local_expl: pd.DataFrame, local_nodes: pd.DataFrame, why_elements: pd.DataFrame,
                 why_target: pd.DataFrame, why_templates: pd.DataFrame, quality_measure: pd.DataFrame,
                 n_local_features: int = 2, n_global_features: int = 2, min_quality: float = 0.0):
        """
        Constructor method for Why

        :param language: Language identifier
        :param local_expl: Pandas DataFrame with the local nodes' explainability
        :param local_nodes: Pandas DataFrame with the importance the local nodes
        :param why_elements: Pandas DataFrame with the natural language explanation of the nodes we want to use
        :param why_target: Pandas DataFrame with the natural language explanation of the nodes we want to use per target
            value
        :param why_templates: Pandas DataFrame with the templates (following Python Template module) of the sentences
            with the explanation
        :param quality_measure: Pandas DataFrame with the quality measure (a kind of confidence level) for each case
        :param n_local_features: Number of local features to take into account for the explanation
        :param n_global_features: Number of global features to take into account for the explanation
        :param min_quality: Minimum quality value to give an explanation; for the cases with an associated quality
            measure below this value, a default sentence will be provided
        :raises NameError: Raises an exception when the chosen language is not available
        """
        self.language = language
        if self.language not in self._SEP_LAST.keys():
            raise NameError("Language {} not supported".format(language))
        self.local_expl = local_expl
        self.local_nodes = local_nodes
        self.why_elements = why_elements
        self.why_target = why_target
        self.why_templates = why_templates
        self.quality_measure = quality_measure
        self.n_local_features = n_local_features
        self.n_global_features = n_global_features
        self.min_quality = min_quality

    def __build_template(self, items: Union[List, Tuple], sep=', ') -> str:
        """
        Build template for a list (or tuple) of variable names as an enumeration in natural language

        :param items: List of variable names (e.g. ['v_local_0', 'v_local_1', 'v_local_2'])
        :param sep: Separator or delimiter of the enumeration
        :return: String with the Python template (e.g. '$v_local_0, $v_local_1 y $v_local_2')
        """
        sep_last = self._SEP_LAST[self.language]
        i_list = [Template.delimiter + i for i in (items if isinstance(items, list) else list(items))]
        return (sep.join(i_list[:-1]) + sep_last + i_list[-1]) if len(i_list) > 1 else i_list[0]

    def build_why(self, key_column: str, key_value: Any = None, template_index: Union[str, int] = RAND) -> Union[
                  pd.DataFrame, str]:
        """
        In case the argument `key_value` id None, builds a DataFrame with the sentences of the reason why each case has
        been assigned a label; otherwise, simply gets the sentence with the reason why a given case has been assigned a
        label

        :param key_column: Name of the column that holds the primary key
        :param key_value: Value to select from the column specified in argument `key_column`
        :param template_index: Index of the template to be used to build the final sentence amongst the ones available
            in `why_templates` attribute; please note that: (1) index 0 is reserved for the default template, (2) if the
            requested index is greater than the last available one, the latter will be provided. Defaults to 'rand'
            (random selection excluding index 0)
        :return: Either a Pandas DataFrame with one sentence per case or a string with the final sentence for the
            requested case
        :raises ValueError: Raises an exception either when the requested key does not exist or when there are more
            than one row for the requested key
        """
        # Check case existence if a single case is requested
        if key_value is None:
            local_expl = self.local_expl
        else:
            local_expl = self.local_expl[self.local_expl[key_column] == key_value]
            if local_expl.shape[0] == 0:
                raise ValueError("Value {} does not exist in column \'{}\'".format(key_value, key_column))
            elif local_expl.shape[0] > 1:
                raise ValueError("More than one row with value {} in column \'{}\'".format(key_value, key_column))

        # Build a dataframe with all the case information
        df = (local_expl[[key_column, TARGET]]
              .merge(self.local_nodes[[key_column, NODE_NAME, NODE_IMPORTANCE]], on=key_column, how='inner')
              .merge(self.why_elements.rename(columns={FEATURE: NODE_NAME}), on=NODE_NAME, how='inner')
              .merge(self.why_target.rename(columns={FEATURE: NODE_NAME}),
                     on=[TARGET, NODE_NAME], how='inner', suffixes=['_' + self._LOCAL, '_' + self._GLOBAL])
              .merge(self.quality_measure[[key_column, QUALITY_MEASURE]], on=key_column, how='left'))
        df[RANK] = df.groupby(key_column)[NODE_IMPORTANCE].rank(method='dense', ascending=False).astype(int)

        max_n_features = max(self.n_local_features, self.n_global_features)
        df_rank = df[df[RANK] <= max_n_features]

        def get_single_why(df_single: pd.DataFrame) -> str:
            """
            Builds a sentence with the reason why a single case has been assigned a label

            :param df_single: Pandas DataFrame with the nodes associated to the selected case
            :return: String with the final sentence for the requested case
            """
            # Check the quality of the explainability values
            r = df_single.head(1)
            quality = r[QUALITY_MEASURE].values[0]
            if quality < self.min_quality:
                return self.why_templates.iloc[0, 0]

            # Build why sentence
            kw_local = dict([('v_' + self._LOCAL + '_' + str(i), v) for i, v in
                             enumerate(df_single[REASON + '_' + self._LOCAL].iloc[:self.n_local_features])])
            kw_global = dict([('v_' + self._GLOBAL + '_' + str(i), v) for i, v in
                              enumerate(df_single[REASON + '_' + self._GLOBAL].iloc[:self.n_global_features])])
            temp_local_explain = self.__build_template(items=list(kw_local))
            temp_global_explain = self.__build_template(items=list(kw_global))

            temp_idx_max = self.why_templates.shape[0] - 1
            temp_idx = random.randint(1, temp_idx_max) if template_index == RAND else min(template_index, temp_idx_max)
            temp_why_str = (Template(Template(self.why_templates.iloc[temp_idx, 0])
                                     .substitute(temp_local_explain=temp_local_explain,
                                                 temp_global_explain=temp_global_explain,
                                                 target=df_single[TARGET].iloc[0]))
                            .substitute(**kw_local, **kw_global)
                            .capitalize())
            return temp_why_str

        df_final = df_rank.groupby(key_column).apply(get_single_why).to_frame(REASON).reset_index()
        if key_value is None:
            return df_final
        else:
            return df_final[REASON].values[0]
