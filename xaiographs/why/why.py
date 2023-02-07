import pandas as pd
import random

from string import Template
from typing import Any, List, Optional, Tuple, Union

from xaiographs.common.constants import COMMA_SEP, FEATURE, LANG_EN, LANG_ES, NODE_IMPORTANCE, NODE_NAME
from xaiographs.common.constants import RELIABILITY, RAND, RANK, REASON, TARGET


class Why(object):
    """
    Main class to provide an explanation on why a given case has been assigned a label (target value), combining
    the local reason (case-specific), the global reason (model-specific) and the target itself.

    Example:
        >>> import pandas as pd
        >>> local_expl = pd.DataFrame(
        ...    {
        ...        'id': [5, 62],
        ...        'age': [0.016, 0.086],
        ...        'fare': [0.146, -0.001],
        ...        'family_size': [0.08, -0.058],
        ...        'embarked': [0.059, 0.099],
        ...        'sex': [0.023, 0.155],
        ...        'pclass': [0.195, -0.081],
        ...        'title': [0.006, 0.163],
        ...        'is_alone': [0.099, 0.014],
        ...        'target': ['survivor', 'no_survivor'],
        ...    },
        ...    columns=['id', 'age', 'fare', 'family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone', 'target']
        ... )
        >>> local_expl
            id   age   fare family_size embarked   sex pclass title is_alone      target
         0   5 0.016  0.146       0.080    0.059 0.023  0.195 0.006    0.099    survivor
         1  62 0.086 -0.001      -0.058    0.099 0.155 -0.081 0.163    0.014 no_survivor
        >>> local_nodes = pd.DataFrame(
        ...    {
        ...        'id': [5, 5, 5, 5, 5, 5, 5, 5, 62, 62, 62, 62, 62, 62, 62, 62],
        ...        'node_name': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'family_size_0.00', 'embarked_S', 'sex_male', 'age_0.95', 'title_Mr', 'title_Mr', 'sex_male', 'embarked_S', 'age_0.95', 'is_alone_1.00', 'fare_0.95', 'family_size_1.00', 'pclass_1.00'],
        ...        'node_importance': [0.195, 0.146, 0.099, 0.08, 0.059, 0.023, 0.016, 0.006, 0.163, 0.155, 0.099, 0.086, 0.014, -0.001, -0.058, -0.081],
        ...        'node_weight': [25, 20, 15, 15, 15, 10, 10, 10, 25, 20, 15, 15, 10, 10, 15, 15],
        ...        'rank': [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8],
        ...        'target': ['survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor']
        ...    },
        ...    columns=['id', 'node_name', 'node_importance', 'node_weight', 'rank', 'target']
        ... )
        >>> local_nodes
           id        node_name node_importance node_weight rank      target
         0  5      pclass_1.00           0.195          25    1    survivor
         1  5        fare_0.75           0.146          20    2    survivor
         2  5    is_alone_1.00           0.099          15    3    survivor
         3  5 family_size_0.00           0.080          15    4    survivor
         4  5       embarked_S           0.059          15    5    survivor
         5  5         sex_male           0.023          10    6    survivor
         6  5         age_0.95           0.016          10    7    survivor
         7  5         title_Mr           0.006          10    8    survivor
         8 62         title_Mr           0.163          25    1 no_survivor
         9 62         sex_male           0.155          20    2 no_survivor
        10 62       embarked_S           0.099          15    3 no_survivor
        11 62         age_0.95           0.086          15    4 no_survivor
        12 62    is_alone_1.00           0.014          10    5 no_survivor
        13 62        fare_0.95          -0.001          10    6 no_survivor
        14 62 family_size_1.00          -0.058          15    7 no_survivor
        15 62      pclass_1.00          -0.081          15    8 no_survivor
        >>> reliability = pd.DataFrame(
        ...    {
        ...        'id': [5, 62],
        ...        'age': [0.95, 0.95],
        ...        'fare': [0.75, 0.95],
        ...        'family_size': [0.0, 1.0],
        ...        'embarked': ['S', 'S'],
        ...        'sex': ['male', 'male'],
        ...        'pclass': [1.0, 1.0],
        ...        'title': ['Mr', 'Mr'],
        ...        'is_alone': [1.0, 1.0],
        ...        'target': ['survivor', 'no_survivor'],
        ...        'reliability': [0.14, 1.0]
        ...    },
        ...    columns = ['id', 'age', 'fare', 'family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone', 'target', 'reliability']
        ... )
        >>> reliability
          id  age fare family_size embarked  sex pclass title is_alone      target reliability
        0  5 0.95 0.75         0.0        S male    1.0    Mr      1.0    survivor        0.14
        1 62 0.95 0.95         1.0        S male    1.0    Mr      1.0 no_survivor        1.00
        >>> why_elements = pd.DataFrame(
        ...    {
        ...        'feature': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'sex_male', 'embarked_S', 'age_0.95'],
        ...        'reason': ['viajar en 1ª clase', 'pagar mucho por el billete', 'viajar solo', 'ser hombre', 'embarcar en un pueblo de clase baja', 'ser una persona muy mayor']
        ...    },
        ...    columns = ['feature', 'reason']
        ... )
        >>> why_elements
                feature                              reason
        0   pclass_1.00                  viajar en 1ª clase
        1     fare_0.75          pagar mucho por el billete
        2 is_alone_1.00                         viajar solo
        3      sex_male                          ser hombre
        4    embarked_S embarcar en un pueblo de clase baja
        5      age_0.95           ser una persona muy mayor
        >>> why_target = pd.DataFrame(
        ...    {
        ...        'target': ['survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor'],
        ...        'feature': ['embarked_S', 'pclass_1.00', 'fare_0.75', 'sex_male', 'embarked_S', 'age_0.95'],
        ...        'reason': ['pocos embarcaron en Southampton', 'muchos viajaban en 1ª clase', 'pagaron mucho por el billete', 'han muerto muchos hombres', 'muchos embarcaron en Southampton', 'eran muy mayores']
        ...    },
        ...    columns = ['target', 'feature', 'reason']
        ... )
        >>> why_target
               target     feature                           reason
        0    survivor  embarked_S  pocos embarcaron en Southampton
        1    survivor pclass_1.00      muchos viajaban en 1ª clase
        2    survivor   fare_0.75     pagaron mucho por el billete
        3 no_survivor    sex_male        han muerto muchos hombres
        4 no_survivor  embarked_S muchos embarcaron en Southampton
        5 no_survivor    age_0.95                 eran muy mayores
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
        >>> why = Why(language='es', local_expl=local_expl, local_nodes=local_nodes, why_elements=why_elements,
        ...           why_target=why_target, why_templates=why_templates, reliability=reliability, n_local_features=2,
        ...           n_global_features=2, min_reliability=0.0)
        >>> why.language
        'es'
    """

    _LOCAL = 'local'
    _GLOBAL = 'global'
    _SEP_LAST = {
        LANG_ES: ' y ',
        LANG_EN: ' and '
    }

    def __init__(self, language: str, local_expl: pd.DataFrame, local_nodes: pd.DataFrame, why_elements: pd.DataFrame,
                 why_target: pd.DataFrame, why_templates: pd.DataFrame, reliability: pd.DataFrame,
                 n_local_features: int = 2, n_global_features: int = 2, min_reliability: float = 0.0,
                 verbose: int = 0):
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
        :param reliability: Pandas DataFrame with the reliability (a kind of confidence level) for each case
        :param n_local_features: Number of local features to take into account for the explanation
        :param n_global_features: Number of global features to take into account for the explanation
        :param min_reliability: Minimum reliability value to give an explanation; for the cases with an associated
            reliability below this value, a default sentence will be provided
        :param verbose: Verbosity level, where any value greater than 0 means the message is printed
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
        self.reliability = reliability
        self.n_local_features = n_local_features
        self.n_global_features = n_global_features
        self.min_reliability = min_reliability
        self.verbose = verbose

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

        Example:
            >>> import pandas as pd
            >>> local_expl = pd.DataFrame(
            ...    {
            ...        'id': [5, 62],
            ...        'age': [0.016, 0.086],
            ...        'fare': [0.146, -0.001],
            ...        'family_size': [0.08, -0.058],
            ...        'embarked': [0.059, 0.099],
            ...        'sex': [0.023, 0.155],
            ...        'pclass': [0.195, -0.081],
            ...        'title': [0.006, 0.163],
            ...        'is_alone': [0.099, 0.014],
            ...        'target': ['survivor', 'no_survivor']
            ...    },
            ...    columns=['id', 'age', 'fare', 'family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone', 'target']
            ... )
            >>> local_expl
                id   age   fare family_size embarked   sex pclass title is_alone      target
             0   5 0.016  0.146       0.080    0.059 0.023  0.195 0.006    0.099    survivor
             1  62 0.086 -0.001      -0.058    0.099 0.155 -0.081 0.163    0.014 no_survivor
            >>> local_nodes = pd.DataFrame(
            ...    {
            ...        'id': [5, 5, 5, 5, 5, 5, 5, 5, 62, 62, 62, 62, 62, 62, 62, 62],
            ...        'node_name': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'family_size_0.00', 'embarked_S', 'sex_male', 'age_0.95', 'title_Mr', 'title_Mr', 'sex_male', 'embarked_S', 'age_0.95', 'is_alone_1.00', 'fare_0.95', 'family_size_1.00', 'pclass_1.00'],
            ...        'node_importance': [0.195, 0.146, 0.099, 0.08, 0.059, 0.023, 0.016, 0.006, 0.163, 0.155, 0.099, 0.086, 0.014, -0.001, -0.058, -0.081],
            ...        'node_weight': [25, 20, 15, 15, 15, 10, 10, 10, 25, 20, 15, 15, 10, 10, 15, 15],
            ...        'rank': [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8],
            ...        'target': ['survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor', 'no_survivor']
            ...    },
            ...    columns=['id', 'node_name', 'node_importance', 'node_weight', 'rank', 'target']
            ... )
            >>> local_nodes
               id        node_name node_importance node_weight rank      target
             0  5      pclass_1.00           0.195          25    1    survivor
             1  5        fare_0.75           0.146          20    2    survivor
             2  5    is_alone_1.00           0.099          15    3    survivor
             3  5 family_size_0.00           0.080          15    4    survivor
             4  5       embarked_S           0.059          15    5    survivor
             5  5         sex_male           0.023          10    6    survivor
             6  5         age_0.95           0.016          10    7    survivor
             7  5         title_Mr           0.006          10    8    survivor
             8 62         title_Mr           0.163          25    1 no_survivor
             9 62         sex_male           0.155          20    2 no_survivor
            10 62       embarked_S           0.099          15    3 no_survivor
            11 62         age_0.95           0.086          15    4 no_survivor
            12 62    is_alone_1.00           0.014          10    5 no_survivor
            13 62        fare_0.95          -0.001          10    6 no_survivor
            14 62 family_size_1.00          -0.058          15    7 no_survivor
            15 62      pclass_1.00          -0.081          15    8 no_survivor
            >>> reliability = pd.DataFrame(
            ...    {
            ...        'id': [5, 62],
            ...        'age': [0.95, 0.95],
            ...        'fare': [0.75, 0.95],
            ...        'family_size': [0.0, 1.0],
            ...        'embarked': ['S', 'S'],
            ...        'sex': ['male', 'male'],
            ...        'pclass': [1.0, 1.0],
            ...        'title': ['Mr', 'Mr'],
            ...        'is_alone': [1.0, 1.0],
            ...        'target': ['survivor', 'no_survivor'],
            ...        'reliability': [0.14, 1.0]
            ...    },
            ...    columns = ['id', 'age', 'fare', 'family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone', 'target', 'reliability']
            ... )
            >>> reliability
              id  age fare family_size embarked  sex pclass title is_alone      target reliability
            0  5 0.95 0.75         0.0        S male    1.0    Mr      1.0    survivor        0.14
            1 62 0.95 0.95         1.0        S male    1.0    Mr      1.0 no_survivor        1.00
            >>> why_elements = pd.DataFrame(
            ...    {
            ...        'feature': ['pclass_1.00', 'fare_0.75', 'is_alone_1.00', 'sex_male', 'embarked_S', 'age_0.95'],
            ...        'reason': ['viajar en 1ª clase', 'pagar mucho por el billete', 'viajar solo', 'ser hombre', 'embarcar en un pueblo de clase baja', 'ser una persona muy mayor']
            ...    },
            ...    columns = ['feature', 'reason']
            ... )
            >>> why_elements
                    feature                              reason
            0   pclass_1.00                  viajar en 1ª clase
            1     fare_0.75          pagar mucho por el billete
            2 is_alone_1.00                         viajar solo
            3      sex_male                          ser hombre
            4    embarked_S embarcar en un pueblo de clase baja
            5      age_0.95           ser una persona muy mayor
            >>> why_target = pd.DataFrame(
            ...    {
            ...        'target': ['survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor'],
            ...        'feature': ['embarked_S', 'pclass_1.00', 'fare_0.75', 'sex_male', 'embarked_S', 'age_0.95'],
            ...        'reason': ['pocos embarcaron en Southampton', 'muchos viajaban en 1ª clase', 'pagaron mucho por el billete', 'han muerto muchos hombres', 'muchos embarcaron en Southampton', 'eran muy mayores']
            ...    },
            ...    columns = ['target', 'feature', 'reason']
            ... )
            >>> why_target
                   target     feature                           reason
            0    survivor  embarked_S  pocos embarcaron en Southampton
            1    survivor pclass_1.00      muchos viajaban en 1ª clase
            2    survivor   fare_0.75     pagaron mucho por el billete
            3 no_survivor    sex_male        han muerto muchos hombres
            4 no_survivor  embarked_S muchos embarcaron en Southampton
            5 no_survivor    age_0.95                 eran muy mayores
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
            >>> why = Why(language='es', local_expl=local_expl, local_nodes=local_nodes, why_elements=why_elements,
            ...           why_target=why_target, why_templates=why_templates, reliability=reliability, n_local_features=2,
            ...           n_global_features=2, min_reliability=0.0)
            >>> df_single_explanation = why.build_why(key_column='id', key_value=5, template_index=1)
            >>> df_single_explanation
            'Por viajar en 1ª clase y pagar mucho por el billete, este caso ha sido clasificado como survivor, teniendo en cuenta que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> df_single_explanation = why.build_why(key_column='id', key_value=5, template_index=2)
            >>> df_single_explanation
            'Por viajar en 1ª clase y pagar mucho por el billete, este caso ha sido clasificado como survivor, puesto que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> df_single_explanation = why.build_why(key_column='id', key_value=5, template_index=3)
            >>> df_single_explanation
            'Este caso ha sido clasificado como survivor por viajar en 1ª clase y pagar mucho por el billete, ya que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> df_single_explanation = why.build_why(key_column='id', key_value=5, template_index=4)
            >>> df_single_explanation
            'La clasificación de este caso como survivor se debe a viajar en 1ª clase y pagar mucho por el billete, ya que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> df_single_explanation = why.build_why(key_column='id', key_value=5, template_index=5)
            >>> df_single_explanation
            'Como muchos viajaban en 1ª clase y pagaron mucho por el billete, y este caso se caracteriza por viajar en 1ª clase y pagar mucho por el billete, ha sido clasificado como survivor.'
            >>> df_single_explanation = why.build_why(key_column='id', key_value=5, template_index='rand')
            >>> df_single_explanation
            'Por viajar en 1ª clase y pagar mucho por el billete, este caso ha sido clasificado como survivor, puesto que muchos viajaban en 1ª clase y pagaron mucho por el billete.'
            >>> df_single_explanation = why.build_why(key_column='id', key_value=62, template_index='rand')
            >>> df_single_explanation
            'Este caso ha sido clasificado como no_survivor por ser hombre y embarcar en un pueblo de clase baja, ya que han muerto muchos hombres y muchos embarcaron en southampton.'
            >>> df_why = why.build_why(key_column='id')
            >>> df_why
              id                                                                                                                                                                                     reason
            0  5        Como muchos viajaban en 1ª clase y pagaron mucho por el billete, y este caso se caracteriza por viajar en 1ª clase y pagar mucho por el billete, ha sido clasificado como survivor.
            1 62 Por embarcar en un pueblo de clase baja y ser hombre, este caso ha sido clasificado como no_survivor, teniendo en cuenta que muchos embarcaron en southampton y han muerto muchos hombres.

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
              .merge(self.reliability[[key_column, RELIABILITY]], on=key_column, how='left'))
        df[RANK] = df.groupby(key_column)[NODE_IMPORTANCE].rank(method='dense', ascending=False).astype(int)

        max_n_features = max(self.n_local_features, self.n_global_features)
        df_rank = df[df[RANK] <= max_n_features]

        def get_single_why(df_single: pd.DataFrame) -> str:
            """
            Builds a sentence with the reason why a single case has been assigned a label

            :param df_single: Pandas DataFrame with the nodes associated to the selected case
            :return: String with the final sentence for the requested case
            """
            # Check the reliability of the explainability values
            r = df_single.head(1)
            reliability = r[RELIABILITY].values[0]
            if reliability < self.min_reliability:
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

    @staticmethod
    def build_semantic_templates(global_nodes: pd.DataFrame, save_path_element: Optional[str] = None,
                                 save_path_target: Optional[str] = None,
                                 sep: Optional[str] = COMMA_SEP) -> List[pd.DataFrame]:
        """
        Builds and saves (when requested) the template files for semantic information; the resulting files must be
        filled up by the user and moved to the corresponding language folder.

        :param global_nodes: Pandas DataFrame with the global nodes' explainability
        :param save_path_element: Path to save the element template file in CSV format
        :param save_path_target: Path to save the target template file in CSV format
        :param sep: Separator string
        :return: List of two Pandas DataFrames, being the first one the element template data and the second one the
            target template data

        Example:
            >>> import pandas as pd
            >>> global_nodes = pd.DataFrame(
            ...    {
            ...        'target': ['survivor', 'survivor', 'survivor', 'no_survivor', 'no_survivor', 'no_survivor'],
            ...        'node_name': ['fare_1.05', 'fare_0.05', 'age_0.05', 'family_size_10.00', 'family_size_7.00', 'family_size_4.00'],
            ...        'node_importance': [0.44, 0.394, 0.252, 0.233, 0.229, 0.209],
            ...        'node_weight': [50, 50, 30, 30, 30, 30],
            ...        'rank': [1, 2, 3, 1, 2, 3],
            ...        'node_count': [4, 18, 66, 11, 8, 22],
            ...        'total_count': [1309, 1309, 1309, 1309, 1309, 1309],
            ...        'node_name_ratio': [0.003, 0.014, 0.05, 0.008, 0.006, 0.017],
            ...        'node_name_ratio_weight': [10, 10, 10, 10, 10, 10],
            ...        'node_name_ratio_rank': [43, 38, 32, 40, 42, 37]
            ...    },
            ...    columns=['target', 'node_name', 'node_importance', 'node_weight', 'rank', 'node_count', 'total_count', 'node_name_ratio', 'node_name_ratio_weight', 'node_name_ratio_rank']
            ... )
            >>> global_nodes
                   target         node_name node_importance node_weight rank node_count total_count node_name_ratio node_name_ratio_weight node_name_ratio_rank
            0    survivor         fare_1.05           0.440          50    1          4        1309           0.003                     10                   43
            1    survivor         fare_0.05           0.394          50    2         18        1309           0.014                     10                   38
            2    survivor          age_0.05           0.252          30    3         66        1309           0.050                     10                   32
            3 no_survivor family_size_10.00           0.233          30    1         11        1309           0.008                     10                   40
            4 no_survivor  family_size_7.00           0.229          30    2          8        1309           0.006                     10                   42
            5 no_survivor  family_size_4.00           0.209          30    3         22        1309           0.017                     10                   37
            >>> element_template, target_template = Why.build_semantic_templates(global_nodes=global_nodes)
            >>> element_template
                        feature reason
            2          age_0.05
            3 family_size_10.00
            5  family_size_4.00
            4  family_size_7.00
            1         fare_0.05
            0         fare_1.05
            >>> target_template
                     target           feature reason
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
        # Build element template DataFrame
        df_element = (global_nodes[[NODE_NAME]]
                      .rename(columns={NODE_NAME: FEATURE})
                      .drop_duplicates()
                      .sort_values(by=FEATURE))
        df_element[REASON] = ''

        # Build target template DataFrame
        df_target = (global_nodes[[TARGET]]
                     .drop_duplicates()
                     .merge(df_element, how='cross')
                     .sort_values(by=[TARGET, FEATURE]))

        # Save to CSV if requested
        if save_path_element is not None:
            df_element.to_csv(path_or_buf=save_path_element, index=False, sep=sep)
        if save_path_target is not None:
            df_target.to_csv(path_or_buf=save_path_target, index=False, sep=sep)

        return [df_element, df_target]
