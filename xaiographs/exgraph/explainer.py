import os
from typing import List, Tuple

import pandas as pd

from xaiographs.common.constants import ID
from xaiographs.common.utils import FeaturesInfo, TargetInfo, get_features_info, get_target_info, sample_by_target, \
    xgprint
from xaiographs.exgraph.exporter import Exporter
from xaiographs.exgraph.feature_selector import FeatureSelector
from xaiographs.exgraph.importance.importance_calculator import ImportanceCalculator
from xaiographs.exgraph.importance.importance_calculator_factory import ImportanceCalculatorFactory
from xaiographs.exgraph.stats_calculator import StatsCalculator


class Explainer(object):
    """
    This class is intended to provide an abstract layer which encapsulates everything related to the explanation process
    from statistics calculation, importance calculation (using the engine chosen by the user) and information export for
    visualization tasks
    """

    def __init__(self, dataset: pd.DataFrame, importance_engine: str, destination_path: str,
                 number_of_features: int = 8, verbose: int = 0):
        """
        Constructor method for Explainer.
        - Property `top_features_target_` provides distance and rank information for each feature and target value, so
        that results can be understood
        - Property `top_features_` provides a list with the all the original features ranked

        :param dataset:                  Pandas DataFrame containing the whole dataset
        :param importance_engine:        String representing the name of the method use to compute feature importance
        :param destination_path:         String representing the path where output files will be stored
        :param number_of_features:       Integer representing the number of features to be selected
        :param verbose:                  Verbosity level, where any value greater than 0 means the message is printed

        """
        self.df = dataset
        self.path = destination_path
        self.engine = importance_engine
        self.number_of_features = number_of_features
        self.top_features_ = []
        self.top_features_target_ = {}
        self.verbose = verbose

    def __get_common_info(self, feature_cols: List[str], target_cols: List[str]) -> Tuple[FeaturesInfo, TargetInfo]:
        """
        This function orchestrates the generation of both, features columns information and target information

        :param feature_cols: List of strings containing the column names for the features
        :param target_cols:  List of strings containing the possible targets
        :return:             NamedTuple containing all the feature column names lists which will be used all through the
                             execution flow and another NamedTuple containing target related info
        """

        features_info = get_features_info(df=self.df, feature_cols=feature_cols, target_cols=target_cols)
        target_info = get_target_info(df=self.df, target_cols=target_cols)

        return features_info, target_info

    def explain(self, feature_cols: List[str], target_cols: List[str], num_samples_local_expl: int = 100,
                num_samples_global_expl: int = 50000, batch_size_expl: int = 5000):
        if num_samples_global_expl < num_samples_local_expl:
            print('ERROR: num_samples_global_expl ({}) < num_samples_local_exp ({}): Number of samples for global '
                  'explainability must be larger than the number of samples for local explainability'
                  .format(num_samples_global_expl, num_samples_local_expl))
            exit(255)

        # This section is intended to retrieve information which will be used throughout the execution flow:
        #   Feature related information: different features columns names lists
        #   Target related information: top1_targets (ground truths) for each row, target_probs (probability for each
        #   target), top1_argmax (the indexes version of the top1_targets) and target columns names
        features_info, target_info = self.__get_common_info(feature_cols=feature_cols, target_cols=target_cols)

        # Feature selector is instantiated
        selector = FeatureSelector(df=self.df, feature_cols=features_info.feature_columns, target_info=target_info,
                                   number_of_features=self.number_of_features, verbose=self.verbose)

        # Then it's used to select the top K features
        topk_features = selector.select_topk()
        self.top_features_ = selector.top_features_
        self.top_features_target_ = selector.top_features_target_

        # Dataset must be rebuilt by selecting the topk features, the ID and the target columns
        self.df = self.df[[ID] + topk_features + target_cols]

        # Since feature columns have changed, information related to features must be generated again
        features_info = get_features_info(df=self.df, feature_cols=topk_features, target_cols=target_cols)

        # Computations have been split in two types: statistics calculation and importance calculation
        #   An ImportanceCalculator object is used to compute importance values
        imp_calc_factory = ImportanceCalculatorFactory()
        importance_calculator = imp_calc_factory.build_importance_calculator(self.engine,
                                                                             explainer_params={},
                                                                             feature_cols=features_info.feature_columns,
                                                                             target_info=target_info,
                                                                             train_stratify=True,
                                                                             verbose=self.verbose)
        top1_importance_features, global_explainability, global_nodes_importance, df_explanation_global = (
            importance_calculator.calculate_importance(df=self.df, features_info=features_info,
                                                       num_samples=num_samples_global_expl, batch_size=batch_size_expl))

        # Here, the row IDs to be sampled for local explanation are generated. A sample ids mask will be used for id
        # filtering, (the list of sample ids is retrieved too to perform consistency checks)
        target_info = get_target_info(df=df_explanation_global, target_cols=target_cols)
        sample_ids_mask, sample_ids = sample_by_target(ids=df_explanation_global[ID].values,
                                                       top1_targets=target_info.top1_targets,
                                                       num_samples=num_samples_local_expl,
                                                       target_probs=target_info.target_probs,
                                                       target_cols=target_info.target_columns)

        # Once global explanation related information is calculated. The explanation DataFrame is sampled, so that only
        # some rows will be taken into account when generating the local output for visualization
        xgprint(self.verbose, 'INFO:     Sampling the dataset to be locally explained: {} samples will be used ...'.
                format(num_samples_local_expl))
        df_explanation_sample = ImportanceCalculator.sample_explanation(df_explanation=df_explanation_global,
                                                                        sample_ids_mask_2_explain=sample_ids_mask)

        #   StatsCalculator takes care of everything related to frequency calculation, counting...
        stats = StatsCalculator(df=df_explanation_global[[ID] + features_info.feature_columns + target_cols],
                                top1_targets=target_info.top1_targets,
                                feature_cols=features_info.feature_columns,
                                float_feature_cols=features_info.float_feature_columns,
                                target_cols=target_info.target_columns,
                                sample_ids_mask=sample_ids_mask, sample_ids=sample_ids, verbose=self.verbose)
        edges_stats, nodes_stats, target_distribution = stats.calculate_stats()

        # Sample reason why
        # TODO: Aquí iría la parte del why
        df_why = pd.read_csv(filepath_or_buffer=os.path.join(self.path, 'reason_why_devrec100k.csv'))
        df_reason_why = df_why[df_why[ID].isin(list(map(int, sample_ids)))]

        # Exporter takes care of the following tasks:
        #   Mixing calculated statistics and calculated importance when needed
        #   Calculating weights in pixels
        #   Persisting results
        # TODO: Al igual que un hipotético fichero con IDs, o un número de samples...habría que meter como parámetro
        #  el path donde se quieren guardar los ficheros
        exporter = Exporter(df_explanation_sample=df_explanation_sample, path=self.path, verbose=self.verbose)
        exporter.export(features_info=features_info, target_info=target_info, sample_ids_mask=sample_ids_mask,
                        global_target_explainability=top1_importance_features,
                        global_explainability=global_explainability,
                        global_nodes_importance=global_nodes_importance, edges_info=edges_stats, nodes_info=nodes_stats,
                        target_distribution=target_distribution, reason_why=df_reason_why)
