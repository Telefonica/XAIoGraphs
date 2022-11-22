from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer, RobustScaler

from xaiographs.common.constants import ID, TARGET
from xaiographs.exgraph.explainer.explainer import Explainer


CAT_COLUMN_NAMES = ['family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone']
CONT_COLUMN_NAMES = ['age', 'fare']
QUANTILE_SIZE = 10
TAR_COLUMN_NAMES = [TARGET]


def titanic_cooking(target_col: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    This function takes care of loading and preprocessing the Titanic dataset so that the resulting DataFrame can
    be used to train a Machine Learning model. Optionally, the column to be predicted can be changed (default is
    'survived')

    :param: target_col:  String representing the column name to be considered as target (defaul is 'survived')
    :return:             Pandas DataFrame containing the preprocessed data so that it's suitable for training a Machine
                         Learning model
                         List of strings providing the names of the definitive categorical features, which may be
                         recalculated depending on which categorical feature will be considered as target (default
                          target is 'survived')
    """
    # A random seed is fixed so that results are reproducible from one execution to another
    np.random.seed(42)

    # Features and labels are retrieved for Titanic dataset
    x_train, y_train = fetch_openml("titanic", version=1, as_frame=True, return_X_y=True)

    # Some features considered irrelevant are dropped from the beginning
    x_train.drop(['boat', 'body', 'home.dest'], axis=1, inplace=True)

    # Synthetic features are calculated out of the given ones
    x_train['family_size'] = x_train['parch'] + x_train['sibsp']
    x_train['is_alone'] = np.where(x_train['family_size'] > 1, 0, 1)

    # Title feature can be extracted from the name
    x_train['title'] = x_train['name'].str.split(", ", expand=True)[1].str.split(".", expand=True)[0]
    # TODO: esto sería equiparar una señorita a una mujer casada
    #  ¿Sería mejor mantener las cuatro categorías más representativas: Mr, Miss, Mrs y Master y luego 'rare' u 'other'?
    x_train.loc[x_train['title'] == 'Miss', 'title'] = 'Mrs'
    x_train.loc[x_train['title'] == 'Master', 'title'] = 'Mr'
    x_train.loc[(x_train['title'] != 'Mrs') & (x_train['title'] != 'Mr'), 'title'] = 'rare'

    # Some other original feature won't be taken into account
    x_train = x_train.drop(['cabin', 'ticket', 'parch', 'sibsp', 'name'], axis=1)

    # Mode is imputed for categorical features
    cat_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent'))])

    # K nearest neighbors imputation will be used, together with the Robust Scaler, to impute and standardize
    # the numerical features
    num_transformer = Pipeline(steps=[('imputer', KNNImputer(n_neighbors=5)), ('scaler', RobustScaler())])

    # Transformation Pipelines will be put into a ColumnTransformer so that they can be all run sequentially
    preprocessor = ColumnTransformer(
        transformers=[('num', num_transformer, CONT_COLUMN_NAMES), ('cat', cat_transformer, CAT_COLUMN_NAMES)])
    preprocessor.fit(x_train)
    x_train_prepro = preprocessor.transform(x_train)

    # Once the features have been preprocessed, the target column is vertically appended
    concat_train_prepro = np.concatenate((x_train_prepro, np.expand_dims(y_train.values, axis=1)), axis=1).tolist()

    # The numpy matrix, representing the preprocessed dataset is not transformed into a pandas DataFrame
    df_train = pd.DataFrame(concat_train_prepro, columns=CONT_COLUMN_NAMES + CAT_COLUMN_NAMES + TAR_COLUMN_NAMES)

    # Survived is the target feature by default. If any other of the features (i.e: pclass) is going to be used as
    # target, target_col parameter will be used to set it up
    if target_col != 'survived':
        df_train.rename(columns={TARGET: 'survived', target_col: TARGET}, inplace=True)
        new_cat_column_names = CAT_COLUMN_NAMES.copy()
        new_cat_column_names.remove(target_col)
        new_cat_column_names.append('survived')
    else:
        new_cat_column_names = CAT_COLUMN_NAMES.copy()

    print('INFO: Target to be predicted for Titanic example: {}'.format(target_col))
    df_train = pd.DataFrame(df_train[CONT_COLUMN_NAMES + new_cat_column_names + TAR_COLUMN_NAMES].values,
                            columns=CONT_COLUMN_NAMES + new_cat_column_names + TAR_COLUMN_NAMES)

    return df_train, new_cat_column_names


def discretize_titanic(titanic_prediction: pd.DataFrame, target_cols: List[str],
                       cat_col_names: List[str]) -> pd.DataFrame:
    """
    This functions takes care of discretizing all continuous variables within the dataset of analyze, to fulfill
    the ImportanceCalculator requirements

    :param: titanic_prediction:  A pandas DataFrame to be explained. Its continuous features are not discretized
    :param: target_cols:         List of strings containing all column names identified as target
    :param: cat_col_names:       List of strings containing all column names to be considered categorical
    :return:                     Pandas DataFrame to be explained. But now its continuous features have been
                                 discretized and the DataFrame is ready for the ImportanceCalculator
    """

    # Continuous features are retrieved
    cont_vars_train = titanic_prediction[CONT_COLUMN_NAMES]

    # Quantile Transformer is used to transform continuous variables so that they follow uniform distributions
    # Deciles are used as landmarks for discretization
    qt = QuantileTransformer(n_quantiles=QUANTILE_SIZE, random_state=0)
    qt.fit(cont_vars_train)
    cont_train = qt.transform(cont_vars_train)

    # Once discretized, continuous features are vertically concatenated with the categorical ones and the target/s
    data_2_explain = np.concatenate((cont_train, titanic_prediction[cat_col_names].values,
                                     titanic_prediction[target_cols].values), axis=1).tolist()

    # A DataFrame is created from the numpy matrix resulting from the previous step
    df_2_explain = pd.DataFrame(data_2_explain, columns=CONT_COLUMN_NAMES + cat_col_names + target_cols)

    for col_name in CONT_COLUMN_NAMES:
        df_2_explain[col_name] = round(df_2_explain[col_name], int(QUANTILE_SIZE/10)) + 0.05

    # A DataFrame with the continuous features discretized is returned. Typing is coerced for certain features
    # The provided dataset it is assumed to have an ID, so here the index is used to simulate that ID
    return df_2_explain.astype(
        {**{'is_alone': 'float'}, **{target_col: 'float' for target_col in target_cols}}).reset_index().rename(
        columns={'index': ID})


def random_forest_titanic(titanic_cooked: pd.DataFrame, cat_col_names: List[str]):
    """
    This function takes care of encoding categorical variables and set dummy variable names accordingly. It also uses
    the resulting dataset for training and prediction. Once predictions have been obtained, the original target in the
    dataset provided as parameter, is replaced by that prediction. The model of choice is a Random Forest Classifier

    :param: titanic_cooked: Pandas DataFrame on which basic imputing and scaling operations have been performed
    :param: cat_col_names:  List of strings containing all column names to be considered categorical
    :return:                Pandas DataFrame which is identical to the aforementioned parameter but its target
                            has been replaced by the prediction of the trained model
    """

    # Features and labels are separated in three different numpy structures: one for continuous features, one for
    # categorical features and the third one for the target/s
    cat = titanic_cooked[cat_col_names].values
    cont = titanic_cooked[CONT_COLUMN_NAMES].values
    tar = titanic_cooked[TAR_COLUMN_NAMES].values

    # One Hot Encoding will be used to encode the categorical features
    enc = OneHotEncoder()
    enc.fit(cat)
    cat_enc = enc.transform(cat)

    # A column name list will be initialized to those names of the continuous features and then, for each categorical
    # feature, an additional name will be appended, consisting of <name_categorical_feature>_<value_categorical_feature>
    # this will be done for each categorical feature and each of their possible values. Finally, the target column name
    # will be added
    enc_names = CONT_COLUMN_NAMES.copy()
    for col_n in cat_col_names:
        for v in pd.unique(titanic_cooked[col_n]):
            enc_names.append(col_n + '_{}'.format(v) if isinstance(v, str) else col_n + '_{:.1f}'.format(v))
    enc_names.append(TARGET)

    # Original DataFrame is rebuilt, so that its structure matches the column name list built in the previous step
    data = np.concatenate((cont, cat_enc.toarray(), tar), axis=1)
    df_train = pd.DataFrame(data, columns=enc_names)
    df_train_features = df_train.drop([TARGET], axis=1)
    df_train_target = df_train[TARGET].astype('int')

    # With the aforementioned DataFrame, a new model is instantiated and trained. Prediction for the same DataFrame is
    # retrieved too
    model = RandomForestClassifier()
    model.fit(df_train_features.values, df_train_target.values)
    pre_prediction = model.predict(df_train_features.values)
    print('INFO: Train accuracy: {:.4f}'.format(accuracy_score(df_train_target.values, pre_prediction)))

    # Target column is replaced in the ORIGINAL dataset (not the one with the dummy variables) by the prediction column
    rf_predict = titanic_cooked.drop([TARGET], axis=1)
    rf_predict[TARGET] = pre_prediction
    rf_predict_targets = pd.get_dummies(rf_predict[TARGET], prefix=TARGET)
    rf_predict = pd.concat([rf_predict.drop([TARGET], axis=1), rf_predict_targets], axis=1)

    # Original dataset is returned exactly as it was received but including the model prediction. Column order must
    # remain the same
    return rf_predict[CONT_COLUMN_NAMES + cat_col_names + list(rf_predict_targets.columns)]


def prepare_titanic(target_col: str = 'survived') -> Tuple[pd.DataFrame, List[str], List[str], List[str]]:
    """
    This function is intended to coordinate the Titanic dataset load and preprocess together with the use of a Machine
    Learning model to predict the target column

    :param:     target_col: String representing the column to be considered as target (default: 'survived'). For a
                two-target problem default can be used, for a more than two targets problem, 'pclass' feature is the
                one that has been used so far. Please bear in mind, binary problems have been modeled as multi target
                (instead of target being 1 or 0, there're target_0 and target_1)
    :return:    Pandas DataFrame properly preprocessed. Its target may have result from the prediction of a Machine
                Learning model
                List of columns containing the features of the resulting Pandas DataFrame
                List of columns used as target
                List of columns to be considered categorical
    """

    # This first step represents the dataset preprocessing, in other words: all that is needed to do to the dataset
    # so that the predictive model will successfully train from it. It's important to remark that it is the user who
    # is responsible for this step
    df_titanic_cooked, final_cat_col_names = titanic_cooking(target_col=target_col)

    # A predictive model (in this case a Random Forest Classifier) is used to train and predict. These predictions
    # replace the original target in the dataset provided as parameter. Then, the resulting DataFrame is returned. Again
    # it is the user who is responsible for this step too
    df_titanic_prediction = random_forest_titanic(titanic_cooked=df_titanic_cooked, cat_col_names=final_cat_col_names)
    feature_cols = []
    target_cols = []
    for col in df_titanic_prediction.columns:
        if col.startswith(TARGET):
            target_cols.append(col)
        else:
            feature_cols.append(col)

    return df_titanic_prediction, feature_cols, target_cols, final_cat_col_names


def main():
    df_titanic_cooked, feature_cols, target_cols, final_cat_col_names = prepare_titanic(target_col='pclass')

    # This next step consists on;
    # - Continuous features discretization
    # - Categorical feature cleansing/dimensionality reduction (neither os these are necessary for Titanic dataset)
    # Right now, this step falls also on the user's side. However at some point the library might also take care of it
    # Right now, it is necessary that headers consist only of strings
    df_titanic = discretize_titanic(titanic_prediction=df_titanic_cooked, target_cols=target_cols,
                                    cat_col_names=final_cat_col_names)

    # The desired explainer is created
    explainer = Explainer(dataset=df_titanic, importance_engine='TEF_SHAP', destination_path='/home/cx02747/Utils/')

    # Explaining process is triggered
    explainer.explain(feature_cols=feature_cols, target_cols=target_cols)


if __name__ == '__main__':
    main()
