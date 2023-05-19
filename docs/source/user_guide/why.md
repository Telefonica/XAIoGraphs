[< 📚 User Guide](user_guide/user_guide)

(user_guide/why)=
# 2. Why


[`Why`](../api_reference/why.md) class provides the functionality of writing in natural language the `reason why` 
for which an element has been classified in a specific class (target value) based on the local explainability results 
offered by the [`Explainer`](../api_reference/explainability.md)  class.


&nbsp;

## Requirements


To generate a natural language sentence that explains `Reason Why` a dataset element has been classified in a 
certain class, you will need: 
- An object of the [`Explainer`](../api_reference/explainability.md) class, executed with the explainability of each element (local explainability).
- Semantics, including a description of each Feature-Value.
- Template for Natural Language Sentences is optional.



```{note}
These templates are available in English and Spanish by default in XAIoGraphs.
```

&nbsp;

## Composing Reason Why

The "Reason Why" sentences for each element are created using a sequence of templates, such as the ones below:

| Templates                                                                                                                     |
|-------------------------------------------------------------------------------------------------------------------------------|
| An explanation cannot be offered for this case.                                                                               |
| For `$temp_values_explain`, this case has been classified as `$target`, considering that `$temp_target_values_explain`.       |
| For `$temp_values_explain`, this case has been classified as `$target`, because `$temp_target_values_explain`.                |
| This case has been classified as `$target` because `$temp_values_explain`, due to `$temp_target_values_explain`.              |
| The classification of this case as `$target` is due to `$temp_values_explain`, because `$temp_target_values_explain`.         |
| As `$temp_target_values_explain`, and this case is characterized by `$temp_values_explain`, has been classified as `$target`. |


`$target` parameter is replaced by the name of the target in which the element has been classified.


Let's now see how to complete the `$temp_values_explain` and `$temp_target_values_explain` parameters.


When working with XAIoGraphs with discretized data, it is required to have an object of the 
[`Explainer`](../api_reference/explainability.md) class that has the importance of its features determined for each 
element; in particular, the importance of the Feature-Value.


For example, consider the following element (see [Titanic example](../examples/titanic.md)):


|gender| title|          age| family_size|  is_alone| embarked|  class| ticket_price| target    | 
|------|------|-------------|------------|----------|---------|-------|-------------|-----------|
|female|   Mrs|  18_30_years|           1|         1|        S|      1|         High| SURVIVED  |


The (ordered) importance of its Features-Values as provided by the [`Explainer`](../api_reference/explainability.md)
class is as follows:


| feature_value     | importance |rank|
|-------------------|------------|----|
| gender_female     | 0.191029   | 1  |
| title_Mrs         | 0.189320   | 2  |
| class_1           | 0.147101   | 3  |
| ticket_price_High | 0.101550   | 4  |
| age_18_30_years   | 0.008612   | 5  |
| family_size_1     | 0.004920   | 6  |
| is_alone_1        | 0.004920   | 6  |
| embarked_S        | -0.027895  | 8  |


We will create the `Reason Why` sentence in natural language, expressing the element's most essential 'K' 
Features-Values (gender_female, title_Mrs, class_1,...) using two semantics (`values semantics` and 
`target values semantics`):

&nbsp;

***Values Semantics***


Each Feature-Value (that you want to explain) will be allocated a sentence (semantics) that will be substituted in 
the sentence template's `$temp_values_explain` variable. As an example:


| feature_value     | reason                        |
|-------------------|-------------------------------|
| gender_male       | to be a man                   |
| gender_female     | to be a woman                 |
| is_alone_1        | travel alone                  |
| ...               | ...                           |
| age_12_18_years   | be a teenager                 |
| ...               | ...                           |
| class_1           | travel in 1st class           |
| ...               | ...                           |
| ticket_price_High | pay too much for the ticket   |
| ...               | ...                           |
| embarked_S        | embark in a lower class town  |
| ...               | ...                           |


Using the following template as a reference:

```
For `$temp_values_explain`, this case has been classified as `$target`, considering that `$temp_target_values_explain`.
```


The parameter `$temp_values_explain` will be substituted by `to be a woman and travel alone` (taking the two most 
important values into account), leaving the sentence:


```
For `to be a woman and travel alone`, this case has been classified as `SURVIVED`, considering that 
`$temp_target_values_explain`.
```


The `Values Semantics` will be provided to the constructor of the [`Why`](../api_reference/why.md) class in 
the `why_values_semantics` parameter as a pandas.DataFrame with two columns:
1. **feature_value**: Value of feature
2. **reason**: semantic of this feature-value

&nbsp;

***Target Values Semantics***


For each Feature-Value (that you wish to explain), and depending on the element's target, a phrase (semantics) 
will be assigned and substituted in the sentence template's `$temp_target_values_explain` variable. As an example:


| target      | feature_value     | reason                         |
|-------------|-------------------|--------------------------------|
| SURVIVED    | gender_male       | few men survived               |
| SURVIVED    | gender_female     | many women survived            |
| SURVIVED    | is_alone_1        | they traveled alone            |
| ...         | ...               | ...                            |
| SURVIVED    | age_12_18_years   | they were teenagers            |
| ...         | ...               | ...                            |
| SURVIVED    | class_1           | many traveled in 1st class     |
| ...         | ...               | ...                            |
| SURVIVED    | ticket_price_High | they paid a lot for the ticket |
| ...         | ...               | ...                            |
| SURVIVED    | embarked_S        | few boarded at Southampton     |
| ...         | ...               | ...                            |
| NO_SURVIVED | gender_male       | many men have died             |
| NO_SURVIVED | gender_female     | to be a woman                  |
| NO_SURVIVED | is_alone_1        | they traveled alone            |


Taking as reference the following template:

```
For `$temp_values_explain`, this case has been classified as `$target`, considering that `$temp_target_values_explain`.
```


And since the element is classified as `SURVIVED`, the parameter `$temp_target_values_explain` will be replaced by 
`many women survived and they traveled alone` (taking into account the two most relevant values), leaving the sentence:


```
For `to be a man and travel alone`, this case has been classified as `SURVIVED`, considering that `many women 
survived and they traveled alone`.
```


`Target Values Semantics` semantics will be passed to the constructor of the [`Why`](../api_reference/why.md) class in 
the `why_target_values_semantics` parameter as a pandas.DataFrame with three columns:
1. **target**: target value
2. **feature_value**: Value of feature dependent of target
3. **reason**: semantic of this feature-value dependent of target


```{note}
In case some `Feature-Value` is not to be explained, it should not appear in the semantics. 
(example: `title_Mrs` or `title_Mr`)
```

&nbsp;

***Number of features to explain***

As mentioned before, the `Reason Why` is created based on the importance of the Features-Values of each element, with 
the greatest value being chosen.
The sentence is created by adding the reason for each of the most essential Features-Values, depending on the 
semantics (`values semantics` and `target values semantics`).


We must specify the number of Features-Values to include in the sentences (`$temp_values_explain` and 
`$temp_target_values_explain`) in the `n_values` and `n_target_values` parameters of the 
[`Why`](../api_reference/why.md) class constructor. These parameters are set to 2 by default.

&nbsp;

## Default Reason Why


XAIoGraph (in the [`Explainer`](../api_reference/explainability.md) class) assigns a local explainability reliability 
score between 0 and 1, with 1 being very trustworthy and 0 being unreliable:

```python
>>> explainer.local_reliability.head(10)
   id       target  reliability
0   0     SURVIVED         1.00
1   1     SURVIVED         1.00
2   2  NO_SURVIVED         1.00
3   3  NO_SURVIVED         1.00
4   4  NO_SURVIVED         0.20
5   5     SURVIVED         0.28
6   6     SURVIVED         0.75
7   7  NO_SURVIVED         0.86
8   8     SURVIVED         1.00
9   9  NO_SURVIVED         1.00
```

[`Why`](../api_reference/why.md) class implementation allows passing as a parameter (`min_reliability`) a 
reliability threshold from which it will build the `Reason Why` sentences.
If the reliability value is below than this threshold, the `Reason Why` will use a generic statement as the first 
sentence of the pandas.DataFrame provided as a parameter (`why_templates`) to the [`Why`](../api_reference/why.md)
class constructor:

| Templates                                                                                                               |
|-------------------------------------------------------------------------------------------------------------------------|
| <span style="color:red">An explanation cannot be offered for this case.</span>                                          |
| For `$temp_values_explain`, this case has been classified as `$target`, considering that `$temp_target_values_explain`. |
| ...                                                                                                                     |


In this example, we assign a default sentence to elements with a reliability of less than or equal to 0.3:

```python
>>> from xaiographs import Explainer
>>> from xaiographs import Why
>>> from xaiographs.datasets import load_titanic_discretized, load_titanic_why
>>>
>>> LANG = 'en'
>>>
>>> example_dataset, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
>>> df_values_semantics, df_target_values_semantics = load_titanic_why(language=LANG)
>>>
>>> explainer = Explainer(importance_engine='LIDE', verbose=0)
>>> explainer.fit(df=example_dataset, feature_cols=feature_cols, target_cols=target_cols)
>>> explainer.local_reliability.head(6)
   id       target  reliability
0   0     SURVIVED         1.00
1   1     SURVIVED         1.00
2   2  NO_SURVIVED         1.00
3   3  NO_SURVIVED         1.00
4   4  NO_SURVIVED         0.20
5   5     SURVIVED         0.28
>>>
>>> why = Why(language=LANG,
...           explainer=explainer,
...           why_values_semantics=df_values_semantics,
...           why_target_values_semantics=df_target_values_semantics,
...           min_reliability=0.3,
...           verbose=0)
>>> why.fit()
>>> why.why_explanation.head(6)
   id  reason
0   0  The classification of this case as survived is due to to be a woman and travel in 1st class, because many women survived and many traveled in 1st class.
1   1  The classification of this case as survived is due to travel in 1st class and be a child, because many traveled in 1st class and they were children.
2   2  For travel in 1st class and be a child, this case has been classified as no_survived, considering that few traveled in 1st class and they were children.
3   3  This case has been classified as no_survived because be young and to be a man, due to they were young and many men have died.
4   4  An explanation cannot be offered for this case.
5   5  An explanation cannot be offered for this case.
```

&nbsp;

## Example


To create a `Reason Why`, we must first assess the importance of each feature in the dataset items provided by the 
[`Explainer`](../api_reference/explainability.md) class. Let's look at an example using the 
[`titanic`](../user_guide/datasets.md#titanic) dataset:


```python
>>> from xaiographs import Explainer
>>> from xaiographs.datasets import load_titanic_discretized
>>>
>>> example_dataset, feature_cols, target_cols, _, _ = load_titanic_discretized()
>>>
>>> explainer = Explainer(importance_engine='LIDE', verbose=0)
>>> explainer.fit(df=example_dataset, feature_cols=feature_cols, target_cols=target_cols)  
```


After executing the explainability of the dataset, the [`Explainer`](../api_reference/explainability.md)  class 
returns the local explainability of each element, assigning an importance value to each of its Features 
([`local_feature_value_explainability`](../api_reference/explainability.md#xaiographs.Explainer.local_feature_value_explainability) property).


```python
>>> explainer.local_feature_value_explainability[explainer.local_feature_value_explainability['rank'] <= 3]
    id      feature_value  importance  rank
0    0      gender_female    0.191029     1
1    0          title_Mrs    0.189320     2
2    0            class_1    0.147101     3
10   1            class_1    0.386458     1
15   1      age_<12_years    0.311776     2
14   1         is_alone_0    0.029181     3
23   2      age_<12_years    0.340105     1
18   2            class_1    0.096683     2
20   2         embarked_S    0.037918     3
31   3    age_18_30_years    0.194554     1
25   3           title_Mr    0.153689     2
24   3        gender_male    0.151856     3
36   4         embarked_S    0.144169     1
37   4    family_size_3-5    0.126038     2
38   4         is_alone_0    0.096112     3
42   5            class_1    0.191949     1
43   5  ticket_price_High    0.172900     2
47   5    age_30_60_years    0.090899     3
48   6      gender_female    0.245250     1
49   6          title_Mrs    0.244135     2
50   6            class_1    0.112574     3
...
```


And a reliability value for each of the explanations 
([`local_reliability`](../api_reference/explainability.md#xaiographs.Explainer.local_reliability) property):


```python
>>> explainer.local_reliability
   id       target  reliability
0   0     SURVIVED         1.00
1   1     SURVIVED         1.00
2   2  NO_SURVIVED         1.00
3   3  NO_SURVIVED         1.00
4   4  NO_SURVIVED         0.20
5   5     SURVIVED         0.28
...
```


We need to build a pandas.DataFrame in order to create natural language sentences, containing a succession of 
sentence templates. The first line will always be written by default for those local explicabilities with reliability 
less than a particular threshold, as defined by the `min_reliability` option of the [`Why`](../api_reference/why.md) 
class.

The remaining sentence templates (one or more sentences) will be written in natural language, with the parameters 
`$target`, `$temp_values_explain` and `$temp_target_values_explain` replaced by the target value and the semantics 
associated with each one (see [`Composing Reason Why`](why.md#composing-reason-why)). If more than one sentence 
template is provided, a sentence will be randomly selected to build the `Reason Why` of each element. 

The following is an example of how to construct a pandas.DataFrame of sentence templates:


```python
>>> import pandas as pd
>>> templates=['An explanation cannot be offered for this case.',
...            'For $temp_values_explain, this case has been classified as $target, considering that $temp_target_values_explain.',
...            'As $temp_target_values_explain, and this case is characterized by $temp_values_explain, has been classified as $target.']
>>> df_why_templates = pd.DataFrame(templates)
```

```{note}
These templates are available in English and Spanish by default in XAIoGraphs.
```


We require the two semantics given in the [`Composing Reason Why`](why.md#composing-reason-why) section to compose 
the sentences. XAIoGraphs supports these semantics for the Titanic via the 
[`load_titanic_why()`](../api_reference/datasets.md#xaiographs.datasets.load_titanic_why) method:


```python
>>> from xaiographs.datasets import load_titanic_why
>>> df_values_semantics, df_target_values_semantics = load_titanic_why(language='en')
>>> df_values_semantics
        feature_value                              reason
0         gender_male                         to be a man
1       gender_female                       to be a woman
2          is_alone_1                        travel alone
3       family_size_2  to be from a family of few members
4     family_size_3-5                   be a large family
5      family_size_>5       be a family with many members
6       age_<12_years                          be a child
7     age_12_18_years                       be a teenager
8     age_18_30_years                            be young
9     age_30_60_years                         be an adult
10      age_>60_years                  be an older person
11            class_1                 travel in 1st class
12            class_2                 travel in 2nd class
13            class_3                 travel in 3rd class
14  ticket_price_High         pay too much for the ticket
15   ticket_price_Mid           pay for a mid-cost ticket
16   ticket_price_Low           pay little for the ticket
17         embarked_S        embark in a lower class town
18         embarked_Q     boarding in a middle class town
19         embarked_C       boarding in a high class town
>>> df_target_values_semantics
         target      feature_value                                   reason
0   NO_SURVIVED        gender_male                       many men have died
1   NO_SURVIVED      gender_female                            to be a woman
2   NO_SURVIVED         is_alone_1                      they traveled alone
3   NO_SURVIVED      family_size_2   they were from a family of few members
4   NO_SURVIVED    family_size_3-5            they were from a large family
5   NO_SURVIVED     family_size_>5  they were from a family of many members
6   NO_SURVIVED      age_<12_years                       they were children
7   NO_SURVIVED    age_12_18_years                      they were teenagers
8   NO_SURVIVED    age_18_30_years                          they were young
9   NO_SURVIVED    age_30_60_years                         they were adults
10  NO_SURVIVED      age_>60_years                          they were older
11  NO_SURVIVED            class_1                few traveled in 1st class
12  NO_SURVIVED            class_2               some traveled in 2nd class
13  NO_SURVIVED            class_3               many traveled in 3rd class
14  NO_SURVIVED  ticket_price_High           they paid a lot for the ticket
15  NO_SURVIVED   ticket_price_Mid           they paid a medium cost ticket
16  NO_SURVIVED   ticket_price_Low          they paid little for the ticket
17  NO_SURVIVED         embarked_C                few embarked in Cherbourg
18  NO_SURVIVED         embarked_Q              some embarked in Queenstown
19  NO_SURVIVED         embarked_S              many boarded at Southampton
20     SURVIVED        gender_male                         few men survived
21     SURVIVED      gender_female                      many women survived
22     SURVIVED         is_alone_1                      they traveled alone
23     SURVIVED      family_size_2   they were from a family of few members
24     SURVIVED    family_size_3-5            they were from a large family
25     SURVIVED     family_size_>5  they were from a family of many members
26     SURVIVED      age_<12_years                       they were children
27     SURVIVED    age_12_18_years                      they were teenagers
28     SURVIVED    age_18_30_years                          they were young
29     SURVIVED    age_30_60_years                         they were adults
30     SURVIVED      age_>60_years                          they were older
31     SURVIVED            class_1               many traveled in 1st class
32     SURVIVED            class_2               some traveled in 2nd class
33     SURVIVED            class_3                few traveled in 3rd class
34     SURVIVED  ticket_price_High           they paid a lot for the ticket
35     SURVIVED   ticket_price_Mid           they paid a medium cost ticket
36     SURVIVED   ticket_price_Low          they paid little for the ticket
37     SURVIVED         embarked_C               many embarked in Cherbourg
38     SURVIVED         embarked_Q              some embarked in Queenstown
39     SURVIVED         embarked_S               few boarded at Southampton
```


With all of this information, we are able to create the `Reason Why` as follows, explaining two features and 
defining a reliability threshold greater than 0.3:


```python
>>> from xaiographs import Why
>>> why = Why(language='en',
...           explainer=explainer,
...           why_values_semantics=df_values_semantics,
...           why_target_values_semantics=df_target_values_semantics,
...           why_templates=df_why_templates,
...           n_values=2,
...           n_target_values=2,      
...           min_reliability=0.3,
...           verbose=0)
>>> why.fit()
>>> why.why_explanation.head(6)
   id  reason
0   0  As many women survived and many traveled in 1st class, and this case is characterized by to be a woman and travel in 1st class, has been classified as survived.
1   1  For travel in 1st class and be a child, this case has been classified as survived, considering that many traveled in 1st class and they were children.
2   2  As few traveled in 1st class and they were children, and this case is characterized by travel in 1st class and be a child, has been classified as no_survived.
3   3  For be young and to be a man, this case has been classified as no_survived, considering that they were young and many men have died.
4   4  An explanation cannot be offered for this case.
5   5  An explanation cannot be offered for this case.
```

```{hint}
XAIoGraphs includes the [`build_semantic_templates()`](../api_reference/why.md#xaiographs.Why.build_semantic_templates) 
function, which returns two `.csv` files (`values_semantics.csv` and `target_values_semantics.csv`) with the 
Features-Values and target - Features-Values of each semantic:
```


```python
>>> from xaiographs import Explainer
>>> from xaiographs import Why
>>> from xaiographs.datasets import load_titanic_discretized
>>> example_dataset, feature_cols, target_cols, _, _ = load_titanic_discretized()
>>> explainer = Explainer(importance_engine='LIDE', verbose=0)
>>> explainer.fit(df=example_dataset, feature_cols=feature_cols, target_cols=target_cols) 
>>> Why.build_semantic_templates(explainer=explainer, destination_template_path='./')
```
