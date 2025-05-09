# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.core.azclierror import ResourceNotFoundError
from knack.util import CLIError
from msrestazure.tools import resource_id
from ...vendored_sdks.appplatform.v2022_01_01_preview import models
from ...spring_cloud_instance import (spring_cloud_create)
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

def _get_test_cmd():
    cli_ctx = DummyCli()
    cli_ctx.data['subscription_id'] = '00000000-0000-0000-0000-000000000000'
    loader = AzCommandsLoader(cli_ctx, resource_type='Microsoft.AppPlatform')
    cmd = AzCliCommand(loader, 'test', None)
    cmd.command_kwargs = {'resource_type': 'Microsoft.AppPlatform'}
    cmd.cli_ctx = cli_ctx
    return cmd


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

    @mock.patch('azext_spring_cloud._utils.cf_resource_groups', _cf_resource_group)
    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        spring_cloud_create(_get_test_cmd(), client, resource_group, name, **kwargs)
        call_args = client.services.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(3, len(call_args[0][0]))
        self.assertEqual((resource_group, name), call_args[0][0][0:2])
        self.created_resource = call_args[0][0][2]


class TestSpringCloudCreateEnerprise(BasicTest):
    def test_asc_create_enterprise(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), disable_app_insights=True)
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)


class TestSpringCloudCreateWithAI(BasicTest):
    def _get_ai_client(ctx, type):
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
    
    @mock.patch('azext_spring_cloud.custom.get_mgmt_service_client', _get_ai_client)
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
        self.assertEqual('get-connection', self.monitoring_settings_resource.properties.app_insights_instrumentation_key)
        self.assertEqual(True, self.monitoring_settings_resource.properties.trace_enabled)


class TestSpringCloudCreateEnerpriseWithApplicationInsights(BasicTest):
    def _get_application_insights_client(ctx, type):
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

    @mock.patch('azext_spring_cloud.buildpack_binding.get_mgmt_service_client', _get_application_insights_client)
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
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), app_insights_key='test-application-insights-key', sampling_rate=23)
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual('ApplicationInsights', self.buildpack_binding_resource.properties.binding_type)
        self.assertEqual('test-application-insights-key',
            self.buildpack_binding_resource.properties.launch_properties.properties['connection-string'])
        self.assertEqual(23,
            self.buildpack_binding_resource.properties.launch_properties.properties['sampling-percentage'])

    def test_asc_create_with_application_insights_name(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'), app_insights='test-application-insights', sampling_rate=53)
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual('ApplicationInsights', self.buildpack_binding_resource.properties.binding_type)
        self.assertEqual('fake-get-connection-string',
            self.buildpack_binding_resource.properties.launch_properties.properties['connection-string'])
        self.assertEqual(53,
            self.buildpack_binding_resource.properties.launch_properties.properties['sampling-percentage'])
