#!/usr/bin/env bash

python --version
mkdir test_results

export PYTHONIOENCODING=utf8
export CI_ENV=True

#COVERAGE_FILE=test_results/.coverage_acceptance_exgraph_behave coverage run --source=. --branch -m behave tests/acceptance/xaiographs/exgraph --no-capture --junit --junit-directory test_results/acceptance && \
#COVERAGE_FILE=test_results/.coverage_acceptance_fairness_behave coverage run --source=. --branch -m behave tests/acceptance/xaiographs/fairness --no-capture --junit --junit-directory test_results/acceptance && \
#COVERAGE_FILE=test_results/.coverage_acceptance_profiling_behave coverage run --source=. --branch -m behave tests/acceptance/xaiographs/profiling --no-capture --junit --junit-directory test_results/acceptance && \
#COVERAGE_FILE=test_results/.coverage_acceptance_transformations_behave coverage run --source=. --branch -m behave tests/acceptance/xaiographs/transformations --no-capture --junit --junit-directory test_results/acceptance && \
#COVERAGE_FILE=test_results/.coverage_acceptance_viz_behave coverage run --source=. --branch -m behave tests/acceptance/xaiographs/viz --no-capture --junit --junit-directory test_results/acceptance && \
#COVERAGE_FILE=test_results/.coverage_acceptance_why_behave coverage run --source=. --branch -m behave tests/acceptance/xaiographs/why --no-capture --junit --junit-directory test_results/acceptance && \
COVERAGE_FILE=test_results/.coverage_unit nosetests --with-coverage --cover-erase --cover-package=. --cover-branches --with-xunit --xunit-file=test_results/unit -v -x tests/unit && \

export COVERAGE_FILE=.coverage  && \
coverage combine test_results/.coverage_*  && \
coverage xml
