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


def get_ext_mod_data(mod_name=const.AKS_PREVIEW_MOD_NAME, profile="latest"):
    profile_split = profile.split('-')
    profile_namespace = '_'.join([profile_split[-1]] + profile_split[:-1])

    # key value pairs of all modules(in azcli & extention) and its absolute path, used later to find test indexes
    path_table = index.get_path_table()
    extensions = path_table["ext"]
    inverse_name_table = index.get_name_index(invert=True)

    # construct 'import_name' & mod_data', used later to find test indexes
    aks_preview_mod_path = extensions[mod_name]
    glob_pattern = os.path.normcase(
        os.path.join("{}*".format(const.EXTENSION_PREFIX)))
    file_path = glob.glob(os.path.join(aks_preview_mod_path, glob_pattern))[0]
    import_name = os.path.basename(file_path)
    mod_data = {
        "alt_name": inverse_name_table[mod_name],
        "filepath": os.path.join(file_path, "tests", profile_namespace),
        "base_path": "{}.tests.{}".format(import_name, profile_namespace),
        "files": {}
    }

    ext_test = index.discover_module_tests(import_name, mod_data)
    return ext_test


def get_ext_test_index(module_data=None, mod_name=const.AKS_PREVIEW_MOD_NAME, profile="latest"):
    if mod_name in module_data:
        mod_data = module_data[mod_name]
    else:
        mod_data = get_ext_mod_data(mod_name=mod_name, profile=profile)
    return mod_data["files"]
