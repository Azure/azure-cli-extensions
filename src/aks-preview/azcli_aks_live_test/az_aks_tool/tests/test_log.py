# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import unittest

import azcli_aks_live_test.az_aks_tool.log as log

THIS_FILE = os.path.abspath(__file__)
THIS_DIR = os.path.dirname(THIS_FILE)
PARENT_DIR = os.path.dirname(THIS_DIR)


class LogTestCase(unittest.TestCase):

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
