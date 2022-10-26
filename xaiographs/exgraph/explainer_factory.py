from typing import Dict

from xaiographs.exgraph.tef_shap import TefShap


class ExplainerFactory(object):
    _TEF_SHAP = 'TEF_SHAP'

    def build_explainer(self, name: str, explainer_params: Dict):
        """
        This function builds an Explainer object. The Explainer type will be given by the name parameter

        :param name:             String providing the name of the Explainer to be built
        :param explainer_params: Dictionary of parameters which will vary according to the Explainer to be built
        :return:                 Explainer object of the requested type
        """
        if name == self._TEF_SHAP:
            return TefShap(explainer_params)
        else:
            return None
