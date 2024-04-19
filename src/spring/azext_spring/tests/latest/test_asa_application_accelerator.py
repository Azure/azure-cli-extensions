# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import unittest
from azure.cli.testsdk import (ScenarioTest)
from .common.test_utils import get_test_cmd
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum
from ...vendored_sdks.appplatform.v2024_05_01_preview import models
from ...application_accelerator import (application_accelerator_create as create,
                                        application_accelerator_delete as delete)

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


def _mock_dev_tool_portal(enable_accelerator):
    resource = models.DevToolPortalResource.deserialize(json.loads('{"properties":{"provisioningState": "Succeeded"}}'))
    resource.properties.features = models.DevToolPortalFeatureSettings(
        application_accelerator=models.DevToolPortalFeatureDetail(
            state=models.DevToolPortalFeatureState.ENABLED if enable_accelerator
            else models.DevToolPortalFeatureState.DISABLED
        )
    )
    return resource


def _mock_enabled_get_dev_tool_portal(*_):
    return _mock_dev_tool_portal(enable_accelerator=True)


def _mock_disabled_get_dev_tool_portal(*_):
    return _mock_dev_tool_portal(enable_accelerator=False)


class ApplicationAccelerator(unittest.TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.created_resource = None
        self.dev_tool_portal = None
        self.deleted = False

    def setUp(self):
        resp = super().setUp()
        free_mock_client.reset_mock()
        return resp

    # @mock.patch('azext_spring._utils.cf_resource_groups', _cf_resource_group)
    def _execute(self, method, cmd, client, *kwargs):
        client = client or _get_basic_mock_client()
        method(cmd, client, *kwargs)
        call_args = client.application_accelerators.begin_create_or_update.call_args_list
        self.created_resource = call_args[0][0][3] if call_args else None
        call_args = client.dev_tool_portals.begin_create_or_update.call_args_list
        self.dev_tool_portal = call_args[0][0][3] if call_args else None
        self.deleted = client.application_accelerators.begin_delete.call_args_list is not None

    @mock.patch('azext_spring.application_accelerator.get_dev_tool_portal', _mock_not_get_dev_tool_portal)
    def test_asa_acc_create_dev_tool_portal_disable_wait(self):
        self._execute(create, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)

    @mock.patch('azext_spring.application_accelerator.get_dev_tool_portal', _mock_enabled_get_dev_tool_portal)
    def test_asa_acc_create_skip_configure_dev_tool_portal_wait(self):
        self._execute(create, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)

    @mock.patch('azext_spring.application_accelerator.get_dev_tool_portal', _mock_disabled_get_dev_tool_portal)
    def test_asa_acc_create_configure_dev_tool_portal_wait(self):
        self._execute(create, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNotNone(self.created_resource)
        self.assertIsNotNone(self.dev_tool_portal)
        self.assertEqual(models.DevToolPortalFeatureState.ENABLED,
                         self.dev_tool_portal.properties.features.application_accelerator.state)

    @mock.patch('azext_spring.application_accelerator.get_dev_tool_portal', _mock_not_get_dev_tool_portal)
    def test_asa_acc_delete_dev_tool_portal_disable_wait(self):
        self._execute(delete, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertIsNone(self.dev_tool_portal)
        self.assertTrue(self.deleted)

    @mock.patch('azext_spring.application_accelerator.get_dev_tool_portal', _mock_disabled_get_dev_tool_portal)
    def test_asa_acc_delete_skip_configure_dev_tool_portal_wait(self):
        self._execute(delete, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertTrue(self.deleted)
        self.assertIsNone(self.dev_tool_portal)

    @mock.patch('azext_spring.application_accelerator.get_dev_tool_portal', _mock_enabled_get_dev_tool_portal)
    def test_asa_acc_delete_configure_dev_tool_portal_wait(self):
        self._execute(delete, get_test_cmd(), None, 'asa', 'rg', False)
        self.assertIsNone(self.created_resource)
        self.assertTrue(self.deleted)
        self.assertIsNotNone(self.dev_tool_portal)
        self.assertEqual(models.DevToolPortalFeatureState.DISABLED,
                         self.dev_tool_portal.properties.features.application_accelerator.state)


'''
Since the scenarios covered here depend on a Azure Spring service instance creation.
It cannot support live run. So mark it as record_only.
'''


class ApiApplicationAcceleratorTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE['spring'])
    def test_application_accelerator(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group
        })

        self.cmd('spring dev-tool create -g {rg} -s {serviceName} --assign-endpoint', checks=[
            self.check('properties.public', True),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-accelerator create -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring dev-tool show -g {rg} -s {serviceName}', checks=[
            self.check('properties.features.applicationAccelerator.state', 'Enabled')
        ])

        self.cmd('spring application-accelerator show -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring application-accelerator delete --yes -g {rg} -s {serviceName}')

        self.cmd('spring dev-tool show -g {rg} -s {serviceName}', checks=[
            self.check('properties.features.applicationAccelerator.state', 'Disabled')
        ])
