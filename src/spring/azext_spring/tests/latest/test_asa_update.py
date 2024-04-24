# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from .common.test_utils import get_test_cmd
from ...custom import spring_update
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


def _mock_get_mgmt_service_client(cli_ctx, client_or_resource_type):
    monitoring_settings = mock.MagicMock()
    monitoring_settings.properties = None
    client = mock.MagicMock()
    client.monitoring_settings.get.return_value = monitoring_settings
    return client


def _get_basic_mock_client(*_):
    return mock.MagicMock()


class BasicTest(unittest.TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.updated_resource = None

    def setUp(self):
        resp = super().setUp()
        free_mock_client.reset_mock()
        return resp

    @mock.patch('azext_spring.custom.get_mgmt_service_client', _mock_get_mgmt_service_client)
    def _execute(self, resource_group, name, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        spring_update(get_test_cmd(), client, resource_group, name, **kwargs)
        call_args = client.services.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(3, len(call_args[0][1]))
        self.assertEqual(resource_group, call_args[0][1]['resource_group_name'])
        self.assertEqual(name, call_args[0][1]['service_name'])
        self.updated_resource = call_args[0][1]['resource']


class TestSpringAppUpdateWithPlannedMaintenance(BasicTest):
    def test_asa_update_with_planned_maintenance(self):
        day_of_week = 'Friday'
        start_hour = 10
        self._execute('rg', 'asa', enable_planned_maintenance=True, planned_maintenance_day=day_of_week, planned_maintenance_start_hour=start_hour)
        resource = self.updated_resource
        self.assertEqual(day_of_week, resource.properties.maintenance_schedule_configuration.day)
        self.assertEqual(start_hour, resource.properties.maintenance_schedule_configuration.hour)
