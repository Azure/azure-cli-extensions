# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import unittest
from azure.cli.testsdk import (ScenarioTest, record_only)
from azure.cli.core.azclierror import ResourceNotFoundError
from knack.util import CLIError
from ...vendored_sdks.appplatform.v2022_11_01_preview import models
from ...application_live_view import (create, delete)
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


def _get_basic_mock_client(*_):
    return mock.MagicMock()


def _mock_not_get_dev_tool_portal(*_):
    return None


def _mock_dev_tool_portal(enable_live_view):
    resource = models.DevToolPortalResource.deserialize(json.loads('{"properties":{"provisioningState": "Succeeded"}}'))
    resource.properties.features = models.DevToolPortalFeatureSettings(
        application_live_view=models.DevToolPortalFeatureDetail(
            state=models.DevToolPortalFeatureState.ENABLED if enable_live_view \
                    else models.DevToolPortalFeatureState.DISABLED
        )
    )
    return resource

def _mock_enabled_get_dev_tool_portal(*_):
    return _mock_dev_tool_portal(enable_live_view=True)

def _mock_disabled_get_dev_tool_portal(*_):
    return _mock_dev_tool_portal(enable_live_view=False)

class ApplicationLiveView(unittest.TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.created_resource = None
        self.dev_tool_portal =None
        self.deleted = False
    
    def setUp(self):
        resp = super().setUp()
        free_mock_client.reset_mock()
        return resp
    
    # @mock.patch('azext_spring._utils.cf_resource_groups', _cf_resource_group)
    def _execute(self, method, cmd, client, *kwargs):
        client = client or _get_basic_mock_client()
        method(cmd, client, *kwargs)
        call_args = client.application_live_views.begin_create_or_update.call_args_list
        self.created_resource = call_args[0][0][3] if call_args else None
        call_args = client.dev_tool_portals.begin_create_or_update.call_args_list
        self.dev_tool_portal = call_args[0][0][3] if call_args else None
        self.deleted = client.application_live_views.begin_delete.call_args_list is not None

    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_not_get_dev_tool_portal)
    def test_asa_alv_create_dev_tool_portal_disable_wait(self):
        self._execute(create, _get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)

    
    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_enabled_get_dev_tool_portal)
    def test_asa_alv_create_skip_configure_dev_tool_portal_wait(self):
        self._execute(create, _get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)


    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_disabled_get_dev_tool_portal)
    def test_asa_alv_create_configure_dev_tool_portal_wait(self):
        self._execute(create, _get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNotNone(self.dev_tool_portal)
        self.assertEqual(models.DevToolPortalFeatureState.ENABLED,
                         self.dev_tool_portal.properties.features.application_live_view.state)


    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_not_get_dev_tool_portal)
    def test_asa_alv_delete_dev_tool_portal_disable_wait(self):
        self._execute(delete, _get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)
        self.assertTrue(self.deleted)

    
    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_disabled_get_dev_tool_portal)
    def test_asa_alv_delete_skip_configure_dev_tool_portal_wait(self):
        self._execute(delete, _get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertTrue(self.deleted)
        self.assertIsNone(self.dev_tool_portal)


    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_enabled_get_dev_tool_portal)
    def test_asa_alv_delete_configure_dev_tool_portal_wait(self):
        self._execute(delete, _get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertTrue(self.deleted)
        self.assertIsNotNone(self.dev_tool_portal)
        self.assertEqual(models.DevToolPortalFeatureState.DISABLED,
                         self.dev_tool_portal.properties.features.application_live_view.state)

@record_only()
class LiveViewTest(ScenarioTest):

    def test_live_view(self):
        self.kwargs.update({
            'serviceName': 'test-cli',
            'rg': 'test-cli'
        })

        self.cmd('spring dev-tool create -g {rg} -s {serviceName} --assign-endpoint', checks=[
            self.check('properties.public', True),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-live-view create -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring dev-tool show -g {rg} -s {serviceName}', checks=[
            self.check('properties.features.applicationLiveView.state', 'Enabled')
        ])

        self.cmd('spring application-live-view delete -g {rg} -s {serviceName}')

        self.cmd('spring dev-tool show -g {rg} -s {serviceName}', checks=[
            self.check('properties.features.applicationLiveView.state', 'Disabled')
        ])
