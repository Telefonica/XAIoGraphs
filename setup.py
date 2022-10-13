# -*- coding: utf-8 -*-

u"""
(c) Copyright 2022 Telefónica. All Rights Reserved.
The copyright to the software program(s) is property of Telefónica.
The program(s) may be used and or copied only with the express written consent of Telefónica or in accordance with
the terms and conditions stipulated in the agreement/contract under which the program(s) have been supplied.
"""

from setuptools import setup, find_packages

__VERSION__ = open('VERSION').read().strip()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='XAIoGraphs',
    version=__VERSION__,
    description='AI Products Python library',
    url='https://github.com/Telefonica/XAIoGraphs',
    author='Telefonica I+D',
    author_email='ricardo.moyagarcia@telefonica.com',
    license='(C) Telefonica I+D',
    long_description='Python library providing explainability AI funcionalities',
    python_requires='>=3.7',
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose']
)
