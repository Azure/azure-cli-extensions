#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Build and install azure-cli extension arcdata.
#
# Invoked under the build CI pipeline in AzureDevOps or gci Make. This script
# is typically executed from a parent instruction.
#
# Usage:
#
# $ install.sh

set -exv

# -- position to repository base root location --
: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../; pwd`}"
DIST_DIR=${REPO_ROOT_DIR}/output/packages
CLI_VERSION=$(${REPO_ROOT_DIR}/scripts/version.sh)

# package and install arcdata az ext
${REPO_ROOT_DIR}/scripts/package.sh

ls -ls ${DIST_DIR}

az --version
az extension add --source ${DIST_DIR}/arcdata-${CLI_VERSION}-py2.py3-none-any.whl -y --debug
az arcdata --help
