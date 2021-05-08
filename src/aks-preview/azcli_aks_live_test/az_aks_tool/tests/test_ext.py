# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

import azcli_aks_live_test.az_aks_tool.utils as utils
import azcli_aks_live_test.az_aks_tool.ext as ext

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)

class ExtTestCase(unittest.TestCase):

    def test_ext_get_ext_test_index(self):
        pass

    def test_ext_get_ext_test_cases(self):
        ext_test_index = {
            "test_validators": {
                "TestValidateIPRanges": ["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces", "test_disable_authorized_ip_ranges", "test_local_ip_address", "test_invalid_ip", "test_IPv6"],
                "TestClusterAutoscalerParamsValidators": ["test_empty_key_empty_value", "test_non_empty_key_empty_value", "test_two_empty_keys_empty_value", "test_one_empty_key_in_pair_one_non_empty", "test_invalid_key", "test_valid_parameters"],
                "TestSubnetId": ["test_invalid_subnet_id", "test_valid_vnet_subnet_id", "test_none_vnet_subnet_id", "test_empty_vnet_subnet_id"]
            }
        }
        ext_matrix = utils.get_test_matrix(
            os.path.join(THIS_DIR, "testdata.json"))
        base = ext_test_index["test_validators"]
        s1 = sorted(ext.get_ext_test_cases(ext_test_index, ext_matrix, []))
        t1 = sorted((base["TestValidateIPRanges"] +
                     base["TestClusterAutoscalerParamsValidators"]))
        s2 = sorted(ext.get_ext_test_cases(ext_test_index, ext_matrix, [
            "test_valid_vnet_subnet_id", "abc"]))
        t2 = sorted((base["TestValidateIPRanges"] + base["TestClusterAutoscalerParamsValidators"] +
                     ["test_valid_vnet_subnet_id"]))
        s3 = sorted(ext.get_ext_test_cases(ext_test_index, ext_matrix, [
            "test_validators.TestSubnetId"]))
        t3 = sorted((base["TestValidateIPRanges"] +
                     base["TestClusterAutoscalerParamsValidators"] + base["TestSubnetId"]))
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)
        self.assertEqual(s3, t3)

    def test_ext_get_ext_exclude_test_cases(self):
        ext_test_index = {
            "test_validators": {
                "TestValidateIPRanges": ["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces", "test_disable_authorized_ip_ranges", "test_local_ip_address", "test_invalid_ip", "test_IPv6"],
                "TestClusterAutoscalerParamsValidators": ["test_empty_key_empty_value", "test_non_empty_key_empty_value", "test_two_empty_keys_empty_value", "test_one_empty_key_in_pair_one_non_empty", "test_invalid_key", "test_valid_parameters"],
                "TestSubnetId": ["test_invalid_subnet_id", "test_valid_vnet_subnet_id", "test_none_vnet_subnet_id", "test_empty_vnet_subnet_id"]
            }
        }
        ext_matrix = utils.get_test_matrix(
            os.path.join(THIS_DIR, "testdata.json"))
        base = ext_test_index["test_validators"]
        s1 = sorted(ext.get_ext_exclude_test_cases(
            ext_test_index, ext_matrix, []))
        t1 = sorted(["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces",
                    "test_disable_authorized_ip_ranges"] + base["TestClusterAutoscalerParamsValidators"])
        s2 = sorted(ext.get_ext_exclude_test_cases(ext_test_index,
                    ext_matrix, ["iprange"]))
        t2 = sorted(["test_simultaneous_allow_and_disallow_with_spaces",
                    "test_simultaneous_enable_and_disable_with_spaces", "test_disable_authorized_ip_ranges"])
        s3 = sorted(ext.get_ext_exclude_test_cases(ext_test_index,
                    ext_matrix, ["default", "test_invalid_subnet_id"]))
        t3 = sorted(["test_simultaneous_allow_and_disallow_with_spaces", "test_simultaneous_enable_and_disable_with_spaces",
                    "test_disable_authorized_ip_ranges"] + base["TestClusterAutoscalerParamsValidators"] + ["test_invalid_subnet_id"])
        s4 = sorted(ext.get_ext_exclude_test_cases(ext_test_index, ext_matrix, [
            "test_valid_vnet_subnet_id", "abc", "test_validators.TestClusterAutoscalerParamsValidators"]))
        t4 = sorted(
            (base["TestClusterAutoscalerParamsValidators"] + ["test_valid_vnet_subnet_id"]))
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)
        self.assertEqual(s3, t3)
        self.assertEqual(s4, t4)
