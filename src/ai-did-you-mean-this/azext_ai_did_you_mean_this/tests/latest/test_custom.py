import unittest

from azure.cli.core.mock import DummyCli
from azure.cli.core import MainCommandsLoader

from azext_ai_did_you_mean_this.custom import normalize_and_sort_parameters


class AiDidYouMeanThisCustomScenarioTest(unittest.TestCase):

    def setUp(self):
        from knack.events import EVENT_INVOKER_POST_CMD_TBL_CREATE
        from azure.cli.core.commands.events import EVENT_INVOKER_PRE_LOAD_ARGUMENTS, EVENT_INVOKER_POST_LOAD_ARGUMENTS
        from azure.cli.core.commands.arm import register_global_subscription_argument, register_ids_argument

        args = ['vm', 'show', '--ids', 'foo']
        command = 'vm show'

        self.cli = DummyCli()
        cli_ctx = self.cli.commands_loader.cli_ctx
        self.cli.invocation = cli_ctx.invocation_cls(cli_ctx=cli_ctx,
                                                     parser_cls=cli_ctx.parser_cls,
                                                     commands_loader_cls=cli_ctx.commands_loader_cls,
                                                     help_cls=cli_ctx.help_cls)

        cmd_loader = self.cli.invocation.commands_loader
        cmd_loader.load_command_table(args)
        cmd_loader.command_table = {command: cmd_loader.command_table[command]}

        cmd_loader.command_name = command
        cli_ctx.invocation.data['command_string'] = command

        register_global_subscription_argument(cli_ctx)
        register_ids_argument(cli_ctx)

        cli_ctx.raise_event(EVENT_INVOKER_PRE_LOAD_ARGUMENTS, commands_loader=cmd_loader)
        cmd_loader.load_arguments(command)
        cli_ctx.raise_event(EVENT_INVOKER_POST_LOAD_ARGUMENTS, commands_loader=cmd_loader)
        cli_ctx.raise_event(EVENT_INVOKER_POST_CMD_TBL_CREATE, commands_loader=cmd_loader)

        self.cmd_tbl = cmd_loader.command_table
        self.cmd = command
        self.parameters = ['-g', '--name', '-n', '--resource-group', '--subscription', 'invalid', '-o', '-h', '--help', '--debug', '--verbose']
        self.expected_parameters = ','.join(['--help', '--name', '--output', '--resource-group', '--subscription'])

    def test_custom_normalize_and_sort_parameters(self):
        parameters = normalize_and_sort_parameters(self.cmd_tbl, self.cmd, self.parameters)
        self.assertEqual(parameters, self.expected_parameters)

    def test_custom_normalize_and_sort_parameters_remove_invalid_command_token(self):
        cmd_with_invalid_token = f'{self.cmd} oops'
        parameters = normalize_and_sort_parameters(self.cmd_tbl, cmd_with_invalid_token, self.parameters)
        self.assertEqual(parameters, self.expected_parameters)
