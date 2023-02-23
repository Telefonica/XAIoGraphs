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
    Main class to provide an explanation on why a given case has been assigned a label (target value), combining
    the local reason (case-specific), the global reason (model-specific) and the target itself.

    Example:
        >>> import pandas as pd
        >>> local_reliability = pd.DataFrame(
        ...    {
        ...        'id': [5, 62],
        ...        'target': ['survivor', 'no_survivor'],
        ...        'reliability': [0.14, 1.0]
        ...    },
        ...    columns=['id', 'target', 'reliability']
        ... )
        >>> local_reliability
            id      target   reliability
         0   5    survivor          0.14
         1  62 no_survivor           1.0
        >>> local_feat_val_expl = pd.DataFrame(
        ...    {
        ...        'id': [5, 5, 5, 5, 5, 5, 5, 5, 62, 62, 62, 62, 62, 62, 62, 62],
        ...        'feature_value': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'family_size_0.00', 'embarked_S', 'sex_male', 'age_0.95', 'title_Mr', 'title_Mr', 'sex_male', 'embarked_S', 'age_0.95', 'is_alone_1.00', 'fare_0.95', 'family_size_1.00', 'pclass_1.00'],
        ...        'importance': [0.195, 0.146, 0.099, 0.08, 0.059, 0.023, 0.016, 0.006, 0.163, 0.155, 0.099, 0.086, 0.014, -0.001, -0.058, -0.081],
        ...        'rank': [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8]
        ...    },
        ...    columns=['id', 'feature_value', 'importance', 'rank']
        ... )
        >>> local_feat_val_expl
           id    feature_value      importance rank
         0  5      pclass_1.00           0.195    1
         1  5        fare_0.75           0.146    2
         2  5    is_alone_1.00           0.099    3
         3  5 family_size_0.00           0.080    4
         4  5       embarked_S           0.059    5
         5  5         sex_male           0.023    6
         6  5         age_0.95           0.016    7
         7  5         title_Mr           0.006    8
         8 62         title_Mr           0.163    1
         9 62         sex_male           0.155    2
        10 62       embarked_S           0.099    3
        11 62         age_0.95           0.086    4
        12 62    is_alone_1.00           0.014    5
        13 62        fare_0.95          -0.001    6
        14 62 family_size_1.00          -0.058    7
        15 62      pclass_1.00          -0.081    8
        >>> why_elements = pd.DataFrame(
        ...    {
        ...        'feature_value': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'sex_male', 'embarked_S', 'age_0.95'],
        ...        'reason': ['viajar en 1ª clase', 'pagar mucho por el billete', 'viajar solo', 'ser hombre', 'embarcar en un pueblo de clase baja', 'ser una persona muy mayor']
        ...    },
        ...    columns = ['feature_value', 'reason']
        ... )
        >>> why_elements
          feature_value                              reason
        0   pclass_1.00                  viajar en 1ª clase
        1     fare_0.75          pagar mucho por el billete
        2 is_alone_1.00                         viajar solo
        3      sex_male                          ser hombre
        4    embarked_S embarcar en un pueblo de clase baja
        5      age_0.95           ser una persona muy mayor
        >>> why_target = pd.DataFrame(
        ...    {
        ...        'target': ['survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor'],
        ...        'feature_value': ['embarked_S', 'pclass_1.00', 'fare_0.75', 'sex_male', 'embarked_S', 'age_0.95'],
        ...        'reason': ['pocos embarcaron en Southampton', 'muchos viajaban en 1ª clase', 'pagaron mucho por el billete', 'han muerto muchos hombres', 'muchos embarcaron en Southampton', 'eran muy mayores']
        ...    },
        ...    columns = ['target', 'feature_value', 'reason']
        ... )
        >>> why_target
               target     feature_value                           reason
        0    survivor        embarked_S  pocos embarcaron en Southampton
        1    survivor       pclass_1.00      muchos viajaban en 1ª clase
        2    survivor         fare_0.75     pagaron mucho por el billete
        3 no_survivor          sex_male        han muerto muchos hombres
        4 no_survivor        embarked_S muchos embarcaron en Southampton
        5 no_survivor          age_0.95                 eran muy mayores
        >>> why_templates = pd.DataFrame(
        ...    {
        ...        0: ['No es posible ofrecer una explicación para este caso.',
        ...            'Por $temp_local_explain, este caso ha sido clasificado como $target, teniendo en cuenta que $temp_global_explain.',
        ...            'Por $temp_local_explain, este caso ha sido clasificado como $target, puesto que $temp_global_explain.',
        ...            'Este caso ha sido clasificado como $target por $temp_local_explain, ya que $temp_global_explain.',
        ...            'La clasificación de este caso como $target se debe a $temp_local_explain, ya que $temp_global_explain.',
        ...            'Como $temp_global_explain, y este caso se caracteriza por $temp_local_explain, ha sido clasificado como $target.']
        ...    },
        ...    columns = [0]
        ... )
        >>> why_templates
                                                                                                                           0
        0                                                              No es posible ofrecer una explicación para este caso.
        1  Por $temp_local_explain, este caso ha sido clasificado como $target, teniendo en cuenta que $temp_global_explain.
        2              Por $temp_local_explain, este caso ha sido clasificado como $target, puesto que $temp_global_explain.
        3                   Este caso ha sido clasificado como $target por $temp_local_explain, ya que $temp_global_explain.
        4             La clasificación de este caso como $target se debe a $temp_local_explain, ya que $temp_global_explain.
        5   Como $temp_global_explain, y este caso se caracteriza por $temp_local_explain, ha sido clasificado como $target.
        >>> why = Why(language='es', local_reliability=local_reliability, local_feat_val_expl=local_feat_val_expl,
        ...           why_elements=why_elements, why_target=why_target, why_templates=why_templates, n_local_features=2,
        ...           n_global_features=2, min_reliability=0.0)
        >>> why.__language
        'es'
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
        """
        Constructor method for Why

        :param language: Language identifier
        :param local_reliability: Pandas DataFrame containing, for each sample, its top1 target and the reliability
                                  value associated to that target
        :param local_feat_val_expl: Pandas DataFrame containing, for each sample, as many rows as feature-value pairs,
                                    together with their calculated importance
        :param why_elements: Pandas DataFrame with the natural language explanation of the nodes we want to use
        :param why_target: Pandas DataFrame with the natural language explanation of the nodes we want to use per target
            value
        :param why_templates: Pandas DataFrame with the templates (following Python Template module) of the sentences
            with the explanation
        :param n_local_features: Number of local features to take into account for the explanation
        :param n_global_features: Number of global features to take into account for the explanation
        :param min_reliability: Minimum reliability value to give an explanation; for the cases with an associated
            reliability below this value, a default sentence will be provided
        :param destination_path: String representing the path where output files will be stored
        :param sample_ids_to_export: List of integers representing the ids of those samples for which their explanation
                                     will be displayed in an interactive environment
        :param verbose: Verbosity level, where any value greater than 0 means the message is printed
        :raises NameError: Raises an exception when the chosen language is not available
        """
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
        """
        Property that returns the explanation provided by the Why module for either all samples or one of the user's
        choice.

        :return: pd.DataFrame, containing a column indicating the sample ID and another column containing the verbal
                 explanation
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
        """
        In case the argument `sample_id_value` id None, builds a DataFrame with the sentences of the reason why each
        case has been assigned a label; otherwise, simply gets the sentence with the reason why a given case has been
        assigned a label

        :param sample_id_column: Name of the column that holds the primary key
        :param sample_id_value: Value to select from the column specified in argument `sample_id_column`
        :param template_index: Index of the template to be used to build the final sentence amongst the ones available
            in `why_templates` attribute; please note that: (1) index 0 is reserved for the default template, (2) if the
            requested index is greater than the last available one, the latter will be provided. Defaults to 'rand'
            (random selection excluding index 0)
        :raises ValueError: Raises an exception either when the requested key does not exist or when there are more
            than one row for the requested key

        Example:
            >>> import pandas as pd
            >>> local_reliability = pd.DataFrame(
            ...    {
            ...        'id': [5, 62],
            ...        'target': ['survivor', 'no_survivor'],
            ...        'reliability': [0.14, 1.0]
            ...    },
            ...    columns=['id', 'target', 'reliability']
            ... )
            >>> local_reliability
                id      target   reliability
             0   5    survivor          0.14
             1  62 no_survivor           1.0
            >>> local_feat_val_expl = pd.DataFrame(
            ...    {
            ...        'id': [5, 5, 5, 5, 5, 5, 5, 5, 62, 62, 62, 62, 62, 62, 62, 62],
            ...        'feature_value': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'family_size_0.00', 'embarked_S', 'sex_male', 'age_0.95', 'title_Mr', 'title_Mr', 'sex_male', 'embarked_S', 'age_0.95', 'is_alone_1.00', 'fare_0.95', 'family_size_1.00', 'pclass_1.00'],
            ...        'importance': [0.195, 0.146, 0.099, 0.08, 0.059, 0.023, 0.016, 0.006, 0.163, 0.155, 0.099, 0.086, 0.014, -0.001, -0.058, -0.081],
            ...        'rank': [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8]
            ...    },
            ...    columns=['id', 'feature_value', 'importance', 'rank']
            ... )
            >>> local_feat_val_expl
               id    feature_value      importance rank
             0  5      pclass_1.00           0.195    1
             1  5        fare_0.75           0.146    2
             2  5    is_alone_1.00           0.099    3
             3  5 family_size_0.00           0.080    4
             4  5       embarked_S           0.059    5
             5  5         sex_male           0.023    6
             6  5         age_0.95           0.016    7
             7  5         title_Mr           0.006    8
             8 62         title_Mr           0.163    1
             9 62         sex_male           0.155    2
            10 62       embarked_S           0.099    3
            11 62         age_0.95           0.086    4
            12 62    is_alone_1.00           0.014    5
            13 62        fare_0.95          -0.001    6
            14 62 family_size_1.00          -0.058    7
            15 62      pclass_1.00          -0.081    8
            >>> why_elements = pd.DataFrame(
            ...    {
            ...        'feature_value': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'sex_male', 'embarked_S', 'age_0.95'],
            ...        'reason': ['viajar en 1ª clase', 'pagar mucho por el billete', 'viajar solo', 'ser hombre', 'embarcar en un pueblo de clase baja', 'ser una persona muy mayor']
            ...    },
            ...    columns = ['feature_value', 'reason']
            ... )
            >>> why_elements
              feature_value                              reason
            0   pclass_1.00                  viajar en 1ª clase
            1     fare_0.75          pagar mucho por el billete
            2 is_alone_1.00                         viajar solo
            3      sex_male                          ser hombre
            4    embarked_S embarcar en un pueblo de clase baja
            5      age_0.95           ser una persona muy mayor
            >>> why_target = pd.DataFrame(
            ...    {
            ...        'target': ['survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor'],
            ...        'feature_value': ['embarked_S', 'pclass_1.00', 'fare_0.75', 'sex_male', 'embarked_S', 'age_0.95'],
            ...        'reason': ['pocos embarcaron en Southampton', 'muchos viajaban en 1ª clase', 'pagaron mucho por el billete', 'han muerto muchos hombres', 'muchos embarcaron en Southampton', 'eran muy mayores']
            ...    },
            ...    columns = ['target', 'feature_value', 'reason']
            ... )
            >>> why_target
                   target     feature_value                           reason
            0    survivor        embarked_S  pocos embarcaron en Southampton
            1    survivor       pclass_1.00      muchos viajaban en 1ª clase
            2    survivor         fare_0.75     pagaron mucho por el billete
            3 no_survivor          sex_male        han muerto muchos hombres
            4 no_survivor        embarked_S muchos embarcaron en Southampton
            5 no_survivor          age_0.95                 eran muy mayores
            >>> why_templates = pd.DataFrame(
            ...    {
            ...        0: ['No es posible ofrecer una explicación para este caso.',
            ...            'Por $temp_local_explain, este caso ha sido clasificado como $target, teniendo en cuenta que $temp_global_explain.',
            ...            'Por $temp_local_explain, este caso ha sido clasificado como $target, puesto que $temp_global_explain.',
            ...            'Este caso ha sido clasificado como $target por $temp_local_explain, ya que $temp_global_explain.',
            ...            'La clasificación de este caso como $target se debe a $temp_local_explain, ya que $temp_global_explain.',
            ...            'Como $temp_global_explain, y este caso se caracteriza por $temp_local_explain, ha sido clasificado como $target.']
            ...    },
            ...    columns = [0]
            ... )
            >>> why_templates
                                                                                                                               0
            0                                                              No es posible ofrecer una explicación para este caso.
            1  Por $temp_local_explain, este caso ha sido clasificado como $target, teniendo en cuenta que $temp_global_explain.
            2              Por $temp_local_explain, este caso ha sido clasificado como $target, puesto que $temp_global_explain.
            3                   Este caso ha sido clasificado como $target por $temp_local_explain, ya que $temp_global_explain.
            4             La clasificación de este caso como $target se debe a $temp_local_explain, ya que $temp_global_explain.
            5   Como $temp_global_explain, y este caso se caracteriza por $temp_local_explain, ha sido clasificado como $target.
            >>> why = Why(language='es', local_reliability=local_reliability, local_feat_val_expl=local_feat_val_expl,
            ...           why_elements=why_elements, why_target=why_target, why_templates=why_templates,
            ...           n_local_features=2, n_global_features=2, min_reliability=0.0)
            >>> df_single_explanation = why.fit(sample_id_column='id', sample_id_value=5, template_index=1)
            >>> df_single_explanation
            'Por viajar en 1ª clase y pagar mucho por el billete, este caso ha sido clasificado como survivor, teniendo en cuenta que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> why.fit(sample_id_column='id', sample_id_value=5, template_index=2)
            >>> why.why_explanation
            'Por viajar en 1ª clase y pagar mucho por el billete, este caso ha sido clasificado como survivor, puesto que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> why.fit(sample_id_column='id', sample_id_value=5, template_index=3)
            >>> why.why_explanation
            'Este caso ha sido clasificado como survivor por viajar en 1ª clase y pagar mucho por el billete, ya que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> why.fit(sample_id_column='id', sample_id_value=5, template_index=4)
            >>> why.why_explanation
            'La clasificación de este caso como survivor se debe a viajar en 1ª clase y pagar mucho por el billete, ya que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> why.fit(sample_id_column='id', sample_id_value=5, template_index=5)
            >>> why.why_explanation
            'Como muchos viajaban en 1ª clase y pagaron mucho por el billete, y este caso se caracteriza por viajar en 1ª clase y pagar mucho por el billete, ha sido clasificado como survivor.'
            >>> why.fit(sample_id_column='id', sample_id_value=5, template_index='rand')
            >>> why.why_explanation
            'Por viajar en 1ª clase y pagar mucho por el billete, este caso ha sido clasificado como survivor, puesto que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> why.fit(sample_id_column='id', sample_id_value=62, template_index='rand')
            >>> why.why_explanation
            'Este caso ha sido clasificado como no_survivor por ser hombre y embarcar en un pueblo de clase baja, ya que han muerto muchos hombres y muchos embarcaron en southampton.'
            >>> why.fit(sample_id_column='id')
            >>> why.why_explanation
              id                                                                                                                                                                                     reason
            0  5        Como muchos viajaban en 1ª clase y pagaron mucho por el billete, y este caso se caracteriza por viajar en 1ª clase y pagar mucho por el billete, ha sido clasificado como survivor.
            1 62 Por embarcar en un pueblo de clase baja y ser hombre, este caso ha sido clasificado como no_survivor, teniendo en cuenta que muchos embarcaron en southampton y han muerto muchos hombres.

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
        """
        Builds and saves (when requested) the template files for semantic information; the resulting files must be
        filled up by the user and moved to the corresponding language folder.

        :param global_feat_val_expl: Pandas DataFrame containing, for each feature value and target pairs its importance
                                     and rank. The rank represents the importance of that feature value pair for the
                                     given target value
        :param destination_template_path: Path to save both: the element (feature-value) template file and the target
                                          template file in CSV format
        :param verbose: Verbosity level, where any value greater than 0 means the message is printed
        :return: List of two Pandas DataFrames, being the first one the element template data and the second one the
            target template data

        Example:
            >>> import pandas as pd
            >>> global_feat_val_expl = pd.DataFrame(
            ...    {
            ...        'target': ['survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor'],
            ...        'feature_value': ['fare_1.05', 'fare_0.05', 'age_0.05', 'family_size_10.00', 'family_size_7.00', 'family_size_4.00'],
            ...        'importance': [0.44, 0.394, 0.252, 0.233, 0.229, 0.209],
            ...        'rank': [1, 2, 3, 1, 2, 3]
            ...    },
            ...    columns=['target', 'feature_value', 'importance', 'rank']
            ... )
            >>> global_feat_val_expl
                   target     feature_value      importance rank
            0    survivor         fare_1.05           0.440    1
            1    survivor         fare_0.05           0.394    2
            2    survivor          age_0.05           0.252    3
            3 no_survivor family_size_10.00           0.233    1
            4 no_survivor  family_size_7.00           0.229    2
            5 no_survivor  family_size_4.00           0.209    3
            >>> element_template, target_template = Why.build_semantic_templates(global_feat_val_expl=global_feat_val_expl)
            >>> element_template
                  feature_value reason
            2          age_0.05
            3 family_size_10.00
            5  family_size_4.00
            4  family_size_7.00
            1         fare_0.05
            0         fare_1.05
            >>> target_template
                     target     feature_value reason
             6  no_survivor          age_0.05
             7  no_survivor family_size_10.00
             8  no_survivor  family_size_4.00
             9  no_survivor  family_size_7.00
            10  no_survivor         fare_0.05
            11  no_survivor         fare_1.05
             0     survivor          age_0.05
             1     survivor family_size_10.00
             2     survivor  family_size_4.00
             3     survivor  family_size_7.00
             4     survivor         fare_0.05
             5     survivor         fare_1.05
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
