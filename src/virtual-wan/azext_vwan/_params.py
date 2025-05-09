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
from .action import RadiusServerAddAction


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    (IpsecEncryption, IpsecIntegrity, IkeEncryption, IkeIntegrity, DhGroup, PfsGroup,
     VirtualNetworkGatewayConnectionProtocol, AuthenticationMethod) = self.get_models(
         'IpsecEncryption', 'IpsecIntegrity', 'IkeEncryption', 'IkeIntegrity', 'DhGroup', 'PfsGroup',
         'VirtualNetworkGatewayConnectionProtocol', 'AuthenticationMethod')

    (VpnGatewayTunnelingProtocol, VpnAuthenticationType) = self.get_models('VpnGatewayTunnelingProtocol', 'VpnAuthenticationType')

    # region VirtualWAN
    vwan_name_type = CLIArgumentType(options_list='--vwan-name', metavar='NAME', help='Name of the virtual WAN.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/virtualWANs'))
    vhub_name_type = CLIArgumentType(options_list='--vhub-name', metavar='NAME', help='Name of the virtual hub.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/networkHubs'))
    vpn_gateway_name_type = CLIArgumentType(options_list='--gateway-name', metavar='NAME', help='Name of the VPN gateway.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/vpnGateways'))
    vpn_site_name_type = CLIArgumentType(options_list='--site-name', metavar='NAME', help='Name of the VPN site config.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/vpnSites'))
    p2s_vpn_gateway_name_type = CLIArgumentType(options_list='--gateway-name', metavar='NAME', help='Name of the P2S VPN gateway.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/p2svpnGateways'))
    associated_route_table_type = CLIArgumentType(options_list=['--associated', '--associated-route-table'], help='The resource id of route table associated with this routing configuration.')
    propagated_route_tables_type = CLIArgumentType(options_list=['--propagated', '--propagated-route-tables'], nargs='+', help='Space-separated list of resource id of propagated route tables.')
    propagated_route_tables_label_type = CLIArgumentType(nargs='+', help='Space-separated list of labels for propagated route tables.')

    with self.argument_context('network') as c:
        c.argument('tags', tags_type)

    with self.argument_context('network vwan') as c:
        c.argument('virtual_wan_name', vwan_name_type, options_list=['--name', '-n'])
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('branch_to_branch_traffic', arg_type=get_three_state_flag(), help='Allow branch-to-branch traffic flow.')
        c.argument('security_provider_name', help='The security provider name.')
        c.argument('office365_category', help='The office local breakout category.')
        c.argument('disable_vpn_encryption', arg_type=get_three_state_flag(), help='State of VPN encryption.')
        c.argument('vwan_type', options_list='--type', arg_type=get_enum_type(['Basic', 'Standard']), help='The type of the VirtualWAN.')
    # endregion

    # region VirtualHub
    with self.argument_context('network vhub', arg_group='Gateway') as c:
        c.argument('express_route_gateway', help='Name or ID of an ExpressRoute gateway.', validator=get_network_resource_name_or_id('express_route_gateway', 'expressRouteGateways'))
        c.argument('p2s_vpn_gateway', help='Name or ID of a P2S VPN gateway.', validator=get_network_resource_name_or_id('p2s_vpn_gateway', 'P2sVpnGateways'))
        c.argument('vpn_gateway', help='Name or ID of a VPN gateway.', validator=get_network_resource_name_or_id('vpn_gateway', 'vpnGateways'))

    with self.argument_context('network vhub get-effective-routes') as c:
        c.argument('virtual_hub_name', vhub_name_type, options_list=['--name', '-n'])
        c.argument('virtual_wan_resource_type', options_list='--resource-type', help='The type of the specified resource like RouteTable, ExpressRouteConnection, HubVirtualNetworkConnection, VpnConnection and P2SConnection.')
        c.argument('resource_id', options_list='--resource-id', help='The resource whose effective routes are being requested')

    with self.argument_context('network vhub connection') as c:
        c.argument('virtual_hub_name', vhub_name_type)
        c.argument('connection_name', help='Name of the connection.', options_list=['--name', '-n'], id_part='child_name_1')
        c.argument('remote_virtual_network', options_list='--remote-vnet', help='Name of ID of the remote VNet to connect to.', validator=get_network_resource_name_or_id('remote_virtual_network', 'virtualNetworks'))
        c.argument('allow_hub_to_remote_vnet_transit', arg_type=get_three_state_flag(), options_list='--remote-vnet-transit', deprecate_info=c.deprecate(target='--remote-vnet-transit'), help='Enable hub to remote VNet transit.')
        c.argument('allow_remote_vnet_to_use_hub_vnet_gateways', arg_type=get_three_state_flag(), options_list='--use-hub-vnet-gateways', deprecate_info=c.deprecate(target='--use-hub-vnet-gateways'), help='Allow remote VNet to use hub\'s VNet gateways.')
        c.argument('enable_internet_security', arg_type=get_three_state_flag(), options_list='--internet-security', help='Enable internet security and default is enabled.', default=True)

    with self.argument_context('network vhub connection list') as c:
        c.argument('virtual_hub_name', vhub_name_type, id_part=None)

    with self.argument_context('network vhub connection', arg_group='RoutingConfiguration', min_api='2020-04-01', is_preview=True) as c:
        c.argument('address_prefixes', nargs='+', help='Space-separated list of all address prefixes.')
        c.argument('next_hop_ip_address', options_list='--next-hop', help='The ip address of the next hop.')
        c.argument('route_name', help='The name of the Static Route that is unique within a Vnet Route.')

    with self.argument_context('network vhub bgpconnection') as c:
        c.argument('virtual_hub_name', vhub_name_type)
        c.argument('connection_name', help='Name of the bgpconnection.', options_list=['--name', '-n'], id_part='child_name_1')
        c.argument('peer_asn', help='Peer ASN', type=int)
        c.argument('peer_ip', help='Peer IP')
        c.argument('virtual_hub_connection', options_list='--vhub-conn', help='The resource id of vhub connection.')

    with self.argument_context('network vhub bgpconnection list') as c:
        c.argument('virtual_hub_name', id_part=None)

    with self.argument_context('network vhub route') as c:
        c.argument('virtual_hub_name', vhub_name_type, id_part=None)
        c.argument('address_prefixes', nargs='+', help='Space-separated list of CIDR prefixes.')
        c.argument('next_hop_ip_address', options_list='--next-hop', help='IP address of the next hop.')
        c.argument('index', type=int, help='List index of the item (starting with 1).')

    with self.argument_context('network vhub route-table') as c:
        c.argument('virtual_hub_name', vhub_name_type, id_part=None)
        c.argument('route_table_name', options_list=['--name', '-n'], help='Name of the virtual hub route table.')
        c.argument('destination_type', arg_type=get_enum_type(['Service', 'CIDR', 'ResourceId']), help='The type of destinations')
        c.argument('destinations', nargs='+', help='Space-separated list of all destinations.')
        c.argument('next_hop_type', arg_type=get_enum_type(['ResourceId']), help='The type of next hop.')
        c.argument('index', type=int, help='List index of the item (starting with 1).')
        c.argument('next_hop', help='The resource ID of the next hop.', min_api='2020-04-01')
        c.argument('route_name', help='The name of the route.', min_api='2020-04-01')
        c.argument('labels', nargs='+', help='Space-separated list of all labels associated with this route table.', min_api='2020-04-01')
    # endregion

    # region VpnGateways
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
        c.argument("vpn_site_link", help='The resource ID of VPN Site Link.')
        c.argument('with_link', help='Create VpnConnection with default link.', arg_type=get_three_state_flag())

    for item in ['network vpn-gateway connection create', 'network vpn-gateway connection update']:
        with self.argument_context(item) as c:
            c.argument('associated_inbound_routemap', help='Resource uri of inbound routemap for this connection’s routing configuration')
            c.argument('associated_outbound_routemap', help='Resource uri of outbound routemap for this connection’s routing configuration')

    with self.argument_context('network vpn-gateway connection list') as c:
        # List commands cannot use --ids flag
        c.argument('resource_name', vpn_gateway_name_type, id_part=None)
        c.argument('gateway_name', id_part=None)

    with self.argument_context('network vpn-gateway connection vpn-site-link-conn') as c:
        c.argument("connection_name", help='Name of the VPN gateway connection.', options_list=['--connection-name'])
        c.argument("item_name", help='Name of the VPN gateway connection.', options_list=['--connection-name'])
        c.argument("vpn_site_link_conn_name", help='Name of the VPN site link connection.', options_list=['--name', '-n'], id_part='child_name_1')
        c.argument("vpn_site_link", help='The resource ID of VPN Site Link.')
        c.argument('routing_weight', type=int, help='Routing weight.')
        c.argument('shared_key', help='Shared key.')
        c.argument('enable_rate_limiting', options_list='--rate-limiting', arg_type=get_three_state_flag(), help='Enable rate limiting.')
        c.argument('connection_bandwidth', help='Expected bandwidth in Mbps.', type=int)
        c.argument('enable_bgp', arg_type=get_three_state_flag(), help='Enable BGP.')
        c.argument('use_local_azure_ip_address', arg_type=get_three_state_flag(), help='Use local azure ip to initiate connection.')
        c.argument('use_policy_based_traffic_selectors', arg_type=get_three_state_flag(), help='Enable policy-based traffic selectors.')
        c.argument('vpn_connection_protocol_type', help='Connection protocol used for this connection.', arg_type=get_enum_type(['IKEv2', 'IKEv1']))
        c.argument('vpn_link_connection_mode', help='Vpn link connection mode.', arg_type=get_enum_type(['Default', 'ResponderOnly', 'InitiatorOnly']))
        c.argument('index', type=int, help='List index of the item (starting with 1).')

    with self.argument_context('network vpn-gateway connection vpn-site-link-conn list') as c:
        c.argument('resource_name', vpn_gateway_name_type, id_part=None)
        c.argument('gateway_name', id_part=None)

    with self.argument_context('network vpn-gateway connection vpn-site-link-conn ipsec-policy list') as c:
        c.argument('resource_name', vpn_gateway_name_type, id_part=None)
        c.argument('gateway_name', id_part=None)

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
        c.argument('with_link', help='Create VPN site with default link.', arg_type=get_three_state_flag())

    with self.argument_context('network vpn-site', arg_group='Device Property') as c:
        c.argument('device_model', help='Model of the device.')
        c.argument('device_vendor', help='Name of the device vendor.')
        c.argument('link_speed', help='Link speed in Mbps.', type=int)

    with self.argument_context('network vpn-site link') as c:
        c.argument('vpn_site_name', vpn_site_name_type)
        c.argument('vpn_site_link_name', help='The name of vpn site link.', options_list=['--name', '-n'])
        c.argument('fqdn', help='FQDN of vpn-site-link.')
        c.argument('link_provider_name', help='Name of the link provider.')
        c.argument('link_speed_in_mbps', help='Link speed.', type=int)
        c.argument('index', type=int, help='List index of the item (starting with 1).')

    with self.argument_context('network vpn-site link list') as c:
        c.argument('resource_name', vpn_gateway_name_type, id_part=None)
        c.argument('virtual_wan_name', vwan_name_type, id_part=None)
        c.argument('vpn_site_name', vpn_site_name_type, options_list=['--site-name'], id_part=None)

    for scope in ['vpn-site', 'vpn-gateway']:
        with self.argument_context(f"network {scope}", arg_group='BGP Peering') as c:
            c.argument('asn', help='BGP speaker\'s ASN.', type=int)
            c.argument('peer_weight', help='Weight added to routes learned from this BGP speaker.', type=int)
            c.argument('bgp_peering_address', help='Peering address and BGP identifier of this BGP speaker.')

    with self.argument_context('network vpn-site download') as c:
        c.argument('virtual_wan_name', vwan_name_type, id_part=None)
        c.argument('vpn_sites', help='Space-separated list of VPN site names or IDs.', nargs='+', validator=get_network_resource_name_or_id('vpn_sites', 'vpnSites'))
    # endregion

    # region VpnServerConfigurations
    with self.argument_context('network vpn-server-config') as c:
        c.argument('vpn_protocols', nargs='+', options_list=['--protocols'], arg_type=get_enum_type(VpnGatewayTunnelingProtocol), help='VPN protocols for the VpnServerConfiguration.')
        c.argument('vpn_auth_types', nargs='+', options_list=['--auth-types'], arg_type=get_enum_type(VpnAuthenticationType), help='List of VPN authentication types for the VpnServerConfiguration.')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('vpn_server_configuration_name', options_list=['--name', '-n'], help='Name of the Vpn server configuration.')
    with self.argument_context('network vpn-server-config', arg_group='AAD Auth') as c:
        c.argument('aad_tenant', help='AAD Vpn authentication parameter AAD tenant.')
        c.argument('aad_audience', help='AAD Vpn authentication parameter AAD audience.')
        c.argument('aad_issuer', help='AAD Vpn authentication parameter AAD issuer.')
    with self.argument_context('network vpn-server-config', arg_group='Certificate Auth') as c:
        c.argument('vpn_client_root_certs', help='List of VPN client root certificate file paths.', nargs='+')
        c.argument('vpn_client_revoked_certs', help='List of VPN client revoked certificate file paths.', nargs='+')
    with self.argument_context('network vpn-server-config', arg_group='Radius Auth') as c:
        c.argument('radius_client_root_certs', help='List of Radius client root certificate file paths.', nargs='+')
        c.argument('radius_server_root_certs', help='List of Radius server root certificate file paths.', nargs='+')
        c.argument('radius_servers', nargs='+', action=RadiusServerAddAction, help='Radius Server configuration.')

    with self.argument_context('network vpn-server-config', arg_group='IP Security') as c:
        c.argument('sa_life_time_seconds', options_list='--sa-lifetime', help='IPSec Security Association (also called Quick Mode or Phase 2 SA) lifetime in seconds for a site-to-site VPN tunnel.', type=int)
        c.argument('sa_data_size_kilobytes', options_list='--sa-data-size', help='IPSec Security Association (also called Quick Mode or Phase 2 SA) payload size in KB for a site-to-site VPN tunnel.', type=int)
        c.argument('ipsec_encryption', arg_type=get_enum_type(IpsecEncryption), help='IPSec encryption algorithm (IKE phase 1).')
        c.argument('ipsec_integrity', arg_type=get_enum_type(IpsecIntegrity), help='IPSec integrity algorithm (IKE phase 1).')
        c.argument('ike_encryption', arg_type=get_enum_type(IkeEncryption), help='IKE encryption algorithm (IKE phase 2).')
        c.argument('ike_integrity', arg_type=get_enum_type(IkeIntegrity), help='IKE integrity algorithm (IKE phase 2).')
        c.argument('dh_group', arg_type=get_enum_type(DhGroup), help='DH Groups used in IKE Phase 1 for initial SA.')
        c.argument('pfs_group', arg_type=get_enum_type(PfsGroup), help='The Pfs Groups used in IKE Phase 2 for new child SA.')
        c.argument('index', type=int, help='List index of the ipsec policy(starting with 0).')
    # endregion

    # region P2SVpnGateways
    with self.argument_context('network p2s-vpn-gateway') as c:
        c.argument('address_space', nargs='+', help='Address space for P2S VpnClient. Space-separated list of IP address ranges.')
        c.argument('p2s_conn_config_name', options_list=['--config-name'], help='Name or p2s connection configuration.')
        c.argument('scale_unit', type=int, help='The scale unit for this VPN gateway.')
        c.argument('gateway_name', options_list=['--name', '-n'], help='Name of the P2S Vpn Gateway.')
        c.argument('virtual_hub', options_list='--vhub', help='Name or ID of a virtual hub.', validator=get_network_resource_name_or_id('virtual_hub', 'virtualHubs'))
        c.argument('vpn_server_config', help='Name or ID of a vpn server configuration.', validator=get_network_resource_name_or_id('vpn_server_config', 'vpnServerConfigurations'))
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    for item in ['network p2s-vpn-gateway create', 'network p2s-vpn-gateway update']:
        with self.argument_context(item) as c:
            c.argument('associated_inbound_routemap', help='Resource uri of inbound routemap for this connection’s routing configuration')
            c.argument('associated_outbound_routemap', help='Resource uri of outbound routemap for this connection’s routing configuration')

    with self.argument_context('network p2s-vpn-gateway connection') as c:
        for dest in ['gateway_name', 'resource_name']:
            c.argument(dest, p2s_vpn_gateway_name_type)
        c.argument('item_name', help='Name of the P2S VPN gateway connection.', options_list=['--name', '-n'], id_part='child_name_1')

    with self.argument_context('network p2s-vpn-gateway connection list') as c:
        c.argument('resource_name', p2s_vpn_gateway_name_type, id_part=None)

    with self.argument_context('network p2s-vpn-gateway vpn-client') as c:
        c.argument('authentication_method', arg_type=get_enum_type(AuthenticationMethod), help='VPN client authentication method.')
    # endregion

    # region Routing Configuration
    for item in ['vpn-gateway connection', 'p2s-vpn-gateway', 'vhub connection']:
        with self.argument_context(f"network {item}", arg_group='Routing Configuration', min_api='2020-04-01', is_preview=True) as c:
            c.argument('associated_route_table', associated_route_table_type)
            c.argument('propagated_route_tables', propagated_route_tables_type)
            c.argument('labels', propagated_route_tables_label_type)
    # endregion
