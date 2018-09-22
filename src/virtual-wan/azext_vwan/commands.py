# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from ._client_factory import (
    cf_virtual_wans, cf_virtual_hubs, cf_vpn_sites, cf_vpn_site_configs, cf_vpn_gateways)
from ._util import (
    list_network_resource_property, delete_network_resource_property_entry, get_network_resource_property_entry)


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_vhub_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.operations.virtual_hubs_operations#VirtualHubsOperations.{}',
        client_factory=cf_virtual_hubs,
        min_api='2018-08-01'
    )

    network_vwan_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.operations.virtual_wans_operations#VirtualWansOperations.{}',
        client_factory=cf_virtual_wans,
        min_api='2018-08-01'
    )

    network_vpn_gateway_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.operations.vpn_gateways_operations#VpnGatewaysOperations.{}',
        client_factory=cf_vpn_gateways,
        min_api='2018-08-01'
    )

    network_vpn_site_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.operations.vpn_sites_operations#VpnSitesOperations.{}',
        client_factory=cf_vpn_sites,
        min_api='2018-08-01'
    )

    network_vpn_site_config_sdk = CliCommandType(
        operations_tmpl='azext_vwan.vendored_sdks.operations.vpn_sites_configuration_operations#VpnSitesConfigurationOperations.{}',
        client_factory=cf_vpn_site_configs,
        min_api='2018-08-01'
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
