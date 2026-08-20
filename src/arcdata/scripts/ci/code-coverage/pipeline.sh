#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Instructions to be invoked under the build CI pipeline in AzureDevOps.
#
# Run verify (Code Coverage + Lint/Style + Argument Signatures)'
#
# Usage:
#
# $ pipeline.sh

set -exv

: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../../../; pwd`}"

# -- script being invoked outside of a make target, thus template has been generated yet.
if [ ! -f ${REPO_ROOT_DIR}/arcdata/azext_arcdata/kubernetes_sdk/dc/templates/bootstrap/role-bootstrapper.yaml.tmpl ]; then
  ${REPO_ROOT_DIR}/scripts/generate-role-template.sh
fi

INDEX_URL=https://build:${PAT_TOKEN}@msdata.pkgs.visualstudio.com/Tina/_packaging/Tina_PublicPackages/pypi/simple

# Install test deps 
pip install -r ${REPO_ROOT_DIR}/dev-requirements.txt --index-url ${INDEX_URL}
pip install -e ${REPO_ROOT_DIR}/tools/pytest-az --index-url ${INDEX_URL}
pip install -e ${REPO_ROOT_DIR}/arcdata --index-url ${INDEX_URL}

# Run code coverage and unit-tests
pytest --junitxml "./output/coverage/TEST-UT-results.xml" --cov=azext_arcdata --cov-report=xml:output/coverage/coverage.xml  --cov-report=html:output/coverage/htmlcov
