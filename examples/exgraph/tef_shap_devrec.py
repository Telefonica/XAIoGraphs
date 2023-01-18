import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import pandas as pd

from xaiographs.common.utils import xgprint
from xaiographs.exgraph.explainer.explainer import Explainer

FLAGSHIP = 'Flagship'
ID = 'id'
ID_ORI = 'elem_id'
LOW = 'LOW'
MID = 'MID'
MID_LOW = 'MID-LOW'
MID_TOP = 'MID-TOP'
N = 'N'
OTHER = 'Other'
SCORE = 'score'
TARGET = 'target'
TOP = 'TOP'
ULTRA_LOW = 'ultra-low'
ULTRALOW = 'ultra low'
UNKNOWN = 'unknown'
WHAT = 'what'
WHEN = 'when'
Y = 'Y'


@dataclass
class ConditionBinmap:
    """
    Dataclass containing the necessary properties to store metadata related to the transformations to be done by the
    `condition2bin_transform` function
    """
    # List of conditions
    conditions: List[bool] = field(default_factory=lambda: [])

    # List of destination bins where feature values will be allocated depending on the fulfilled condition (there must
    # be exactly the same bins as conditions)
    bins: List[Any] = field(default_factory=lambda: [])

    # Default bin used for those feature values not matching any of the conditions (this shouldn't happen)
    default_value: Any = None


@dataclass
class FeatureValuemap:
    """
    Dataclass containing the necessary properties to store metadata related to the transformations to be done by the
    `valuemap_transform` function
    """
    # List of original values
    ori_values: List[Any] = field(default_factory=lambda: [])

    # List of destination values used to replace the original ones
    dest_values: List[Any] = field(default_factory=lambda: [])

    # Value which will replace any other values not present among the original values
    default_value: Any = None

    # Whether conversion to uppercase is required
    upper: bool = False

    # Whether conversion to uppercase must be skipped for some value
    upper_except: Any = None


def build_conditionbinmap_dict(df: pd.DataFrame, dataset_name: str) -> Dict[str, ConditionBinmap]:
    """
    This function provides the metadata for those features which need to be processed as follows: a set of conditions
    are defined so that, for each condition a replacement value is defined. This implies that if a value of that
    feature fulfills a certain condition, it's then replaced by the condition corresponding replacement value. Some
    features may share their conditions and their replacement values

    :param df:              Pandas DataFrame containing the features which will be processed this way
    :param dataset_name:    String representing which of the two (WHAT / WHEN) Device Recommender datasets is going to
                            be processed
    :return:                Dictionary providing the necessary metadata for each feature which requires to be processed
                            by the `condition2bin_transform` function
    """
    feature_conditionbinmap_dict = {}
    for feature in ['num_months_ext_age', 'num_months_renewal_duration_hist', 'mb_total_qt',
                    'voice_out_min_qt', 'ctr_activeprod_days', 'ctr_rev_eur_a3m',
                    'ctr_service_start_date_months']:
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                  (df[feature] >= 0) & (
                                                                                          df[feature] <= 1),
                                                                                  (df[feature] >= 2) & (
                                                                                          df[feature] <= 3),
                                                                                  (df[feature] >= 4) & (
                                                                                          df[feature] <= 5),
                                                                                  (df[feature] >= 6) & (
                                                                                          df[feature] <= 7),
                                                                                  df[feature] >= 8],
                                                                      bins=[OTHER, LOW, MID_LOW, MID, MID_TOP, TOP],
                                                                      default_value=0)})
    if dataset_name == WHAT:
        for feature in ['sms_out_num', 'cls_age']:
            feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                      (df[feature] >= 0) & (
                                                                                              df[feature] <= 1),
                                                                                      (df[feature] >= 2) & (
                                                                                              df[feature] <= 3),
                                                                                      (df[feature] >= 4) & (
                                                                                              df[feature] <= 5),
                                                                                      (df[feature] >= 6) & (
                                                                                              df[feature] <= 7),
                                                                                      df[feature] >= 8],
                                                                          bins=[OTHER, LOW, MID_LOW, MID, MID_TOP, TOP],
                                                                          default_value=0)})
        feature = 'acdp_cnt_6m'
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                  df[feature] == 0,
                                                                                  df[feature] == 1,
                                                                                  df[feature] == 2,
                                                                                  df[feature] >= 3],
                                                                      bins=[UNKNOWN, LOW, MID_LOW,
                                                                            MID_TOP, TOP],
                                                                      default_value=0)})
        feature = 'ctr_cnt_cancellations'
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                  df[feature] == 0,
                                                                                  df[feature] >= 1],
                                                                      bins=[UNKNOWN, LOW, TOP],
                                                                      default_value=0)})
        for feature in ['cls_cnt_act_myhandy', 'prt_ctr_cnt_myhandy']:
            feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                      df[feature] == 0,
                                                                                      df[feature] == 1,
                                                                                      df[feature] >= 2],
                                                                          bins=[UNKNOWN, LOW, MID, TOP],
                                                                          default_value=0)})

    if dataset_name == WHEN:
        feature = 'months_from_launch'
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                  (df[feature] >= 0) & (
                                                                                          df[feature] <= 1),
                                                                                  (df[feature] >= 2) & (
                                                                                          df[feature] <= 3),
                                                                                  (df[feature] >= 4) & (
                                                                                          df[feature] <= 5),
                                                                                  (df[feature] >= 6) & (
                                                                                          df[feature] <= 7),
                                                                                  df[feature] >= 8],
                                                                      bins=[OTHER, LOW, MID_LOW, MID, MID_TOP, TOP],
                                                                      default_value=0)})
        feature = 'n_renewals_hist'
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] == 0,
                                                                                  df[feature] == 1,
                                                                                  df[feature] == 2,
                                                                                  df[feature] == 3,
                                                                                  df[feature] > 3],
                                                                      bins=['0', '1', '2', '3', '+3'],
                                                                      default_value=0)})
        feature = 'sms_out_num'
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                  df[feature] == 0,
                                                                                  (df[feature] >= 1) & (
                                                                                          df[feature] <= 5),
                                                                                  (df[feature] >= 6) & (
                                                                                          df[feature] <= 15),
                                                                                  (df[feature] >= 16) & (
                                                                                          df[feature] <= 50),
                                                                                  df[feature] >= 50],
                                                                      bins=[UNKNOWN, '0', '1-5', '6-15', '16-50',
                                                                            '+50'],
                                                                      default_value=0)})
        feature = 'acdp_cnt_6m'
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                  df[feature] == 0,
                                                                                  df[feature] == 1,
                                                                                  (df[feature] >= 2) & (
                                                                                          df[feature] <= 5),
                                                                                  df[feature] > 5],
                                                                      bins=[UNKNOWN, '0', '1', '2-5', '+5'],
                                                                      default_value=0)})
        feature = 'cls_age'
        feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] <= 0,
                                                                                  (df[feature] > 0) & (
                                                                                          df[feature] <= 25),
                                                                                  (df[feature] >= 26) & (
                                                                                          df[feature] <= 45),
                                                                                  (df[feature] >= 46) & (
                                                                                          df[feature] <= 60),
                                                                                  (df[feature] >= 61) & (
                                                                                          df[feature] <= 80),
                                                                                  df[feature] > 80],
                                                                      bins=[UNKNOWN, '-25', '26-45', '46-60', '61-80',
                                                                            '+80'],
                                                                      default_value=0)})
        for feature in ['cls_cnt_act_myhandy', 'ctr_cnt_cancellations']:
            feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                      df[feature] == 0,
                                                                                      (df[feature] >= 1) & (
                                                                                              df[feature] <= 2),
                                                                                      df[feature] > 2],
                                                                          bins=[UNKNOWN, '0', '1-2', '+2'],
                                                                          default_value=0)})
        for feature in ['prt_ctr_cnt_myhandy', 'acc_ctr_cnt_tot', 'cls_cnt_ctr_tot']:
            feature_conditionbinmap_dict.update({feature: ConditionBinmap(conditions=[df[feature] < 0,
                                                                                      df[feature] == 0,
                                                                                      (df[feature] >= 1) & (
                                                                                              df[feature] <= 2),
                                                                                      (df[feature] >= 3) & (
                                                                                              df[feature] <= 4),
                                                                                      df[feature] > 4],
                                                                          bins=[UNKNOWN, '0', '1-2', '3-4', '4+'],
                                                                          default_value=0)})

    return feature_conditionbinmap_dict


def build_featurevaluemap_dict(dataset_name: str) -> Dict[str, FeatureValuemap]:
    """
    This function provides the metadata for those features which need to be processed in either one or serveral of
    this ways:
    - Map each value to another value (one to one mapping)
    - Assign a default value if the feature original value is not in the list of the values to be mapped
    - Transform to uppercase some of the values to be mapped

    :param dataset_name:    String representing which of the two (WHAT / WHEN) Device Recommender datasets is going to
                            be processed
    :return:                Dictionary providing the necessary metadata for each feature which requires to be processed
                            by the `valuemap_transform` function
    """
    feature_valuemap_dict = {'pre_postpaid_id': FeatureValuemap(ori_values=[1, 2], dest_values=['Post', 'Pre'])}
    feature_valuemap_dict.update({'brand_des': FeatureValuemap(ori_values=['apple', 'samsung', 'huawei', 'xiaomi'],
                                                               default_value=OTHER.lower())})
    feature_valuemap_dict.update(
        {'device_value_des_enrich': FeatureValuemap(ori_values=[ULTRALOW, FLAGSHIP, TOP.lower(),
                                                                MID.lower(), LOW.lower()],
                                                    dest_values=[ULTRA_LOW],
                                                    default_value=OTHER.lower())})
    feature_valuemap_dict.update({'cls_o2more_user': FeatureValuemap(upper=True, upper_except=UNKNOWN)})
    feature_valuemap_dict.update({'cls_title_name': FeatureValuemap(ori_values=['herr', 'frau'],
                                                                    dest_values=['MALE', 'FEMALE'],
                                                                    default_value=UNKNOWN)})
    feature_valuemap_dict.update({'ctr_email_address_flag': FeatureValuemap(upper=True, upper_except=UNKNOWN)})
    feature_valuemap_dict.update({'ctr_lifetime_value': FeatureValuemap(ori_values=['a', 'b', 'c', 'd'],
                                                                        dest_values=[TOP, MID_TOP, MID_LOW, LOW],
                                                                        default_value=UNKNOWN)})
    feature_valuemap_dict.update({'ctr_mnp_flag': FeatureValuemap(upper=True, upper_except=UNKNOWN)})
    feature_valuemap_dict.update({'ctr_multicard_flag': FeatureValuemap(upper=True, upper_except=UNKNOWN)})

    if dataset_name == WHAT:
        feature_valuemap_dict.update({'os_des': FeatureValuemap(ori_values=['android', 'ios'],
                                                                dest_values=['Android', 'iOS'],
                                                                default_value=OTHER)})
        feature_valuemap_dict.update({'resolution_display_des': FeatureValuemap(ori_values=['-1'], dest_values=[OTHER],
                                                                                upper=True, upper_except=OTHER)})
        feature_valuemap_dict.update({'battery_type_id': FeatureValuemap(ori_values=['li', 'ni'],
                                                                         default_value=OTHER.lower())})
        feature_valuemap_dict.update({'months_from_launch': FeatureValuemap(upper=True)})
        feature_valuemap_dict.update({'battery_capacity_qt': FeatureValuemap(ori_values=['-1'], dest_values=[OTHER],
                                                                             upper=True, upper_except=OTHER)})
        feature_valuemap_dict.update({'size_display_qt': FeatureValuemap(ori_values=['-1'], dest_values=[OTHER],
                                                                         upper=True, upper_except=OTHER)})
        feature_valuemap_dict.update({'camera_mpx_des': FeatureValuemap(ori_values=['-1'], dest_values=[OTHER],
                                                                        upper=True, upper_except=OTHER)})
        feature_valuemap_dict.update({'processor_speet_qt': FeatureValuemap(ori_values=['-1'], dest_values=[OTHER],
                                                                            upper=True, upper_except=OTHER)})
        feature_valuemap_dict.update({'technology_4g_ob_ind': FeatureValuemap(ori_values=['lte', 'no lte'],
                                                                              dest_values=[Y, N],
                                                                              default_value=UNKNOWN)})
        feature_valuemap_dict.update({'technology_5g_cd': FeatureValuemap(ori_values=['yes', 'no'],
                                                                          dest_values=[Y, N], default_value=UNKNOWN)})
        feature_valuemap_dict.update({'form_factor_des': FeatureValuemap(ori_values=['foldable', 'unknown'],
                                                                         dest_values=[Y, N], default_value=N)})
        feature_valuemap_dict.update(
            {'device_value_des_purchase_enrich': FeatureValuemap(ori_values=[ULTRALOW, FLAGSHIP,
                                                                             TOP.lower(),
                                                                             MID.lower(),
                                                                             LOW.lower()],
                                                                 dest_values=[ULTRA_LOW],
                                                                 default_value=OTHER.lower())})
    if dataset_name == WHEN:
        feature_valuemap_dict.update({'fl_lines_cust': FeatureValuemap(ori_values=[0, 1], dest_values=['0', '1'])})
        feature_valuemap_dict.update({'renewal_origin': FeatureValuemap(upper=True)})
        feature_valuemap_dict.update({'group_id_catalog': FeatureValuemap(ori_values=[1, 2, 3, 4, 5],
                                                                          dest_values=[LOW, MID_LOW, MID, MID_TOP, TOP],
                                                                          default_value=OTHER)})

    return feature_valuemap_dict


def prepare_devrec(dataset_path: str, dataset_name: str = WHAT, dataset_filename: str = '', sep: str = ',',
                   when_threshold: float = 0.85, verbose: int = 0) -> Tuple[Union[pd.DataFrame, None], List[str],
                                                                            List[str]]:
    """
    This function is intended to preprocess (cook) Device Recommender related datasets, so far WHEN and WHAT
    (observations only) dataset preprocessing have been implemented

    :param dataset_path:     String representing the path where the dataset to be processed is stored
    :param dataset_name:     String representing which of the two (WHAT / WHEN) Device Recommender datasets is going to
                             be processed
    :param dataset_filename: String which allows the user to specify a certain filename containing the dataset to be
                             preprocessed
    :param sep:              String representing the separator character to take into account when parsing original
                             datasets (default is comma ',')
    :param when_threshold:   Float representing the value for which, every score greater than that, will be considered
                             to be associated to a renewal in WHEN dataset
    :param verbose:          Verbosity level, where any value greater than 0 means the message is printed
    :return:                 Tuple containing:
                             - Pandas DataFrame containing the preprocessed dataset
                             - List of strings containing the features names
                             - List of strings containing the targets names
    """
    if dataset_name not in [WHAT, WHEN]:
        print('ERROR: dataset name {}, not recognized!'.format(dataset_name))
        return None, [], []

    xgprint(verbose, 'INFO: Preprocessing devrec {} dataset'.format(dataset_name))

    # Preparing FeatureMap dictionary
    featvalmap_dict = build_featurevaluemap_dict(dataset_name=dataset_name)

    # If a specific dataset filename has not been provided, default will be used
    if not len(dataset_filename):
        if dataset_name == WHAT:
            dataset_filename = 'what_dr_100K.csv'
        if dataset_name == WHEN:
            dataset_filename = 'when_dr_all_2M.csv'
    dataset_filepath = os.path.join(dataset_path, dataset_filename)
    xgprint(verbose, 'INFO:     Reading {}'.format(dataset_filepath))
    df = pd.read_csv(filepath_or_buffer=dataset_filepath, sep=sep)

    # Target preprocessing
    if dataset_name == WHAT:
        df = to_multiclass_problem(df=df, sort_columns=[ID_ORI, SCORE], exclude_columns=[TARGET, SCORE],
                                   sort_criteria=[True, False])
    if dataset_name == WHEN:
        df = set_target_from_threshold(df=df, threshold=when_threshold)
    xgprint(verbose, 'INFO:     Targets are distributed as follows:')
    xgprint(verbose, df[TARGET].value_counts())

    # Feature preprocessing
    if dataset_name == WHEN:
        xgprint(verbose, 'INFO:     Preprocessing features (value_discretization):')
        df = value_discretization(df=df, verbose=verbose)
    xgprint(verbose, 'INFO:     Preprocessing features (condition2bin_transform):')
    featcondbinmap_dict = build_conditionbinmap_dict(df=df, dataset_name=dataset_name)
    df = condition2bin_transform(df=df, feature_conditionbinmap_dict=featcondbinmap_dict, verbose=verbose)
    xgprint(verbose, 'INFO:     Preprocessing features (valuemap_transform):')
    df = valuemap_transform(df=df, feature_valuemap_dict=featvalmap_dict, verbose=verbose)

    # Drop unused/constant features
    features_to_drop = []
    if dataset_name == WHAT:
        features_to_drop = ['score', 'version_os_des', 'sim_num_des', 'brand_id', 'acc_ctr_cnt_tot', 'cls_cnt_ctr_tot']
    if dataset_name == WHEN:
        features_to_drop = ['target_nm', 'tac_id_next_renewal', 'brand_des_renewal', 'brand_id', 'future_renewal',
                            'past_renewal', 'score']
    xgprint(verbose, 'INFO:     Dropping unused/constant features: {}'.format(features_to_drop))
    df.drop(features_to_drop, axis=1, inplace=True)

    # Rename features
    xgprint(verbose, 'INFO:     Renaming features:')
    df, feature_cols = rename_header(df=df, dataset_name=dataset_name)

    # Target postprocessing
    xgprint(verbose, 'INFO:     Processing target:')
    df, target_cols = target_transform(df=df, dataset_name=dataset_name)

    return df, feature_cols, target_cols


def condition2bin_transform(df: pd.DataFrame, feature_conditionbinmap_dict: Dict[str, ConditionBinmap],
                            verbose: int = 0) -> pd.DataFrame:
    """
    This function takes care of transforming those feature which requires mapping all values inside a given interval
    to a certain value. There mechanics are as follows: if the current value of the feature fulfills a certain condition
    that value is replaced by another one which will be used to replace all other values fulfilling that condition

    :param df:                               Pandas DataFrame whose features will be transformed
    :param feature_conditionbinmap_dict:     Dictionary providing the necessary metadata for each feature which requires
                                             to be processed by the `condition2bin_transform` function
    :param verbose:                          Verbosity level, where any value greater than 0 means the message is
                                             printed
    :return:                                 Pandas DataFrame with those features transformed
    """
    for feature, conditionbinmap in feature_conditionbinmap_dict.items():
        if feature not in df.columns:
            continue
        condlist = conditionbinmap.conditions
        choices = conditionbinmap.bins
        default_value = conditionbinmap.default_value
        xgprint(verbose, 'INFO:          ========{}========'.format(feature))
        xgprint(verbose, df[feature].value_counts())
        df[feature] = np.select(condlist=condlist, choicelist=choices, default=default_value)
        xgprint(verbose, df[feature].value_counts())

    return df


def set_target_from_threshold(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """
    This function calculates each sample's target value by applying a given threshold to the sample's score

    :param df:          Pandas DataFrame whose target will be set
    :param threshold:   Float representing the value to be taken into account when calculating the target values from
                        the score
    :return:            Pandas DataFrame with the target set according to the threshold
    """
    df_score = df[df[TARGET] == 0].copy()
    target_thresh = df_score['score'].quantile(q=threshold)
    df_score.loc[df_score['score'] > target_thresh, 'target'] = 1

    return df_score


def value_discretization(df: pd.DataFrame, nbins=10, verbose: int = 0) -> pd.DataFrame:
    """
    This function splits in `nbins` similar width the continuous features. This way, each original values is replaced by
    the bin in which it falls (from 0 to nbins - 1). Further processing is later applied to this variables so that their
    bins are mapped to a human-readable value (0, 1 bins are mapped to LOW, 2. 3 bins are mapped to MID-LOW and so on)

    :param df:      Pandas DataFrame containing the features to be discretized
    :param nbins:   Number of bins among which the feature values will be distributed
    :param verbose: Verbosity level, where any value greater than 0 means the message is printed
    :return:        Pandas DataFrame whose features to discretize have been discretized
    """
    for feature in ['num_months_ext_age', 'num_months_renewal_duration_hist', 'months_from_launch', 'mb_total_qt',
                    'voice_out_min_qt', 'ctr_activeprod_days', 'ctr_rev_eur_a3m', 'ctr_service_start_date_months']:
        if len(np.unique(df[feature].values)) < nbins:
            print(
                '        WARNING: Number of unique values for feature {} is smaller than the number of bins: {}'.format(
                    feature, np.unique(df[feature].values)))
        df.loc[df[feature] < 0, feature] = None
        df[feature] = pd.qcut(df[feature], q=nbins, labels=np.arange(nbins)).astype('float').fillna(value=-1).astype(
            'int')
        xgprint(verbose, 'INFO:          ========{}========'.format(feature))
        xgprint(verbose, df[feature].value_counts())

    return df


def valuemap_transform(df: pd.DataFrame, feature_valuemap_dict: Dict[str, FeatureValuemap],
                       verbose: int = 0) -> pd.DataFrame:
    """
    This function takes care of those features which require one-to-one direct mapping and/or case transformations.
    A dataclass FeatureValuemap has been created to store metadata related to the transformations to be done

    :param df:                      Pandas DataFrame whose features will be transformed
    :param feature_valuemap_dict:   Dictionary providing for each feature, its values mapping instructions in the form
                                    of a FeatureValueMap dataclass object
    :param verbose:                 Verbosity level, where any value greater than 0 means the message is printed
    :return:                        Pandas DataFrame with those features transformed
    """
    for feature, valuemap in feature_valuemap_dict.items():
        if feature not in df.columns:
            continue
        ori_values = valuemap.ori_values
        dest_values = valuemap.dest_values
        default_value = valuemap.default_value
        xgprint(verbose, 'INFO:          ========{}========'.format(feature))
        xgprint(verbose, df[feature].value_counts())

        if default_value is not None:
            df.loc[~df[feature].isin(ori_values), feature] = default_value
        for i, value in enumerate(dest_values):
            df.loc[df[feature] == ori_values[i], feature] = value

        upper_value = valuemap.upper
        upper_except = valuemap.upper_except
        if upper_value:
            if upper_except is not None:
                df.loc[df[feature] != upper_except, feature] = df.loc[df[feature] != upper_except, feature].str.upper()
            else:
                df[feature] = df[feature].str.upper()
        xgprint(verbose, df[feature].value_counts())

    return df


def to_multiclass_problem(df: pd.DataFrame, sort_columns: List[str], exclude_columns: List[str],
                          sort_criteria: List[bool]) -> pd.DataFrame:
    """
    This function takes care of selecting for each record the target with the highest score

    :param df:              Pandas DataFrame which must be transformed
    :param sort_columns:    List of strings containing the names of those columns which must be sorted in order to
                            isolate for each record, the highest score
    :param exclude_columns: List of strings containing the names of those columns which won't be taken into account
                            when deleting duplicates
    :param sort_criteria:   List of boolean indicating whether sorting according to sort_columns parameter must be done
                            ascending or descending depending on the column
    :return:                Pandas DataFrame with one record per id whose target is the one which featured the highest
                            score
    """
    return df.sort_values(by=sort_columns, ascending=sort_criteria).drop_duplicates(
        subset=[c for c in df.columns if c not in exclude_columns])


def rename_header(df: pd.DataFrame, dataset_name: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    This function takes care of renaming pandas DataFrame columns

    :param df:              Pandas DataFrame whose columns will be renamed
    :param dataset_name:    String representing which of the two (WHAT / WHEN) Device Recommender datasets is being
                            processed
    :return:                Pandas DataFrame with its columns renamed
    """
    features_ori_names = []
    features_new_names = []
    if dataset_name == WHAT:
        features_ori_names = [ID_ORI, 'num_months_ext_age', 'pre_postpaid_id', 'num_months_renewal_duration_hist',
                              'os_des', 'resolution_display_des', 'battery_type_id', 'months_from_launch',
                              'battery_capacity_qt', 'size_display_qt', 'camera_mpx_des', 'processor_speet_qt',
                              'technology_4g_ob_ind', 'technology_5g_cd', 'form_factor_des', 'brand_des',
                              'device_value_des_enrich', 'device_value_des_purchase_enrich', 'mb_total_qt',
                              'sms_out_num', 'voice_out_min_qt', 'acdp_cnt_6m', 'cls_age', 'cls_cnt_act_myhandy',
                              'cls_o2more_user', 'cls_title_name', 'ctr_activeprod_days', 'ctr_cnt_cancellations',
                              'ctr_email_address_flag', 'ctr_lifetime_value', 'ctr_mnp_flag', 'ctr_multicard_flag',
                              'ctr_rev_eur_a3m', 'ctr_service_start_date_months', 'prt_ctr_cnt_myhandy']
        features_new_names = [ID, 'active_line_mt', 'paid_type', 'last_renewal_mt', 'o.s', 'resolution_display',
                              'battery_type', 'device_age_mt', 'battery', 'display_size', 'camera_mpx',
                              'processor_speed', 'is_4g', 'is_5g', 'is_foldable', 'brand', 'range', 'range_purchase',
                              'data_mb', 'sms_num', 'voice_min', 'calls_help_6m', 'age', 'myhandy_n_contracts',
                              'is_priority', 'gender', 'active_num_days', 'cancellations_num', 'is_email',
                              'lifetime_value', 'is_portability', 'is_multicard', 'revenue_3m', 'start_service_mt',
                              'myhandy_contracts_num']
    if dataset_name == WHEN:
        features_ori_names = [ID_ORI, 'num_months_ext_age', 'fl_lines_cust', 'pre_postpaid_id', 'n_renewals_hist',
                              'num_months_renewal_duration_hist', 'months_from_launch', 'renewal_origin',
                              'group_id_catalog', 'device_value_des_enrich', 'brand_des', 'mb_total_qt', 'sms_out_num',
                              'voice_out_min_qt', 'acdp_cnt_6m', 'cls_age', 'cls_cnt_act_myhandy', 'cls_o2more_user',
                              'cls_title_name', 'ctr_activeprod_days', 'ctr_cnt_cancellations',
                              'ctr_email_address_flag', 'ctr_lifetime_value', 'ctr_mnp_flag', 'ctr_multicard_flag',
                              'ctr_rev_eur_a3m', 'ctr_service_start_date_months', 'prt_ctr_cnt_myhandy',
                              'acc_ctr_cnt_tot', 'cls_cnt_ctr_tot']
        features_new_names = [ID, 'active_line_mt', 'lines', 'paid_type', 'num_renewals', 'last_renewal_mt',
                              'device_age_mt', 'device_tef', 'groupby_device', 'range', 'brand', 'data_mb', 'sms_num',
                              'voice_min', 'calls_help_6m', 'age', 'myhandy_n_contracts', 'is_priority', 'gender',
                              'active_num_days', 'cancellations_num', 'is_email', 'lifetime_value', 'is_portability',
                              'is_multicard', 'revenue_3m', 'start_service_mt', 'myhandy_contracts_num',
                              'myhandy_all_contracts_num', 'myhandy_total_contracts_num']

    return df.rename(columns=dict(zip(features_ori_names, features_new_names))), features_new_names[1:]


def target_transform(df: pd.DataFrame, dataset_name: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    This function renames the target columns names obtained after applying pandas dummies so that they become more
    representative and readable

    :param df:              Pandas DataFrame whose target columns will be renamed
    :param dataset_name:    String representing which of the two (WHAT / WHEN) Device Recommender datasets is going to
                            be processed
    :return:                Pandas DataFrame with the target columns renamed
    """
    if dataset_name == WHAT:
        target_ori_names = ['{}_Galaxy A51'.format(TARGET), '{}_Galaxy S21'.format(TARGET),
                            '{}_iPhone 11'.format(TARGET), '{}_Mi 10T'.format(TARGET),
                            '{}_iPhone SE 2020'.format(TARGET)]
        target_new_names = ['a51', 's21', 'mi10t', 'ip11', 'ipse2020']
        return pd.get_dummies(df,
                              prefix=TARGET,
                              columns=[TARGET]).rename(columns=dict(zip(target_ori_names,
                                                                        target_new_names))), target_new_names
    if dataset_name == WHEN:
        return pd.get_dummies(df, prefix=TARGET, columns=[TARGET]), ['_'.join([TARGET, str(val)]) for val in
                                                                     np.unique(df[TARGET].values)]


def main():
    # Device recommender dataset to be used is specified here (WHAT or WHEN)
    # Dataset filename can be parametrized by using prepare_devrec_dataset_filename parameter otherwise,
    # 'what_dr_100K.csv' will be used for WHAT and 'when_dr_all_2M.csv' for WHEN
    dataset_name = WHAT

    # Dataset path is specified here
    path = '../../datasets/'

    # Verbosity level: 0 or 1
    verbosity = 1
    df_devrec_cooked, feature_cols, target_cols = prepare_devrec(dataset_path=path, dataset_name=dataset_name,
                                                                 verbose=verbosity)
    if df_devrec_cooked is None:
        exit(255)
    xgprint(verbosity, 'INFO: "{}" summary:'.format(dataset_name))
    if verbosity:
        df_devrec_cooked.info()
    xgprint(verbosity, 'INFO: "{}" features names {}:'.format(dataset_name, feature_cols))
    xgprint(verbosity, 'INFO: "{}" targets {}:'.format(dataset_name, target_cols))

    # The desired explainer is created
    explainer = Explainer(dataset=df_devrec_cooked, importance_engine='TEF_SHAP',
                          destination_path='/home/cx02747/Utils/', number_of_features=11, verbose=verbosity)

    # Explaining process is triggered
    explainer.explain(feature_cols=feature_cols, target_cols=target_cols, num_samples_global_expl=50000)


if __name__ == '__main__':
    main()
