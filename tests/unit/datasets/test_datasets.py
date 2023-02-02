import pandas as pd
import unittest

from xaiographs.datasets.datasets import load_titanic, load_titanic_discretized, FEATURE_COLS_TITANIC, \
    TARGET_COLS_TITANIC, TARGET_COL, PREDICT_COL

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class DatasetsUnitTest(unittest.TestCase):

    @staticmethod
    def load_titanic_unit_test():
        """ Test: Method to load titanic dataset
        """
        df_expected = pd.DataFrame({'passenger_id': [0, 1, 2],
                                    'gender': ['female', 'male', 'female'],
                                    'title': ['Mrs', 'Mr', 'Mrs'],
                                    'age': [29.0, 0.9167, 2.0],
                                    'family_size': [0, 3, 3],
                                    'is_alone': [1, 0, 0],
                                    'embarked': ['S', 'S', 'S'],
                                    'class': [1, 1, 1],
                                    'ticket_price': [211.3375, 151.55, 151.55],
                                    'survived': [1, 1, 0]},
                                   columns=['passenger_id', 'gender', 'title', 'age', 'family_size', 'is_alone',
                                            'embarked', 'class', 'ticket_price', 'survived'])
        df_dataset = load_titanic()
        pd.testing.assert_frame_equal(df_dataset.head(3), df_expected)

    def load_titanic_discretized_unit_test(self):
        """ Test: Method to load titanic dataset discretized
        """
        df_expected = pd.DataFrame({'passenger_id': [0, 1, 2],
                                    'gender': ['female', 'male', 'female'],
                                    'title': ['Mrs', 'Mr', 'Mrs'],
                                    'age': ['18_30_years', '<12_years', '<12_years'],
                                    'family_size': ['=1', '3-5', '3-5'],
                                    'is_alone': [1, 0, 0],
                                    'embarked': ['S', 'S', 'S'],
                                    'class': [1, 1, 1],
                                    'ticket_price': ['High', 'High', 'High'],
                                    'NO_SURVIVED': [0, 0, 1],
                                    'SURVIVED': [1, 1, 0],
                                    'y_true': [1, 1, 0],
                                    'y_predict': [1, 1, 0]},
                                   columns=['passenger_id', 'gender', 'title', 'age', 'family_size', 'is_alone',
                                            'embarked', 'class', 'ticket_price', 'NO_SURVIVED', 'SURVIVED', 'y_true',
                                            'y_predict'])

        df_dataset, features_cols, target_cols, y_true, y_predict = load_titanic_discretized()

        pd.testing.assert_frame_equal(df_dataset.head(3), df_expected)
        self.assertListEqual(features_cols, FEATURE_COLS_TITANIC)
        self.assertListEqual(target_cols, TARGET_COLS_TITANIC)
        self.assertEqual(y_true, TARGET_COL)
        self.assertEqual(y_predict, PREDICT_COL)

