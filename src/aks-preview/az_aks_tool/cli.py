# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import glob
import os
import logging

import az_aks_tool.const as const
import az_aks_tool.index as index
logger = logging.getLogger(__name__)


def get_cli_mod_data(mod_name=const.ACS_MOD_NAME, profile="latest"):
    profile_split = profile.split('-')
    profile_namespace = '_'.join([profile_split[-1]] + profile_split[:-1])

    # key value pairs of all modules(in azcli & extention) and its absolute path, used later to find test indexes
    path_table = index.get_path_table()
    command_modules = path_table["mod"]
    inverse_name_table = index.get_name_index(invert=True)

    # construct 'import_name' & mod_data', used later to find test indexes
    acs_mod_path = command_modules[mod_name]
    mod_data = {
        "alt_name": "{}{}".format(const.COMMAND_MODULE_PREFIX, mod_name),
        "filepath": os.path.join(acs_mod_path, "tests", profile_namespace),
        "base_path": "azure.cli.command_modules.{}.tests.{}".format(mod_name, profile_namespace),
        "files": {}
    }

    cli_test = index.discover_module_tests(mod_name, mod_data)
    return cli_test


def get_cli_test_index(module_data=None, mod_name=const.ACS_MOD_NAME, profile="latest"):
    if mod_name in module_data:
        mod_data = module_data[mod_name]
    else:
        mod_data = get_cli_mod_data(mod_name=mod_name, profile=profile)    
    return mod_data["files"]
