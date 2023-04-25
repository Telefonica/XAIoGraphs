[< 📚 User Guide](user_guide/user_guide)

(user_guide/fairness)=
# 3. Fairness

[`Fairness`](../api_reference/fairness.md) class offers functionalities to explain how ***fair or unfair are the 
classifications*** made by a (Deep) Machine Learning model on a set of features that we consider sensitive 
(gender, age, ethnic group, religion, etc.).

These explanations are based on three fairness criterias ([Independence](#independence-criterion), 
[Separation](#separation-criterion), and [Sufficiency](#sufficiency-criterion)) that are used to determine if a 
classification model is fair. It will be regarded fair if none of the sensitive features influence 
its predictions.

***Fairness Scores*** and ***Fairness Category*** are calculated based on the definitions of each fairness criterion in 
order to explain and indicate which target class and which value of the sensitive feature is committing a possible 
injustice in classification.


To perform these calculations we need a dataset with the following characteristics:
- 'N' columns with features
- Column with target class ('y_true')
- Column with predictions class ('y_predict')
- List of sensitive features to be examined


Below is an example of a dataset, taking ['Gender'] as list of sensitive features to be examined:

| Gender | y_true | y_predict |
|:------:|:------:|:---------:|
|  MAN   |  YES   | YES       |
|  MAN   |  YES   | YES       |
| WOMAN  |   NO   | NO        |
|  MAN   |   NO   | YES       |
| WOMAN  |  YES   | NO        |
|  MAN   |  YES   | NO        |
|  MAN   |  YES   | YES       |
| WOMAN  |  YES   | YES       |
|  MAN   |   NO   | NO        |
| WOMAN  |   NO   | NO        |


## Independence criterion

We say that the random variables (Y, A) satisfy independence if the sensitive feature 'A' are statistically 
independent of the prediction 'Y'.

$$
independence =  P\left ( Y=c \mid A=a \right )
$$

That is, the probability of being classified by the model in each of the classes must be the same for two elements 
with different sensitive feature values (Demographic Parity).

```{attention}
The acceptance rate must be equal for each group (A=a, A=b)
```

We define the Independence Score as:

$$
independence\ score= \left | P\left ( Y=c \mid A=a \right ) - P\left ( Y=c \mid A=b \right ) \right |
$$

```{hint}
Taking the example dataset above, we calculate the independence score as:

$$
P(Y = 'YES' | A = 'MAN') = \frac{4}{6} = 0.66

P(Y = 'YES' | A = 'WOMAN') = \frac{1}{4} = 0.25
$$
$$
independence\ score = |0.66 - 0.25| = 0.41
$$

```


## Separation criterion

We say the random variables (Y, A, T) satisfy separation if the sensitive characteristics 'A' are statistically 
independent of the prediction 'Y' given the target value 'T'.

$$
separation = P\left ( Y=c \mid T=c, A=a \right ) 
$$

That is, the probability of being classified by the model in each of the classes is the same for two elements with 
different sensitive feature values, given that both belong to the same group (Equal opportunities).

```{attention}
The probability of predicting a true positive or a false positive for each group (A=a, A=b) must be the same.
```

We define the separation score as: 

$$
separation\ score= \left | P\left ( Y=c \mid T=c, A=a \right ) - P\left ( Y=c \mid T=c, A=b \right ) \right |
$$

```{hint}
Taking the example dataset above, we calculate the separation score as:

$$
P(Y = 'YES' | T = 'YES', A = 'MAN') = \frac{3}{4} = 0.75

P(Y = 'YES' | T = 'YES', A = 'WOMAN') = \frac{1}{2} = 0.5
$$
$$
separation\ score = |0.75 - 0.5| = 0.25
$$
```


## Sufficiency criterion

We say the random variables (Y, A, T) satisfy sufficiency if the sensitive characteristics 'A' are statistically 
independent of the target value 'T' given the prediction 'Y'.

$$
sufficiency\ score=  P\left ( T=c \mid Y=c, A=a \right ) 
$$

That is, the probability of being classified by the model in each of the classes is the same for two elements with 
different sensitive feature values, since the prediction includes them in the same group (Predictive Parity).

```{attention}
The probability that two elements with different values of the sensitive feature are well classified must be the same.
```

We define the sufficiency score as: 

$$
sufficiency\ score= \left | P\left ( T=c \mid Y=c, A=a \right ) - P\left ( T=c \mid Y=c, A=b \right ) \right |
$$


```{hint}
Taking the example dataset above, we calculate the sufficiency score as:

$$
P(T = 'YES' | Y = 'YES', A = 'MAN') = \frac{3}{4} = 0.75

P(T = 'YES' | Y = 'YES', A = 'WOMAN') = \frac{1}{1} = 1.0
$$
$$
sufficiency\ score = |0.75 - 1.0| = 0.25
$$
```


## Fairness Category

In order to make the equity results easier to grasp, some categories have been established that identify the 
features and values on which You might be committing discrimination with a color code from green to red (similar 
to that used in other industries like Nutriscore or energy efficiency).

Below are the categories and theirs score ranges:


|Category|     Range Score      |
|:------:|:--------------------:|
|A+      | 0.0 <= score <= 0.02 |
|A       | 0.02 < score <= 0.05 |
|B       | 0.05 < score <= 0.08 |
|C       | 0.08 < score <= 0.15 |
|D       | 0.15 < score <= 0.25 |
|E       | 0.25 < score <= 1.0  |


Each of those categories has the following color designation:

```{image} ../../imgs/XaioWeb_Fairness_Legend.png
:alt: XaioWeb Fairness Legend
:class: bg-primary
:width: 600px
:align: center
```

## Example

To demonstrate how to apply the [`Fairness`](../api_reference/fairness.md) class's features, consider the following 
dataset, which has two features (gender and title) and two columns, one with the true class (`y_true`) 
and another with the model's prediction (`y_predict`).

&nbsp;

```python
>>> import pandas as pd
>>> df = pd.DataFrame({'gender': ['MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN', 'MAN', 'MAN', 'WOMAN', 'MAN', 'WOMAN'],
...                    'title': ['Mr', 'Mr', 'Mrs', 'Mr', 'Mrs', 'Mr', 'Mr', 'Mrs', 'Mr', 'Mrs'],
...                    'y_true': ['YES', 'YES', 'NO', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO'],
...                    'y_predict': ['YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'YES', 'YES', 'NO', 'NO']},
...                   columns=['gender', 'title', 'y_true', 'y_predict'])
>>> df
  gender title y_true y_predict
0    MAN    Mr    YES       YES
1    MAN    Mr    YES       YES
2  WOMAN   Mrs     NO        NO
3    MAN    Mr     NO       YES
4  WOMAN   Mrs    YES        NO
5    MAN    Mr    YES        NO
6    MAN    Mr    YES       YES
7  WOMAN   Mrs    YES       YES
8    MAN    Mr     NO        NO
9  WOMAN   Mrs     NO        NO
```

&nbsp;

[`fit()`](../api_reference/fairness.md#xaiographs.Fairness.fit) method in the [`Fairness`](../api_reference/fairness.md)
class conducts all Fairness computations (score and category). `df`,`sensitive_cols`, `target_col`, and `predict_col` 
parameters are required by the [`fit()`](../api_reference/fairness.md#xaiographs.Fairness.fit) method:

&nbsp;

```python
>>> from xaiographs import Fairness
>>> f = Fairness()
>>> f.fit(df=df, 
...       sensitive_cols=['gender'], 
...       target_col='y_true', 
...       predict_col='y_predict')
```

&nbsp;

We retrieve the global Fairness criteria results by accessing the various attributes (properties). We get a DataFrame 
with the scores and categories of the fairness criterion for each of the sensitive features when we use 
the [`fairness_global_info`](../api_reference/fairness.md#xaiographs.Fairness.fairness_global_info) attribute:

&nbsp;

```python
>>> f.fairness_global_info
  sensitive_feature  independence_global_score independence_category  separation_global_score separation_category  sufficiency_global_score sufficiency_category
0            gender                   0.416667                     E                    0.375                   E                  0.216667                    D
```

&nbsp;

The attributes [`independence_info`](../api_reference/fairness.md#xaiographs.Fairness.independence_info), 
[`separation_info`](../api_reference/fairness.md#xaiographs.Fairness.separation_info), and 
[`sufficiency_info`](../api_reference/fairness.md#xaiographs.Fairness.sufficiency_info) 
are accessible for more information on the calculation of Fairness criteria:

&nbsp;

```python
>>> f.independence_info
  sensitive_feature sensitive_value target_label  independence_score independence_category
0            gender     MAN | WOMAN          YES            0.416667                     E
1            gender     MAN | WOMAN           NO            0.416667                     E

>>> f.separation_info
  sensitive_feature sensitive_value target_label  separation_score separation_category
0            gender     MAN | WOMAN          YES          0.250000                   D
1            gender     MAN | WOMAN           NO          0.500000                   E

>>> f.sufficiency_info
  sensitive_feature sensitive_value target_label  sufficiency_score sufficiency_category
0            gender     MAN | WOMAN          YES           0.250000                    D
1            gender     MAN | WOMAN           NO           0.166667                    D
```

&nbsp;

[`fairness_info`](../api_reference/fairness.md#xaiographs.Fairness.fairness_info) attribute is available to obtain all 
the information of all the Fairness criteria, which returns all the scores and categories as well as the weight of 
each feature value:

&nbsp;

```python
>>> f.fairness_info
  sensitive_feature sensitive_value  is_binary_sensitive_feature target_label independence_score independence_category  independence_score_weight separation_score separation_category  separation_score_weight sufficiency_score sufficiency_category  sufficiency_score_weight
0            gender     MAN | WOMAN                         True          YES           0.416667                     E                        0.5             0.25                   D                      0.5          0.250000                    D                       0.6
1            gender     MAN | WOMAN                         True           NO           0.416667                     E                        0.5             0.50                   E                      0.5          0.166667                    D                       0.4
```

&nbsp;

We have included a table to help you comprehend these recent results:

|Column Name                 | elem 0        | elem 1       |
|----------------------------|---------------|--------------|
|sensitive_feature           | gender        | gender       |
|sensitive_value             | MAN - WOMAN   | MAN - WOMAN  |
|is_binary_sensitive_feature | True          | True         |
|target_label                | YES           | NO           |
|independence_score          | 0.416667      | 0.416667     |
|independence_category       | E             | E            |
|independence_score_weight   | 0.5           | 0.5          |
|separation_score            | 0.25          | 0.50         |
|separation_category         | D             | E            |
|separation_score_weight     | 0.5           | 0.5          |
|sufficiency_score           | 0.250000      | 0.166667     |
|sufficiency_category        | D             | D            |
|sufficiency_score_weight    | 0.6           | 0.4          |


The Fairness class also offers complementary information such as:

* Confusion Matrix


```python
>>> f.confusion_matrix
y_predict  NO  YES
y_true
NO          3    1
YES         2    4
```
&nbsp;

* Matrix of correlations (pearson) between features:


```python
>>> f.correlation_matrix
        gender  title
gender     NaN    1.0
title      NaN    NaN
```
&nbsp;

* List of highly correlated features ($pearson \geq 0.9$) for proxy feature detection.


```python
>>> f.highest_correlation_features
  feature_1 feature_2  correlation_value  is_correlation_sensible
0     title    gender                1.0                     True
```

[< 📚 User Guide](user_guide/user_guide)