# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import Iterable
import json
import os


def check_file_existence(file_path):
    if file_path is not None and os.path.isfile(file_path):
        return True
    return False


def get_test_matrix(matrix_file_path):
    json_file = open(matrix_file_path, 'r')
    test_matrix = json.load(json_file)
    json_file.close()
    return test_matrix


def decorate_qualified_prefix(test_cases, prefix):
    decorated_test_cases = ["{}.{}".format(prefix, x) for x in test_cases]
    return decorated_test_cases


def extract_file_class_pairs(tag_list):
    pairs = []
    for k in tag_list:
        tags = k.split(".")
        if len(tags) == 2:
            pairs.append((tags[0], tags[1]))
    return pairs


def filter_valid_file_class_pairs(pairs, test_index):
    valid_pairs = []
    for pair in pairs:
        if pair[0] in test_index and pair[1] in test_index[pair[0]]:
            valid_pairs.append(pair)
            print("Find valid file & class pair: '{}'".format(pair))
        else:
            print("Invalid file & class pair: '{}'".format(pair))
    return valid_pairs


def get_all_values_from_nested_dict(d):
    for v in d.values():
        if isinstance(v, dict):
            yield from get_all_values_from_nested_dict(v)
        else:
            yield v


def flatten_nested_list(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in flatten_nested_list(item):
                yield x
        else:
            yield item


def filter_valid_test_cases(test_cases, test_index):
    valid_test_cases = []
    nested_test_cases = list(get_all_values_from_nested_dict(test_index))
    falttened_test_cases = list(flatten_nested_list(nested_test_cases))
    for test_case in test_cases:
        if test_case in falttened_test_cases:
            valid_test_cases.append(test_case)
            print("Find valid test case: '{}'".format(test_case))
        else:
            print("Invalid test case: '{}'".format(test_case))
    return valid_test_cases
