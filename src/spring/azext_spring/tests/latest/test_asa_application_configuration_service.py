# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ...application_configuration_service import (application_configuration_service_create,
                                                  application_configuration_service_update)

import unittest
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError, ArgumentUsageError
from .common.test_utils import get_test_cmd
from ..._validators_enterprise import validate_refresh_interval
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

    @mock.patch('azext_spring._utils.cf_resource_groups', _cf_resource_group)
    def _execute(self, resource_group, generation, refresh_interval, **kwargs):
        client = kwargs.pop('client', None) or _get_basic_mock_client()
        application_configuration_service_create(get_test_cmd(), client, 'myasa',
                                                 resource_group, generation, refresh_interval)
        call_args = client.configuration_services.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        self.assertEqual((resource_group, generation),
                         (call_args[0][0][0], call_args[0][0][3].properties.generation))
        self.created_resource = call_args[0][0][3]


class TestApplicationConfigurationService(BasicTest):
    def test_acs_create(self):
        self._execute('rg', 'Gen1', 120)
        resource = self.created_resource
        self.assertIsNotNone(resource.properties)
        self.assertEqual(120, resource.properties.settings.refresh_interval_in_seconds)


class TestApplicationConfigurationServiceValidator(unittest.TestCase):
    def test_validate_refresh_interval_parameter(self):
        ns = Namespace(refresh_interval="a")
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_refresh_interval(ns)
        self.assertEqual("--refresh-interval should be a number.", str(context.exception))

        ns = Namespace(refresh_interval=-1)
        with self.assertRaises(ArgumentUsageError) as context:
            validate_refresh_interval(ns)
        self.assertEqual("--refresh-interval must be greater than or equal to 0.", str(context.exception))
