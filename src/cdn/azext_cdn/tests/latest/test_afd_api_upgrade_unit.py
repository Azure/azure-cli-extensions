# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import copy
import json
import os
import shlex
from contextlib import ExitStack
from itertools import product
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qs, urlparse

from azure.core import PipelineClient
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.core.polling import NoPolling
from azure.cli.core import _session
from azure.cli.core.aaz import AAZUndefined
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.aaz._poller import AAZLROPoller
from azure.cli.core.mock import DummyCli

from azext_cdn.custom.custom_afdx import (
    AFDProfileCreate, AFDRouteCreate, AFDRouteUpdate, AFDRuleActionAdd,
)
from azext_cdn.custom.custom_cdn import (
    CDNEndpointCreate, CDNEndpointUpdate,
    CDNProfileCreate, CDNProfileDelete, CDNProfileList, CDNProfileShow, CDNProfileUpdate,
)
from .afdx_scenario_mixin import ByocVaultRecordingProcessor, CdnAfdScenarioMixin


SUBSCRIPTION = '00000000-0000-0000-0000-000000000000'
API_VERSION = '2026-09-01-preview'
ARM_URL = 'https://management.azure.com'
PROFILE_ID = (
    f'/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Cdn/profiles/profile'
)
EDGE_ACTION_ID = f'/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action'
COMMON_ARGS = ['--resource-group', 'rg', '--profile-name', 'profile']


class OfflineAazTest(TestCase):

    api_version = API_VERSION

    def setUp(self):
        self.contexts = ExitStack()
        self.addCleanup(self.contexts.close)
        config_dir = self.contexts.enter_context(TemporaryDirectory())
        environment = self.contexts.enter_context(patch.dict('os.environ', {
            'AZURE_CONFIG_DIR': config_dir,
            'AZURE_CORE_COLLECT_TELEMETRY': 'false',
            'AZURE_CORE_ONLY_SHOW_ERRORS': 'true',
        }))
        environment.pop('AZURE_TEST_RUN_LIVE', None)
        environment.pop('ARM_CLOUD_METADATA_URL', None)
        self.contexts.enter_context(patch('socket.socket.connect', side_effect=AssertionError('Network is disabled')))
        self.contexts.enter_context(patch(
            'requests.sessions.Session.request', side_effect=AssertionError('Network is disabled')
        ))
        self.contexts.enter_context(patch('azure.cli.core.aaz._command_ctx.Profile', autospec=True))
        self.contexts.enter_context(patch(
            'azure.cli.core.commands.client_factory.get_subscription_id', return_value=SUBSCRIPTION
        ))
        self.contexts.enter_context(patch('azure.cli.core.util.handle_version_update'))
        # AzCli reloads shared Session instances that other modules also reference.
        for session in vars(_session).values():
            if isinstance(session, _session.Session):
                self.contexts.enter_context(patch.object(session, 'filename', session.filename))
                self.contexts.enter_context(patch.object(session, 'data', copy.deepcopy(session.data)))
        self.cli = DummyCli()
        self.loader = SimpleNamespace(cli_ctx=self.cli)
        transport = MagicMock(spec=HttpTransport)
        transport.send.side_effect = AssertionError('Network is disabled')
        self.client = PipelineClient(base_url=ARM_URL, transport=transport, policies=[])
        self.addCleanup(self.client.close)
        self.client.send_request = Mock(side_effect=self._send_request)
        self.client.build_lro_polling = Mock(side_effect=self._build_polling)
        self.contexts.enter_context(patch.object(AAZCommandCtx, 'get_http_client', return_value=self.client))
        self.contexts.enter_context(patch.object(
            AAZCommandCtx, 'get_login_credential', side_effect=AssertionError('Credentials are disabled')
        ))
        self.responses = []
        self.requests = []

    def _send_request(self, request, stream=False, **_kwargs):
        self.assertFalse(stream)
        self.assertTrue(self.responses, f'Unexpected request: {request.method} {request.url}')
        method, status, body = self.responses.pop(0)
        self.assertEqual(method, request.method)
        self.assertEqual([self.api_version], parse_qs(urlparse(request.url).query)['api-version'])
        self.requests.append(request)
        response = Mock(spec=HttpResponse)
        response.request = request
        response.status_code = status
        response.reason = 'Mock response'
        response.headers = {'Content-Type': 'application/json'}
        response.text.return_value = json.dumps(body)
        response.body.return_value = json.dumps(body).encode('utf-8')
        context = PipelineContext(None, stream=False)
        context[ContentDecodePolicy.CONTEXT_NAME] = copy.deepcopy(body)
        return PipelineResponse(request, response, context)

    def _build_polling(self, _no_wait, session, deserialize, _on_error, **_kwargs):
        polling = Mock(spec=NoPolling)
        polling.resource.side_effect = lambda: deserialize(session)
        return polling

    def _command(self, command_type, arguments):
        command = command_type(loader=self.loader)
        parser = argparse.ArgumentParser(add_help=False)
        for name, argument in command._cli_arguments_loader():  # pylint: disable=protected-access
            settings = argument.type.settings
            options = {key: settings[key] for key in ('action', 'nargs', 'choices', 'required') if key in settings}
            parser.add_argument(
                *argument.options_list, dest=name, default=settings.get('default', AAZUndefined), **options
            )
        parsed = vars(parser.parse_args(arguments))
        parsed['subscription'] = SUBSCRIPTION
        return command, parsed

    def _invoke(self, command_type, arguments, responses=()):
        self.responses = list(responses)
        self.requests = []
        command, parsed = self._command(command_type, arguments)
        result = command(command_args=parsed)
        if isinstance(result, AAZLROPoller):
            result = result.result(timeout=5)
        self.assertFalse(self.responses, 'Not all expected requests were sent')
        return result

    def _body(self):
        return json.loads(self.requests[-1].body)

    @staticmethod
    def _resource(properties):
        return {
            'id': PROFILE_ID,
            'name': 'profile',
            'properties': dict(properties, provisioningState='Succeeded', deploymentStatus='Deployed'),
        }

    def _write(self, command_type, arguments, properties, existing=None):
        resource = self._resource(properties)
        responses = []
        if existing is not None:
            responses.append(('GET', 200, self._resource(existing)))
        responses.append(('PUT', 200, resource))
        output = self._invoke(command_type, arguments, responses)
        sent = self._body()['properties']
        for key, value in properties.items():
            self.assertEqual(value, sent[key], key)
            self.assertEqual(value, output[key], key)
        self.assertNotIn('provisioningState', sent)
        self.assertNotIn('deploymentStatus', sent)
        return output


class AfdApiUpgradeUnitTest(OfflineAazTest):

    def test_profile_create_uses_global_location_without_resource_group_lookup(self):
        for environment_type in (None, 'NonProduction'):
            with self.subTest(environment_type=environment_type):
                arguments = ['-g', 'rg', '--profile-name', 'profile', '--sku', 'Standard_AzureFrontDoor']
                if environment_type:
                    arguments += ['--environment-type', environment_type]
                self._invoke(AFDProfileCreate, arguments, [('PUT', 201, self._resource({}))])
                body = self._body()
                self.assertEqual(1, len(self.requests))
                self.assertEqual('global', body['location'])
                if environment_type:
                    self.assertEqual({'environmentType': environment_type}, body['properties']['extendedProperties'])
                else:
                    self.assertNotIn('extendedProperties', body.get('properties', {}))

    def test_route_origin_group_normalization(self):
        origin_group_id = PROFILE_ID + '/originGroups/group'
        for command_type in (AFDRouteCreate, AFDRouteUpdate):
            for origin_group in ('group', origin_group_id):
                with self.subTest(command=command_type.AZ_NAME, origin_group=origin_group):
                    existing = {'originPath': '/keep'}
                    properties = dict(existing, originGroup={'id': origin_group_id})
                    arguments = COMMON_ARGS + [
                        '--endpoint-name', 'endpoint', '--route-name', 'route',
                        '--origin-group', origin_group,
                    ]
                    if command_type is AFDRouteCreate:
                        arguments += ['--origin-path', '/keep']
                    self._write(command_type, arguments, properties,
                                existing if command_type is AFDRouteUpdate else None)

    def test_rule_action_add_appends_and_selects_last_matching_action(self):
        arguments = COMMON_ARGS + ['--rule-set-name', 'rules', '--rule-name', 'rule']
        action = {'name': 'EdgeAction', 'parameters': {
            'edgeActionReference': {'id': EDGE_ACTION_ID}, 'invocationPoint': 'ClientResponse',
            'typeName': 'DeliveryRuleEdgeActionParameters',
        }}
        previous = copy.deepcopy(action)
        previous['parameters']['invocationPoint'] = 'ClientRequest'
        existing = self._resource({'actions': [previous], 'order': 0})
        populated = self._resource({'actions': [previous, action], 'order': 0})
        edge_parameters = (
            '{parameters:{edge-action-reference:{id:' + EDGE_ACTION_ID + '},invocation-point:ClientResponse}}'
        )
        named_args = arguments + ['--action-name', 'EdgeAction']
        output = self._invoke(AFDRuleActionAdd, named_args + ['--edge-action', edge_parameters], [
            ('GET', 200, existing), ('PUT', 200, populated),
        ])
        self.assertEqual(action, output)
        self.assertEqual(0, self._body()['properties']['order'])
        self.assertEqual([previous, action], self._body()['properties']['actions'])


class OfflineAazIsolationUnitTest(TestCase):

    def test_global_sessions_are_restored_after_cleanup(self):
        for setup_fails in (False, True):
            with self.subTest(setup_fails=setup_fails):
                with TemporaryDirectory() as config_dir, ExitStack() as contexts:
                    originals = []
                    for name, session in vars(_session).items():
                        if not isinstance(session, _session.Session):
                            continue
                        filename = os.path.join(config_dir, name + '.json')
                        data = {'original': name}
                        contexts.enter_context(patch.object(session, 'filename', filename))
                        contexts.enter_context(patch.object(session, 'data', data))
                        originals.append((session, filename, data))
                    fixture = OfflineAazTest()
                    try:
                        if setup_fails:
                            with patch(__name__ + '.PipelineClient', side_effect=RuntimeError('Setup failed')):
                                with self.assertRaisesRegex(RuntimeError, 'Setup failed'):
                                    fixture.setUp()
                        else:
                            fixture.setUp()
                        fixture_config_dir = fixture.cli.config.config_dir
                    finally:
                        self.assertTrue(fixture.doCleanups())
                    self.assertFalse(os.path.exists(fixture_config_dir))
                    for session, filename, data in originals:
                        self.assertEqual(filename, session.filename)
                        self.assertIs(data, session.data)
                        self.assertEqual({'original': data['original']}, session.data)
                        session['after'] = 'cleanup'
                        with open(filename, encoding='utf-8-sig') as stream:
                            self.assertEqual(dict(data, after='cleanup'), json.load(stream))


class NonProductionProfileFixtureUnitTest(TestCase):

    def test_nonproduction_profile_uses_official_commands_and_preserves_readiness(self):
        for sku in (None, 'Premium_AzureFrontDoor'):
            with self.subTest(sku=sku):
                scenario = Mock()
                created, waited, shown = Mock(), Mock(), Mock()
                scenario.cmd.side_effect = [created, waited, shown]
                options = {'sku': sku} if sku else {}
                result = CdnAfdScenarioMixin.afd_nonproduction_profile_create_cmd(
                    scenario, 'rg', 'profile', **options)
                calls = scenario.cmd.call_args_list
                self.assertEqual(3, len(calls))
                self.assertEqual([
                    'afd', 'profile', 'create', '-g', 'rg', '--profile-name', 'profile',
                    '--sku', sku or 'Standard_AzureFrontDoor',
                    '--environment-type', 'NonProduction', '--no-wait',
                ], shlex.split(calls[0].args[0]))
                self.assertEqual({}, calls[0].kwargs)
                self.assertEqual('afd profile wait -g rg --profile-name profile --created', calls[1].args[0])
                self.assertEqual({}, calls[1].kwargs)
                self.assertEqual('afd profile show -g rg --profile-name profile', calls[2].args[0])
                self.assertEqual({'checks'}, calls[2].kwargs.keys())
                checks = calls[2].kwargs['checks']
                self.assertEqual(1, len(checks))
                shown.get_output_in_json.return_value = {'extendedProperties': {'environmentType': 'NonProduction'}}
                checks[0](shown)
                shown.get_output_in_json.return_value = {'extendedProperties': {'environmentType': 'Production'}}
                with self.assertRaises(AssertionError):
                    checks[0](shown)
                self.assertIs(shown, result)


class ByocIdentityFixtureUnitTest(TestCase):

    def test_shared_vault_recording_preserves_fixture_and_scrubs_other_identities(self):
        principal_id = '11111111-1111-1111-1111-111111111111'
        other_id = '22222222-2222-2222-2222-222222222222'
        fixture_policy = {'objectId': principal_id, 'tenantId': 'fixture-tenant',
                          'permissions': {'secrets': ['get']}}
        other_policy = {'objectId': other_id, 'tenantId': 'other-tenant',
                        'applicationId': 'other-application', 'permissions': {'secrets': ['list']}}
        payload = {
            'properties': {'accessPolicies': [other_policy, fixture_policy], 'enabledForDeployment': False},
            'systemData': {'lastModifiedBy': 'other-user@example.invalid', 'lastModifiedAt': '2026-10-26T00:00:00Z'},
        }
        processor = ByocVaultRecordingProcessor(principal_id)
        request = SimpleNamespace(body=json.dumps(payload).encode())
        response = {'body': {'string': json.dumps(payload)}}
        processor.process_request(request)
        processor.process_response(response)
        scrubbed = json.loads(request.body)
        self.assertEqual(scrubbed, json.loads(response['body']['string']))
        policies = scrubbed['properties']['accessPolicies']
        self.assertEqual(fixture_policy, policies[1])
        self.assertEqual(other_policy['permissions'], policies[0]['permissions'])
        for name in ('objectId', 'tenantId', 'applicationId'):
            self.assertNotEqual(other_policy[name], policies[0][name])
            self.assertTrue(policies[0][name].startswith('00000000-0000-0000-0000-'))
        self.assertFalse(scrubbed['properties']['enabledForDeployment'])
        self.assertNotEqual(payload['systemData']['lastModifiedBy'], scrubbed['systemData']['lastModifiedBy'])
        self.assertEqual(payload['systemData']['lastModifiedAt'], scrubbed['systemData']['lastModifiedAt'])
        self.assertIsInstance(request.body, bytes)
        first_pass = request.body
        processor.process_request(request)
        self.assertEqual(first_pass, request.body)
        for unrelated in ('not-json', '{"properties":{"tlsSettings":{}}}', '{"properties":null}', '[1,2]', None):
            request.body = unrelated
            processor.process_request(request)
            self.assertEqual(unrelated, request.body)

    def test_vault_access_is_scoped_and_cleaned_up(self):
        identity = {
            'principalId': '11111111-1111-1111-1111-111111111111',
            'tenantId': '22222222-2222-2222-2222-222222222222',
        }
        for in_recording, fail, same_subscription in product((False, True), repeat=3):
            with self.subTest(in_recording=in_recording, fail=fail, same_subscription=same_subscription):
                vault_options = {
                    'vault_name': 'AfdxE2eTestKV04',
                    'vault_resource_group': 'DoNotDeleteThisRG',
                    'vault_subscription': '11111111-2222-3333-4444-555555555555',
                } if same_subscription else {}
                scenario = Mock()
                scenario.assertTrue = self.assertTrue
                scenario.in_recording = in_recording
                scenario.is_live = False
                scenario.recording_processors = []
                scenario.get_subscription_id.return_value = SUBSCRIPTION
                scenario.cmd.return_value.get_output_in_json.return_value = identity
                if fail:
                    with self.assertRaisesRegex(RuntimeError, 'fixture failure'):
                        with CdnAfdScenarioMixin.afd_byoc_identity(scenario, 'rg', 'profile', **vault_options):
                            raise RuntimeError('fixture failure')
                else:
                    with CdnAfdScenarioMixin.afd_byoc_identity(scenario, 'rg', 'profile', **vault_options):
                        self.assertEqual(2, scenario.cmd.call_count)

                calls = scenario.cmd.call_args_list
                self.assertEqual(3, len(calls))
                self.assertEqual([], scenario.recording_processors)
                self.assertIn('afd profile identity assign', calls[0].args[0])
                vault_subscription = (
                    vault_options.get('vault_subscription', '3c0124f9-e564-4c42-86f7-fa79457aedc3')
                    if in_recording else SUBSCRIPTION
                )
                for call, operation in zip(calls[1:], ('set-policy', 'delete-policy')):
                    arguments = shlex.split(call.args[0])
                    expected = [
                        'keyvault', operation, '--name', vault_options.get('vault_name', 'Azure-CDN-BYOC'),
                        '--resource-group', vault_options.get('vault_resource_group', 'byoc'),
                        '--subscription', vault_subscription, '--object-id', identity['principalId'],
                    ]
                    if operation == 'set-policy':
                        expected += ['--secret-permissions', 'get']
                    self.assertEqual(expected, arguments)


class ClassicCdnCompatibilityUnitTest(OfflineAazTest):

    api_version = '2026-04-01-preview'

    def test_classic_profile_command_registration(self):
        for verb, command_type in (
            ('create', CDNProfileCreate), ('delete', CDNProfileDelete), ('list', CDNProfileList),
            ('show', CDNProfileShow), ('update', CDNProfileUpdate),
        ):
            with self.subTest(command=verb):
                self.assertEqual('cdn profile ' + verb, command_type.AZ_NAME)

    def test_classic_profile_customizations(self):
        resource = {
            'id': PROFILE_ID,
            'name': 'profile',
            'location': 'global',
            'sku': {'name': 'Standard_Microsoft'},
            'properties': {'provisioningState': 'Succeeded'},
        }
        arguments = ['--resource-group', 'rg', '--name', 'profile']
        for command_type, args, responses in (
            (CDNProfileCreate, arguments + ['--sku', 'Standard_Microsoft'], [('PUT', 200, resource)]),
            (CDNProfileUpdate, arguments + ['--tags', '{key:value}'],
             [('GET', 200, resource), ('PUT', 200, resource)]),
        ):
            with self.subTest(command=command_type.__name__):
                command, _ = self._command(command_type, args)
                options = [
                    option
                    for _, argument in command._cli_arguments_loader()  # pylint: disable=protected-access
                    for option in argument.options_list
                ]
                self.assertNotIn('--location' if command_type is CDNProfileCreate else '--sku', options)
                with patch('azure.cli.core.aaz._command_ctx.get_resource_group_location', return_value='global'):
                    self._invoke(command_type, args, responses)
                if command_type is CDNProfileCreate:
                    self.assertEqual('global', self._body()['location'])

    def test_classic_endpoint_origin_and_flag_customizations(self):
        self._invoke(CDNEndpointCreate, COMMON_ARGS + [
            '--endpoint-name', 'endpoint', '--location', 'global', '--origin', 'origin.example',
            '--no-http', '--no-https', '--enable-compression',
        ], [('PUT', 200, self._resource({}))])
        properties = self._body()['properties']
        self.assertEqual(1, len(properties['origins']))
        origin = properties['origins'][0]
        self.assertEqual('origin-example', origin['name'])
        self.assertEqual('origin.example', origin['properties']['hostName'])
        self.assertEqual(80, origin['properties']['httpPort'])
        self.assertEqual(443, origin['properties']['httpsPort'])
        self.assertFalse(properties['isHttpAllowed'])
        self.assertFalse(properties['isHttpsAllowed'])
        self.assertTrue(properties['isCompressionEnabled'])
        self.assertIn('text/plain', properties['contentTypesToCompress'])

    def test_classic_endpoint_update_normalizes_group_and_preserves_compression(self):
        origin_group_id = PROFILE_ID + '/endpoints/endpoint/originGroups/group'
        for origin_group in ('group', origin_group_id):
            with self.subTest(origin_group=origin_group):
                existing = self._resource({'isCompressionEnabled': False})
                existing['location'] = 'global'
                self._invoke(CDNEndpointUpdate, COMMON_ARGS + [
                    '--endpoint-name', 'endpoint', '--default-origin-group', origin_group,
                    '--no-http', '--no-https',
                ], [('GET', 200, existing)] * 2 + [('PUT', 200, existing)])
                properties = self._body()['properties']
                self.assertEqual({'id': origin_group_id}, properties['defaultOriginGroup'])
                self.assertFalse(properties['isCompressionEnabled'])
                self.assertFalse(properties['isHttpAllowed'])
                self.assertFalse(properties['isHttpsAllowed'])
