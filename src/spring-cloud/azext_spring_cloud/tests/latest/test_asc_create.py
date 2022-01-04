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
    # return 'East US'


def _get_basic_mock_client(*_):
    return mock.MagicMock()

class BasicTest(unittest.TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.created_resource = None
    
    
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


class TestSpringCloudCreate(BasicTest):
    @mock.patch('azext_spring_cloud.custom.get_mgmt_service_client', _get_basic_mock_client)
    def test_asc_create_happy_path(self):
        self._execute('rg', 'asc', sku=self._get_sku())
        resource = self.created_resource
        self.assertEqual('S0', resource.sku.name)
        self.assertEqual('Standard', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)

    def test_asc_create_enterprise(self):
        self._execute('rg', 'asc', sku=self._get_sku('Enterprise'))
        resource = self.created_resource
        self.assertEqual('E0', resource.sku.name)
        self.assertEqual('Enterprise', resource.sku.tier)
        self.assertEqual(False, resource.properties.zone_redundant)
