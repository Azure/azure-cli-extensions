import os
import sys
import unittest


class UtilsTestCase(unittest.TestCase):

    def test_utils_check_file_existence(self):
        s1 = check_file_existence(None)
        s2 = check_file_existence(THIS_DIR)
        s3 = check_file_existence(THIS_FILE)
        s4 = check_file_existence(os.path.join(THIS_DIR, "testdata.json"))
        self.assertEqual(s1, False)
        self.assertEqual(s2, False)
        self.assertEqual(s3, True)
        self.assertEqual(s4, True)

    def test_utils_get_test_matrix(self):
        s = get_test_matrix(os.path.join(THIS_DIR, "testdata.json"))
        self.assertEqual(len(s), 2)     # number of keys

    def test_utils_decorate_qualified_prefix(self):
        test_cases = ["a", "b", "c"]
        s = decorate_qualified_prefix(test_cases, "p")
        self.assertEqual(s, ["p.a", "p.b", "p.c"])

    def test_utils_extract_file_class_pairs(self):
        test_cases = ["abc", "a.b", "a.b.c"]
        s = extract_file_class_pairs(test_cases)
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
        s = filter_valid_file_class_pairs(pairs, test_index)
        self.assertEqual(s, [("a", "b")])

    def test_utils_get_all_values_from_nested_dict(self):
        d = {
            "a": {
                "b": ["aaa", "bbb"]
            },
            "x": ["xxx"]
        }
        s = list(get_all_values_from_nested_dict(d))
        self.assertEqual(s, [["aaa", "bbb"], ["xxx"]])

    def test_utils_flatten_nested_list(self):
        lis = [["aaa", "bbb"], ["xxx"]]
        s = list(flatten_nested_list(lis))
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
        s = filter_valid_test_cases(test_cases, test_index)
        self.assertEqual(s, ["aaa", "yyy"])

    def test_get_filted_test_cases(self):
        test_cases = ["a", "b", "c", "d"]
        s1 = get_filted_test_cases(test_cases, [])
        t1 = ["a", "b", "c", "d"]
        s2 = get_filted_test_cases(test_cases, ["a", "x"])
        t2 = ["b", "c", "d"]
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)


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
        ext_matrix = get_test_matrix(os.path.join(THIS_DIR, "testdata.json"))
        base = ext_test_index["test_validators"]
        s1 = get_ext_test_cases(ext_test_index, ext_matrix, []).sort()
        t1 = (base["TestValidateIPRanges"] +
              base["TestClusterAutoscalerParamsValidators"]).sort()
        s2 = get_ext_test_cases(ext_test_index, ext_matrix, [
                                "test_valid_vnet_subnet_id", "abc"]).sort()
        t2 = (base["TestValidateIPRanges"] + base["TestClusterAutoscalerParamsValidators"] +
              ["test_valid_vnet_subnet_id"]).sort()
        s3 = get_ext_test_cases(ext_test_index, ext_matrix, [
                                "test_validators.TestSubnetId"]).sort()
        t3 = (base["TestValidateIPRanges"] +
              base["TestClusterAutoscalerParamsValidators"] + base["TestSubnetId"]).sort()
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
        ext_matrix = get_test_matrix(os.path.join(THIS_DIR, "testdata.json"))
        base = ext_test_index["test_validators"]
        s1 = get_ext_exclude_test_cases(ext_test_index, ext_matrix, []).sort()
        t1 = ["test_local_ip_address", "test_invalid_ip", "test_IPv6"].sort()
        s2 = get_ext_exclude_test_cases(ext_test_index, ext_matrix, [
                                        "test_valid_vnet_subnet_id", "abc", "test_validators.TestClusterAutoscalerParamsValidators"]).sort()
        t2 = (["test_local_ip_address", "test_invalid_ip", "test_IPv6"] +
              base["TestClusterAutoscalerParamsValidators"] + ["test_valid_vnet_subnet_id"]).sort()
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)


if __name__ == '__main__':
    THIS_FILE = os.path.abspath(__file__)
    THIS_DIR = os.path.dirname(THIS_FILE)
    PARENT_DIR = os.path.dirname(THIS_DIR)
    sys.path.append(PARENT_DIR)
    from utils import *
    from ext import *
    unittest.main()
    sys.path.remove(PARENT_DIR)
