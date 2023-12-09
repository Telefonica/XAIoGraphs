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
from typing import List, Tuple

import pandas as pd

from xaiographs.common.constants import LANG_EN, LANG_ES

ID = ['id']
# Titanic Dataset
TITANIC_PATH = 'data/titanic/dataset.csv'
TITANIC_DISCRETIZED_PATH = 'data/titanic/dataset_discretized.csv'
TITANIC_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/titanic/values_semantics_en.csv',
    LANG_ES: 'data/titanic/values_semantics_es.csv'
}
TITANIC_TARGET_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/titanic/target_values_semantics_en.csv',
    LANG_ES: 'data/titanic/target_values_semantics_es.csv'
}
FEATURE_COLS_TITANIC = ['gender', 'title', 'age', 'family_size', 'is_alone', 'embarked', 'class', 'ticket_price']
TARGET_COLS_TITANIC = ['SURVIVED', 'NO_SURVIVED']

# Body Performance Dataset
BODY_PERFORM_PATH = 'data/body_performance/dataset.csv'
BODY_PERFORM_DISCRETIZED_PATH = 'data/body_performance/dataset_discretized.csv'
BODY_PERFORM_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/body_performance/values_semantics_en.csv',
    LANG_ES: 'data/body_performance/values_semantics_es.csv'
}
BODY_PERFORM_TARGET_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/body_performance/target_values_semantics_en.csv',
    LANG_ES: 'data/body_performance/target_values_semantics_es.csv'
}
FEATURE_COLS_BODY_PERFORM = ['age', 'gender', 'height_cm', 'weight_kg', 'body_fat_%', 'diastolic', 'systolic',
                             'gripForce', 'sit_and_bend_forward_cm', 'sit-ups_counts', 'broad_jump_cm']
TARGET_COLS_BODY_PERFORM = ['high_performance', 'mid_performance', 'low_performance']

# Education Performance Dataset
EDUC_PERFORM_PATH = 'data/education_performance/dataset_performance.csv'
EDUC_PERFORM_DISCRETIZED_PATH = 'data/education_performance/dataset_discretized.csv'
EDUC_PERFORM_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/education_performance/values_semantics_en.csv',
    LANG_ES: 'data/education_performance/values_semantics_es.csv'
}
EDUC_PERFORM_TARGET_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/education_performance/target_values_semantics_en.csv',
    LANG_ES: 'data/education_performance/target_values_semantics_es.csv'
}
FEATURE_COLS_EDUC_PERFORM = ['age', 'sex', 'graduated_h_school_type', 'scholarship_type',
                             'additional_work', 'activity', 'partner', 'total_salary', 'transport',
                             'accomodation', 'mother_ed', 'farther_ed', 'parental_status',
                             'mother_occup', 'father_occup', 'weekly_study_hours',
                             'reading_non_scientific', 'reading_scientific',
                             'attendance_seminars_dep', 'impact_of_projects', 'attendances_classes',
                             'preparation_midterm_company', 'preparation_midterm_time',
                             'taking_notes', 'listenning', 'discussion_improves_interest',
                             'flip_classrom']
TARGET_COLS_EDUC_PERFORM = ['A', 'B', 'C', 'D', 'Fail']

# COMPAS Dataset
COMPAS_PATH = 'data/compas/dataset_compas.csv'
COMPAS_DISCRETIZED_PATH = 'data/compas/dataset_discretized.csv'
COMPAS_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/compas/values_semantics_en.csv',
    LANG_ES: 'data/compas/values_semantics_es.csv'
}
COMPAS_TARGET_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/compas/target_values_semantics_en.csv',
    LANG_ES: 'data/compas/target_values_semantics_es.csv'
}
FEATURE_COLS_COMPAS = ['Gender', 'Age_range', 'Ethnicity', 'MaritalStatus', 'c_charge_degree', 'is_recid',
                       'is_violent_recid']
TARGET_COLS_COMPAS = ['High_Recid', 'Medium_Recid', 'Low_Recid']

# COMPAS Reality Dataset
COMPAS_REALITY_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/compas_reality/values_semantics_en.csv',
    LANG_ES: 'data/compas_reality/values_semantics_es.csv'
}
COMPAS_REALITY_TARGET_VALUES_SEMANTICS_PATH = {
    LANG_EN: 'data/compas_reality/target_values_semantics_en.csv',
    LANG_ES: 'data/compas_reality/target_values_semantics_es.csv'
}
TARGET_COLS_COMPAS_REALITY = ['Recid', 'No_Recid']

# All datasets that include predictions must have a column with the prediction and another with its real target
TARGET_COL = 'y_true'
PREDICT_COL = 'y_predict'

# CONSTANTS
SRC_DIR = os.path.dirname(__file__)


def load_titanic() -> pd.DataFrame:
    """Returns Titanic dataset with the following Features:

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


    Returns
    -------
    load_titanic : pd.DataFrame
        Titanic dataset


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
    """Returns titanic dataset (and other metadata) to be tested in xaiographs. The dataset contains  \
    a series of discretized features, two columns (SURVIVED and NO_SURVIVED) with the probability [0,1] of  \
    classification given by an ML model and two columns 'y_true' and 'y_predict' with GroundTruth and prediction \
    given by ML model.  \
    Dataset contains the following columns:

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

    Returns
    -------
    load_titanic_discretized : Tuple[pd.DataFrame, List[str], List[str], str, str]
        + pd.DataFrame, with data
        + List[str], with features name columns
        + List[str], with target names probabilities
        + str, with GroundTruth
        + str, with prediction ML model



    Example:
            >>> from xaiographs.datasets import load_titanic_discretized
            >>> df_dataset, features_cols, target_cols, y_true, y_predict = load_titanic_discretized()
            >>> df_dataset.head(5)
               id  gender title          age family_size  is_alone embarked  class ticket_price  SURVIVED NO_SURVIVED       y_true    y_predict
            0   0  female   Mrs  18_30_years           1         1        S      1         High         1           0     SURVIVED     SURVIVED
            1   1    male    Mr    <12_years         3-5         0        S      1         High         1           0     SURVIVED     SURVIVED
            2   2  female   Mrs    <12_years         3-5         0        S      1         High         0           1  NO_SURVIVED  NO_SURVIVED
            3   3    male    Mr  18_30_years         3-5         0        S      1         High         0           1  NO_SURVIVED  NO_SURVIVED
            4   4  female   Mrs  18_30_years         3-5         0        S      1         High         0           1  NO_SURVIVED  NO_SURVIVED
            >>> features_cols
            ['gender', 'title', 'age', 'family_size', 'is_alone', 'embarked', 'class', 'ticket_price']
            >>> target_cols
            ['SURVIVED', 'NO_SURVIVED']
            >>> y_true
            'y_true'
            >>> y_predict
            'y_predict'
    """
    df_dataset = pd.read_csv(os.path.join(SRC_DIR, TITANIC_DISCRETIZED_PATH))
    return df_dataset, FEATURE_COLS_TITANIC, TARGET_COLS_TITANIC, TARGET_COL, PREDICT_COL


def load_titanic_why(language: str = LANG_EN) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns the necessary DataFrames to test the WHY module of XAIoGraphs with the explainability \
    calculated with the Titanic dataset.


    Parameters
    ----------
    language : str
        Language identifier {es: Spanish, en: English}. Default uses English language


    Returns
    -------
    load_titanic_why : Tuple[pd.DataFrame, pd.DataFrame]
        + pd.DataFrame with the natural language explanation of feature-value we want to use
        + pd.DataFrame with the natural language explanation of feature-value we want to use per target


    Example:
            >>> from xaiographs.datasets import load_titanic_why
            >>> df_values_semantics, df_target_values_semantics = load_titanic_why()
            >>> df_values_semantics.head(5)
                 feature_value                              reason
            0      gender_male                         to be a man
            1    gender_female                       to be a woman
            2       is_alone_1                        travel alone
            3    family_size_2  to be from a family of few members
            4  family_size_3-5                   be a large family
            >>> df_target_values_semantics.head(5)
                    target    feature_value                                  reason
            0  NO_SURVIVED      gender_male                      many men have died
            1  NO_SURVIVED    gender_female                           to be a woman
            2  NO_SURVIVED       is_alone_1                     they traveled alone
            3  NO_SURVIVED    family_size_2  they were from a family of few members
            4  NO_SURVIVED  family_size_3-5           they were from a large family

    """
    df_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, TITANIC_VALUES_SEMANTICS_PATH[LANG_ES]))
                          if language == LANG_ES
                          else pd.read_csv(os.path.join(SRC_DIR, TITANIC_VALUES_SEMANTICS_PATH[LANG_EN])))
    df_target_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, TITANIC_TARGET_VALUES_SEMANTICS_PATH[LANG_ES]))
                                 if language == LANG_ES
                                 else pd.read_csv(os.path.join(SRC_DIR, TITANIC_TARGET_VALUES_SEMANTICS_PATH[LANG_EN])))

    return df_values_semantic, df_target_values_semantic


def load_body_performance() -> pd.DataFrame:
    """Returns body performance dataset with the following Features:

    + **id:** unique person identifier
    + **age:** person age
    + **gender:** person gender
    + **height_cm:** Measurement of the waist expressed in centimeters
    + **weight_kg:** Weight of the person expressed in kilograms
    + **body_fat_%:** Percentage of body fat
    + **diastolic:** diastolic blood pressure (min)
    + **systolic:** systolic blood pressure (min)
    + **gripForce:** Measure the grip force of the hands
    + **sit_and_bend_forward_cm:** Distance expressed in centimeters from the length of the entire back, from the heels to the crown of the head
    + **sit-ups_counts:** Num of repetitions of raising the torso to a sitting position and returning to the original position without using the arms or lifting the feet
    + **broad_jump_cm:** Longest jump forward jump with a running start and a single leap, expressed in centimiters
    + **class:** Grade of performance

    Returns
    -------
    load_body_performance : pd.DataFrame
        Body Performance dataset


        Example:
            >>> from xaiographs.datasets import load_body_performance
            >>> df_dataset = load_body_performance()
            >>> df_dataset.head(5)
               id   age gender  height_cm  weight_kg  body_fat_%  diastolic  systolic  gripForce  sit_and_bend_forward_cm  sit-ups_counts  broad_jump_cm             class
            0   0  27.0      M      172.3      75.24        21.3       80.0     130.0       54.9                     18.4            60.0          217.0   mid_performance
            1   1  25.0      M      165.0      55.80        15.7       77.0     126.0       36.4                     16.3            53.0          229.0  high_performance
            2   2  31.0      M      179.6      78.00        20.1       92.0     152.0       44.8                     12.0            49.0          181.0   mid_performance
            3   3  32.0      M      174.5      71.10        18.4       76.0     147.0       41.4                     15.2            53.0          219.0   mid_performance
            4   4  28.0      M      173.8      67.70        17.1       70.0     127.0       43.5                     27.1            45.0          217.0   mid_performance
    """

    return pd.read_csv(os.path.join(SRC_DIR, BODY_PERFORM_PATH))


def load_body_performance_discretized() -> Tuple[pd.DataFrame, List[str], List[str], str, str]:
    """Returns body performance dataset (and other metadata) to be tested in xaiographs. The dataset contains  \
    a series of discretized features, four columns (high_performance,mid-top_performance,mid-low_performance,low_performance) \
    with the probability [0,1] of classification given by an ML model and two columns 'y_true' and 'y_predict' \
    with GroundTruth and prediction given by ML model.  \
    Dataset contains the following columns:

    + **id:** unique person identifier
    + **age:** person age
    + **gender:** person gender
    + **height_cm:** Measurement of the waist expressed in centimeters
    + **weight_kg:** Weight of the person expressed in kilograms
    + **body_fat_%:** Percentage of body fat
    + **diastolic:** diastolic blood pressure (min)
    + **systolic:** systolic blood pressure (min)
    + **gripForce:** Measure the grip force of the hands
    + **sit_and_bend_forward_cm:** Distance expressed in centimeters from the length of the entire back, from the heels to the crown of the head
    + **sit-ups_counts:** Num of repetitions of raising the torso to a sitting position and returning to the original position without using the arms or lifting the feet
    + **broad_jump_cm:** Longest jump forward jump with a running start and a single leap, expressed in centimiters
    + **y_true:** real target - {high_performance,mid-top_performance,mid-low_performance,low_performance}
    + **y_predict:** machine learning model prediction - {high_performance,mid-top_performance,mid-low_performance,low_performance}
    + **high_performance:** probability [0,1] that the person has a high level of body performance. Calculated by ML model
    + **mid-top_performance:** probability [0,1] that the person has a mid-top level of body performance. Calculated by ML model
    + **mid-low_performance:** probability [0,1] that the person has a mid-low level of body performance. Calculated by ML model
    + **low_performance:** probability [0,1] that the person has a low level of body performance. Calculated by ML model

    Returns
    -------
    load_body_performance_discretized : Tuple[pd.DataFrame, List[str], List[str], str, str]
        + pd.DataFrame, with data
        + List[str], with features name columns
        + List[str], with target names probabilities
        + str, with GroundTruth
        + str, with prediction ML model



    Example:
            >>> from xaiographs.datasets import load_body_performance_discretized
            >>> df_dataset, features_cols, target_cols, y_true, y_predict = load_body_performance_discretized()
            >>> df_dataset.head(5)
               id    age gender    height_cm  weight_kg body_fat_%  diastolic     systolic  gripForce sit_and_bend_forward_cm sit-ups_counts  broad_jump_cm            y_true         y_predict  high_performance  mid_performance  low_performance
            0   0  26-35      M  160-mid-176  55-mid-79  15-mid-30  68-mid-89  115-mid-144    over_47                6-mid-23        over_54    150-mid-229   mid_performance   mid_performance                 0                1                0
            1   1    <25      M  160-mid-176  55-mid-79   under_15  68-mid-89  115-mid-144  26-mid-47                6-mid-23      25-mid-54    150-mid-229  high_performance  high_performance                 1                0                0
            2   2  26-35      M     over_176  55-mid-79  15-mid-30    over_89     over_144  26-mid-47                6-mid-23      25-mid-54    150-mid-229   mid_performance   mid_performance                 0                1                0
            3   3  26-35      M  160-mid-176  55-mid-79  15-mid-30  68-mid-89     over_144  26-mid-47                6-mid-23      25-mid-54    150-mid-229   mid_performance   mid_performance                 0                1                0
            4   4  26-35      M  160-mid-176  55-mid-79  15-mid-30  68-mid-89  115-mid-144  26-mid-47                 over_23      25-mid-54    150-mid-229   mid_performance   mid_performance                 0                1                0
            >>> features_cols
            ['age', 'gender', 'height_cm', 'weight_kg', 'body_fat_%', 'diastolic', 'systolic',
            'gripForce', 'sit_and_bend_forward_cm', 'sit-ups_counts', 'broad_jump_cm']
            >>> target_cols
            ['high_performance', 'mid_performance', 'low_performance']
            >>> y_true
            'y_true'
            >>> y_predict
            'y_predict'
    """
    df_dataset = pd.read_csv(os.path.join(SRC_DIR, BODY_PERFORM_DISCRETIZED_PATH))
    return df_dataset, FEATURE_COLS_BODY_PERFORM, TARGET_COLS_BODY_PERFORM, TARGET_COL, PREDICT_COL


def load_body_performance_why(language: str = LANG_EN) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns the necessary DataFrames to test the WHY module of XAIoGraphs with the explainability \
    calculated with the Body Performance dataset.


    Parameters
    ----------
    language : str
        Language identifier {es: Spanish, en: English}. Default uses English language


    Returns
    -------
    load_body_performance_why : Tuple[pd.DataFrame, pd.DataFrame]
        + pd.DataFrame with the natural language explanation of feature-value we want to use
        + pd.DataFrame with the natural language explanation of feature-value we want to use per target


    Example:
            >>> from xaiographs.datasets import load_body_performance_why
            >>> df_values_semantics, df_target_values_semantics = load_body_performance_why()
            >>> df_values_semantics.head(5)
                    feature_value	reason
                0	    age_26-35	being a child
                1	    age_36-45	being adolescent
                2	    age_46-55	being young
                3	      age_<25	to be adult
                4	      age_>55   being an older person
            >>> df_target_values_semantics.head(5)
                    target	            feature_value	reason
                0	high_performance	    age_26-35    a child with a physical condition above average
                1	high_performance	    age_36-45    a teenager with a higher than average physical...
                2	high_performance	    age_46-55    a young man with a physical condition above av...
                3	high_performance	      age_<25    an adult with a physical condition above average
                4	high_performance	      age_>55    an older person with a higher than average phy...

    """
    df_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, BODY_PERFORM_VALUES_SEMANTICS_PATH[LANG_ES]))
                          if language == LANG_ES
                          else pd.read_csv(os.path.join(SRC_DIR, BODY_PERFORM_VALUES_SEMANTICS_PATH[LANG_EN])))
    df_target_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, BODY_PERFORM_TARGET_VALUES_SEMANTICS_PATH[LANG_ES]))
                                 if language == LANG_ES
                                 else pd.read_csv(
        os.path.join(SRC_DIR, BODY_PERFORM_TARGET_VALUES_SEMANTICS_PATH[LANG_EN])))

    return df_values_semantic, df_target_values_semantic


def load_education_performance() -> pd.DataFrame:
    """Returns body performance dataset with the following Features:

    + **id:** unique studen identifier
    + **age:** Student Age
    + **sex:** Sex
    + **graduated_h_school_type:** Graduated high-school type
    + **scholarship_type:** Scholarship type
    + **additional_work:** Additional work
    + **activity:**Regular artistic or sports activity
    + **partner:** Do you have a partner
    + **total_salary:** Total salary if available
    + **transport:** Transportation to the university
    + **accomodation:** Accommodation type in Cyprus
    + **mother_ed:** Mother's education
    + **farther_ed:** Father's education
    + **siblings:** Number of sisters/brothers
    + **parental_status:** Parental status
    + **mother_occup:** Mother's occupation
    + **father_occup:** Father's occupation
    + **weekly_study_hours:** Weekly study hours
    + **reading_non_scientific:** Reading frequency
    + **reading_scientific:** Reading frequency
    + **attendance_seminars_dep:**Attendance to the seminars/conferences related to the department
    + **impact_of_projects:** Impact of your projects/activities on your success
    + **attendances_classes:** Attendance to classes
    + **preparation_midterm_company:** Preparation to midterm exams 1
    + **preparation_midterm_time:** Preparation to midterm exams 2
    + **taking_notes:** Taking notes in classes
    + **listenning:** Listening in classes
    + **discussion_improves_interest:** Discussion improves my interest and success in the course
    + **flip_classrom:** Flip-classroom
    + **grade:** Grade of performance

    Returns
    -------
    load_education_performance : pd.DataFrame
        Education Performance dataset


        Example:
            >>> from xaiographs.datasets import load_education_performance
            >>> df_dataset = load_education_performance()
            >>> df_dataset.head(3)
               id  age  sex  graduated_h_school_type  scholarship_type  additional_work  activity  partner  total_salary  transport  accomodation  mother_ed  farther_ed  siblings  parental_status  mother_occup  father_occup  weekly_study_hours  reading_non_scientific  reading_scientific  attendance_seminars_dep  impact_of_projects  attendances_classes  preparation_midterm_company  preparation_midterm_time  taking_notes  listenning  discussion_improves_interest  flip_classrom  course_id  grade
            0  0     2    1                        2                 3                2         2        1             3          4             2          1           2         3                1             2             3                   2                       2                   2                        1                   1                    2                            1                         1             2           2                             2              2          1   Fail
            1  1     1    1                        1                 4                1         1        2             4          2             3          4           4         1                1             3             2                   3                       3                   3                        1                   3                    1                            3                         2             3           1                             3              3          1   Fail
            2  2     1    1                        1                 4                2         2        2             1          1             1          3           4         4                2             2             2                   3                       2                   2                        1                   1                    1                            1                         1             2           2                             2              3          1   Fail
    """

    return pd.read_csv(os.path.join(SRC_DIR, EDUC_PERFORM_PATH))


def load_education_performance_discretized() -> Tuple[pd.DataFrame, List[str], List[str], str, str]:
    """Returns education performance dataset (and other metadata) to be tested in xaiographs. The dataset contains  \
    a series of discretized features, five columns (A, B, C, D, Fail) with the probability [0,1] of classification  \
    given by an ML model and two columns 'y_true' & 'y_predict' with GroundTruth and prediction given by ML model.  \
    Dataset contains the following columns:

    + **id:** unique studen identifier
    + **age:** Student Age
    + **sex:** Sex
    + **graduated_h_school_type:** Graduated high-school type
    + **scholarship_type:** Scholarship type
    + **additional_work:** Additional work
    + **activity:**Regular artistic or sports activity
    + **partner:** Do you have a partner
    + **total_salary:** Total salary if available
    + **transport:** Transportation to the university
    + **accomodation:** Accommodation type in Cyprus
    + **mother_ed:** Mother's education
    + **farther_ed:** Father's education
    + **siblings:** Number of sisters/brothers
    + **parental_status:** Parental status
    + **mother_occup:** Mother's occupation
    + **father_occup:** Father's occupation
    + **weekly_study_hours:** Weekly study hours
    + **reading_non_scientific:** Reading frequency
    + **reading_scientific:** Reading frequency
    + **attendance_seminars_dep:**Attendance to the seminars/conferences related to the department
    + **impact_of_projects:** Impact of your projects/activities on your success
    + **attendances_classes:** Attendance to classes
    + **preparation_midterm_company:** Preparation to midterm exams 1
    + **preparation_midterm_time:** Preparation to midterm exams 2
    + **taking_notes:** Taking notes in classes
    + **listenning:** Listening in classes
    + **discussion_improves_interest:** Discussion improves my interest and success in the course
    + **flip_classrom:** Flip-classroom
    + **y_true:** real target - {A, B, C, D, Fail}
    + **y_predict:** machine learning model prediction - {A, B, C, D, Fail}
    + **A:** probability [0,1] that the person has a better educational performance. Calculated by ML model
    + **B:** probability [0,1] that the person has a second educational performance. Calculated by ML model
    + **C:** probability [0,1] that the person has a third educational performance. Calculated by ML model
    + **D:** probability [0,1] that the person has a fourth educational performance. Calculated by ML model
    + **Fail:** probability [0,1] that the person has a lower educational performance. Calculated by ML model


    Returns
    -------
    load_education_performance_discretized : Tuple[pd.DataFrame, List[str], List[str], str, str]
        + pd.DataFrame, with data
        + List[str], with features name columns
        + List[str], with target names probabilities
        + str, with GroundTruth
        + str, with prediction ML model



    Example:
            >>> from xaiographs.datasets import load_education_performance_discretized
            >>> df_dataset, features_cols, target_cols, y_true, y_predict = load_education_performance_discretized()
            >>> df_dataset.head(3)
               id   age     sex  graduated_h_school_type  scholarship_type  additional_work  activity  partner  total_salary         transport  accomodation       mother_ed        farther_ed             parental_status             mother_occup             father_occup  weekly_study_hours  reading_non_scientific  reading_scientific  attendance_seminars_dep  impact_of_projects  attendances_classes  preparation_midterm_company       preparation_midterm_time  taking_notes  listenning  discussion_improves_interest    flip_classrom  y_true  y_predict  A  B  C  D  Fail
            0  0  22-25  female                    state               50%               No        No      Yes   USD 271-340             Other     dormitory  primary school  secondary school                     married                housewife  private sector employee            <5 hours               Sometimes           Sometimes                      Yes            positive            sometimes                        alone       closest date to the exam     sometimes   sometimes                     sometimes           useful    Fail       Fail  0  0  0  0  1
            1  1  18-21  female                  private               75%              Yes       Yes       No   USD 341-410  Private car/taxi   with family      university        university                     married       government officer       government officer          6-10 hours                   Often               Often                      Yes             neutral               always               not applicable  regularly during the semester        always       never                        always   not applicable    Fail       Fail  0  0  0  0  1
            2  2  18-21  female                  private               75%               No        No       No   USD 135-200               Bus        rental     high school        university                    divorced                housewife       government officer          6-10 hours               Sometimes           Sometimes                      Yes            positive               always                        alone       closest date to the exam     sometimes   sometimes                     sometimes   not applicable    Fail       Fail  0  0  0  0  1
            >>> features_cols
            ['age', 'sex', 'graduated_h_school_type', 'scholarship_type', 'additional_work', 'activity', 'partner', 
            'total_salary', 'transport', 'accomodation', 'mother_ed', 'farther_ed', 'parental_status', 'mother_occup', 
            'father_occup', 'weekly_study_hours', 'reading_non_scientific', 'reading_scientific', 'attendance_seminars_dep', 
            'impact_of_projects', 'attendances_classes', 'preparation_midterm_company', 'preparation_midterm_time', 
            'taking_notes', 'listenning', 'discussion_improves_interest', 'flip_classrom']
            >>> target_cols
            ['A', 'B', 'C', 'D', 'Fail']
            >>> y_true
            'y_true'
            >>> y_predict
            'y_predict'
    """
    df_dataset = pd.read_csv(os.path.join(SRC_DIR, EDUC_PERFORM_DISCRETIZED_PATH))
    return df_dataset, FEATURE_COLS_EDUC_PERFORM, TARGET_COLS_EDUC_PERFORM, TARGET_COL, PREDICT_COL


def load_education_performance_why(language: str = LANG_EN) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns the necessary DataFrames to test the WHY module of XAIoGraphs with the explainability \
    calculated with the Body Performance dataset.


    Parameters
    ----------
    language : str
        Language identifier {es: Spanish, en: English}. Default uses English language


    Returns
    -------
    load_education_performance_why : Tuple[pd.DataFrame, pd.DataFrame]
        + pd.DataFrame with the natural language explanation of feature-value we want to use
        + pd.DataFrame with the natural language explanation of feature-value we want to use per target


    Example:
            >>> from xaiographs.datasets import load_education_performance_why
            >>> df_values_semantics, df_target_values_semantics = load_education_performance_why()
            >>> df_values_semantics.head(5)
                          feature_value                                        reason
            0        accomodation_other  having been in another type of accommodation
            1    accomodation_dormitory               having been housed in a bedroom
            2       accomodation_rental         having been in a rented accommodation
            3  accomodation_with family         having been in a family accommodation
            4                 age_18-21                      being under 21 years old
            >>> df_target_values_semantics.head(5)
              target             feature_value                       reason
            0      A        accomodation_Other     live in other facilities
            1      A    accomodation_dormitory          living in a bedroom
            2      A       accomodation_rental             living in rental
            3      A  accomodation_with family     he lives with his family
            4      A                 age_18-21  it is below the average age

    """
    df_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, EDUC_PERFORM_VALUES_SEMANTICS_PATH[LANG_ES]))
                          if language == LANG_ES
                          else pd.read_csv(os.path.join(SRC_DIR, EDUC_PERFORM_VALUES_SEMANTICS_PATH[LANG_EN])))
    df_target_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, EDUC_PERFORM_TARGET_VALUES_SEMANTICS_PATH[LANG_ES]))
                                 if language == LANG_ES
                                 else pd.read_csv(
        os.path.join(SRC_DIR, EDUC_PERFORM_TARGET_VALUES_SEMANTICS_PATH[LANG_EN])))

    return df_values_semantic, df_target_values_semantic


def load_compas() -> pd.DataFrame:
    """Returns COMPAS dataset with the following Features:

    + **id**
    + **FirstName**
    + **LastName**
    + **Gender**
    + **Age_range**
    + **Ethnicity**
    + **days_b_screening_arrest**
    + **c_jail_in**
    + **c_jail_out**
    + **Days_in_jail**
    + **c_charge_degree**
    + **c_charge_desc**
    + **is_recid**
    + **is_violent_recid**
    + **score_risk_recidivism**
    + **score_text_risk_recidivism**
    + **score_risk_violence**
    + **score_text_risk_violence**
    + **Low_Recid**
    + **Medium_Recid**
    + **High_Recid**
    + **No_Recid**
    + **Recid**
    + **predict_two_year_recid**
    + **real_two_year_recid**

    Returns
    -------
    compas : pd.DataFrame
        compas dataset


        Example:
            >>> from xaiographs.datasets import load_compas
            >>> df_dataset = load_compas()
            >>> df_dataset.head(3)
               id FirstName   LastName Gender        Age_range         Ethnicity  days_b_screening_arrest     c_jail_in    c_jail_out  Days_in_jail c_charge_degree                   c_charge_desc  is_recid  is_violent_recid score_risk_recidivism score_text_risk_recidivism  score_risk_violence score_text_risk_violence  Low_Recid  Medium_Recid  High_Recid  No_Recid  score_text_risk_violence  Low_Recid  Medium_Recid  High_Recid  No_Recid  Recid  predict_two_year_recid  real_two_year_recid
            0   1    miguel  hernandez   Male  Greater than 45             Other                     -1.0  13/8/13 6:03  14/8/13 5:41             1               F    Aggravated Assault w/Firearm         0                 0                     1                        Low                    1                      Low          1             0           0         1                       Low          1             0           0         1      0                       0                    0
            1   3     kevon      dixon   Male          25 - 45  African-American                     -1.0  26/1/13 3:45   5/2/13 5:36            10               F  Felony Battery w/Prior Convict         1                 1                     3                        Low                    1                      Low          1             0           0         0                       Low          1             0           0         0      1                       0                    1
            2   5     marcu      brown   Male     Less than 25  African-American                      NaN           NaN           NaN             0               F          Possession of Cannabis         0                 0                     8                       High                    6                   Medium          0             0           1         1                    Medium          0             0           1         1      0                       1                    0
    """

    return pd.read_csv(os.path.join(SRC_DIR, COMPAS_PATH), sep='|', header=0)


def load_compas_discretized() -> Tuple[pd.DataFrame, List[str], List[str], str, str]:
    """Returns COMPAS dataset (and other metadata) to be tested in xaiographs. The dataset contains  \
    a series of discretized features, three columns (Low_Recid, Medium_Recid, High_Recid) with the probability [0,1] \
    of classification given by COMPAS model that predict the probability of recidivism,  and two columns 'y_true' & \
    'y_predict' with GroundTruth and prediction given by ML model (0: did not recidivist two years after arrest, \
    1: two years after the arrest, recidivist). Dataset contains the following columns:

    + **id:** unique person identifier
    + **Gender:** {Male, Female}
    + **Age_range:** {Less than 25, 25 - 45, Greater than 45}
    + **Ethnicity:** {African-American, Asian, Caucasian, Hispanic, Native American, Other}
    + **MaritalStatus:** {Married, Separated, Single, Other}
    + **c_charge_degree:** {F, M}
    + **is_recid:** {YES, NO}
    + **is_violent_recid:** {YES, NO}
    + **Low_Recid:** probability assigned by the model to the label "low probability of recidivism".
    + **Medium_Recid:** probability assigned by the model to the label "medium probability of recidivism".
    + **High_Recid:** probability assigned by the model to the label "High probability of recidivism".
    + **y_predict:** Model prediction (1: recidivism, 0: no recidivism)
    + **y_true:** Recidivism two years after arrest (1: recidivism, 0: no recidivism)


    Returns
    -------
    load_compas_discretized : Tuple[pd.DataFrame, List[str], List[str], str, str]
        + pd.DataFrame, with data
        + List[str], with features name columns
        + List[str], with target names probabilities
        + str, with GroundTruth
        + str, with prediction ML model



    Example:
            >>> from xaiographs.datasets import load_compas_discretized
            >>> df_dataset, features_cols, target_cols, y_true, y_predict = load_compas_discretized()
            >>> df_dataset.head(3)
              id Gender        Age_range         Ethnicity MaritalStatus c_charge_degree is_recid is_violent_recid  High_Recid  Medium_Recid  Low_Recid    y_true y_predict
            0  1   Male  Greater than 45             Other        Single               F       NO               NO           0             0          1  No_Recid  No_Recid
            1  3   Male          25 - 45  African-American        Single               F      YES              YES           0             0          1     Recid  No_Recid
            2  5   Male          25 - 45             Other     Separated               M       NO               NO           0             0          1  No_Recid  No_Recid
            >>> features_cols
            ['Gender', 'Age_range', 'Ethnicity', 'MaritalStatus', 'c_charge_degree', 'is_recid', 'is_violent_recid']
            >>> target_cols
            ['High_Recid', 'Medium_Recid', 'Low_Recid']
            >>> y_true
            'y_true'
            >>> y_predict
            'y_predict'
    """
    df_dataset = pd.read_csv(os.path.join(SRC_DIR, COMPAS_DISCRETIZED_PATH))
    return (df_dataset[ID + FEATURE_COLS_COMPAS + TARGET_COLS_COMPAS + [TARGET_COL] + [PREDICT_COL]],
            FEATURE_COLS_COMPAS, TARGET_COLS_COMPAS, TARGET_COL, PREDICT_COL)


def load_compas_why(language: str = LANG_EN) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns the necessary DataFrames to test the WHY module of XAIoGraphs with the explainability \
    calculated with the COMPAS dataset.


    Parameters
    ----------
    language : str
        Language identifier {es: Spanish, en: English}. Default uses English language


    Returns
    -------
    load_compas_why : Tuple[pd.DataFrame, pd.DataFrame]
        + pd.DataFrame with the natural language explanation of feature-value we want to use
        + pd.DataFrame with the natural language explanation of feature-value we want to use per target


    Example:
            >>> from xaiographs.datasets import load_compas_why
            >>> df_values_semantics, df_target_values_semantics = load_compas_why()
            >>> df_values_semantics.head(5)
                            feature_value                  reason
            0           Age_range_25 - 45             middle-aged
            1   Age_range_Greater than 45  be older than 45 years
            2      Age_range_Less than 25                be young
            3  Ethnicity_African-American             being black
            4             Ethnicity_Asian     being of Asian race
            >>> df_target_values_semantics.head(5)
                   target               feature_value                                                                                         reason
            0  High_Recid           Age_range_25 - 45 some in the age range between 25 and 45 years old were classified as "High Risk of recidivism"
            1  High_Recid   Age_range_Greater than 45                 few of those over 45 years of age were classified as "High Risk of recidivism"
            2  High_Recid      Age_range_Less than 25                        many under 25 years of age were classified as "High Risk of recidivism"
            3  High_Recid  Ethnicity_African-American                                        many classified as "High Risk of Recidivism" were Black
            4  High_Recid             Ethnicity_Asian                            very few classified as "High Risk of Recidivism" were of Asian race

    """
    df_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, COMPAS_VALUES_SEMANTICS_PATH[LANG_ES]))
                          if language == LANG_ES
                          else pd.read_csv(os.path.join(SRC_DIR, COMPAS_VALUES_SEMANTICS_PATH[LANG_EN])))
    df_target_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, COMPAS_TARGET_VALUES_SEMANTICS_PATH[LANG_ES]))
                                 if language == LANG_ES
                                 else pd.read_csv(
        os.path.join(SRC_DIR, COMPAS_TARGET_VALUES_SEMANTICS_PATH[LANG_EN])))

    return df_values_semantic, df_target_values_semantic


def load_compas_reality_discretized() -> Tuple[pd.DataFrame, List[str], List[str], str, str]:
    """Returns COMPAS dataset (and other metadata) to be tested in xaiographs. The dataset contains  \
    a series of discretized features, two columns (No_Recid, Recid) with two flags indicating whether or not they \
    reoffended two years after arrest. Dataset contains the following columns:

    + **id:** unique person identifier
    + **Gender:** {Male, Female}
    + **Age_range:** {Less than 25, 25 - 45, Greater than 45}
    + **Ethnicity:** {African-American, Asian, Caucasian, Hispanic, Native American, Other}
    + **MaritalStatus:** {Married, Separated, Single, Other}
    + **c_charge_degree:** {F, M}
    + **is_recid:** {YES, NO}
    + **is_violent_recid:** {YES, NO}
    + **No_Recid:** not recidivist two years after arrest
    + **Recid:** recidivist two years after the arrest


    Returns
    -------
    load_compas_discretized : Tuple[pd.DataFrame, List[str], List[str], str, str]
        + pd.DataFrame, with data
        + List[str], with features name columns
        + List[str], with target names probabilities



    Example:
            >>> from xaiographs.datasets import load_compas_reality_discretized
            >>> df_dataset, features_cols, target_cols = load_compas_reality_discretized()
            >>> df_dataset.head(3)
              id Gender        Age_range         Ethnicity MaritalStatus c_charge_degree is_recid is_violent_recid  Recid  No_Recid
            0  1   Male  Greater than 45             Other        Single               F       NO               NO      0         1
            1  3   Male          25 - 45  African-American        Single               F      YES              YES      1         0
            2  5   Male          25 - 45             Other     Separated               M       NO               NO      0         1

            >>> features_cols
            ['Gender', 'Age_range', 'Ethnicity', 'MaritalStatus', 'c_charge_degree', 'is_recid', 'is_violent_recid']
            >>> target_cols
            ['Recid', 'No_Recid']

    """
    df_dataset = pd.read_csv(os.path.join(SRC_DIR, COMPAS_DISCRETIZED_PATH))
    return (df_dataset[ID + FEATURE_COLS_COMPAS + TARGET_COLS_COMPAS_REALITY],
            FEATURE_COLS_COMPAS, TARGET_COLS_COMPAS_REALITY)


def load_compas_reality_why(language: str = LANG_EN) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns the necessary DataFrames to test the WHY module of XAIoGraphs with the explainability \
    calculated with the COMPAS dataset.


    Parameters
    ----------
    language : str
        Language identifier {es: Spanish, en: English}. Default uses English language


    Returns
    -------
    load_compas_why : Tuple[pd.DataFrame, pd.DataFrame]
        + pd.DataFrame with the natural language explanation of feature-value we want to use
        + pd.DataFrame with the natural language explanation of feature-value we want to use per target


    Example:
            >>> from xaiographs.datasets import load_compas_reality_why
            >>> df_values_semantics, df_target_values_semantics = load_compas_reality_why()
            >>> df_values_semantics.head(3)
                           feature_value                  reason
            0           Age_range_25 - 45             middle-aged
            1   Age_range_Greater than 45  be older than 45 years
            2      Age_range_Less than 25                be young
            >>> df_target_values_semantics.head(3)
              target               feature_value                                                              reason
            0  Recid           Age_range_25 - 45 some in the age range between 25 and 45 years were repeat offenders
            1  Recid   Age_range_Greater than 45                          few of those over 45 were repeat offenders
            2  Recid      Age_range_Less than 25           many of those under 25 years of age were repeat offenders

    """
    df_values_semantic = (pd.read_csv(os.path.join(SRC_DIR, COMPAS_REALITY_VALUES_SEMANTICS_PATH[LANG_ES]))
                          if language == LANG_ES
                          else pd.read_csv(os.path.join(SRC_DIR, COMPAS_REALITY_VALUES_SEMANTICS_PATH[LANG_EN])))
    df_target_values_semantic = (
        pd.read_csv(os.path.join(SRC_DIR, COMPAS_REALITY_TARGET_VALUES_SEMANTICS_PATH[LANG_ES]))
        if language == LANG_ES
        else pd.read_csv(
            os.path.join(SRC_DIR, COMPAS_REALITY_TARGET_VALUES_SEMANTICS_PATH[LANG_EN])))

    return df_values_semantic, df_target_values_semantic
