[< 📚 User Guide](user_guide/user_guide)

(user_guide/datasets)=
# Datasets

To test the capabilities of XAIoGraphs, it provides a series of datasets via 
[xaiographs.datasets](../api_reference/datasets.md) module's features.

The following datasets are included:

| Datset                                          | Rows  | Num. Feats |      Task       |
|:------------------------------------------------|:-----:|:----------:|:---------------:|
| [Titanic](#titanic)                             | 1309  |     8      |     Binary      |
| [Body Performace](#body-performance)            | 13393 |     11     | Multi-Class (3) | 
| [Education Performance](#education-performance) |  145  |     29     | Multi-Class (5) |

[//]: # (| [Compas]&#40;#compas&#41;                               | ????  |    ????    |     Binary      |)

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




[//]: # (&nbsp;)

[//]: # (## Compas)

[//]: # ()
[//]: # (|                                              |                                                                                                   |)

[//]: # (|----------------------------------------------|---------------------------------------------------------------------------------------------------|)

[//]: # (| **Source**                                   | [https://github.com/propublica/compas-analysis]&#40;https://github.com/propublica/compas-analysis&#41;    |)

[//]: # (| **Num Rows:**                                | TBD                                                                                               |)

[//]: # (| **Num Features**                             | TBD                                                                                               |)

[//]: # (| **Num Targets:**                             | TBD                                                                                               |)

[//]: # (| **function to obtain dataset**               | [`xaiographs.datasets.TBD&#40;&#41;`]&#40;../api_reference/datasets.md#xaiographs.datasets.TBD&#41;               | )

[//]: # (| **function to obtain discretized dataset**   | [`xaiographs.datasets.TBD&#40;&#41;`]&#40;../api_reference/datasets.md#xaiographs.datasets.TBD&#41;               |)


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


[< 📚 User Guide](user_guide/user_guide)