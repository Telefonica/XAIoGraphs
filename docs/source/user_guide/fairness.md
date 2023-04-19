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
The probability that two elements with different values of the sensitive variable are well classified must be the same.
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

TODO


|Category|     Range Score      |
|:------:|:--------------------:|
|A+      | 0.0 <= score <= 0.02 |
|A       | 0.02 < score <= 0.05 |
|B       | 0.05 < score <= 0.08 |
|C       | 0.08 < score <= 0.15 |
|D       | 0.15 < score <= 0.25 |
|E       | 0.25 < score <= 1.0  |

## Example

TODO






[< 📚 User Guide](user_guide/user_guide)