# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list, tags_type, get_location_type, get_three_state_flag, get_enum_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._validators import get_network_resource_name_or_id


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    (IpsecEncryption, IpsecIntegrity, IkeEncryption, IkeIntegrity, DhGroup, PfsGroup,
     VirtualNetworkGatewayConnectionProtocol) = self.get_models(
         'IpsecEncryption', 'IpsecIntegrity', 'IkeEncryption', 'IkeIntegrity', 'DhGroup', 'PfsGroup',
         'VirtualNetworkGatewayConnectionProtocol')

    # region VirtualWAN
    vwan_name_type = CLIArgumentType(options_list='--vwan-name', metavar='NAME', help='Name of the virtual WAN.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/virtualWANs'))
    vhub_name_type = CLIArgumentType(options_list='--vhub-name', metavar='NAME', help='Name of the virtual hub.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/networkHubs'))
    vpn_gateway_name_type = CLIArgumentType(options_list='--gateway-name', metavar='NAME', help='Name of the VPN gateway.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/vpnGateways'))
    vpn_site_name_type = CLIArgumentType(options_list='--site-name', metavar='NAME', help='Name of the VPN site config.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/vpnSites'))

    with self.argument_context('network') as c:
        c.argument('tags', tags_type)

    with self.argument_context('network vwan') as c:
        c.argument('virtual_wan_name', vwan_name_type, options_list=['--name', '-n'])
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('branch_to_branch_traffic', arg_type=get_three_state_flag(), help='Allow branch-to-branch traffic flow.')
        c.argument('vnet_to_vnet_traffic', arg_type=get_three_state_flag(), help='Allow VNet-to-VNet traffic flow.')
        c.argument('security_provider_name', help='The security provider name.')
        c.argument('office365_category', help='The office local breakout category.')
        c.argument('disable_vpn_encryption', arg_type=get_three_state_flag(), help='State of VPN encryption.')
    # endregion

    # region VirtualHub
    with self.argument_context('network vhub') as c:
        c.argument('virtual_hub_name', vhub_name_type, options_list=['--name', '-n'])
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('virtual_wan', options_list='--vwan', help='Name or ID of the virtual WAN.', validator=get_network_resource_name_or_id('virtual_wan', 'virtualWans'))
        c.argument('address_prefix', help='CIDR address prefix for the virtual hub.')

    with self.argument_context('network vhub', arg_group='Gateway') as c:
        c.argument('express_route_gateway', help='Name or ID of an ExpressRoute gateway.', validator=get_network_resource_name_or_id('express_route_gateway', 'expressRouteGateways'))
        c.argument('p2s_vpn_gateway', help='Name or ID of a P2S VPN gateway.', validator=get_network_resource_name_or_id('p2s_vpn_gateway', 'P2sVpnGateways'))
        c.argument('vpn_gateway', help='Name or ID of a VPN gateway.', validator=get_network_resource_name_or_id('vpn_gateway', 'vpnGateways'))

    with self.argument_context('network vhub connection') as c:
        for dest in ['virtual_hub_name', 'resource_name']:
            c.argument(dest, vhub_name_type)
        for dest in ['item_name', 'connection_name']:
            c.argument(dest, help='Name of the connection.', options_list=['--name', '-n'], id_part='child_name_1')
        c.argument('remote_virtual_network', options_list='--remote-vnet', help='Name of ID of the remote VNet to connect to.', validator=get_network_resource_name_or_id('remote_virtual_network', 'virtualNetworks'))
        c.argument('allow_hub_to_remote_vnet_transit', arg_type=get_three_state_flag(), options_list='--remote-vnet-transit', help='Enable hub to remote VNet transit.')
        c.argument('allow_remote_vnet_to_use_hub_vnet_gateways', arg_type=get_three_state_flag(), options_list='--use-hub-vnet-gateways', help='Allow remote VNet to use hub\'s VNet gateways.')
        c.argument('enable_internet_security', arg_type=get_three_state_flag(), options_list='--internet-security', help='Enable internet security.')

    with self.argument_context('network vhub connection list') as c:
        c.argument('resource_name', vhub_name_type, id_part=None)

    with self.argument_context('network vhub route') as c:
        c.argument('virtual_hub_name', vhub_name_type, id_part=None)
        c.argument('address_prefixes', nargs='+', help='Space-separated list of CIDR prefixes.')
        c.argument('next_hop_ip_address', options_list='--next-hop', help='IP address of the next hop.')
        c.argument('index', type=int, help='List index of the item (starting with 1).')

    with self.argument_context('network vhub route-table') as c:
        c.argument('virtual_hub_name', vhub_name_type, id_part=None)
        c.argument('route_table_name', options_list=['--name', '-n'], help='Name of the virtual hub route table.')
        c.argument('attached_connections', options_list='--connections', nargs='+', arg_type=get_enum_type(['All_Vnets', 'All_Branches']), help='List of all connections attached to this route table')
        c.argument('destination_type', arg_type=get_enum_type(['Service', 'CIDR']), help='The type of destinations')
        c.argument('destinations', nargs='+', help='Space-separated list of all destinations.')
        c.argument('next_hop_type', arg_type=get_enum_type(['IPAddress']), help='The type of next hops. Currently it only supports IP Address.')
        c.argument('next_hops', nargs='+', help='Space-separated list of IP address of the next hop.')
        c.argument('index', type=int, help='List index of the item (starting with 1).')
    # endregion

    # region VpnGateways
    with self.argument_context('network vpn-gateway') as c:
        c.argument('virtual_hub', options_list='--vhub', help='Name or ID of a virtual hub.', validator=get_network_resource_name_or_id('virtual_hub', 'virtualHubs'))
        c.argument('scale_unit', type=int, help='The scale unit for this VPN gateway.')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('gateway_name', vpn_gateway_name_type, options_list=['--name', '-n'])

    with self.argument_context('network vpn-gateway connection') as c:
        for dest in ['gateway_name', 'resource_name']:
            c.argument(dest, vpn_gateway_name_type)
        for dest in ['item_name', 'connection_name']:
            c.argument(dest, help='Name of the VPN gateway connection.', options_list=['--name', '-n'], id_part='child_name_1')
        c.argument('remote_vpn_site', help='Name of ID of the remote VPN site.', validator=get_network_resource_name_or_id('remote_vpn_site', 'vpnSites'))
        c.argument('connection_bandwidth', help='Expected bandwidth in Mbps.', type=int)
        c.argument('enable_bgp', arg_type=get_three_state_flag(), help='Enable BGP.')
        c.argument('enable_internet_security', options_list='--internet-security', arg_type=get_three_state_flag(), help='Enable internet security.')
        c.argument('enable_rate_limiting', options_list='--rate-limiting', arg_type=get_three_state_flag(), help='Enable rate limiting.')
        c.argument('protocol_type', arg_type=get_enum_type(VirtualNetworkGatewayConnectionProtocol), help='Connection protocol.')
        c.argument('routing_weight', type=int, help='Routing weight.')
        c.argument('shared_key', help='Shared key.')

    with self.argument_context('network vpn-gateway connection list') as c:
        c.argument('resource_name', vpn_gateway_name_type, id_part=None)

    with self.argument_context('network vpn-gateway connection', arg_group='IP Security') as c:
        c.argument('sa_life_time_seconds', options_list='--sa-lifetime', help='IPSec Security Association (also called Quick Mode or Phase 2 SA) lifetime in seconds for a site-to-site VPN tunnel.', type=int)
        c.argument('sa_data_size_kilobytes', options_list='--sa-data-size', help='IPSec Security Association (also called Quick Mode or Phase 2 SA) payload size in KB for a site-to-site VPN tunnel.', type=int)
        c.argument('ipsec_encryption', arg_type=get_enum_type(IpsecEncryption), help='IPSec encryption algorithm (IKE phase 1).')
        c.argument('ipsec_integrity', arg_type=get_enum_type(IpsecIntegrity), help='IPSec integrity algorithm (IKE phase 1).')
        c.argument('ike_encryption', arg_type=get_enum_type(IkeEncryption), help='IKE encryption algorithm (IKE phase 2).')
        c.argument('ike_integrity', arg_type=get_enum_type(IkeIntegrity), help='IKE integrity algorithm (IKE phase 2).')
        c.argument('dh_group', arg_type=get_enum_type(DhGroup), help='DH Groups used in IKE Phase 1 for initial SA.')
        c.argument('pfs_group', arg_type=get_enum_type(PfsGroup), help='The Pfs Groups used in IKE Phase 2 for new child SA.')

    with self.argument_context('network vpn-gateway connection ipsec-policy') as c:
        c.argument('gateway_name', vpn_gateway_name_type, id_part=None)
        c.argument('connection_name', options_list='--connection-name', help='Name of the VPN gateway connection.')
        c.argument('index', type=int, help='List index of the item (starting with 1).')
    # endregion

    # region VpnSites
    with self.argument_context('network vpn-site') as c:
        c.argument('vpn_site_name', vpn_site_name_type, options_list=['--name', '-n'])
        c.argument('virtual_wan', help='Name or ID of the virtual WAN.', validator=get_network_resource_name_or_id('virtual_wan', 'virtualWans'))
        c.argument('is_security_site', arg_type=get_three_state_flag(), options_list='--security-site', help='Whether the VPN site is security-related.')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('ip_address', help='IP address of the VPN site.')
        c.argument('site_key', help='Key for the VPN site that can be used for connections.')
        c.argument('address_prefixes', nargs='+', help='Space-separated list of CIDR address prefixes.')

    with self.argument_context('network vpn-site', arg_group='Device Property') as c:
        c.argument('device_model', help='Model of the device.')
        c.argument('device_vendor', help='Name of the device vendor.')
        c.argument('link_speed', help='Link speed in Mbps.', type=int)

    for scope in ['vpn-site', 'vpn-gateway']:
        with self.argument_context('network {}'.format(scope), arg_group='BGP Peering') as c:
            c.argument('asn', help='BGP speaker\'s ASN.', type=int)
            c.argument('peer_weight', help='Weight added to routes learned from this BGP speaker.', type=int)
            c.argument('bgp_peering_address', help='Peering address and BGP identifier of this BGP speaker.')

    with self.argument_context('network vpn-site download') as c:
        c.argument('virtual_wan_name', vwan_name_type, id_part=None)
        c.argument('vpn_sites', help='Space-separated list of VPN site names or IDs.', nargs='+', validator=get_network_resource_name_or_id('vpn_sites', 'vpnSites'))
    # endregion
