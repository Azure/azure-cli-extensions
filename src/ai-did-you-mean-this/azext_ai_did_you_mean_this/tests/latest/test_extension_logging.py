# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import unittest

from knack.log import CLI_LOGGER_NAME

from azext_ai_did_you_mean_this._const import THOTH_LOG_PREFIX
from azext_ai_did_you_mean_this._logging import get_logger

LOGGER_NAME = __name__
logger = get_logger(LOGGER_NAME)

TEST_MSG = 'the quick brown fox jumps over the lazy dog'


class TestExtensionLogging(unittest.TestCase):
    def setUp(self):
        self.logger_name = f'{CLI_LOGGER_NAME}.{LOGGER_NAME}'

    def test_that_log_prefix_is_prepended(self):
        with self.assertLogs(self.logger_name, logging.DEBUG) as extension_logs:
            logger.debug(TEST_MSG)

            logs = '\n'.join(extension_logs.output)
            self.assertIn(THOTH_LOG_PREFIX, logs)
