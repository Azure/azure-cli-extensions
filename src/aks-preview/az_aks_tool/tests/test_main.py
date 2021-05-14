# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import unittest

import az_aks_tool.main as main

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)


class MainTestCase(unittest.TestCase):

    def test_init_argparse(self):
        args = main.init_argparse(["-p", "./"])
        self.assertEqual(args.report_path, "./")
