# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import sys
import re
import logging
import pathlib

import az_aks_tool.filter as custom_filter
logger = logging.getLogger(__name__)


def create_directory(dir_path):
    if dir_path:
        if not os.path.isdir(dir_path):
            print("Directory '{}' not exist, creating...".format(dir_path))
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    else:
        print("Invalid dir path: '{}'".format(dir_path))


def check_file_existence(file_path):
    if file_path is not None and os.path.isfile(file_path):
        return True
    return False


def get_test_matrix(matrix_file_path):
    test_matrix = {}
    if check_file_existence(matrix_file_path):
        json_file = open(matrix_file_path, 'r')
        test_matrix = json.load(json_file)
        json_file.close()
    else:
        logger.warning("Matrix file '{}' not exists!".format(matrix_file_path))
    return test_matrix


def get_filted_test_cases(test_cases, exclude_test_cases):
    filtered_test_cases = [
        x for x in test_cases if x not in exclude_test_cases]
    logger.info("Find {} cases, exclude {} cases, finally get {} cases!".format(
        len(test_cases), len(exclude_test_cases), len(filtered_test_cases)))
    return filtered_test_cases


def add_qualified_prefix(test_cases, prefix):
    decorated_test_cases = ["{}.{}".format(prefix, x) for x in test_cases]
    return decorated_test_cases


def get_fully_qualified_test_cases(test_index, matrix_file_path, mod_name, extra_coverage=None, extra_filter=None):
    qualified_test_cases = []
    matrix = get_test_matrix(matrix_file_path)
    test_cases = custom_filter.get_test_cases(
        test_index, matrix, extra_coverage)
    exclude_test_cases = custom_filter.get_exclude_test_cases(test_index,
                                                              matrix, extra_filter)
    filtered_test_cases = get_filted_test_cases(
        test_cases, exclude_test_cases)
    # add prefix
    qualified_test_cases = add_qualified_prefix(
        filtered_test_cases, mod_name)
    return qualified_test_cases


def heading(txt):
    """ Create standard heading to stderr """
    line_len = len(txt) + 4
    print('\n' + '=' * line_len, file=sys.stderr)
    print('| {} |'.format(txt), file=sys.stderr)
    print('=' * line_len + '\n', file=sys.stderr)


def extract_module_name(path):
    _CORE_NAME_REGEX = re.compile(
        r'azure-cli-(?P<name>[^/\\]+)[/\\]azure[/\\]cli')
    _MOD_NAME_REGEX = re.compile(
        r'azure-cli[/\\]azure[/\\]cli[/\\]command_modules[/\\](?P<name>[^/\\]+)')
    _EXT_NAME_REGEX = re.compile(r'.*(?P<name>azext_[^/\\]+).*')

    for expression in [_MOD_NAME_REGEX, _CORE_NAME_REGEX, _EXT_NAME_REGEX]:
        match = re.search(expression, path)
        if not match:
            continue
        return match.groupdict().get('name')
    raise Exception(
        'unexpected error: unable to extract name from path: {}'.format(path))
