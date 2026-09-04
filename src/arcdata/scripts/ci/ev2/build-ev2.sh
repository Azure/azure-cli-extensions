#!/bin/bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Build and install azure-cli extension arcdata.
#
# This cript rotates sourcing environment variables to generate EV2 manifests,
# used by the Azure DevOps Release Pipelines.
#

set -exv

TARGET_DIRECTORY=$1

ROOT=`git rev-parse --show-toplevel`
pushd ${ROOT}

export EV2_SOURCE_PATH="${ROOT}/projects/azure-cli-extension/scripts/ci/ev2"
export EV2_ENV_PATH="${EV2_SOURCE_PATH}/sourceenv"

source ${EV2_SOURCE_PATH}/sourceenv/blob-storage.env
export DOLLAR='$'
envsubst < "$EV2_SOURCE_PATH/ServiceModels.json.tmpl" > "${TARGET_DIRECTORY}/ServiceModels.json"
envsubst < "$EV2_SOURCE_PATH/RolloutSpecs.json.tmpl" > "${TARGET_DIRECTORY}/RolloutSpecs.json"
envsubst < "$EV2_SOURCE_PATH/Parameters.json.tmpl" > "${TARGET_DIRECTORY}/Parameters.json"

# Non tpl file
#
cp "${EV2_SOURCE_PATH}/ScopeBindings.json" "${TARGET_DIRECTORY}"

popd