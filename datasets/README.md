# Dataset folder

* In this folder we can find some datasets (of small size) to test the functionalities of XAIoGraphs.


## Datasets listing:

### Milk Quality (milknew.csv)

* Source: https://www.kaggle.com/code/jiaowoguanren/milk-quality-prediction-tensorflow-resmlp/data
  
* Description: dataset with 7 milk characteristics, classifying them as Low (Bad) or Medium (Moderate) High (Good).

* Features: (8 Features x 1059 elements)

    + **pH**: This Column defines PH alus of the milk which ranges from 3 to 9.5 max : 6.25 to 6.90

    + **Temprature**: This Column defines Temprature of the milk which ranges from 34'C to 90'C max : 34'C to 45.20'C

    + **Taste**: This Column defines Taste of the milk which is categorical data 0 (Bad) or 1 (Good) max : 1 (Good)

    + **Odor**: This Column defines Odor of the milk which is categorical data 0 (Bad) or 1 (Good) max : 0 (Bad)

    + **Fat**: This Column defines Odor of the milk which is categorical data 0 (Low) or 1 (High) max : 1 (High)

    + **Turbidity**: This Column defines Turbidity of the milk which is categorical data 0 (Low) or 1 (High) max : 1 (High)

    + **Colour**: This Column defines Colour of the milk which ranges from 240 to 255 max : 255

    + **Grade**: This Column defines Grade (Target) of the milk which is categorical data Where Low (Bad) or Medium (Moderate) High (Good)

### Body Performance (bodyPerformance.csv.csv)

* Source: https://www.kaggle.com/datasets/kukuroo3/body-performance-data
  
* Description: This is data that confirmed the grade of performance with age and some exercise performance data.

* Features: (12 Features x 13393 elements)

    + **age**: 20 ~64
    
    + **gender**: F,M

    + **height_cm**: (If you want to convert to feet, divide by 30.48)

    + **weight_kg**

    + **body fat_%**

    + **diastolic**: diastolic blood pressure (min)

    + **systolic**: systolic blood pressure (min)

    + **gripForce**

    + **sit and bend forward_cm**

    + **sit-ups counts**

    + **broad jump_cm**

    + **class**: A,B,C,D ( A: best) / stratified
