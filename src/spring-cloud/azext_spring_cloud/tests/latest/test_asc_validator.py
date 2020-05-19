# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from argparse import Namespace
from azure.cli.core.util import CLIError
from ..._validators import (validate_vnet, validate_vnet_required_parameters, _validate_cidr_range)

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand


def _get_test_cmd():
    cli_ctx = DummyCli()
    cli_ctx.data['subscription_id'] = '00000000-0000-0000-0000-000000000000'
    loader = AzCommandsLoader(cli_ctx, resource_type='Microsoft.AppPlatform')
    cmd = AzCliCommand(loader, 'test', None)
    cmd.command_kwargs = {'resource_type': 'Microsoft.AppPlatform'}
    cmd.cli_ctx = cli_ctx
    return cmd


class TestValidateIPRanges(unittest.TestCase):
    def test_lack_of_parameters(self):
        ns = Namespace(vnet='test-vnet', app_subnet='app', service_runtime_subnet='svc', resource_group='test', reserved_cidr_range=None)
        with self.assertRaises(CLIError) as context:
            validate_vnet_required_parameters(ns)
            self.assertEqual('--reserved-cidr-range, --app-subnet, --service-runtime-subnet must be set when deploying to VNet',
                             str(context.exception))

    def test_single_cidr(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8')
        _validate_cidr_range(ns)
        self.assertEqual(ns.reserved_cidr_range, '10.0.0.0/8')

    def test_multi_cidr(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16')
        _validate_cidr_range(ns)
        self.assertEqual(ns.reserved_cidr_range, '10.0.0.0/8,20.0.0.0/16,30.0.0.0/16')

    def test_multi_cidr_with_additional_commas(self):
        ns = Namespace(reserved_cidr_range=',10.0.0.0/8,,20.0.0.0/16,,30.0.0.0/16,')
        _validate_cidr_range(ns)
        self.assertEqual(ns.reserved_cidr_range, '10.0.0.0/8,20.0.0.0/16,30.0.0.0/16')

    def test_multi_cidr_with_overlaps(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,10.0.0.0/16,30.0.0.0/16')
        with self.assertRaises(CLIError) as context:
            _validate_cidr_range(ns)
            self.assertEqual('--reserved-cidr-range should not overlap each other, but 10.0.0.0/8 and 10.0.0.0/16 overlapping.',
                             str(context.exception))

    def test_valid_vnet(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8', vnet='test-vnet', app_subnet='app', service_runtime_subnet='svc', resource_group='test')
        validate_vnet(_get_test_cmd(), ns)
        self.assertEqual(ns.app_subnet.lower(),
                         '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app'.lower())
        self.assertEqual(ns.service_runtime_subnet.lower(),
                         '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc'.lower())

    def test_invalid_vnet(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8',
                       vnet='/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/NetworkInterfaces/test-vnet',
                       app_subnet='app', service_runtime_subnet='svc', resource_group='test')
        with self.assertRaises(CLIError) as context:
            validate_vnet(_get_test_cmd(), ns)
            self.assertTrue('is not a valid VirtualNetwork resource ID' in str(context.exception))

    def test_only_subnet_name(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8', app_subnet='app', service_runtime_subnet='svc', resource_group='test', vnet=None)
        with self.assertRaises(CLIError) as context:
            validate_vnet(_get_test_cmd(), ns)
            self.assertTrue('is not a valid subnet resource ID' in str(context.exception))

    def test_valid_subnets(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8', resource_group='test', vnet=None,
                       app_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc')
        validate_vnet(_get_test_cmd(), ns)
        self.assertEqual(ns.app_subnet.lower(),
                         '/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app'.lower())
        self.assertEqual(ns.service_runtime_subnet.lower(),
                         '/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc'.lower())

    def test_subnets_same(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8', resource_group='test', vnet=None,
                       app_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualnetworks/test-Vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app')
        with self.assertRaises(CLIError) as context:
            validate_vnet(_get_test_cmd(), ns)
            self.assertEqual('--app-subnet and --service-runtime-subnet should not be same.', str(context.exception))

    def test_subnets_in_different_vnet(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8', resource_group='test', vnet=None,
                       app_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualnetworks/test-Vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet1/subnets/svc')
        with self.assertRaises(CLIError) as context:
            validate_vnet(_get_test_cmd(), ns)
            self.assertEqual('--app-subnet and --service-runtime-subnet should be in the same Virtual Networks.', str(context.exception))
