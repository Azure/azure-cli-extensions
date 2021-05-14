# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import unittest

import az_aks_tool.log as log

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)


class LogTestCase(unittest.TestCase):

    def test_parse_module_name(self):
        root_module_name = log.parse_module_name(levels=1)
        error_module_name = log.parse_module_name(levels=5)
        self.assertEqual(root_module_name, "az_aks_tool")
        self.assertEqual(error_module_name, None)

    def test_setup_logging(self):
        log.setup_logging("unittest", "unittest_log.log")
        logger = logging.getLogger("unittest.test_setup_logging")
        logger.debug("test setup logging")
        logger.info("test setup logging")
        logger.warning("test setup logging")
        f = open("unittest_log.log", "r")
        raw_logs = f.readlines()
        f.close()
        self.assertEqual(len(raw_logs), 3)
