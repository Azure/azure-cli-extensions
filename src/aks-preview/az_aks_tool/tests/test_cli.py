# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

import az_aks_tool.utils as utils
import az_aks_tool.cli as cli

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)

class CliTestCase(unittest.TestCase):

    def test_get_cli_mod_data(self):
        pass

    def test_get_cli_test_index(self):
        pass
