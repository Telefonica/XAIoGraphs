import numpy as np
import pandas as pd

from datasets.titanic_cooking import titanic_cooking
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer
from xaiographs.exgraph.explainer_factory import ExplainerFactory

CAT_COLUMN_NAMES = ['family_size', 'embarked', 'sex', 'pclass', 'title', 'is_alone']
CONT_COLUMN_NAMES = ['age', 'fare']
COUNT_COLUMN = 'count'
QUANTILE_SIZE = 10
TARGET_COLUMN = 'target'
TAR_COLUMN_NAMES = [TARGET_COLUMN]


def random_forest_titanic(titanic_cooked):
    """
    A partir del dataset original, se entrenamo un modelo de predicción, en este caso RandomForest, y sobre este
    dataset se sustituye el target original por la predicción del modelo entrenado.

    :params: titanic_cooked: pd.Dataframe: dataframe de origen
    :return: rf_predict: pd.Dataframe: dataframe de origen al que se le ha sustituido la columna 'target' original
                                       por la predicción del modelo entrenado, en este caso, RandomForest
    """

    # Separamos las features según su naturaleza
    cont = titanic_cooked[CONT_COLUMN_NAMES].values
    cat = titanic_cooked[CAT_COLUMN_NAMES].values
    tar = titanic_cooked[TAR_COLUMN_NAMES].values

    # Creamos el OHE a partir de las features categóricas
    enc = OneHotEncoder()
    enc.fit(cat)
    cat_enc = enc.transform(cat)

    # Creamos una colección de features dummy para en función de los posibles valores de las features categóricas
    enc_names = CONT_COLUMN_NAMES.copy()
    for col_n in CAT_COLUMN_NAMES:
        for v in pd.unique(titanic_cooked[col_n]):
            enc_names.append(col_n + '_{}'.format(v) if isinstance(v, str) else col_n + '_{:.1f}'.format(v))
    enc_names.append(TARGET_COLUMN)

    # Reconstruimos el dataframe original usando la colección de features dummy anteriormente calculadas
    data = np.concatenate((cont, cat_enc.toarray(), tar), axis=1)
    model_train_df = pd.DataFrame(data, columns=enc_names)

    # Generamos y entrenamos un modelo, en este caso RandomForest, a partir de los datos y obtenemos la predicción
    model = RandomForestClassifier()
    model.fit(model_train_df.drop([TARGET_COLUMN], axis=1).values, model_train_df[TARGET_COLUMN].values)
    pre_prediction = model.predict(model_train_df.drop([TARGET_COLUMN], axis=1).values)

    print('TRAIN ACCURACY: {:.4f}'.format(accuracy_score(model_train_df[TARGET_COLUMN].values, pre_prediction)))

    # Sustituimos la columna 'target' del dataset original por la predicción del modelo
    rf_predict = titanic_cooked.drop([TARGET_COLUMN], axis=1)
    rf_predict[TARGET_COLUMN] = pre_prediction

    # Devolvemos el dataset con la predicción, asegurandonos del órden de las columnas
    return rf_predict[CONT_COLUMN_NAMES + CAT_COLUMN_NAMES + TAR_COLUMN_NAMES]


def discretize_titanic(titanic_rf_prediction: pd.DataFrame) -> pd.DataFrame:
    """
    Esta función permite discretizar todas las variables continuas del dataset a analizar para cumplir con los
    requerimientos del explainer.

    :params: titanic_rf_prediction: pd.DataFrame: dataframe a explicar sin discretizar
    :return: df_2_explain: pd.Dataframe: dataframe a explicar discretizado y preparado para el explainer
    """

    # Tomamos del dataset las features continuas
    cont_vars_train = titanic_rf_prediction[CONT_COLUMN_NAMES]

    # Calculamos los cuantiles para las variables continuas, en este caso se usarán los deciles (10)
    qt = QuantileTransformer(n_quantiles=QUANTILE_SIZE, random_state=0)
    qt.fit(cont_vars_train)
    cont_train = qt.transform(cont_vars_train)

    # Generamos un datasource a partir de las variables continuas calculadas en el paso anterior y las restantes
    # columnas (categóricas y target) del dataframe original
    datasource_2_explain = np.concatenate((cont_train, titanic_rf_prediction[CAT_COLUMN_NAMES].values,
                                           titanic_rf_prediction[TAR_COLUMN_NAMES].values), axis=1).tolist()

    # Generamos un dataframe a partir del datasource creado en el paso anterior
    df_2_explain = pd.DataFrame(datasource_2_explain, columns=CONT_COLUMN_NAMES + CAT_COLUMN_NAMES + TAR_COLUMN_NAMES)

    for col_name in CONT_COLUMN_NAMES:
        df_2_explain[col_name] = round(df_2_explain[col_name], int(QUANTILE_SIZE/10)) + 0.05


    # Devolvemos el dataframe con las features continuas discretizadas, asegurándonos del formate de las columnas
    return df_2_explain.astype({TARGET_COLUMN: 'float', 'is_alone': 'float'})


def main():
    """
    Función principal del ejemplo de explicabilidad aplicada al dataset de supervivientes del Titanic
    """

    ####################################################################################################################
    # PREPARACIÓN DEL DATASET PARA SU PROCESAMIENTO
    ####################################################################################################################
    # Lectura y preprocesamiento de las features (x) para el modelo complejo que queremos explicar,
    # por ejemplo RandomForest
    titanic_cooked = titanic_cooking()

    # Generamos el dataframe con las predicciones del modelo complejo, por ejemplo RandomForest, a explicar
    titanic_rf_prediction = random_forest_titanic(titanic_cooked)

    # Preprocesamiento de las features (x) para el explainer:
    #   1.- Discretización de las features continuas
    #   2.- Limpieza de features categoricas (no aplica en ese ejemplo de Titanic)
    titanic_2_explain = discretize_titanic(titanic_rf_prediction)


    ####################################################################################################################
    # FLUJO PRINCIPAL DEL EXPLAINER
    ####################################################################################################################
    # Creamos el explainer específico de TEF_SHAP
    explainer = ExplainerFactory().build_explainer(name='TEF_SHAP', explainer_params={})

    # Entrenamos el explainer
    explainer_trained = explainer.train(titanic_2_explain, target_cols=TAR_COLUMN_NAMES, count_col=COUNT_COLUMN)
    # Usamos el explainer para generar la información local

    local_explanation = explainer.local_explain(df_discretized=titanic_2_explain,
                                                target_cols=TAR_COLUMN_NAMES,
                                                count_col=COUNT_COLUMN,
                                                res_dict=None,
                                                **explainer_trained)
    # Usamos el explainer para generar la información global
    global_explanation = explainer.global_explain(**local_explanation)


    ####################################################################################################################
    # EXPORTACIÓN DE LOS DATOS CALCULADOS PARA SU VISUALIZACIÓN WEB
    ####################################################################################################################
    # TODO: Exportar toda la información generado a CSV para su visualización web


if __name__ == '__main__':
    main()
