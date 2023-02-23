from xaiographs import Explainer
from xaiographs import Why
from xaiographs import Fairness
from xaiographs.datasets import load_titanic_discretized, load_titanic_why


def main():
    # LOAD DATASETS & SEMANTICS
    df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
    df_global_semantics, df_target_semantics, df_why_templates = load_titanic_why(language='es')

    # EXPLAINER
    explainer = Explainer(dataset=df_titanic, importance_engine='TEF_SHAP', verbose=1)
    explainer.fit(feature_cols=feature_cols, target_cols=target_cols)

    # WHY
    why = Why(language='es',
              local_reliability=explainer.local_dataset_reliability,
              local_feat_val_expl=explainer.local_feature_value_explainability,
              why_elements=df_global_semantics,
              why_templates=df_why_templates,
              why_target=df_target_semantics,
              sample_ids_to_export=explainer.sample_ids_to_display,
              verbose=1)
    why.fit()

    # FAIRNESS
    f = Fairness(verbose=1)
    f.fit(df=df_titanic[feature_cols + [y_true] + [y_predict]],
          sensitive_cols=['gender', 'class', 'age'],
          target_col=y_true,
          predict_col=y_predict)


if __name__ == "__main__":
    main()
