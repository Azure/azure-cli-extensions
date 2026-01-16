# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azext_networkcloud import NetworkcloudCommandsLoader
from azext_networkcloud.operations.storageappliance._run_read_command import (
    RunReadCommand,
)
from azext_networkcloud.tests.unit.test_run_command_options import (
    RunCommandOptionsTestClass,
)
from azure.cli.core.mock import DummyCli


class TestRunReadCommand(unittest.TestCase, RunCommandOptionsTestClass):
    def setUp(self):
        self._cli_ctx = DummyCli()
        self._loader = NetworkcloudCommandsLoader(cli_ctx=self._cli_ctx)
        self.cmd = RunReadCommand(loader=self._loader, cli_ctx=self._cli_ctx)
