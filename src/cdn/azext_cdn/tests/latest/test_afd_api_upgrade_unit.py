# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import copy
import io
import json
import os
import shlex
from contextlib import ExitStack, redirect_stderr
from datetime import datetime, timedelta, timezone
from itertools import product
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qs, urlencode, urlparse

from azure.core import PipelineClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.core.polling import NoPolling
from azure.cli.core import _session
from azure.cli.core.aaz import AAZUndefined
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.aaz._poller import AAZLROPoller
from azure.cli.core.mock import DummyCli
from azure.cli.testsdk.exceptions import JMESPathCheckAssertionError
from knack.util import CLIError

from azext_cdn import CdnCommandsLoader
from azext_cdn.aaz.latest.afd.origin_group import Create as AFDOriginGroupCreate
from azext_cdn.aaz.latest.afd.rule_set import Create as AFDRuleSetCreate
from azext_cdn.aaz.latest.afd.secret import Create as AFDSecretCreate
from azext_cdn.custom.custom_afdx import (
    AFDCustomDomainCreate, AFDOriginCreate, AFDOriginGroupUpdate, AFDProfileCreate, AFDRouteCreate, AFDRouteUpdate,
    AFDRuleActionAdd, AFDRuleCreate,
)
from azext_cdn.custom.custom_cdn import (
    CDNEndpointCreate, CDNEndpointUpdate,
    CDNProfileCreate, CDNProfileDelete, CDNProfileList, CDNProfileShow, CDNProfileUpdate,
)
from .afdx_scenario_mixin import ByocVaultRecordingProcessor, CdnAfdScenarioMixin
from .scenario_mixin import CdnScenarioMixin
from . import config as test_config
from . import run_tests
from . import test_custom_domain_scenarios as custom_domain_scenarios


SUBSCRIPTION = '00000000-0000-0000-0000-000000000000'
API_VERSION = '2026-10-01'
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


class StableApiSurfaceUnitTest(OfflineAazTest):

    def test_command_registration_excludes_preview_only_resources(self):
        loader = CdnCommandsLoader(self.cli)
        commands = loader.load_command_table(None)
        self.assertIn('afd profile create', commands)
        self.assertIn('cdn profile create', commands)
        for name, command in commands.items():
            with self.subTest(command=name):
                self.assertFalse(name.startswith(('afd auth-policy', 'cdn profile deployment-version')))
                for resource in getattr(command, '_aaz_info', {}).get('resources', []):
                    self.assertEqual(API_VERSION, resource[2])

    def test_removed_arguments_and_grpc_protocol_are_rejected(self):
        group_args = COMMON_ARGS + ['--origin-group-name', 'group']
        route_args = COMMON_ARGS + ['--endpoint-name', 'endpoint', '--route-name', 'route']
        rule_args = COMMON_ARGS + ['--rule-set-name', 'rules', '--rule-name', 'rule']
        cases = [
            (AFDOriginGroupCreate, group_args + ['--capacity-settings', '{}']),
            (AFDOriginGroupUpdate, group_args + ['--capacity-distribution-settings', '{}']),
            (AFDOriginGroupCreate, group_args + ['--probe-protocol', 'Grpc']),
            (AFDOriginGroupUpdate, group_args + ['--probe-protocol', 'Grpc']),
            (AFDRouteCreate, route_args + ['--grpc-state', 'Enabled']),
            (AFDRouteUpdate, route_args + ['--grpc-state', 'Disabled']),
            (AFDRuleActionAdd, rule_args + ['--action-name', 'AfdUrlSigning']),
            (AFDRuleActionAdd, rule_args + ['--action-name', 'UrlSigning', '--afd-url-signing', '{}']),
            (AFDRuleCreate, rule_args + ['--order', '1', '--actions', '[{afd-url-signing:{}}]']),
            (AFDRuleSetCreate, COMMON_ARGS + [
                '--rule-set-name', 'rules', '--batch-mode', 'true',
                '--rules', '[{rule-name:r0,order:0,actions:[{afd-url-signing:{}}]}]',
            ]),
        ]
        for command, arguments in cases:
            with self.subTest(command=command.AZ_NAME, arguments=arguments), redirect_stderr(io.StringIO()):
                with self.assertRaises((SystemExit, CLIError)):
                    self._invoke(command, arguments)
                self.assertEqual([], self.requests)

    def test_origin_authentication_round_trips_on_stable_api(self):
        properties = {
            'authentication': {
                'type': 'SystemAssignedIdentity',
                'scope': 'https://storage.azure.com/.default',
                'tokenDestinationHeader': 'X-Azure-Authorization',
            },
            'healthProbeSettings': {'probeProtocol': 'Https'},
        }
        self._write(AFDOriginGroupCreate, COMMON_ARGS + [
            '--origin-group-name', 'group', '--probe-protocol', 'Https',
            '--authentication', json.dumps({
                'type': 'SystemAssignedIdentity', 'scope': 'https://storage.azure.com/.default',
                'token-destination-header': 'X-Azure-Authorization',
            }),
        ], properties)

    def test_custom_domain_mtls_and_tls_groups_round_trip_on_stable_api(self):
        properties = {
            'hostName': 'cdn.example.com',
            'tlsSettings': {
                'certificateType': 'ManagedCertificate',
                'minimumTlsVersion': 'TLS12',
                'serverTlsGroupPolicy': 'Custom',
                'serverTlsGroups': ['X25519MLKEM768'],
            },
            'mtlsSettings': {'scenario': 'CompleteMtlsPassthroughToOrigin'},
        }
        self._write(AFDCustomDomainCreate, COMMON_ARGS + [
            '--custom-domain-name', 'domain', '--host-name', 'cdn.example.com',
            '--certificate-type', 'ManagedCertificate', '--minimum-tls-version', 'TLS12',
            '--tls-group-policy', 'Custom', '--server-tls-groups', 'X25519MLKEM768',
            '--mtls-settings', '{complete-mtls-passthrough-to-origin:{}}',
        ], properties)

    def test_url_signing_secret_is_retained_on_stable_api(self):
        source_id = (
            f'/subscriptions/{SUBSCRIPTION}/resourceGroups/rg'
            '/providers/Microsoft.KeyVault/vaults/vault/secrets/signing-key'
        )
        self._write(AFDSecretCreate, COMMON_ARGS + [
            '--secret-name', 'signing-key', '--parameters',
            '{url-signing-key:{key-id:k1,secret-source:{id:' + source_id + '},secret-version:v1}}',
        ], {'parameters': {
            'type': 'UrlSigningKey', 'keyId': 'k1',
            'secretSource': {'id': source_id}, 'secretVersion': 'v1',
        }})

    def test_origin_custom_certificate_validation_round_trips_on_stable_api(self):
        self._write(AFDOriginCreate, COMMON_ARGS + [
            '--origin-group-name', 'group', '--origin-name', 'origin', '--host-name', 'origin.example.com',
            '--certificate-name-check-validation-mode', 'CustomCertificateSubject',
            '--custom-certificate-subjects', 'certificate.example.com',
        ], {
            'hostName': 'origin.example.com',
            'certificateNameCheckValidationMode': 'CustomCertificateSubject',
            'customCertificateSubjects': ['certificate.example.com'],
        })

    def test_batch_rules_retain_edge_action_client_response(self):
        action = {'name': 'EdgeAction', 'parameters': {
            'edgeActionReference': {'id': EDGE_ACTION_ID}, 'invocationPoint': 'ClientResponse',
            'typeName': 'DeliveryRuleEdgeActionParameters',
        }}
        rule = {'rule-name': 'r0', 'order': 0, 'actions': [{
            'edge-action': {'parameters': {
                'edge-action-reference': {'id': EDGE_ACTION_ID}, 'invocation-point': 'ClientResponse',
            }},
        }]}
        self._write(AFDRuleSetCreate, COMMON_ARGS + [
            '--rule-set-name', 'rules', '--batch-mode', 'true', '--rules', json.dumps([rule]),
        ], {'batchMode': True, 'rules': [{'ruleName': 'r0', 'order': 0, 'actions': [action]}]})

    def test_nonproduction_override_is_not_exposed_on_update_or_classic_cdn(self):
        from azext_cdn.custom.custom_afdx import AFDProfileUpdate
        for command in (AFDProfileUpdate, CDNProfileCreate, CDNProfileUpdate):
            with self.subTest(command=command.AZ_NAME), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    self._command(command, [
                        '-g', 'rg', '--profile-name', 'profile', '--environment-type', 'NonProduction',
                    ])


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

    api_version = API_VERSION

    def test_legacy_rule_add_uses_stable_api_and_preserves_existing_rules(self):
        from azure.core.pipeline.policies import SansIOHTTPPolicy
        from azext_cdn.custom.custom import add_rule
        from azext_cdn.vendored_sdks import CdnManagementClient

        class Response(HttpResponse):
            def __init__(self, request, payload):
                super().__init__(request, None)
                self.status_code = 200
                self.headers = {'Content-Type': 'application/json'}
                self.reason = 'OK'
                self._payload = payload

            def body(self):
                return json.dumps(self._payload).encode()

            def text(self, encoding=None):
                return self.body().decode(encoding or 'utf-8')

        existing_rule = {'name': 'existing', 'order': 0, 'conditions': [], 'actions': []}
        endpoint = {
            'id': PROFILE_ID + '/endpoints/endpoint', 'name': 'endpoint', 'location': 'global',
            'properties': {
                'provisioningState': 'Succeeded',
                'deliveryPolicy': {'description': 'keep', 'rules': [existing_rule]},
            },
        }
        requests = []
        payloads = [
            {'id': PROFILE_ID, 'name': 'profile', 'location': 'global',
             'sku': {'name': 'Standard_Microsoft'}},
            endpoint,
            endpoint,
        ]

        def send(request, **_kwargs):
            self.assertEqual([API_VERSION], parse_qs(urlparse(request.url).query)['api-version'])
            requests.append(request)
            return Response(request, payloads.pop(0))

        transport = MagicMock(spec=HttpTransport)
        transport.send.side_effect = send
        with CdnManagementClient(
            credential=Mock(), subscription_id=SUBSCRIPTION, transport=transport,
            authentication_policy=SansIOHTTPPolicy(),
        ) as client:
            add_rule(
                self.cli, client, 'rg', 'profile', 'endpoint', order=1, rule_name='new',
                action_name='ModifyResponseHeader', header_action='Overwrite',
                header_name='X-Test', header_value='stable',
            ).result(timeout=5)
        self.assertEqual(['GET', 'GET', 'PATCH'], [request.method for request in requests])
        self.assertFalse(payloads)
        policy = json.loads(requests[-1].body)['properties']['deliveryPolicy']
        self.assertEqual('keep', policy['description'])
        self.assertEqual(existing_rule, policy['rules'][0])
        self.assertEqual('new', policy['rules'][1]['name'])
        self.assertEqual('stable', policy['rules'][1]['actions'][0]['parameters']['value'])

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


class CdnTestConfigurationUnitTest(TestCase):

    def test_existing_endpoint_subscription_is_selected_only_for_its_scenario(self):
        from azure.cli.core._profile import Profile

        other = '11111111-2222-3333-4444-555555555555'
        cached = [{'id': SUBSCRIPTION, 'isDefault': True}, {'id': other, 'isDefault': False}]
        settings = {
            'subscription_id': SUBSCRIPTION, 'cloud': 'AzureCloud', 'arm_endpoint': ARM_URL,
            'fixtures': {'endpoint': PROFILE_ID.replace(SUBSCRIPTION, other) + '/endpoints/endpoint'},
        }
        for method, expected in (('test_existing', [False, True]), ('test_other', [True, False])):
            with self.subTest(method=method), ExitStack() as stack:
                stack.enter_context(patch.object(Profile, 'load_cached_subscriptions', return_value=cached))
                stack.enter_context(patch.object(
                    test_config, 'load_test_config', side_effect=lambda: copy.deepcopy(settings)))
                scenario = SimpleNamespace(
                    in_recording=True, cli_ctx=DummyCli(), addCleanup=stack.callback,
                    _testMethodName=method, subscription_fixture_by_test={'test_existing': 'endpoint'},
                )
                test_config.configure_test_environment(scenario)
                self.assertEqual(expected, [
                    item['isDefault'] for item in Profile(cli_ctx=scenario.cli_ctx).load_cached_subscriptions()
                ])
        self.assertEqual([True, False], [item['isDefault'] for item in cached])
        self.assertEqual(SUBSCRIPTION, settings['subscription_id'])

    def test_local_and_environment_overrides_preserve_other_defaults(self):
        baseline = {
            'subscription_id': SUBSCRIPTION, 'cloud': 'AzureCloud',
            'fixtures': {'classic_profile_id': PROFILE_ID, 'private_link_location': 'EastUS'},
        }
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'config.json').write_text(json.dumps(baseline), encoding='utf-8')
            (path / 'config.local.json').write_text(json.dumps({
                'fixtures': {'private_link_location': 'westus'},
            }), encoding='utf-8')
            override = path / 'override.json'
            override.write_text(json.dumps({'cloud': 'AnotherCloud'}), encoding='utf-8')
            with patch.object(test_config, 'CONFIG_DIR', path), patch.dict(os.environ, {
                'AZURE_CDN_TEST_CONFIG': '', 'AZURE_CDN_TEST_SUBSCRIPTION_ID': '',
                'AZURE_CDN_TEST_CLOUD': '', 'AZURE_CDN_TEST_ARM_ENDPOINT': '',
            }):
                settings = test_config.load_test_config()
                self.assertEqual('westus', settings['fixtures']['private_link_location'])
                self.assertEqual(PROFILE_ID, settings['fixtures']['classic_profile_id'])
                with patch.dict(os.environ, {
                    'AZURE_CDN_TEST_CONFIG': str(override),
                    'AZURE_CDN_TEST_CLOUD': 'EnvironmentCloud',
                }):
                    settings = test_config.load_test_config()
                    self.assertEqual('EnvironmentCloud', settings['cloud'])
                    self.assertEqual(SUBSCRIPTION, settings['subscription_id'])

    def test_recording_selects_configured_subscription_without_mutating_cache(self):
        from azure.cli.core._profile import Profile

        other = '11111111-2222-3333-4444-555555555555'
        cached = [{'id': other, 'isDefault': True}, {'id': SUBSCRIPTION, 'isDefault': False}]
        settings = {'subscription_id': SUBSCRIPTION, 'cloud': 'AzureCloud', 'arm_endpoint': ARM_URL}
        with ExitStack() as stack:
            cache_reader = stack.enter_context(
                patch.object(Profile, 'load_cached_subscriptions', return_value=cached))
            stack.enter_context(patch.object(test_config, 'load_test_config', return_value=settings))
            scenario = SimpleNamespace(in_recording=True, cli_ctx=DummyCli(), addCleanup=stack.callback)
            test_config.configure_test_environment(scenario)
            selected = Profile(cli_ctx=scenario.cli_ctx).load_cached_subscriptions()
            self.assertEqual([False, True], [item['isDefault'] for item in selected])
            self.assertEqual([True, False], [item['isDefault'] for item in cached])
            with patch.dict(settings, {'cloud': 'AnotherCloud'}):
                with self.assertRaisesRegex(ValueError, 'cloud does not match'):
                    Profile(cli_ctx=scenario.cli_ctx).load_cached_subscriptions()
            cache_reader.return_value = [cached[0]]
            with self.assertRaisesRegex(ValueError, 'absent from the Azure CLI account cache'):
                Profile(cli_ctx=scenario.cli_ctx).load_cached_subscriptions()
        self.assertEqual([True, False], [item['isDefault'] for item in cached])

    def test_playback_does_not_read_account_cache_and_maps_fixture_subscription(self):
        with patch.object(test_config, 'load_test_config', side_effect=AssertionError('No live settings needed')):
            test_config.configure_test_environment(SimpleNamespace(in_recording=False))
        vault = '/subscriptions/11111111-2222-3333-4444-555555555555/resourceGroups/byoc/vault'
        with patch.object(test_config, 'load_test_config', return_value={'fixtures': {'vault': vault}}):
            self.assertEqual(
                '/subscriptions/' + SUBSCRIPTION + '/resourceGroups/byoc/vault',
                test_config.fixture('vault', SUBSCRIPTION))
            self.assertEqual(vault, test_config.fixture('vault'))

    def test_invalid_timeout_is_rejected(self):
        for value in (0, -1, True, float('inf'), '300'):
            with self.subTest(value=value), patch.object(test_config, 'load_test_config', return_value={
                'timeouts': {'replay': {'case_seconds': value, 'suite_seconds': 1800}},
            }):
                with self.assertRaisesRegex(ValueError, 'positive, finite'):
                    test_config.timeout_settings('replay')


class CdnTestRunnerUnitTest(TestCase):

    def test_worker_is_directly_waited_and_preserves_virtual_environment(self):
        processes = []
        popen = subprocess.Popen

        def start_worker(*args, **kwargs):
            process = popen(*args, **kwargs)
            processes.append(process)
            return process

        with TemporaryDirectory() as directory:
            log = Path(directory) / 'worker.log'
            script = (
                'import json, os, sys; '
                'print(json.dumps([os.getpid(), sys.prefix, sys.executable])); sys.exit(7)'
            )
            with patch.object(run_tests.subprocess, 'Popen', side_effect=start_worker):
                result = run_tests.run_with_timeout([sys.executable, '-c', script], log, 10)
            worker_pid, prefix, executable = json.loads(log.read_text(encoding='utf-8'))
        self.assertEqual(7, result)
        self.assertEqual(processes[0].pid, worker_pid)
        self.assertEqual(sys.prefix, prefix)
        self.assertEqual(sys.executable, executable)

    def test_hung_worker_is_terminated(self):
        with TemporaryDirectory() as directory:
            result = run_tests.run_with_timeout(
                [sys.executable, '-c', 'import time; time.sleep(60)'],
                Path(directory) / 'worker.log', 0.2)
        self.assertEqual(124, result)

    def test_failed_recordings_are_archived_and_previous_cassettes_restored(self):
        for original in (None, b'previous successful cassette'):
            with self.subTest(original=original), TemporaryDirectory() as directory:
                path = Path(directory)
                recording = path / 'case.yaml'
                temporary = path / 'case.temp.yaml'
                recording.write_bytes(b'failed capture')
                temporary.write_bytes(b'interrupted capture')
                run_tests.preserve_failed_recording(recording, original, path)
                self.assertEqual(b'failed capture', (path / 'failed-recordings' / 'case.yaml').read_bytes())
                self.assertEqual(b'interrupted capture', (path / 'failed-recordings' / 'case.temp.yaml').read_bytes())
                self.assertFalse(temporary.exists())
                if original is None:
                    self.assertFalse(recording.exists())
                else:
                    self.assertEqual(original, recording.read_bytes())

    def test_suite_deadline_prevents_starting_more_workers(self):
        with TemporaryDirectory() as directory, patch.dict(os.environ):
            path = Path(directory)
            (path / 'recordings').mkdir()
            (path / 'recordings' / 'test_one.yaml').write_bytes(b'recorded')
            cases = ['module.Case.test_one', 'module.Case.test_two']
            with patch.object(run_tests, 'TEST_DIR', path), \
                    patch.object(run_tests, 'collect_tests', return_value=cases), \
                    patch.object(run_tests, 'timeout_settings', return_value={
                        'case_seconds': 10, 'suite_seconds': 15}), \
                    patch.object(run_tests, 'run_with_timeout', return_value=0) as worker, \
                    patch.object(run_tests.time, 'time', side_effect=[0, 0, 20]):
                result = run_tests.main(['replay', '--output-dir', str(path)])
            self.assertEqual(1, result)
            worker.assert_called_once()
            results = json.loads((path / 'results.json').read_text(encoding='utf-8'))
            self.assertEqual(['passed', 'not_run'], [item['status'] for item in results])


class AnalyticsTimeRangeUnitTest(TestCase):

    def test_recording_uses_current_utc_time_and_a_five_minute_window(self):
        now = datetime(2031, 4, 3, 10, 20, 30, 123456, tzinfo=timezone.utc)
        scenario = SimpleNamespace(is_playback_mode=lambda: False)
        with patch('azext_cdn.tests.latest.afdx_scenario_mixin.datetime', wraps=datetime) as clock:
            clock.now.return_value = now
            start, end = CdnAfdScenarioMixin.analytics_time_range(scenario, 'getLogAnalyticsMetrics')
        self.assertEqual(now.replace(microsecond=0), start)
        self.assertEqual(timezone.utc, start.tzinfo)
        self.assertEqual(timedelta(minutes=5), end - start)

    def test_playback_preserves_the_matching_recorded_operation_time_range(self):
        query = urlencode({
            'dateTimeBegin': '2031-04-03T10:20:30.000Z',
            'dateTimeEnd': '2031-04-03T10:27:30.000Z',
        })
        for operation in ('getLogAnalyticsMetrics', 'getWafLogAnalyticsMetrics'):
            with self.subTest(operation=operation):
                requests = [
                    SimpleNamespace(method='GET', uri=ARM_URL + '/otherOperation?' + query),
                    SimpleNamespace(method='GET', uri=ARM_URL + '/' + operation + '?' + query),
                ]
                scenario = SimpleNamespace(is_playback_mode=lambda: True, cassette=SimpleNamespace(requests=requests))
                start, end = CdnAfdScenarioMixin.analytics_time_range(scenario, operation)
                self.assertEqual(datetime(2031, 4, 3, 10, 20, 30, tzinfo=timezone.utc), start)
                self.assertEqual(datetime(2031, 4, 3, 10, 27, 30, tzinfo=timezone.utc), end)

    def test_playback_without_a_matching_request_fails_instead_of_using_current_time(self):
        scenario = SimpleNamespace(is_playback_mode=lambda: True, cassette=SimpleNamespace(requests=[]))
        with self.assertRaisesRegex(AssertionError, 'No recorded Analytics time range'):
            CdnAfdScenarioMixin.analytics_time_range(scenario, 'getLogAnalyticsMetrics')


class ClassicCdnFixtureUnitTest(TestCase):

    def test_existing_byoc_keeps_certificate_subscription_scalar_during_playback(self):
        parameters = {'protocolType': 'ServerNameIndication', 'certificateSourceParameters': {
            'subscriptionId': '11111111-2222-3333-4444-555555555555',
            'resourceGroupName': 'vault-rg', 'vaultName': 'vault', 'secretName': 'certificate',
        }}
        settings = {
            'byoc_vault_id': '/subscriptions/11111111-2222-3333-4444-555555555555/'
                             'resourceGroups/vault-rg/providers/Microsoft.KeyVault/vaults/vault',
            'classic_byoc_secret_name': 'certificate',
        }
        scenario = SimpleNamespace(
            assertEqual=self.assertEqual, _https_state_check=Mock(),
            custom_domain_show_cmd=Mock(return_value=SimpleNamespace(
                get_output_in_json=lambda: {'customHttpsParameters': parameters})),
        )
        scenario_type = custom_domain_scenarios.CdnCustomDomainScenarioTest
        with patch.object(custom_domain_scenarios, 'fixture', side_effect=settings.__getitem__):
            result = scenario_type._existing_https_parameters(  # pylint: disable=protected-access
                scenario, 'rg', 'profile', 'endpoint', 'domain', 'www.example.com', 'AzureKeyVault')
        self.assertEqual(parameters, result)

    def test_https_accepts_only_deployed_or_matching_pending_certificate_state(self):
        scenario_type = custom_domain_scenarios.CdnCustomDomainScenarioTest
        for source, pending in (('Cdn', 'SubmittingDomainControlValidationRequest'),
                                ('AzureKeyVault', 'ImportingUserProvidedCertificate')):
            check = scenario_type._https_state_check(source)  # pylint: disable=protected-access
            for state, substate, accepted in (
                    ('Enabled', 'CertificateDeployed', True),
                    ('Enabling', pending, True),
                    ('Enabling', 'DeployingCertificate', True),
                    ('Enabling', 'CertificateDeployed', False),
                    ('Enabling', 'DomainControlValidationRequestRejected', False),
                    ('Enabling', 'DomainControlValidationRequestTimedOut', False),
                    ('Enabling', 'CertificateRejected', False),
                    ('Enabling', 'DeletingCertificate', False),
                    ('Enabling', 'Unknown', False),
                    ('Enabling', 'ImportingUserProvidedCertificate', source == 'AzureKeyVault'),
                    ('Enabling', 'PendingDomainControlValidationRequestApproval', source == 'Cdn'),
                    ('Enabled', pending, False),
                    ('Failed', pending, False),
                    ('Disabled', pending, False)):
                with self.subTest(source=source, state=state, substate=substate):
                    result = SimpleNamespace(output='', get_output_in_json=lambda state=state, substate=substate: {
                        'customHttpsProvisioningState': state, 'customHttpsProvisioningSubstate': substate,
                    })
                    if accepted:
                        check(result)
                    else:
                        with self.assertRaises(JMESPathCheckAssertionError):
                            check(result)

    def test_existing_endpoint_fixture_does_not_create_or_register_deletion(self):
        scenario = self._scenario()
        scenario.endpoint_show_cmd = Mock()
        endpoint_id = PROFILE_ID + '/endpoints/existing'
        with patch('azext_cdn.tests.latest.scenario_mixin.fixture', return_value=endpoint_id):
            self.assertEqual(('rg', 'profile', 'existing'), scenario.classic_cdn_endpoint('endpoint'))
        scenario.endpoint_show_cmd.assert_called_once_with('rg', 'existing', 'profile')
        scenario.addCleanup.assert_not_called()
        scenario.cmd.assert_not_called()
        with self.assertRaisesRegex(ValueError, 'must not be deleted'):
            scenario.profile_delete_cmd('rg', 'profile')

    def test_repeated_byoc_enable_preserves_latest_or_fixed_version(self):
        for version in (None, 'fixed-version', 'omitted'):
            with self.subTest(version=version):
                parameters = {'certificateSourceParameters': {
                    'subscriptionId': SUBSCRIPTION, 'resourceGroupName': 'vault-rg', 'vaultName': 'vault',
                    'secretName': 'certificate', 'secretVersion': version,
                }}
                if version == 'omitted':
                    parameters['certificateSourceParameters'].pop('secretVersion')
                scenario = SimpleNamespace(
                    custom_domain_enable_https_command=Mock(), _assert_https_unchanged=Mock(),
                )
                custom_domain_scenarios.CdnCustomDomainScenarioTest._repeat_byoc_https(  # pylint: disable=protected-access
                    scenario, 'rg', 'profile', 'endpoint', 'domain', parameters)
                scenario.custom_domain_enable_https_command.assert_called_once_with(
                    'rg', 'profile', 'endpoint', 'domain',
                    user_cert_subscription_id=SUBSCRIPTION, user_cert_group_name='vault-rg',
                    user_cert_vault_name='vault', user_cert_secret_name='certificate',
                    user_cert_secret_version=None if version == 'omitted' else version,
                    user_cert_protocol_type='sni', min_tls_version='1.2')
                scenario._assert_https_unchanged.assert_called_once_with(  # pylint: disable=protected-access
                    'rg', 'profile', 'endpoint', 'domain', parameters)

    @staticmethod
    def _scenario():
        scenario = CdnScenarioMixin()
        scenario.get_subscription_id = Mock(return_value=SUBSCRIPTION)
        scenario.cmd = Mock()
        scenario.addCleanup = Mock()
        scenario.profile_show_cmd = Mock(return_value=SimpleNamespace(
            get_output_in_json=lambda: {'sku': {'name': 'Standard_Microsoft'}},
        ))
        return scenario

    def test_existing_profile_rejects_another_subscription_or_sku(self):
        scenario = self._scenario()
        other_subscription = '11111111-2222-3333-4444-555555555555'
        resource_id = PROFILE_ID.replace(SUBSCRIPTION, other_subscription)
        with patch.dict(os.environ, {'AZURE_CDN_TEST_PROFILE_ID': resource_id}):
            with self.assertRaisesRegex(ValueError, 'test subscription'):
                scenario.classic_cdn_profile()
        scenario.profile_show_cmd.assert_not_called()

        scenario.profile_show_cmd.return_value.get_output_in_json = lambda: {
            'sku': {'name': 'Standard_AzureFrontDoor'},
        }
        with patch.dict(os.environ, {'AZURE_CDN_TEST_PROFILE_ID': PROFILE_ID}):
            with self.assertRaisesRegex(ValueError, 'Standard_Microsoft'):
                scenario.classic_cdn_profile()

    def test_shared_profile_and_existing_endpoints_cannot_be_deleted_or_overwritten(self):
        scenario = self._scenario()
        with patch.dict(os.environ, {'AZURE_CDN_TEST_PROFILE_ID': PROFILE_ID}):
            group, profile = scenario.classic_cdn_profile()
        with self.assertRaisesRegex(ValueError, 'must not be deleted'):
            scenario.profile_delete_cmd(group, profile)

        scenario.endpoint_show_cmd = Mock()
        with self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
            scenario.endpoint_create_cmd(group, 'existing', profile, 'origin.example')
        scenario.cmd.assert_not_called()
        scenario.addCleanup.assert_not_called()

    def test_endpoint_cleanup_is_registered_before_a_failed_create(self):
        scenario = self._scenario()
        with patch.dict(os.environ, {'AZURE_CDN_TEST_PROFILE_ID': PROFILE_ID}):
            group, profile = scenario.classic_cdn_profile()
        scenario.endpoint_show_cmd = Mock(side_effect=ResourceNotFoundError())
        scenario.cmd.side_effect = CLIError('Creation failed')
        with self.assertRaisesRegex(CLIError, 'Creation failed'):
            scenario.endpoint_create_cmd(group, 'owned', profile, 'origin.example')
        scenario.addCleanup.assert_called_once_with(
            scenario._cleanup_classic_endpoint, group, 'owned', profile,  # pylint: disable=protected-access
        )
        scenario.endpoint_delete_cmd = Mock(side_effect=ResourceNotFoundError())
        callback, *arguments = scenario.addCleanup.call_args.args
        callback(*arguments)
        scenario.endpoint_delete_cmd.assert_called_once_with(group, 'owned', profile)
