#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Invoked under the build CI pipeline in AzureDevOps. This script is typically
# executed from a parent instruction.
#
# The single entry point to obtain the ArcData extension version.
#
# Usage:
#
# $ version.sh

: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../; pwd`}"

CLI_VERSION=`cat ${REPO_ROOT_DIR}/arcdata/azext_arcdata/__version__.py | \
   grep __version__ | \
   sed s/' '//g | \
   sed s/'__version__='// | \
   sed s/\"//g | \
   sed "s/^'\(.*\)'$/\1/"`

# -- Dynamically include ADO build pipeline run number, skip release_candidate & release/* branches --
if [ -n "${PIPELINE_BUILD_NUMBER}" ] && [ "${SOURCE_BRANCH}" != "refs/heads/release_candidate"  || "${SOURCE_BRANCH}" != "refs/heads/release/"* ]; then
   PIPELINE_BUILD_NUMBER=${CLI_VERSION}.${PIPELINE_BUILD_NUMBER}
   sed -i "s/${CLI_VERSION}/${PIPELINE_BUILD_NUMBER}/g" ${REPO_ROOT_DIR}/arcdata/azext_arcdata/__version__.py

   CLI_VERSION=`cat ${REPO_ROOT_DIR}/arcdata/azext_arcdata/__version__.py | \
      grep __version__ | \
      sed s/' '//g | \
      sed s/'__version__='// | \
      sed s/\"//g | \
      sed "s/^'\(.*\)'$/\1/"`
fi

echo ${CLI_VERSION}