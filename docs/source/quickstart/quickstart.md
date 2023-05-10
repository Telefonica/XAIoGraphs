# 🚀 Quickstart

## Installation 🔨 

Create a virtual environment using conda for easier management of dependencies and packages. 
For installing conda, follow the instructions on the [official conda website](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)

```python
>> conda create --name xaio37 python=3.7
>> conda activate xaio37
```

```{warning} 
Use a python version 3.7 or higher
```

XAIoGraphs can be installed from [PyPI](https://pypi.org/project/xaiographs/)

```python
>> pip install xaiographs
```

## Start with your first example 📝

Use the following entry point to view an example run with the virtual environment enabled:

```python
>> titanic_example
```

Alternatively, you may run the code below to view a full implementation of all XAIoGraphs functionalities:

```python
from xaiographs import Explainer
from xaiographs import Why
from xaiographs import Fairness
from xaiographs.datasets import load_titanic_discretized, load_titanic_why

LANG = 'en'

# LOAD DATASETS & SEMANTICS
df_titanic, feature_cols, target_cols, y_true, y_predict = load_titanic_discretized()
df_global_semantics, df_target_semantics = load_titanic_why(language=LANG)

# EXPLAINER
explainer = Explainer(importance_engine='LIDE', verbose=1)
explainer.fit(df=df_titanic, feature_cols=feature_cols, target_cols=target_cols)

# WHY
why = Why(language=LANG,
          explainer=explainer,
          why_global_semantics=df_global_semantics,
          why_target_semantics=df_target_semantics,
          verbose=1)
why.fit()

# FAIRNESS
f = Fairness(verbose=1)
f.fit(df=df_titanic[feature_cols + [y_true] + [y_predict]],
      sensitive_cols=['gender', 'class', 'age'],
      target_col=y_true,
      predict_col=y_predict)
```

Following execution, a folder called "xaioweb files" is created, which contains a set of '.json' files that will 
be used to present the results in the XAIoWeb graphical interface.

## Launching XAIoWeb 📊

XAIoWeb is a local web interface that displays the outcomes of the explanations in three sections: Global, Local, 
and Fairness. To launch the web (with the virtual environment enabled), run the following entry point:

```python
>> xaioweb -d xaioweb_files -o
```

This entry point takes the following parameters:

- `-d` o `--data` [REQUIRED]: JSON files path
- `-p` o `--port` [OPTIONAL]: Web server port. 8080 by default
- `-o` o `--open` [OPTIONAL]: Open web in browser
- `-f` o `--force` [OPTIONAL]: Force building the web from scratch, overwriting the existing one
