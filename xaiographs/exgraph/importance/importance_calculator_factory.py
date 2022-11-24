from xaiographs.exgraph.importance.tef_shap import TefShap


class ImportanceCalculatorFactory(object):
    TEF_SHAP = 'TEF_SHAP'

    def __init__(self):
        pass

    def build_importance_calculator(self, name: str, **importance_calculator_params):
        """
        This function builds an ImportanceCalculator object. The ImportanceCalculator type will be given by the name
        parameter

        :param name:                         String providing the name of the ImportanceCalculator to be built
        :param importance_calculator_params: Dictionary of parameters which will vary according to the
                                             ImportanceCalculator to be built
        :return:                             ImportanceCalculator object of the requested type
        """
        if name == self.TEF_SHAP:
            print('INFO: {} importance calculator will be instantiated'.format(name))
            return TefShap(**importance_calculator_params)
        else:
            print('ERROR:{} is not a valid importance calculator!!'.format(name))
            return None
