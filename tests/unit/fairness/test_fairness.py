import numpy as np
import pandas as pd
import unittest

from xaiographs.fairness.fairness import Fairness

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class FairnessUnitTest(unittest.TestCase):

    def setUp(self) -> None:
        # Definimos Dataset
        self.df_dataset = pd.DataFrame(
            {
                'Gender': ['MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN', 'MEN', 'MEN', 'WOMAN', 'MEN', 'WOMAN'],
                'Color': ['BLUE', 'BLUE', 'GREEN', 'BLUE', 'BLUE', 'GREEN', 'PINK', 'PINK', 'PINK', 'PINK'],
                'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
                'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
            columns=['Gender', 'Color', 'y_true', 'y_predict'])

    def check_dataset_values_unit_test(self):
        """
        """
        print("\nDataset to test:\n{}".format(self.df_dataset))
        # Column (sensitive_col) does not exist
        with self.assertRaises(AttributeError):
            Fairness._Fairness__check_dataset_values(df=self.df_dataset,
                                                     sensitive_col='SENSITIVE_COLUMN_NOT_EXIST',
                                                     target_col=None,
                                                     predict_col='y_predict',
                                                     target_label='YES',
                                                     sensitive_value='XXX')

        # Column (sensitive_col) does not exist
        with self.assertRaises(AttributeError):
            Fairness._Fairness__check_dataset_values(df=self.df_dataset,
                                                     sensitive_col='Gender',
                                                     target_col=None,
                                                     predict_col='PREDICT_COLUMN_NOT_EXIST',
                                                     target_label='XXX',
                                                     sensitive_value='MEN')

        # Column (target_col) does not exist
        with self.assertRaises(AttributeError):
            Fairness._Fairness__check_dataset_values(df=self.df_dataset,
                                                     sensitive_col='Gender',
                                                     target_col='TARGET_COLUMN_NOT_EXIST',
                                                     predict_col='y_predict',
                                                     target_label='YES',
                                                     sensitive_value='MEN')

        # target_label does not exist
        with self.assertRaises(KeyError):
            Fairness._Fairness__check_dataset_values(df=self.df_dataset,
                                                     sensitive_col='Gender',
                                                     target_col=None,
                                                     predict_col='y_predict',
                                                     target_label='ERROR_TARGET_LABEL',
                                                     sensitive_value='MEN')

        # sensitive_value does not exist
        with self.assertRaises(KeyError):
            Fairness._Fairness__check_dataset_values(df=self.df_dataset,
                                                     sensitive_col='Gender',
                                                     target_col=None,
                                                     predict_col='y_predict',
                                                     target_label='YES',
                                                     sensitive_value='ERROR_SENSITIVE_VALUE')

    def fit_independence_unit_test(self):
        """ Test: Calculate Independence Criteria for 'Gender' sensitive Feature and Prediction value equals as 1.

        A-> sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        independence score = | P(Y=1∣T=1,A=a) - P(Y=1∣T=1,A=b) |

        P(Y = 'YES' | A = 'MEN') = 4 / 6 = 0.66
        P(Y = 'YES' | A = 'WOMAN') = 1 / 4 = 0.25
        independence score = |0.66 - 0.25| = 0.41
        """
        print("\nDataset to test:\n{}".format(self.df_dataset))

        # Independence Score Calculation OK
        f = Fairness(destination_path='./')
        independence_value_ok = f.fit_independence(df=self.df_dataset,
                                                   sensitive_col='Gender',
                                                   predict_col='y_predict',
                                                   target_label='YES',
                                                   sensitive_value='MEN')
        assert round(independence_value_ok, 4) == 0.4167

    def fit_separation_unit_test(self):
        """ Test: Calculate Separation Criteria for 'Gender' sensitive Feature and Prediction value equals as 1.

        A-> sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        separation score = | P(Y=1∣T=1,A=a) - P(Y=1∣T=1,A=b) |

        P(Y = 'YES' | T = 'YES', A = 'MEN') = 3 / 4 = 0.75
        P(Y = 'YES' | T = 'YES', A = 'WOMAN') = 1 / 2 = 0.5
        separation score = |0.75 - 0.5| = 0.25
        """
        # Independence Score Calculation OK
        f = Fairness(destination_path='./')
        separation_value = f.fit_separation(df=self.df_dataset,
                                            sensitive_col='Gender',
                                            target_col='y_true',
                                            predict_col='y_predict',
                                            target_label='YES',
                                            sensitive_value='MEN')
        assert round(separation_value, 2) == 0.25

    def fit_sufficiency_unit_test(self):
        """ Test: Calculate Separation Criteria for 'Gender' sensitive Feature and Prediction value equals as 1.

        A-> sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        sufficiency score = | P(T=1∣Y=1,A=a) - P(T=1∣Y=1,A=b) |

        P(T = 'YES' | Y = 'YES', A = 'MEN') = 3 / 4 = 0.75
        P(T = 'YES' | Y = 'YES', A = 'WOMAN') = 1 / 1 = 1.0
        sufficiency score = |0.75 - 1.0| = 0.25
        """
        print("\nDataset to test:\n{}".format(self.df_dataset))

        # Independence Score Calculation OK
        f = Fairness(destination_path='./')
        sufficiency_value = f.fit_sufficiency(df=self.df_dataset,
                                              sensitive_col='Gender',
                                              target_col='y_true',
                                              predict_col='y_predict',
                                              target_label='YES',
                                              sensitive_value='MEN')
        assert round(sufficiency_value, 2) == 0.25

    def fit_fairness_metrics_unit_test(self):
        """ Test: Calculate Independence, Separation and Sufficiency Criterias for 'Gender' sensitive Feature
        and Prediction value equals as 1.

        A-> sensitive Feature
        Y-> y_predict (Prediction)
        T-> y_true (Target)
        ==============================================================
        independence score = | P(Y=1∣T=1,A=a) - P(Y=1∣T=1,A=b) |
        P(Y = 'YES' | A = 'MEN') = 4 / 6 = 0.66
        P(Y = 'YES' | A = 'WOMAN') = 1 / 4 = 0.25
        independence score = |0.66 - 0.25| = 0.41
        ==============================================================
        separation score = | P(Y=1∣T=1,A=a) - P(Y=1∣T=1,A=b) |
        P(Y = 'YES' | T = 'YES', A = 'MEN') = 3 / 4 = 0.75
        P(Y = 'YES' | T = 'YES', A = 'WOMAN') = 1 / 2 = 0.5
        separation score = |0.75 - 0.5| = 0.25
        ==============================================================
        sufficiency score = | P(T=1∣Y=1,A=a) - P(T=1∣Y=1,A=b) |
        P(T = 'YES' | Y = 'YES', A = 'MEN') = 3 / 4 = 0.75
        P(T = 'YES' | Y = 'YES', A = 'WOMAN') = 1 / 1 = 1.0
        sufficiency score = |0.75 - 1.0| = 0.25
        ==============================================================
        """
        print("\nDataset to test:\n{}".format(self.df_dataset))

        # Independence Score Calculation OK
        f = Fairness(destination_path='./')
        fairness_scores = f.fit_fairness_metrics(df=self.df_dataset,
                                                 sensitive_col='Gender',
                                                 target_col='y_true',
                                                 predict_col='y_predict',
                                                 target_label='YES',
                                                 sensitive_value='MEN')
        assert round(fairness_scores[0], 2) == 0.42
        assert round(fairness_scores[1], 2) == 0.25
        assert round(fairness_scores[2], 2) == 0.25

    def get_fairness_category_unit_test(self):
        """ Test: Calculate Fairness Category based on Score Category:
        A+ : score <= 0.02
        A  : 0.02 < score <= 0.05
        B  : 0.05 < score <= 0.08
        C  : 0.08 < score <= 0.15
        D  : 0.15 < score <= 0.25
        E  : 0.25 < score <= 1.0
        """
        assert Fairness.get_fairness_category(score=0.01) == 'A+'
        assert Fairness.get_fairness_category(score=0.02) == 'A+'
        assert Fairness.get_fairness_category(score=0.02000001) == 'A'
        assert Fairness.get_fairness_category(score=0.04) == 'A'
        assert Fairness.get_fairness_category(score=0.05) == 'A'
        assert Fairness.get_fairness_category(score=0.05000001) == 'B'
        assert Fairness.get_fairness_category(score=0.07) == 'B'
        assert Fairness.get_fairness_category(score=0.08) == 'B'
        assert Fairness.get_fairness_category(score=0.08000001) == 'C'
        assert Fairness.get_fairness_category(score=0.1) == 'C'
        assert Fairness.get_fairness_category(score=0.15) == 'C'
        assert Fairness.get_fairness_category(score=0.15000001) == 'D'
        assert Fairness.get_fairness_category(score=0.2) == 'D'
        assert Fairness.get_fairness_category(score=0.25) == 'D'
        assert Fairness.get_fairness_category(score=0.25000001) == 'E'
        assert Fairness.get_fairness_category(score=0.5) == 'E'
        assert Fairness.get_fairness_category(score=1.0) == 'E'
        assert Fairness.get_fairness_category(score=1000) == 'E'

    def encoder_dataset_unit_test(self):
        """ Test: Method to encoder not numeric features
        """
        df_expected = pd.DataFrame({'Gender': [0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
                                    'Color': [0, 0, 1, 0, 0, 1, 2, 2, 2, 2],
                                    'y_true': [1, 1, 0, 0, 1, 1, 1, 1, 0, 0],
                                    'y_predict': [1, 1, 0, 1, 0, 0, 1, 1, 0, 0]},
                                   columns=['Gender', 'Color', 'y_true', 'y_predict'],
                                   dtype='int64')

        df = Fairness._Fairness__encoder_dataset(df=self.df_dataset).astype(np.int64)

        print("\nDataset to Encoder:\n{}".format(self.df_dataset.head(5)))
        print("encoder_dataset_unit_test -> Result DataFrame:\n{}".format(df.head(5)))
        print("encoder_dataset_unit_test -> Expected DataFrame:\n{}".format(df_expected.head(5)))

        pd.testing.assert_frame_equal(df, df_expected)

    def fit_correlation_features_unit_test(self):
        """ Test: Method to calculate matrix correlation features (upper triangular matrix)
        """
        df_expected = pd.DataFrame({'Gender': [float('NaN'), float('NaN')],
                                    'Gender2': [1.0, float('NaN')]},
                                   columns=['Gender', 'Gender2'],
                                   index=['Gender', 'Gender2'],
                                   dtype='float64')

        # Copy 'Gender' column to obtain correlation '1'
        self.df_dataset['Gender2'] = self.df_dataset['Gender']
        print("\nDataset to test:\n{}".format(self.df_dataset[['Gender', 'Gender2']]))

        f = Fairness(destination_path='./')
        f._Fairness__fit_correlation_features(df=self.df_dataset[['Gender', 'Gender2']])

        print("fit_correlation_features_unit_test -> Result DataFrame:\n{}".format(f.correlation_matrix))
        print("fit_correlation_features_unit_test -> Expected DataFrame:\n{}".format(df_expected))

        pd.testing.assert_frame_equal(f.correlation_matrix, df_expected)

    @staticmethod
    def find_highest_correlation_features_unit_test():
        """ Test: Method that finds pairs of features that have a correlation greater than a threshold
        """
        df_test = pd.DataFrame({'F1': [float('NaN'), float('NaN'), float('NaN')],
                                'F2': [0.91, float('NaN'), float('NaN')],
                                'F3': [0.11, 0.22, float('NaN')]},
                               columns=['F1', 'F2', 'F3'],
                               index=['F1', 'F2', 'F3'],
                               dtype='float64')
        df_expected = pd.DataFrame({'feature_1': ['F2'],
                                    'feature_2': ['F1'],
                                    'correlation_value': [0.91],
                                    'is_correlation_sensible': [True]},
                                   columns=['feature_1', 'feature_2', 'correlation_value', 'is_correlation_sensible'])

        f = Fairness(destination_path='./')
        print("CASE 1: There are 1 highest pair correlation features")
        f._Fairness__find_highest_correlation_features(df_correlations=df_test,
                                                       threshold=0.9,
                                                       sensitive_cols=['F1'])
        print("find_highest_correlation_features_unit_test -> Result DataFrame:\n{}"
              .format(f.highest_correlation_features))
        print("find_highest_correlation_features_unit_test -> Expected DataFrame:\n{}\n"
              .format(df_expected))
        pd.testing.assert_frame_equal(f.highest_correlation_features, df_expected)

        print("CASE 2: There are no highest correlation features")
        f = Fairness(destination_path='./')
        f._Fairness__find_highest_correlation_features(df_correlations=df_test,
                                                       threshold=0.95,
                                                       sensitive_cols=['F1'])
        print("find_highest_correlation_features_unit_test -> Result DataFrame:\n{}"
              .format(f.highest_correlation_features))
        assert f.highest_correlation_features.shape[0] == 0

    def in_processing_unit_test(self):
        """ Test: Method to encoder not numeric features
        """
        f = Fairness(destination_path='./')
        f._Fairness__pre_processing(df=self.df_dataset,
                                    sensitive_cols=['Gender', 'Color'],
                                    target_col='y_true',
                                    predict_col='y_predict')
        f._Fairness__in_processing(df=self.df_dataset,
                                   sensitive_cols=['Gender', 'Color'],
                                   target_col='y_true',
                                   predict_col='y_predict')
