#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Instructions to be invoked under the build CI pipeline in AzureDevOps.
#
# Kickoff wheel install tests against different python versions in `$TOX_ENV`.
#
# Prerequisites:
#
#   ENV VARS:
#
#   - export TOX_ENV=py36|py37|py38
#
# Usage:
#
# $ pipeline-linux.sh

set -exv

: "${TOX_ENV:?TOX_ENV environment variable not set to (py311}"
: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../../../; pwd`}"
DIST_DIR=${BUILD_ARTIFACTSTAGINGDIRECTORY:=${REPO_ROOT_DIR}/output/unit-tests}
export REPO_ROOT_DIR=${REPO_ROOT_DIR}
mkdir -p ${DIST_DIR}

#INDEX_URL=https://msdata:${PAT_TOKEN}@msdata.pkgs.visualstudio.com/_packaging/Arcdata/pypi/simple/ 
#INDEX_URL=https://build::${PAT_TOKEN}@msdata.pkgs.visualstudio.com/Tina/_packaging/adshybrid-Consumption/pypi/simple/
INDEX_URL=https://build:${PAT_TOKEN}@msdata.pkgs.visualstudio.com/Tina/_packaging/Tina_PublicPackages/pypi/simple

python --version

pip install --index-url ${INDEX_URL} -r ${REPO_ROOT_DIR}/dev-requirements.txt
pip install -e ${REPO_ROOT_DIR}/arcdata --index-url ${INDEX_URL}
pip install -e ${REPO_ROOT_DIR}/tools/pytest-az --index-url ${INDEX_URL}

cp ${REPO_ROOT_DIR}/scripts/ci/unit-tests/tox.ini ${DIST_DIR}
tox -e ${TOX_ENV} -c ${DIST_DIR}/tox.ini
