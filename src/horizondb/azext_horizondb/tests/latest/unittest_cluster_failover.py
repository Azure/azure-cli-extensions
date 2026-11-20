# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from argparse import ArgumentParser
from contextlib import redirect_stderr
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.cli.core import get_default_cli
from azure.cli.core.aaz._client import AAZMgmtClient
from azure.cli.core.azclierror import InvalidArgumentValueError
from requests.structures import CaseInsensitiveDict

from azext_horizondb import HorizonDBCommandsLoader
from azext_horizondb.aaz.latest.horizondb.cluster._failover import Failover

from . import test_horizondb_cluster as cluster_scenarios


class FailoverResponse(HttpResponse):

    def __init__(self, request, status_code, body, headers):
        super().__init__(request, None)
        self.status_code = status_code
        self.headers = CaseInsensitiveDict(headers or {})
        self.headers['Content-Type'] = 'application/json'
        self.content_type = 'application/json'
        self.reason = 'Conflict' if status_code == 409 else 'OK'
        self._body = json.dumps(body).encode() if body is not None else b''

    def body(self):
        return self._body


class ClusterFailoverTests(TestCase):

    def setUp(self):
        self.cli_ctx = get_default_cli()
        self.args = {
            'subscription': '00000000-0000-0000-0000-000000000001',
            'resource_group': 'test-rg',
            'cluster_name': 'test-cluster',
        }
        self.cluster_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test-rg'
            '/providers/Microsoft.HorizonDb/clusters/test-cluster'
        )
        self.cluster = {
            'id': self.cluster_id,
            'name': 'test-cluster',
            'type': 'Microsoft.HorizonDb/clusters',
            'location': 'eastus2',
            'properties': {
                'state': 'Ready',
                'provisioningState': 'Succeeded',
                'readWritePool': {'designatedPoolResourceId': self.cluster_id + '/pools/primary'},
            },
        }
        self.status_url = 'https://management.azure.com' + self.cluster_id + '/operationStatuses/test-operation'
        self.result_url = 'https://management.azure.com' + self.cluster_id + '/operationResults/test-operation'
        self.accepted_headers = {
            'Azure-AsyncOperation': self.status_url,
            'Location': self.result_url,
            'Retry-After': '0',
        }
        self.responses = []
        self.requests = []
        self.transport = Mock(spec=HttpTransport)
        self.transport.send.side_effect = self.send
        credential = Mock(spec=['get_token'])
        credential.get_token.return_value = AccessToken('offline-test-token', 4102444800)

        def get_http_client(ctx, client_type):
            self.assertEqual(client_type, 'MgmtClient')
            return AAZMgmtClient(ctx, credential, retry_total=0,
                                 logging_policy=SansIOHTTPPolicy())

        for target, kwargs in [
                ('azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
                 {'autospec': True, 'side_effect': get_http_client}),
                ('azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_login_credential',
                 {'side_effect': AssertionError('Failover tests must not use Azure credentials.')}),
                ('azure.core.pipeline.transport._requests_basic.RequestsTransport',
                 {'return_value': self.transport}),
                ('requests.sessions.Session.request',
                 {'side_effect': AssertionError('Failover tests must not make network requests.')})]:
            patcher = patch(target, **kwargs)
            patcher.start()
            self.addCleanup(patcher.stop)

    def send(self, request, **_kwargs):
        self.requests.append(request)
        self.assertTrue(self.responses, 'Unexpected HTTP request: ' + request.url)
        status_code, body, headers = self.responses.pop(0)
        return FailoverResponse(request, status_code, body, headers)

    def invoke(self, **changes):
        result = Failover(cli_ctx=self.cli_ctx)(command_args=dict(self.args, **changes))
        return result.result() if result is not None else None

    def test_registered_name_aliases_send_bodyless_failover_request(self):
        loader = HorizonDBCommandsLoader(cli_ctx=self.cli_ctx)
        command = loader.load_command_table(['horizondb', 'cluster', 'failover'])['horizondb cluster failover']
        self.assertIsInstance(command, Failover)
        command.load_arguments()
        parser = ArgumentParser()
        for name, argument in command.arguments.items():
            settings = argument.type.settings
            parser.add_argument(*settings['options_list'], dest=name, **{
                key: settings[key] for key in ['action', 'nargs', 'const'] if key in settings
            })

        for option in ['--name', '-n', '--cluster-name']:
            with self.subTest(option=option):
                args = vars(parser.parse_args([option, 'test-cluster', '-g', 'test-rg', '--no-wait']))
                self.responses = [(202, None, self.accepted_headers)]
                self.assertIsNone(self.invoke(**args))
                request = self.requests[-1]
                self.assertEqual(request.method, 'POST')
                self.assertEqual(request.url, 'https://management.azure.com' + self.cluster_id +
                                 '/failover?api-version=2026-10-01-preview')
                self.assertIsNone(request.body)

        for option in ['--pool-name', '--target-node', '--availability-zone', '--mode', '--yes']:
            with self.subTest(option=option), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit):
                    parser.parse_args([option, 'unsupported'])

    def test_invalid_or_missing_selectors_fail_before_http(self):
        for cluster_name in ['', '-cluster', 'cluster-', 'Cluster', 'bad.name', 'a' * 64]:
            with self.subTest(cluster_name=cluster_name):
                with self.assertRaises(InvalidArgumentValueError):
                    self.invoke(cluster_name=cluster_name)
        for argument in ['cluster_name', 'resource_group']:
            with self.subTest(missing=argument):
                args = dict(self.args)
                del args[argument]
                with self.assertRaises(InvalidArgumentValueError):
                    Failover(cli_ctx=self.cli_ctx)(command_args=args)
        self.assertEqual(self.requests, [])

    def test_cli_resource_id_and_explicit_subscription_selectors(self):
        subscription = {
            'id': self.args['subscription'],
            'name': 'Offline test subscription',
            'tenantId': '00000000-0000-0000-0000-000000000002',
            'isDefault': True,
            'state': 'Enabled',
        }
        for selectors in [
                ['--ids', self.cluster_id],
                ['--subscription', self.args['subscription'], '-g', 'test-rg', '-n', 'test-cluster']]:
            with self.subTest(selectors=selectors), patch(
                    'azure.cli.core._profile.Profile.get_subscription', return_value=subscription):
                self.responses = [(202, None, self.accepted_headers)]
                output = StringIO()
                self.assertEqual(self.cli_ctx.invoke(
                    ['horizondb', 'cluster', 'failover', *selectors, '--no-wait'],
                    out_file=output,
                ), 0)
                self.assertEqual(output.getvalue().strip(), '')
                self.assertEqual(self.requests[-1].url, 'https://management.azure.com' + self.cluster_id +
                                 '/failover?api-version=2026-10-01-preview')
                self.assertEqual(self.responses, [])

    def test_missing_playback_recording_fails_before_resource_preparation(self):
        scenario = cluster_scenarios.HorizonDBClusterFailoverScenarioTest('test_horizondb_cluster_failover')
        scenario.in_recording = True
        scenario.is_live = False
        with patch('azure.cli.testsdk.scenario_tests.base.ReplayableTest.setUp') as prepare:
            with self.assertRaisesRegex(AssertionError, 'Failover playback recording is missing'):
                scenario.setUp()
            prepare.assert_not_called()

    def test_cluster_name_boundaries_are_accepted(self):
        for cluster_name in ['a', '9', 'a' * 63]:
            with self.subTest(cluster_name=cluster_name):
                self.responses = [(202, None, self.accepted_headers)]
                self.assertIsNone(self.invoke(cluster_name=cluster_name, no_wait=True))
                self.assertIn('/clusters/' + cluster_name + '/failover?', self.requests[-1].url)

    def test_immediate_completion_returns_cluster(self):
        self.responses = [(200, self.cluster, {})]
        self.assertEqual(self.invoke(), self.cluster)
        self.assertEqual(len(self.requests), 1)

    def test_waits_for_async_operation_and_returns_location_result(self):
        self.responses = [
            (202, None, self.accepted_headers),
            (200, {'status': 'InProgress'}, {'Retry-After': '0'}),
            (200, {'status': 'Succeeded'}, {}),
            (200, self.cluster, {}),
        ]
        self.assertEqual(self.invoke(), self.cluster)
        self.assertEqual([(request.method, request.url) for request in self.requests[1:]], [
            ('GET', self.status_url), ('GET', self.status_url), ('GET', self.result_url),
        ])
        self.assertEqual(self.responses, [])

    def test_waits_using_location_when_async_operation_header_is_absent(self):
        self.responses = [
            (202, None, {'Location': self.result_url, 'Retry-After': '0'}),
            (202, None, {'Retry-After': '0'}),
            (200, self.cluster, {}),
        ]
        self.assertEqual(self.invoke(), self.cluster)
        self.assertEqual([request.url for request in self.requests[1:]], [self.result_url, self.result_url])

    def test_no_wait_returns_after_acceptance_without_polling(self):
        self.responses = [(202, None, self.accepted_headers)]
        self.assertIsNone(self.invoke(no_wait=True))
        self.assertEqual(len(self.requests), 1)

    def test_service_conflict_is_not_replaced_by_client_eligibility_checks(self):
        message = 'The designated pool is not eligible for failover or a conflicting operation is in progress.'
        self.responses = [(409, {'error': {'code': 'Conflict', 'message': message}}, {})]
        with self.assertRaisesRegex(HttpResponseError, message) as error:
            self.invoke()
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual([request.method for request in self.requests], ['POST'])

    def test_polling_and_final_result_errors_propagate(self):
        error = {'code': 'FailoverFailed', 'message': 'Failover could not complete.'}
        for responses in [
                [(200, {'status': 'Failed', 'error': error}, {})],
                [(200, {'status': 'Succeeded'}, {}), (500, {'error': error}, {})]]:
            with self.subTest(responses=responses):
                self.responses = [(202, None, self.accepted_headers)] + responses
                with self.assertRaisesRegex(HttpResponseError, 'Failover could not complete'):
                    self.invoke()
