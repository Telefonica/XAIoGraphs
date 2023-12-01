# -*- coding: utf-8 -*-

u"""
© 2023 Telefónica Digital España S.L.
This file is part of XAIoGraphs.

XAIoGraphs is free software: you can redistribute it and/or modify it under the terms of the Affero GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

XAIoGraphs is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Affero GNU General Public License
for more details.

You should have received a copy of the Affero GNU General Public License along with XAIoGraphs. If not,
see https://www.gnu.org/licenses/."""

from xaiographs import Explainer
from xaiographs import Why
from xaiographs.datasets import load_compas_reality_discretized, load_compas_reality_why

LANG = 'en'


def main():
    # LOAD DATASETS & SEMANTICS
    df_compas, feature_cols, target_cols = load_compas_reality_discretized()
    df_values_semantics, df_target_values_semantics = load_compas_reality_why(language=LANG)

    # EXPLAINER
    explainer = Explainer(importance_engine='LIDE', verbose=1)
    explainer.fit(df=df_compas, feature_cols=feature_cols, target_cols=target_cols)

    # WHY
    why = Why(language=LANG,
              explainer=explainer,
              why_values_semantics=df_values_semantics,
              why_target_values_semantics=df_target_values_semantics,
              verbose=1)
    why.fit()


if __name__ == "__main__":
    main()
