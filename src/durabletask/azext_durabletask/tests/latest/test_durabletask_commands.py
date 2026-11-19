# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.parse import urlunsplit

from requests.structures import CaseInsensitiveDict

from azure.cli.core.aaz._client import AAZMgmtClient
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.azclierror import ValidationError
from azure.cli.testsdk.base import execute, get_dummy_cli
from azure.cli.testsdk.patches import patch_load_cached_subscriptions, patch_main_exception_handler
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.pipeline.policies import ContentDecodePolicy, NetworkTraceLoggingPolicy
from azure.core.pipeline.transport import HttpResponse

from azext_durabletask import _scheduler


SUBSCRIPTION = '00000000-0000-0000-0000-000000000000'
SCHEDULER_PATH = (
    f'/subscriptions/{SUBSCRIPTION}/resourceGroups/test-rg'
    '/providers/Microsoft.DurableTask/schedulers/test-scheduler'
)
IDENTITY_ID = (
    f'/subscriptions/{SUBSCRIPTION}/resourceGroups/test-rg'
    '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-identity'
)
PARTNER_ID = SCHEDULER_PATH.replace('test-scheduler', 'test-partner')
KEY_URI = 'https://test-vault.vault.azure.net/keys/test-key/test-version'


class _Response(HttpResponse):
    def __init__(self, request, status, data, headers):
        super().__init__(request, None)
        self.status_code = status
        self.headers = CaseInsensitiveDict({'Content-Type': 'application/json', **headers})
        self.reason = 'test response'
        self._body = json.dumps(data).encode('utf-8') if data is not None else b''

    def body(self):
        return self._body


class DurabletaskCommandTests(unittest.TestCase):
    """Run CLI parsing and AAZ operations with mocked HTTP pipeline responses."""

    def setUp(self):
        self.cli_ctx = get_dummy_cli()
        patch_load_cached_subscriptions(self)
        patch_main_exception_handler(self)
        self.client = AAZMgmtClient(
            SimpleNamespace(cli_ctx=self.cli_ctx), credential=Mock(),
            logging_policy=NetworkTraceLoggingPolicy())
        self.responses = []
        self.requests = []
        for patcher in (
            patch.object(AAZCommandCtx, 'get_http_client', return_value=self.client),
            patch.object(self.client._pipeline, 'run', side_effect=self._send_request),
            patch('requests.sessions.Session.request', side_effect=AssertionError('Unexpected network request')),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def _send_request(self, request, **_):
        self.assertTrue(self.responses, f'Unexpected HTTP request: {request.method} {request.url}')
        request.headers.setdefault('x-ms-client-request-id', SUBSCRIPTION)
        self.requests.append(request)
        status, data, headers = self.responses.pop(0)
        response = _Response(request, status, data, headers)
        context = PipelineContext(None)
        context[ContentDecodePolicy.CONTEXT_NAME] = copy.deepcopy(data)
        return PipelineResponse(request, response, context)

    def _cmd(self, command, *responses):
        self.responses = [
            (response[0], response[1], response[2] if len(response) == 3 else {})
            for response in responses
        ]
        self.requests = []
        result = execute(self.cli_ctx, f'{command} --subscription {SUBSCRIPTION}')
        self.assertFalse(self.responses, 'The command did not consume all expected HTTP responses')
        return result

    def _assert_request(self, index, method, path, body=None, api_version='2026-07-01-preview'):
        request = self.requests[index]
        self.assertEqual(request.method, method)
        expected_url = urlunsplit(('https', 'management.azure.com', path, f'api-version={api_version}', ''))
        self.assertEqual(request.url, expected_url)
        if body is not None:
            self.assertEqual(json.loads(request.body), body)

    @staticmethod
    def _scheduler(capacity=0, **kwargs):
        return {
            'id': SCHEDULER_PATH,
            'name': 'test-scheduler',
            'type': 'Microsoft.DurableTask/schedulers',
            'location': 'eastus',
            'tags': {'purpose': 'test'},
            'properties': {
                'provisioningState': 'Succeeded',
                'endpoint': 'https://test-scheduler.durabletask.io',
                'sku': {'name': 'Consumption', 'capacity': capacity},
                'ipAllowlist': [],
                'publicNetworkAccess': 'Enabled',
            },
            **kwargs,
        }

    @staticmethod
    def _child(path, **properties):
        return {
            'id': SCHEDULER_PATH + path,
            'name': path.rsplit('/', 1)[-1],
            'properties': {'provisioningState': 'Succeeded', **properties},
        }

    def test_durabletask_scheduler_lifecycle(self):
        scheduler = self._scheduler()
        result = self._cmd(
            'az durabletask scheduler create -g test-rg -n test-scheduler -l eastus '
            '--sku-name Consumption --public-network-access Enabled --tags purpose=test',
            (201, scheduler))
        self.assertEqual(result.get_output_in_json()['name'], 'test-scheduler')
        self._assert_request(0, 'PUT', SCHEDULER_PATH, {
            'location': 'eastus', 'tags': {'purpose': 'test'},
            'properties': {
                'sku': {'name': 'Consumption'}, 'ipAllowlist': [], 'publicNetworkAccess': 'Enabled',
            },
        }, api_version='2026-02-01')

        self._cmd('az durabletask scheduler show -g test-rg -n test-scheduler', (200, scheduler))
        self._assert_request(0, 'GET', SCHEDULER_PATH, api_version='2026-02-01')
        result = self._cmd('az durabletask scheduler list -g test-rg', (200, {'value': [scheduler]}))
        self.assertEqual(result.get_output_in_json(), [dict(scheduler, resourceGroup='test-rg')])
        self._assert_request(0, 'GET', SCHEDULER_PATH.rsplit('/', 1)[0], api_version='2026-02-01')
        self._cmd('az durabletask scheduler list', (200, {'value': [scheduler]}))
        self._assert_request(
            0, 'GET', f'/subscriptions/{SUBSCRIPTION}/providers/Microsoft.DurableTask/schedulers',
            api_version='2026-02-01')

        updated = copy.deepcopy(scheduler)
        updated['tags'] = {'purpose': 'updated'}
        updated['properties']['ipAllowlist'] = ['10.0.0.0/24']
        result = self._cmd(
            'az durabletask scheduler update -g test-rg -n test-scheduler '
            '--tags purpose=updated --ip-allowlist 10.0.0.0/24',
            (200, scheduler), (200, updated))
        self.assertEqual(result.get_output_in_json()['tags'], {'purpose': 'updated'})
        self.assertEqual(len(self.requests), 2)
        self._assert_request(0, 'GET', SCHEDULER_PATH, api_version='2026-02-01')
        self._assert_request(1, 'PUT', SCHEDULER_PATH, {
            'location': 'eastus', 'tags': {'purpose': 'updated'},
            'properties': {
                'sku': {'name': 'Consumption'}, 'ipAllowlist': ['10.0.0.0/24'],
                'publicNetworkAccess': 'Enabled',
            },
        }, api_version='2026-02-01')
        self._cmd('az durabletask scheduler delete -g test-rg -n test-scheduler --yes', (204, None))
        self._assert_request(0, 'DELETE', SCHEDULER_PATH, api_version='2026-02-01')

    def test_durabletask_scheduler_sku_validation(self):
        for arguments, message in (
            ('', 'The --sku-name parameter is required'),
            ('--sku-name Dedicated', 'The --sku-capacity parameter is required'),
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValidationError, message):
                    self._cmd(
                        'az durabletask scheduler create -g test-rg -n test-scheduler -l eastus '
                        + arguments)
                self.assertFalse(self.requests)

        scheduler = self._scheduler(capacity=2)
        scheduler['properties']['sku']['name'] = 'Dedicated'
        self._cmd(
            'az durabletask scheduler create -g test-rg -n test-scheduler -l eastus '
            '--sku-name Dedicated --sku-capacity 2', (200, scheduler))
        self.assertEqual(json.loads(self.requests[0].body)['properties']['sku'],
                         {'name': 'Dedicated', 'capacity': 2})

    def test_durabletask_scheduler_update_capacity_boundaries(self):
        for capacity in (None, 0, 2):
            with self.subTest(capacity=capacity):
                scheduler = self._scheduler(capacity=capacity)
                if capacity == 2:
                    scheduler['properties']['sku']['name'] = 'Dedicated'
                self._cmd(
                    'az durabletask scheduler update -g test-rg -n test-scheduler --tags purpose=test',
                    (200, scheduler), (200, scheduler))
                sku = json.loads(self.requests[1].body)['properties']['sku']
                self.assertEqual(sku, {'name': 'Dedicated', 'capacity': 2} if capacity == 2
                                 else {'name': 'Consumption'})

    def test_durabletask_identity_lifecycle(self):
        scheduler = self._scheduler(identity={'type': 'None'})
        assigned = self._scheduler(identity={
            'type': 'UserAssigned', 'userAssignedIdentities': {IDENTITY_ID: {
                'principalId': 'test-principal', 'clientId': 'test-client',
            }},
        })
        result = self._cmd(
            f'az durabletask scheduler identity assign -g test-rg -n test-scheduler '
            f'--user-assigned {IDENTITY_ID}', (200, scheduler), (200, assigned))
        self.assertEqual(result.get_output_in_json()['type'], 'UserAssigned')
        body = json.loads(self.requests[1].body)
        self.assertEqual(body['identity'], {
            'type': 'UserAssigned', 'userAssignedIdentities': {IDENTITY_ID: {}},
        })
        self.assertNotIn('capacity', body['properties']['sku'])
        result = self._cmd(
            'az durabletask scheduler identity show -g test-rg -n test-scheduler', (200, assigned))
        self.assertEqual(result.get_output_in_json(), assigned['identity'])
        self._cmd(
            f'az durabletask scheduler identity remove -g test-rg -n test-scheduler '
            f'--mi-user-assigned {IDENTITY_ID}', (200, assigned), (200, scheduler))
        body = json.loads(self.requests[1].body)
        self.assertEqual(body['identity']['type'], 'None')
        self.assertNotIn('capacity', body['properties']['sku'])

    def test_durabletask_identity_selective_removal(self):
        other_id = IDENTITY_ID.replace('test-identity', 'other-identity')
        existing_ids = {IDENTITY_ID.lower(): {}, other_id.lower(): {}}
        for arguments, identity_type, expected in (
            (f'--user-assigned {IDENTITY_ID}', 'UserAssigned', {
                'type': 'UserAssigned', 'userAssignedIdentities': {other_id.lower(): {}},
            }),
            (f'--mi-user-assigned {IDENTITY_ID.upper()} {other_id}', 'UserAssigned', {'type': 'None'}),
            (f'--user-assigned {IDENTITY_ID}', 'SystemAssigned,UserAssigned', {
                'type': 'SystemAssigned,UserAssigned', 'userAssignedIdentities': {other_id.lower(): {}},
            }),
            ('--user-assigned', 'SystemAssigned,UserAssigned', {'type': 'SystemAssigned'}),
            (f'--user-assigned {IDENTITY_ID}-missing', 'UserAssigned', {
                'type': 'UserAssigned', 'userAssignedIdentities': existing_ids,
            }),
            ('', 'UserAssigned', {'type': 'UserAssigned', 'userAssignedIdentities': existing_ids}),
        ):
            with self.subTest(arguments=arguments, identity_type=identity_type):
                scheduler = self._scheduler(identity={
                    'type': identity_type, 'userAssignedIdentities': copy.deepcopy(existing_ids),
                })
                updated = self._scheduler(identity=expected)
                self._cmd(
                    'az durabletask scheduler identity remove -g test-rg -n test-scheduler ' + arguments,
                    (200, scheduler), (200, updated))
                body = json.loads(self.requests[1].body)
                self.assertEqual(body['identity'], expected)
                self.assertNotIn('capacity', body['properties']['sku'])

    def test_durabletask_taskhub_lifecycle(self):
        path = SCHEDULER_PATH + '/taskHubs/test-hub'
        hub = self._child('/taskHubs/test-hub')
        self._cmd(
            'az durabletask taskhub create -g test-rg -s test-scheduler -n test-hub', (201, hub))
        self._assert_request(0, 'PUT', path, {})
        result = self._cmd(
            'az durabletask taskhub show -g test-rg -s test-scheduler -n test-hub', (200, hub))
        self.assertEqual(result.get_output_in_json()['properties']['provisioningState'], 'Succeeded')
        self._assert_request(0, 'GET', path)
        result = self._cmd(
            'az durabletask taskhub list -g test-rg -s test-scheduler', (200, {'value': [hub]}))
        self.assertEqual(result.get_output_in_json(), [dict(hub, resourceGroup='test-rg')])
        self._assert_request(0, 'GET', path.rsplit('/', 1)[0])
        self._cmd(
            'az durabletask taskhub delete -g test-rg -s test-scheduler -n test-hub --yes',
            (204, None))
        self._assert_request(0, 'DELETE', path)

    def test_durabletask_taskqueue_lifecycle(self):
        path = SCHEDULER_PATH + '/taskHubs/test-hub/taskQueues/test-queue'
        queue = self._child('/taskHubs/test-hub/taskQueues/test-queue',
                            throughput={'actionsPerSecond': 100})
        result = self._cmd(
            'az durabletask taskqueue create -g test-rg -s test-scheduler -t test-hub '
            '-n test-queue --actions-per-second 100', (201, queue))
        self.assertEqual(result.get_output_in_json()['properties']['throughput']['actionsPerSecond'], 100)
        self._assert_request(0, 'PUT', path, {'properties': {'throughput': {'actionsPerSecond': 100}}})
        self._cmd(
            'az durabletask taskqueue show -g test-rg -s test-scheduler -t test-hub -n test-queue',
            (200, queue))
        self._assert_request(0, 'GET', path)
        result = self._cmd(
            'az durabletask taskqueue list -g test-rg -s test-scheduler -t test-hub',
            (200, {'value': [queue]}))
        self.assertEqual(result.get_output_in_json(), [dict(queue, resourceGroup='test-rg')])
        self._assert_request(0, 'GET', path.rsplit('/', 1)[0])
        updated = copy.deepcopy(queue)
        updated['properties']['throughput']['actionsPerSecond'] = 200
        self._cmd(
            'az durabletask taskqueue update -g test-rg -s test-scheduler -t test-hub '
            '--taskqueue-name test-queue --actions-per-second 200', (200, queue), (200, updated))
        self._assert_request(0, 'GET', path)
        self._assert_request(1, 'PUT', path, {'properties': {'throughput': {'actionsPerSecond': 200}}})
        self._cmd(
            'az durabletask taskqueue delete -g test-rg -s test-scheduler -t test-hub '
            '-n test-queue --yes', (204, None))
        self._assert_request(0, 'DELETE', path)

    def test_durabletask_taskqueue_throughput_boundaries(self):
        path = SCHEDULER_PATH + '/taskHubs/test-hub/taskQueues/test-queue'
        queue = self._child('/taskHubs/test-hub/taskQueues/test-queue',
                            throughput={'actionsPerSecond': 100})
        for argument, value in (('', 100), ('--actions-per-second 0', 0),
                                ('--actions-per-second null', None)):
            with self.subTest(argument=argument):
                self._cmd(
                    'az durabletask taskqueue update -g test-rg -s test-scheduler -t test-hub '
                    '-n test-queue ' + argument, (200, queue), (200, queue))
                self._assert_request(1, 'PUT', path, {
                    'properties': {'throughput': {'actionsPerSecond': value} if value is not None else {}},
                })

    def test_durabletask_taskqueue_async_create(self):
        queue = self._child('/taskHubs/test-hub/taskQueues/test-queue',
                            throughput={'actionsPerSecond': 100})
        pending = copy.deepcopy(queue)
        pending['properties']['provisioningState'] = 'Creating'
        operation_url = 'https://management.azure.com' + SCHEDULER_PATH + '/operationStatuses/test-operation'
        result = self._cmd(
            'az durabletask taskqueue create -g test-rg -s test-scheduler -t test-hub '
            '-n test-queue --actions-per-second 100',
            (202, pending, {'Azure-AsyncOperation': operation_url, 'Retry-After': '0'}),
            (200, {'status': 'Succeeded'}), (200, queue))
        self.assertEqual(result.get_output_in_json()['properties']['throughput']['actionsPerSecond'], 100)
        self.assertEqual([request.method for request in self.requests], ['PUT', 'GET', 'GET'])
        self.assertEqual(self.requests[1].url, operation_url)

    def test_durabletask_taskqueue_no_wait_does_not_poll(self):
        queue = self._child('/taskHubs/test-hub/taskQueues/test-queue',
                            throughput={'actionsPerSecond': 100})
        queue['properties']['provisioningState'] = 'Creating'
        result = self._cmd(
            'az durabletask taskqueue create -g test-rg -s test-scheduler -t test-hub '
            '-n test-queue --actions-per-second 100 --no-wait',
            (202, queue, {'Azure-AsyncOperation': 'https://management.azure.com/test-operation'}))
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(result.output.strip(), '')

    def test_durabletask_taskqueue_async_failure(self):
        queue = self._child('/taskHubs/test-hub/taskQueues/test-queue',
                            throughput={'actionsPerSecond': 100})
        queue['properties']['provisioningState'] = 'Creating'
        operation_url = 'https://management.azure.com' + SCHEDULER_PATH + '/operationStatuses/test-operation'
        with self.assertRaisesRegex(HttpResponseError, 'Unsupported SKU'):
            self._cmd(
                'az durabletask taskqueue create -g test-rg -s test-scheduler -t test-hub '
                '-n test-queue --actions-per-second 100',
                (202, queue, {'Azure-AsyncOperation': operation_url, 'Retry-After': '0'}),
                (200, {'status': 'Failed', 'error': {'code': 'InvalidSku', 'message': 'Unsupported SKU'}}))
        self.assertEqual(len(self.requests), 2)

    def test_durabletask_retention_policy_lifecycle(self):
        path = SCHEDULER_PATH + '/retentionPolicies/default'
        policies = [
            {'retentionPeriodInDays': 30},
            {'retentionPeriodInDays': 1, 'orchestrationState': 'Canceled'},
            {'retentionPeriodInDays': 2, 'orchestrationState': 'Completed'},
            {'retentionPeriodInDays': 3, 'orchestrationState': 'Failed'},
            {'retentionPeriodInDays': 4, 'orchestrationState': 'Terminated'},
        ]
        policy = self._child('/retentionPolicies/default', retentionPolicies=policies)
        result = self._cmd(
            'az durabletask retention-policy create -g test-rg -s test-scheduler '
            '-d 30 -x 1 -c 2 -f 3 -t 4', (201, policy))
        self.assertEqual(result.get_output_in_json()['properties']['retentionPolicies'], policies)
        self._assert_request(0, 'PUT', path, {'properties': {'retentionPolicies': policies}},
                             api_version='2026-02-01')
        self._cmd(
            'az durabletask retention-policy show -g test-rg -s test-scheduler', (200, policy))
        self._cmd(
            'az durabletask retention-policy delete -g test-rg -s test-scheduler --yes',
            (204, None))
        self._assert_request(0, 'DELETE', path, api_version='2026-02-01')

    def test_durabletask_retention_policy_requires_period(self):
        with self.assertRaisesRegex(ValueError, 'At least one retention period'):
            self._cmd('az durabletask retention-policy create -g test-rg -s test-scheduler')
        self.assertFalse(self.requests)

    def test_durabletask_encryption_lifecycle(self):
        path = SCHEDULER_PATH + '/transparentDataEncryptions/default'
        encryption = self._child(
            '/transparentDataEncryptions/default', keySource='CustomerManaged',
            keyVaultKeyUri=KEY_URI, autoRotationEnabled=False)
        self._cmd(
            'az durabletask scheduler transparent-data-encryption create -g test-rg '
            f'--scheduler-name test-scheduler --key-vault-key-uri {KEY_URI} '
            '--auto-rotation-enabled false', (201, encryption))
        self._assert_request(0, 'PUT', path, {'properties': {
            'keySource': 'CustomerManaged', 'keyVaultKeyUri': KEY_URI, 'autoRotationEnabled': False,
        }})
        result = self._cmd(
            'az durabletask scheduler transparent-data-encryption show -g test-rg '
            '--scheduler-name test-scheduler', (200, encryption))
        self.assertEqual(result.get_output_in_json()['properties']['keyVaultKeyUri'], KEY_URI)
        self._assert_request(0, 'GET', path)
        for argument, value in (('true', True), ('false', False)):
            with self.subTest(argument=argument):
                updated = copy.deepcopy(encryption)
                updated['properties']['autoRotationEnabled'] = value
                result = self._cmd(
                    'az durabletask scheduler transparent-data-encryption update -g test-rg '
                    '--scheduler-name test-scheduler --auto-rotation-enabled ' + argument,
                    (200, encryption), (200, updated))
                self.assertIs(result.get_output_in_json()['properties']['autoRotationEnabled'], value)
                self._assert_request(0, 'GET', path)
                self._assert_request(1, 'PUT', path, {'properties': {
                    'keySource': 'CustomerManaged', 'keyVaultKeyUri': KEY_URI,
                    'autoRotationEnabled': value,
                }})
        self._cmd(
            'az durabletask scheduler transparent-data-encryption delete -g test-rg '
            '--scheduler-name test-scheduler --yes', (204, None))
        self._assert_request(0, 'DELETE', path)

    def test_durabletask_failover_async_action(self):
        instance = self._child('/failoverInstances/default', partnerSchedulerResourceId=PARTNER_ID,
                               replicationRole='Secondary', failoverState='Ready')
        operation_url = 'https://management.azure.com' + SCHEDULER_PATH + '/operationResults/test-operation'
        result = self._cmd(
            'az durabletask scheduler failover-instance failover -g test-rg -s test-scheduler',
            (202, None, {'Location': operation_url, 'Retry-After': '0'}), (200, instance))
        self.assertEqual(result.get_output_in_json()['properties']['replicationRole'], 'Secondary')
        self.assertEqual([request.method for request in self.requests], ['POST', 'GET'])
        self.assertEqual(self.requests[1].url, operation_url)

    def test_durabletask_encryption_update_preserves_omitted_fields(self):
        encryption = self._child(
            '/transparentDataEncryptions/default', keySource='CustomerManaged',
            keyVaultKeyUri=KEY_URI, autoRotationEnabled=True)
        self._cmd(
            'az durabletask scheduler transparent-data-encryption update -g test-rg '
            '--scheduler-name test-scheduler', (200, encryption), (200, encryption))
        self.assertEqual(json.loads(self.requests[1].body), {'properties': {
            'keySource': 'CustomerManaged', 'keyVaultKeyUri': KEY_URI, 'autoRotationEnabled': True,
        }})

    def test_durabletask_encryption_update_clears_nullable_key_uri(self):
        encryption = self._child(
            '/transparentDataEncryptions/default', keySource='CustomerManaged',
            keyVaultKeyUri=KEY_URI, autoRotationEnabled=True)
        self._cmd(
            'az durabletask scheduler transparent-data-encryption update -g test-rg '
            '--scheduler-name test-scheduler --key-source MicrosoftManaged --key-vault-key-uri null',
            (200, encryption), (200, encryption))
        self.assertEqual(json.loads(self.requests[1].body), {'properties': {
            'keySource': 'MicrosoftManaged', 'autoRotationEnabled': True,
        }})

    def test_durabletask_failover_instance_lifecycle(self):
        path = SCHEDULER_PATH + '/failoverInstances/default'
        instance = self._child(
            '/failoverInstances/default', partnerSchedulerResourceId=PARTNER_ID,
            partnerSchedulerLocation='westus', replicationRole='Primary', failoverState='Ready')
        self._cmd(
            'az durabletask scheduler failover-instance create -g test-rg -s test-scheduler '
            f'--partner-scheduler-resource-id {PARTNER_ID}', (201, instance))
        self._assert_request(0, 'PUT', path, {
            'properties': {'partnerSchedulerResourceId': PARTNER_ID},
        })
        result = self._cmd(
            'az durabletask scheduler failover-instance show -g test-rg -s test-scheduler',
            (200, instance))
        self.assertEqual(result.get_output_in_json()['properties']['replicationRole'], 'Primary')
        self._assert_request(0, 'GET', path)
        new_partner = PARTNER_ID.replace('test-partner', 'new-partner')
        updated = copy.deepcopy(instance)
        updated['properties']['partnerSchedulerResourceId'] = new_partner
        self._cmd(
            'az durabletask scheduler failover-instance update -g test-rg -s test-scheduler '
            f'--pid {new_partner}', (200, instance), (200, updated))
        self._assert_request(1, 'PUT', path, {
            'properties': {'partnerSchedulerResourceId': new_partner},
        })
        self._cmd(
            'az durabletask scheduler failover-instance failover -g test-rg -s test-scheduler',
            (200, instance))
        self._assert_request(0, 'POST', path + '/failover')
        self._cmd(
            'az durabletask scheduler failover-instance force-failover-allow-data-loss '
            '-g test-rg -s test-scheduler', (200, instance))
        self._assert_request(0, 'POST', path + '/forceFailoverAllowDataLoss')
        self._cmd(
            'az durabletask scheduler failover-instance delete -g test-rg -s test-scheduler --yes',
            (204, None))
        self._assert_request(0, 'DELETE', path)

    def test_durabletask_restart_aliases(self):
        for option in ('-n', '--name', '--scheduler-name'):
            with self.subTest(option=option):
                result = self._cmd(
                    f'az durabletask scheduler restart -g test-rg {option} test-scheduler',
                    (204, None))
                self.assertTrue(result.output.strip(), 'Restart must preserve its existing JSON response')
                self.assertEqual(result.get_output_in_json(), {
                    'schedulerName': 'test-scheduler', 'resourceGroupName': 'test-rg',
                    'status': 'Restart initiated',
                })
                self._assert_request(0, 'POST', SCHEDULER_PATH + '/restart')
                result = self._cmd(
                    f'az durabletask scheduler restart -g test-rg {option} test-scheduler '
                    '--query status -o tsv', (204, None))
                self.assertEqual(result.output.strip(), 'Restart initiated')

    def test_durabletask_attach_command_arguments(self):
        target = (
            f'/subscriptions/{SUBSCRIPTION}/resourceGroups/app-rg'
            '/providers/Microsoft.Web/sites/test-function'
        )
        with patch.object(_scheduler, '_get_functionapp_identity', return_value='test-principal'), \
                patch.object(_scheduler, '_check_target_permissions'), \
                patch.object(_scheduler, '_check_access'), \
                patch.object(_scheduler, '_update_functionapp_settings') as settings, \
                patch('azure.cli.core.commands.arm.resolve_role_id', return_value='test-role'), \
                patch('azure.cli.core.commands.client_factory.get_mgmt_service_client') as factory:
            result = self._cmd(
                'az durabletask scheduler attach -g test-rg -n test-scheduler '
                f'--task-hub-name test-hub --target {target} --role-type worker',
                (200, self._scheduler()), (200, self._child('/taskHubs/test-hub')))
        self.assertEqual(result.get_output_in_json()['roleAssigned'], 'Durable Task Worker')
        settings.assert_called_once()
        self.assertEqual(settings.call_args.args[1:], (
            'test-function', 'app-rg', SUBSCRIPTION, self._scheduler()['properties']['endpoint'],
            'test-hub', None))
        factory.return_value.role_assignments.create.assert_called_once()

    def test_durabletask_service_errors_propagate(self):
        for command in (
            'az durabletask scheduler restart -g test-rg -n test-scheduler',
            'az durabletask taskqueue create -g test-rg -s test-scheduler -t test-hub '
            '-n test-queue --actions-per-second 100',
            'az durabletask scheduler transparent-data-encryption update -g test-rg '
            '--scheduler-name test-scheduler --auto-rotation-enabled true',
        ):
            with self.subTest(command=command):
                with self.assertRaisesRegex(HttpResponseError, 'Access denied'):
                    self._cmd(
                        command, (403, {'error': {'code': 'AuthorizationFailed', 'message': 'Access denied'}}))
                self.assertEqual(len(self.requests), 1)

    def test_durabletask_taskqueue_list_paging(self):
        queue = self._child('/taskHubs/test-hub/taskQueues/test-queue',
                            throughput={'actionsPerSecond': 100})
        second = copy.deepcopy(queue)
        second['name'] = 'second-queue'
        second['id'] = second['id'].replace('test-queue', 'second-queue')
        next_link = (
            'https://management.azure.com' + SCHEDULER_PATH +
            '/taskHubs/test-hub/taskQueues?api-version=2026-07-01-preview&$skiptoken=next'
        )
        result = self._cmd(
            'az durabletask taskqueue list -g test-rg -s test-scheduler -t test-hub',
            (200, {'value': [queue], 'nextLink': next_link}), (200, {'value': [second]}))
        self.assertEqual(result.get_output_in_json(), [
            dict(queue, resourceGroup='test-rg'), dict(second, resourceGroup='test-rg'),
        ])
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(self.requests[1].method, 'GET')
        self.assertEqual(self.requests[1].url, next_link)
