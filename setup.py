# -*- coding: utf-8 -*-

from setuptools import setup

__VERSION__ = open('VERSION').read().strip()
WEB_ENTRY_POINT = 'xaioweb'

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
    packages=['xaiographs'],
    include_package_data=True,
    install_requires=required,
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        "console_scripts": [
            "{} = xaiographs.viz.launcher:main".format(WEB_ENTRY_POINT)
        ]
    }
)
