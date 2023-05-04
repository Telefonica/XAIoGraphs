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

- Now, for the resulting *(N, 4)* matrix, each value is normalized by diving it by the sum of its column elements:

$$
\mathbf{A'} = {\begin{bmatrix}
    a_{00}/\sum_{i=0}^{N-1} a_{i0} & a_{01}/\sum_{i=0}^{N-1} a_{i1} & a_{02}/\sum_{i=0}^{N-1} a_{i2} & a_{03}/\sum_{i=0}^{N-1} a_{i3} \\
    a_{10}/\sum_{i=0}^{N-1} a_{i0} & a_{11}/\sum_{i=0}^{N-1} a_{i1} & a_{12}/\sum_{i=0}^{N-1} a_{i2} & a_{13}/\sum_{i=0}^{N-1} a_{i3} \\
    \vdots & \vdots & \ddots & \vdots \\
    a_{N-10}/\sum_{i=0}^{N-1} a_{i0} & a_{N-11}/\sum_{i=0}^{N-1} a_{i1} & a_{N-12}/\sum_{i=0}^{N-1} a_{i2} & a_{N-13}/\sum_{i=0}^{N-1} a_{i3}
\end{bmatrix}}
$$
- Then, for each feature (each matrix row), its elements are added, as a result the matrix becomes single column hence 
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

So that, the higher the distance, the most relevant the feature will be...for that target class. Hence this must be 
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

LIDE is a local explainability algorithm which works on tabular data and doesn't make any assumptions on the origin of 
the target (the column to be explained). Before further reading, please take a look at the 
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
 function) prediction if this had been generated taking into account only the features included in coalition $S$
 
