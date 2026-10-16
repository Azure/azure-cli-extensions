#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Instructions to be invoked under the build CI pipeline in AzureDevOps.
#
# Run Lint/Style + Argument Signatures
#
# Usage:
#
# $ pipeline.sh

set -exv

: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../../../; pwd`}"

# Assert linting
${REPO_ROOT_DIR}/scripts/lint.sh || exit 1
