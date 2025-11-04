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


import pandas as pd
import unittest

from xaiographs.datasets.datasets import load_titanic, load_titanic_discretized, load_titanic_why, \
    FEATURE_COLS_TITANIC, TARGET_COLS_TITANIC, TARGET_COL, PREDICT_COL

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class DatasetsUnitTest(unittest.TestCase):

    @staticmethod
    def test_load_titanic():
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

    def test_load_titanic_discretized(self):
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
                                    'SURVIVED': [1, 1, 0],
                                    'NO_SURVIVED': [0, 0, 1],
                                    'y_true': ['SURVIVED', 'SURVIVED', 'NO_SURVIVED'],
                                    'y_predict': ['SURVIVED', 'SURVIVED', 'NO_SURVIVED']},
                                   columns=['id', 'gender', 'title', 'age', 'family_size', 'is_alone',
                                            'embarked', 'class', 'ticket_price', 'SURVIVED', 'NO_SURVIVED', 'y_true',
                                            'y_predict'])

        df_dataset, features_cols, target_cols, y_true, y_predict = load_titanic_discretized()

        pd.testing.assert_frame_equal(df_dataset.head(3), df_expected)
        self.assertListEqual(features_cols, FEATURE_COLS_TITANIC)
        self.assertListEqual(target_cols, TARGET_COLS_TITANIC)
        self.assertEqual(y_true, TARGET_COL)
        self.assertEqual(y_predict, PREDICT_COL)
