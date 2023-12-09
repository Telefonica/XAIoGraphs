# XAIoGraphs

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-green.svg)](https://www.gnu.org/licenses/agpl-3.0)

![python versions](https://img.shields.io/badge/python-3.7%2C%203.8%2C%203.9-blue.svg)

XAIoGraphs (e**X**plainability **A**rticicial **I**ntelligence **o**ver **Graphs**) is an Explicability and Fairness 
Python library for classification problems with tabulated and discretized data.

The explainability methods in this library don't make any hypotheses about the data, so it does not require the AI model.
Simply need data and predictions (or decisions), being able to explain AI models, rule models, and reality.

```{image} ../imgs/XAIoGraphs_schema.png
:alt: XAIoGraphs_schema
:class: bg-primary
:align: center
```

This library includes the following functionalities:

+ **Global Explainability**: Explains predictions or decisions as a whole, focusing on the variables that have the most influence.
+ **Local Explainability**: Explains the prediction of a single element.
+ **Reliability Measure** of local explainability.
+ **Reason Why:** *explanation in natural language* of the classification of each element.
+ **Fairness Scoring**: highlights potential discriminations in classifications based on sensitive features.

To understand or ***interpret the explanations*** uses ***XAIoWeb***, a ***web interface*** running in local mode (127.0.0.1:8080). 
It displays the explanations outcomes in three sections: Global, Local and Fairness.

```{image} ../imgs/XAIoWeb.png
:alt: XAIoWeb
:class: bg-primary
:align: center
```

<hr>

```{include} quickstart/quickstart.md
```

<hr>

```{include} contributors/contributors.md
```

```{toctree}
:hidden:
:includehidden:
:maxdepth: 2

🚀 Quickstart <quickstart/quickstart.md>
📚 User Guide <user_guide/user_guide.md>
💎 API Reference <api_reference/api_reference.md>
💻  XAIoWeb <xaioweb/xaioweb.md>
✏️ Example <examples/examples.md>
🤝 Contributors <contributors/contributors.md>
```
