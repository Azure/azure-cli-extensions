# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
from collections import Iterable
logger = logging.getLogger(__name__)


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
            logger.debug("Valid file & class pair: '{}'".format(pair))
        else:
            logger.debug("Invalid file & class pair: '{}'".format(pair))
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
            logger.debug("Valid test case: '{}'".format(test_case))
        else:
            logger.debug("Invalid test case: '{}'".format(test_case))
    return valid_test_cases


def get_test_cases(test_index, matrix, extra_coverage=None):
    test_cases = []
    coverage = matrix.get("coverage", {})
    # default coverage
    for fileName, className in coverage.items():
        for c in className:
            test_cases.extend(test_index[fileName][c])
    # custom extra coverage
    if extra_coverage:
        # method 1: fileName.className
        file_class_pairs = extract_file_class_pairs(extra_coverage)
        valid_file_class_pairs = filter_valid_file_class_pairs(
            file_class_pairs, test_index)
        for valid_pair in valid_file_class_pairs:
            test_cases.extend(
                test_index[valid_pair[0]][valid_pair[1]])
        # method 2: test cases
        test_cases.extend(filter_valid_test_cases(
            extra_coverage, test_index))
    return list(set(test_cases))


def get_exclude_test_cases(test_index, matrix, extra_filter=None):
    exclude_test_cases = []
    exclude = matrix.get("exclude", {})
    # default exclude
    if not extra_filter or "default" in extra_filter:
        matrix_test_cases = []
        matrix_file_class_pairs = []
        for k, v in exclude.items():
            # method 1: reason -> test cases
            matrix_test_cases.extend(v)
            # method 2: fileName -> className
            matrix_file_class_pairs.extend((k, x) for x in v)
        # method 1: reason -> test cases
        exclude_test_cases.extend(
            filter_valid_test_cases(matrix_test_cases, test_index))
        # method 2: fileName -> className
        valid_matrix_file_class_pairs = filter_valid_file_class_pairs(
            matrix_file_class_pairs, test_index)
        for valid_matrix_pair in valid_matrix_file_class_pairs:
            exclude_test_cases.extend(
                test_index[valid_matrix_pair[0]][valid_matrix_pair[1]])
    # custom extra_filter
    if extra_filter:
        # method 1: matrix exclude key
        for k, v in exclude.items():
            if k in extra_filter:
                exclude_test_cases.extend(v)
        # method 2: fileName.className
        file_class_pairs = extract_file_class_pairs(extra_filter)
        valid_file_class_pairs = filter_valid_file_class_pairs(
            file_class_pairs, test_index)
        for valid_pair in valid_file_class_pairs:
            exclude_test_cases.extend(
                test_index[valid_pair[0]][valid_pair[1]])
        # method 3: test cases
        exclude_test_cases.extend(
            filter_valid_test_cases(extra_filter, test_index))
    return list(set(exclude_test_cases))
