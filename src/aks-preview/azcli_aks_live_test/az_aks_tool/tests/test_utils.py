# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

import azcli_aks_live_test.az_aks_tool.utils as utils

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)


class UtilsTestCase(unittest.TestCase):

    def test_utils_check_file_existence(self):
        s1 = utils.check_file_existence(None)
        s2 = utils.check_file_existence(THIS_DIR)
        s3 = utils.check_file_existence(THIS_FILE)
        s4 = utils.check_file_existence(
            os.path.join(THIS_DIR, "testdata.json"))
        self.assertEqual(s1, False)
        self.assertEqual(s2, False)
        self.assertEqual(s3, True)
        self.assertEqual(s4, True)

    def test_utils_get_test_matrix(self):
        s = utils.get_test_matrix(os.path.join(THIS_DIR, "testdata.json"))
        self.assertEqual(len(s), 2)     # number of keys

    def test_utils_decorate_qualified_prefix(self):
        test_cases = ["a", "b", "c"]
        s = utils.decorate_qualified_prefix(test_cases, "p")
        self.assertEqual(s, ["p.a", "p.b", "p.c"])

    def test_utils_extract_file_class_pairs(self):
        test_cases = ["abc", "a.b", "a.b.c"]
        s = utils.extract_file_class_pairs(test_cases)
        self.assertEqual(s, [("a", "b")])

    def test_utils_filter_valid_file_class_pairs(self):
        pairs = [("a", "b"), ("c", "d"), ("e", "f")]
        test_index = {
            "a": {
                "b": ["aaa", "bbb"]
            },
            "x": {
                "y": ["xxx", "yyy"]
            }
        }
        s = utils.filter_valid_file_class_pairs(pairs, test_index)
        self.assertEqual(s, [("a", "b")])

    def test_utils_get_all_values_from_nested_dict(self):
        d = {
            "a": {
                "b": ["aaa", "bbb"]
            },
            "x": ["xxx"]
        }
        s = list(utils.get_all_values_from_nested_dict(d))
        self.assertEqual(s, [["aaa", "bbb"], ["xxx"]])

    def test_utils_flatten_nested_list(self):
        lis = [["aaa", "bbb"], ["xxx"]]
        s = list(utils.flatten_nested_list(lis))
        self.assertEqual(s, ["aaa", "bbb", "xxx"])

    def test_utils_filter_valid_test_cases(self):
        test_cases = ["abc", "a.b", "a.b.c", "aaa", "yyy"]
        test_index = {
            "a": {
                "b": ["aaa", "bbb"]
            },
            "x": {
                "y": ["xxx", "yyy"]
            }
        }
        s = utils.filter_valid_test_cases(test_cases, test_index)
        self.assertEqual(s, ["aaa", "yyy"])

    def test_get_filted_test_cases(self):
        test_cases = ["a", "b", "c", "d"]
        s1 = utils.get_filted_test_cases(test_cases, [])
        t1 = ["a", "b", "c", "d"]
        s2 = utils.get_filted_test_cases(test_cases, ["a", "x"])
        t2 = ["b", "c", "d"]
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)
