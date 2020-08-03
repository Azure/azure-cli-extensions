# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from enum import Enum, auto

from azure.cli.core.mock import DummyCli
from azure.cli.core import MainCommandsLoader

from azext_ai_did_you_mean_this.custom import normalize_and_sort_parameters
from azext_ai_did_you_mean_this.tests.latest._commands import get_commands, AzCommandType

from azext_ai_did_you_mean_this.tests.latest.mock.extension_telemetry_session import ExtensionTelemetryMockSession
from azext_ai_did_you_mean_this.telemetry import TelemetryProperty, get_property, _extension_telemetry_manager
from azext_ai_did_you_mean_this._parameter import GLOBAL_PARAM_BLOCKLIST


class TestNormalizeAndSortParameters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestNormalizeAndSortParameters, cls).setUpClass()

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
        for cmd in get_commands():
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

        self.telemetry_properties = [
            TelemetryProperty.RawCommand,
            TelemetryProperty.Command,
            TelemetryProperty.RawParams,
            TelemetryProperty.Params,
            TelemetryProperty.UnrecognizedParams
        ]

    def _assert_telemetry_properties_are_set(self, raw_command: str, command: str, raw_parameters: list, parameters: str):
        self.assertEqual(get_property(TelemetryProperty.RawCommand), raw_command)
        self.assertEqual(get_property(TelemetryProperty.Command), command)
        self.assertEqual(get_property(TelemetryProperty.RawParams), ','.join(raw_parameters))
        self.assertEqual(get_property(TelemetryProperty.Params), parameters)
        raw_parameter_set = set(sorted(param for param in raw_parameters if param.startswith('--')))
        raw_parameter_set.difference_update(GLOBAL_PARAM_BLOCKLIST)
        normalized_parameters = set(parameters.split(','))
        unrecognized_parameters = list(sorted(raw_parameter_set - normalized_parameters))

        def is_prefix(token, parameters):
            number_of_matches = len([p for p in parameters if token != p and p.startswith(token)])
            return number_of_matches == 1

        unrecognized_parameters = ','.join([p for p in unrecognized_parameters if not is_prefix(p, normalized_parameters)])
        self.assertEqual(get_property(TelemetryProperty.UnrecognizedParams), unrecognized_parameters)

        for telemetry_property in self.telemetry_properties:
            self.assertIn(telemetry_property, _extension_telemetry_manager.properties)

    def _assert_session_telemetry_properties_are_set(self, session: ExtensionTelemetryMockSession):
        for telemetry_property in self.telemetry_properties:
            self.assertIn(telemetry_property, session.extension_event.properties)
            self.assertDictContainsSubset(
                _extension_telemetry_manager.properties,
                session.extension_event.properties
            )

    def test_custom_normalize_and_sort_parameters(self):
        for cmd in AzCommandType:
            with ExtensionTelemetryMockSession() as session:
                command, parameters = normalize_and_sort_parameters(self.cmd_tbl, cmd.command, cmd.parameters)
                self.assertEqual(parameters, cmd.expected_parameters)
                self.assertEqual(command, cmd.command)

                self._assert_telemetry_properties_are_set(cmd.command, command, cmd.parameters, parameters)

            self._assert_session_telemetry_properties_are_set(session)

    def test_custom_normalize_and_sort_parameters_remove_invalid_command_token(self):
        for cmd in AzCommandType:
            with ExtensionTelemetryMockSession() as session:
                cmd_with_invalid_token = f'{cmd.command} oops'
                command, parameters = normalize_and_sort_parameters(self.cmd_tbl, cmd_with_invalid_token, cmd.parameters)
                self.assertEqual(parameters, cmd.expected_parameters)
                self.assertEqual(command, cmd.command)

                self._assert_telemetry_properties_are_set(cmd_with_invalid_token, command, cmd.parameters, parameters)

            self._assert_session_telemetry_properties_are_set(session)

    def test_custom_normalize_and_sort_parameters_empty_parameter_list(self):
        with ExtensionTelemetryMockSession() as session:
            cmd = AzCommandType.ACCOUNT_SET
            params = ['']
            command, parameters = normalize_and_sort_parameters(self.cmd_tbl, cmd.command, params)
            self.assertEqual(parameters, '')
            self.assertEqual(command, cmd.command)

            self._assert_telemetry_properties_are_set(cmd.command, command, params, '')

        self._assert_session_telemetry_properties_are_set(session)

    def test_custom_normalize_and_sort_parameters_invalid_command(self):
        with ExtensionTelemetryMockSession() as session:
            invalid_cmd = 'Lorem ipsum.'
            invalid_params = ['--foo', '--baz']
            command, parameters = normalize_and_sort_parameters(self.cmd_tbl, invalid_cmd, invalid_params)
            self.assertEqual(parameters, '')
            # verify that recursive parsing removes the last invalid whitespace delimited token.
            self.assertEqual(command, 'Lorem')

            self._assert_telemetry_properties_are_set(invalid_cmd, 'Lorem', invalid_params, '')

        self._assert_session_telemetry_properties_are_set(session)
