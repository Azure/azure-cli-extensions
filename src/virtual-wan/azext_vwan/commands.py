# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from .profiles import CUSTOM_VWAN

from ._client_factory import (
    cf_virtual_wans, cf_virtual_hubs, cf_vpn_sites, cf_vpn_site_configs,
    cf_vpn_gateways, cf_vpn_gateway_connection, cf_virtual_hub_route_table_v2s, cf_vpn_server_config,
    cf_p2s_vpn_gateways, cf_virtual_hub_bgpconnection)
from ._util import (
    list_network_resource_property,
    get_network_resource_property_entry
)
from ._format import transform_effective_route_table

ROUTE_TABLE_DEPRECATION_INFO = 'network vhub route-table'


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_vhub_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VirtualHubsOperations.{}',
        client_factory=cf_virtual_hubs,
        resource_type=CUSTOM_VWAN,
        min_api='2018-08-01'
    )

    network_vhub_bgpconnection_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VirtualHubBgpConnectionOperations.{}',
        client_factory=cf_virtual_hub_bgpconnection,
        resource_type=CUSTOM_VWAN
    )

    network_vhub_route_table_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VirtualHubRouteTableV2SOperations.{}',
        client_factory=cf_virtual_hub_route_table_v2s,
        resource_type=CUSTOM_VWAN,
        min_api='2019-09-01'
    )

    network_vwan_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VirtualWansOperations.{}',
        client_factory=cf_virtual_wans,
        resource_type=CUSTOM_VWAN,
        min_api='2018-08-01'
    )

    network_vpn_gateway_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VpnGatewaysOperations.{}',
        client_factory=cf_vpn_gateways,
        min_api='2018-08-01'
    )

    network_vpn_gateway_connection_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VpnConnectionsOperations.{}',
        client_factory=cf_vpn_gateway_connection,
        min_api='2020-05-01'
    )

    network_vpn_site_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VpnSitesOperations.{}',
        client_factory=cf_vpn_sites,
        min_api='2018-08-01'
    )

    network_vpn_site_config_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VpnSitesConfigurationOperations.{}',
        client_factory=cf_vpn_site_configs,
        min_api='2018-08-01'
    )

    network_vpn_server_config_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#VpnServerConfigurationsOperations.{}',
        client_factory=cf_vpn_server_config,
        resource_type=CUSTOM_VWAN,
        min_api='2020-03-01'
    )

    network_p2s_vpn_gateway_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.v2022_07_01.operations#P2SVpnGatewaysOperations.{}',
        client_factory=cf_p2s_vpn_gateways,
        resource_type=CUSTOM_VWAN,
        min_api='2020-03-01'
    )

    network_util = CliCommandType(
        operations_tmpl='azext_vwan._util#{}',
        client_factory=None
    )

    # region VirtualWANs
    with self.command_group('network vwan', network_vwan_sdk) as g:
        g.custom_command('create', 'create_virtual_wan')
        g.command('delete', 'begin_delete')
        g.show_command('show')
        g.custom_command('list', 'list_virtual_wans')
        g.generic_update_command('update', custom_func_name='update_virtual_wan', setter_name="begin_create_or_update", setter_arg_name='wan_parameters')
    # endregion

    # region VirtualHubs
    with self.command_group('network vhub', network_vhub_sdk, client_factory=cf_virtual_hubs) as g:
        g.custom_command('get-effective-routes', 'get_effective_virtual_hub_routes', supports_no_wait=True, table_transformer=transform_effective_route_table)

    with self.command_group("network vhub connection"):
        from .custom import VHubConnectionCreate, VHubConnectionUpdate
        self.command_table["network vhub connection create"] = VHubConnectionCreate(loader=self)
        self.command_table["network vhub connection update"] = VHubConnectionUpdate(loader=self)

    with self.command_group('network vhub bgpconnection', network_vhub_bgpconnection_sdk, client_factory=cf_virtual_hub_bgpconnection) as g:
        g.custom_command('create', 'create_hub_vnet_bgpconnection', supports_no_wait=True)
        g.command('delete', 'begin_delete', supports_no_wait=True, confirmation=True)
        g.show_command('show')
        g.custom_command('list', 'list_hub_vnet_bgpconnection')
        g.generic_update_command('update', custom_func_name='update_hub_vnet_bgpconnection', setter_name="begin_create_or_update", supports_no_wait=True)
        g.wait_command('wait')

    with self.command_group('network vhub route', network_vhub_sdk, deprecate_info=self.deprecate(redirect=ROUTE_TABLE_DEPRECATION_INFO, hide=False)) as g:
        g.custom_command('add', 'add_hub_route', supports_no_wait=True)
        g.custom_command('list', 'list_hub_routes')
        g.custom_command('remove', 'remove_hub_route', supports_no_wait=True)
        g.custom_command('reset', 'reset_hub_routes',
                         supports_no_wait=True)

    with self.command_group('network vhub route-table', network_vhub_route_table_sdk) as g:
        g.custom_command('create', 'create_vhub_route_table', supports_no_wait=True)
        g.custom_command('update', 'update_vhub_route_table', supports_no_wait=True)
        g.custom_show_command('show', 'get_vhub_route_table')
        g.custom_command('list', 'list_vhub_route_tables')
        g.custom_command('delete', 'delete_vhub_route_table')
        g.wait_command('wait')

    with self.command_group('network vhub route-table route', network_vhub_route_table_sdk) as g:
        g.custom_command('add', 'add_hub_routetable_route', supports_no_wait=True)
        g.custom_command('list', 'list_hub_routetable_route')
        g.custom_command('remove', 'remove_hub_routetable_route', supports_no_wait=True)
    # endregion

    # region VpnGateways
    with self.command_group("network vpn-gateway nat-rule"):
        from .custom import VPNGatewayNatRuleCreate, VPNGatewayNatRuleUpdate, VPNGatewayNatRuleList, \
            VPNGatewayNatRuleShow
        self.command_table["network vpn-gateway nat-rule create"] = VPNGatewayNatRuleCreate(loader=self)
        self.command_table["network vpn-gateway nat-rule update"] = VPNGatewayNatRuleUpdate(loader=self)
        self.command_table["network vpn-gateway nat-rule list"] = VPNGatewayNatRuleList(loader=self)
        self.command_table["network vpn-gateway nat-rule show"] = VPNGatewayNatRuleShow(loader=self)

    with self.command_group('network vpn-gateway connection', network_vpn_gateway_connection_sdk) as g:
        g.custom_command('create', 'create_vpn_gateway_connection', supports_no_wait=True)
        g.command('list', 'list_by_vpn_gateway')
        g.show_command('show', 'get')
        g.command('delete', 'begin_delete')
        g.generic_update_command('update', custom_func_name='update_vpn_gateway_connection', setter_name="begin_create_or_update",
                                 setter_arg_name='vpn_connection_parameters', supports_no_wait=True)
        g.wait_command('wait')

    with self.command_group('network vpn-gateway connection ipsec-policy', network_vpn_gateway_sdk) as g:
        g.custom_command('add', 'add_vpn_gateway_connection_ipsec_policy', supports_no_wait=True)
        g.custom_command('list', 'list_vpn_conn_ipsec_policies')
        g.custom_command('remove', 'remove_vpn_conn_ipsec_policy', supports_no_wait=True)

    with self.command_group('network vpn-gateway connection vpn-site-link-conn', network_vpn_gateway_connection_sdk) as g:
        g.custom_command('add', 'add_vpn_gateway_connection_vpn_site_link_conn', supports_no_wait=True)
        g.custom_command('remove', 'remove_vpn_gateway_connection_vpn_site_link_conn', supports_no_wait=True)
        g.custom_command('list', 'list_vpn_conn_vpn_site_link_conn')

    with self.command_group('network vpn-gateway connection vpn-site-link-conn ipsec-policy', network_vpn_gateway_connection_sdk) as g:
        g.custom_command('add', 'add_vpn_gateway_connection_link_ipsec_policy', supports_no_wait=True)
        g.custom_command('list', 'list_vpn_conn_link_ipsec_policies')
        g.custom_command('remove', 'remove_vpn_conn_link_ipsec_policy', supports_no_wait=True)
    # endregion

    # region VpnSites
    with self.command_group('network vpn-site', network_vpn_site_sdk) as g:
        g.custom_command('create', 'create_vpn_site', supports_no_wait=True)
        g.command('delete', 'begin_delete')
        g.custom_command('list', 'list_vpn_sites')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_vpn_site', setter_name='begin_create_or_update', setter_arg_name='vpn_site_parameters', supports_no_wait=True)

    with self.command_group('network vpn-site link', network_vpn_site_sdk) as g:
        g.custom_command('add', 'add_vpn_site_link', supports_no_wait=True)
        g.custom_command('remove', 'remove_vpn_site_link', supports_no_wait=True)
        g.custom_command('list', 'list_vpn_site_link')

    with self.command_group('network vpn-site', network_vpn_site_config_sdk) as g:
        g.command('download', 'begin_download')
    # endregion

    # region VpnServer
    with self.command_group('network vpn-server-config', network_vpn_server_config_sdk) as g:
        g.custom_command('create', 'create_vpn_server_config', supports_no_wait=True)
        g.custom_command('set', 'create_vpn_server_config', supports_no_wait=True)
        # due to service limitation, we cannot support update command right now.
        # g.generic_update_command('update', custom_func_name='update_vpn_server_config', supports_no_wait=True, setter_arg_name='vpn_server_configuration_parameters')
        g.show_command('show')
        g.command('delete', 'begin_delete', confirmation=True)
        g.custom_command('list', 'list_vpn_server_config')
        g.wait_command('wait')

    with self.command_group('network vpn-server-config ipsec-policy', network_vpn_server_config_sdk) as g:
        g.custom_command('add', 'add_vpn_server_config_ipsec_policy', supports_no_wait=True)
        g.custom_command('list', 'list_vpn_server_config_ipsec_policies')
        g.custom_command('remove', 'remove_vpn_server_config_ipsec_policy', supports_no_wait=True)
        g.wait_command('wait')

    with self.command_group('network p2s-vpn-gateway', network_p2s_vpn_gateway_sdk) as g:
        g.custom_command('create', 'create_p2s_vpn_gateway', supports_no_wait=True)
        g.command('delete', 'begin_delete', confirmation=True)
        g.custom_command('list', 'list_p2s_vpn_gateways')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_p2s_vpn_gateway', supports_no_wait=True, setter_name="begin_create_or_update", setter_arg_name='p2_s_vpn_gateway_parameters')
        g.wait_command('wait')

    resource = 'p2_svpn_gateways'
    prop = 'p2_s_connection_configurations'
    with self.command_group('network p2s-vpn-gateway connection', network_util, min_api='2020-04-01', is_preview=True) as g:
        g.command('list', list_network_resource_property(resource, prop))
        g.show_command('show', get_network_resource_property_entry(resource, prop))

    with self.command_group('network p2s-vpn-gateway vpn-client', network_p2s_vpn_gateway_sdk, min_api='2020-05-01') as g:
        g.custom_command('generate', 'generate_vpn_profile')
    # endregion
