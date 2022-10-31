from typing import List

import numpy as np
import pandas as pd

from xaiographs.common.constants import COMMA_SEP, TARGET


def save_global_target_explained_info(df_explained_global: pd.DataFrame, feature_cols: List[str], target_cols: List[str],
                                      top1_targets: List[str]):
    pd.DataFrame(np.concatenate((np.array(target_cols).reshape(-1, 1), np.transpose(df_explained_global)), axis=1),
                 columns=[TARGET] + feature_cols).to_csv('/home/cx02747/Utils/global_target_explainability.csv',
                                                         sep=COMMA_SEP, index=False)

    target_probs = np.array([top1_targets.count(target) for target in target_cols]) / len(top1_targets)
    pd.DataFrame((target_probs.reshape(-1, 1) * np.transpose(df_explained_global)).mean(axis=0).reshape(1, -1),
                 columns=feature_cols).to_csv('/home/cx02747/Utils/global_explainability.csv', sep=COMMA_SEP,
                                              index=False)
