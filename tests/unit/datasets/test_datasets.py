import pandas as pd
import unittest

from xaiographs.datasets.datasets import load_titanic, load_titanic_discretized, load_titanic_why, \
    FEATURE_COLS_TITANIC, TARGET_COLS_TITANIC, TARGET_COL, PREDICT_COL

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class DatasetsUnitTest(unittest.TestCase):

    @staticmethod
    def load_titanic_unit_test():
        """ Test: Method to load titanic dataset
        """
        df_expected = pd.DataFrame({'id': [0, 1, 2],
                                    'gender': ['female', 'male', 'female'],
                                    'title': ['Mrs', 'Mr', 'Mrs'],
                                    'age': [29.0, 0.9167, 2.0],
                                    'family_size': [0, 3, 3],
                                    'is_alone': [1, 0, 0],
                                    'embarked': ['S', 'S', 'S'],
                                    'class': [1, 1, 1],
                                    'ticket_price': [211.3375, 151.55, 151.55],
                                    'survived': [1, 1, 0]},
                                   columns=['id', 'gender', 'title', 'age', 'family_size', 'is_alone',
                                            'embarked', 'class', 'ticket_price', 'survived'])
        df_dataset = load_titanic()
        pd.testing.assert_frame_equal(df_dataset.head(3), df_expected)

    def load_titanic_discretized_unit_test(self):
        """ Test: Method to load titanic dataset discretized
        """
        df_expected = pd.DataFrame({'id': [0, 1, 2],
                                    'gender': ['female', 'male', 'female'],
                                    'title': ['Mrs', 'Mr', 'Mrs'],
                                    'age': ['18_30_years', '<12_years', '<12_years'],
                                    'family_size': ['1', '3-5', '3-5'],
                                    'is_alone': [1, 0, 0],
                                    'embarked': ['S', 'S', 'S'],
                                    'class': [1, 1, 1],
                                    'ticket_price': ['High', 'High', 'High'],
                                    'NO_SURVIVED': [0, 0, 1],
                                    'SURVIVED': [1, 1, 0],
                                    'y_true': ['SURVIVED', 'SURVIVED', 'NO_SURVIVED'],
                                    'y_predict': ['SURVIVED', 'SURVIVED', 'NO_SURVIVED']},
                                   columns=['id', 'gender', 'title', 'age', 'family_size', 'is_alone',
                                            'embarked', 'class', 'ticket_price', 'NO_SURVIVED', 'SURVIVED', 'y_true',
                                            'y_predict'])

        df_dataset, features_cols, target_cols, y_true, y_predict = load_titanic_discretized()

        pd.testing.assert_frame_equal(df_dataset.head(3), df_expected)
        self.assertListEqual(features_cols, FEATURE_COLS_TITANIC)
        self.assertListEqual(target_cols, TARGET_COLS_TITANIC)
        self.assertEqual(y_true, TARGET_COL)
        self.assertEqual(y_predict, PREDICT_COL)

    def load_titanic_why_unit_test(self):
        """ Test: Method to load titanic why templates
        """

        df_global_semantics_en_expected = (
            pd.DataFrame({'feature': ['gender_male', 'gender_female', 'is_alone_1'],
                          'reason': ['to be a man', 'to be a woman', 'travel alone']},
                         columns=['feature', 'reason']))

        df_global_semantics_es_expected = (
            pd.DataFrame({'feature': ['gender_male', 'gender_female', 'is_alone_1'],
                          'reason': ['ser hombre', 'ser mujer', 'viajar solo']},
                         columns=['feature', 'reason']))

        df_target_semantics_en_expected = (
            pd.DataFrame({'target': ['NO_SURVIVED', 'NO_SURVIVED', 'NO_SURVIVED'],
                          'feature': ['gender_male', 'gender_female', 'is_alone_1'],
                          'reason': ['many men have died', 'to be a woman', 'they traveled alone']},
                         columns=['target', 'feature', 'reason']))

        df_target_semantics_es_expected = (
            pd.DataFrame({'target': ['NO_SURVIVED', 'NO_SURVIVED', 'NO_SURVIVED'],
                          'feature': ['gender_male', 'gender_female', 'is_alone_1'],
                          'reason': ['han muerto muchos hombres', 'ser mujer', 'viajaban solos']},
                         columns=['target', 'feature', 'reason']))

        df_why_templates_en_expected = (
            pd.DataFrame([['An explanation cannot be offered for this case.'],
                          ['For $temp_local_explain, this case has been classified as $target, considering that $temp_global_explain.'],
                          ['For $temp_local_explain, this case has been classified as $target, because $temp_global_explain.']]))

        df_why_templates_es_expected = (
            pd.DataFrame([['No es posible ofrecer una explicación para este caso.'],
                          ['Por $temp_local_explain, este caso ha sido clasificado como $target, teniendo en cuenta que $temp_global_explain.'],
                          ['Por $temp_local_explain, este caso ha sido clasificado como $target, puesto que $temp_global_explain.']]))

        df_global_semantics, df_target_semantics, df_why_templates = load_titanic_why()
        df_global_semantics_en, df_target_semantics_en, df_why_templates_en = load_titanic_why(language='en')
        df_global_semantics_es, df_target_semantics_es, df_why_templates_es = load_titanic_why(language='es')
        df_global_semantics_err, df_target_semantics_err, df_why_templates_err = load_titanic_why(language='splunje')

        pd.testing.assert_frame_equal(df_global_semantics.head(3), df_global_semantics_en_expected)
        pd.testing.assert_frame_equal(df_global_semantics_en.head(3), df_global_semantics_en_expected)
        pd.testing.assert_frame_equal(df_global_semantics_es.head(3), df_global_semantics_es_expected)
        pd.testing.assert_frame_equal(df_global_semantics_err.head(3), df_global_semantics_en_expected)

        pd.testing.assert_frame_equal(df_target_semantics.head(3), df_target_semantics_en_expected)
        pd.testing.assert_frame_equal(df_target_semantics_en.head(3), df_target_semantics_en_expected)
        pd.testing.assert_frame_equal(df_target_semantics_es.head(3), df_target_semantics_es_expected)
        pd.testing.assert_frame_equal(df_target_semantics_err.head(3), df_target_semantics_en_expected)

        pd.testing.assert_frame_equal(df_why_templates.head(3), df_why_templates_en_expected)
        pd.testing.assert_frame_equal(df_why_templates_en.head(3), df_why_templates_en_expected)
        pd.testing.assert_frame_equal(df_why_templates_es.head(3), df_why_templates_es_expected)
        pd.testing.assert_frame_equal(df_why_templates_err.head(3), df_why_templates_en_expected)
