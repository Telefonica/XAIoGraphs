(examples/examples)=
# ✏️ Examples

XAIoGraphs contains a set of examples that can be executed as `entry points`:



| Example                                           | Entry Point                    | Rows  | Num. Feats |      Task       |
|:--------------------------------------------------|:-------------------------------|:-----:|:----------:|:---------------:|
| [Titanic](titanic.md)                             | titanic_example                | 1309  |     8      |     Binary      |
| [Compas](compas.md)                               | compas_example                 | ????  |    ????    |     Binary      |
| [Body Performace](body_performance.md)            | body_performance_example       | 13393 |     11     | Multi-Class (3) | 
| [Education Performance](education_performance.md) | education_performance_example  |  145  |     29     | Multi-Class (5) |


Use the entry points to see an example run with the XAIoGraphs library installed in a Python virtual environment 
activated. Example:

```bash
>> titanic_example
```


Run the following command with the virtual environment enabled to see the results in [`XAIoWeb`](../xaioweb/xaioweb.md):


```python
>> xaioweb -d xaioweb_files -o
```

You can see more information about each of these examples at the links below:

* [Titanic Example](titanic.md)
* [Compas Example](compas.md)
* [Body Performace Example](body_performance.md)
* [Education Performance Example](education_performance.md) 
