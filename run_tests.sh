#!/usr/bin/env bash

python --version
mkdir test_results

export PYTHONIOENCODING=utf8
export CI_ENV=True

COVERAGE_FILE=test_results/.coverage_unit nosetests --with-coverage --cover-erase --cover-package=. --cover-branches --with-xunit --xunit-file=test_results/unit -v -x tests/unit && \

export COVERAGE_FILE=.coverage  && \
coverage combine test_results/.coverage_*  && \
coverage xml
