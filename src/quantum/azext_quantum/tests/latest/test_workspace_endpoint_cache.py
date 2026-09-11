import json
import os
import unittest
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from azure.core.exceptions import ResourceNotFoundError
from knack.config import CLIConfig

from ..._client_factory import cf_jobs, cf_providers, cf_quotas
from ...operations.job import job_show
from ...operations.workspace import WorkspaceInfo, clear, set as set_workspace


class WorkspaceEndpointCacheTest(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.config = CLIConfig(config_dir=directory.name, config_env_var_prefix='QUANTUM_CACHE_TEST',
                                use_local_config=False)
        self.cloud = SimpleNamespace(endpoints=SimpleNamespace(resource_manager='https://management.azure.com/'))
        self.cmd = SimpleNamespace(cli_ctx=SimpleNamespace(config=self.config, cloud=self.cloud))
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.subscription = stack.enter_context(patch(
            'azure.cli.core.commands.client_factory.get_subscription_id', return_value='saved-subscription'))
        self.profile = stack.enter_context(patch('azure.cli.core._profile.Profile'))
        self.profile.return_value.get_subscription.return_value = {'tenantId': 'saved-tenant'}
        self.endpoint = 'https://saved-workspace.eastus.quantum.azure.com'
        self.other_endpoint = 'https://other-workspace.westus-v2.quantum.azure.com'
        self.arm = stack.enter_context(patch('azext_quantum._client_factory.cf_workspaces'))
        self.arm.return_value.get.return_value.properties.endpoint_uri = self.other_endpoint
        self.credentials = stack.enter_context(patch('azext_quantum._client_factory._get_data_credentials'))
        self.client = stack.enter_context(patch('azext_quantum._client_factory.WorkspaceClient'))

    def save_workspace(self):
        WorkspaceInfo(self.cmd, 'saved-group', 'saved-workspace').save(self.cmd, self.endpoint)

    def test_save_namespaced_cache_with_identity(self):
        self.config.set_value('defaults', 'endpoint', 'devcenter-endpoint')
        self.save_workspace()

        cache = json.loads(self.config.get('quantum', 'workspace_endpoint_cache', '{}'))
        self.assertEqual(cache, {
            'version': 1,
            'resource_id': '/subscriptions/saved-subscription/resourcegroups/saved-group/'
                           'providers/microsoft.quantum/workspaces/saved-workspace',
            'arm_endpoint': 'https://management.azure.com',
            'tenant_id': 'saved-tenant',
            'endpoint': self.endpoint,
        })
        self.assertEqual(self.config.get('defaults', 'endpoint'), 'devcenter-endpoint')
        self.assertEqual(self.config.get('defaults', 'group'), 'saved-group')
        self.assertEqual(self.config.get('defaults', 'workspace'), 'saved-workspace')
        self.profile.return_value.get_subscription.assert_called_with('saved-subscription')

    def test_matching_identity_uses_cache_without_arm(self):
        self.save_workspace()
        for group, workspace in [(None, None), ('saved-group', 'saved-workspace'),
                                 ('SAVED-GROUP', 'SAVED-WORKSPACE')]:
            for factory in (cf_jobs, cf_providers, cf_quotas):
                with self.subTest(group=group, workspace=workspace, factory=factory.__name__):
                    info = WorkspaceInfo(self.cmd, group, workspace)
                    factory(self.cmd.cli_ctx, info.subscription, info.resource_group, info.name, info.endpoint)
                    self.client.assert_called_with(self.endpoint, self.credentials.return_value)
        self.arm.assert_not_called()

    def test_other_workspace_uses_arm_without_changing_saved_state(self):
        self.save_workspace()
        before = self.config.items('defaults'), self.config.items('quantum')
        self.client.return_value.services.jobs.get.return_value.as_dict.return_value = {'id': 'job-id'}

        result = job_show(self.cmd, 'job-id', 'other-group', 'other-workspace')

        self.assertEqual(result, {'id': 'job-id'})
        self.arm.return_value.get.assert_called_once_with('other-group', 'other-workspace')
        self.client.assert_called_once_with(self.other_endpoint, self.credentials.return_value)
        self.client.return_value.services.jobs.get.assert_called_once_with(
            'saved-subscription', 'other-group', 'other-workspace', 'job-id')
        self.assertEqual((self.config.items('defaults'), self.config.items('quantum')), before)

    def test_partial_overrides_keep_independent_defaults_but_not_endpoint(self):
        self.save_workspace()
        for group, workspace, expected_group, expected_workspace in [
            (None, 'other-workspace', 'saved-group', 'other-workspace'),
            ('other-group', None, 'other-group', 'saved-workspace'),
        ]:
            with self.subTest(group=group, workspace=workspace):
                info = WorkspaceInfo(self.cmd, group, workspace)
                self.assertEqual((info.resource_group, info.name), (expected_group, expected_workspace))
                self.assertIsNone(info.endpoint)

    def test_other_subscription_does_not_reuse_cache(self):
        self.save_workspace()
        self.subscription.return_value = 'other-subscription'
        self.assertIsNone(WorkspaceInfo(self.cmd).endpoint)

    def test_other_cloud_does_not_reuse_cache(self):
        self.save_workspace()
        self.cloud.endpoints.resource_manager = 'https://management.usgovcloudapi.net/'
        self.assertIsNone(WorkspaceInfo(self.cmd).endpoint)

    def test_other_tenant_does_not_reuse_cache(self):
        self.save_workspace()
        self.profile.return_value.get_subscription.return_value = {'tenantId': 'other-tenant'}
        self.assertIsNone(WorkspaceInfo(self.cmd).endpoint)

    def test_changed_defaults_do_not_reuse_cache(self):
        self.save_workspace()
        self.config.set_value('defaults', 'workspace', 'other-workspace')
        self.assertIsNone(WorkspaceInfo(self.cmd).endpoint)

    def test_legacy_endpoint_is_ignored_in_config_and_environment(self):
        self.config.set_value('defaults', 'endpoint', self.endpoint)
        self.assertIsNone(WorkspaceInfo(self.cmd, 'other-group', 'other-workspace').endpoint)
        with patch.dict(os.environ, {self.config.env_var_name('defaults', 'endpoint'): self.endpoint}):
            self.assertIsNone(WorkspaceInfo(self.cmd, 'other-group', 'other-workspace').endpoint)

    def test_legacy_environment_cannot_override_namespaced_cache(self):
        self.save_workspace()
        with patch.dict(os.environ, {self.config.env_var_name('defaults', 'endpoint'): self.other_endpoint}):
            self.assertEqual(WorkspaceInfo(self.cmd).endpoint, self.endpoint)

    def test_cache_survives_config_reload(self):
        self.save_workspace()
        self.cmd.cli_ctx.config = CLIConfig(config_dir=self.config.config_dir,
                                            config_env_var_prefix='QUANTUM_CACHE_TEST', use_local_config=False)
        self.assertEqual(WorkspaceInfo(self.cmd).endpoint, self.endpoint)
        self.assertFalse(self.cmd.cli_ctx.config.has_option('defaults', 'endpoint'))

    def test_no_cache_uses_arm_without_saving_defaults(self):
        job_show(self.cmd, 'job-id', 'other-group', 'other-workspace')
        self.arm.return_value.get.assert_called_once_with('other-group', 'other-workspace')
        self.assertEqual(self.config.items('defaults'), [])
        self.assertEqual(self.config.items('quantum'), [])

    def test_cache_assumes_endpoint_valid_and_preserves_service_error(self):
        self.save_workspace()
        before = self.config.get('quantum', 'workspace_endpoint_cache')
        error = ResourceNotFoundError('Job cannot be found')
        self.client.return_value.services.jobs.get.side_effect = error

        with self.assertRaises(ResourceNotFoundError) as raised:
            job_show(self.cmd, 'job-id', 'saved-group', 'saved-workspace')

        self.assertIs(raised.exception, error)
        self.client.return_value.services.jobs.get.assert_called_once()
        self.arm.assert_not_called()
        self.assertEqual(self.config.get('quantum', 'workspace_endpoint_cache'), before)

    def test_missing_workspace_identity_does_not_use_cache(self):
        self.save_workspace()
        self.config.remove_option('defaults', 'workspace')
        self.assertIsNone(WorkspaceInfo(self.cmd).endpoint)

    def test_cache_identity_is_case_insensitive(self):
        self.save_workspace()
        self.subscription.return_value = 'SAVED-SUBSCRIPTION'
        self.profile.return_value.get_subscription.return_value = {'tenantId': 'SAVED-TENANT'}
        self.cloud.endpoints.resource_manager = 'https://MANAGEMENT.AZURE.COM'
        self.assertEqual(WorkspaceInfo(self.cmd, 'SAVED-GROUP', 'SAVED-WORKSPACE').endpoint, self.endpoint)

    def test_clear_removes_owned_cache_and_preserves_unrelated_settings(self):
        self.config.set_value('defaults', 'endpoint', 'devcenter-endpoint')
        self.config.set_value('defaults', 'location', 'westus')
        self.config.set_value('defaults', 'target_id', 'target')
        self.config.set_value('quantum', 'version_check_date', '2026-09-10')
        self.save_workspace()

        clear(self.cmd)

        self.assertEqual(self.config.get('defaults', 'group'), '')
        self.assertEqual(self.config.get('defaults', 'workspace'), '')
        self.assertFalse(self.config.has_option('quantum', 'workspace_endpoint_cache'))
        self.assertEqual(self.config.get('defaults', 'endpoint'), 'devcenter-endpoint')
        self.assertEqual(self.config.get('defaults', 'location'), 'westus')
        self.assertEqual(self.config.get('defaults', 'target_id'), 'target')
        self.assertEqual(self.config.get('quantum', 'version_check_date'), '2026-09-10')

    def test_explicit_internal_endpoint_still_takes_precedence(self):
        self.save_workspace()
        self.assertEqual(WorkspaceInfo(self.cmd, endpoint=self.other_endpoint).endpoint, self.other_endpoint)
        self.assertEqual(WorkspaceInfo(self.cmd, endpoint='').endpoint, '')

    def test_unreadable_cache_is_a_miss(self):
        self.save_workspace()
        for value in ('not-json', '[]', 'null', '{"version": 99}', '{"version": 1}', ''):
            with self.subTest(value=value):
                self.config.set_value('quantum', 'workspace_endpoint_cache', value)
                self.assertIsNone(WorkspaceInfo(self.cmd).endpoint)

    def test_incomplete_cache_is_a_miss(self):
        self.save_workspace()
        cache = json.loads(self.config.get('quantum', 'workspace_endpoint_cache'))
        for key in cache:
            with self.subTest(key=key):
                incomplete = {name: value for name, value in cache.items() if name != key}
                self.config.set_value('quantum', 'workspace_endpoint_cache', json.dumps(incomplete))
                self.assertIsNone(WorkspaceInfo(self.cmd).endpoint)

    def test_set_replaces_cache_using_arm_metadata(self):
        self.save_workspace()
        with patch('azext_quantum.operations.workspace.cf_workspaces') as workspaces:
            workspace = workspaces.return_value.get.return_value
            workspace.properties.endpoint_uri = self.other_endpoint
            result = set_workspace(self.cmd, 'other-workspace', 'other-group')

        self.assertIs(result, workspace)
        workspaces.return_value.get.assert_called_once_with('other-group', 'other-workspace')
        self.assertEqual(WorkspaceInfo(self.cmd).endpoint, self.other_endpoint)
        self.assertIsNone(WorkspaceInfo(self.cmd, 'saved-group', 'saved-workspace').endpoint)
