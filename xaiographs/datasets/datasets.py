import os
from typing import List, Tuple

import pandas as pd

# Titanic Dataset
TITANIC_PATH = 'data/titanic.csv'
TITANIC_DISCRETIZED_PATH = 'data/titanic_discretized.csv'
FEATURE_COLS_TITANIC = ['gender', 'title', 'age', 'family_size', 'is_alone', 'embarked', 'pclass', 'ticket_price']
TARGET_COLS_TITANIC = ['NO_SURVIVED', 'SURVIVED']

# All datasets that include predictions must have a column with the prediction and another with its real target
TARGET_COL = 'y_true',
PREDICT_COL = 'y_predict'

# CONSTANTS
SRC_DIR = os.path.dirname(__file__)


def load_titanic() -> pd.DataFrame:
    """

    :return:
    """
    return pd.read_csv(os.path.join(SRC_DIR, TITANIC_PATH))


def load_titanic_discretized() -> Tuple[pd.DataFrame, List[str], List[str], str, str]:
    """

    :return:
    """
    df_dataset = pd.read_csv(os.path.join(SRC_DIR, TITANIC_DISCRETIZED_PATH))
    return df_dataset, FEATURE_COLS_TITANIC, TARGET_COLS_TITANIC, TARGET_COL, PREDICT_COL
