import os
from typing import List, Tuple

import pandas as pd

# Titanic Dataset
TITANIC_PATH = 'data/titanic.csv'
TITANIC_DISCRETIZED_PATH = 'data/titanic_discretized.csv'
FEATURE_COLS_TITANIC = ['gender', 'title', 'age', 'family_size', 'is_alone', 'embarked', 'class', 'ticket_price']
TARGET_COLS_TITANIC = ['NO_SURVIVED', 'SURVIVED']

# All datasets that include predictions must have a column with the prediction and another with its real target
TARGET_COL = 'y_true'
PREDICT_COL = 'y_predict'

# CONSTANTS
SRC_DIR = os.path.dirname(__file__)


def load_titanic() -> pd.DataFrame:
    """Function returns a dataframe with the Titanic dataset with the following Features

        + **id:** unique passenger identifier
        + **gender:** passenger gender
        + **title:** passenger title
        + **age:** passenger age
        + **family_size:** number of family members the passenger was traveling with
        + **is_alone:** flag that indicates if the passenger was traveling alone or with a family
        + **embarked:** city of embarkation {S: Southampton, C: Cherbourg, Q: Queenstown}
        + **class:** class in which the passenger was traveling {1: first class, 2: second class, 3: third class}
        + **ticket_price:** price that the passenger pays for the trip
        + **survived:** flag that indicates if it survived or not {1: Survived, 0: No Survived}

        :return:pd.DataFrame, with titanic dataset

        Example:
            >>> from xaiographs.datasets import load_titanic
            >>> df_dataset = load_titanic()
            >>> df_dataset.head(5)
               id  gender title      age  family_size  is_alone embarked  class  ticket_price  survived
            0   0  female   Mrs  29.0000            0         1        S      1      211.3375         1
            1   1    male    Mr   0.9167            3         0        S      1      151.5500         1
            2   2  female   Mrs   2.0000            3         0        S      1      151.5500         0
            3   3    male    Mr  30.0000            3         0        S      1      151.5500         0
            4   4  female   Mrs  25.0000            3         0        S      1      151.5500         0
        """
    return pd.read_csv(os.path.join(SRC_DIR, TITANIC_PATH))


def load_titanic_discretized() -> Tuple[pd.DataFrame, List[str], List[str], str, str]:
    """Function returns the titanic dataset (and other metadata) to be tested in xaiographs. The dataset contains  \
    a series of discretized features, two columns (SURVIVED and NO_SURVIVED) with the probability [0,1] of  \
    classification given by an ML model and two columns 'y_true' and 'y_predict' with GroundTruth and prediction \
    given by ML model. To test the explainability module, it returns two lists, one with name of the feature  \
    columns and another list with the name of the columns that show the probability of classification for each class. \
    To test the Fairness module, return the name of columns that contain the GroundTruth and ML model prediction. \
    Information on the dataset columns with the values they can take is shown below:

        + **id:** unique passenger identifier
        + **gender:** passenger gender - {male, female}
        + **title:** passenger title - {Mrs, Mr, rare}
        + **age:** passenger age discretized - {<12_years, 12_18_years, 18_30_years, 30_60_years, >60_years}
        + **family_size:** number of family members the passenger was traveling with - {1, 2, 3-5, >5}
        + **is_alone:** flag that indicates if the passenger was traveling alone or with a family - {0, 1}
        + **embarked:** city of embarkation - {S: Southampton, C: Cherbourg, Q: Queenstown}
        + **class:** class in which the passenger was traveling - {1: first class, 2: second class, 3: third class}
        + **ticket_price:** discretized price that the passenger pays for the trip - {high, mid, low}
        + **NO_SURVIVED:** probability [0,1] that the passenger will not survive. Calculated by ML model
        + **SURVIVED:** probability [0,1] that the passenger will survive. Calculated by ML model
        + **y_true:** real target - {SURVIVED, NO_SURVIVED}
        + **y_predict:** machine learning model prediction - {SURVIVED, NO_SURVIVED}

    :return: Tuple: 1) pd.DataFrame, with data, 2) List[str], with features name columns, \
    3) List[str], with target names probabilities, 4) str, with GroundTruth, 5) str, with prediction ML model

    Example:
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_dataset, features_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> df_dataset.head(5)
               id  gender title          age family_size  is_alone embarked  class ticket_price  NO_SURVIVED  SURVIVED       y_true    y_predict
            0   0  female   Mrs  18_30_years           1         1        S      1         High            0         1     SURVIVED     SURVIVED
            1   1    male    Mr    <12_years         3-5         0        S      1         High            0         1     SURVIVED     SURVIVED
            2   2  female   Mrs    <12_years         3-5         0        S      1         High            1         0  NO_SURVIVED  NO_SURVIVED
            3   3    male    Mr  18_30_years         3-5         0        S      1         High            1         0  NO_SURVIVED  NO_SURVIVED
            4   4  female   Mrs  18_30_years         3-5         0        S      1         High            1         0  NO_SURVIVED  NO_SURVIVED
            >>> features_cols
            ['gender', 'title', 'age', 'family_size', 'is_alone', 'embarked', 'class', 'ticket_price']
            >>> target_cols
            ['NO_SURVIVED', 'SURVIVED']
            >>> y_true
            'y_true'
            >>> y_predict
            'y_predict'
    """
    df_dataset = pd.read_csv(os.path.join(SRC_DIR, TITANIC_DISCRETIZED_PATH))
    return df_dataset, FEATURE_COLS_TITANIC, TARGET_COLS_TITANIC, TARGET_COL, PREDICT_COL