# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import glob
import os
import logging
from azdev.operations.testtool import _discover_module_tests
from azdev.utilities import EXTENSION_PREFIX, get_path_table, get_name_index

import azcli_aks_live_test.az_aks_tool.utils as utils
logger = logging.getLogger(__name__)


def get_ext_test_index(mod_name):
    # key value pairs of all modules(in azcli & extention) and its absolute path, used later to find test indexes
    path_table = get_path_table()
    extensions = path_table["ext"]
    inverse_name_table = get_name_index(invert=True)

    # construct 'import_name' & mod_data', used later to find test indexes
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

    # use azdev internal func '_discover_module_tests' to find test index
    ext_test = _discover_module_tests(import_name, mod_data)
    ext_test_index = ext_test["files"]
    return ext_test_index


def get_ext_test_cases(ext_test_index, ext_matrix, ext_extra_coverage):
    ext_test_cases = []
    ext_coverage = ext_matrix["coverage"]
    # default coverage
    for fileName, className in ext_coverage.items():
        for c in className:
            ext_test_cases.extend(ext_test_index[fileName][c])
    # custom extra coverage
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
    # default exclude
    if not ext_filter or "default" in ext_filter:
        matrix_test_cases = []
        matrix_file_class_pairs = []
        for k, v in ext_exclude.items():
            # method 1: reason -> test cases
            matrix_test_cases.extend(v)
            # method 2: fileName -> className
            matrix_file_class_pairs.extend((k, x) for x in v)
        # method 1: reason -> test cases
        ext_exclude_test_cases.extend(
            utils.filter_valid_test_cases(matrix_test_cases, ext_test_index))
        # method 2: fileName -> className
        valid_matrix_file_class_pairs = utils.filter_valid_file_class_pairs(
            matrix_file_class_pairs, ext_test_index)
        for valid_matrix_pair in valid_matrix_file_class_pairs:
            ext_exclude_test_cases.extend(
                ext_test_index[valid_matrix_pair[0]][valid_matrix_pair[1]])
    # custom filter
    if ext_filter:
        # method 1: matrix exclude key
        for k, v in ext_exclude.items():
            if k in ext_filter:
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
