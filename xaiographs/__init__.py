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

import sys
import numpy as np

from .exgraph.explainer import Explainer
from .fairness import Fairness
from .why.why import Why

# Check the Python version
if sys.version_info < (3, 10) or sys.version_info >= (3, 13):
    raise RuntimeError("Your Python {}.{}.{} version is incompatible with XAIoGraphs.\n"
                       "XAIoGraphs requires Python 3.10 or higher, but less than 3.13."
                       .format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))

# Check the numpy version
numpy_version = np.__version__

# Split the version into a tuple of integers (e.g., '1.26.4' -> (1, 26, 4))
numpy_version_tuple = tuple(map(int, numpy_version.split('.')))

# Check if the version is within the allowed range (>=1.26.0, <2.0.0)
if not ((1, 26, 0) <= numpy_version_tuple < (2, 0, 0)):
    raise ImportError("Your numpy version {} is incompatible with XAIoGraphs.\n"
                      "XAIoGraphs requires numpy version 1.26.0 or higher, but less than 2.0.0"
                      .format(numpy_version))
