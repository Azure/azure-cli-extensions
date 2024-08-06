# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from argparse import Namespace
from azure.cli.core.util import CLIError
from azure.cli.core.azclierror import InvalidArgumentValueError
from .common.test_utils import get_test_cmd
from ..._validators import (validate_vnet, validate_vnet_required_parameters, _validate_cidr_range,
                            _set_default_cidr_range, validate_sku)

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand


def _mock_get_vnet(cmd, vnet_id):
    def _mock_get(id):
        def _get_subnet(vnet_id, name, address_prefix=None, app_route_table_name=None, svc_route_table_name=None,
                        ip_configurations=None, location=None):
            subnet = {
                "id": '{0}/subnets/{1}'.format(vnet_id, name),
                "name": name
            }
            route_table = None
            if name == 'app' and app_route_table_name:
                route_table = {"id": app_route_table_name}
            if name == 'svc' and svc_route_table_name:
                route_table = {"id": svc_route_table_name}
            subnet["routeTable"] = route_table

            subnet["addressPrefix"] = address_prefix
            subnet["ipConfigurations"] = ip_configurations
            return subnet

        def _get_mock_vnet(id, location, **kwargs):
            vnet = {
                "id": id,
                "location": location,
                "subnets": [_get_subnet(id, x, **kwargs) for x in ['app', 'svc']]
            }
            return vnet

        all_mocks = [
            _get_mock_vnet(
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualNetworks/test-vnet",
                'eastus',
                address_prefix='10.0.0.0/24'),
            _get_mock_vnet(
                "/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                'eastus',
                address_prefix='10.0.0.0/24'),
            _get_mock_vnet(
                "/subscriptions/22222222-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                'eastus',
                app_route_table_name='app', svc_route_table_name='svc', address_prefix='10.0.0.0/24'),
            _get_mock_vnet(
                "/subscriptions/33333333-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                'eastus',
                address_prefix='10.0.0.0/24'),
            _get_mock_vnet(
                "/subscriptions/55555555-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                'eastus',
                app_route_table_name='app', svc_route_table_name='app', address_prefix='10.0.0.0/24'),
            _get_mock_vnet(
                "/subscriptions/66666666-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                'eastus',
                app_route_table_name='app', address_prefix='10.0.0.0/24'),
        ]
        for x in all_mocks:
            if x["id"] == id:
                return x
        return None

    return _mock_get(vnet_id)


def _mock_get_graph_rbac_management_client(cli_ctx, subscription_id=None, **_):
    client = mock.MagicMock()

    def _mock_list(filter):
        service_principal = mock.MagicMock()
        service_principal.object_id = "00000000-0000-0000-0000-000000000000"
        return [service_principal]

    client.service_principals.list = _mock_list
    return client


def _mock_get_authorization_client(cli_ctx, subscription_id=None):
    client = mock.MagicMock()

    def _mock_list_for_scope(scope):
        def _get_mock_role_assignment(scope, object_id):
            role_assignment = mock.MagicMock()
            role_assignment.scope = scope
            role_assignment.principal_id = object_id
            role_assignment.role_definition_id = "/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
            return role_assignment

        all_mocks = [
            _get_mock_role_assignment(
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualNetworks/test-vnet",
                "00000000-0000-0000-0000-000000000000"),
            _get_mock_role_assignment(
                "/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                "00000000-0000-0000-0000-000000000000"),
            _get_mock_role_assignment(
                "/subscriptions/22222222-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                "00000000-0000-0000-0000-000000000000"),
            _get_mock_role_assignment(
                "/subscriptions/33333333-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet",
                "11111111-0000-0000-0000-000000000000")
        ]
        return [x for x in all_mocks if x.scope == scope]

    client.role_assignments.list_for_scope = _mock_list_for_scope
    return client


class TestValidateIPRanges(unittest.TestCase):
    def test_lack_of_parameters(self):
        ns = Namespace(vnet='test-vnet', app_subnet='app', service_runtime_subnet=None, resource_group='test',
                       reserved_cidr_range='10.0.0.0/14', sku=None, location='eastus')
        with self.assertRaises(CLIError) as context:
            validate_vnet_required_parameters(ns)
        self.assertEqual('--app-subnet, --service-runtime-subnet must be set when deploying to VNet',
                         str(context.exception))

    def test_single_cidr(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8')
        with self.assertRaises(CLIError) as context:
            _validate_cidr_range(ns)
        self.assertEqual('--reserved-cidr-range should be 3 unused /16 IP ranges', str(context.exception))

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
        self.assertEqual(
            '--reserved-cidr-range should not overlap each other, but 10.0.0.0/8 and 10.0.0.0/16 overlapping.',
            str(context.exception))

    @mock.patch('azext_spring._validators._get_vnet', _mock_get_vnet)
    @mock.patch('azext_spring._validators._get_authorization_client', _mock_get_authorization_client)
    @mock.patch('azext_spring._validators._get_graph_rbac_management_client',
                _mock_get_graph_rbac_management_client)
    def test_valid_vnet(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', vnet='test-vnet', app_subnet='app',
                       location='eastus',
                       service_runtime_subnet='svc', resource_group='test', sku=None)
        validate_vnet(get_test_cmd(), ns)
        self.assertEqual(ns.app_subnet.lower(),
                         '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app'.lower())
        self.assertEqual(ns.service_runtime_subnet.lower(),
                         '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc'.lower())

    def test_invalid_vnet(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16',
                       vnet='/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/NetworkInterfaces/test-vnet',
                       app_subnet='app', service_runtime_subnet='svc', resource_group='test', sku=None)
        with self.assertRaises(CLIError) as context:
            validate_vnet(get_test_cmd(), ns)
        self.assertTrue('is not a valid VirtualNetwork resource ID' in str(context.exception))

    def test_only_subnet_name(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', app_subnet='app',
                       service_runtime_subnet='svc', resource_group='test', vnet=None, sku=None)
        with self.assertRaises(CLIError) as context:
            validate_vnet(get_test_cmd(), ns)
        self.assertTrue('is not a valid subnet resource ID' in str(context.exception))

    @mock.patch('azext_spring._validators._get_vnet', _mock_get_vnet)
    @mock.patch('azext_spring._validators._get_authorization_client', _mock_get_authorization_client)
    @mock.patch('azext_spring._validators._get_graph_rbac_management_client',
                _mock_get_graph_rbac_management_client)
    def test_valid_subnets(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', resource_group='test', vnet=None,
                       sku=None, location='eastus',
                       app_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc')
        validate_vnet(get_test_cmd(), ns)
        self.assertEqual(ns.app_subnet.lower(),
                         '/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app'.lower())
        self.assertEqual(ns.service_runtime_subnet.lower(),
                         '/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc'.lower())

    @mock.patch('azext_spring._validators._get_vnet', _mock_get_vnet)
    @mock.patch('azext_spring._validators._get_authorization_client', _mock_get_authorization_client)
    @mock.patch('azext_spring._validators._get_graph_rbac_management_client',
                _mock_get_graph_rbac_management_client)
    def test_subnet_with_route_table(self):
        # bind with different route tables
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', resource_group='test', vnet=None,
                       sku=None, location='eastus',
                       app_subnet='/subscriptions/22222222-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/22222222-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc')
        validate_vnet(get_test_cmd(), ns)

        # bind with the same route table
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', resource_group='test', vnet=None,
                       sku=None, location='eastus',
                       app_subnet='/subscriptions/55555555-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/55555555-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc')
        with self.assertRaises(CLIError) as context:
            validate_vnet(get_test_cmd(), ns)
        self.assertTrue(
            '--service-runtime-subnet and --app-subnet should associate with different route tables.' in str(
                context.exception))

        # one subnet bind route table while the other not
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', resource_group='test', vnet=None,
                       sku=None, location='eastus',
                       app_subnet='/subscriptions/66666666-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/66666666-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc')
        with self.assertRaises(CLIError) as context:
            validate_vnet(get_test_cmd(), ns)
        self.assertTrue(
            '--service-runtime-subnet and --app-subnet should both associate with different route tables or neither.' in str(
                context.exception))

    def test_subnets_same(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', resource_group='test', vnet=None,
                       sku=None, location='eastus',
                       app_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualnetworks/test-Vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app')
        with self.assertRaises(CLIError) as context:
            validate_vnet(get_test_cmd(), ns)
        self.assertEqual('--app-subnet and --service-runtime-subnet should not be the same.', str(context.exception))

    def test_subnets_in_different_vnet(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.0/16', resource_group='test', vnet=None,
                       sku=None, location='eastus',
                       app_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualnetworks/test-Vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/11111111-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/VirtualNetworks/test-vnet1/subnets/svc')
        with self.assertRaises(CLIError) as context:
            validate_vnet(get_test_cmd(), ns)
        self.assertEqual('--app-subnet and --service-runtime-subnet should be in the same Virtual Networks.',
                         str(context.exception))

    def test_set_default_cidr_range(self):
        self.assertEqual('11.1.0.0/16,11.2.0.0/16,11.3.0.1/16', _set_default_cidr_range(['10.0.0.0/8', '11.0.2.0/16']))
        self.assertEqual('10.0.0.0/16,10.1.0.0/16,10.2.0.1/16', _set_default_cidr_range(['172.168.0.0/8']))
        # Should jump 127.0.0.0/8
        self.assertEqual('128.0.0.0/16,128.1.0.0/16,128.2.0.1/16', _set_default_cidr_range(
            ['0.0.0.0/2', '64.0.0.0/3', '96.0.0.0/4', '112.0.0.0/5', '120.0.0.0/6', '124.0.0.0/7', '126.0.0.0/8']))
        with self.assertRaises(CLIError) as context:
            # Should never be 127.0.0.0/8
            _set_default_cidr_range(
                ['128.0.0.0/1', '0.0.0.0/2', '64.0.0.0/3', '96.0.0.0/4', '112.0.0.0/5', '120.0.0.0/6', '124.0.0.0/7',
                 '126.0.0.0/8'])
        self.assertEqual(
            'Cannot set "reserved-cidr-range" automatically.Please specify "--reserved-cidr-range" with 3 unused CIDR ranges in your network environment.',
            str(context.exception))

    @mock.patch('azext_spring._validators._get_vnet', _mock_get_vnet)
    @mock.patch('azext_spring._validators._get_authorization_client', _mock_get_authorization_client)
    @mock.patch('azext_spring._validators._get_graph_rbac_management_client',
                _mock_get_graph_rbac_management_client)
    def test_vnet_location(self):
        ns = Namespace(reserved_cidr_range='10.0.0.0/8,20.0.0.0/16,30.0.0.1/16', resource_group='test', vnet=None,
                       sku=None, location='westus',
                       app_subnet='/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/app',
                       service_runtime_subnet='/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/svc')
        with self.assertRaises(CLIError) as context:
            validate_vnet(get_test_cmd(), ns)
        self.assertTrue(
            '--vnet and Azure Spring Apps instance should be in the same location.' in str(context.exception))


def _mock_term_client(accepted, registered):
    def _mock_get(offer_type, publisher_id, offer_id, plan_id):
        term = mock.MagicMock()
        term.accepted = accepted
        return term

    def _mock_provider_get(namespace):
        provider = mock.MagicMock()
        provider.registration_state = 'Registered' if registered else 'NotRegistered'
        return provider

    client = mock.MagicMock()
    client.marketplace_agreements = mock.MagicMock()
    client.marketplace_agreements.get = _mock_get
    client.providers = mock.MagicMock()
    client.providers.get = _mock_provider_get
    return client


def _mock_happy_client(cli_ctx, client_type, **kwargs):
    return _mock_term_client(True, True)


def _mock_not_accepted_term_client(cli_ctx, client_type, **kwargs):
    return _mock_term_client(False, True)


def _mock_not_registered_client(cli_ctx, client_type, **kwargs):
    return _mock_term_client(True, False)


class TestSkuValidator(unittest.TestCase):
    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client', _mock_happy_client)
    def test_happy_path(self):
        ns = Namespace(sku='Enterprise', marketplace_plan_id=None)
        validate_sku(get_test_cmd(), ns)
        self.assertEqual('Enterprise', ns.sku.tier)

    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client', _mock_not_accepted_term_client)
    def test_term_not_accept(self):
        ns = Namespace(sku='Enterprise', marketplace_plan_id=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_sku(get_test_cmd(), ns)
        self.assertTrue('Terms for Azure Spring Apps Enterprise is not accepted.' in str(context.exception))

    @mock.patch('azure.cli.core.commands.client_factory.get_mgmt_service_client', _mock_not_registered_client)
    def test_provider_not_registered(self):
        ns = Namespace(sku='Enterprise', marketplace_plan_id=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_sku(get_test_cmd(), ns)
        self.assertTrue('Microsoft.SaaS resource provider is not registered.' in str(context.exception))
