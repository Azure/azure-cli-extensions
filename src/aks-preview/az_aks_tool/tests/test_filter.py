# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

import az_aks_tool.utils as utils
import az_aks_tool.filter as custom_filter

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)


class FilterTestCase(unittest.TestCase):

    def test_extract_file_class_pairs(self):
        test_cases = ["abc", "a.b", "a.b.c"]
        s = custom_filter.extract_file_class_pairs(test_cases)
        self.assertEqual(s, [("a", "b")])

    def test_filter_valid_file_class_pairs(self):
        pairs = [("a", "b"), ("c", "d"), ("e", "f")]
        test_index = {
            "a": {
                "b": ["aaa", "bbb"]
            },
            "x": {
                "y": ["xxx", "yyy"]
            }
        }
        s = custom_filter.filter_valid_file_class_pairs(pairs, test_index)
        self.assertEqual(s, [("a", "b")])

    def test_get_all_values_from_nested_dict(self):
        d = {
            "a": {
                "b": ["aaa", "bbb"]
            },
            "x": ["xxx"]
        }
        s = list(custom_filter.get_all_values_from_nested_dict(d))
        self.assertEqual(s, [["aaa", "bbb"], ["xxx"]])

    def test_flatten_nested_list(self):
        lis = [["aaa", "bbb"], ["xxx"]]
        s = list(custom_filter.flatten_nested_list(lis))
        self.assertEqual(s, ["aaa", "bbb", "xxx"])

    def test_filter_valid_test_cases(self):
        test_cases = ["abc", "a.b", "a.b.c", "aaa", "yyy"]
        test_index = {
            "a": {
                "b": ["aaa", "bbb"]
            },
            "x": {
                "y": ["xxx", "yyy"]
            }
        }
        s = custom_filter.filter_valid_test_cases(test_cases, test_index)
        self.assertEqual(s, ["aaa", "yyy"])

    def test_get_test_cases(self):
        test_index = {
            "test_validators": {
                "TestValidateIPRanges": ["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces", "test_disable_authorized_ip_ranges", "test_local_ip_address", "test_invalid_ip", "test_IPv6"],
                "TestClusterAutoscalerParamsValidators": ["test_empty_key_empty_value", "test_non_empty_key_empty_value", "test_two_empty_keys_empty_value", "test_one_empty_key_in_pair_one_non_empty", "test_invalid_key", "test_valid_parameters"],
                "TestSubnetId": ["test_invalid_subnet_id", "test_valid_vnet_subnet_id", "test_none_vnet_subnet_id", "test_empty_vnet_subnet_id"]
            }
        }
        matrix = utils.get_test_matrix(
            os.path.join(THIS_DIR, "testdata.json"))
        base = test_index["test_validators"]
        s1 = sorted(custom_filter.get_test_cases(test_index, matrix, []))
        t1 = sorted((base["TestValidateIPRanges"] +
                     base["TestClusterAutoscalerParamsValidators"]))
        s2 = sorted(custom_filter.get_test_cases(test_index, matrix, [
            "test_valid_vnet_subnet_id", "abc"]))
        t2 = sorted((base["TestValidateIPRanges"] + base["TestClusterAutoscalerParamsValidators"] +
                     ["test_valid_vnet_subnet_id"]))
        s3 = sorted(custom_filter.get_test_cases(test_index, matrix, [
            "test_validators.TestSubnetId"]))
        t3 = sorted((base["TestValidateIPRanges"] +
                     base["TestClusterAutoscalerParamsValidators"] + base["TestSubnetId"]))
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)
        self.assertEqual(s3, t3)

    def test_get_exclude_test_cases(self):
        test_index = {
            "test_validators": {
                "TestValidateIPRanges": ["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces", "test_disable_authorized_ip_ranges", "test_local_ip_address", "test_invalid_ip", "test_IPv6"],
                "TestClusterAutoscalerParamsValidators": ["test_empty_key_empty_value", "test_non_empty_key_empty_value", "test_two_empty_keys_empty_value", "test_one_empty_key_in_pair_one_non_empty", "test_invalid_key", "test_valid_parameters"],
                "TestSubnetId": ["test_invalid_subnet_id", "test_valid_vnet_subnet_id", "test_none_vnet_subnet_id", "test_empty_vnet_subnet_id"]
            }
        }
        matrix = utils.get_test_matrix(
            os.path.join(THIS_DIR, "testdata.json"))
        base = test_index["test_validators"]
        s1 = sorted(custom_filter.get_exclude_test_cases(
            test_index, matrix, []))
        t1 = sorted(["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces",
                    "test_disable_authorized_ip_ranges"] + base["TestClusterAutoscalerParamsValidators"])
        s2 = sorted(custom_filter.get_exclude_test_cases(test_index,
                    matrix, ["iprange"]))
        t2 = sorted(["test_simultaneous_allow_and_disallow_with_spaces",
                    "test_simultaneous_enable_and_disable_with_spaces", "test_disable_authorized_ip_ranges"])
        s3 = sorted(custom_filter.get_exclude_test_cases(test_index,
                    matrix, ["default", "test_invalid_subnet_id"]))
        t3 = sorted(["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces",
                    "test_disable_authorized_ip_ranges"] + base["TestClusterAutoscalerParamsValidators"] + ["test_invalid_subnet_id"])
        s4 = sorted(custom_filter.get_exclude_test_cases(test_index, matrix, [
            "test_valid_vnet_subnet_id", "abc", "test_validators.TestClusterAutoscalerParamsValidators"]))
        t4 = sorted(
            (base["TestClusterAutoscalerParamsValidators"] + ["test_valid_vnet_subnet_id"]))
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)
        self.assertEqual(s3, t3)
        self.assertEqual(s4, t4)
