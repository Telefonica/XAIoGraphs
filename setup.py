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


from setuptools import setup

from xaiographs.common.constants import WEB_ENTRY_POINT

__VERSION__ = open('VERSION').read().strip()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='xaiographs',
    version=__VERSION__,
    description='Python library providing Explainability & Fairness AI functionalities',
    long_description_content_type="text/markdown",
    long_description=open('README.md', 'r').read(),
    url='https://github.com/Telefonica/XAIoGraphs',
    keywords=['explainability', 'fairness', 'IA', 'Machine Learning'],
    author='Telefonica I+D',
    author_email='ricardo.moyagarcia@telefonica.com',
    license='AGPL-3.0 license',
    python_requires='>=3.7',
    packages=['xaiographs'],
    include_package_data=True,
    install_requires=required,
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        "console_scripts": [
            "{} = xaiographs.viz.launcher:main".format(WEB_ENTRY_POINT),
            "titanic_example = xaiographs.examples.titanic_example:main",
            "body_performance_example = xaiographs.examples.body_performance_example:main",
            "education_performance_example = xaiographs.examples.education_performance_example:main",
            "compas_example = xaiographs.examples.compas_example:main"
        ]
    }
)
