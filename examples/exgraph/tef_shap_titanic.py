import itertools
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from absl import logging
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer, RobustScaler

from xaiographs.common.constants import COUNT, ID, NODE_1, NODE_2, TARGET, PERCENTAGE
from xaiographs.exgraph.tef_shap import TefShap

CAT_COLUMN_NAMES_BI = ['family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone']
CAT_COLUMN_NAMES_MULTI = ['family_size', 'embarked', 'sex', 'title', 'is_alone', 'survived']
CONT_COLUMN_NAMES = ['age', 'fare']
QUANTILE_SIZE = 10
TAR_COLUMN_NAMES = [TARGET]

"""
This process illustrates the end to end usage of XAIoGraphs from the bare dataset to the exportation of the 
retrieved explainability information so that it can be displayed 
"""


def titanic_cooking(multi_label: bool) -> pd.DataFrame:
    """
    This function takes care of loading and preprocessing the Titanic dataset so that the resulting DataFrame can
    be used to train a Machine Learning model

    :return: A pandas DataFrame containing the preprocessed data so that it's suitable for training a Machine Learning
             model
    """
    # A random seed is fixed so that results are reproducible from one execution to another
    np.random.seed(42)

    # Features and labels are retrieved for Titanic dataset
    x_train, y_train = fetch_openml("titanic", version=1, as_frame=True, return_X_y=True)

    # Some features considered irrelevant are dropped from the beginning
    x_train.drop(['boat', 'body', 'home.dest'], axis=1, inplace=True)

    # Synthetic features are calculated out of the given ones
    x_train['family_size'] = x_train['parch'] + x_train['sibsp']
    x_train['is_alone'] = np.where(x_train['family_size'] > 1, 1, 0)

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
        transformers=[('num', num_transformer, CONT_COLUMN_NAMES), ('cat', cat_transformer, CAT_COLUMN_NAMES_BI)])
    preprocessor.fit(x_train)
    x_train_prepro = preprocessor.transform(x_train)

    # Once the features have been preprocessed, the target column is vertically appended
    concat_train_prepro = np.concatenate((x_train_prepro, np.expand_dims(y_train.values, axis=1)), axis=1).tolist()

    # The numpy matrix, representing the preprocessed dataset is not transformed into a pandas DataFrame
    df_train = pd.DataFrame(concat_train_prepro, columns=CONT_COLUMN_NAMES + CAT_COLUMN_NAMES_BI + TAR_COLUMN_NAMES)

    if multi_label:
        df_train.rename(columns={"target": "survived", "pclass": "target"}, inplace=True)
        df_train_targets = pd.get_dummies(df_train[TARGET], prefix=TARGET)
        df_train = pd.DataFrame(np.concatenate((df_train[CONT_COLUMN_NAMES + CAT_COLUMN_NAMES_MULTI].values,
                                                df_train_targets.values), axis=1),
                                columns=CONT_COLUMN_NAMES + CAT_COLUMN_NAMES_MULTI + list(df_train_targets.columns))
    return df_train


def discretize_titanic(multi_label: bool, titanic_prediction: pd.DataFrame, target_cols: List[str]) -> pd.DataFrame:
    """
    This functions takes care of discretizing all continuous variables within the dataset of analyze, to fulfill
    the Explainer requirements

    :param:  titanic_prediction: A pandas DataFrame to be explained. Its continuous features are not discretized
    :param: target_cols:         List of strings containing all column names identified as target
    :return:                     A pandas DataFrame to be explained. But now its continuous features have been
                                 discretized and the DataFrame is ready for the Explainer
    """
    if multi_label:
        cat_column_names = CAT_COLUMN_NAMES_MULTI
    else:
        cat_column_names = CAT_COLUMN_NAMES_BI

    # Continuous features are retrieved
    cont_vars_train = titanic_prediction[CONT_COLUMN_NAMES]

    # Quantile Transformer is used to transform continuous variables so that they follow uniform distributions
    # Deciles are used as landmarks for discretization
    qt = QuantileTransformer(n_quantiles=QUANTILE_SIZE, random_state=0)
    qt.fit(cont_vars_train)
    cont_train = qt.transform(cont_vars_train)

    # Once discretized, continuous features are vertically concatenated with the categorical ones and the target/s
    data_2_explain = np.concatenate((cont_train, titanic_prediction[cat_column_names].values,
                                     titanic_prediction[target_cols].values), axis=1).tolist()

    # A DataFrame is created from the numpy matrix resulting from the previous step
    df_2_explain = pd.DataFrame(data_2_explain, columns=CONT_COLUMN_NAMES + cat_column_names + target_cols)

    for col_name in CONT_COLUMN_NAMES:
        df_2_explain[col_name] = round(df_2_explain[col_name], int(QUANTILE_SIZE/10)) + 0.05

    # A DataFrame with the continuous features discretized is returned. Typing is coerced for certain features
    # The provided dataset it is assumed to have an ID, so here the index is used to simulate that ID
    ## TODO METER ID
    return df_2_explain.astype(
        {**{'is_alone': 'float'}, **{target_col: 'float' for target_col in target_cols}}).reset_index().rename(
        columns={'index': ID})


def random_forest_titanic(titanic_cooked: pd.DataFrame):
    """
    This function takes care of encoding categorical variables and set dummy variable names accordingly. It also uses
    the resulting dataset for training and prediction. Once predictions have been obtained, the original target in the
    dataset provided as parameter, is replaced by that prediction. The model of choice is a Random Forest Classifier

    :param: titanic_cooked: A pandas DataFrame on which basic imputing and scaling operations have been performed
    :return:                A pandas DataFrame which is identical to the aforementioned parameter but its target
                            has been replaced by the prediction of the trained model
    """

    # Features and labels are separated in three different numpy structures: one for continuous features, one for
    # categorical features and the third one for the target/s
    cat = titanic_cooked[CAT_COLUMN_NAMES_BI].values
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
    for col_n in CAT_COLUMN_NAMES_BI:
        for v in pd.unique(titanic_cooked[col_n]):
            enc_names.append(col_n + '_{}'.format(v) if isinstance(v, str) else col_n + '_{:.1f}'.format(v))
    enc_names.append(TARGET)

    # Original DataFrame is rebuilt, so that its structure matches the column name list built in the previous step
    data = np.concatenate((cont, cat_enc.toarray(), tar), axis=1)
    model_train_df = pd.DataFrame(data, columns=enc_names)

    # With the aforementioned DataFrame, a new model is instantiated and trained. Prediction for the same DataFrame is
    # retrieved too
    model = RandomForestClassifier()
    model.fit(model_train_df.drop([TARGET], axis=1).values, model_train_df[TARGET].values)
    pre_prediction = model.predict(model_train_df.drop([TARGET], axis=1).values)
    logging.info('TRAIN ACCURACY: {:.4f}'.format(accuracy_score(model_train_df[TARGET].values, pre_prediction)))

    # Target column is replaced in the ORIGINAL dataset (not the one with the dummy variables) by the prediction column
    rf_predict = titanic_cooked.drop([TARGET], axis=1)
    rf_predict[TARGET] = pre_prediction

    # Original dataset is returned exactly as it was received but including the model prediction. Column order must
    # remain the same
    return rf_predict[CONT_COLUMN_NAMES + CAT_COLUMN_NAMES_BI + TAR_COLUMN_NAMES]


def prepare_titanic(multi_label: bool) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """


    :param multi_label:
    :return:
    """
    feature_cols = []
    target_cols = []
    # This first step represents the dataset preprocessing, in other words: all that is needed to do to the dataset
    # so that the predictive model will successfully train from it. It's important to remark that it is the user who
    # is responsible for this step
    df_titanic_cooked = titanic_cooking(multi_label=multi_label)

    if multi_label:
        for col in df_titanic_cooked.columns:
            if col.startswith(TARGET):
                target_cols.append(col)
            else:
                feature_cols.append(col)
        return df_titanic_cooked, feature_cols, target_cols

    # A predictive model (in this case a Random Forest Classifier) is used to train and predict. These predictions
    # replace the original target in the dataset provided as parameter. Then, the resulting DataFrame is returned. Again
    # it is the user who is responsible for this step too
    df_titanic_prediction = random_forest_titanic(titanic_cooked=df_titanic_cooked)
    for col in df_titanic_prediction.columns:
        if col.startswith(TARGET):
            target_cols.append(col)
        else:
            feature_cols.append(col)

    return df_titanic_prediction, feature_cols, target_cols


def main():
    logging.set_verbosity(logging.INFO)
    multi_label_problem = True
    output_path = Path.joinpath(Path(__file__).parent.parent.absolute(), TefShap.__name__, 'Titanic')
    print(output_path)

    df_titanic_cooked, feature_cols, target_cols = prepare_titanic(multi_label=multi_label_problem)

    # This next step consists on;
    # - Continuous features discretization
    # - Categorical feature cleansing/dimensionality reduction (neither os these are necessary for Titanic dataset)
    # Right now, this step falls also on the user's side. However at some point the library might also take care of it
    # Right now, it is necessary that headers consist only of strings
    titanic_2_explain = discretize_titanic(multi_label=multi_label_problem, titanic_prediction=df_titanic_cooked,
                                           target_cols=target_cols)

    # Cálculo de estadísticos
    # Sobre df_2_explain: target_distribution.csv group by count por target_cols
    # if target_distribution.csv must be generated the following steps must be followed
    target_count = np.sum(titanic_2_explain[target_cols].values, axis=0).reshape(-1, 1)
    pd.DataFrame(np.concatenate((np.array(target_cols).reshape(-1, 1),
                                 target_count,
                                 target_count / np.sum(target_count)), axis=1),
                 columns=[TARGET, COUNT, PERCENTAGE]).to_csv(
        '/home/cx02747/Utils/target_distribution.csv', sep=',', index=False)

    # if global_explainability_graph_edges_weights.csv must be generated the following steps must be followed
    float_feature_cols = titanic_2_explain[feature_cols].select_dtypes(include='float')
    for feature_col in feature_cols:
        if feature_col in float_feature_cols:
            titanic_2_explain[feature_col] = feature_col + '_' + titanic_2_explain[feature_col].apply(
                "{:.02f}".format).map(str)
        else:
            titanic_2_explain[feature_col] = feature_col + '_' + titanic_2_explain[feature_col].map(str)

    top1_argmax = np.argmax(titanic_2_explain[target_cols].values, axis=1)
    top1_target = np.array([target_cols[am] for am in top1_argmax])
    titanic_2_explain[TARGET] = top1_target
    feature_cols_combinations = itertools.combinations(feature_cols, 2)
    df_global_graph_edges_list = []
    df_local_graph_edges_list = []
    for feature_cols_tuple in feature_cols_combinations:
        feature_cols_pair = list(feature_cols_tuple)
        df_local_graph_edges_list.append(titanic_2_explain[[ID, TARGET] + feature_cols_pair].rename(
                columns={feature_cols_pair[0]: NODE_1, feature_cols_pair[1]: NODE_2}))
        df_global_graph_edges_list.append(
            titanic_2_explain[[TARGET] + feature_cols_pair].value_counts().reset_index(name='edge_weight').rename(
                columns={feature_cols_pair[0]: NODE_1, feature_cols_pair[1]: NODE_2}))

    df_global_graph_edges = pd.concat(df_global_graph_edges_list).sort_values(by=[TARGET, NODE_1, NODE_2]).reset_index(
        drop=True)
    df_local_graph_edges_wo_weight = pd.concat(df_local_graph_edges_list).sort_values(
        by=[ID, NODE_1, NODE_2]).reset_index(drop=True)
    df_local_graph_edges = df_local_graph_edges_wo_weight.merge(df_global_graph_edges, how='left', on=[TARGET, NODE_1,
                                                                                                       NODE_2])
    df_local_graph_edges.to_pickle('/home/cx02747/Utils/local_edges_final.pkl')
    exit(0)
    # From here, the Explainer main flow starts
    # TEF_SHAP explainer is instantiated
    explainer = TefShap(explainer_params={})

    # Explainer is trained here. Just like in Machine Learning, the dataset must accurately represent the problem domain
    # to obtain valid results
    explainer_trained = explainer.train(titanic_2_explain.drop(ID, axis=1), target_cols=target_cols)

    # The trained Explainer is used to provide local explainability. In this case the dataset to train and to explain
    # are identical. However, this isn't always the case. They can be different
    local_explanation = explainer.local_explain(df_2_explain=titanic_2_explain,
                                                target_cols=target_cols,
                                                **explainer_trained)

    # Usamos el explainer para generar la información global (tantos números como features)
    global_explanation = explainer.global_explain(feature_cols=feature_cols, target_cols=target_cols,
                                                  **local_explanation)
    print(global_explanation.shape)

    ####################################################################################################################
    # EXPORTACIÓN DE LOS DATOS CALCULADOS PARA SU VISUALIZACIÓN WEB
    ####################################################################################################################
    # TODO: Exportar toda la información generado a CSV para su visualización web


if __name__ == '__main__':
    main()
