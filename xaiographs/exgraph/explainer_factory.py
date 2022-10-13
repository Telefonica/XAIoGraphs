from xaiographs.exgraph.explainer import Explainer
from xaiographs.exgraph.tef_shap import TefShap

from typing import Dict


class ExplainerFactory(object):
    NAME = Explainer.NAME
    TEF_SHAP = 'TEF_SHAP'

    def build_explainer(self, name: str, explainer_params: Dict):
        if name == self.TEF_SHAP:
            return TefShap(explainer_params)
        else:
            return None
