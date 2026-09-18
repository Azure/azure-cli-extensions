#!/usr/bin/env bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# Build azure-cli extension arcdata.
#
# Invoked under the build CI pipeline in AzureDevOps or gci Make. This script
# is typically executed from a parent instruction.
#
# Usage:
#
# $ package.sh

#set -exv

# -- position to repository base root location --
: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../; pwd`}"
DIST_DIR=${REPO_ROOT_DIR}/output/packages
CLI_VERSION=$(${REPO_ROOT_DIR}/scripts/version.sh)
cd ${REPO_ROOT_DIR} || exit 1

echo "azext_arcdata VERSION: ${CLI_VERSION}"
echo "DIST DIRECTORY: ${DIST_DIR}"
echo "GIT commit hash: ${BUILD_SOURCEVERSION}"
echo "DOCKER_IMAGE: ${DOCKER_IMAGE}"

# -- mix in build info into package meta for `az extension show -n arcdata` --
if [[ "${DOCKER_IMAGE}" ]]; then
  DOCKER_IMAGE_TOKENS=($(echo ${DOCKER_IMAGE} | tr "_" "\n"))
  IMAGE_TAG=${DOCKER_IMAGE_TOKENS[0]}_${DOCKER_IMAGE_TOKENS[1]}
  COMMIT_HASH=${DOCKER_IMAGE_TOKENS[-1]}
  BRANCH=${DOCKER_IMAGE/${IMAGE_TAG}_/}
  PROPS="{\n    \"imageTag\": \"${IMAGE_TAG}\",\n\
    \"branch\": \"${BRANCH/_${COMMIT_HASH}/}\",\n\
    \"commit\": \"${COMMIT_HASH}\","
    sed -i "s/{/${PROPS}/g" ${REPO_ROOT_DIR}/arcdata/azext_arcdata/azext_metadata.json
fi

# -- script being invoked outside of a make target, thus template has been generated yet.
if [ ! -f ${REPO_ROOT_DIR}/arcdata/azext_arcdata/kubernetes_sdk/dc/templates/bootstrap/role-bootstrapper.yaml.tmpl ]; then
  ${REPO_ROOT_DIR}/scripts/generate-role-template.sh
fi

# pip install --index-url https://<username>:<pat>@<package_index_url> <package_name>
INDEX_URL=https://build:${PAT_TOKEN}@msdata.pkgs.visualstudio.com/Tina/_packaging/Tina_PublicPackages/pypi/simple

if ! command -v python &> /dev/null
then
  echo "Python is not defined, setting py=python3"
  py=python3
else
  echo "Python is defined, setting py=python"
  py=python
fi

echo ${py}
${py} --version
                     
pip install --index-url ${INDEX_URL} -U pip setuptools==70.0.0 wheel==0.30.0
pip list

# -- package --
mkdir -p ${DIST_DIR}

# -- Build wheel and pack assets --
setup_file=$(find arcdata -name 'setup.py')
pushd `dirname $setup_file`
cp ${REPO_ROOT_DIR}/THIRDPARTYNOTICES.txt ./azext_arcdata
cp ${REPO_ROOT_DIR}/LICENSE ./azext_arcdata
${py} setup.py bdist_wheel -d ${DIST_DIR}
popd
