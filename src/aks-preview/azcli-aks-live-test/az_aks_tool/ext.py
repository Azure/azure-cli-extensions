# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import glob
import os
from azdev.operations.testtool import _discover_module_tests
from azdev.utilities import EXTENSION_PREFIX, get_path_table, get_name_index

import utils


def get_ext_test_index(mod_name):
    # path table & name index
    path_table = get_path_table()
    command_modules = path_table['mod']
    extensions = path_table["ext"]
    inverse_name_table = get_name_index(invert=True)

    # import_name & mod_data
    aks_preview_mod_path = extensions[mod_name]
    glob_pattern = os.path.normcase(
        os.path.join("{}*".format(EXTENSION_PREFIX)))
    file_path = glob.glob(os.path.join(aks_preview_mod_path, glob_pattern))[0]
    import_name = os.path.basename(file_path)
    mod_data = {
        "alt_name": inverse_name_table[mod_name],
        "filepath": os.path.join(file_path, "tests", "latest"),
        "base_path": "{}.tests.{}".format(import_name, "latest"),
        "files": {}
    }

    # azdev hook
    ext_test = _discover_module_tests(import_name, mod_data)
    ext_test_index = ext_test["files"]
    return ext_test_index


def get_ext_test_cases(ext_test_index, ext_matrix, ext_extra_coverage):
    ext_test_cases = []
    ext_coverage = ext_matrix["coverage"]
    for fileName, className in ext_coverage.items():
        for c in className:
            ext_test_cases.extend(ext_test_index[fileName][c])
    # extra coverage
    if ext_extra_coverage:
        # method 1: fileName.className
        file_class_pairs = utils.extract_file_class_pairs(ext_extra_coverage)
        valid_file_class_pairs = utils.filter_valid_file_class_pairs(
            file_class_pairs, ext_test_index)
        for valid_pair in valid_file_class_pairs:
            ext_test_cases.extend(
                ext_test_index[valid_pair[0]][valid_pair[1]])
        # method 2: test cases
        ext_test_cases.extend(utils.filter_valid_test_cases(
            ext_extra_coverage, ext_test_index))
    return list(set(ext_test_cases))


def get_ext_exclude_test_cases(ext_test_index, ext_matrix, ext_filter):
    ext_exclude_test_cases = []
    ext_exclude = ext_matrix["exclude"]
    if not ext_filter:
        for k, v in ext_exclude.items():
            ext_exclude_test_cases.extend(v)
    else:
        # method 1: matrix exclude key
        for k, v in ext_exclude.items():
            if k in ext_filter or "default" in ext_filter:
                ext_exclude_test_cases.extend(v)
        # method 2: fileName.className
        file_class_pairs = utils.extract_file_class_pairs(ext_filter)
        valid_file_class_pairs = utils.filter_valid_file_class_pairs(
            file_class_pairs, ext_test_index)
        for valid_pair in valid_file_class_pairs:
            ext_exclude_test_cases.extend(
                ext_test_index[valid_pair[0]][valid_pair[1]])
        # method 3: test cases
        ext_exclude_test_cases.extend(
            utils.filter_valid_test_cases(ext_filter, ext_test_index))
    return list(set(ext_exclude_test_cases))


def get_ext_filted_test_cases(ext_test_cases, ext_exclude_test_cases):
    ext_filtered_test_cases = [
        x for x in ext_test_cases if x not in ext_exclude_test_cases]
    return ext_filtered_test_cases
