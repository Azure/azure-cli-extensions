#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Instructions to be invoked under the build CI pipeline in AzureDevOps.
# Updates `azure-cli-extensions-pr.tpl` with current `CLI_VERSION` to be saved
# as an executable shell script in ADO artifacts used during the ADO releases
# stage.
#
# Usage:
#
# $ pipeline.sh
#

set -exv

: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../../../; pwd`}"
DIST_DIR=${REPO_ROOT_DIR}/output
PR_SCRIPT_TPL=${REPO_ROOT_DIR}/scripts/ci/release/azure-cli-extensions-pr.tpl
PR_SCRIPT=${DIST_DIR}/azure-cli-extensions-pr.sh
CLI_VERSION=$(${REPO_ROOT_DIR}/scripts/version.sh)

mkdir -p ${DIST_DIR}

# sub in CLI_VERSION
echo "CLI_VERSION = ${CLI_VERSION}"
sed -e "s|{{CLI_VERSION}}|${CLI_VERSION}|g" ${PR_SCRIPT_TPL} > ${PR_SCRIPT}
chmod 755 ${PR_SCRIPT}
