# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qsl, urlsplit

from azure.cli.core import MainCommandsLoader, get_default_cli
from azure.cli.core.commands import ExtensionCommandSource
from azext_horizondb import HorizonDBCommandsLoader

from .recording_processors import ArmOperationResultsRecordingProcessor


class _MaintenanceEventCommandsLoader(MainCommandsLoader):

    def load_command_table(self, args):
        loader = HorizonDBCommandsLoader(cli_ctx=self.cli_ctx)
        self.command_table.update(loader.load_command_table(args))
        self.command_group_table.update(loader.command_group_table)
        self.loaders.append(loader)
        for name, command in self.command_table.items():
            self.cmd_to_loader_map[name] = [loader]
            command.command_source = ExtensionCommandSource(
                extension_name='horizondb',
                overrides_command=False,
                preview=True,
                experimental=False,
            )
        return self.command_table


class MaintenanceEventTests(TestCase):

    def setUp(self):
        self.cli_ctx = get_default_cli()
        self.cli_ctx.commands_loader_cls = _MaintenanceEventCommandsLoader
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Unit tests must not use Azure credentials or HTTP clients.'),
        )
        self.http_client = http_client.start()
        self.addCleanup(http_client.stop)
        request = patch(
            'requests.sessions.Session.request',
            side_effect=AssertionError('Unit tests must not send network requests.'),
        )
        self.request = request.start()
        self.addCleanup(request.stop)

    def _invoke_cli(self, *args):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                exit_code = self.cli_ctx.invoke(
                    ['horizondb', 'cluster', 'pool', 'maintenance-event', *args],
                    out_file=stdout,
                )
            except SystemExit as error:
                exit_code = error.code
        self.assertEqual(exit_code, 0, stderr.getvalue())
        self.http_client.assert_not_called()
        self.request.assert_not_called()
        return stdout.getvalue()

    def test_registered_list_returns_policy_without_http(self):
        expected = (
            'Maintenance updates are managed by the system. '
            'Currently, HorizonDB supports System-Managed Maintenance Window.'
        )
        for output_format in ['json', 'tsv']:
            with self.subTest(output_format=output_format):
                output = self._invoke_cli(
                    'list',
                    '--resource-group', 'test-rg',
                    '--cluster-name', 'test-cluster',
                    '--pool-name', 'test-pool',
                    '--subscription', '00000000-0000-0000-0000-000000000001',
                    '--output', output_format,
                )
                result = json.loads(output) if output_format == 'json' else output.strip()
                self.assertEqual(result, expected)

    def test_list_help_hides_filtering_and_pagination(self):
        help_text = self._invoke_cli('list', '--help')
        for option in ['--filter', '--max-items', '--next-token']:
            with self.subTest(option=option):
                self.assertNotIn(option, help_text)

    def test_group_help_hides_show_command(self):
        help_text = self._invoke_cli('--help')
        self.assertRegex(help_text, r'(?m)^\s+list\b')
        self.assertNotRegex(help_text, r'(?m)^\s+show\b')


class ArmOperationResultsRecordingProcessorTests(TestCase):

    def setUp(self):
        self.processor = ArmOperationResultsRecordingProcessor()
        self.uri = (
            'https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000/'
            'operationresults/private-rg-job?api-version=2024-11-01'
            '&t=fake-timestamp&c=fake-certificate&s=fake-signature&h=fake-hash'
        )

    def test_operation_result_requests_remove_signed_data(self):
        request = SimpleNamespace(uri=self.uri)
        self.processor.process_request(request)
        parsed = urlsplit(request.uri)
        self.assertNotIn('private-rg-job', parsed.path)
        self.assertEqual(dict(parse_qsl(parsed.query)), {'api-version': '2024-11-01'})
        sanitized_uri = request.uri
        self.processor.process_request(request)
        self.assertEqual(request.uri, sanitized_uri)

        other = SimpleNamespace(uri=self.uri.replace('private-rg-job', 'other-rg-job'))
        self.processor.process_request(other)
        self.assertNotEqual(other.uri, sanitized_uri)

    def test_operation_result_response_headers_match_scrubbed_requests(self):
        request = SimpleNamespace(uri=self.uri)
        self.processor.process_request(request)
        ordinary_uri = 'https://management.azure.com/resourcegroups/test-rg?api-version=2024-11-01'
        for header in ['Location', 'Azure-AsyncOperation', 'Operation-Location']:
            with self.subTest(header=header):
                response = {'headers': {header: [self.uri, ordinary_uri]}}
                self.processor.process_response(response)
                self.assertEqual(response['headers'][header], [request.uri, ordinary_uri])
