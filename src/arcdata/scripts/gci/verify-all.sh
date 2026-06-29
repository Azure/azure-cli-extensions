#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Instructions to be invoked under the build GCI pipeline in container.
#
# Usage:
#
# $ verify-all.sh

set -exv

: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../../; pwd`}"
DIST_DIR=${REPO_ROOT_DIR}/output/coverage

mkdir -p ${DIST_DIR}

# -- script being invoked outside of a make target, thus template has been generated yet.
if [ ! -f ${REPO_ROOT_DIR}/arcdata/azext_arcdata/kubernetes_sdk/dc/templates/bootstrap/role-bootstrapper.yaml.tmpl ]; then
  ${REPO_ROOT_DIR}/scripts/generate-role-template.sh
fi

python3 -m venv ${REPO_ROOT_DIR}/env
. ${REPO_ROOT_DIR}/env/bin/activate
pip install -r ${REPO_ROOT_DIR}/dev-requirements.txt
pip install -e ${REPO_ROOT_DIR}/arcdata
pip install -e ${REPO_ROOT_DIR}/tools/pytest-az

#TODO - turn on
# Run command argument signatures checks
# flake8 ${REPO_ROOT_DIR}/arcdata/azext_arcdata || exit 1
black ${REPO_ROOT_DIR}/arcdata/azext_arcdata || exit 1

# Run code coverage and unit-tests
pytest --capture=sys ${REPO_ROOT_DIR}/arcdata/azext_arcdata/test --junitxml "./output/coverage/TEST-UT-results.xml" --cov=azext_arcdata --cov-report=xml:output/coverage/coverage.xml --cov-report=html:output/coverage/htmlcov