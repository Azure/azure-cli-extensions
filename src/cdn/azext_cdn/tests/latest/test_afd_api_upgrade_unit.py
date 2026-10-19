# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import copy
import io
import json
from contextlib import ExitStack, redirect_stderr
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qs, urlparse

from azure.core import PipelineClient
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.core.polling import NoPolling
from azure.cli.core.aaz import AAZUndefined, AAZWaitCommand
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.aaz._paging import AAZPaged
from azure.cli.core.aaz._poller import AAZLROPoller
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.mock import DummyCli

from azext_cdn.aaz.latest.afd import auth_policy, custom_domain, origin, origin_group, route, rule_set
from azext_cdn.aaz.latest.afd.rule import action as rule_action
from azext_cdn.aaz.latest.cdn import origin_group as cdn_origin_group
from azext_cdn.aaz.latest.cdn.profile import deployment_version
from azext_cdn.custom.custom_afdx import (
    AFDCustomDomainCreate, AFDCustomDomainUpdate, AFDOriginCreate, AFDOriginUpdate,
    AFDOriginGroupUpdate, AFDRouteCreate, AFDRouteUpdate, AFDRuleCreate,
    AFDRuleActionAdd, AFDRuleActionRemove, AFDRuleActionShow, AFDRuleActionUpdate,
)
from azext_cdn.custom.custom_cdn import CDNEndpointCreate


SUBSCRIPTION = '00000000-0000-0000-0000-000000000000'
API_VERSION = '2026-09-01-preview'
ARM_URL = 'https://management.azure.com'
PROFILE_ID = (
    f'/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Cdn/profiles/profile'
)
POLICY_ID = PROFILE_ID + '/authPolicies/policy'
DOMAIN_ID = PROFILE_ID + '/customDomains/domain'
ROUTE_ID = PROFILE_ID + '/afdEndpoints/endpoint/routes/route'
EDGE_ACTION_ID = f'/subscriptions/{SUBSCRIPTION}/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action'
COMMON_ARGS = ['--resource-group', 'rg', '--profile-name', 'profile']
POLICY_ARGS = COMMON_ARGS + ['--auth-policy-name', 'policy']
ENTRA_CONFIG = "[{entra-id:{audiences:[audience],issuer:'https://issuer.example/v2.0'}}]"
EDGE_ACTION = (
    '{edge-action:{parameters:{edge-action-reference:{id:' + EDGE_ACTION_ID
    + '},invocation-point:ClientResponse}}}'
)


class OfflineAazTest(TestCase):

    def setUp(self):
        self.contexts = ExitStack()
        self.addCleanup(self.contexts.close)
        config_dir = TemporaryDirectory()
        self.addCleanup(config_dir.cleanup)
        environment = self.contexts.enter_context(patch.dict('os.environ', {
            'AZURE_CONFIG_DIR': config_dir.name,
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
        self.pollings = []

    def _send_request(self, request, stream=False, **_kwargs):
        self.assertFalse(stream)
        self.assertTrue(self.responses, f'Unexpected request: {request.method} {request.url}')
        method, status, body = self.responses.pop(0)
        self.assertEqual(method, request.method)
        self.assertEqual([API_VERSION], parse_qs(urlparse(request.url).query)['api-version'])
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

    def _build_polling(self, no_wait, session, deserialize, _on_error, **_kwargs):
        polling = Mock(spec=NoPolling)
        polling.resource.side_effect = lambda: deserialize(session)
        self.pollings.append((bool(no_wait), polling))
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
        self.pollings = []
        command, parsed = self._command(command_type, arguments)
        if isinstance(command, AAZWaitCommand):
            # Exercise the generated getter, not the unchanged core wait-condition loop.
            result = command._handler(parsed)  # pylint: disable=protected-access
        else:
            result = command(command_args=parsed)
        if isinstance(result, AAZLROPoller):
            result = result.result(timeout=5)
        elif isinstance(result, AAZPaged):
            result = list(result)
        self.assertFalse(self.responses, 'Not all expected requests were sent')
        return result

    def _body(self):
        return json.loads(self.requests[-1].body)

    @staticmethod
    def _resource(properties):
        return {
            'id': POLICY_ID,
            'name': 'policy',
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
        output_properties = output['properties'] if command_type in (auth_policy.Create, auth_policy.Update) else output
        for key, value in properties.items():
            self.assertEqual(value, sent[key], key)
            self.assertEqual(value, output_properties[key], key)
        self.assertNotIn('provisioningState', sent)
        self.assertNotIn('deploymentStatus', sent)
        return output

    def _assert_invalid(self, command_type, arguments):
        with redirect_stderr(io.StringIO()), self.assertRaises((InvalidArgumentValueError, SystemExit)):
            self._invoke(command_type, arguments)
        self.assertEqual([], self.requests)


class AuthPolicyUnitTest(OfflineAazTest):

    @staticmethod
    def _properties():
        return {
            'action': 'Block',
            'forwardTokenToOrigin': True,
            'associations': {'isProfileLevel': True},
            'authConfigs': [{
                'identityProvider': 'EntraID',
                'audiences': ['audience'],
                'issuer': 'https://issuer.example/v2.0',
            }],
        }

    @staticmethod
    def _create_args():
        return POLICY_ARGS + [
            '--associations', '{is-profile-level:true}', '--auth-configs', ENTRA_CONFIG,
        ]

    def test_auth_policy_create_defaults(self):
        output = self._write(auth_policy.Create, self._create_args(), self._properties())
        self.assertEqual(POLICY_ID, output['id'])
        self.assertEqual(POLICY_ID, urlparse(self.requests[0].url).path)
        self.assertNotIn('entra-id', self._body()['properties']['authConfigs'][0])
        self.assertNotIn('entra_id', self._body()['properties']['authConfigs'][0])
        self.assertNotIn('authLocation', self._body()['properties']['authConfigs'][0])

    def test_auth_policy_create_actions_and_forwarding_aliases(self):
        for action in ('Block', 'Log'):
            for alias in ('--forward-token', '--forward-token-to-origin'):
                for forwarding in (True, False):
                    with self.subTest(action=action, alias=alias, forwarding=forwarding):
                        expected = self._properties()
                        expected.update(action=action, forwardTokenToOrigin=forwarding)
                        self._write(auth_policy.Create, self._create_args() + [
                            '--action', action, alias, str(forwarding).lower(),
                        ], expected)

    def test_auth_policy_associations_and_limits(self):
        for count in (1, 15):
            with self.subTest(count=count):
                domains = [{'id': DOMAIN_ID + str(index)} for index in range(count)]
                routes = [{'id': ROUTE_ID + str(index)} for index in range(count)]
                associations = (
                    '{is-profile-level:false,domains:['
                    + ','.join('{id:' + item['id'] + '}' for item in domains)
                    + '],routes:['
                    + ','.join('{id:' + item['id'] + '}' for item in routes) + ']}'
                )
                expected = self._properties()
                expected['associations'] = {'isProfileLevel': False, 'domains': domains, 'routes': routes}
                self._write(auth_policy.Create, POLICY_ARGS + [
                    '--auth-configs', ENTRA_CONFIG, '--associations', associations,
                ], expected)
        for field in ('domains', 'routes'):
            with self.subTest(over_limit=field):
                value = '{' + field + ':[' + ','.join('{id:' + DOMAIN_ID + '}' for _ in range(16)) + ']}'
                self._assert_invalid(auth_policy.Create, POLICY_ARGS + [
                    '--auth-configs', ENTRA_CONFIG, '--associations', value,
                ])

    def test_auth_policy_validation(self):
        invalid_configs = [
            '[]',
            "[{entra-id:{issuer:'https://issuer.example'}}]",
            '[{entra-id:{audiences:[audience]}}]',
            "[{entra-id:{audiences:[],issuer:'https://issuer.example'}}]",
            "[{entra-id:{audiences:[audience],issuer:'https://issuer.example',auth-location:QueryString}}]",
        ]
        for config in invalid_configs:
            with self.subTest(config=config):
                self._assert_invalid(auth_policy.Create, POLICY_ARGS + [
                    '--auth-configs', config, '--associations', '{is-profile-level:true}',
                ])

    def test_auth_policy_update_preserves_existing_fields(self):
        existing = self._properties()
        expected = copy.deepcopy(existing)
        expected.update(action='Log', forwardTokenToOrigin=False)
        expected['authConfigs'][0]['authLocation'] = 'Header'
        expected['authConfigs'][0]['authLocationSelector'] = 'Authorization'
        config = (
            "[{entra-id:{audiences:[audience],issuer:'https://issuer.example/v2.0',"
            'auth-location:Header,auth-location-selector:Authorization}}]'
        )
        self._write(auth_policy.Update, POLICY_ARGS + [
            '--action', 'Log', '--forward-token', 'false', '--auth-configs', config,
        ], expected, existing)
        self.assertEqual(['GET', 'PUT'], [request.method for request in self.requests])

    def test_auth_policy_update_associations_and_forwarding_aliases(self):
        for alias in ('--forward-token', '--forward-token-to-origin'):
            with self.subTest(alias=alias):
                existing = self._properties()
                expected = copy.deepcopy(existing)
                expected['forwardTokenToOrigin'] = False
                expected['associations'] = {
                    'isProfileLevel': False,
                    'domains': [{'id': DOMAIN_ID}],
                    'routes': [{'id': ROUTE_ID}],
                }
                associations = (
                    '{is-profile-level:false,domains:[{id:' + DOMAIN_ID
                    + '}],routes:[{id:' + ROUTE_ID + '}]}'
                )
                self._write(auth_policy.Update, POLICY_ARGS + [
                    alias, 'false', '--associations', associations,
                ], expected, existing)

    def test_auth_policy_show_and_wait_getter(self):
        policy = self._resource(self._properties())
        policy['properties']['authConfigs'][0]['authLocation'] = 'Header'
        policy['properties']['associations']['domains'] = [{'id': DOMAIN_ID, 'isActive': True}]
        for command_type in (auth_policy.Show, auth_policy.Wait):
            with self.subTest(command=command_type.AZ_NAME):
                output = self._invoke(command_type, POLICY_ARGS, [('GET', 200, policy)])
                self.assertEqual(policy, output)
                self.assertEqual(POLICY_ID, urlparse(self.requests[0].url).path)

    def test_auth_policy_list_empty_and_paginated(self):
        self.assertEqual([], self._invoke(auth_policy.List, COMMON_ARGS, [('GET', 200, {'value': []})]))
        policy = self._resource(self._properties())
        second = copy.deepcopy(policy)
        second.update(id=POLICY_ID + '2', name='policy2')
        next_link = ARM_URL + PROFILE_ID + '/authPolicies?api-version=' + API_VERSION + '&page=2'
        output = self._invoke(auth_policy.List, COMMON_ARGS, [
            ('GET', 200, {'value': [policy], 'nextLink': next_link}),
            ('GET', 200, {'value': [second]}),
        ])
        self.assertEqual([policy, second], output)
        self.assertEqual(['2'], parse_qs(urlparse(self.requests[1].url).query)['page'])

    def test_auth_policy_lro_modes(self):
        for command_type in (auth_policy.Create, auth_policy.Update):
            for status in (200, 201, 202):
                for no_wait in (False, True):
                    with self.subTest(command=command_type.AZ_NAME, status=status, no_wait=no_wait):
                        arguments = self._create_args() + (['--no-wait'] if no_wait else [])
                        resource = self._resource(self._properties())
                        responses = [('GET', 200, resource)] if command_type is auth_policy.Update else []
                        responses.append(('PUT', status, resource))
                        with patch.object(command_type, 'post_operations') as post_operations:
                            output = self._invoke(command_type, arguments, responses)
                        actual_no_wait, polling = self.pollings[0]
                        self.assertEqual(no_wait, actual_no_wait)
                        if no_wait:
                            self.assertIsNone(output)
                            polling.run.assert_not_called()
                            polling.resource.assert_not_called()
                            post_operations.assert_not_called()
                        else:
                            self.assertEqual('Succeeded', output['properties']['provisioningState'])
                            polling.run.assert_called_once_with()
                            polling.resource.assert_called_once_with()
                            post_operations.assert_called_once_with()

    def test_auth_policy_delete_statuses(self):
        for status in (200, 202, 204):
            for no_wait in (False, True):
                with self.subTest(status=status, no_wait=no_wait):
                    arguments = POLICY_ARGS + (['--no-wait'] if no_wait else [])
                    self.assertIsNone(self._invoke(auth_policy.Delete, arguments, [('DELETE', status, None)]))
                    self.assertEqual(POLICY_ID, urlparse(self.requests[0].url).path)
                    self.assertEqual(no_wait, self.pollings[0][0])

    def test_auth_policy_initial_errors(self):
        error = {'error': {'code': 'MockFailure', 'message': 'The policy request failed.'}}
        for command_type, arguments, method in (
                (auth_policy.Create, self._create_args(), 'PUT'),
                (auth_policy.Update, POLICY_ARGS + ['--action', 'Log'], 'GET'),
                (auth_policy.Show, POLICY_ARGS, 'GET'),
                (auth_policy.List, COMMON_ARGS, 'GET'),
                (auth_policy.Delete, POLICY_ARGS, 'DELETE')):
            for status in (400, 401, 404, 409, 500):
                with self.subTest(command=command_type.AZ_NAME, status=status):
                    with patch.object(command_type, 'post_operations') as post_operations:
                        with self.assertRaises(HttpResponseError):
                            self._invoke(command_type, arguments, [(method, status, error)])
                    self.assertEqual([], self.pollings)
                    self.assertEqual(1, len(self.requests))
                    post_operations.assert_not_called()


class AfdApiUpgradeUnitTest(OfflineAazTest):

    def test_custom_domain_tls_groups(self):
        groups = [
            'SecP256r1MLKEM768', 'SecP384r1MLKEM1024', 'X25519',
            'X25519MLKEM768', 'prime256v1', 'secp384r1', 'secp521r1',
        ]
        for command_type in (AFDCustomDomainCreate, AFDCustomDomainUpdate):
            for policy in ('Custom', 'Enhanced', 'Standard'):
                for alias in ('--tls-group-policy', '--server-tls-group-policy'):
                    with self.subTest(command=command_type.AZ_NAME, policy=policy, alias=alias):
                        existing = {
                            'hostName': 'cdn.example',
                            'tlsSettings': {'certificateType': 'ManagedCertificate'},
                        }
                        properties = copy.deepcopy(existing)
                        properties['tlsSettings']['serverTlsGroupPolicy'] = policy
                        arguments = COMMON_ARGS + ['--custom-domain-name', 'domain', alias, policy]
                        if command_type is AFDCustomDomainCreate:
                            arguments += ['--host-name', 'cdn.example', '--certificate-type', 'ManagedCertificate']
                        if policy == 'Custom':
                            properties['tlsSettings']['serverTlsGroups'] = groups
                            arguments += ['--server-tls-groups', '[' + ','.join(groups) + ']']
                        self._write(command_type, arguments, properties,
                                    existing if command_type is AFDCustomDomainUpdate else None)

    def test_origin_certificate_modes_and_subjects(self):
        for command_type in (AFDOriginCreate, AFDOriginUpdate):
            for mode in ('OriginHostname', 'IncomingHostHeader', 'CustomCertificateSubject'):
                for long_names in (False, True):
                    with self.subTest(command=command_type.AZ_NAME, mode=mode, long_names=long_names):
                        existing = {'hostName': 'origin.example', 'originHostHeader': 'keep.example'}
                        properties = dict(existing, certificateNameCheckValidationMode=mode)
                        mode_option = (
                            '--certificate-name-check-validation-mode' if long_names else '--cert-name-check-mode'
                        )
                        arguments = COMMON_ARGS + [
                            '--origin-group-name', 'group', '--origin-name', 'origin', mode_option, mode,
                        ]
                        if command_type is AFDOriginCreate:
                            arguments += ['--host-name', 'origin.example', '--origin-host-header', 'keep.example']
                        if mode == 'CustomCertificateSubject':
                            subjects = ['origin.example', '*.example'] if long_names else ['origin.example']
                            properties['customCertificateSubjects'] = subjects
                            option = '--custom-certificate-subjects' if long_names else '--cert-subjects'
                            arguments += [option, '[' + ','.join(subjects) + ']']
                        self._write(command_type, arguments, properties,
                                    existing if command_type is AFDOriginUpdate else None)

    def test_origin_group_capacity_distribution(self):
        for command_type in (origin_group.Create, AFDOriginGroupUpdate):
            for distribution in ('DynamicWeights', 'StaticWeights'):
                for threshold, alias in ((20, '--capacity-settings'), (100, '--capacity-distribution-settings')):
                    with self.subTest(command=command_type.AZ_NAME, distribution=distribution, threshold=threshold):
                        existing = {
                            'loadBalancingSettings': {'sampleSize': 4, 'successfulSamplesRequired': 3},
                            'healthProbeSettings': {'probePath': '/', 'probeProtocol': 'Https'},
                        }
                        properties = copy.deepcopy(existing)
                        properties['healthProbeSettings']['probeProtocol'] = 'Grpc'
                        properties['loadBalancingSettings']['capacityDistributionSettings'] = {
                            'capacityConsciousThreshold': threshold, 'distributionType': distribution,
                        }
                        arguments = COMMON_ARGS + [
                            '--origin-group-name', 'group', '--probe-protocol', 'Grpc', alias,
                            '{capacity-conscious-threshold:' + str(threshold)
                            + ',distribution-type:' + distribution + '}',
                        ]
                        if command_type is origin_group.Create:
                            arguments += [
                                '--probe-path', '/', '--sample-size', '4', '--successful-samples-required', '3',
                            ]
                        self._write(command_type, arguments, properties,
                                    existing if command_type is AFDOriginGroupUpdate else None)

    def test_route_grpc_and_origin_group_normalization(self):
        for command_type in (AFDRouteCreate, AFDRouteUpdate):
            for state in ('Disabled', 'Enabled'):
                with self.subTest(command=command_type.AZ_NAME, state=state):
                    existing = {'originPath': '/keep'}
                    properties = dict(existing, grpcState=state, originGroup={'id': PROFILE_ID + '/originGroups/group'})
                    arguments = COMMON_ARGS + [
                        '--endpoint-name', 'endpoint', '--route-name', 'route',
                        '--grpc-state', state, '--origin-group', 'group',
                    ]
                    if command_type is AFDRouteCreate:
                        arguments += ['--origin-path', '/keep']
                    self._write(command_type, arguments, properties,
                                existing if command_type is AFDRouteUpdate else None)

    def test_new_properties_in_read_commands(self):
        cases = [
            (custom_domain, ['--custom-domain-name', 'domain'],
             {'tlsSettings': {'serverTlsGroupPolicy': 'Custom', 'serverTlsGroups': ['X25519MLKEM768']}}),
            (origin, ['--origin-group-name', 'group', '--origin-name', 'origin'],
             {'certificateNameCheckValidationMode': 'CustomCertificateSubject',
              'customCertificateSubjects': ['origin.example']}),
            (origin_group, ['--origin-group-name', 'group'],
             {'loadBalancingSettings': {'capacityDistributionSettings': {
                 'capacityConsciousThreshold': 80, 'distributionType': 'DynamicWeights'}},
              'healthProbeSettings': {'probeProtocol': 'Grpc'}}),
            (route, ['--endpoint-name', 'endpoint', '--route-name', 'route'], {'grpcState': 'Enabled'}),
        ]
        for module, arguments, properties in cases:
            for command_type in (module.Show, module.List, module.Wait):
                with self.subTest(command=command_type.AZ_NAME):
                    tokens = COMMON_ARGS + arguments
                    if command_type is module.List:
                        tokens = tokens[:-2]
                    resource = self._resource(properties)
                    response = {'value': [resource]} if command_type is module.List else resource
                    output = self._invoke(command_type, tokens, [('GET', 200, response)])
                    expected = resource if command_type is module.Wait else {
                        'id': resource['id'], 'name': resource['name'], **resource['properties'],
                    }
                    self.assertEqual([expected] if command_type is module.List else expected, output)

    def test_invalid_feature_arguments(self):
        origin_args = COMMON_ARGS + [
            '--origin-group-name', 'group', '--origin-name', 'origin', '--host-name', 'origin.example',
        ]
        group_args = COMMON_ARGS + ['--origin-group-name', 'group']
        domain_args = COMMON_ARGS + [
            '--custom-domain-name', 'domain', '--host-name', 'cdn.example',
            '--certificate-type', 'ManagedCertificate',
        ]
        route_args = COMMON_ARGS + ['--endpoint-name', 'endpoint', '--route-name', 'route']
        cases = [
            (AFDOriginCreate, origin_args, ['--cert-subjects', '[]']),
            (AFDOriginCreate, origin_args, ['--cert-subjects', '[a.example,b.example,c.example]']),
            (AFDOriginUpdate, origin_args, ['--cert-subjects', '[a.example,b.example,c.example]']),
            (AFDOriginCreate, origin_args, ['--cert-name-check-mode', 'InvalidMode']),
            (origin_group.Create, group_args, ['--capacity-settings', '{capacity-conscious-threshold:19}']),
            (origin_group.Create, group_args, ['--capacity-settings', '{capacity-conscious-threshold:101}']),
            (AFDOriginGroupUpdate, group_args, ['--capacity-settings', '{capacity-conscious-threshold:101}']),
            (origin_group.Create, group_args, ['--capacity-settings', '{distribution-type:InvalidType}']),
            (AFDCustomDomainCreate, domain_args, ['--tls-group-policy', 'InvalidPolicy']),
            (AFDCustomDomainUpdate, domain_args, ['--server-tls-groups', '[InvalidGroup]']),
            (AFDRouteCreate, route_args, ['--grpc-state', 'InvalidState']),
        ]
        for command_type, arguments, invalid in cases:
            with self.subTest(command=command_type.AZ_NAME, invalid=invalid):
                self._assert_invalid(command_type, arguments + invalid)

    def test_cdn_grpc_probes(self):
        for command_type in (cdn_origin_group.Create, cdn_origin_group.Update):
            with self.subTest(command=command_type.AZ_NAME):
                properties = {'healthProbeSettings': {'probeProtocol': 'Grpc', 'probePath': '/'}}
                arguments = COMMON_ARGS + [
                    '--endpoint-name', 'endpoint', '--origin-group-name', 'group',
                    '--health-probe-settings', '{probe-protocol:Grpc,probe-path:/}',
                ]
                self._write(command_type, arguments, properties,
                            {'healthProbeSettings': {'probeProtocol': 'Https', 'probePath': '/'}}
                            if command_type is cdn_origin_group.Update else None)

    def test_edge_action_client_response(self):
        for command_type in (AFDRuleCreate, rule_set.Create):
            with self.subTest(command=command_type.AZ_NAME):
                arguments = COMMON_ARGS + ['--rule-set-name', 'rules']
                edge = {'name': 'EdgeAction', 'parameters': {
                    'edgeActionReference': {'id': EDGE_ACTION_ID}, 'invocationPoint': 'ClientResponse',
                    'typeName': 'DeliveryRuleEdgeActionParameters',
                }}
                if command_type is AFDRuleCreate:
                    arguments += ['--rule-name', 'rule', '--order', '0', '--actions', '[' + EDGE_ACTION + ']']
                    properties = {'actions': [edge], 'order': 0}
                else:
                    arguments += [
                        '--batch-mode', 'true', '--rules',
                        '[{rule-name:responseRule,order:0,actions:[' + EDGE_ACTION + ']}]',
                    ]
                    properties = {
                        'batchMode': True,
                        'rules': [{'ruleName': 'responseRule', 'order': 0, 'actions': [edge]}],
                    }
                self._invoke(command_type, arguments, [('PUT', 200, self._resource(properties))])
                body = self._body()['properties']
                action = body['actions'][0] if command_type is AFDRuleCreate else body['rules'][0]['actions'][0]
                self.assertEqual('ClientResponse', action['parameters']['invocationPoint'])
                self.assertEqual({'id': EDGE_ACTION_ID}, action['parameters']['edgeActionReference'])
                self.assertEqual('DeliveryRuleEdgeActionParameters', action['parameters']['typeName'])
                if command_type is rule_set.Create:
                    self.assertEqual('responseRule', body['rules'][0]['ruleName'])

    def test_rule_action_property_commands(self):
        arguments = COMMON_ARGS + ['--rule-set-name', 'rules', '--rule-name', 'rule']
        action = {'name': 'EdgeAction', 'parameters': {
            'edgeActionReference': {'id': EDGE_ACTION_ID}, 'invocationPoint': 'ClientResponse',
            'typeName': 'DeliveryRuleEdgeActionParameters',
        }}
        empty = self._resource({'actions': [], 'order': 0})
        populated = self._resource({'actions': [action], 'order': 0})
        edge_parameters = (
            '{parameters:{edge-action-reference:{id:' + EDGE_ACTION_ID + '},invocation-point:ClientResponse}}'
        )
        named_args = arguments + ['--action-name', 'EdgeAction']
        output = self._invoke(AFDRuleActionAdd, named_args + ['--edge-action', edge_parameters], [
            ('GET', 200, empty), ('PUT', 200, populated),
        ])
        self.assertEqual('ClientResponse', output['parameters']['invocationPoint'])
        self.assertEqual(0, self._body()['properties']['order'])
        self.assertEqual('ClientResponse', self._body()['properties']['actions'][0]['parameters']['invocationPoint'])
        self.assertEqual([action], self._invoke(rule_action.List, arguments, [('GET', 200, populated)]))
        self.assertEqual(action, self._invoke(AFDRuleActionShow, named_args, [('GET', 200, populated)]))
        output = self._invoke(AFDRuleActionUpdate, named_args + ['--edge-action', edge_parameters], [
            ('GET', 200, populated), ('PUT', 200, populated),
        ])
        self.assertEqual(action, output)
        self._invoke(AFDRuleActionRemove, named_args, [('GET', 200, populated), ('PUT', 200, empty)])
        self.assertEqual([], self._body()['properties']['actions'])

    def test_cdn_endpoint_shared_enums(self):
        origin_id = PROFILE_ID + '/endpoints/endpoint/origins/origin-example'
        arguments = COMMON_ARGS + [
            '--endpoint-name', 'endpoint', '--location', 'global', '--origin', 'origin.example',
            '--delivery-policy', '{rules:[{name:responseRule,order:0,actions:[' + EDGE_ACTION + ']}]}',
            '--origin-groups',
            '[{name:group,origins:[{id:' + origin_id + '}],health-probe-settings:{probe-protocol:Grpc}}]',
        ]
        self._invoke(CDNEndpointCreate, arguments, [('PUT', 200, self._resource({}))])
        properties = self._body()['properties']
        edge_parameters = properties['deliveryPolicy']['rules'][0]['actions'][0]['parameters']
        self.assertEqual('ClientResponse', edge_parameters['invocationPoint'])
        self.assertEqual('DeliveryRuleEdgeActionParameters', edge_parameters['typeName'])
        self.assertEqual('Grpc', properties['originGroups'][0]['properties']['healthProbeSettings']['probeProtocol'])

    def test_deployment_version_api_remains_pinned(self):
        commands = (
            deployment_version.Approve, deployment_version.Compare, deployment_version.List,
            deployment_version.Show, deployment_version.Update,
        )
        for command_type in commands:
            with self.subTest(command=command_type.AZ_NAME):
                info = command_type._aaz_info  # pylint: disable=protected-access
                self.assertEqual('2025-09-01-preview', info['version'])
                self.assertTrue(all(resource[2] == '2025-09-01-preview'
                                    for resource in info['resources']))
