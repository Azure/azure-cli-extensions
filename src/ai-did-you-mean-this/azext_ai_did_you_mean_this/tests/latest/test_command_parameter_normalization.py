# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from copy import deepcopy
from enum import Enum, auto

from azure.cli.core import MainCommandsLoader
from azure.cli.core.mock import DummyCli

from azext_ai_did_you_mean_this.tests.latest.data._command_normalization_scenario import \
    CommandNormalizationScenario
from azext_ai_did_you_mean_this.tests.latest.data._command_parameter_normalization_scenario import \
    CommandParameterNormalizationScenario
from azext_ai_did_you_mean_this.tests.latest.data.scenarios import \
    NORMALIZATION_TEST_SCENARIOS


class TestCommandParameterNormalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommandParameterNormalization, cls).setUpClass()

        from knack.events import EVENT_INVOKER_POST_CMD_TBL_CREATE
        from azure.cli.core.commands.events import EVENT_INVOKER_PRE_LOAD_ARGUMENTS, EVENT_INVOKER_POST_LOAD_ARGUMENTS
        from azure.cli.core.commands.arm import register_global_subscription_argument, register_ids_argument

        # setup a dummy CLI with a valid invocation object.
        cls.cli = DummyCli()
        cli_ctx = cls.cli.commands_loader.cli_ctx
        cls.cli.invocation = cli_ctx.invocation_cls(cli_ctx=cli_ctx,
                                                    parser_cls=cli_ctx.parser_cls,
                                                    commands_loader_cls=cli_ctx.commands_loader_cls,
                                                    help_cls=cli_ctx.help_cls)
        # load command table for every module
        cmd_loader = cls.cli.invocation.commands_loader
        cmd_loader.load_command_table(None)

        # Note: Both of the below events rely on EVENT_INVOKER_POST_CMD_TBL_CREATE.
        # register handler for adding subscription argument
        register_global_subscription_argument(cli_ctx)
        # register handler for adding ids argument.
        register_ids_argument(cli_ctx)

        cli_ctx.raise_event(EVENT_INVOKER_PRE_LOAD_ARGUMENTS, commands_loader=cmd_loader)

        # load arguments for each command
        for scenario in NORMALIZATION_TEST_SCENARIOS:
            cmd = scenario.command
            # simulate command invocation by filling in required metadata.
            cmd_loader.command_name = cmd
            cli_ctx.invocation.data['command_string'] = cmd
            # load argument info for the given command.
            cmd_loader.load_arguments(cmd)

        cli_ctx.raise_event(EVENT_INVOKER_POST_LOAD_ARGUMENTS, commands_loader=cmd_loader)
        cli_ctx.raise_event(EVENT_INVOKER_POST_CMD_TBL_CREATE, commands_loader=cmd_loader)

        cls.cmd_tbl = cmd_loader.command_table

    def setUp(self):
        super().setUp()

        self.scenarios = NORMALIZATION_TEST_SCENARIOS

    def assertScenarioIsHandledCorrectly(self, scenario: CommandParameterNormalizationScenario):
        normalized_command, normalized_parameters, unrecognized_parameters = scenario.normalize(self.cmd_tbl)
        self.assertEqual(normalized_parameters, scenario.normalized_parameters)
        self.assertEqual(normalized_command, scenario.normalized_command)

    def _create_invalid_subcommand_scenario(self,
                                            scenario: CommandParameterNormalizationScenario,
                                            invalid_subcommand: str):

        invalid_subcommands = [invalid_subcommand] * (1 if scenario.command else 2)
        sep = ' ' if scenario.command else ''
        command_with_invalid_subcommand = scenario.command + sep + ' '.join(invalid_subcommands)

        invalid_subcommand_scenario = deepcopy(scenario)
        invalid_subcommand_scenario.command = CommandNormalizationScenario(
            command_with_invalid_subcommand,
            scenario.command if scenario.command else invalid_subcommand
        )
        return invalid_subcommand_scenario

    def test_command_parameter_normalization(self):
        for scenario in self.scenarios:
            # base command
            self.assertScenarioIsHandledCorrectly(scenario)
            # command with invalid subcommand
            invalid_subcommand_scenario = self._create_invalid_subcommand_scenario(scenario, 'oops')
            self.assertScenarioIsHandledCorrectly(invalid_subcommand_scenario)
