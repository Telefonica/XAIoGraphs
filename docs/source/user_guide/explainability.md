[< 📚 User Guide](user_guide/user_guide)

(user_guide/explainability)=
# 1. Explainability

[`Explainability`](../api_reference/explainability.md) class provides an abstract layer which encapsulates everything 
related to the explanation process from statistics calculation, importance calculation (using the engine chosen by the 
user) and information export for visualization tasks. It is intended to offer to the user different explainability 
algorithms (currenty only ***LIDE (Local Interpretable Data Explanations***) is available).


## Requirements

To perform the calculations involved in this process, we need a tabular dataset with the following characteristics:
- 'N' columns with features (predictor columns)
-  A target column (column to be explained)
-  Theoretically, the target column could be *any* type of column, however for the moment only categorical targets are 
expected
-  Features (predictor columns) must either be categorical or have undergone a discretization process (their domain
must be comprised by a limited number of values)

To provide an understanding on what goes on when running 
[`fit()`](../api_reference/explainability.md#xaiographs.Explainer.fit) of the 
[`Explainer`](../api_reference/explainability.md) class. Let us delve into the two main parts of the process


## Feature Selection

As it will be shown in the explainability part, the process can quickly become computationally expensive. The two 
straightforward ways to mitigate this problem are, either limiting the number of samples to explain, or limiting the 
number of features to be taken into account:
-  The former is achieved by setting up the `num_samples_global_expl` parameter when invoking the 
[`fit()`](../api_reference/explainability.md#xaiographs.Explainer.fit) method of the 
[`Explainer`](../api_reference/explainability.md) class.
-  The latter can be tuned by means of the `number_of_features` parameter when instantiating the 
[`Explainer`](../api_reference/explainability.md) class. 

```{tip}
Both parameters have been initialized with sensitive defaults according to our experience, so ,for a first run, they can
 be safely left untouched
```

While the sampling is done keeping each target class original ratios, the feature selection process is more complex and
will be summarized here:
- Let us consider each target class and all the features. Then
    - For each target class:
        - For each feature:
            - Two histograms are computed:
                - First histogram is computed considering the dataset filtered by `target == target class`
                - Second histogram is computed considering the dataset filtered by `target != target class`
            - What we get here are two distributions:
                - First shows how feature values are distributed when target equals target class
                - Second shows how feature values are distributed when target is different from target class
            - For a relevant feature, which is a feature whose value strongly influences the target value, we expect 
            those two distributions to be significantly different
            
Once the intuition behind the feature selection process has been introduced. Let us delve into the details of how 
distributions are compared, which is, for a given feature, given the two histograms how to say how different (or 
similar) they are. For this purpose a variant of the
 [Jensen-Shannon distance](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html) 
 will be used:
- First the following is computed:

$$
mjs = \sqrt{\frac{D(p \parallel m) + D(q \parallel m)}{2}}
$$

- From here, several statistics are calculated:

$$              
{\begin{bmatrix}\sqrt{median(mjs)}, \sqrt{mean(mjs)}, \sqrt{max(mjs)}, \sqrt{sum(mjs)}\end{bmatrix}}
$$       

So it turns out that the modified Jensen-Shannon distance returns a four element array containing the calculations
 above.

```{admonition} Four better than one
:class: important

Computing four different statistics rather than a single one helps balancing the pros and cons of each of them when 
considered individually
```

With that four element result in mind:
- After applying the formula to each of the N features, N four element arrays will be obtained and stacked:

$$
\mathbf{A} = {\begin{bmatrix}
    a_{00} & a_{01} & a_{02} & a_{03} \\
    a_{10} & a_{11} & a_{12} & a_{13} \\
    \vdots & \vdots & \ddots & \vdots \\
    a_{N-10} & a_{N-11} & a_{N-12} & a_{N-13}
\end{bmatrix}}
$$

- Now, for the resulting *(N, 4)* matrix, each value is normalized by dividing it by the sum of its column elements:

$$
\mathbf{A'} = {\begin{bmatrix}
    a_{00}/\sum_{i=0}^{N-1} a_{i0} & a_{01}/\sum_{i=0}^{N-1} a_{i1} & a_{02}/\sum_{i=0}^{N-1} a_{i2} & a_{03}/\sum_{i=0}^{N-1} a_{i3} \\
    a_{10}/\sum_{i=0}^{N-1} a_{i0} & a_{11}/\sum_{i=0}^{N-1} a_{i1} & a_{12}/\sum_{i=0}^{N-1} a_{i2} & a_{13}/\sum_{i=0}^{N-1} a_{i3} \\
    \vdots & \vdots & \ddots & \vdots \\
    a_{N-10}/\sum_{i=0}^{N-1} a_{i0} & a_{N-11}/\sum_{i=0}^{N-1} a_{i1} & a_{N-12}/\sum_{i=0}^{N-1} a_{i2} & a_{N-13}/\sum_{i=0}^{N-1} a_{i3}
\end{bmatrix}}
$$
- Then, for each feature (each matrix row), its elements are added, as a result the matrix becomes a single column hence 
 a vector containing one element per feature:
 
$$
\mathbf{b} = {\begin{bmatrix}
    a_{00}' + a_{01}' + a_{02}' + a_{03}' \\
    a_{10}' + a_{11}' + a_{12}' + a_{13}' \\
    \vdots \\
    a_{N-10}' + a_{N-11}' + a_{N-12}' + a_{N-13}'
\end{bmatrix}} = {\begin{bmatrix} b_{0} & b_{1} & \dots & b_{N-1}\end{bmatrix}}
$$

where
$
a_{nm}' = a_{nm}/\sum_{i=0}^{n} a_{im}
$
and
$
b_{n} = \sum_{i=0}^{n} a_{ni}'
$


- Finally each element is normalized by dividing it by the sum of all the elements.
$
\mathbf{b'} = {\begin{bmatrix} b_{0}/\sum_{i=0}^{N-1} b_{i} & b_{1}/\sum_{i=0}^{N-1} b_{i} & \dots & b_{N-1}/\sum_{i=0}^{N-1} b_{i}\end{bmatrix}}
= {\begin{bmatrix} b_{0}' & b_{1}' & \dots & b_{N-1}'\end{bmatrix}}
$

The obtained vector contains a number for each feature and that number represents the feature distance between:
- The feature values distribution when target equals to the target class being taken into account
- The feature values distribution when target is different from that target class

Therefore, the higher the distance, the most relevant the feature will be...for that target class. Hence this must be 
computed for all possible target values in the case of a multiple classification problem (a non-binary problem). So:
- In the case of a binary classification problem, we can proceed to rank the obtained distances
- In the case of a multiple classification problem, feature distributions distances for the rest of the possible target 
classes must be computed. Once this is done, distances for each feature will be added, ending up with a single number
per feature

At this point we have a single number per feature which must be ranked: the highest the number the most relevant the
 feature is considered

```{admonition} Choose your top K
:class: important

How many of the most important features will be picked up can be setup by means of the `number_of_features` parameter 
when instantiating the [`Explainer`](../api_reference/explainability.md) class.
```
 
## LIDE (Local Interpretable Data Explanations)

LIDE is a local explainability algorithm which works on tabular data and doesn't make any assumptions about the origin 
of the target (the column to be explained). Before further reading, please take a look at the 
[requirements section](#requirements)

Let us understand what local explainability means:
- Explainability means that the algorithm tries to estimate how predictor columns (features) influence the target column
 value. In other words, the importance of the features in relation to the target
- Local implies that LIDE, provides a customized and independent estimation for each sample (dataset row)

For taxonomy lovers, LIDE belongs to the surrogate model based algorithms family, which are  models that are used to 
explain individual predictions of black box machine learning models. In a more mathematical way:
- Given a black box model (or complex function) $F(X)$, for each $x$ within the dataset an explainable 
a local model $g(Z')=g(h(X))$ is defined (for instance, a linear model). This model must be able to locally 
approximate the black box model (or complex function) to explain

```{tip}
Explanation models often use simplified inputs $x'$ that map to the original inputs through a mapping function 
$h$ so that $x = h(x')$
```

More formally: for each tuple of variables $X = \{x_{1}, x_{2}, \dots, x_{N}\}$ a linear surrogate model exists
 so that:

$$
g(Z') = φ_{0} + \sum_{i=1}^{M} φ_{i}z_{i}'  
$$

which satisfies the following: $ F(X) = g(Z') = g(h(X))$. This property is called *Local Accuracy* where:
- $Z'=h(X)$ represents the mapping between $X$ (features used by the black box model) and the dummy variables $Z'$ used to 
provide the explanation. For instance, if $x ∈ \{a, b, c\}$ then, the subsequent dummy variables are:

$$
z_{a}'=h(x=a)={\begin{bmatrix} 1 & 0 & 0\end{bmatrix}}

z_{b}'=h(x=b)={\begin{bmatrix} 0 & 1 & 0\end{bmatrix}}

z_{c}'=h(x=c)={\begin{bmatrix} 0 & 0 & 1\end{bmatrix}}
$$

- $M$ is the number of dummy variables used to generate the explanation for the black box model

Now, if *Missingness* and *Consistency* properties [are achieved](https://arxiv.org/pdf/1705.07874.pdf) along
 *Local Accuracy* then the above coefficients $φ_{i}$ of the linear surrogated model, match the Shapley values (defined 
 by the following equation):

$$
φ_{i}(v)=\sum_{S⊆M\{i\}} \frac{|S|!(M-|S|-1)!}{M!}(v(S ∪ {i}) - v(S))
$$
where:
- $M$ represents the number of features
- $S$ represents a feature coalition (group)
- $v(S)$ represents the *coalition worth*. Which can be described as the estimation of the black box model (or complex
 function) ($F(X)$) prediction if this had been generated taking into account only the features included in coalition 
 $S$
 
So, coalition worth can be computed as the expected value of the blackbox model prediction when the coalition features 
are within the model input:

$$
v(S) = E[F(X_{s̅}, X_{s})|X_{s}] = \int{F(X_{s̅}, X_{s})P(X_{s̅}|X_{s}}) dX_{s̅}
$$
where:
- $S$ represents $X_{s}≡\{x_{1}, x_{2}, \dots, x_{s}\} ⊆ X$ which are the features included in the coalition
- $S̅$ represents $X_{s̅}=\{X\}-\{X_{s}\}$ which is the set of features complementary to $S$
- $P(X_{s̅}|X_{s})$ is the probability of $X_{s̅}$ given or conditioned by $X_{s}$
 
In order to simplify the above calculation, SHAP algorithm assumes the *Feature Independence* hypothesis, which is a 
strong assumption:

$$
P(X_{s̅}|X_{s}) = P(X_{s̅})
$$ 
 **LIDE does not rely on that assumption** but instead, directly estimates $P(X_{s̅}|X_{s})$ (thus the $v(S)$ needed to 
 obtain the Shapley values). We won't delve into details, but, in order to this estimation it relies on two 
 hypotheses:
 - $Z'=h(X)=f(discretize(X))$, that is to say, dummy variables used for explanation are obtained from the discretized 
 version of features X used by the black box model
 - When generating the explanation, access is granted to a set of statistically significant historical data 
 $\{x_{1}^{i}, x_{2}^{i}, \dots, x_{N}^{i}, F(x^{i})\}$ where $i ∈ [1, K]$ being $K$ large enough depending on the 
 problem to be explained
 
The latter assumption is particularly crucial since LIDE depends on the historical data at disposal: a larger amount 
leads to a high quality explanation and a higher computational overhead. Less data means the opposite: less quality
 explanation but also a less computationally demanding process. Furthermore, LIDE does neither generate artificial data
 nor modify the probability distribution of the problem to be solved.


## Example

Following that, we will demonstrate how to acquire the various explainability results in XAIoGraphs for a 
classification problem using tabular data, with `titanic` dataset example.
Raw titanic dataset can be obtained using the 
[`load_titanic()`](../api_reference/datasets.md#xaiographs.datasets.load_titanic) function:

```python
>>> from xaiographs.datasets import load_titanic
>>> df_dataset = load_titanic()
>>> df_dataset.head(3)
    id  gender title      age  family_size  is_alone embarked  class  ticket_price  survived
0    0  female   Mrs  29.0000            0         1        S      1      211.3375         1
1    1    male    Mr   0.9167            3         0        S      1      151.5500         1
2    2  female   Mrs   2.0000            3         0        S      1      151.5500         0
```

To determine the explainability, we have discretized the continuous features (`age`, `family_size` and `ticket_price`) 
and produced as many columns representing the probability of the target as there are targets in the dataset.
In this example, we will have two columns with probabilities of `0` and `1`: `SURVIVED` and `NO_SURVIVED`. 
The function [`load_titanic_discretized()`](../api_reference/datasets.md#xaiographs.datasets.load_titanic_discretized) 
in XAIoGraphs already provides this altered dataset.

```python
>>> from xaiographs.datasets import load_titanic_discretized
>>> df_dataset, features_cols, target_cols, _, _ = load_titanic_discretized()
>>> df_dataset[features_cols + target_cols].head(3)
   id  gender title          age family_size  is_alone embarked  class ticket_price  SURVIVED NO_SURVIVED 
0   0  female   Mrs  18_30_years           1         1        S      1         High         1           0 
1   1    male    Mr    <12_years         3-5         0        S      1         High         1           0 
2   2  female   Mrs    <12_years         3-5         0        S      1         High         0           1
```

To obtain different explainability results, we must create an object of class [`Explainer`](../api_reference/explainer.md) 
and analyze it through the `dataset` and the explainability engine (`LIDE`). Later, by using the `fit()` method and 
handing it a list containing the names of the feature columns (`feature_cols`) and another list containing the names 
of the target columns (`target_cols`), it will execute all of the computations required to provide the explainability:

```python
>>> from xaiographs import Explainer
>>> from xaiographs.datasets import load_titanic_discretized
>>> df_dataset, features_cols, target_cols, _, _ = load_titanic_discretized()
>>> explainer = Explainer(importance_engine='LIDE', number_of_features=8, verbose=1)
>>> explainer.fit(df=df_dataset, feature_cols=features_cols, target_cols=target_cols)
```

```{warning}
By default, the `LIDE` explainability method performs explanations with the 8 most essential features. 
You can change this value using the class constructor's `number_of_features` parameter.

`number_of_features` parameter must be less than 13 to avoid "infinite" computation durations.
```


The following are the outcomes provided by the [`Explainer`](../api_reference/explainer.md)  class's various properties:

&nbsp;

<h4> Top Features </h4>

Because the explainability procedure is quite expensive and it is not computationally feasible to explain more than 12 
or 13 features, we organize the variables a priori by relevance (see 
[`Features Selector`](explainability.md#feature-selection) section).
This will allow us to select the 'N' variables to explain (`number_of_features` parameter constructor).

The variable selector's rating is retrieved by accessing the 
[`top_features`](../api_reference/explainability.md#xaiographs.Explainer.top_features) property.


```python
>>> explainer.top_features
        feature  rank
0        gender     1
1         title     2
2         class     3
3  ticket_price     4
4      embarked     5
5   family_size     6
6      is_alone     7
7           age     8
```


&nbsp;

<h4> Top Features by Target </h4>


The [`top_features_by_target`](../api_reference/explainability.md#xaiographs.Explainer.top_features_by_target) 
property displays the importance of features by target together with the 
[Jensen-Shannon distance](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html) distance:

```python
>>> explainer.top_features_by_target
         target       feature  distance
0      SURVIVED        gender  0.262507
1      SURVIVED         title  0.241172
2      SURVIVED         class  0.128430
3      SURVIVED  ticket_price  0.117809
4      SURVIVED      embarked  0.076622
5      SURVIVED   family_size  0.069195
6      SURVIVED      is_alone  0.053045
7      SURVIVED           age  0.051220
8   NO_SURVIVED        gender  0.262507
9   NO_SURVIVED         title  0.241172
10  NO_SURVIVED         class  0.128430
11  NO_SURVIVED  ticket_price  0.117809
12  NO_SURVIVED      embarked  0.076622
13  NO_SURVIVED   family_size  0.069195
14  NO_SURVIVED      is_alone  0.053045
15  NO_SURVIVED           age  0.051220
```


```{note}
Because this is a binary example, the distance between the variables is the same for both classes.
```

&nbsp;

<h4> Global Explainability </h4>

[`global_explainability`](../api_reference/explainability.md#xaiographs.Explainer.global_explainability) property 
containing each feature ranked by its global importance.

```python
>>> explainer.global_explainability
        feature  importance  rank
0        gender    0.124936     1
1         title    0.122790     2
2         class    0.089931     3
3  ticket_price    0.062145     4
7           age    0.059930     5
4      embarked    0.059490     6
5   family_size    0.042980     7
6      is_alone    0.031692     8
```

&nbsp;

<h4> Global Target Explainability </h4>

[`global_target_explainability`](../api_reference/explainability.md#xaiographs.Explainer.global_target_explainability) 
property returns all  features to be explained, ranked by their global importance by target value.

```python
>>> explainer.global_target_explainability
         target       feature  importance  rank
8   NO_SURVIVED        gender    0.124936     1
9   NO_SURVIVED         title    0.122790     2
10  NO_SURVIVED         class    0.089931     3
11  NO_SURVIVED  ticket_price    0.062145     4
15  NO_SURVIVED           age    0.059930     5
12  NO_SURVIVED      embarked    0.059490     6
13  NO_SURVIVED   family_size    0.042980     7
14  NO_SURVIVED      is_alone    0.031692     8
0      SURVIVED        gender    0.124936     1
1      SURVIVED         title    0.122790     2
2      SURVIVED         class    0.089931     3
3      SURVIVED  ticket_price    0.062145     4
7      SURVIVED           age    0.059930     5
4      SURVIVED      embarked    0.059490     6
5      SURVIVED   family_size    0.042980     7
6      SURVIVED      is_alone    0.031692     8
```


&nbsp;

<h4> Global Target Feature-Value Explainability </h4>


[`global_target_feature_value_explainability`](../api_reference/explainability.md#xaiographs.Explainer.global_target_feature_value_explainability)
property that, for each target value, returns all the pairs feature-value ranked by their global importance.

```python
>>> explainer.global_target_feature_value_explainability
         target      feature_value  importance  rank
6   NO_SURVIVED      age_<12_years   -0.181679     1
28  NO_SURVIVED     family_size_>5    0.179046     2
30  NO_SURVIVED      gender_female   -0.172290     3
46  NO_SURVIVED          title_Mrs   -0.168379     4
8   NO_SURVIVED      age_>60_years    0.141469     5
10  NO_SURVIVED            class_1   -0.114309     6
16  NO_SURVIVED         embarked_C   -0.097454     7
32  NO_SURVIVED        gender_male    0.095240     8
44  NO_SURVIVED           title_Mr    0.094939     9
24  NO_SURVIVED      family_size_2   -0.084919    10
14  NO_SURVIVED            class_3    0.066115    11
38  NO_SURVIVED  ticket_price_High   -0.063437    12
40  NO_SURVIVED   ticket_price_Low    0.053317    13
12  NO_SURVIVED            class_2   -0.035934    14
20  NO_SURVIVED         embarked_S    0.030768    15
48  NO_SURVIVED         title_rare   -0.020909    16
34  NO_SURVIVED         is_alone_0   -0.019949    17
42  NO_SURVIVED   ticket_price_Mid    0.017978    18
26  NO_SURVIVED    family_size_3-5    0.017444    19
0   NO_SURVIVED    age_12_18_years   -0.016456    20
18  NO_SURVIVED         embarked_Q   -0.015209    21
4   NO_SURVIVED    age_30_60_years    0.014129    22
2   NO_SURVIVED    age_18_30_years    0.013591    23
22  NO_SURVIVED      family_size_1    0.005527    24
36  NO_SURVIVED         is_alone_1    0.005527    24
7      SURVIVED      age_<12_years    0.181679     1
29     SURVIVED     family_size_>5   -0.179046     2
31     SURVIVED      gender_female    0.172290     3
47     SURVIVED          title_Mrs    0.168379     4
9      SURVIVED      age_>60_years   -0.141469     5
11     SURVIVED            class_1    0.114309     6
17     SURVIVED         embarked_C    0.097454     7
33     SURVIVED        gender_male   -0.095240     8
45     SURVIVED           title_Mr   -0.094939     9
25     SURVIVED      family_size_2    0.084919    10
15     SURVIVED            class_3   -0.066115    11
39     SURVIVED  ticket_price_High    0.063437    12
41     SURVIVED   ticket_price_Low   -0.053317    13
13     SURVIVED            class_2    0.035934    14
21     SURVIVED         embarked_S   -0.030768    15
49     SURVIVED         title_rare    0.020909    16
35     SURVIVED         is_alone_0    0.019949    17
43     SURVIVED   ticket_price_Mid   -0.017978    18
27     SURVIVED    family_size_3-5   -0.017444    19
1      SURVIVED    age_12_18_years    0.016456    20
19     SURVIVED         embarked_Q    0.015209    21
5      SURVIVED    age_30_60_years   -0.014129    22
3      SURVIVED    age_18_30_years   -0.013591    23
23     SURVIVED      family_size_1   -0.005527    24
37     SURVIVED         is_alone_1   -0.005527    24
```

&nbsp;

<h4> Global Frequency Feature Values </h4>


[`global_frequency_feature_value`](../api_reference/explainability.md#xaiographs.Explainer.global_frequency_feature_value)
property returns the number of occurrences for each feature-value pair.

```python
>>> explainer.global_frequency_feature_value.sort_values('frequency', ascending=False)
        feature_value  frequency
36         is_alone_1       1025
22      family_size_1       1025
20         embarked_S        916
32        gender_male        843
44           title_Mr        818
14            class_3        709
2     age_18_30_years        551
4     age_30_60_years        522
38  ticket_price_High        477
30      gender_female        466
46          title_Mrs        457
40   ticket_price_Low        433
42   ticket_price_Mid        399
10            class_1        323
34         is_alone_0        284
12            class_2        277
16         embarked_C        270
24      family_size_2        159
18         embarked_Q        123
0     age_12_18_years        105
6       age_<12_years         98
26    family_size_3-5         90
28     family_size_>5         35
48         title_rare         34
8       age_>60_years         33
```


&nbsp;

<h4> Local Feature Value Explainability</h4>


[`local_feature_value_explainability`](../api_reference/explainability.md#xaiographs.Explainer.local_feature_value_explainability)
property that, for each sample, returns as many rows as feature-value pairs, together with their calculated importance.

```python
>>> explainer.local_feature_value_explainability.head(16)
    id      feature_value  importance  rank
0    0      gender_female    0.191029     1
1    0          title_Mrs    0.189320     2
2    0            class_1    0.147101     3
3    0  ticket_price_High    0.101550     4
4    0         embarked_S   -0.027895     8
5    0      family_size_1    0.004920     6
6    0         is_alone_1    0.004920     6
7    0    age_18_30_years    0.008612     5
8    1        gender_male   -0.055966     7
9    1           title_Mr   -0.058635     8
10   1            class_1    0.386458     1
11   1  ticket_price_High    0.021270     4
12   1         embarked_S   -0.003752     5
13   1    family_size_3-5   -0.010774     6
14   1         is_alone_0    0.029181     3
15   1      age_<12_years    0.311776     2
```


&nbsp;

<h4> Local Reliability</h4>

[`local_reliability`](../api_reference/explainability.md#xaiographs.Explainer.local_reliability) property that, for 
each sample, returns its top1 target and the reliability value associated to that target.

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


&nbsp;

<h4> Importance Values</h4>


[`importance_values`](../api_reference/explainability.md#xaiographs.importance_values) property returns the computed 
importance values. Structure (numpy.array) containing for each sample, feature and target value, the computed importance values.

```python
>>> explainer.importance_values
array([[[ 0.19102919, -0.19102919],
        [ 0.18931973, -0.18931973],
        [ 0.14710146, -0.14710146],
        ...,
        [ 0.0049198 , -0.0049198 ],
        [ 0.0049198 , -0.0049198 ],
        [ 0.00861183, -0.00861183]],

       [[-0.05596649,  0.05596649],
        [-0.05863524,  0.05863524],
        [ 0.38645767, -0.38645767],
        ...,
        [-0.01077448,  0.01077448],
        [ 0.0291813 , -0.0291813 ],
        [ 0.31177627, -0.31177627]],

       [[ 0.04319279, -0.04319279],
        [ 0.04255799, -0.04255799],
        [-0.09668253,  0.09668253],
        ...,
        [-0.02768731,  0.02768731],
        [ 0.00612063, -0.00612063],
        [-0.34010499,  0.34010499]],

       ...,

       [[-0.09110644,  0.09110644],
        [-0.09225141,  0.09225141],
        [-0.06639871,  0.06639871],
        ...,
        [-0.02507825,  0.02507825],
        [-0.02507825,  0.02507825],
        [-0.03583761,  0.03583761]],

       [[-0.09110644,  0.09110644],
        [-0.09225141,  0.09225141],
        [-0.06639871,  0.06639871],
        ...,
        [-0.02507825,  0.02507825],
        [-0.02507825,  0.02507825],
        [-0.03583761,  0.03583761]],

       [[-0.08246317,  0.08246317],
        [-0.08290531,  0.08290531],
        [-0.04468906,  0.04468906],
        ...,
        [-0.02018317,  0.02018317],
        [-0.02018317,  0.02018317],
        [-0.02992086,  0.02992086]]])
```