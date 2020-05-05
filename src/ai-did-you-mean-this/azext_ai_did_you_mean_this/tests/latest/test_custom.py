import unittest
from enum import Enum, auto

from azure.cli.core.mock import DummyCli
from azure.cli.core import MainCommandsLoader

from azext_ai_did_you_mean_this.custom import normalize_and_sort_parameters
from azext_ai_did_you_mean_this.tests.latest._commands import get_commands, AzCommandType


class AiDidYouMeanThisCustomScenarioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        # load command table for the respective modules.
        cmd_loader = cls.cli.invocation.commands_loader
        cmd_loader.load_command_table(None)

        # Note: Both of the below events rely on EVENT_INVOKER_POST_CMD_TBL_CREATE.
        # register handler for adding subscription argument
        register_global_subscription_argument(cli_ctx)
        # register handler for adding ids argument.
        register_ids_argument(cli_ctx)

        cli_ctx.raise_event(EVENT_INVOKER_PRE_LOAD_ARGUMENTS, commands_loader=cmd_loader)

        # load arguments for each command
        for cmd in get_commands():
            # simulate command invocation by filling in required metadata.
            cmd_loader.command_name = cmd
            cli_ctx.invocation.data['command_string'] = cmd
            # load argument info for the given command.
            cmd_loader.load_arguments(cmd)

        cli_ctx.raise_event(EVENT_INVOKER_POST_LOAD_ARGUMENTS, commands_loader=cmd_loader)
        cli_ctx.raise_event(EVENT_INVOKER_POST_CMD_TBL_CREATE, commands_loader=cmd_loader)

        cls.cmd_tbl = cmd_loader.command_table

    def test_custom_normalize_and_sort_parameters(self):
        for cmd in AzCommandType:
            parameters = normalize_and_sort_parameters(self.cmd_tbl, cmd.command, cmd.parameters)
            self.assertEqual(parameters, cmd.expected_parameters)

    def test_custom_normalize_and_sort_parameters_remove_invalid_command_token(self):
        for cmd in AzCommandType:
            cmd_with_invalid_token = f'{cmd.command} oops'
            parameters = normalize_and_sort_parameters(self.cmd_tbl, cmd_with_invalid_token, cmd.parameters)
            self.assertEqual(parameters, cmd.expected_parameters)

    def test_custom_normalize_and_sort_parameters_empty_parameter_list(self):
        cmd = AzCommandType.ACCOUNT_SET
        parameters = normalize_and_sort_parameters(self.cmd_tbl, cmd.command, '')
        self.assertEqual(parameters, '')

    def test_custom_normalize_and_sort_parameters_invalid_command(self):
        invalid_cmd = 'Lorem ipsum.'
        parameters = normalize_and_sort_parameters(self.cmd_tbl, invalid_cmd, ['--foo', '--baz'])
        self.assertEqual(parameters, '')
