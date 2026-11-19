# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import patch

from azure.cli.testsdk import ScenarioTest
from azext_durabletask import DurabletaskCommandsLoader


class DurabletaskScenario(ScenarioTest):
    def test_durabletask_command_help(self):
        loader = DurabletaskCommandsLoader(cli_ctx=self.cli_ctx)
        commands = loader.load_command_table(None)
        self.assertIn('durabletask scheduler attach', commands)
        self.assertIn('durabletask taskqueue create', commands)
        with patch('requests.sessions.Session.request', side_effect=AssertionError('Unexpected network request')):
            for command in sorted(commands):
                with self.subTest(command=command):
                    try:
                        self.cmd(f'az {command} --help')
                    except SystemExit as ex:
                        self.assertEqual(ex.code, 0)
