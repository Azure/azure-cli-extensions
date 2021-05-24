# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

import az_aks_tool.utils as utils

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)


class UtilsTestCase(unittest.TestCase):

    def test_check_file_existence(self):
        s1 = utils.check_file_existence(None)
        s2 = utils.check_file_existence(THIS_DIR)
        s3 = utils.check_file_existence(THIS_FILE)
        s4 = utils.check_file_existence(
            os.path.join(THIS_DIR, "testdata.json"))
        self.assertEqual(s1, False)
        self.assertEqual(s2, False)
        self.assertEqual(s3, True)
        self.assertEqual(s4, True)

    def test_get_test_matrix(self):
        s = utils.get_test_matrix(os.path.join(THIS_DIR, "testdata.json"))
        self.assertEqual(len(s), 2)     # number of keys

    def test_get_filted_test_cases(self):
        test_cases = ["a", "b", "c", "d"]
        s1 = utils.get_filted_test_cases(test_cases, [])
        t1 = ["a", "b", "c", "d"]
        s2 = utils.get_filted_test_cases(test_cases, ["a", "x"])
        t2 = ["b", "c", "d"]
        self.assertEqual(s1, t1)
        self.assertEqual(s2, t2)
    
    def test_add_qualified_prefix(self):
        test_cases = ["a", "b", "c"]
        s = utils.add_qualified_prefix(test_cases, "p")
        self.assertEqual(s, ["p.a", "p.b", "p.c"])

    def test_get_fully_qualified_test_cases(self):
        pass

    def test_heading(self):
        pass

    def test_extract_module_name(self):
        pass
