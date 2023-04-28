[< 📚 User Guide](user_guide/user_guide)

(user_guide/explainability)=
# 1. Explainability

[`Explainability`](../api_reference/explainability.md) class provides an abstract layer which encapsulates everything 
related to the explanation process from statistics calculation, importance calculation (using the engine chosen by the 
user) and information export for visualization tasks. It is intended to offer to the user different explainability 
algorithms (currenty only ***LIDE (Local Interpretable Data Explanations***) is available).


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

```{note}
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
[\sqrt{median(mjs)}, \sqrt{mean(mjs)}, \sqrt{max(mjs)}, \sqrt{sum(mjs)}]
$$       

So it turns out that the modified Jensen-Shannon distance returns a four element array containing the calculations
 above.
 
```{hint}
Computing four different statistics rather than a single one helps balancing the pros and cons of each of them when 
considered individually
```

With that four element result in mind:
- After applying the formula to each of the N features, N four element arrays will be obtained and stacked:

$
\mathbf{A} = {\begin{bmatrix}
    a_{00} & a_{01} & a_{02} & a_{03} \\
    a_{10} & a_{11} & a_{12} & a_{13} \\
    \vdots & \vdots & \ddots & \vdots \\
    a_{N-10} & a_{N-11} & a_{N-12} & a_{N-13}
\end{bmatrix}}
$

- Now, for the resulting *(N, 4)* matrix, each value is normalized by diving it by the sum of its column elements:

$
\mathbf{A'} = {\begin{bmatrix}
    a_{00}/\sum_{i=0}^{N-1} a_{i0} & a_{01}/\sum_{i=0}^{N-1} a_{i1} & a_{02}/\sum_{i=0}^{N-1} a_{i2} & a_{03}/\sum_{i=0}^{N-1} a_{i3} \\
    a_{10}/\sum_{i=0}^{N-1} a_{i0} & a_{11}/\sum_{i=0}^{N-1} a_{i1} & a_{12}/\sum_{i=0}^{N-1} a_{i2} & a_{13}/\sum_{i=0}^{N-1} a_{i3} \\
    \vdots & \vdots & \ddots & \vdots \\
    a_{N-10}/\sum_{i=0}^{N-1} a_{i0} & a_{N-11}/\sum_{i=0}^{N-1} a_{i1} & a_{N-12}/\sum_{i=0}^{N-1} a_{i2} & a_{N-13}/\sum_{i=0}^{N-1} a_{i3}
\end{bmatrix}}
$
- Then, for each feature (each matrix row), its elements are added, as a result the matrix becomes single column hence 
 a vector containing one element per feature:
 
$
\mathbf{b} = {\begin{bmatrix}
    a_{00'} + a_{01'} + a_{02'} + a_{03'} \\
    a_{10'} + a_{11'} + a_{12'} + a_{13'} \\
    \vdots \\
    a_{N-10'} + a_{N-11'} + a_{N-12'} + a_{N-13'}
\end{bmatrix}} = [b_{0}, b_{1}, \dots, b_{N-1}]
$
where
$
a_{nm'} = a_{nm}/\sum_{i=0}^{n} a_{im}
$
and
$
b_{n} = \sum_{i=0}^{n} a_{ni'}
$

- Finally each element is normalized by dividing it by the sum of all the elements.