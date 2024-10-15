# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import unittest
from azure.cli.testsdk import (ScenarioTest)
from .common.test_utils import get_test_cmd
from .custom_preparers import SpringPreparer, SpringResourceGroupPreparer
from .custom_dev_setting_constant import SpringTestEnvironmentEnum
from ...vendored_sdks.appplatform.v2024_05_01_preview import models
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


def _get_basic_mock_client(*_):
    return mock.MagicMock()


def _mock_not_get_dev_tool_portal(*_):
    return None


def _mock_dev_tool_portal(enable_live_view):
    resource = models.DevToolPortalResource.deserialize(json.loads('{"properties":{"provisioningState": "Succeeded"}}'))
    resource.properties.features = models.DevToolPortalFeatureSettings(
        application_live_view=models.DevToolPortalFeatureDetail(
            state=models.DevToolPortalFeatureState.ENABLED if enable_live_view
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
        self.dev_tool_portal = None
        self.deleted = False
        self.created_alv_request = None
        self.dev_tool_portal_request = None

    def setUp(self):
        resp = super().setUp()
        free_mock_client.reset_mock()
        return resp

    # @mock.patch('azext_spring._utils.cf_resource_groups', _cf_resource_group)
    def _execute(self, method, cmd, client, *kwargs):
        client = client or _get_basic_mock_client()
        method(cmd, client, *kwargs)
        self.created_alv_request = client.application_live_views.begin_create_or_update.call_args_list
        self.created_resource = self.created_alv_request[0][0][3] if self.created_alv_request else None
        self.dev_tool_portal_request = client.dev_tool_portals.begin_create_or_update.call_args_list
        self.dev_tool_portal = self.dev_tool_portal_request[0][0][3] if self.dev_tool_portal_request else None
        self.deleted = client.application_live_views.begin_delete.call_args_list is not None

    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_not_get_dev_tool_portal)
    def test_asa_alv_create_dev_tool_portal_disable_wait(self):
        self._execute(create, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertEqual('rg', self.created_alv_request[0][0][0])
        self.assertEqual('asa', self.created_alv_request[0][0][1])
        self.assertEqual('default', self.created_alv_request[0][0][2])
        self.assertIsNone(self.dev_tool_portal)

    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_enabled_get_dev_tool_portal)
    def test_asa_alv_create_skip_configure_dev_tool_portal_wait(self):
        self._execute(create, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)

    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_disabled_get_dev_tool_portal)
    def test_asa_alv_create_configure_dev_tool_portal_wait(self):
        self._execute(create, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNotNone(self.dev_tool_portal)
        self.assertEqual(models.DevToolPortalFeatureState.ENABLED,
                         self.dev_tool_portal.properties.features.application_live_view.state)
        self.assertEqual('rg', self.dev_tool_portal_request[0][0][0])
        self.assertEqual('asa', self.dev_tool_portal_request[0][0][1])
        self.assertEqual('default', self.dev_tool_portal_request[0][0][2])

    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_not_get_dev_tool_portal)
    def test_asa_alv_delete_dev_tool_portal_disable_wait(self):
        self._execute(delete, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)
        self.assertTrue(self.deleted)

    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_disabled_get_dev_tool_portal)
    def test_asa_alv_delete_skip_configure_dev_tool_portal_wait(self):
        self._execute(delete, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertTrue(self.deleted)
        self.assertIsNone(self.dev_tool_portal)

    @mock.patch('azext_spring.application_live_view.get_dev_tool_portal', _mock_enabled_get_dev_tool_portal)
    def test_asa_alv_delete_configure_dev_tool_portal_wait(self):
        self._execute(delete, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertTrue(self.deleted)
        self.assertIsNotNone(self.dev_tool_portal)
        self.assertEqual(models.DevToolPortalFeatureState.DISABLED,
                         self.dev_tool_portal.properties.features.application_live_view.state)


class LiveViewTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE['spring'])
    def test_live_view(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group
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

        self.cmd('spring application-live-view delete -g {rg} -s {serviceName} -y')

        self.cmd('spring dev-tool show -g {rg} -s {serviceName}', checks=[
            self.check('properties.features.applicationLiveView.state', 'Disabled')
        ])
