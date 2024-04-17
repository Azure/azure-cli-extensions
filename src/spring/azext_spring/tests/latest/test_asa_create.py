# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from .common.test_utils import get_test_cmd
from ...vendored_sdks.appplatform.v2024_05_01_preview import models
from ...spring_instance import (spring_create)
from ..._utils import (_get_sku_name)

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand

from knack.log import get_logger

logger = get_logger(__name__)
free_mock_client = mock.MagicMock()


def _cf_resource_group(cli_ctx, subscription_id=None):
    client = mock.MagicMock()
    rg = mock.MagicMock()
    rg.location = 'east us'
    client.resource_groups.get.return_value = rg
    return client


def _get_basic_mock_client(*_):
    return mock.MagicMock()


class BasicTest(unittest.TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.created_resource = None

    def setUp(self):
        resp = super().setUp()
        free_mock_client.reset_mock()
        return resp

    def _get_sku(self, tier='Standard'):
        return models.Sku(
            tier=tier,
            name=_get_sku_name(tier)
        )

    @mock.patch('azext_spring._utils.cf_resource_groups', _cf_resource_group)
    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        spring_create(get_test_cmd(), client, resource_group, name, **kwargs)
        call_args = client.services.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(3, len(call_args[0][0]))
        self.assertEqual((resource_group, name), call_args[0][0][0:2])
        self.created_resource = call_args[0][0][2]


class TestSpringCloudCreateEnterprise(BasicTest):
    def test_asc_create_enterprise(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), disable_app_insights=True)
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)
        self.assertIsNone(resource.properties.marketplace_resource)

    def test_asc_create_enterprise_with_plan(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), disable_app_insights=True,
                      marketplace_plan_id='my-plan')
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)
        self.assertEqual('my-plan', resource.properties.marketplace_resource.plan)
        self.assertEqual('azure-spring-cloud-vmware-tanzu-2', resource.properties.marketplace_resource.product)
        self.assertEqual('vmware-inc', resource.properties.marketplace_resource.publisher)


class TestSpringAppsCreateWithApplicationLiveView(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.alv_resource = None
        self.alv_request = None
        self.dev_tool = None
        self.dev_tool_request = None

    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        super()._execute(resource_group, name, client=client, **kwargs)
        self.alv_request = client.application_live_views.begin_create_or_update.call_args_list
        self.alv_resource = self.alv_request[0][0][3] if self.alv_request else None
        self.dev_tool_request = client.dev_tool_portals.begin_create_or_update.call_args_list
        self.dev_tool = self.dev_tool_request[0][0][3] if self.dev_tool_request else None

    def test_asa_enterprise_with_alv(self):
        self._execute('rg', 'asa', sku=self._get_sku('Enterprise'), enable_application_live_view=True,
                      disable_app_insights=True)
        self.assertIsNotNone(self.alv_resource)
        self.assertEqual('rg', self.alv_request[0][0][0])
        self.assertEqual('asa', self.alv_request[0][0][1])
        self.assertEqual('default', self.alv_request[0][0][2])
        self.assertIsNotNone(self.dev_tool)
        self.assertEqual(models.DevToolPortalFeatureState.ENABLED,
                         self.dev_tool.properties.features.application_live_view.state)
        self.assertEqual('rg', self.dev_tool_request[0][0][0])
        self.assertEqual('asa', self.dev_tool_request[0][0][1])
        self.assertEqual('default', self.dev_tool_request[0][0][2])

    def test_asa_enterprise_without_alv(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), enable_application_live_view=False,
                      disable_app_insights=True)
        self.assertIsNone(self.alv_resource)
        self.assertIsNone(self.dev_tool)

    def test_asa_standard_with_alv(self):
        self._execute('rg', 'asc', sku=self._get_sku('Standard'), enable_application_live_view=True,
                      disable_app_insights=True)
        self.assertIsNone(self.alv_resource)
        self.assertIsNone(self.dev_tool)

    def test_asa_basic_with_alv(self):
        self._execute('rg', 'asc', sku=self._get_sku('Basic'), enable_application_live_view=True,
                      disable_app_insights=True)
        self.assertIsNone(self.alv_resource)
        self.assertIsNone(self.dev_tool)


class TestSpringAppsCreateWithApplicationConfigurationService(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.acs_resource = None
        self.acs_request = None

    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        super()._execute(resource_group, name, client=client, **kwargs)
        self.acs_request = client.configuration_services.begin_create_or_update.call_args_list
        self.acs_resource = self.acs_request[0][0][3] if self.acs_request else None

    def test_asa_enterprise_with_acs(self):
        self._execute('rg', 'asa', sku=self._get_sku('Enterprise'),
                      enable_application_configuration_service=True)
        self.assertIsNotNone(self.acs_resource)
        self.assertEqual('rg', self.acs_request[0][0][0])
        self.assertEqual('asa', self.acs_request[0][0][1])
        self.assertEqual('default', self.acs_request[0][0][2])
        self.assertIsNotNone(self.acs_resource)
        self.assertEqual(models.ConfigurationServiceGeneration.GEN2, self.acs_resource.properties.generation)


class TestSpringAppsCreateWithApplicationAccelerator(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.acc_resource = None
        self.dev_tool = None

    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        super()._execute(resource_group, name, client=client, **kwargs)
        call_args = client.application_accelerators.begin_create_or_update.call_args_list
        self.acc_resource = call_args[0][0][3] if call_args else None
        call_args = client.dev_tool_portals.begin_create_or_update.call_args_list
        self.dev_tool = call_args[0][0][3] if call_args else None

    def test_asa_enterprise_with_acc(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), enable_application_accelerator=True,
                      disable_app_insights=True)
        self.assertIsNotNone(self.acc_resource)
        self.assertIsNotNone(self.dev_tool)

    def test_asa_enterprise_without_acc(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), enable_application_accelerator=False,
                      disable_app_insights=True)
        self.assertIsNone(self.acc_resource)
        self.assertIsNone(self.dev_tool)

    def test_asa_standard_with_acc(self):
        self._execute('rg', 'asc', sku=self._get_sku('Standard'), enable_application_accelerator=True,
                      disable_app_insights=True)
        self.assertIsNone(self.acc_resource)
        self.assertIsNone(self.dev_tool)

    def test_asa_basic_with_acc(self):
        self._execute('rg', 'asc', sku=self._get_sku('Basic'), enable_application_accelerator=True,
                      disable_app_insights=True)
        self.assertIsNone(self.acc_resource)
        self.assertIsNone(self.dev_tool)


def _workspaces_get_func(*args, **kwargs):
    if args[1] == 'asc-with-existing-workspace':
        workspace = mock.MagicMock()
        workspace.id = 'workspace-id'
        return workspace
    else:
        return None


class TestSpringCloudCreateWithAI(BasicTest):
    def _get_ai_client(ctx, type, api_version=None):
        free_mock_client.workspaces.get.side_effect = _workspaces_get_func
        ai_create_resource = mock.MagicMock()
        ai_create_resource.connection_string = 'fake-connection'
        free_mock_client.components.create_or_update.return_value = ai_create_resource
        ai_get_resource = mock.MagicMock()
        ai_get_resource.connection_string = 'get-connection'
        free_mock_client.components.get.return_value = ai_get_resource
        return free_mock_client

    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.monitoring_settings_resource = None

    @mock.patch('azext_spring.custom.get_mgmt_service_client', _get_ai_client)
    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        super()._execute(resource_group, name, client=client, **kwargs)

        call_args = free_mock_client.monitoring_settings.begin_update_put.call_args_list

        self.assertEqual(1, len(call_args))
        self.assertEqual(3, len(call_args[0][1]))
        self.assertEqual(resource_group, call_args[0][1]['resource_group_name'])
        self.assertEqual(name, call_args[0][1]['service_name'])
        self.monitoring_settings_resource = call_args[0][1]['monitoring_setting_resource']

    def test_asc_create_with_AI_happy_path(self):
        self._execute('rg', 'asc', sku=self._get_sku())
        resource = self.created_resource
        self.assertEqual('S0', resource.sku.name)
        self.assertEqual('Standard', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)
        self.assertEqual('fake-connection',
                         self.monitoring_settings_resource.properties.app_insights_instrumentation_key)
        self.assertEqual(True, self.monitoring_settings_resource.properties.trace_enabled)

    def test_asc_create_with_AI_and_existing_workspace(self):
        self._execute('rg', 'asc-with-existing-workspace', sku=self._get_sku())
        resource = self.created_resource
        self.assertEqual('S0', resource.sku.name)
        self.assertEqual('Standard', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)
        self.assertEqual('fake-connection', self.monitoring_settings_resource.properties.app_insights_instrumentation_key)
        self.assertEqual(True, self.monitoring_settings_resource.properties.trace_enabled)

    def test_asc_create_with_AI_key(self):
        self._execute('rg', 'asc', sku=self._get_sku(), app_insights_key='my-key')
        resource = self.created_resource
        self.assertEqual('S0', resource.sku.name)
        self.assertEqual('Standard', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)
        self.assertEqual('my-key', self.monitoring_settings_resource.properties.app_insights_instrumentation_key)
        self.assertEqual(True, self.monitoring_settings_resource.properties.trace_enabled)

    def test_asc_create_with_AI_name(self):
        self._execute('rg', 'asc', sku=self._get_sku(), app_insights='my-key')
        resource = self.created_resource
        self.assertEqual('S0', resource.sku.name)
        self.assertEqual('Standard', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)
        self.assertEqual('get-connection',
                         self.monitoring_settings_resource.properties.app_insights_instrumentation_key)
        self.assertEqual(True, self.monitoring_settings_resource.properties.trace_enabled)


class TestSpringCloudCreateEnterpriseWithApplicationInsights(BasicTest):
    def _get_application_insights_client(ctx, type, api_version=None):
        application_insights_create_resource = mock.MagicMock()
        application_insights_create_resource.connection_string = 'fake-create-connection-string'

        application_insights_get_resource = mock.MagicMock()
        application_insights_get_resource.connection_string = 'fake-get-connection-string'

        free_mock_client.components.create_or_update.return_value = application_insights_create_resource
        free_mock_client.components.get.return_value = application_insights_get_resource

        return free_mock_client

    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.buildpack_binding_resource = None

    @mock.patch('azext_spring.buildpack_binding.get_mgmt_service_client', _get_application_insights_client)
    @mock.patch('azext_spring.custom.get_mgmt_service_client', _get_application_insights_client)
    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        super()._execute(resource_group, name, client=client, **kwargs)

        call_args = client.buildpack_binding.begin_create_or_update.call_args_list

        self.assertEqual(1, len(call_args))
        self.assertEqual(2, len(call_args[0]))
        self.assertEqual(resource_group, call_args[0][0][0])
        self.assertEqual(name, call_args[0][0][1])
        self.assertEqual("default", call_args[0][0][2])
        self.assertEqual("default", call_args[0][0][3])
        self.assertEqual("default", call_args[0][0][4])
        self.buildpack_binding_resource = call_args[0][0][5]

    def test_asc_create_with_application_insights_default(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'))
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual('ApplicationInsights', self.buildpack_binding_resource.properties.binding_type)
        self.assertEqual('fake-create-connection-string',
                         self.buildpack_binding_resource.properties.launch_properties.properties['connection-string'])
        self.assertEqual(10,
                         self.buildpack_binding_resource.properties.launch_properties.properties['sampling-percentage'])

    def test_asc_create_with_application_insights_key(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), app_insights_key='test-application-insights-key',
                      sampling_rate=23)
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual('ApplicationInsights', self.buildpack_binding_resource.properties.binding_type)
        self.assertEqual('test-application-insights-key',
                         self.buildpack_binding_resource.properties.launch_properties.properties['connection-string'])
        self.assertEqual(23,
                         self.buildpack_binding_resource.properties.launch_properties.properties['sampling-percentage'])

    def test_asc_create_with_application_insights_name(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), app_insights='test-application-insights',
                      sampling_rate=53)
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual('ApplicationInsights', self.buildpack_binding_resource.properties.binding_type)
        self.assertEqual('fake-get-connection-string',
                         self.buildpack_binding_resource.properties.launch_properties.properties['connection-string'])
        self.assertEqual(53,
                         self.buildpack_binding_resource.properties.launch_properties.properties['sampling-percentage'])


class TestSpringAppCreateWithIngressConfig(BasicTest):
    def test_asa_create_basic_with_ingress_config(self):
        self._execute('rg', 'asc', sku=self._get_sku('Basic'), ingress_read_timeout=500, disable_app_insights=True)
        resource = self.created_resource
        self.assertEqual(500, resource.properties.network_profile.ingress_config.read_timeout_in_seconds)

    def test_asa_create_standard_with_ingress_config(self):
        self._execute('rg', 'asc', sku=self._get_sku('Standard'), ingress_read_timeout=300, disable_app_insights=True)
        resource = self.created_resource
        self.assertEqual(300, resource.properties.network_profile.ingress_config.read_timeout_in_seconds)

    def test_asa_create_enterprise_with_ingress_config(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), ingress_read_timeout=100, disable_app_insights=True)
        resource = self.created_resource
        self.assertEqual(100, resource.properties.network_profile.ingress_config.read_timeout_in_seconds)


class TestSpringAppCreateWithLogStreamConfig(BasicTest):
    def test_asa_create_standard_with_log_stream_config(self):
        self._execute('rg', 'asc', sku=self._get_sku('Standard'), enable_dataplane_public_endpoint=True,
                      disable_app_insights=True)
        resource = self.created_resource
        self.assertEqual(True, resource.properties.vnet_addons.data_plane_public_endpoint)

    def test_asa_create_enterprise_with_log_stream_config(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), enable_dataplane_public_endpoint=True,
                      disable_app_insights=True)
        resource = self.created_resource
        self.assertEqual(True, resource.properties.vnet_addons.data_plane_public_endpoint)
