# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from .profiles import CUSTOM_VHUB_ROUTE_TABLE

from ._client_factory import (
    cf_virtual_wans, cf_virtual_hubs, cf_vpn_sites, cf_vpn_site_configs,
    cf_vpn_gateways, cf_virtual_hub_route_table_v2s, cf_vpn_server_config,
    cf_p2s_vpn_gateways)
from ._util import (
    list_network_resource_property, delete_network_resource_property_entry, get_network_resource_property_entry)


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_vhub_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2020_04_01.operations#VirtualHubsOperations.{}',
        client_factory=cf_virtual_hubs,
        resource_type=CUSTOM_VHUB_ROUTE_TABLE,
        min_api='2018-08-01'
    )

    network_vhub_route_table_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2020_04_01.operations#VirtualHubRouteTableV2sOperations.{}',
        client_factory=cf_virtual_hub_route_table_v2s,
        resource_type=CUSTOM_VHUB_ROUTE_TABLE,
        min_api='2019-09-01'
    )

    network_vwan_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2020_04_01.operations#VirtualWansOperations.{}',
        client_factory=cf_virtual_wans,
        resource_type=CUSTOM_VHUB_ROUTE_TABLE,
        min_api='2018-08-01'
    )

    network_vpn_gateway_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2018_08_01.operations#VpnGatewaysOperations.{}',
        client_factory=cf_vpn_gateways,
        min_api='2018-08-01'
    )

    network_vpn_site_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2018_08_01.operations#VpnSitesOperations.{}',
        client_factory=cf_vpn_sites,
        min_api='2018-08-01'
    )

    network_vpn_site_config_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2018_08_01.operations#VpnSitesConfigurationOperations.{}',
        client_factory=cf_vpn_site_configs,
        min_api='2018-08-01'
    )

    network_vpn_server_config_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2020_04_01.operations#VpnServerConfigurationsOperations.{}',
        client_factory=cf_vpn_server_config,
        resource_type=CUSTOM_VHUB_ROUTE_TABLE,
        min_api='2020-03-01'
    )

    network_p2s_vpn_gateway_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2020_04_01.operations#P2sVpnGatewaysOperations.{}',
        client_factory=cf_p2s_vpn_gateways,
        resource_type=CUSTOM_VHUB_ROUTE_TABLE,
        min_api='2020-03-01'
    )

    network_util = CliCommandType(
        operations_tmpl='azext_vwan._util#{}',
        client_factory=None
    )

    # region VirtualWANs
    with self.command_group('network vwan', network_vwan_sdk) as g:
        g.custom_command('create', 'create_virtual_wan')
        g.command('delete', 'delete')
        g.show_command('show')
        g.custom_command('list', 'list_virtual_wans')
        g.generic_update_command('update', custom_func_name='update_virtual_wan', setter_arg_name='wan_parameters')
    # endregion

    # region VirtualHubs
    with self.command_group('network vhub', network_vhub_sdk) as g:
        g.custom_command('create', 'create_virtual_hub', supports_no_wait=True)
        g.command('delete', 'delete')
        g.show_command('show')
        g.custom_command('list', 'list_virtual_hubs')
        g.generic_update_command('update', custom_func_name='update_virtual_hub', setter_arg_name='virtual_hub_parameters', supports_no_wait=True)

    with self.command_group('network vhub connection', network_vhub_sdk) as g:
        g.custom_command('create', 'create_hub_vnet_connection', supports_no_wait=True)

    resource = 'virtual_hubs'
    prop = 'virtual_network_connections'
    with self.command_group('network vhub connection', network_util) as g:
        g.command('delete', delete_network_resource_property_entry(resource, prop))
        g.command('list', list_network_resource_property(resource, prop))
        g.show_command('show', get_network_resource_property_entry(resource, prop))

    with self.command_group('network vhub route', network_vhub_sdk) as g:
        g.custom_command('add', 'add_hub_route', supports_no_wait=True)
        g.custom_command('list', 'list_hub_routes')
        g.custom_command('remove', 'remove_hub_route', supports_no_wait=True)

    with self.command_group('network vhub route-table', network_vhub_route_table_sdk, resource_type=CUSTOM_VHUB_ROUTE_TABLE) as g:
        g.custom_command('create', 'create_vhub_route_table', supports_no_wait=True)
        g.custom_command('update', 'update_vhub_route_table', supports_no_wait=True)
        g.custom_show_command('show', 'get_vhub_route_table')
        g.custom_command('list', 'list_vhub_route_tables')
        g.custom_command('delete', 'delete_vhub_route_table')
        g.wait_command('wait')

    with self.command_group('network vhub route-table route', network_vhub_route_table_sdk, resource_type=CUSTOM_VHUB_ROUTE_TABLE) as g:
        g.custom_command('add', 'add_hub_routetable_route', supports_no_wait=True)
        g.custom_command('list', 'list_hub_routetable_route')
        g.custom_command('remove', 'remove_hub_routetable_route', supports_no_wait=True)
    # endregion

    # region VpnGateways
    with self.command_group('network vpn-gateway', network_vpn_gateway_sdk) as g:
        g.custom_command('create', 'create_vpn_gateway', supports_no_wait=True)
        g.command('delete', 'delete')
        g.custom_command('list', 'list_vpn_gateways')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_vpn_gateway', supports_no_wait=True, setter_arg_name='vpn_gateway_parameters')

    with self.command_group('network vpn-gateway connection', network_vpn_gateway_sdk) as g:
        g.custom_command('create', 'create_vpn_gateway_connection', supports_no_wait=True)

    resource = 'vpn_gateways'
    prop = 'connections'
    with self.command_group('network vpn-gateway connection', network_util) as g:
        g.command('delete', delete_network_resource_property_entry(resource, prop))
        g.command('list', list_network_resource_property(resource, prop))
        g.show_command('show', get_network_resource_property_entry(resource, prop))

    with self.command_group('network vpn-gateway connection ipsec-policy', network_vpn_gateway_sdk) as g:
        g.custom_command('add', 'add_vpn_gateway_connection_ipsec_policy', supports_no_wait=True)
        g.custom_command('list', 'list_vpn_conn_ipsec_policies')
        g.custom_command('remove', 'remove_vpn_conn_ipsec_policy', supports_no_wait=True)
    # endregion

    # region VpnSites
    with self.command_group('network vpn-site', network_vpn_site_sdk) as g:
        g.custom_command('create', 'create_vpn_site', supports_no_wait=True)
        g.command('delete', 'delete')
        g.custom_command('list', 'list_vpn_sites')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_vpn_site', setter_arg_name='vpn_site_parameters', supports_no_wait=True)

    with self.command_group('network vpn-site', network_vpn_site_config_sdk) as g:
        g.command('download', 'download')
    # endregion

    # region VpnServer
    with self.command_group('network vpn-server-config', network_vpn_server_config_sdk, resource_type=CUSTOM_VHUB_ROUTE_TABLE) as g:
        g.custom_command('create', 'create_vpn_server_config', supports_no_wait=True)
        g.custom_command('set', 'create_vpn_server_config', supports_no_wait=True)
        # due to service limitation, we cannot support update command right now.
        # g.generic_update_command('update', custom_func_name='update_vpn_server_config', supports_no_wait=True, setter_arg_name='vpn_server_configuration_parameters')
        g.show_command('show')
        g.command('delete', 'delete', confirmation=True)
        g.custom_command('list', 'list_vpn_server_config')
        g.wait_command('wait')

    with self.command_group('network vpn-server-config ipsec-policy', network_vpn_server_config_sdk, resource_type=CUSTOM_VHUB_ROUTE_TABLE) as g:
        g.custom_command('add', 'add_vpn_server_config_ipsec_policy', supports_no_wait=True)
        g.custom_command('list', 'list_vpn_server_config_ipsec_policies')
        g.custom_command('remove', 'remove_vpn_server_config_ipsec_policy', supports_no_wait=True)
        g.wait_command('wait')

    with self.command_group('network p2s-vpn-gateway', network_p2s_vpn_gateway_sdk, resource_type=CUSTOM_VHUB_ROUTE_TABLE) as g:
        g.custom_command('create', 'create_p2s_vpn_gateway', supports_no_wait=True)
        g.command('delete', 'delete', confirmation=True)
        g.custom_command('list', 'list_p2s_vpn_gateways')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_p2s_vpn_gateway', supports_no_wait=True, setter_arg_name='p2_svpn_gateway_parameters')
        g.wait_command('wait')
    # endregion
