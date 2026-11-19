# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from azure.cli.core.azclierror import ResourceNotFoundError, ValidationError
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.mgmt.appcontainers.models import EnvironmentVar

from azext_durabletask import _scheduler
from azext_durabletask._format import (
    scheduler_list_table_format, scheduler_table_format, taskhub_list_table_format, taskhub_table_format,
)
from azext_durabletask._retention_policy import _build_retention_policies


SUBSCRIPTION = '00000000-0000-0000-0000-000000000000'
RESOURCE_PREFIX = f'/subscriptions/{SUBSCRIPTION}/resourceGroups/test-rg/providers'
SCHEDULER_ID = RESOURCE_PREFIX + '/Microsoft.DurableTask/schedulers/test-scheduler'
IDENTITY_ID = RESOURCE_PREFIX + '/Microsoft.ManagedIdentity/userAssignedIdentities/test-identity'
ENDPOINT = 'https://test-scheduler.durabletask.io'


class DurabletaskAttachTests(unittest.TestCase):
    def setUp(self):
        self.cli_ctx = SimpleNamespace(data={'subscription_id': SUBSCRIPTION})
        self.cmd = SimpleNamespace(cli_ctx=self.cli_ctx)
        self.scheduler = {
            'id': SCHEDULER_ID,
            'properties': {'provisioningState': 'Succeeded', 'endpoint': ENDPOINT},
        }
        patches = {
            'scheduler_show': patch.object(
                _scheduler, '_SchedulerShow', return_value=Mock(return_value=self.scheduler)),
            'hub_show': patch.object(_scheduler, '_TaskHubShow', return_value=Mock(return_value={})),
            'function_identity': patch.object(
                _scheduler, '_get_functionapp_identity', return_value='test-principal'),
            'container_identity': patch.object(
                _scheduler, '_get_containerapp_identity', return_value='test-principal'),
            'resolve_identity': patch.object(
                _scheduler, '_resolve_user_assigned_identity', return_value=('test-principal', 'test-client')),
            'ensure_function_identity': patch.object(_scheduler, '_ensure_identity_on_functionapp'),
            'ensure_container_identity': patch.object(_scheduler, '_ensure_identity_on_containerapp'),
            'function_settings': patch.object(_scheduler, '_update_functionapp_settings'),
            'container_settings': patch.object(_scheduler, '_update_containerapp_env_vars'),
            'permissions': patch.object(_scheduler, '_check_target_permissions'),
            'access': patch.object(_scheduler, '_check_access'),
            'role': patch('azure.cli.core.commands.arm.resolve_role_id', return_value='test-role-id'),
            'client_factory': patch('azure.cli.core.commands.client_factory.get_mgmt_service_client'),
        }
        for name, patcher in patches.items():
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)
        self.assignments = self.client_factory.return_value.role_assignments

    def _attach(self, resource_type='Microsoft.Web/sites', role='worker', identity=None):
        target = RESOURCE_PREFIX + f'/{resource_type}/test-app'
        return _scheduler.attach_scheduler(
            self.cmd, 'test-rg', 'test-scheduler', 'test-hub', target, role, identity)

    def test_durabletask_attach_system_assigned_functionapp(self):
        result = self._attach()
        self.assertEqual(result, {
            'schedulerName': 'test-scheduler', 'resourceGroupName': 'test-rg',
            'taskHubName': 'test-hub', 'targetResourceId': RESOURCE_PREFIX + '/Microsoft.Web/sites/test-app',
            'targetType': 'functionapp', 'connectionString': f'Endpoint={ENDPOINT};Authentication=ManagedIdentity',
            'identityPrincipalId': 'test-principal', 'roleAssigned': 'Durable Task Worker',
        })
        self.function_identity.assert_called_once_with(self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION)
        self.container_identity.assert_not_called()
        self.function_settings.assert_called_once_with(
            self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, ENDPOINT, 'test-hub', None)
        self.container_settings.assert_not_called()
        self.resolve_identity.assert_not_called()
        call = self.assignments.create.call_args.kwargs
        self.assertEqual(call['scope'], SCHEDULER_ID)
        self.assertEqual(call['parameters'].principal_id, 'test-principal')
        self.assertEqual(call['parameters'].role_definition_id, 'test-role-id')
        self.assertEqual(call['parameters'].principal_type, 'ServicePrincipal')

    def test_durabletask_attach_system_assigned_containerapp(self):
        result = self._attach('Microsoft.App/containerApps', role='reader')
        self.assertEqual(result['targetType'], 'containerapp')
        self.assertEqual(result['roleAssigned'], 'Durable Task Data Reader')
        self.container_identity.assert_called_once_with(self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION)
        self.container_settings.assert_called_once_with(
            self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, ENDPOINT, 'test-hub', None)
        self.function_settings.assert_not_called()

    def test_durabletask_attach_user_assigned_identity(self):
        for resource_type, target_type in (
            ('Microsoft.Web/sites', 'functionapp'), ('Microsoft.App/containerApps', 'containerapp'),
        ):
            with self.subTest(target_type=target_type):
                result = self._attach(resource_type, role='contributor', identity=IDENTITY_ID)
                self.assertEqual(result['identityResourceId'], IDENTITY_ID)
                self.assertEqual(result['identityClientId'], 'test-client')
                self.assertEqual(result['roleAssigned'], 'Durable Task Data Contributor')
                self.assertEqual(result['connectionString'],
                                 f'Endpoint={ENDPOINT};Authentication=ManagedIdentity;ClientID=test-client')
        self.ensure_function_identity.assert_called_once_with(
            self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, IDENTITY_ID)
        self.ensure_container_identity.assert_called_once_with(
            self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, IDENTITY_ID)
        self.function_identity.assert_not_called()
        self.container_identity.assert_not_called()

    def test_durabletask_attach_rejects_unready_scheduler(self):
        self.scheduler['properties']['provisioningState'] = 'Creating'
        with self.assertRaisesRegex(ValidationError, 'not ready'):
            self._attach()
        self.hub_show.return_value.assert_not_called()
        self.assignments.create.assert_not_called()
        self.function_settings.assert_not_called()

    def test_durabletask_attach_rejects_missing_endpoint(self):
        del self.scheduler['properties']['endpoint']
        with self.assertRaisesRegex(ValidationError, 'does not have an endpoint'):
            self._attach()
        self.assignments.create.assert_not_called()

    def test_durabletask_attach_missing_hub(self):
        error = HttpResponseError(message='Not found')
        error.status_code = 404
        self.hub_show.return_value.side_effect = error
        with self.assertRaisesRegex(ResourceNotFoundError, "Task hub 'test-hub' not found"):
            self._attach()
        self.assignments.create.assert_not_called()
        self.function_identity.assert_not_called()

    def test_durabletask_attach_hub_errors_propagate(self):
        error = HttpResponseError(message='Access denied')
        error.status_code = 403
        self.hub_show.return_value.side_effect = error
        with self.assertRaises(HttpResponseError) as raised:
            self._attach()
        self.assertIs(raised.exception, error)
        self.assignments.create.assert_not_called()

    def test_durabletask_attach_existing_role_is_idempotent(self):
        for error in (
            ResourceExistsError(message='Already exists'),
            HttpResponseError(message='Role assignment already exists'),
        ):
            with self.subTest(error=type(error).__name__):
                self.assignments.create.side_effect = error
                result = self._attach()
                self.assertEqual(result['roleAssigned'], 'Durable Task Worker')
        self.assertEqual(self.function_settings.call_count, 2)

    def test_durabletask_attach_role_errors_stop_settings_update(self):
        error = HttpResponseError(message='Access denied')
        self.assignments.create.side_effect = error
        with self.assertRaises(HttpResponseError) as raised:
            self._attach()
        self.assertIs(raised.exception, error)
        self.function_settings.assert_not_called()


class DurabletaskSettingsTests(unittest.TestCase):
    def setUp(self):
        patcher = patch('azure.cli.core.commands.client_factory.get_mgmt_service_client')
        self.factory = patcher.start()
        self.addCleanup(patcher.stop)
        self.client = self.factory.return_value
        self.cli_ctx = Mock()

    def test_durabletask_functionapp_settings_preserve_existing_values(self):
        for client_id in (None, 'test-client'):
            with self.subTest(client_id=client_id):
                self.client.web_apps.list_application_settings.return_value = SimpleNamespace(
                    properties={'KEEP_ME': 'existing', 'TASKHUB_NAME': 'old-hub'})
                _scheduler._update_functionapp_settings(
                    self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, ENDPOINT, 'test-hub', client_id)
                settings = self.client.web_apps.update_application_settings.call_args.args[2].properties
                connection = f'Endpoint={ENDPOINT};Authentication=ManagedIdentity'
                if client_id:
                    connection += ';ClientID=test-client'
                self.assertEqual(settings, {
                    'KEEP_ME': 'existing', 'TASKHUB_NAME': 'test-hub',
                    'DURABLE_TASK_SCHEDULER_CONNECTION_STRING': connection,
                })
                self.assertEqual(self.factory.call_args.kwargs['subscription_id'], SUBSCRIPTION)

    def test_durabletask_containerapp_settings_preserve_all_containers(self):
        first = SimpleNamespace(env=[
            EnvironmentVar(name='KEEP_ME', secret_ref='existing-secret'),
            EnvironmentVar(name='TASKHUB_NAME', value='old-hub'),
        ])
        second = SimpleNamespace(env=None)
        template = SimpleNamespace(containers=[first, second])
        self.client.container_apps.get.return_value = SimpleNamespace(template=template)
        _scheduler._update_containerapp_env_vars(
            self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, ENDPOINT, 'test-hub', 'test-client')
        payload = self.client.container_apps.begin_update.call_args.args[2]
        self.assertEqual(payload, {'template': template})
        self.assertEqual(first.env[0].secret_ref, 'existing-secret')
        for container in template.containers:
            values = {env.name: env.value for env in container.env}
            self.assertEqual(values['TASKHUB_NAME'], 'test-hub')
            self.assertEqual(values['DURABLE_TASK_SCHEDULER_CONNECTION_STRING'],
                             f'Endpoint={ENDPOINT};Authentication=ManagedIdentity;ClientID=test-client')
            self.assertEqual(sum(env.name == 'TASKHUB_NAME' for env in container.env), 1)
        self.client.container_apps.begin_update.return_value.result.assert_called_once()

    def test_durabletask_containerapp_requires_containers(self):
        for template in (None, SimpleNamespace(containers=[])):
            with self.subTest(template=template):
                self.client.container_apps.get.return_value = SimpleNamespace(template=template)
                with self.assertRaisesRegex(ValidationError, 'no containers'):
                    _scheduler._update_containerapp_env_vars(
                        self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, ENDPOINT, 'test-hub')
        self.client.container_apps.begin_update.assert_not_called()

    def test_durabletask_identity_attachment_preserves_existing_identities(self):
        existing_id = IDENTITY_ID.replace('test-identity', 'existing-identity')
        for ensure_identity, operations in (
            (_scheduler._ensure_identity_on_functionapp, self.client.web_apps),
            (_scheduler._ensure_identity_on_containerapp, self.client.container_apps),
        ):
            with self.subTest(ensure_identity=ensure_identity.__name__):
                operations.get.return_value = SimpleNamespace(identity=SimpleNamespace(
                    type='SystemAssigned,UserAssigned', user_assigned_identities={existing_id: {}}))
                ensure_identity(self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, IDENTITY_ID)
                update = operations.update if operations is self.client.web_apps else operations.begin_update
                identity = update.call_args.args[2]['identity']
                self.assertEqual(identity.type, 'SystemAssigned,UserAssigned')
                self.assertEqual(identity.user_assigned_identities, {existing_id: {}, IDENTITY_ID: {}})

    def test_durabletask_identity_attachment_is_case_insensitive(self):
        for ensure_identity, operations in (
            (_scheduler._ensure_identity_on_functionapp, self.client.web_apps),
            (_scheduler._ensure_identity_on_containerapp, self.client.container_apps),
        ):
            with self.subTest(ensure_identity=ensure_identity.__name__):
                operations.get.return_value = SimpleNamespace(identity=SimpleNamespace(
                    type='UserAssigned', user_assigned_identities={IDENTITY_ID.upper(): {}}))
                ensure_identity(self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION, IDENTITY_ID)
                operations.update.assert_not_called()
                operations.begin_update.assert_not_called()

    def test_durabletask_target_requires_managed_identity(self):
        for get_identity, operations in (
            (_scheduler._get_functionapp_identity, self.client.web_apps),
            (_scheduler._get_containerapp_identity, self.client.container_apps),
        ):
            with self.subTest(get_identity=get_identity.__name__):
                operations.get.return_value = SimpleNamespace(name='test-app', identity=None)
                with self.assertRaisesRegex(ValidationError, 'does not have a managed identity'):
                    get_identity(self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION)

    def test_durabletask_target_not_found(self):
        for get_identity, operations in (
            (_scheduler._get_functionapp_identity, self.client.web_apps),
            (_scheduler._get_containerapp_identity, self.client.container_apps),
        ):
            with self.subTest(get_identity=get_identity.__name__):
                error = HttpResponseError(message='Not found')
                error.status_code = 404
                operations.get.side_effect = error
                with self.assertRaises(ResourceNotFoundError):
                    get_identity(self.cli_ctx, 'test-app', 'test-rg', SUBSCRIPTION)

    def test_durabletask_resolve_user_assigned_identity(self):
        self.client.user_assigned_identities.get.return_value = SimpleNamespace(
            principal_id='test-principal', client_id='test-client')
        self.assertEqual(
            _scheduler._resolve_user_assigned_identity(self.cli_ctx, IDENTITY_ID),
            ('test-principal', 'test-client'))
        self.client.user_assigned_identities.get.assert_called_once_with('test-rg', 'test-identity')


class DurabletaskValidationTests(unittest.TestCase):
    def test_durabletask_parse_supported_targets(self):
        for provider, expected in (
            ('Microsoft.Web/sites', 'functionapp'), ('microsoft.app/containerapps', 'containerapp'),
        ):
            with self.subTest(provider=provider):
                self.assertEqual(
                    _scheduler._parse_target(RESOURCE_PREFIX + f'/{provider}/test-app'),
                    (expected, 'test-app', 'test-rg', SUBSCRIPTION))

    def test_durabletask_parse_invalid_targets(self):
        for target in (
            'test-app', '/providers/Microsoft.Web/sites/test-app',
            RESOURCE_PREFIX + '/Microsoft.Storage/storageAccounts/test-storage',
        ):
            with self.subTest(target=target):
                with self.assertRaisesRegex(ValidationError, 'Invalid target resource ID'):
                    _scheduler._parse_target(target)

    def test_durabletask_retention_zero_and_state_mapping(self):
        args = {
            key: Mock(to_serialized_data=Mock(return_value=str(days)))
            for days, key in enumerate((
                'default_days', 'canceled_days', 'completed_days', 'failed_days', 'terminated_days'))
        }
        self.assertEqual(_build_retention_policies(args), [
            {'retentionPeriodInDays': 0},
            {'retentionPeriodInDays': 1, 'orchestrationState': 'Canceled'},
            {'retentionPeriodInDays': 2, 'orchestrationState': 'Completed'},
            {'retentionPeriodInDays': 3, 'orchestrationState': 'Failed'},
            {'retentionPeriodInDays': 4, 'orchestrationState': 'Terminated'},
        ])

    def test_durabletask_scheduler_table_output(self):
        scheduler = {
            'id': SCHEDULER_ID, 'name': 'test-scheduler', 'location': 'eastus',
            'properties': {'provisioningState': 'Succeeded', 'sku': {'name': 'Dedicated', 'capacity': 2}},
        }
        expected = {
            'Name': 'test-scheduler', 'ResourceGroup': 'test-rg', 'Location': 'eastus',
            'State': 'Succeeded', 'SKU': 'Dedicated', 'Capacity Units': 2,
        }
        self.assertEqual(scheduler_table_format(scheduler), expected)
        self.assertEqual(scheduler_list_table_format([scheduler]), [expected])
        self.assertEqual(list(scheduler_table_format(scheduler)), list(expected))
        self.assertEqual(scheduler_list_table_format([]), [])

    def test_durabletask_taskhub_table_output(self):
        hub = {
            'id': SCHEDULER_ID + '/taskHubs/test-hub', 'name': 'test-hub',
            'properties': {'provisioningState': 'Succeeded'},
        }
        expected = {'Name': 'test-hub', 'ResourceGroup': 'test-rg', 'State': 'Succeeded'}
        self.assertEqual(taskhub_table_format(hub), expected)
        self.assertEqual(taskhub_list_table_format([hub]), [expected])
        self.assertEqual(taskhub_list_table_format([]), [])
        self.assertEqual(taskhub_table_format({}), {'Name': '', 'ResourceGroup': '', 'State': ''})


class DurabletaskAccessTests(unittest.TestCase):
    def setUp(self):
        self.cli_ctx = SimpleNamespace(
            cloud=SimpleNamespace(endpoints=SimpleNamespace(resource_manager='https://management.example.test/')))
        for name, patcher in (
            ('caller', patch.object(_scheduler, '_get_caller_object_id', return_value='test-caller')),
            ('request', patch('azure.cli.core.util.send_raw_request')),
        ):
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)

    def test_durabletask_check_access_request(self):
        self.request.return_value.json.return_value = {'value': []}
        _scheduler._check_access(self.cli_ctx, SCHEDULER_ID, ['test/action'], 'test resource')
        args, kwargs = self.request.call_args
        self.assertEqual(args, (
            self.cli_ctx, 'POST', 'https://management.example.test' + SCHEDULER_ID +
            '/providers/Microsoft.Authorization/checkAccess?api-version=2022-04-01',
        ))
        self.assertEqual(json.loads(kwargs['body']), {
            'Subject': {'ObjectId': 'test-caller'}, 'Actions': [{'Id': 'test/action'}],
        })

    def test_durabletask_check_access_accepts_both_response_shapes(self):
        allowed = [{'actionId': 'test/action', 'accessDecision': 'Allowed'}]
        for response in (allowed, {'value': allowed}):
            with self.subTest(response=response):
                self.request.return_value.json.return_value = response
                with patch.object(_scheduler.logger, 'warning') as warning:
                    _scheduler._check_access(self.cli_ctx, SCHEDULER_ID, ['test/action'], 'test resource')
                warning.assert_not_called()

    def test_durabletask_check_access_denial_warns(self):
        self.request.return_value.json.return_value = [
            {'actionId': 'test/action', 'accessDecision': 'Denied'},
        ]
        with self.assertLogs(_scheduler.logger, level='WARNING') as logs:
            _scheduler._check_access(self.cli_ctx, SCHEDULER_ID, ['test/action'], 'test resource')
        self.assertIn("action 'test/action' returned 'Denied'", logs.output[0])

    def test_durabletask_check_access_failure_warns(self):
        self.request.side_effect = HttpResponseError(message='Access check unavailable')
        with self.assertLogs(_scheduler.logger, level='WARNING') as logs:
            _scheduler._check_access(self.cli_ctx, SCHEDULER_ID, ['test/action'], 'test resource')
        self.assertIn('Failed to check access', logs.output[0])

    def test_durabletask_check_access_missing_caller_warns(self):
        self.caller.return_value = None
        with self.assertLogs(_scheduler.logger, level='WARNING') as logs:
            _scheduler._check_access(self.cli_ctx, SCHEDULER_ID, ['test/action'], 'test resource')
        self.assertIn('Could not determine caller object ID', logs.output[0])
        self.request.assert_not_called()
