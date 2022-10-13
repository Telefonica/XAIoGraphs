import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

CONT_COLUMN_NAMES = ['age', 'fare']
CAT_COLUMN_NAMES = ['family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone']
TAR_COLUMN_NAMES = ['target']


def titanic_cooking():
    np.random.seed(42)

    x, y = fetch_openml("titanic", version=1, as_frame=True, return_X_y=True)
    x.drop(['boat', 'body', 'home.dest'], axis=1, inplace=True)
    x_split_train, x_split_test, y_split_train, y_split_test = train_test_split(x, y, stratify=y, test_size=0.1)

    x_train = pd.concat([x_split_train, x_split_test])
    y_train = pd.concat([y_split_train, y_split_test])

    x_train['family_size'] = x_train['parch'] + x_train['sibsp']
    x_train['is_alone'] = np.where(x_train['family_size'] > 1, 1, 0)
    x_train['title'] = x_train['name'].str.split(", ", expand=True)[1].str.split(".", expand=True)[0]

    x_train.loc[x_train['title'] == 'Miss', 'title'] = 'Mrs'
    x_train.loc[x_train['title'] == 'Master', 'title'] = 'Mr'
    x_train.loc[(x_train['title'] != 'Mrs') & (x_train['title'] != 'Mr'), 'title'] = 'rare'

    x_train = x_train.drop(['cabin', 'ticket', 'parch', 'sibsp', 'name'], axis=1)

    cat_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent'))])
    num_transformer = Pipeline(steps=[('imputer', KNNImputer(n_neighbors=5)), ('scaler', RobustScaler())])
    preprocessor = ColumnTransformer(
        transformers=[('num', num_transformer, CONT_COLUMN_NAMES), ('cat', cat_transformer, CAT_COLUMN_NAMES)])

    preprocessor.fit(x_train)

    x_train_prepro = preprocessor.transform(x_train)

    concat_train_prepro = np.concatenate((x_train_prepro, np.expand_dims(y_train.values, axis=1)), axis=1).tolist()

    df_train = pd.DataFrame(concat_train_prepro, columns=CONT_COLUMN_NAMES + CAT_COLUMN_NAMES + TAR_COLUMN_NAMES)

    return df_train
