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
  
### Higgs Bosson (higgsBossonTraining.csv)

* Source: https://www.kaggle.com/datasets/knight079/higgsb (train)
  
* Description: This is a dataset describing a Higgs Bosson: sometimes called the Higgs particle, is an elementary particle in the Standard Model of particle physics produced by the quantum excitation.

* Features: (33 Features x 250000 elements)

    + **1 EventId**:
    + **2 DER_mass_MMC**:
    + **3 DER_mass_transverse_met_lep**:
    + **4 DER_mass_vis**:
    + **5 DER_pt_h**:
    + **6 DER_deltaeta_jet_jet**:
    + **7 DER_mass_jet_jet**:
    + **8 DER_prodeta_jet_jet**:
    + **9 DER_deltar_tau_lep**:
    + **10 DER_pt_tot**:
    + **11 DER_sum_pt**:
    + **12 DER_pt_ratio_lep_tau**:
    + **13 DER_met_phi_centrality**:
    + **14 DER_lep_eta_centrality**:
    + **15 PRI_tau_pt**:
    + **16 PRI_tau_eta**:
    + **17 PRI_tau_phi**:
    + **18 PRI_lep_pt**:
    + **19 PRI_lep_eta**:
    + **20 PRI_lep_phi**:
    + **21 PRI_met**:
    + **22 PRI_met_phi**:
    + **23 PRI_met_sumet**:
    + **24 PRI_jet_num**:
    + **25 PRI_jet_leading_pt**:
    + **26 PRI_jet_leading_eta**:
    + **27 PRI_jet_leading_phi**:
    + **28 PRI_jet_subleading_pt**:
    + **29 PRI_jet_subleading_eta**:
    + **30 PRI_jet_subleading_phi**:
    + **31 PRI_jet_all_pt**:
    + **32 Weight**:
    + **33 Label**: s (34%) ,b (66%) (target)
  