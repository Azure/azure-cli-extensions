# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.util import sdk_no_wait

from ._client_factory import network_client_factory, network_client_route_table_factory
from ._util import _get_property


logger = get_logger(__name__)


class UpdateContext(object):

    def __init__(self, instance):
        self.instance = instance

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def update_param(self, prop, value, allow_clear):
        if value == '' and allow_clear:
            setattr(self.instance, prop, None)
        elif value is not None:
            setattr(self.instance, prop, value)


def _generic_list(cli_ctx, operation_name, resource_group_name):
    ncf = network_client_factory(cli_ctx)
    operation_group = getattr(ncf, operation_name)
    if resource_group_name:
        return operation_group.list_by_resource_group(resource_group_name)
    return operation_group.list()


def _get_property(items, name):
    result = next((x for x in items if x.name.lower() == name.lower()), None)
    if not result:
        raise CLIError("Property '{}' does not exist".format(name))
    return result


def _upsert(parent, collection_name, obj_to_add, key_name, warn=True):
    if not getattr(parent, collection_name, None):
        setattr(parent, collection_name, [])
    collection = getattr(parent, collection_name, None)

    value = getattr(obj_to_add, key_name)
    if value is None:
        raise CLIError(
            "Unable to resolve a value for key '{}' with which to match.".format(key_name))
    match = next((x for x in collection if getattr(x, key_name, None) == value), None)
    if match:
        if warn:
            logger.warning("Item '%s' already exists. Replacing with new values.", value)
        collection.remove(match)

    collection.append(obj_to_add)


def _find_item_at_path(instance, path):
    # path accepts the pattern property/name/property/name
    curr_item = instance
    path_comps = path.split('.')
    for i, comp in enumerate(path_comps):
        if i % 2:
            # name
            curr_item = next((x for x in curr_item if x.name == comp), None)
        else:
            # property
            curr_item = getattr(curr_item, comp, None)
        if not curr_item:
            raise CLIError("not found: '{}' not found at path '{}'".format(comp, '.'.join(path_comps[:i])))
    return curr_item


# region VirtualWAN
def create_virtual_wan(cmd, resource_group_name, virtual_wan_name, tags=None, location=None,
                       security_provider_name=None, branch_to_branch_traffic=None,
                       vnet_to_vnet_traffic=None, office365_category=None, disable_vpn_encryption=None,
                       vwan_type=None):
    client = network_client_factory(cmd.cli_ctx).virtual_wans
    VirtualWAN = cmd.get_models('VirtualWAN')
    wan = VirtualWAN(
        tags=tags,
        location=location,
        disable_vpn_encryption=disable_vpn_encryption,
        security_provider_name=security_provider_name,
        allow_branch_to_branch_traffic=branch_to_branch_traffic,
        allow_vnet_to_vnet_traffic=vnet_to_vnet_traffic,
        office365_local_breakout_category=office365_category,
        type=vwan_type
    )
    return client.create_or_update(resource_group_name, virtual_wan_name, wan)


def update_virtual_wan(instance, tags=None, security_provider_name=None, branch_to_branch_traffic=None,
                       vnet_to_vnet_traffic=None, office365_category=None, disable_vpn_encryption=None,
                       vwan_type=None):
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
        c.update_param('security_provider_name', security_provider_name, False)
        c.update_param('allow_branch_to_branch_traffic', branch_to_branch_traffic, False)
        c.update_param('allow_vnet_to_vnet_traffic', vnet_to_vnet_traffic, False)
        c.update_param('office365_local_breakout_category', office365_category, False)
        c.update_param('disable_vpn_encryption', disable_vpn_encryption, False)
        c.update_param('type', vwan_type, False)
    return instance


def list_virtual_wans(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'virtual_wans', resource_group_name)
# endregion


# region VirtualHubs
def create_virtual_hub(cmd, resource_group_name, virtual_hub_name, address_prefix, virtual_wan,
                       location=None, tags=None, no_wait=False, sku=None):
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    VirtualHub, SubResource = cmd.get_models('VirtualHub', 'SubResource')
    hub = VirtualHub(
        tags=tags,
        location=location,
        address_prefix=address_prefix,
        virtual_wan=SubResource(id=virtual_wan),
        sku=sku
    )
    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name, virtual_hub_name, hub)


def update_virtual_hub(instance, cmd, address_prefix=None, virtual_wan=None, tags=None, sku=None):
    SubResource = cmd.get_models('SubResource')
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
        c.update_param('address_prefix', address_prefix, False)
        c.update_param('virtual_wan', SubResource(id=virtual_wan) if virtual_wan else None, False)
        c.update_param('sku', sku, False)
    return instance


def list_virtual_hubs(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'virtual_hubs', resource_group_name)


def create_hub_vnet_connection(cmd, resource_group_name, virtual_hub_name, connection_name, remote_virtual_network,
                               allow_hub_to_remote_vnet_transit=None, allow_remote_vnet_to_use_hub_vnet_gateways=None,
                               enable_internet_security=None, no_wait=False):
    HubVirtualNetworkConnection, SubResource = cmd.get_models(
        'HubVirtualNetworkConnection', 'SubResource')
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    connection = HubVirtualNetworkConnection(
        name=connection_name,
        remote_virtual_network=SubResource(id=remote_virtual_network),
        allow_hub_to_remote_vnet_transit=allow_hub_to_remote_vnet_transit,
        allow_remote_vnet_to_use_hub_vnet_gateway=allow_remote_vnet_to_use_hub_vnet_gateways,
        enable_internet_security=enable_internet_security
    )
    _upsert(hub, 'virtual_network_connections', connection, 'name', warn=True)
    poller = sdk_no_wait(no_wait, client.create_or_update, resource_group_name, virtual_hub_name, hub)
    if no_wait:
        return poller

    from azure.cli.core.commands import LongRunningOperation
    return _get_property(LongRunningOperation(cmd.cli_ctx)(poller).virtual_network_connections, connection_name)


# pylint: disable=inconsistent-return-statements
def add_hub_route(cmd, resource_group_name, virtual_hub_name, address_prefixes, next_hop_ip_address, no_wait=False):
    VirtualHubRoute = cmd.get_models('VirtualHubRoute')
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    route = VirtualHubRoute(address_prefixes=address_prefixes, next_hop_ip_address=next_hop_ip_address)
    hub.route_table.routes.append(route)
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, virtual_hub_name, hub)
    try:
        return poller.result().route_table.routes
    except AttributeError:
        return


def list_hub_routes(cmd, resource_group_name, virtual_hub_name):
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    return hub.route_table.routes


# pylint: disable=inconsistent-return-statements
def remove_hub_route(cmd, resource_group_name, virtual_hub_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    try:
        hub.route_table.routes.pop(index - 1)
    except IndexError:
        raise CLIError('invalid index: {}. Index can range from 1 to {}'.format(index, len(hub.route_table.routes)))
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, virtual_hub_name, hub)
    try:
        return poller.result().route_table.routes
    except AttributeError:
        return


# pylint: disable=inconsistent-return-statements
def create_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name,
                            attached_connections, destination_type, destinations,
                            next_hop_type, next_hops,
                            tags=None, no_wait=False, location=None):
    VirtualHubRouteTableV2, VirtualHubRouteV2 = cmd.get_models('VirtualHubRouteTableV2', 'VirtualHubRouteV2')
    client = network_client_route_table_factory(cmd.cli_ctx).virtual_hub_route_table_v2s
    route = VirtualHubRouteV2(destination_type=destination_type,
                              destinations=destinations,
                              next_hop_type=next_hop_type,
                              next_hops=next_hops)
    route_table = VirtualHubRouteTableV2(location=location,
                                         tags=tags,
                                         attached_connections=attached_connections,
                                         routes=[route])
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, virtual_hub_name, route_table_name, route_table)
    try:
        return poller.result()
    except AttributeError:
        return


def update_vhub_route_table(instance, attached_connections=None, tags=None):
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
        c.update_param('attached_connections', attached_connections, False)
    return instance


# pylint: disable=inconsistent-return-statements
def add_hub_routetable_route(cmd, resource_group_name, virtual_hub_name, route_table_name,
                             destination_type, destinations,
                             next_hop_type, next_hops, no_wait=False):
    VirtualHubRouteV2 = cmd.get_models('VirtualHubRouteV2')
    client = network_client_route_table_factory(cmd.cli_ctx).virtual_hub_route_table_v2s
    route_table = client.get(resource_group_name, virtual_hub_name, route_table_name)
    route = VirtualHubRouteV2(destination_type=destination_type,
                              destinations=destinations,
                              next_hop_type=next_hop_type,
                              next_hops=next_hops)
    route_table.routes.append(route)
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, virtual_hub_name, route_table_name, route_table)
    try:
        return poller.result().routes
    except AttributeError:
        return


def list_hub_routetable_route(cmd, resource_group_name, virtual_hub_name, route_table_name):
    client = network_client_route_table_factory(cmd.cli_ctx).virtual_hub_route_table_v2s
    route_table = client.get(resource_group_name, virtual_hub_name, route_table_name)
    return route_table.routes


# pylint: disable=inconsistent-return-statements
def remove_hub_routetable_route(cmd, resource_group_name, virtual_hub_name, route_table_name, index, no_wait=False):
    client = network_client_route_table_factory(cmd.cli_ctx).virtual_hub_route_table_v2s
    route_table = client.get(resource_group_name, virtual_hub_name, route_table_name)
    try:
        route_table.routes.pop(index - 1)
    except IndexError:
        raise CLIError('invalid index: {}. Index can range from 1 to {}'.format(index, len(route_table.routes)))
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, virtual_hub_name, route_table_name, route_table)
    try:
        return poller.result().routes
    except AttributeError:
        return
# endregion


# region VpnGateways
def create_vpn_gateway(cmd, resource_group_name, gateway_name, virtual_hub,
                       location=None, tags=None, scale_unit=None,
                       asn=None, bgp_peering_address=None, peer_weight=None, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    VpnGateway, SubResource = cmd.get_models('VpnGateway', 'SubResource')
    gateway = VpnGateway(
        location=location,
        tags=tags,
        virtual_hub=SubResource(id=virtual_hub) if virtual_hub else None,
        vpn_gateway_scale_unit=scale_unit,
        bgp_settings={
            'asn': asn,
            'bgpPeeringAddress': bgp_peering_address,
            'peerWeight': peer_weight
        }
    )
    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name, gateway_name, gateway)


def update_vpn_gateway(instance, cmd, virtual_hub=None, tags=None, scale_unit=None,
                       asn=None, bgp_peering_address=None, peer_weight=None):
    SubResource = cmd.get_models('SubResource')
    with UpdateContext(instance) as c:
        c.update_param('virtual_hub', SubResource(id=virtual_hub) if virtual_hub else None, True)
        c.update_param('tags', tags, True)
        c.update_param('vpn_gateway_scale_unit', scale_unit, False)

    bgp_settings = instance.bgp_settings
    with UpdateContext(bgp_settings) as c:
        c.update_param('asn', asn, False)
        c.update_param('bgp_peering_address', bgp_peering_address, False)
        c.update_param('peer_weight', peer_weight, False)

    return instance


def create_vpn_gateway_connection(cmd, resource_group_name, gateway_name, connection_name,
                                  remote_vpn_site, routing_weight=None, protocol_type=None,
                                  connection_bandwidth=None, shared_key=None, enable_bgp=None,
                                  enable_rate_limiting=None, enable_internet_security=None, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    VpnConnection, SubResource = cmd.get_models('VpnConnection', 'SubResource')
    gateway = client.get(resource_group_name, gateway_name)
    conn = VpnConnection(
        name=connection_name,
        remote_vpn_site=SubResource(id=remote_vpn_site),
        routing_weight=routing_weight,
        protocol_type=protocol_type,
        connection_bandwidth=connection_bandwidth,
        shared_key=shared_key,
        enable_bgp=enable_bgp,
        enable_rate_limiting=enable_rate_limiting,
        enable_internet_security=enable_internet_security
    )
    _upsert(gateway, 'connections', conn, 'name')
    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name, gateway_name, gateway)


def list_vpn_gateways(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'vpn_gateways', resource_group_name)


# pylint: disable=inconsistent-return-statements
def add_vpn_gateway_connection_ipsec_policy(cmd, resource_group_name, gateway_name, connection_name,
                                            sa_life_time_seconds, sa_data_size_kilobytes, ipsec_encryption,
                                            ipsec_integrity, ike_encryption, ike_integrity, dh_group, pfs_group,
                                            no_wait=False):
    IpsecPolicy = cmd.get_models('IpsecPolicy')
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    gateway = client.get(resource_group_name, gateway_name)
    conn = _find_item_at_path(gateway, 'connections.{}'.format(connection_name))
    conn.ipsec_policies.append(
        IpsecPolicy(
            sa_life_time_seconds=sa_life_time_seconds,
            sa_data_size_kilobytes=sa_data_size_kilobytes,
            ipsec_encryption=ipsec_encryption,
            ipsec_integrity=ipsec_integrity,
            ike_encryption=ike_encryption,
            ike_integrity=ike_integrity,
            dh_group=dh_group,
            pfs_group=pfs_group
        )
    )
    _upsert(gateway, 'connections', conn, 'name', warn=False)
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, gateway_name, gateway)
    try:
        return _get_property(poller.result().connections, connection_name)
    except AttributeError:
        return


def list_vpn_conn_ipsec_policies(cmd, resource_group_name, gateway_name, connection_name):
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    gateway = client.get(resource_group_name, gateway_name)
    conn = _find_item_at_path(gateway, 'connections.{}'.format(connection_name))
    return conn.ipsec_policies


# pylint: disable=inconsistent-return-statements
def remove_vpn_conn_ipsec_policy(cmd, resource_group_name, gateway_name, connection_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    gateway = client.get(resource_group_name, gateway_name)
    conn = _find_item_at_path(gateway, 'connections.{}'.format(connection_name))
    try:
        conn.ipsec_policies.pop(index - 1)
    except IndexError:
        raise CLIError('invalid index: {}. Index can range from 1 to {}'.format(index, len(conn.ipsec_policies)))
    _upsert(gateway, 'connections', conn, 'name', warn=False)
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, gateway_name, gateway)
    try:
        return _get_property(poller.result().connections, connection_name)
    except AttributeError:
        return
# endregion


# region VpnSites
def create_vpn_site(cmd, resource_group_name, vpn_site_name, ip_address,
                    asn=None, bgp_peering_address=None,
                    virtual_wan=None, location=None, tags=None,
                    site_key=None, address_prefixes=None, is_security_site=None,
                    device_vendor=None, device_model=None, link_speed=None,
                    peer_weight=None, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_sites
    VpnSite, SubResource = cmd.get_models('VpnSite', 'SubResource')
    site = VpnSite(
        location=location,
        tags=tags,
        is_security_site=is_security_site,
        ip_address=ip_address,
        site_key=site_key,
        virtual_wan=SubResource(id=virtual_wan) if virtual_wan else None,
        address_space={'addressPrefixes': address_prefixes},
        device_properties={
            'deviceVendor': device_vendor,
            'deviceModel': device_model,
            'linkSpeedInMbps': link_speed
        },
        bgp_properties={
            'asn': asn,
            'bgpPeeringAddress': bgp_peering_address,
            'peerWeight': peer_weight
        }
    )
    if not any([asn, bgp_peering_address, peer_weight]):
        site.bgp_properties = None
    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name, vpn_site_name, site)


def update_vpn_site(instance, cmd, ip_address=None, virtual_wan=None, tags=None,
                    site_key=None, address_prefixes=None, is_security_site=None,
                    device_vendor=None, device_model=None, link_speed=None,
                    asn=None, bgp_peering_address=None, peer_weight=None):
    SubResource = cmd.get_models('SubResource')
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
        c.update_param('ip_address', ip_address, False)
        c.update_param('virtual_wan', SubResource(id=virtual_wan) if virtual_wan else None, False)
        c.update_param('is_security_site', is_security_site, False)
        c.update_param('site_key', site_key, True)

    device_properties = instance.device_properties
    with UpdateContext(device_properties) as c:
        c.update_param('device_vendor', device_vendor, True)
        c.update_param('device_model', device_model, True)
        c.update_param('link_speed_in_mbps', link_speed, False)

    address_space = instance.address_space
    with UpdateContext(address_space) as c:
        c.update_param('address_prefixes', address_prefixes, False)

    bgp_properties = instance.bgp_properties
    with UpdateContext(bgp_properties) as c:
        c.update_param('asn', asn, False)
        c.update_param('bgp_peering_address', bgp_peering_address, False)
        c.update_param('peer_weight', peer_weight, False)

    return instance


def list_vpn_sites(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'vpn_sites', resource_group_name)
# endregion
