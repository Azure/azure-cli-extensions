#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

#!/usr/bin/env bash

# Description:
#
# Lints the azure-cli extension arcdata using `azdev`
#
# Invoked under the build CI pipeline in AzureDevOps or gci Make. This script
# is typically executed from a parent instruction.
#
# Usage:
#
# $ lint.sh

set -exv

# -- position to repository base root location --
: "${REPO_ROOT_DIR:=`cd $(dirname $0); cd ../; pwd`}"
DIST_DIR=${REPO_ROOT_DIR}/output/packages
mkdir -p ${DIST_DIR}

INDEX_URL=https://build:${PAT_TOKEN}@msdata.pkgs.visualstudio.com/Tina/_packaging/Tina_PublicPackages/pypi/simple

# -- prepare and activate virtualenv --
python -m venv ${DIST_DIR}/env
. ${DIST_DIR}/env/bin/activate
pip install azdev black --index-url ${INDEX_URL}
which pip
which python
pip install azdev --index-url ${INDEX_URL}
python -m pip install regex --index-url ${INDEX_URL}

# -- assert code formatting/styling --
black ${REPO_ROOT_DIR}/arcdata/azext_arcdata || exit 1

# -- install arcdata whl --
${REPO_ROOT_DIR}/scripts/package.sh
export AZURE_EXTENSION_DIR=${DIST_DIR}/.azure/cliextensions
arcdata_ext=(`ls ${DIST_DIR}/arcdata*.whl`)
az extension add --source ${arcdata_ext[*]} -y --debug
az arcdata --help

# -- assert ext linting --
git clone --single-branch -b dev https://github.com/Azure/azure-cli.git ${DIST_DIR}/azure-cli
git clone --single-branch -b main https://github.com/Azure/azure-cli-extensions.git ${DIST_DIR}/azure-cli-extensions
azdev setup -c ${DIST_DIR}/azure-cli -r ${DIST_DIR}/azure-cli-extensions

# -- lint like in azure-cli-extension github repo --
# We are purposely omitting the following since we opt-out in the `azure-cli-extensions/linter_exclusions.yml` 
# to be caught there during PR:
# - option_length_too_long
# - parameter_should_not_end_in_resource_group
# - require_wait_command_if_no_wait
azdev linter --include-whl-extensions arcdata --rules disallowed_html_tag_from_paramete faulty_help_example_parameters_rule faulty_help_example_rule faulty_help_type_rule unrecognized_help_entry_rule unrecognized_help_parameter_rule expired_command_group missing_group_help expired_command missing_command_help no_ids_for_list_commands bad_short_option expired_option expired_parameter missing_parameter_help no_parameter_defaults_for_update_commands no_positional_parameters --debug || exit 1

# -- cleanup --
az extension remove --name arcdata
unset AZURE_EXTENSION_DIR
deactivate

#TODO - turn on
# Run command argument signatures checks
# flake8 ${REPO_ROOT_DIR}/arcdata/azext_arcdata || exit 1