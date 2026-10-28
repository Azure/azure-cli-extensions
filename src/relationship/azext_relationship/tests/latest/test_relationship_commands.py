# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import copy
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch
from urllib.parse import parse_qs, urlsplit

from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand, AAZHttpOperation
from azure.cli.testsdk.scenario_tests import GeneralNameReplacer
from azure.core import PipelineClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

from azext_relationship import RelationshipCommandsLoader
from azext_relationship.tests.latest import test_relationship_scenario


SUBSCRIPTION = '00000000-0000-0000-0000-000000000001'
RESOURCE_URI = f'/subscriptions/{SUBSCRIPTION}/resourceGroups/relationship-test'
SERVICE_GROUP = '/providers/Microsoft.Management/serviceGroups/sourceSG'
TARGET = '/providers/Microsoft.Management/serviceGroups/targetSG'
TENANT = '00000000-0000-0000-0000-000000000002'
VERSION = '2026-08-01'
# Terminate the URL literal so credential scanning cannot join it to a later decorator.
ARM = 'https://management.azure.com/'.rstrip('/')
WRITABLE_GROUPS = ('dependency-of', 'service-group-member', 'dependency-of-by-service-group')


class RelationshipCommandTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cli_ctx = get_default_cli()
        cls.commands = RelationshipCommandsLoader(cls.cli_ctx).load_command_table(None)

    def _command(self, group, verb, **overrides):
        command_type = type(self.commands[f'relationship {group} {verb}'])
        command = command_type(loader=RelationshipCommandsLoader(self.cli_ctx))
        arguments = {
            'subscription': SUBSCRIPTION,
            'resource_uri': RESOURCE_URI,
            'service_group_name': 'sourceSG',
            'name': 'test.relationship-1',
        }
        if verb == 'create':
            arguments.update({'target_id': TARGET, 'source_id': SERVICE_GROUP})
        arguments.update(overrides)
        AAZCommand._handler(command, arguments)
        client = Mock(wraps=PipelineClient(base_url=ARM))
        command.ctx._clients['MgmtClient'] = client
        return command, client

    @staticmethod
    def _session(body):
        return SimpleNamespace(
            http_response=SimpleNamespace(status_code=200),
            context={ContentDecodePolicy.CONTEXT_NAME: body},
        )

    @staticmethod
    def _operations(command):
        return [
            operation(command.ctx)
            for operation in vars(type(command)).values()
            if isinstance(operation, type) and issubclass(operation, AAZHttpOperation)
        ]

    def test_complete_registered_command_surface(self):
        expected = {
            f'relationship {group} {verb}'
            for group in WRITABLE_GROUPS
            for verb in ('create', 'show', 'update', 'list', 'delete', 'wait')
        }
        expected.add('relationship contains list')
        self.assertEqual(set(self.commands), expected)
        for name in (
            'relationship dependency-of update',
            'relationship service-group-member update',
            'relationship dependency-of-by-service-group create',
            'relationship dependency-of-by-service-group update',
        ):
            with self.subTest(command=name):
                examples = self.commands[name].AZ_HELP['examples']
                self.assertTrue(examples)
                self.assertTrue(examples[0]['text'].startswith('az ' + name + ' '))

    def test_all_stable_relationship_routes_are_represented(self):
        expected = set()
        for scope in (RESOURCE_URI, SERVICE_GROUP):
            path = f'{scope}/providers/Microsoft.Relationships/dependencyOf'
            expected.add(('GET', path))
            expected.update((method, f'{path}/test.relationship-1') for method in ('GET', 'PUT', 'DELETE'))
        path = f'{RESOURCE_URI}/providers/Microsoft.Relationships/serviceGroupMember'
        expected.add(('GET', path))
        expected.update((method, f'{path}/test.relationship-1') for method in ('GET', 'PUT', 'DELETE'))
        expected.update({
            ('GET', f'/subscriptions/{SUBSCRIPTION}/providers/Microsoft.Relationships/contains'),
            ('GET', f'{RESOURCE_URI}/providers/Microsoft.Relationships/contains'),
        })
        actual = set()
        for name in self.commands:
            _, group, verb = name.split()
            command, _ = self._command(group, verb, resource_group='relationship-test')
            for operation in self._operations(command):
                actual.add((operation.method, urlsplit(operation.url).path))
                self.assertEqual(operation.query_parameters['api-version'], VERSION)
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 14)

    def test_create_serializes_only_writable_relationship_properties(self):
        for group in WRITABLE_GROUPS:
            with self.subTest(group=group):
                command, _ = self._command(group, 'create')
                operation, = self._operations(command)
                expected = {'sourceId': SERVICE_GROUP} if group == 'service-group-member' else {'targetId': TARGET}
                self.assertEqual(operation.content, {'properties': expected})
                self.assertTrue(command.AZ_SUPPORT_NO_WAIT)

    def test_service_group_member_uses_source_not_target_arguments(self):
        for verb in ('create', 'update'):
            with self.subTest(verb=verb):
                command, _ = self._command('service-group-member', verb)
                schema = command.get_arguments_schema()
                self.assertTrue(hasattr(schema, 'source_id'))
                self.assertTrue(hasattr(schema, 'source_tenant'))
                self.assertFalse(hasattr(schema, 'target_id'))
                self.assertFalse(hasattr(schema, 'target_tenant'))

    def test_create_requires_the_writable_endpoint_id(self):
        for group in WRITABLE_GROUPS:
            with self.subTest(group=group):
                command, _ = self._command(group, 'create')
                name = 'source_id' if group == 'service-group-member' else 'target_id'
                argument = getattr(command.get_arguments_schema(), name)
                self.assertTrue(argument.to_cmd_arg(name, cli_ctx=self.cli_ctx).type.settings['required'])

    def test_generic_resource_uri_preserves_subscription_and_service_group_scopes(self):
        for scope in (f'/subscriptions/{SUBSCRIPTION}', RESOURCE_URI, SERVICE_GROUP):
            for verb in ('create', 'show', 'update', 'list', 'delete', 'wait'):
                with self.subTest(scope=scope, verb=verb):
                    command, _ = self._command('dependency-of', verb, resource_uri=scope)
                    for operation in self._operations(command):
                        self.assertTrue(
                            urlsplit(operation.url).path.startswith(
                                f'{scope}/providers/Microsoft.Relationships/dependencyOf'
                            )
                        )

    def test_service_group_routes_do_not_add_subscription_scope(self):
        for verb in ('create', 'show', 'update', 'list', 'delete', 'wait'):
            with self.subTest(verb=verb):
                command, _ = self._command('dependency-of-by-service-group', verb)
                for operation in self._operations(command):
                    self.assertTrue(urlsplit(operation.url).path.startswith(SERVICE_GROUP + '/providers/'))
                    self.assertNotIn('/subscriptions/', operation.url)

    def test_service_group_name_is_encoded_as_one_path_segment(self):
        command, _ = self._command(
            'dependency-of-by-service-group', 'list', service_group_name='name/with space'
        )
        operation, = self._operations(command)
        self.assertIn('/serviceGroups/name%2Fwith%20space/providers/', operation.url)

    def test_contains_selects_scope_and_serializes_filter(self):
        expression = "properties.metadata.targetType eq 'Microsoft.Compute/virtualMachines'"
        for resource_group in (None, 'relationship-test'):
            with self.subTest(resource_group=resource_group):
                arguments = {'filter': expression}
                if resource_group:
                    arguments['resource_group'] = resource_group
                command, client = self._command('contains', 'list', **arguments)
                client.send_request.return_value = self._session({'value': []})
                command._execute_operations()
                client.send_request.assert_called_once()
                request = client.send_request.call_args.kwargs['request']
                scope = RESOURCE_URI if resource_group else f'/subscriptions/{SUBSCRIPTION}'
                self.assertEqual(urlsplit(request.url).path, f'{scope}/providers/Microsoft.Relationships/contains')
                self.assertEqual(parse_qs(urlsplit(request.url).query), {
                    'api-version': [VERSION], '$filter': [expression],
                })
                self.assertEqual(command._output()[0], [])

    def test_lists_follow_next_link_and_preserve_response_properties(self):
        for group in (*WRITABLE_GROUPS, 'contains'):
            with self.subTest(group=group):
                command, client = self._command(group, 'list')
                next_link = ARM + '/next-page?api-version=' + VERSION + '&$skipToken=a%2Bb%3D'
                relationship = {
                    'name': 'first',
                    'properties': {
                        'sourceId': SERVICE_GROUP, 'targetId': TARGET,
                        'metadata': {'sourceType': 'sourceType', 'targetType': 'targetType'},
                        'originInformation': {'relationshipOriginType': 'SystemDiscoveredByRule'},
                        'provisioningState': 'Succeeded',
                    },
                }
                client.send_request.side_effect = [
                    self._session({'value': [relationship], 'nextLink': next_link}),
                    self._session({'value': [{'name': 'second'}]}),
                ]
                result = list(command.build_paging(command._execute_operations, command._output))
                self.assertEqual([item['name'] for item in result], ['first', 'second'])
                self.assertEqual(result[0]['properties'], relationship['properties'])
                requests = [call.kwargs['request'] for call in client.send_request.call_args_list]
                self.assertEqual(len(requests), 2)
                self.assertEqual(parse_qs(urlsplit(requests[1].url).query)['$skipToken'], ['a+b='])

    def test_lists_support_max_items_and_continuation_tokens(self):
        for group in (*WRITABLE_GROUPS, 'contains'):
            with self.subTest(group=group):
                command, client = self._command(group, 'list', pagination_limit=1)
                client.send_request.return_value = self._session({'value': [{'name': 'one'}, {'name': 'two'}]})
                page = list(command.build_paging(command._execute_operations, command._output))
                self.assertEqual([item['name'] for item in page], ['one'])
                token = base64.b64encode(
                    json.dumps({'next_link': None, 'offset': 1}).encode('utf-8')
                ).decode('utf-8')
                resumed, resumed_client = self._command(
                    group, 'list', pagination_token=token, pagination_limit=1
                )
                resumed_client.send_request.return_value = self._session({'value': [{'name': 'one'}, {'name': 'two'}]})
                results = list(resumed.build_paging(resumed._execute_operations, resumed._output))
                self.assertEqual([item['name'] for item in results], ['two'])

    def test_updates_get_then_put_and_preserve_unmodified_writable_properties(self):
        for group in WRITABLE_GROUPS:
            with self.subTest(group=group):
                property_name = 'sourceId' if group == 'service-group-member' else 'targetId'
                tenant_arg = 'source_tenant' if group == 'service-group-member' else 'target_tenant'
                tenant_property = 'sourceTenant' if group == 'service-group-member' else 'targetTenant'
                resource_id = SERVICE_GROUP if group == 'service-group-member' else TARGET
                command, client = self._command(group, 'update', no_wait=True, **{tenant_arg: TENANT})
                instance = {
                    'id': RESOURCE_URI + '/providers/Microsoft.Relationships/example/test',
                    'name': 'test.relationship-1',
                    'type': 'Microsoft.Relationships/example',
                    'systemData': {'createdBy': 'server'},
                    'properties': {
                        'sourceId': SERVICE_GROUP,
                        'targetId': TARGET,
                        'metadata': {'sourceType': 'server', 'targetType': 'server'},
                        'provisioningState': 'Succeeded',
                    },
                }
                client.send_request.return_value = self._session(copy.deepcopy(instance))
                client.build_lro_polling = Mock()
                list(command._execute_operations())
                requests = [call.kwargs['request'] for call in client.send_request.call_args_list]
                self.assertEqual([request.method for request in requests], ['GET', 'PUT'])
                self.assertEqual(requests[0].url, requests[1].url)
                self.assertEqual(json.loads(requests[1].body), {
                    'properties': {property_name: resource_id, tenant_property: TENANT},
                })
                self.assertTrue(client.build_lro_polling.call_args.args[0].to_serialized_data())

    def test_update_does_not_put_when_the_relationship_is_not_found(self):
        for group in WRITABLE_GROUPS:
            with self.subTest(group=group):
                command, client = self._command(group, 'update')
                client.send_request.side_effect = ResourceNotFoundError('Relationship not found')
                with self.assertRaises(ResourceNotFoundError):
                    list(command._execute_operations())
                client.send_request.assert_called_once()
                self.assertEqual(client.send_request.call_args.kwargs['request'].method, 'GET')

    def test_list_errors_are_not_replaced_with_empty_results(self):
        for group in (*WRITABLE_GROUPS, 'contains'):
            with self.subTest(group=group):
                command, client = self._command(group, 'list')
                client.send_request.side_effect = HttpResponseError('Authorization failed')
                with self.assertRaisesRegex(HttpResponseError, 'Authorization failed'):
                    list(command.build_paging(command._execute_operations, command._output))


class ServiceGroupDependencyPropagationRetryTest(unittest.TestCase):

    @staticmethod
    def _error(status=403, code='AuthorizationFailed'):
        error = HttpResponseError(message='Permission not propagated.')
        error.status_code = status
        error.error = SimpleNamespace(code=code) if code else None
        error.response = SimpleNamespace(headers={'x-ms-correlation-request-id': 'first-attempt-correlation'})
        return error

    @patch('azext_relationship.tests.latest.test_relationship_scenario.time.sleep')
    def test_success_does_not_wait_or_retry(self, sleep):
        scenario = Mock()
        scenario.is_live = True
        result = test_relationship_scenario.RelationshipScenarioTest._create_service_group_dependency(
            scenario, 'create-command'
        )
        self.assertIs(result, scenario.cmd.return_value)
        scenario.cmd.assert_called_once_with('create-command')
        sleep.assert_not_called()

    @patch('azext_relationship.tests.latest.test_relationship_scenario.time.sleep')
    def test_live_authorization_failure_waits_and_retries_identical_command(self, sleep):
        scenario = Mock()
        scenario.is_live = True
        expected = Mock()
        scenario.cmd.side_effect = [self._error(), expected]
        with self.assertLogs(
            'azext_relationship.tests.latest.test_relationship_scenario', level='WARNING'
        ) as captured:
            result = test_relationship_scenario.RelationshipScenarioTest._create_service_group_dependency(
                scenario, 'create-command'
            )
        self.assertIs(result, expected)
        self.assertEqual(scenario.cmd.call_args_list, [call('create-command'), call('create-command')])
        sleep.assert_called_once_with(300)
        self.assertIn('first-attempt-correlation', captured.output[0])
        self.assertIn('Permission not propagated.', captured.output[0])

    @patch('azext_relationship.tests.latest.test_relationship_scenario.time.sleep')
    def test_second_failure_is_propagated_without_another_retry(self, sleep):
        scenario = Mock()
        scenario.is_live = True
        second_error = self._error()
        scenario.cmd.side_effect = [self._error(), second_error]
        with self.assertLogs('azext_relationship.tests.latest.test_relationship_scenario', level='WARNING'):
            with self.assertRaises(HttpResponseError) as captured:
                test_relationship_scenario.RelationshipScenarioTest._create_service_group_dependency(
                    scenario, 'create-command'
                )
        self.assertIs(captured.exception, second_error)
        self.assertEqual(scenario.cmd.call_count, 2)
        sleep.assert_called_once_with(300)

    @patch('azext_relationship.tests.latest.test_relationship_scenario.time.sleep')
    def test_other_http_errors_are_not_retried(self, sleep):
        for status, code in (
            (401, 'AuthorizationFailed'),
            (400, 'InvalidRequest'),
            (403, 'LinkedAuthorizationFailed'),
            (403, None),
            (500, 'InternalServerError'),
        ):
            with self.subTest(status=status, code=code):
                scenario = Mock()
                scenario.is_live = True
                error = self._error(status, code)
                scenario.cmd.side_effect = error
                with self.assertRaises(HttpResponseError) as captured:
                    test_relationship_scenario.RelationshipScenarioTest._create_service_group_dependency(
                        scenario, 'create-command'
                    )
                self.assertIs(captured.exception, error)
                scenario.cmd.assert_called_once_with('create-command')
        sleep.assert_not_called()

    @patch('azext_relationship.tests.latest.test_relationship_scenario.time.sleep')
    def test_recorded_authorization_failure_replays_retry_without_waiting(self, sleep):
        scenario = Mock()
        scenario.is_live = False
        expected = Mock()
        scenario.cmd.side_effect = [self._error(), expected]
        with self.assertLogs('azext_relationship.tests.latest.test_relationship_scenario', level='WARNING'):
            result = test_relationship_scenario.RelationshipScenarioTest._create_service_group_dependency(
                scenario, 'create-command'
            )
        self.assertIs(result, expected)
        self.assertEqual(scenario.cmd.call_args_list, [call('create-command'), call('create-command')])
        sleep.assert_not_called()

    @patch('azext_relationship.tests.latest.test_relationship_scenario.time.sleep')
    def test_non_http_failure_is_not_retried(self, sleep):
        scenario = Mock()
        scenario.is_live = True
        scenario.cmd.side_effect = ValueError('Invalid command arguments.')
        with self.assertRaises(ValueError):
            test_relationship_scenario.RelationshipScenarioTest._create_service_group_dependency(
                scenario, 'create-command'
            )
        scenario.cmd.assert_called_once_with('create-command')
        sleep.assert_not_called()


class RelationshipRecordingTest(unittest.TestCase):

    @staticmethod
    def _scenario(method, live):
        scenario = object.__new__(test_relationship_scenario.RelationshipScenarioTest)
        scenario._testMethodName = method
        scenario.is_live = live
        scenario.in_recording = live
        scenario.name_replacer = Mock()
        scenario.recording_processors = []
        scenario.replay_processors = []
        return scenario

    def test_signed_polling_query_values_are_sanitized(self):
        processor = test_relationship_scenario.RelationshipRecordingProcessor()
        for route in ('operationStatuses', 'operationResults', 'operationresults'):
            with self.subTest(route=route):
                original = (
                    ARM + f'/providers/Microsoft.Relationships/locations/eastus/{route}/op'
                    '?api-version=2026-08-01&t=private-t&c=private-c&s=private-s&h=private-h'
                )
                request = SimpleNamespace(uri=original)
                processor.process_request(request)
                query = parse_qs(urlsplit(request.uri).query)
                self.assertEqual(query, {
                    'api-version': [VERSION],
                    't': ['sanitized'], 'c': ['sanitized'], 's': ['sanitized'], 'h': ['sanitized'],
                })
                self.assertEqual(urlsplit(request.uri).path, urlsplit(original).path)
                response = {'headers': {'Location': [original], 'Azure-AsyncOperation': [original]}}
                processor.process_response(response)
                self.assertEqual(response['headers']['Location'], [request.uri])
                self.assertEqual(response['headers']['Azure-AsyncOperation'], [request.uri])
                processor.process_request(request)
                self.assertEqual(response['headers']['Location'], [request.uri])

    def test_normal_request_urls_are_not_modified(self):
        url = ARM + '/subscriptions/example/providers/Microsoft.Relationships/contains?api-version=' + VERSION
        request = SimpleNamespace(uri=url)
        test_relationship_scenario.RelationshipRecordingProcessor().process_request(request)
        self.assertEqual(request.uri, url)

    def test_identity_and_credential_headers_are_filtered(self):
        for header in (
            'authorization', 'cookie', 'set-cookie', 'x-ms-arm-signed-obo-token',
            'x-ms-authorization-auxiliary', 'x-ms-operation-identifier',
        ):
            with self.subTest(header=header):
                self.assertIn(header, test_relationship_scenario.RelationshipScenarioTest.FILTER_HEADERS)

    @patch.object(test_relationship_scenario.ScenarioTest, 'setUp')
    def test_dependency_lifecycle_uses_only_its_dedicated_fixture(self, _):
        prefix = '/providers/Microsoft.Management/serviceGroups/'
        for shared_name in ('testsg', 'sg'):
            shared = prefix + shared_name
            dedicated = shared + '-dependency'
            with patch.dict(os.environ, {
                'AZURE_RELATIONSHIP_TEST_TARGET_SG': shared,
                'AZURE_RELATIONSHIP_TEST_DEPENDENCY_SG': dedicated,
            }, clear=True):
                for method, fixture, recorded_name in (
                    ('test_dependency_of_by_service_group_crud', dedicated, 'clitestdependencysg'),
                    ('test_dependency_of_crud', shared, 'clitestsharedsg'),
                ):
                    with self.subTest(shared=shared_name, method=method):
                        scenario = self._scenario(method, live=True)
                        scenario.name_replacer = GeneralNameReplacer()
                        scenario.setUp()
                        self.assertEqual(scenario.service_group_id, fixture)
                        suffix = '/providers/Microsoft.Relationships/dependencyOf/example'
                        request = SimpleNamespace(uri=ARM + fixture + suffix, body=None, headers={})
                        scenario.name_replacer.process_request(request)
                        self.assertEqual(request.uri, ARM + prefix + recorded_name + suffix)

    @patch.object(test_relationship_scenario.ScenarioTest, 'setUp')
    def test_shared_fixture_cannot_be_reused_for_dependency_lifecycle(self, _):
        shared = '/providers/Microsoft.Management/serviceGroups/shared'
        with patch.dict(os.environ, {
            'AZURE_RELATIONSHIP_TEST_TARGET_SG': shared,
            'AZURE_RELATIONSHIP_TEST_DEPENDENCY_SG': shared,
        }, clear=True):
            with self.assertRaisesRegex(AssertionError, 'separate Service Group'):
                self._scenario('test_dependency_of_by_service_group_crud', live=True).setUp()

    @patch.object(test_relationship_scenario.ScenarioTest, 'setUp')
    def test_playback_uses_mocked_fixtures_without_environment(self, _):
        with patch.dict(os.environ, {}, clear=True):
            for method, name in (
                ('test_dependency_of_by_service_group_crud', 'clitestdependencysg'),
                ('test_dependency_of_crud', 'clitestsharedsg'),
            ):
                with self.subTest(method=method):
                    scenario = self._scenario(method, live=False)
                    scenario.setUp()
                    self.assertEqual(
                        scenario.service_group_id, '/providers/Microsoft.Management/serviceGroups/' + name
                    )

    @patch.object(test_relationship_scenario.ScenarioTest, 'setUp')
    def test_missing_recording_does_not_start_an_implicit_live_run(self, _):
        scenario = self._scenario('test_dependency_of_crud', live=False)
        scenario.in_recording = True
        with self.assertRaisesRegex(AssertionError, 'Missing recording'):
            scenario.setUp()


if __name__ == '__main__':
    unittest.main()
