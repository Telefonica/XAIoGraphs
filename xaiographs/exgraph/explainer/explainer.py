import os
from typing import List

import pandas as pd

from xaiographs.common.constants import ID
from xaiographs.common.utils import filter_by_ids, get_common_info, get_features_info, sample_by_target
from xaiographs.exgraph.exporter.exporter import Exporter
from xaiographs.exgraph.feature_selector.feature_selector import FeatureSelector
from xaiographs.exgraph.importance.importance_calculator_factory import ImportanceCalculatorFactory
from xaiographs.exgraph.statistics.stats_calculator import StatsCalculator


class Explainer(object):
    """
    This class is intended to provide an abstract layer which encapsulates everything related to the explanation process
    from statistics calculatio, importance calculation (using the engine chosen by the user) and information export for
    visualization tasks
    """

    def __init__(self, dataset: pd.DataFrame, importance_engine: str, destination_path: str):
        """
        Constructor method for Explainer.
        - Property `top_features_target_` provides distance and rank information for each feature and target value, so
        that results can be understood
        - Property `top_features_` provides a list with the all the original features ranked

        :param dataset:                  Pandas DataFrame containing the whole dataset
        :param importance_engine:        String representing the name of the method use to compute feature importance
        :param destination_path:         String representing the path where output files will be stored

        """
        self.df = dataset
        self.path = destination_path
        self.engine = importance_engine
        self.top_features_ = []
        self.top_features_target_ = {}

    def explain(self, feature_cols: List[str], target_cols: List[str]):
        # This section is intended to retrieve information which will be used throughout the execution flow:
        #   Feature related information: different features columns names lists
        #   Target related information: top1_targets (ground truths) for each row, target_probs (probability for each
        #   target), top1_argmax (the indexes version of the top1_targets) and target columns names
        features_info, target_info = get_common_info(df=self.df, feature_cols=feature_cols, target_cols=target_cols)

        # Feature selector is instantiated
        selector = FeatureSelector(df=self.df, feature_cols=features_info.feature_columns,
                                   target_info=target_info, number_of_features=8)

        # Then it's used to select the top K features
        topk_features = selector.select_topk()
        self.top_features_ = selector.top_features_
        self.top_features_target_ = selector.top_features_target_

        # Dataset must be rebuilt by selecting the topk features, the ID and the target columns
        self.df = self.df[[ID] + topk_features + target_cols]

        # Since feature columns have changed, information related to features must be generated again
        features_info = get_features_info(df=self.df, feature_cols=topk_features, target_cols=target_cols)

        # Here, the row IDs to be sampled for explanation are generated. A sample ids mask will be used for id
        # filtering, (the list of sample ids is retrieved too to perform consistency checks)
        # TODO: Los ID a samplear podrían pasarse a través de un fichero de texto. El parámetro que determina el número
        #  de muestras también debería poder ser pasado como entrada. Ambas opciones (fichero con IDs/parámetro con
        #  número de muestras, son excluyentes
        sample_ids_mask, sample_ids = sample_by_target(ids=self.df[ID].values, top1_targets=target_info.top1_targets,
                                                       num_samples=100,
                                                       target_probs=target_info.target_probs,
                                                       target_cols=target_info.target_columns)

        # Computations have been split in two types: statistics calculation and importance calculation
        #   StatsCalculator takes care of everything related to frequency calculation, counting...
        stats = StatsCalculator(df=self.df, top1_targets=target_info.top1_targets,
                                feature_cols=features_info.feature_columns,
                                float_feature_cols=features_info.float_feature_columns,
                                target_cols=target_info.target_columns,
                                sample_ids_mask=sample_ids_mask, sample_ids=sample_ids)
        edges_stats, nodes_stats, target_distribution = stats.calculate_stats()

        #   An ImportanceCalculator object is used to compute importance values
        imp_calc_factory = ImportanceCalculatorFactory()
        importance_calculator = imp_calc_factory.build_importance_calculator(self.engine,
                                                                             explainer_params={},
                                                                             df=self.df,
                                                                             sample_ids_mask_2_explain=sample_ids_mask,
                                                                             feature_cols=features_info.feature_columns,
                                                                             target_cols=target_info.target_columns,
                                                                             train_stratify=True)

        top1_importance_features, global_explainability, global_nodes_importance, df_explanation_sample = (
            importance_calculator.calculate_importance(features_info=features_info, target_info=target_info))

        # Sample reason why
        # TODO: Aquí iría la parte del why
        df_reason_why = filter_by_ids(df=pd.read_csv(filepath_or_buffer=os.path.join(self.path, 'reason_why.csv')),
                                      sample_id_mask=sample_ids_mask)

        # Exporter takes care of the following tasks:
        #   Mixing calculated statistics and calculated importance when needed
        #   Calculating weights in pixels
        #   Persisting results
        # TODO: Al igual que un hipotético fichero con IDs, o un número de samples...habría que meter como parámetro
        #  el path donde se quieren guardar los ficheros
        exporter = Exporter(df_explanation_sample=df_explanation_sample, path=self.path)
        exporter.export(features_info=features_info, target_info=target_info, sample_ids_mask=sample_ids_mask,
                        global_target_explainability=top1_importance_features,
                        global_explainability=global_explainability,
                        global_nodes_importance=global_nodes_importance, edges_info=edges_stats, nodes_info=nodes_stats,
                        target_distribution=target_distribution, reason_why=df_reason_why)
