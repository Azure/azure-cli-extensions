# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from azure.core import PipelineClient
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.cli.core import get_default_cli
from azext_horizondb import HorizonDBCommandsLoader


class DefaultParameterGroupTests(TestCase):

    def setUp(self):
        self.loader = HorizonDBCommandsLoader(cli_ctx=get_default_cli())
        self.commands = self.loader.load_command_table(None)
        self.args = {
            'subscription': '00000000-0000-0000-0000-000000000001',
            'location': 'eastus2',
        }
        self.path = (
            '/subscriptions/' + self.args['subscription'] +
            '/providers/Microsoft.HorizonDb/locations/eastus2/parameterGroups'
        )
        self.client = PipelineClient(base_url='https://management.azure.com')
        self.addCleanup(self.client.close)
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            return_value=self.client,
        )
        http_client.start()
        self.addCleanup(http_client.stop)
        send_request = patch.object(self.client, 'send_request')
        self.send_request = send_request.start()
        self.addCleanup(send_request.stop)

    @staticmethod
    def _group(version):
        return {
            'name': 'default-postgresql-' + version + '-provisioned',
            'type': 'Microsoft.HorizonDb/locations/parameterGroups',
            'properties': {
                'postgreSqlVersion': version,
                'description': 'Engine defaults',
                'provisioningState': 'Succeeded',
                'parameters': [{
                    'name': 'work_mem',
                    'value': '4096',
                    'defaultValue': '4096',
                    'allowedValues': '64-2147483647',
                    'dataType': 'Integer',
                    'description': 'Sets the maximum memory for query workspaces.',
                    'documentationLink': 'https://www.postgresql.org/docs/current/runtime-config-resource.html',
                    'isDynamic': True,
                    'isReadOnly': False,
                    'unit': 'kB',
                    'valueSource': 'EngineDefault',
                }],
            },
        }

    @staticmethod
    def _response(body):
        return SimpleNamespace(
            http_response=SimpleNamespace(status_code=200),
            context={ContentDecodePolicy.CONTEXT_NAME: body},
        )

    def test_list_requests_regional_defaults_and_follows_next_link(self):
        groups = [self._group('17'), self._group('18')]
        next_link = 'https://management.azure.com' + self.path + '?api-version=2026-10-01-preview&$skiptoken=page2'
        self.send_request.side_effect = [
            self._response({'value': groups[:1], 'nextLink': next_link}),
            self._response({'value': groups[1:]}),
        ]

        command = self.commands['horizondb parameter-group default list']
        result = list(command(command_args=self.args))

        self.assertEqual(result, groups)
        self.assertEqual(self.send_request.call_count, 2)
        for index, call in enumerate(self.send_request.call_args_list):
            request = call.kwargs['request']
            url = urlparse(request.url)
            self.assertEqual(request.method, 'GET')
            self.assertEqual(url.path, self.path)
            expected_query = {'api-version': ['2026-10-01-preview']}
            if index:
                expected_query['$skiptoken'] = ['page2']
            self.assertEqual(parse_qs(url.query), expected_query)

    def test_list_returns_empty_collection(self):
        self.send_request.return_value = self._response({'value': []})

        command = self.commands['horizondb parameter-group default list']

        self.assertEqual(list(command(command_args=self.args)), [])
        self.send_request.assert_called_once()

    def test_show_requests_named_default_and_preserves_parameter_metadata(self):
        group = self._group('17')
        self.send_request.return_value = self._response(group)

        command = self.commands['horizondb parameter-group default show']
        result = command(command_args=dict(self.args, name=group['name']))

        self.assertEqual(result, group)
        self.send_request.assert_called_once()
        request = self.send_request.call_args.kwargs['request']
        url = urlparse(request.url)
        self.assertEqual(request.method, 'GET')
        self.assertEqual(url.path, self.path + '/' + group['name'])
        self.assertEqual(parse_qs(url.query), {'api-version': ['2026-10-01-preview']})
