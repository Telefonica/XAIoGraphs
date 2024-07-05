[< 📚 User Guide](user_guide/user_guide)

(user_guide/datasets)=
# Datasets

To test the capabilities of XAIoGraphs, it provides a series of datasets via 
[xaiographs.datasets](../api_reference/datasets.md) module's features.

The following datasets are included:

| Dataset                                                         | Rows  | Num. Feats |       Task       |
|:----------------------------------------------------------------|:-----:|:----------:|:----------------:|
| [Titanic](titanic.md)                                           | 1309  |     8      |      Binary      |
| [COMPAS](compas.md)                                             | 4230  |     7      | Multi-Class (3)  |
| [COMPAS Reality](compas_reality.md)                             | 4230  |     7      |      Binary      |
| [Body Performace](body_performance.md)                          | 13393 |     11     | Multi-Class (3)  | 
| [Education Performance](education_performance.md)               |  145  |     29     | Multi-Class (5)  |
| [Smartphone Brand Preferences](smartphone_brand_preferences.md) |  981  |     17     | Multi-Class (5)  |

These datasets are accessible in both raw and discretized form, ready for usage by the 
[`Explainability`](../api_reference/explainability.md)  and [`Fairness`](../api_reference/fairness.md) classes.

The details of these Datasets are shown below:

```{note}
The original Datasets have been treated to remove outlayers, impute null values, and so on.
```

&nbsp;

## Titanic


The supposedly "unsinkable" RMS Titanic sank on April 15, 1912, during her first voyage after hitting an iceberg. 
Unfortunately, there were not enough lifeboats to accommodate everyone, and 1502 out of 2224 passengers and staff 
perished.Individual Titanic passengers' chances of survival are described in the famous `Titanic Dataset`.



|                                              |                                                                                                                               |
|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **Source**                                   | [https://www.kaggle.com/c/titanic](https://www.kaggle.com/c/titanic)                                                          |
| **Num Rows:**                                | 1309                                                                                                                          |
| **Num Features**                             | 8                                                                                                                             |
| **Num Targets:**                             | 2                                                                                                                             |
| **function to obtain dataset**               | [`xaiographs.datasets.load_titanic()`](../api_reference/datasets.md#xaiographs.datasets.load_titanic)                         | 
| **function to obtain discretized dataset**   | [`xaiographs.datasets.load_titanic_discretized()`](../api_reference/datasets.md#xaiographs.datasets.load_titanic_discretized) |




&nbsp;
## Compas

COMPAS (Correctional Offender Management Profiling for Alternative Sanctions) is a popular commercial algorithm used 
by judges and parole officers for scoring criminal defendant’s likelihood of reoffending (recidivism). It has been 
shown that the algorithm is biased in favor of white defendants, and against black inmates, based on a 2 year follow 
up study (i.e who actually committed crimes or violent crimes after 2 years). The pattern of mistakes, as measured 
by precision/sensitivity is notable.

|                                                      |                                                                                                                                             |
|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| **Source**                                           | [https://github.com/propublica/compas-analysis](https://github.com/propublica/compas-analysis)                                              |
| **Num Rows:**                                        | 4230                                                                                                                                        |
| **Num Features**                                     | 7                                                                                                                                           |
| **Num Targets:**                                     | 3 (model) - 2 (reality)                                                                                                                     |
| **function to obtain dataset**                       | [`xaiographs.datasets.load_compas()`](../api_reference/datasets.md#xaiographs.datasets.datasets.load_compas)                                | 
| **function to obtain discretized dataset (Model)**   | [`xaiographs.datasets.load_compas_discretized()`](../api_reference/datasets.md#xaiographs.datasets.load_compas_discretized)                 |
| **function to obtain discretized dataset (Reality)** | [`xaiographs.datasets.load_compas_reality_discretized()`](../api_reference/datasets.md#xaiographs.datasets.load_compas_reality_discretized) |


&nbsp;
## Body Performance


This dataset demonstrates how performance levels change with age and some exercise-related variables.

|                                              |                                                                                                                                                 |
|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| **Source**                                   | [https://www.kaggle.com/datasets/kukuroo3/body-performance-data](https://www.kaggle.com/datasets/kukuroo3/body-performance-data)                |
| **Num Rows:**                                | 13393                                                                                                                                           |
| **Num Features**                             | 11                                                                                                                                              |
| **Num Targets:**                             | 3                                                                                                                                               |
| **function to obtain dataset**               | [`xaiographs.datasets.load_body_performance()`](../api_reference/datasets.md#xaiographs.datasets.load_body_performance)                         | 
| **function to obtain discretized dataset**   | [`xaiographs.datasets.load_body_performance_discretized()`](../api_reference/datasets.md#xaiographs.datasets.load_body_performance_discretized) |


&nbsp;
## Education Performance

The data was collected from the Faculty of Engineering and Faculty of Educational Sciences students in 2019. The 
purpose is to predict students' end-of-term performances using ML techniques.

|                                              |                                                                                                                                                                                                  |
|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Source**                                   | [https://www.kaggle.com/datasets/mariazhokhova/higher-education-students-performance-evaluation](https://www.kaggle.com/datasets/mariazhokhova/higher-education-students-performance-evaluation) |
| **Num Rows:**                                | 145                                                                                                                                                                                              |
| **Num Features**                             | 29                                                                                                                                                                                               |
| **Num Targets:**                             | 5                                                                                                                                                                                                |
| **function to obtain dataset**               | [`xaiographs.datasets.load_education_performance()`](../api_reference/datasets.md#xaiographs.datasets.load_education_performance)                                                                | 
| **function to obtain discretized dataset**   | [`xaiographs.datasets.load_education_performance_discretized()`](../api_reference/datasets.md#xaiographs.datasets.load_education_performance_discretized)                                        |

&nbsp;
## Smartphone Brand Preferences

The data was collected through a combination of three datasets containing the most noteworthy features on the preferred smartphones in the US in 2022, user's data and smartphone ratings. This information was obtained via a Mechanical Turk survey where participants assessed 10 randomly presented phones by likelihood of purchase and provided personal information. This example highlights the most important features smartphones from certain brands have, to predict the most likely smartphone-brand purchase.

|                                              |                                                                                                                                                                                                  |
|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Source**                                   | [https://www.kaggle.com/datasets/meirnizri/cellphones-recommendations/data?select=cellphones+ratings.csv](https://www.kaggle.com/datasets/meirnizri/cellphones-recommendations/data?select=cellphones+ratings.csv) |
| **Num Rows:**                                | 259                                                                                                                                                                                              |
| **Num Features**                             | 11                                                                                                                                                                                               |
| **Num Targets:**                             | 5                                                                                                                                                                                                |
| **function to obtain dataset**               | [`xaiographs.datasets.load_phone_brand_preferences()`](../api_reference/datasets.md#xaiographs.datasets.load_education_performance)                                                                | 
| **function to obtain discretized dataset**   | [`xaiographs.datasets.load_phone_brand_preferences_discretized()`](../api_reference/datasets.md#xaiographs.datasets.load_education_performance_discretized)                                        |


[< 📚 User Guide](user_guide/user_guide)