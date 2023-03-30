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


from xaiographs.common.utils import xgprint
from xaiographs.exgraph.importance.lide import LIDE


class ImportanceCalculatorFactory(object):
    LIDE = 'LIDE'

    def __init__(self):
        """Importance Calculator factory class

        """
        pass

    def build_importance_calculator(self, name: str, **importance_calculator_params):
        """
        This function builds an ImportanceCalculator object. The ImportanceCalculator type will be given by the name
        parameter

        :param name:                         String, providing the name of the ImportanceCalculator to be built
        :param importance_calculator_params: Dictionary, of parameters which will vary according to the
                                             ImportanceCalculator to be built
        :return:                             ImportanceCalculator object of the requested type
        """
        if name == self.LIDE:
            xgprint(importance_calculator_params['verbose'],
                    'INFO: {} importance calculator will be instantiated'.format(name))
            return LIDE(**importance_calculator_params)
        else:
            print('ERROR:{} is not a valid importance calculator!!'.format(name))
            return None
