#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Instructions to be invoked under the build CI pipeline in AzureDevOps.
#
# Usage:
#
# $ pipeline.sh

set -exv

: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../../../; pwd`}"
DIST_DIR=${REPO_ROOT_DIR}/output
CLI_VERSION=$(${REPO_ROOT_DIR}/scripts/version.sh)
#EXT_WHL=${BUILD_ARTIFACTSTAGINGDIRECTORY}/arcdata-${CLI_VERSION}-py2.py3-none-any.whl
ls -la ${BUILD_ARTIFACTSTAGINGDIRECTORY}
ls -la ${BUILD_ARTIFACTSTAGINGDIRECTORY}/ONEBRANCH_ARTIFACT/
ls -la ${BUILD_ARTIFACTSTAGINGDIRECTORY}/ONEBRANCH_ARTIFACT/wheels
EXT_WHL=${BUILD_ARTIFACTSTAGINGDIRECTORY}/ONEBRANCH_ARTIFACT/wheels/arcdata-${CLI_VERSION}-py2.py3-none-any.whl

mkdir -p ${DIST_DIR}
python ${REPO_ROOT_DIR}/scripts/ci/index-update/index.py ${EXT_WHL} ${DIST_DIR}
