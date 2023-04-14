# 💻  XAIoWeb

<p>In this section we will analyze the different modules and components of the web.</p>

<p><p>We will see the behavior and the explanation of each of the graphs that make up it.</p>

<p>Each of the graphs that we will see below has a functionality that allows its export as an image to facilitate being included in any report and presentation.
To do this, you will need to click on the camera icon located in the upper right corner.</p>


---

&nbsp;
## Global Explainability

<p>The Global module presents a statistical calculation on the main characteristics of the dataset.</p>

<p>It must be understood that all entries in the dataset are analyzed individually and their statistics are subsequently aggregated in this module.</p>

<p>It is important to understand that the results are presented at the level of the entire dataset and according to the different targets that make up it.</p>

<p>The page is divided into two major sections, the top (formed by the Features Importance and Target distribution graphs) displays the information of the entire dataset.
The bottom, under the title "Feature distribution by target", shows the features information for a specific target, displaing consolidated calculations grouped by the target value.</p>

<p>Next, we will look at each of the graphs that make up it and its meaning.</p>

&nbsp;
### <strong>Features importance</strong>
<p>This graph displays at a general level (regardless of the target) the importance ordered downward of each of the features of the dataset.
The importance of these is represented, not only by the length of the horizontal segment but also by its opacity level.</p>

![global_features_importance](../../imgs/XaioWeb_Global_Features_Importance.png)

<p>Take notes that in the upper right corner of the chart, next to the export function, we have a switch that allows you to show the breakdown of values according to the target.</p>

![global_features_importance_breakdown](../../imgs/XaioWeb_Global_Features_Importance_Breakdown.png)

<p>As an important note, the colors of the targets that the graph located to the right (Target distribution) have beenined to facilitate their reading.
The X-axis has also been removed as the numerical values are different from the aggregate view (as the representative is the size of the horizontal sections) to avoid errors in the interpretation of the data.</p>

&nbsp;
### <strong>Target distribution</strong>
<p>This graph displays the distribution of targets across the dataset.</p>

<p>It is a simple statistical tool to contextualize the information contained in the dataset and visually see the importance of each of the targets.</p>

![global_target_distribution](../../imgs/XaioWeb_Global_Target_Distribution.png)

&nbsp;
### <strong>Feature importante (by target)</strong>
<p>In this case, the graph is similar to the one located right above, but only those records have been taken into account for the selected target.</p>

![global_target_features_target](../../imgs/XaioWeb_Global_Target_Features_Target.png)

<p>Take notes that in the upper right corner of the chart, next to the export function, we have a switch that allows you to compare the values of the selected target with the general data shown in the top chart. In the specific case of datasets with binary target (there are only 2 possible values for the target) this graph will show overlapping graphs, as the average values of a target are annulled with those of the opposite.</p>

![global_target_features_target_comparative](../../imgs/XaioWeb_Global_Target_Features_Target_Comparative.png)

&nbsp;
### <strong>Feature Heatmap (by target)</strong>
<p>This graph displays a heat map with the different values that the features of the dataset can take.
Those values that are most on the left will be those that contribute most positively to the target (represented by the redest color) and those located more on the right will contribute more negatively.</p>

![global_target_heatmap](../../imgs/XaioWeb_Global_Target_HeatMap.png)

<p>The different numerical values are represented depending on the opacity of the color, so that those more relevant (both positively and negatively) will have a more solid color, while those closer to the value 0 will be a more white color.
The length of each of the possible values of a feature represents the number of occurrences of that value within the dataset, so that the longer values have more presence while the smaller ones have little occurrence in the data.</p>

&nbsp;
### <strong>Features-values importance (by target)</strong>
<p>This graph displays the specific contribution values for the feature/value pairs. This can be positive (represented in red) or negative.(representado en azul)</p>

<p>It is important to note that the values shown are the same as those shown on the HeatMap.</p>

![global_target_features-values_importance](../../imgs/XaioWeb_Global_Target_Features-values_importance.png)

<p>Take notes that in the upper right corner of the chart, next to the export function, we have a switch that allows you to visualize the frequency of the feature/value (Represented in the HeatMap by its length)</p>

![global_target_features-values_importance_frecuency](../../imgs/XaioWeb_Global_Target_Features-values_importance_Frecuency.png)

&nbsp;
### <strong>Features-values relations (by target)</strong>
<p>This graph displays the relationships between the different features/values.</p>

![global_target_features-values_relations](../../imgs/XaioWeb_Global_Target_Features-values_Relations.png)


&nbsp;

<p><em>It is important to emphasize that these two last graphs are filtered thanks to sliders located just above them.</em>

![global_target_filter](../../imgs/XaioWeb_Global_Target_Filter.png)

<em>By shifting each of the bars, viewing criteria can be modified to analyze different data behaviors.</em></p>

---

&nbsp;

## Local Explainability

<p>The Local module presents the individual results, showing and explaining the results for a given dataset record.</p>

<p>Like the case of the previous module, the page is distributed into two important sections, the top presents a table with the dataset records, having by columns the different features. And the bottom that shows the calculations made for the selected record of the dataset. </p>

&nbsp;
### <strong>Dataset</strong>

<p>This section displays the dataset records on which the calculations have been made, each of the features is presented in columns with the specific values taken.</p>

<p>It is important to note two very representative columns, the first is a checkbox that allows you to select the record on which the data is analyzed and which will be taken as a reference for the graphics located at the bottom of the screen.</p>

<p>And the last column called 'reliability', this represents a measure of the quality of the data. Since the XaioGraph does not have access to the model, it must predict the target of each record based on the analysis of the dataset, that is why there may be discrepancies between reality and prediction, and this column is what it represents, the degree of equality between the real target and the predict, which is why the records with values close to 1 are those in which both coincide and therefore the error dragged when generating individual calculations is much smaller.</p>

![local_dataset](../../imgs/XaioWeb_Local_Dataset.png)

&nbsp;
### <strong>Local Explantion (Reason Why)</strong>

<p>This section shows a brief verbal explanation of the data that make up the record of the selected dataset. Underlining the reasons why this case has the target it has.</p>

![reason_why](../../imgs/XaioWeb_Reason_Why.png)

&nbsp;
### <strong>Features-values importance</strong>
<p>This graph displays the specific contribution values for the feature/value pairs. This can be positive (represented in red) or negative.(representado en azul)</p>

![local_features_values_importance](../../imgs/XaioWeb_Local_Features_values_importance.png)

&nbsp;
### <strong>Features-values relations (by target)</strong>
<p>This graph displays the relationships between the different features/values.</p>

![local_features_values_relations](../../imgs/XaioWeb_Local_Features_values_relations.png)

&nbsp;

<p><em>It is important to emphasize that these two last graphs are filtered thanks to the slider located just above them.</em>

![local_filter](../../imgs/XaioWeb_Local_Filter.png)

<em>By shifting the bar, the most relevant features can be displayed, so as to facilitate their reading and understanding.</em></p>


---

&nbsp;

## Fairness

<p>The fairness module shows the results from an ethical point of view, trying to detect possible misconduct or conditioners that can generate sensitive variables such as gender, age, etc. that can give the case of discrimination or harm.

<p>Following the same structure as the previous modules, the page is divided into two. In the upper part we can see an analysis of all those variables detected that can constitute a case of bias and that its analysis is recommended in detail.
While at the bottom, we enter the specific details of each of these variables mentioned in the top section.</p>

<p>To facilitate the understanding and reading of the data, a similar color scheme has been chosen for employees in other fields such as the Nutriscore Index in food or energy efficiency in appliances or construction. It is therefore a color scale from green to red.
Therefore, green values are those with values closer to 0 and therefore do not present any relevant anomalies. While red are those that have exceeded a threshold of tolerance and it is important to analyze it in detail.</p>

![fairness_legend](../../imgs/XaioWeb_Fairness_Legend.png)

&nbsp;
### <strong>Fairness Criterias Score</strong>
<p>This graph shows the analysis performed for each of the sensitive features based on the criteria of Independence, Separation and Sufficiency.</p>

![fairness_criterias_score](../../imgs/XaioWeb_Fairness_Criterias_Score.png)

&nbsp;
### <strong>Confussion Matrix</strong>
<p>This graph is a confusion matrix to represent the performance of the prediction algorithm.</p>

<p>As in any confusion matrix, columns represent the number of predictions for each target while rows represent the real class instances.</p>

![fairness_confussion_matrix](../../imgs/XaioWeb_Fairness_Confussion_Matrix.png)

<p>Take notes that in the upper right corner of the chart, next to the export function, we have a switch that allows you to analize the numeric values or percentage values.</p>

![fairness_confussion_matrix_percentage](../../imgs/XaioWeb_Fairness_Confussion_Matrix_Percentage.png)

&nbsp;
### <strong>Features correlation (by feature)</strong>
<p>This section displays the different degrees of correlation of the selected feature with the remaining features of the dataset, showing the Pearson correlation value</p>

![fairness_correlation](../../imgs/XaioWeb_Fairness_Correlation.png)

&nbsp;
### <strong>Independence, Separation & Sufficiency values (by feature)</strong>
<p>These three graphs show the values of Independence, Separation and Sufficiency of the selected feature, making a breakdown and analysis of each of the possible values it has</p>

![fairness_independence](../../imgs/XaioWeb_Fairness_Independence.png)
![fairness_separation](../../imgs/XaioWeb_Fairness_Separation.png)
![fairness_sufficiency](../../imgs/XaioWeb_Fairness_Sufficiency.png)
