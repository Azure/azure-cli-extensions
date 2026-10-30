# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import json
import logging
import os
import pytest
import shlex
import tempfile
import time
import unittest
import unittest.mock
import yaml
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime
from functools import partial
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse, parse_qs

from knack.config import CLIConfig

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import ScenarioTest
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError, ResourceNotFoundError as CliResourceNotFoundError
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError as AzureResourceNotFoundError

from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, issue_cmd_with_param_missing, get_test_workspace_storage, run_cleanup_commands, get_offer_targets_with_quota
from ...commands import transform_output
from ...operations.job import (
    list_files,
    download_file,
    update,
    _validate_max_poll_wait_secs,
    _convert_numeric_params,
    _construct_filter_query,
    _construct_orderby_expression,
    submit,
    run,
    ERROR_MSG_INVALID_PRIORITY_ARGUMENT,
    ERROR_MSG_INVALID_ORDER_ARGUMENT,
    ERROR_MSG_MISSING_ORDERBY_ARGUMENT)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# Temporary V2 workspaces only run short simulator jobs in this test; cap the allocation request accordingly.
TEST_V2_QUOTA_ALLOCATION_MINUTES = 2


class QuantumJobsArgumentTest(unittest.TestCase):

    def test_job_handlers_do_not_accept_storage(self):
        for handler in (submit, run):
            with self.subTest(handler=handler.__name__):
                self.assertNotIn('storage', inspect.signature(handler).parameters)

    def test_storage_argument_is_not_registered(self):
        from azure.cli.core.mock import DummyCli
        from ... import QuantumCommandsLoader

        loader = QuantumCommandsLoader(cli_ctx=DummyCli())
        loader.skip_applicability = True
        loader.load_command_table(None)
        loader.load_arguments(None)

        for scope, arguments in loader.argument_registry.arguments.items():
            with self.subTest(scope=scope):
                self.assertNotIn('storage', arguments)

    def _get_job_command_parser(self, command_name):
        from azure.cli.core.mock import DummyCli
        from azure.cli.core.parser import AzCliCommandParser
        from ... import QuantumCommandsLoader

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        cli = DummyCli()
        cli.config = CLIConfig(
            config_dir=directory.name,
            config_env_var_prefix='QUANTUM_PARSER_TEST',
            use_local_config=False,
        )
        cli.local_context = SimpleNamespace(is_on=False)

        loader = QuantumCommandsLoader(cli_ctx=cli)
        loader.skip_applicability = True
        loader.load_command_table(None)
        loader.command_table = {command_name: loader.command_table[command_name]}

        main_loader = cli.commands_loader
        main_loader.command_table = loader.command_table
        main_loader.command_group_table = loader.command_group_table
        main_loader.cmd_to_loader_map = {command_name: [loader]}
        cli.invocation = SimpleNamespace(
            commands_loader=main_loader,
            data={'command_string': command_name},
        )
        main_loader.load_arguments(command_name)

        parser = AzCliCommandParser(cli_ctx=cli, prog='az')
        parser.load_command_table(main_loader)
        return parser

    def test_job_commands_parse_without_storage(self):
        commands = ('quantum job submit', 'quantum run', 'quantum execute')
        for command_name in commands:
            with self.subTest(command=command_name):
                parser = self._get_job_command_parser(command_name)
                args = command_name.split()
                args.extend(['-g', 'test-rg', '-w', 'test-ws', '-t', 'provider.sim'])
                args.extend(['--job-input-file', 'input.bc', '--job-input-format', 'qir.v1'])
                parsed = parser.parse_args(args)
                self.assertEqual(parsed.command, command_name)
                self.assertEqual(parsed.job_input_file, 'input.bc')

    def test_job_command_help_preserves_summary_and_examples(self):
        from knack.help_files import helps
        from ... import _help  # pylint: disable=unused-import

        commands = ('quantum job submit', 'quantum run', 'quantum execute')
        for command_name in commands:
            with self.subTest(command=command_name):
                definition = yaml.safe_load(helps[command_name])
                self.assertEqual(definition['type'], 'command')
                self.assertEqual(
                    definition['long-summary'].strip(),
                    'Jobs use storage linked to the Azure Quantum workspace. '
                    'Arbitrary per-job storage accounts are not supported.',
                )
                # Examples must remain a separate YAML key, not become summary text.
                self.assertEqual(len(definition['examples']), 3)
                for example in definition['examples']:
                    self.assertTrue(example['name'])
                    self.assertIn('az ' + command_name, example['text'])
                    self.assertNotIn('--storage', example['text'])

    @unittest.mock.patch('azure.cli.core.util.show_updates_available')
    def test_job_command_help_does_not_show_storage(self, updates_mock):
        from azure.cli.core._help import AzCliHelp

        commands = ('quantum job submit', 'quantum run', 'quantum execute')
        for command_name in commands:
            with self.subTest(command=command_name):
                parser = self._get_job_command_parser(command_name)
                command_parser = parser.subparser_map[command_name]
                help_renderer = AzCliHelp(cli_ctx=parser.cli_ctx)
                output = StringIO()

                with redirect_stdout(output):
                    help_renderer.show_help(
                        'az', command_name.split(), command_parser, is_group=False
                    )

                help_text = output.getvalue()
                self.assertIn('--job-input-file', help_text)
                self.assertIn('--target-id', help_text)
                self.assertNotIn('--storage', help_text)
                normalized_help = ' '.join(help_text.split())
                self.assertIn(
                    'Jobs use storage linked to the Azure Quantum workspace.', normalized_help
                )
                self.assertIn(
                    'Arbitrary per-job storage accounts are not supported.', normalized_help
                )
                self.assertIn('Examples', help_text)
                self.assertIn('az ' + command_name, normalized_help)

    def test_workspace_create_preserves_optional_storage_account(self):
        # Optional workspace storage is separate from the removed per-job override.
        command_name = 'quantum workspace create'
        parser = self._get_job_command_parser(command_name)
        command = parser.cli_ctx.invocation.commands_loader.command_table[command_name]
        argument = command.arguments['storage_account']
        self.assertIn('--storage-account', argument.options_list)
        self.assertIn('-a', argument.options_list)
        self.assertFalse(argument.options.get('required', False))

        args = command_name.split() + ['-g', 'test-rg', '-w', 'test-ws', '-l', 'eastus']
        parsed = parser.parse_args(args)
        self.assertIsNone(parsed.storage_account)

        for option in ('--storage-account', '-a'):
            with self.subTest(option=option):
                parser = self._get_job_command_parser(command_name)
                parsed = parser.parse_args(args + [option, 'teststorage'])
                self.assertEqual(parsed.storage_account, 'teststorage')


class QuantumJobsStorageRejectionTest(unittest.TestCase):
    """Exercise the invocation hook and real error rendering, not only parser metadata."""

    _COMMANDS = ('quantum job submit', 'quantum run', 'quantum execute')
    # These were unambiguous aliases of --storage before removal; --s was ambiguous.
    _STORAGE_OPTIONS = ('--st', '--sto', '--stor', '--stora', '--storag', '--storage')
    _MARKER = 'FAKE_STORAGE_KEY_NOT_A_REAL_SECRET'
    _CONNECTION = 'DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=' + _MARKER
    _MESSAGE = 'The --storage option has been removed.'
    _GUIDANCE = 'Remove --storage from the command. Jobs use storage linked to the Azure Quantum workspace.'

    def setUp(self):
        from azure.cli.core import MainCommandsLoader
        from azure.cli.core.azlogging import AzCliLogging
        from azure.cli.core.cloud import AZURE_PUBLIC_CLOUD
        from azure.cli.core.parser import AzCliCommandParser
        from azure.cli.core._help import AzCliHelp
        from knack.cli import CLI
        from ... import QuantumCommandsLoader

        class QuantumOnlyLoader(MainCommandsLoader):
            def load_command_table(self, args):
                # Only replace command discovery; argument loading, events, and parsing are real.
                loader = QuantumCommandsLoader(cli_ctx=self.cli_ctx)
                self.command_table = loader.load_command_table(args)
                self.command_group_table = loader.command_group_table
                self.cmd_to_loader_map = {name: [loader] for name in self.command_table}
                self.loaders = [loader]
                return self.command_table

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.config_dir = Path(directory.name).resolve()
        # Avoid AzCli/DummyCli initialization, which loads global account/session caches.
        self.cli = CLI(
            cli_name='az', config_dir=str(self.config_dir),
            config_env_var_prefix='QUANTUM_REJECTION_TEST',
            config_cls=partial(CLIConfig, use_local_config=False),
            logging_cls=AzCliLogging, commands_loader_cls=QuantumOnlyLoader,
            parser_cls=AzCliCommandParser, help_cls=AzCliHelp,
        )
        self.cli.cloud = deepcopy(AZURE_PUBLIC_CLOUD)
        self.cli.cloud.profile = 'latest'
        self.cli.local_context = SimpleNamespace(is_on=False)
        self.cli.refresh_request_id = lambda: None
        self.cli.data['completer_active'] = False
        self.cli.config.set_value('core', 'use_command_index', 'false')
        self.cli.config.set_value('core', 'error_recommendation', 'off')
        self.cli.config.set_value('core', 'collect_telemetry', 'false')
        self.cli.enable_color = False
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for target in ('socket.socket.connect', 'socket.getaddrinfo'):
            self.stack.enter_context(unittest.mock.patch(
                target, side_effect=AssertionError('Offline test attempted network access.')))
        self.stack.enter_context(unittest.mock.patch(
            'azext_quantum._version_check_helper.check_version', return_value=None))
        self.stack.enter_context(unittest.mock.patch('azure.cli.core.util.show_updates_available'))

    @staticmethod
    def _job_args(command):
        return command.split() + [
            '-g', 'test-rg', '-w', 'test-ws', '-t', 'provider.sim',
            '--job-input-file', 'input.bc', '--job-input-format', 'qir.v1',
        ]

    def _invoke(self, args):
        from azure.cli.core.commands import AzCliCommandInvoker

        stdout, stderr = StringIO(), StringIO()
        error_logger = logging.getLogger('cli.azure.cli.core.azclierror')
        handler = logging.StreamHandler(stderr)
        # Existing pytest/CLI handlers may already be bound to a different stream.
        with ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(error_logger, 'handlers', [handler]))
            stack.enter_context(unittest.mock.patch.object(error_logger, 'level', logging.ERROR))
            stack.enter_context(unittest.mock.patch.object(error_logger, 'propagate', False))
            stack.enter_context(redirect_stdout(stdout))
            stack.enter_context(redirect_stderr(stderr))
            error_type = stack.enter_context(unittest.mock.patch('azure.cli.core.telemetry.set_error_type'))
            user_fault = stack.enter_context(unittest.mock.patch('azure.cli.core.telemetry.set_user_fault'))
            # Stop at the service boundary for positive controls; rejected inputs must not reach it.
            validation = stack.enter_context(unittest.mock.patch.object(AzCliCommandInvoker, '_validation'))
            dispatch = stack.enter_context(unittest.mock.patch.object(
                AzCliCommandInvoker, '_run_job', return_value={'id': 'test-job'}))
            invocation = AzCliCommandInvoker(
                cli_ctx=self.cli, commands_loader_cls=self.cli.commands_loader_cls,
                parser_cls=self.cli.parser_cls, help_cls=self.cli.help_cls,
            )
            self.cli.invocation = invocation
            exit_code = 1
            try:
                result = invocation.execute(args)
                exit_code = result.exit_code
            except SystemExit as error:
                exit_code = error.code
            finally:
                # Match CLI.invoke's post-execute log cleanup, including on SystemExit.
                self.cli.logging.end_cmd_metadata_logging(exit_code)
                handler.close()

        command_log = '\n'.join(path.read_text(encoding='utf-8')
                                for path in (self.config_dir / 'commands').glob('*.log'))
        return SimpleNamespace(
            exit_code=exit_code, stdout=stdout.getvalue(), stderr=stderr.getvalue(),
            command_log=command_log, validation=validation, dispatch=dispatch,
            error_type=error_type, user_fault=user_fault,
        )

    def _assert_safe_rejection(self, result, logging_enabled=True):
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr.count(self._MESSAGE), 1)
        self.assertIn(self._GUIDANCE, result.stderr)
        for output in (result.stdout, result.stderr, result.command_log):
            self.assertNotIn(self._MARKER, output)
            self.assertNotIn('AccountKey=', output)
        if logging_enabled:
            self.assertIn(self._MESSAGE, result.command_log)
            self.assertIn('exit code: 2', result.command_log)
        else:
            self.assertEqual(result.command_log, '')
        result.error_type.assert_called_once_with('UnrecognizedArgumentError')
        result.user_fault.assert_called_once_with(self._MESSAGE)
        result.validation.assert_not_called()
        result.dispatch.assert_not_called()

    def test_job_commands_reject_storage_without_echoing_secrets(self):
        for command in self._COMMANDS:
            for option in self._STORAGE_OPTIONS:
                for options in ([option, self._CONNECTION], [option + '=' + self._CONNECTION]):
                    with self.subTest(command=command, option=option, equals=len(options) == 1):
                        self._assert_safe_rejection(self._invoke(self._job_args(command) + options))

    def test_storage_from_file_and_verbosity_options(self):
        path = self.config_dir / 'fake-connection.txt'
        path.write_text(self._CONNECTION, encoding='utf-8')
        for value in (self._CONNECTION, '@' + str(path)):
            for flags in ([], ['--only-show-errors'], ['--verbose']):
                for option in self._STORAGE_OPTIONS:
                    for options in ([option, value], [option + '=' + value]):
                        with self.subTest(option=option, file=value.startswith('@'),
                                          flags=flags, equals=len(options) == 1):
                            self._assert_safe_rejection(self._invoke(
                                self._job_args('quantum job submit') + options + flags))

    def test_storage_rejection_precedes_other_argument_errors(self):
        for option in self._STORAGE_OPTIONS:
            for options in (
                    [option], [option + '='], [option, ''],
                    [option, self._CONNECTION, '--storage=' + self._CONNECTION + '-second'],
                    ['--unknown', 'value', option, self._CONNECTION],
                    ['--help', option, self._CONNECTION],
                    ['--', option, self._CONNECTION]):
                with self.subTest(options=options):
                    # Deliberately omit other required arguments. They must not cause a secret echo.
                    self._assert_safe_rejection(self._invoke(['quantum', 'job', 'submit'] + options))

    def test_storage_rejection_without_command_file_logging(self):
        self.cli.config.set_value('logging', 'enable_log_file', 'false')
        for option in self._STORAGE_OPTIONS:
            with self.subTest(option=option):
                self._assert_safe_rejection(self._invoke(
                    self._job_args('quantum run') + [option, self._CONNECTION]), logging_enabled=False)

    def test_normal_job_commands_and_literal_option_values_are_preserved(self):
        options_to_test = [[], ['--shots', '10'], ['--sh', '10']]
        for option in self._STORAGE_OPTIONS:
            options_to_test.extend(([f'--job-name={option}'], [f'--job-name={option}=value']))
        for command in self._COMMANDS:
            for options in options_to_test:
                with self.subTest(command=command, options=options):
                    result = self._invoke(self._job_args(command) + options)
                    self.assertEqual(result.exit_code, 0)
                    result.validation.assert_called_once()
                    result.dispatch.assert_called_once()
                    result.user_fault.assert_not_called()

    def test_workspace_storage_options_are_preserved(self):
        cases = [
            ([], None), (['--storage-account', 'storage'], 'storage'),
            (['--storage-account=storage'], 'storage'), (['-a', 'storage'], 'storage'),
        ]
        for option in self._STORAGE_OPTIONS:
            cases.extend((([option, 'storage'], 'storage'), ([option + '=storage'], 'storage')))
        for kind in ('V1', 'V2'):
            for options, expected in cases:
                with self.subTest(kind=kind, options=options):
                    result = self._invoke([
                        'quantum', 'workspace', 'create', '-g', 'rg', '-w', 'ws', '-l', 'eastus',
                        '--workspace-kind', kind,
                    ] + options)
                    self.assertEqual(result.exit_code, 0)
                    result.dispatch.assert_called_once()
                    parsed = result.dispatch.call_args.args[0]
                    self.assertEqual(parsed.storage_account, expected)
                    result.user_fault.assert_not_called()

    def test_help_is_preserved(self):
        for command in self._COMMANDS:
            with self.subTest(command=command):
                result = self._invoke(command.split() + ['--help'])
                self.assertEqual(result.exit_code, 0)
                self.assertIn('--job-input-file', result.stdout)
                self.assertNotIn('--storage', result.stdout)
                result.dispatch.assert_not_called()
                result.user_fault.assert_not_called()

    def test_guard_does_not_accumulate_on_repeated_loader_initialization(self):
        from knack.events import EVENT_INVOKER_PRE_PARSE_ARGS
        from ... import QuantumCommandsLoader, _reject_removed_job_storage_argument

        for _ in range(3):
            QuantumCommandsLoader(cli_ctx=self.cli)
        self.assertEqual(self.cli._event_handlers[EVENT_INVOKER_PRE_PARSE_ARGS].count(
            _reject_removed_job_storage_argument), 1)
        self._assert_safe_rejection(self._invoke(
            self._job_args('quantum execute') + ['--storage', self._CONNECTION]))

    def test_guard_ignores_non_job_contexts_and_unrelated_option_names(self):
        from ... import _reject_removed_job_storage_argument

        for command, args, completing in (
                ('quantum workspace create', ['--storage-account', 'storage'], False),
                ('quantum workspace create', ['--storage', 'storage'], False),
                ('quantum workspace create', ['--st', 'storage'], False),
                ('quantum job submit', ['--storage-account=storage'], False),
                ('quantum job submit', ['--storage-other=value'], False),
                ('quantum job submit', ['--store=value'], False),
                ('quantum job submit', ['--staging=value'], False),
                ('quantum job submit', ['--s', '10'], False),
                ('quantum job submit', ['--job-name=--storage'], False),
                ('quantum job submit', ['--job-name=--st=value'], False),
                ('quantum job submit', ['--storage', self._CONNECTION], True),
                ('quantum job submit', ['--st', self._CONNECTION], True),
                ('quantum job list', ['--st', self._CONNECTION], False),
                ('quantum job list', ['--storage', self._CONNECTION], False)):
            with self.subTest(command=command, args=args, completing=completing):
                parser = unittest.mock.Mock()
                self.cli.invocation = SimpleNamespace(data={'command_string': command}, parser=parser)
                self.cli.data['completer_active'] = completing
                _reject_removed_job_storage_argument(self.cli, args=args)
                parser.exit.assert_not_called()
        self.cli.invocation = None
        _reject_removed_job_storage_argument(self.cli, args=['--storage'])


class QuantumJobsOperationsTest(unittest.TestCase):

    @unittest.mock.patch('azext_quantum.operations.job.output')
    @unittest.mock.patch('azext_quantum.operations.job.wait')
    @unittest.mock.patch('azext_quantum.operations.job.submit')
    def test_run_forwards_optional_arguments(self, submit_mock, wait_mock, output_mock):
        cmd = SimpleNamespace(cli_ctx=object())
        job_params = {'custom': 'value'}
        expected_result = {'result': 'finished'}
        submit_mock.return_value = {'id': 'job-123'}
        wait_mock.return_value = {'id': 'job-123'}
        output_mock.return_value = expected_result
        # Call run() with distinct values
        result = run(
            cmd, 'test-rg', 'test-ws', 'provider.sim', 'input.bc', 'qir.v1',
            job_name='test-job', shots=25, job_params=job_params,
            target_capability='AdaptiveExecution',
            job_output_format='custom.results.v1', entry_point='Main',
        )
        # Check what was forwarded
        submit_mock.assert_called_once_with(
            cmd, 'test-rg', 'test-ws', 'provider.sim', 'input.bc', 'qir.v1',
            job_name='test-job', shots=25, job_params=job_params,
            target_capability='AdaptiveExecution',
            job_output_format='custom.results.v1', entry_point='Main',
        )
        wait_mock.assert_called_once_with(cmd, 'job-123', 'test-rg', 'test-ws')
        output_mock.assert_called_once_with(cmd, 'job-123', 'test-rg', 'test-ws')
        self.assertIs(result, expected_result)

    @unittest.mock.patch('azext_quantum.operations.job.output')
    @unittest.mock.patch('azext_quantum.operations.job.wait')
    @unittest.mock.patch('azext_quantum.operations.job.submit')
    def test_run_without_optional_arguments(self, submit_mock, wait_mock, output_mock):
        cmd = SimpleNamespace(cli_ctx=object())
        expected_result = {'result': 'finished'}
        submit_mock.return_value = {'id': 'job-123'}
        wait_mock.return_value = {'id': 'job-123'}
        output_mock.return_value = expected_result
        # Omitted options must retain their defaults after removing the storage parameter.
        result = run(cmd, 'test-rg', 'test-ws', 'provider.sim', 'input.bc', 'qir.v1')
        # Check what was forwarded
        submit_mock.assert_called_once_with(
            cmd, 'test-rg', 'test-ws', 'provider.sim', 'input.bc', 'qir.v1',
            job_name=None, shots=None, job_params=None,
            target_capability=None,
            job_output_format=None, entry_point=None,
        )
        wait_mock.assert_called_once_with(cmd, 'job-123', 'test-rg', 'test-ws')
        output_mock.assert_called_once_with(cmd, 'job-123', 'test-rg', 'test-ws')
        self.assertIs(result, expected_result)

    def test_submit_uses_workspace_storage(self):
        from ...operations import job as job_ops

        cmd = SimpleNamespace(cli_ctx=object())
        info = SimpleNamespace(
            subscription='sub', resource_group='test-rg', name='test-ws',
            endpoint='https://test-ws.eastus.quantum.azure.com',
        )
        credential = object()
        job_id = '00000000-0000-0000-0000-000000000001'
        container_uri = f'https://example.com/job-{job_id}?test-sas'
        expected_result = {'id': job_id}
        input_data = b'test-qir-bitcode'
        job_params = {'custom': 'value'}

        # Exercise real submission logic while replacing files, credentials and service boundaries.
        with unittest.mock.patch.object(job_ops, 'WorkspaceInfo', return_value=info), \
                unittest.mock.patch.object(job_ops, 'TargetInfo', return_value=SimpleNamespace(target_id='provider.sim')), \
                unittest.mock.patch.object(job_ops, 'get_provider', return_value='provider'), \
                unittest.mock.patch.object(job_ops, '_get_data_credentials', return_value=credential) as get_credentials, \
                unittest.mock.patch.object(job_ops, 'Workspace') as workspace_factory, \
                unittest.mock.patch.object(job_ops, 'ContainerClient') as container_factory, \
                unittest.mock.patch.object(job_ops, 'upload_blob') as upload, \
                unittest.mock.patch.object(job_ops, 'cf_jobs') as jobs_factory, \
                unittest.mock.patch.object(job_ops.uuid, 'uuid4', return_value=job_id), \
                unittest.mock.patch('builtins.open', unittest.mock.mock_open(read_data=input_data)) as open_input:
            workspace_factory.return_value.get_container_uri.return_value = container_uri
            jobs_factory.return_value.create.return_value.as_dict.return_value = expected_result
            upload.return_value = f'https://example.com/job-{job_id}/inputData'

            result = submit(
                cmd, 'test-rg', 'test-ws', 'provider.sim', 'input.bc', 'qir.v1',
                job_name='test-job', shots=25, job_params=job_params,
                target_capability='AdaptiveExecution',
                job_output_format='custom.results.v1', entry_point='Main',
            )

            open_input.assert_called_once_with('input.bc', 'rb')
            get_credentials.assert_called_once_with(cmd.cli_ctx, 'sub')
            # No storage connection string is passed to the embedded SDK.
            workspace_factory.assert_called_once_with(
                resource_id='/subscriptions/sub/resourceGroups/test-rg/providers/Microsoft.Quantum/Workspaces/test-ws',
                credential=credential,
            )
            workspace_factory.return_value.get_container_uri.assert_called_once_with(job_id=job_id)
            container_factory.from_container_url.assert_called_once_with(container_uri)
            upload.assert_called_once_with(
                container_factory.from_container_url.return_value,
                'inputData', 'qir.v1', None, input_data, return_sas_token=False,
            )
            jobs_factory.assert_called_once_with(
                cmd.cli_ctx, 'sub', 'test-rg', 'test-ws', info.endpoint,
            )
            # The submitted payload uses the same workspace-provided container as the upload.
            jobs_factory.return_value.create.assert_called_once_with(
                'sub', 'test-rg', 'test-ws', job_id, {
                    'name': 'test-job',
                    'containerUri': container_uri,
                    'inputDataFormat': 'qir.v1',
                    'outputDataFormat': 'custom.results.v1',
                    'inputParams': {
                        'custom': 'value', 'shots': 25,
                        'targetCapability': 'AdaptiveExecution', 'entryPoint': 'Main',
                        'arguments': [],
                    },
                    'providerId': 'provider',
                    'target': 'provider.sim',
                    'metadata': None,
                    'tags': [],
                },
            )
        self.assertIs(result, expected_result)


class QuantumJobsScenarioTest(ScenarioTest):

    def _cmd_with_retry(self, command, retry_error_code, retries=3, delay=10):
        for attempt in range(retries):
            try:
                return self.cmd(command)
            except HttpResponseError as error:
                error_code = getattr(getattr(error, 'error', None), 'code', None)
                if (error_code != retry_error_code and f'({retry_error_code})' not in str(error)) \
                        or attempt == retries - 1:
                    raise
                time.sleep(delay)

    def _get_available_v2_simulator_with_quota(self, location):
        offers = self.cmd('az quantum suite-offer list -o json').get_output_in_json()
        for provider_id, targets_with_quota in get_offer_targets_with_quota(offers, location, min_quota=1):
            targets_with_quota = {
                target_id.lower(): quota for target_id, quota in targets_with_quota.items()
            }
            providers = self.cmd(
                f'az quantum suite-offer target list -p {provider_id} -o json'
            ).get_output_in_json()
            for provider in providers:
                for target in provider.get('targets', []):
                    target_id = target.get('id') or ''
                    available_quota = targets_with_quota.get(target_id.lower())
                    if available_quota \
                            and '.sim.' in target_id.lower() \
                            and (target.get('currentAvailability') or '').lower() == 'available':
                        # Keep the temporary allocation small without exceeding the available quota.
                        return provider_id, target_id, min(TEST_V2_QUOTA_ALLOCATION_MINUTES, available_quota)
        self.skipTest(
            f"No V2 simulator target with allocated quota is currently available in '{location}'."
        )

    @unittest.mock.patch('azext_quantum.tests.latest.test_quantum_jobs.time.sleep')
    def test_cmd_with_retry(self, mock_sleep):
        command_result = unittest.mock.Mock()
        transient_error = HttpResponseError('(StorageAccountInaccessible) transient error')
        with unittest.mock.patch.object(
                self, 'cmd', side_effect=[transient_error, transient_error, command_result]) as mock_cmd:
            self.assertIs(
                self._cmd_with_retry('az quantum job submit', 'StorageAccountInaccessible', retries=3, delay=10),
                command_result,
            )
        self.assertEqual(mock_cmd.call_count, 3)
        self.assertEqual(mock_sleep.call_args_list, [unittest.mock.call(10), unittest.mock.call(10)])

        mock_sleep.reset_mock()
        with unittest.mock.patch.object(self, 'cmd', side_effect=transient_error) as mock_cmd:
            with self.assertRaises(HttpResponseError):
                self._cmd_with_retry('az quantum job submit', 'StorageAccountInaccessible', retries=3, delay=10)
        self.assertEqual(mock_cmd.call_count, 3)
        self.assertEqual(mock_sleep.call_args_list, [unittest.mock.call(10), unittest.mock.call(10)])

        mock_sleep.reset_mock()
        non_retryable_error = HttpResponseError('(AuthorizationFailed) access denied')
        with unittest.mock.patch.object(self, 'cmd', side_effect=non_retryable_error) as mock_cmd:
            with self.assertRaises(HttpResponseError):
                self._cmd_with_retry('az quantum job submit', 'StorageAccountInaccessible', retries=3, delay=10)
        mock_cmd.assert_called_once_with('az quantum job submit')
        mock_sleep.assert_not_called()

    def test_get_available_v2_simulator_with_quota(self):
        offers = [{
            'properties': {
                'providerId': 'provider-a',
                'location': 'East US',
                'targetQuotas': [
                    {'targetId': 'provider-a.sim.zero', 'standardMinutesLifetime': 0},
                    {'targetId': 'Provider-A.Sim.One', 'standardMinutesLifetime': 1},
                    {'targetId': 'provider-a.sim.large', 'standardMinutesLifetime': 20},
                ],
            },
        }]
        providers = [{
            'targets': [
                {'id': 'provider-a.sim.zero', 'currentAvailability': 'Available'},
                {'id': 'provider-a.qpu', 'currentAvailability': 'Available'},
                {'id': 'provider-a.sim.unavailable', 'currentAvailability': 'Unavailable'},
                {'id': 'Provider-A.Sim.One', 'currentAvailability': 'Available'},
            ],
        }]
        with unittest.mock.patch.object(
                self,
                'cmd',
                side_effect=[
                    unittest.mock.Mock(get_output_in_json=unittest.mock.Mock(return_value=offers)),
                    unittest.mock.Mock(get_output_in_json=unittest.mock.Mock(return_value=providers)),
                ]):
            result = self._get_available_v2_simulator_with_quota('eastus')

        self.assertEqual(result, ('provider-a', 'Provider-A.Sim.One', 1))

    def test_get_available_v2_simulator_with_quota_caps_allocation(self):
        offers = [{
            'properties': {
                'providerId': 'provider-a',
                'location': 'eastus',
                'targetQuotas': [
                    {'targetId': 'provider-a.sim.large', 'standardMinutesLifetime': 20},
                ],
            },
        }]
        providers = [{
            'targets': [
                {'id': 'provider-a.sim.large', 'currentAvailability': 'Available'},
            ],
        }]
        with unittest.mock.patch.object(
                self,
                'cmd',
                side_effect=[
                    unittest.mock.Mock(get_output_in_json=unittest.mock.Mock(return_value=offers)),
                    unittest.mock.Mock(get_output_in_json=unittest.mock.Mock(return_value=providers)),
                ]):
            result = self._get_available_v2_simulator_with_quota('East US')

        self.assertEqual(result, ('provider-a', 'provider-a.sim.large', 2))

    def test_get_available_v2_simulator_with_quota_skips_when_no_target_matches(self):
        offers = [{
            'properties': {
                'providerId': 'provider-a',
                'location': 'eastus',
                'targetQuotas': [
                    {'targetId': 'provider-a.sim.zero', 'standardMinutesLifetime': 0},
                    {'targetId': 'provider-a.sim.unavailable', 'standardMinutesLifetime': 1},
                    {'targetId': 'provider-a.qpu', 'standardMinutesLifetime': 10},
                ],
            },
        }]
        providers = [{
            'targets': [
                {'id': 'provider-a.sim.zero', 'currentAvailability': 'Available'},
                {'id': 'provider-a.sim.unavailable', 'currentAvailability': 'Unavailable'},
                {'id': 'provider-a.qpu', 'currentAvailability': 'Available'},
            ],
        }]
        with unittest.mock.patch.object(
                self,
                'cmd',
                side_effect=[
                    unittest.mock.Mock(get_output_in_json=unittest.mock.Mock(return_value=offers)),
                    unittest.mock.Mock(get_output_in_json=unittest.mock.Mock(return_value=providers)),
                ]):
            with self.assertRaisesRegex(
                    unittest.SkipTest,
                    "No V2 simulator target with allocated quota is currently available in 'eastus'"):
                self._get_available_v2_simulator_with_quota('eastus')

    @live_only()
    def test_jobs(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -g {get_test_resource_group()} -w {get_test_workspace()}')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

    # @pytest.fixture(autouse=True)
    # def _pass_fixtures(self, capsys):
    #     self.capsys = capsys
    # # See "TODO" in issue_cmd_with_param_missing un utils.py

    def test_job_errors(self):
        issue_cmd_with_param_missing(self, "az quantum job cancel", "az quantum job cancel -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy\nCancel an Azure Quantum job by id.")
        issue_cmd_with_param_missing(self, "az quantum job delete", "az quantum job delete -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy\nDelete an Azure Quantum job by id.")
        issue_cmd_with_param_missing(self, "az quantum job update", "az quantum job update -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --job-name 'My new name'\nUpdate an Azure Quantum job by id.")
        issue_cmd_with_param_missing(self, "az quantum job output", "az quantum job output -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table\nPrint the results of a successful Azure Quantum job.")
        issue_cmd_with_param_missing(self, "az quantum job file list", "az quantum job file list -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table\nList the files stored in a job's output storage container.")
        issue_cmd_with_param_missing(self, "az quantum job file download", "az quantum job file download -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -n rawOutputData\nDownload a file from a job's output storage container.")
        issue_cmd_with_param_missing(self, "az quantum job show", "az quantum job show -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --query status\nGet the status of an Azure Quantum job.")
        issue_cmd_with_param_missing(self, "az quantum job wait", "az quantum job wait -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --max-poll-wait-secs 60 -o table\nWait for completion of a job, check at 60 second intervals.")

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_list_files(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import datetime
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob1 = unittest.mock.MagicMock()
        blob1.name = "rawOutputData"
        blob1.size = 42
        blob1.last_modified = datetime.datetime(2026, 1, 15, 12, 0, 0)

        blob2 = unittest.mock.MagicMock()
        blob2.name = "atom-logs.txt"
        blob2.size = 1024
        blob2.last_modified = None

        mock_container_client.from_container_url.return_value.list_blobs.return_value = [blob1, blob2]

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        result = list_files(cmd, job_id, "rg", "ws")

        mock_cf_jobs.return_value.get.assert_called_once_with("sub", "rg", "ws", job_id)
        mock_container_client.from_container_url.assert_called_once_with("https://acct.blob.core.windows.net/job-id?sas")
        self.assertEqual(result, [
            {"name": "rawOutputData", "size": 42, "lastModified": "2026-01-15T12:00:00"},
            {"name": "atom-logs.txt", "size": 1024, "lastModified": None}
        ])

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_list_files_raises_when_container_missing(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"
        mock_container_client.from_container_url.return_value.list_blobs.side_effect = AzureResourceNotFoundError("not found")

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with self.assertRaises(CliResourceNotFoundError):
            list_files(cmd, job_id, "rg", "ws")

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file_raises_when_file_missing(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"
        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        blob_client.download_blob.side_effect = AzureResourceNotFoundError("not found")

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with self.assertRaises(CliResourceNotFoundError):
            download_file(cmd, job_id, "missingFile", "rg", "ws")

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import tempfile

        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        file_content = b"hello world"

        def fake_readinto(stream):
            stream.write(file_content)
            return len(file_content)

        blob_client.download_blob.return_value.readinto.side_effect = fake_readinto

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = download_file(cmd, job_id, "rawOutputData", "rg", "ws", dest=tmp_dir)

            expected_path = os.path.join(tmp_dir, "rawOutputData")
            self.assertTrue(os.path.exists(expected_path))
            with open(expected_path, "rb") as file_handle:
                self.assertEqual(file_handle.read(), file_content)

            mock_cf_jobs.return_value.get.assert_called_once_with("sub", "rg", "ws", job_id)
            mock_container_client.from_container_url.return_value.get_blob_client.assert_called_once_with("rawOutputData")
            self.assertEqual(result["name"], "rawOutputData")
            self.assertEqual(result["path"], os.path.abspath(expected_path))
            self.assertEqual(result["size"], len(file_content))

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file_sanitizes_traversal_name(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import tempfile

        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        file_content = b"payload"

        def fake_readinto(stream):
            stream.write(file_content)
            return len(file_content)

        blob_client.download_blob.return_value.readinto.side_effect = fake_readinto

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with tempfile.TemporaryDirectory() as tmp_dir:
            target_dir = os.path.join(tmp_dir, "downloads")
            os.makedirs(target_dir)

            result = download_file(cmd, job_id, "../../evil.txt", "rg", "ws", dest=target_dir)

            # Only the basename is used, so the file stays inside target_dir
            # and never escapes via the traversal segments in the blob name.
            safe_path = os.path.join(target_dir, "evil.txt")
            self.assertTrue(os.path.exists(safe_path))
            self.assertFalse(os.path.exists(os.path.join(tmp_dir, "evil.txt")))
            self.assertEqual(result["path"], os.path.abspath(safe_path))

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file_creates_missing_output_directory(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import tempfile

        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        file_content = b"payload"

        def fake_readinto(stream):
            stream.write(file_content)
            return len(file_content)

        blob_client.download_blob.return_value.readinto.side_effect = fake_readinto

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with tempfile.TemporaryDirectory() as tmp_dir:
            # A non-existent --dest is created and treated as a directory.
            new_dir = os.path.join(tmp_dir, "downloads")

            result = download_file(cmd, job_id, "outputData", "rg", "ws", dest=new_dir)

            expected_path = os.path.join(new_dir, "outputData")
            self.assertTrue(os.path.isdir(new_dir))
            self.assertTrue(os.path.exists(expected_path))
            self.assertEqual(result["path"], os.path.abspath(expected_path))

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_job_update(self, mock_workspace_info, mock_cf_jobs):
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"
        info.endpoint = "endpoint"
        client = mock_cf_jobs.return_value
        client.get.return_value.as_dict.return_value = {"id": "job-id"}
        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        # Calling with no updatable fields should raise.
        with self.assertRaises(RequiredArgumentMissingError):
            update(cmd, job_id, "rg", "ws")

        # An invalid priority value should raise.
        with self.assertRaises(InvalidArgumentValueError) as context:
            update(cmd, job_id, "rg", "ws", job_priority="NotAPriority")
        self.assertEqual(str(context.exception), ERROR_MSG_INVALID_PRIORITY_ARGUMENT)

        # An empty or whitespace-only job name is ignored, so with no other fields it should raise.
        with self.assertRaises(RequiredArgumentMissingError):
            update(cmd, job_id, "rg", "ws", job_name="   ")

        # Passing only blank/whitespace tags is an explicit request to clear all tags,
        # which sends an empty list rather than raising.
        result = update(cmd, job_id, "rg", "ws", job_tags=["", "   "])
        client.update.assert_called_once_with("sub", "rg", "ws", job_id, {"tags": []})
        self.assertEqual(result, {"id": "job-id"})
        client.update.reset_mock()
        client.get.reset_mock()

        # A valid update should build a merge-patch with only the provided fields
        # and return the refreshed job. Surrounding whitespace is trimmed and blank
        # tags are dropped.
        result = update(cmd, job_id, "rg", "ws", job_name="  New name  ", job_priority="High", job_tags=["a", "  ", "b "])
        client.update.assert_called_once_with("sub", "rg", "ws", job_id, {"name": "New name", "priority": "High", "tags": ["a", "b"]})
        client.get.assert_called_once_with("sub", "rg", "ws", job_id)
        self.assertEqual(result, {"id": "job-id"})

    def test_transform_output(self):
        # Call with a good histogram
        test_job_results = '{"Histogram":["[0,0,0]",0.125,"[1,0,0]",0.125,"[0,1,0]",0.125,"[1,1,0]",0.125]}'
        table = transform_output(json.loads(test_job_results))
        table_row = table[0]
        hist_row = table_row['']
        second_char = hist_row[1]
        self.assertEqual(second_char, "\u2588")    # Expecting a "Full Block" character here

        # Give it a malformed histogram
        test_job_results = '{"Histogram":["[0,0,0]",0.125,"[1,0,0]",0.125,"[0,1,0]",0.125,"[1,1,0]"]}'
        table = transform_output(json.loads(test_job_results))
        self.assertEqual(table, json.loads(test_job_results))    # No transform should be done if input param is bad

        # Call with output from a failed job
        test_job_results = \
            '{\
                "beginExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
                "cancellationTime": null,\
                "containerUri": "https://foo...",\
                "costEstimate": null,\
                "creationTime": "2022-02-25T18:56:53.275035+00:00",\
                "endExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
                "errorData": {\
                    "code": "InsufficientResources",\
                    "message": "Too many qubits requested"\
                },\
                "id": "11111111-2222-3333-4444-555555555555",\
                "inputDataFormat": "microsoft.ionq-ir.v2",\
                "inputDataUri": "https://bar...",\
                "inputParams": {\
                    "shots": "500"\
                },\
                "isCancelling": false,\
                "metadata": {\
                    "entryPointInput": {\"Qubits\":null},\
                    "outputMappingBlobUri": "https://baz..."\
                },\
                "name": "",\
                "outputDataFormat": "microsoft.quantum-results.v1",\
                "outputDataUri": "https://quux...",\
                "providerId": "ionq",\
                "status": "Failed",\
                "tags": [],\
                "target": "ionq.simulator"\
            }'

        table = transform_output(json.loads(test_job_results))
        self.assertEqual(table['Status'], "Failed")
        self.assertEqual(table['Error Code'], "InsufficientResources")
        self.assertEqual(table['Error Message'], "Too many qubits requested")
        self.assertEqual(table['Target'], "ionq.simulator")
        self.assertEqual(table['Job ID'], "11111111-2222-3333-4444-555555555555")
        self.assertEqual(table['Submission Time'], "2022-02-25T18:56:53.275035+00:00")

        # Call with missing "status", "code", "message", "target", "id", and "creationTime"
        test_job_results = \
            '{\
                "beginExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
                "cancellationTime": null,\
                "containerUri": "https://foo...",\
                "costEstimate": null,\
                "endExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
                "errorData": {\
                },\
                "inputDataFormat": "microsoft.ionq-ir.v2",\
                "inputDataUri": "https://bar...",\
                "inputParams": {\
                    "shots": "500"\
                },\
                "isCancelling": false,\
                "metadata": {\
                    "entryPointInput": {\"Qubits\":null},\
                    "outputMappingBlobUri": "https://baz..."\
                },\
                "name": "",\
                "outputDataFormat": "microsoft.quantum-results.v1",\
                "outputDataUri": "https://quux...",\
                "providerId": "ionq",\
                "tags": []\
            }'

        table = transform_output(json.loads(test_job_results))
        notFound = "Not found"
        self.assertEqual(table['Status'], notFound)
        self.assertEqual(table['Error Code'], notFound)
        self.assertEqual(table['Error Message'], notFound)
        self.assertEqual(table['Target'], notFound)
        self.assertEqual(table['Job ID'], notFound)
        self.assertEqual(table['Submission Time'], notFound)

    def test_validate_max_poll_wait_secs(self):
        wait_secs = _validate_max_poll_wait_secs(1)
        self.assertEqual(type(wait_secs), float)
        self.assertEqual(wait_secs, 1.0)

        wait_secs = _validate_max_poll_wait_secs("60")
        self.assertEqual(type(wait_secs), float)
        self.assertEqual(wait_secs, 60.0)

        # Invalid values should raise errors
        try:
            wait_secs = _validate_max_poll_wait_secs(0.999999999)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "--max-poll-wait-secs parameter is not valid: 0.999999999"

        try:
            wait_secs = _validate_max_poll_wait_secs(-1.0)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "--max-poll-wait-secs parameter is not valid: -1.0"

        try:
            wait_secs = _validate_max_poll_wait_secs("foobar")
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "--max-poll-wait-secs parameter is not valid: foobar"

    def test_convert_numeric_params(self):
        # Show that it converts numeric strings, but doesn't modify params that are already numeric
        test_job_params = {"integer1": "1", "float1.5": "1.5", "integer2": 2, "float2.5": 2.5, "integer3": "3", "float3.5": "3.5"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"integer1": 1, "float1.5": 1.5, "integer2": 2, "float2.5": 2.5, "integer3": 3, "float3.5": 3.5}

        # Make sure it doesn't modify non-numeric strings
        test_job_params = {"string1": "string_value1", "string2": "string_value2", "string3": "string_value3"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"string1": "string_value1", "string2": "string_value2", "string3": "string_value3"}

        # Make sure it doesn't modify the "tags" list
        test_job_params = {"string1": "string_value1", "tags": ["tag1", "tag2", "3", "4"], "integer1": "1"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"string1": "string_value1", "tags": ["tag1", "tag2", "3", "4"], "integer1": 1}

        # Make sure it doesn't modify nested dict like metadata uses
        test_job_params = {"string1": "string_value1", "metadata": {"meta1": "meta_value1", "meta2": "2"}, "integer1": "1"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"string1": "string_value1", "metadata": {"meta1": "meta_value1", "meta2": "2"}, "integer1": 1}

    @live_only()
    def test_submit(self):
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = self.create_random_name(prefix='e2e-test-w', length=18)
        test_provider_sku_list = "rigetti/azure-basic-qvm-only-unlimited,ionq/aq-internal-testing"
        test_storage = get_test_workspace_storage()
        bell_state_input_file = "src/quantum/azext_quantum/tests/latest/input_data/bell-state.quil"
        qiskit_3_qubit_ghz_circuit_input_file = "src/quantum/azext_quantum/tests/latest/input_data/Qiskit-3-qubit-GHZ-circuit.json"

        try:
            self.cmd(f"az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage} -r {test_provider_sku_list} --skip-autoadd")

            self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp}")

            # Submit a job to Rigetti and look for SAS tokens in URIs in the output
            # Poll while the new workspace's storage role assignment propagates.
            results = self._cmd_with_retry(
                f"az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file {bell_state_input_file} --job-output-format rigetti.quil-results.v1 -o json",
                retry_error_code='StorageAccountInaccessible',
                retries=13,
                delay=10,
            ).get_output_in_json()
            self.assert_not_contains_standard_sas_params(results["containerUri"])
            self.assert_not_contains_standard_sas_params(results["inputDataUri"])
            self.assert_not_contains_standard_sas_params(results["outputDataUri"])

            job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()

            self.assert_contains_standard_sas_params(job["containerUri"])
            self.assert_contains_standard_sas_params(job["inputDataUri"])
            self.assert_contains_standard_sas_params(job["outputDataUri"])

            files = self.cmd(f'az quantum job file list -j {results["id"]} -o json').get_output_in_json()
            self.assertIsInstance(files, list)
            self.assertTrue(files)
            input_file_name = os.path.basename(urlparse(results['inputDataUri']).path)
            listed_file = next(
                (item for item in files if item['name'] == input_file_name),
                None,
            )
            self.assertIsNotNone(listed_file)
            self.assertEqual(set(listed_file.keys()), {'name', 'size', 'lastModified'})
            self.assertGreaterEqual(listed_file['size'], 0)
            if listed_file['lastModified'] is not None:
                datetime.fromisoformat(listed_file['lastModified'].replace('Z', '+00:00'))
            file_name = listed_file['name']
            with tempfile.TemporaryDirectory() as download_dir:
                downloaded = self.cmd(
                    f'az quantum job file download -j {results["id"]} -n {shlex.quote(file_name)} '
                    f'--dest "{download_dir}" -o json'
                ).get_output_in_json()
                self.assertEqual(downloaded['name'], file_name)
                self.assertTrue(os.path.isfile(downloaded['path']))
                self.assertEqual(downloaded['size'], listed_file['size'])
                self.assertEqual(os.path.getsize(downloaded['path']), listed_file['size'])
                with open(bell_state_input_file, 'rb') as expected_file, open(downloaded['path'], 'rb') as actual_file:
                    self.assertEqual(actual_file.read(), expected_file.read())

            # Update the submitted job's name and tags, then confirm both changes were applied.
            updated_job = self.cmd(
                f'az quantum job update -j {results["id"]} --job-name "Updated job name" --job-tags tag1 tag2 -o json'
            ).get_output_in_json()
            self.assertEqual(updated_job["name"], "Updated job name")
            self.assertEqual(updated_job["tags"], ["tag1", "tag2"])

            # Run a Quil pass-through job on Rigetti
            results = self.cmd(f"az quantum run -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file {bell_state_input_file} --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
            self.assertIn("ro", results)

            # Run an IonQ Circuit pass-through job on IonQ
            results = self.cmd(f"az quantum run -t ionq.simulator --shots 100 --job-input-format ionq.circuit.v1 --job-input-file {qiskit_3_qubit_ghz_circuit_input_file} --job-output-format ionq.quantum-results.v1 --job-params shots=100 content-type=application/json -o json").get_output_in_json()
            self.assertIn("histogram", results)

            # Test "az quantum job list" output, for filter-params, --skip, --top, and --orderby
            results = self.cmd("az quantum job list --provider-id rigetti -o json").get_output_in_json()
            self.assertIn("rigetti", str(results))

            results = self.cmd("az quantum job list --target-id ionq.simulator -o json").get_output_in_json()
            self.assertIn("ionq.simulator", str(results))

            jobs_list = self.cmd("az quantum job list --top 1 -o json").get_output_in_json()
            self.assertEqual(len(jobs_list), 1)

            jobs_list = self.cmd("az quantum job list --skip 1 -o json").get_output_in_json()
            self.assertEqual(len(jobs_list), 2)

            jobs_list = self.cmd("az quantum job list --orderby Target --top 1 -o json").get_output_in_json()
            self.assertEqual(len(jobs_list), 1)
            results = str(jobs_list)
            self.assertIn("ionq", results)
            self.assertTrue("rigetti" not in results)

            jobs_list = self.cmd("az quantum job list --orderby Target --skip 1 -o json").get_output_in_json()
            self.assertEqual(len(jobs_list), 2)
            results = str(jobs_list)
            self.assertIn("rigetti", results)
            self.assertTrue("ionq" not in results)

        finally:
            run_cleanup_commands(self, [
                ('temporary workspace',
                 f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp}'),
                ('workspace defaults', 'az quantum workspace clear'),
            ])

    def _test_submit_with_disabled_then_enabled_storage_key_access(self, workspace_kind=None):
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = self.create_random_name(prefix='e2e-test-w', length=18)
        target_id = 'rigetti.sim.qvm'
        job_input_file = "src/quantum/azext_quantum/tests/latest/input_data/bell-state.quil"
        job_input_format = 'rigetti.quil.v1'
        job_output_format = 'rigetti.quil-results.v1'
        workspace_kind_args = ''
        if workspace_kind == 'V2':
            provider_id, target_id, workspace_quota_minutes = \
                self._get_available_v2_simulator_with_quota(test_location)
            test_provider_sku_list = f'{provider_id}/default'
            job_input_file = "src/quantum/azext_quantum/tests/latest/input_data/Program.qs"
            job_input_format = 'qir.v1'
            job_output_format = 'microsoft.quantum-results.v1'
            workspace_kind_args = (
                f'--workspace-kind V2 --quota provider-id={provider_id} target-id={target_id} '
                f'standard-minutes-lifetime={workspace_quota_minutes}'
            )
        else:
            test_provider_sku_list = "rigetti/azure-basic-qvm-only-unlimited"
        test_storage_temp = self.create_random_name(prefix='e2etests', length=24)
        submit_command = (
            f'az quantum job submit -t {target_id} --job-input-format {job_input_format} '
            f'--job-input-file {job_input_file} --job-output-format {job_output_format} '
            '--job-name "Storage authentication E2E" -o json'
        )

        try:
            # Test that create workspace with not existing storage will create storage
            self.cmd(f"az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_temp} -r {test_provider_sku_list} --skip-autoadd {workspace_kind_args}")

            # Verify that access keys are disabled on the newly created storage account
            storage_info = self.cmd(f"az storage account show -g {test_resource_group} -n {test_storage_temp} -o json").get_output_in_json()
            self.assertFalse(storage_info["allowSharedKeyAccess"], "Access keys should be disabled on the newly created storage account for new workspace")

            self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp}")

            # Test that job submission works with disabled access keys on linked storage (/sasUri returns user delegation SAS),
            # polling while the new workspace's storage role assignment propagates.
            results = self._cmd_with_retry(
                submit_command,
                retry_error_code='StorageAccountInaccessible',
                retries=13,
                delay=10,
            ).get_output_in_json()
            self.assertIn("id", results)

            job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
            self.assert_contains_standard_sas_params(job["containerUri"])
            self.assert_contains_standard_sas_params(job["inputDataUri"])
            self.assert_contains_standard_sas_params(job["outputDataUri"])
            self.assert_contains_user_delegation_sas_params(job["containerUri"])
            self.assert_contains_user_delegation_sas_params(job["inputDataUri"])
            self.assert_contains_user_delegation_sas_params(job["outputDataUri"])

            # Enable access keys on this disposable account to verify the legacy service SAS path.
            updated = self.cmd(
                f'az storage account update -g {test_resource_group} -n {test_storage_temp} '
                '--allow-shared-key-access true '
                '--tags "Az.Sec.DisableLocalAuth.Storage::Skip=true" -o json'
            ).get_output_in_json()
            self.assertTrue(updated["allowSharedKeyAccess"], "Access keys should be enabled after update")
            self.assertEqual(updated["tags"]["Az.Sec.DisableLocalAuth.Storage::Skip"], "true")

            time.sleep(300) # wait for the cache to update

            # Test that job submission works with enabled access keys on linked storage (/sasUri returns container-scoped Service SAS)
            results = self.cmd(submit_command).get_output_in_json()
            self.assertIn("id", results)

            job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
            self.assert_contains_standard_sas_params(job["containerUri"])
            self.assert_contains_standard_sas_params(job["inputDataUri"])
            self.assert_contains_standard_sas_params(job["outputDataUri"])
            self.assert_not_contains_user_delegation_sas_params(job["containerUri"])
            self.assert_not_contains_user_delegation_sas_params(job["inputDataUri"])
            self.assert_not_contains_user_delegation_sas_params(job["outputDataUri"])

        finally:
            run_cleanup_commands(self, [
                ('temporary workspace',
                 f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp}'),
                ('temporary storage account',
                 f'az storage account delete -g {test_resource_group} -n {test_storage_temp} --yes'),
                ('workspace defaults', 'az quantum workspace clear'),
            ])

    @live_only()
    def test_submit_with_disabled_then_enabled_storage_key_access(self):
        self._test_submit_with_disabled_then_enabled_storage_key_access()

    @live_only()
    def test_submit_with_disabled_then_enabled_storage_key_access_v2(self):
        self._test_submit_with_disabled_then_enabled_storage_key_access(workspace_kind='V2')

    def test_job_list_param_formating(self):
        # Validate filter query formatting for each param
        #
        # Should return None if params are set to None
        job_type = None
        item_type = None
        provider_id = None
        target_id = None
        job_status = None
        created_after = None
        created_before = None
        job_name = None
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query is None

        job_type = "QuantumComputing"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "JobType eq 'QuantumComputing'"
        job_type = None

        item_type = "job"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "ItemType eq 'job'"
        item_type = None

        provider_id = "Microsoft"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "ProviderId eq 'Microsoft'"
        provider_id = None

        target_id = "Awesome.Quantum.SuperComputer"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "Target eq 'Awesome.Quantum.SuperComputer'"
        target_id = None

        job_status = "Succeeded"        
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "State eq 'Succeeded'"
        job_status = None        

        created_after = "2025-01-27"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "CreationTime ge 2025-01-27"
        created_after = None

        created_before = "2025-01-27"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "CreationTime le 2025-01-27"
        created_before = None

        job_name = "TestJob"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "startswith(Name, 'TestJob')"
        job_name = None


        # Validate orderby expression formatting
        # Should return None if params are set to None
        orderby = None
        order = None
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression is None

        # Test valid params
        orderby = "Target"
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression == "Target"

        order = "asc"
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression == "Target asc"

        order = "desc"
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression == "Target desc"

        # Test orderby/order errors
        orderby = "Target"
        order = "foo"
        try:
            orderby_expression = _construct_orderby_expression(orderby, order)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == ERROR_MSG_INVALID_ORDER_ARGUMENT

        orderby = ""
        order = "desc"
        try:
            orderby_expression = _construct_orderby_expression(orderby, order)
            assert False
        except RequiredArgumentMissingError as e:
            assert str(e) == ERROR_MSG_MISSING_ORDERBY_ARGUMENT

    def assert_contains_user_delegation_sas_params(self, uri: str):
        """Assert that the given URI contains user delegation SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertIn("skoid", params)   # signed key object ID (service principal OID)
        self.assertIn("sktid", params)   # signed key tenant ID
        self.assertIn("skt", params)     # signed key start time
        self.assertIn("ske", params)     # signed key expiry time
        self.assertIn("sks", params)     # signed key service (b = Blob)
        self.assertIn("skv", params)     # signed key version

    def assert_not_contains_user_delegation_sas_params(self, uri: str):
        """Assert that the given URI does not contain user delegation SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertNotIn("skoid", params)
        self.assertNotIn("sktid", params)
        self.assertNotIn("skt", params)
        self.assertNotIn("ske", params)
        self.assertNotIn("sks", params)
        self.assertNotIn("skv", params)

    def assert_contains_standard_sas_params(self, uri: str):
        """Assert that the given URI contains standard SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertIn("sv", params)    # SAS version
        self.assertIn("st", params)    # start time
        self.assertIn("se", params)    # expiry time
        self.assertIn("sr", params)    # signed resource (e.g. c = container)
        self.assertIn("sp", params)    # permissions
        self.assertIn("sig", params)   # signature

    def assert_not_contains_standard_sas_params(self, uri: str):
        """Assert that the given URI does not contain standard SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertNotIn("sv", params)
        self.assertNotIn("st", params)
        self.assertNotIn("se", params)
        self.assertNotIn("sr", params)
        self.assertNotIn("sp", params)
        self.assertNotIn("sig", params)
