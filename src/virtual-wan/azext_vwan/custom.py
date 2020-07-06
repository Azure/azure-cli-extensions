# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
import re
import hashlib

from OpenSSL import crypto
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
        if value in ('', []) and allow_clear:
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
def create_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name, destination_type,
                            destinations, next_hop_type, next_hops=None, attached_connections=None, next_hop=None,
                            route_name=None, labels=None, no_wait=False):
    if attached_connections:  # route table v2
        if next_hops is None:
            raise CLIError('Usage error: --next-hops must be provided when --connections is provided.')
        if labels is not None or route_name is not None or next_hop is not None:
            raise CLIError(
                'Usage error: None of [--labels, --route-name, --next-hop] is supported when --connections is provided.'
            )

        VirtualHubRouteTableV2, VirtualHubRouteV2 = cmd.get_models('VirtualHubRouteTableV2', 'VirtualHubRouteV2')
        client = _v2_route_table_client(cmd.cli_ctx)
        route = VirtualHubRouteV2(destination_type=destination_type,
                                  destinations=destinations,
                                  next_hop_type=next_hop_type,
                                  next_hops=next_hops)
        route_table = VirtualHubRouteTableV2(attached_connections=attached_connections, routes=[route])
    else:  # route table v3
        if next_hop is None or route_name is None:
            raise CLIError(
                'Usage error: --next-hop and --route-name must be provided when --connections is not provided.')
        if next_hops is not None:
            raise CLIError('Usage error: --next-hops is not supported when --connections is not provided.')

        HubRouteTable, HubRoute = cmd.get_models('HubRouteTable', 'HubRoute')
        client = _v3_route_table_client(cmd.cli_ctx)
        route = HubRoute(name=route_name,
                         destination_type=destination_type,
                         destinations=destinations,
                         next_hop_type=next_hop_type,
                         next_hop=next_hop)
        route_table = HubRouteTable(routes=[route], labels=labels)

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name,
                       virtual_hub_name, route_table_name, route_table)


def update_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name,
                            attached_connections=None, labels=None, no_wait=False):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    if _is_v2_route_table(route_table):
        if labels is not None:
            raise CLIError('Usage error: --labels is not supported for this v2 route table.')
        client = _v2_route_table_client(cmd.cli_ctx)
        route_table.attached_connections = attached_connections
    else:
        if attached_connections is not None:
            raise CLIError('Usage error: --connections is not supported for this v3 route table.')
        client = _v3_route_table_client(cmd.cli_ctx)
        route_table.labels = labels

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name,
                       virtual_hub_name, route_table_name, route_table)


def get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name):
    from msrestazure.azure_exceptions import CloudError
    try:
        return _v3_route_table_client(cmd.cli_ctx)\
            .get(resource_group_name, virtual_hub_name, route_table_name)  # Get v3 route table first.
    except CloudError as ex:
        if ex.status_code == 404:
            return _v2_route_table_client(cmd.cli_ctx)\
                .get(resource_group_name, virtual_hub_name, route_table_name)  # Get v2 route table.

        raise


def delete_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name, no_wait=False):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    client = _route_table_client(cmd.cli_ctx, route_table)

    return sdk_no_wait(no_wait, client.delete, resource_group_name, virtual_hub_name, route_table_name)


def list_vhub_route_tables(cmd, resource_group_name, virtual_hub_name):
    v2_route_tables = _v2_route_table_client(cmd.cli_ctx).list(resource_group_name, virtual_hub_name)
    v3_route_tables = _v3_route_table_client(cmd.cli_ctx).list(resource_group_name, virtual_hub_name)

    all_route_tables = list(v2_route_tables) + list(v3_route_tables)
    return all_route_tables


# pylint: disable=inconsistent-return-statements
def add_hub_routetable_route(cmd, resource_group_name, virtual_hub_name, route_table_name,
                             destination_type, destinations, next_hop_type,
                             next_hops=None, next_hop=None, route_name=None, no_wait=False):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    if _is_v2_route_table(route_table):
        if next_hops is None:
            raise CLIError('Usage error: --next-hops must be provided as you are adding route to v2 route table.')
        if route_name is not None or next_hop is not None:
            raise CLIError(
                'Usage error: Neither --route-name nore --next-hop is not supported for this v2 route table.')

        client = _v2_route_table_client(cmd.cli_ctx)
        VirtualHubRouteV2 = cmd.get_models('VirtualHubRouteV2')
        route = VirtualHubRouteV2(destination_type=destination_type,
                                  destinations=destinations,
                                  next_hop_type=next_hop_type,
                                  next_hops=next_hops)
        route_table.routes.append(route)
    else:
        if next_hop is None or route_name is None:
            raise CLIError(
                'Usage error: --next-hop and --route-name must be provided as you are adding route to v3 route table.')
        if next_hops is not None:
            raise CLIError('Usage error: --next-hops is not supported for this v3 route table.')

        client = _v3_route_table_client(cmd.cli_ctx)
        HubRoute = cmd.get_models('HubRoute')
        route = HubRoute(name=route_name,
                         destination_type=destination_type,
                         destinations=destinations,
                         next_hop_type=next_hop_type,
                         next_hop=next_hop)
        route_table.routes.append(route)

    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, virtual_hub_name, route_table_name, route_table)
    try:
        return poller.result().routes
    except AttributeError:
        return


def list_hub_routetable_route(cmd, resource_group_name, virtual_hub_name, route_table_name):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    return route_table.routes


# pylint: disable=inconsistent-return-statements
def remove_hub_routetable_route(cmd, resource_group_name, virtual_hub_name, route_table_name, index, no_wait=False):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    try:
        route_table.routes.pop(index - 1)
    except IndexError:
        raise CLIError('invalid index: {}. Index can range from 1 to {}'.format(index, len(route_table.routes)))

    client = _route_table_client(cmd.cli_ctx, route_table)
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, virtual_hub_name, route_table_name, route_table)
    try:
        return poller.result().routes
    except AttributeError:
        return


def _is_v2_route_table(route_table):
    return hasattr(route_table, 'attached_connections')


def _route_table_client(cli_ctx, route_table):
    if _is_v2_route_table(route_table):
        return _v2_route_table_client(cli_ctx)

    return _v3_route_table_client(cli_ctx)


def _v2_route_table_client(cli_ctx):
    return network_client_route_table_factory(cli_ctx).virtual_hub_route_table_v2s


def _v3_route_table_client(cli_ctx):
    return network_client_route_table_factory(cli_ctx).hub_route_tables
# endregion


# region VpnGateways
def create_vpn_gateway(cmd, resource_group_name, gateway_name, virtual_hub,
                       location=None, tags=None, scale_unit=None,
                       asn=None, bgp_peering_address=None, peer_weight=None, no_wait=False):
    from msrestazure.azure_exceptions import CloudError
    from .vendored_sdks.v2018_08_01.v2018_08_01.models.error_py3 import ErrorException
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    try:
        client.get(resource_group_name, gateway_name)
    except (CloudError, ErrorException):
        pass
    else:
        raise CLIError('{} VPN gateway already exist. Please delete it first.'.format(gateway_name))
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


# region VPN server configuarions
# pylint: disable=line-too-long
def create_vpn_server_config(cmd, resource_group_name, vpn_server_configuration_name, location=None,
                             vpn_protocols=None, vpn_auth_types=None,
                             vpn_client_root_certs=None, vpn_client_revoked_certs=None,
                             radius_servers=None, radius_client_root_certs=None, radius_server_root_certs=None,
                             aad_tenant=None, aad_audience=None, aad_issuer=None, no_wait=False):
    client = network_client_route_table_factory(cmd.cli_ctx).vpn_server_configurations
    (VpnServerConfiguration,
     AadAuthenticationParameters,
     VpnServerConfigVpnClientRootCertificate,
     VpnServerConfigVpnClientRevokedCertificate,
     VpnServerConfigRadiusServerRootCertificate,
     VpnServerConfigRadiusClientRootCertificate) = cmd.get_models('VpnServerConfiguration',
                                                                  'AadAuthenticationParameters',
                                                                  'VpnServerConfigVpnClientRootCertificate',
                                                                  'VpnServerConfigVpnClientRevokedCertificate',
                                                                  'VpnServerConfigRadiusServerRootCertificate',
                                                                  'VpnServerConfigRadiusClientRootCertificate')
    vpn_server_config = VpnServerConfiguration(
        location=location,
        vpn_protocols=vpn_protocols,
        vpn_authentication_types=vpn_auth_types,
        vpn_client_root_certificates=_load_certificates_and_build_name_and_public_cert_data(VpnServerConfigVpnClientRootCertificate,
                                                                                            vpn_client_root_certs),
        vpn_client_revoked_certificates=_load_certificates_and_build_name_and_thumbprint(VpnServerConfigVpnClientRevokedCertificate,
                                                                                         vpn_client_revoked_certs),
        radius_servers=radius_servers,
        radius_client_root_certificates=_load_certificates_and_build_name_and_thumbprint(VpnServerConfigRadiusClientRootCertificate,
                                                                                         radius_client_root_certs),
        radius_server_root_certificates=_load_certificates_and_build_name_and_public_cert_data(VpnServerConfigRadiusServerRootCertificate,
                                                                                               radius_server_root_certs),
        aad_authentication_parameters=AadAuthenticationParameters(
            aad_tenant=aad_tenant,
            aad_audience=aad_audience,
            aad_issuer=aad_issuer
        )
    )

    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name, vpn_server_configuration_name, vpn_server_config)


# pylint: disable=line-too-long
def update_vpn_server_config(instance, cmd, vpn_protocols=None, vpn_auth_types=None,
                             vpn_client_root_certs=None, vpn_client_revoked_certs=None,
                             radius_servers=None, radius_client_root_certs=None, radius_server_root_certs=None,
                             aad_tenant=None, aad_audience=None, aad_issuer=None):
    (VpnServerConfigVpnClientRootCertificate,
     VpnServerConfigVpnClientRevokedCertificate,
     VpnServerConfigRadiusServerRootCertificate,
     VpnServerConfigRadiusClientRootCertificate) = cmd.get_models('VpnServerConfigVpnClientRootCertificate',
                                                                  'VpnServerConfigVpnClientRevokedCertificate',
                                                                  'VpnServerConfigRadiusServerRootCertificate',
                                                                  'VpnServerConfigRadiusClientRootCertificate')
    with UpdateContext(instance) as c:
        c.update_param('vpn_protocols', vpn_protocols, False)
        c.update_param('vpn_authentication_types', vpn_auth_types, False)
        c.update_param('vpn_client_root_certificates', _load_certificates_and_build_name_and_public_cert_data(VpnServerConfigVpnClientRootCertificate, vpn_client_root_certs), True)
        c.update_param('vpn_client_revoked_certificates', _load_certificates_and_build_name_and_thumbprint(VpnServerConfigVpnClientRevokedCertificate, vpn_client_revoked_certs), True)
        c.update_param('radius_servers', radius_servers, True)
        c.update_param('radius_client_root_certificates', _load_certificates_and_build_name_and_thumbprint(VpnServerConfigRadiusClientRootCertificate, radius_client_root_certs), True)
        c.update_param('radius_server_root_certificates', _load_certificates_and_build_name_and_public_cert_data(VpnServerConfigRadiusServerRootCertificate, radius_server_root_certs), True)

    device_properties = instance.aad_authentication_parameters
    with UpdateContext(device_properties) as c:
        c.update_param('aad_tenant', aad_tenant, True)
        c.update_param('aad_audience', aad_audience, True)
        c.update_param('aad_issuer', aad_issuer, False)

    return instance


def list_vpn_server_config(cmd, resource_group_name=None):
    client = network_client_route_table_factory(cmd.cli_ctx).vpn_server_configurations
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def add_vpn_server_config_ipsec_policy(cmd, resource_group_name, vpn_server_configuration_name,
                                       sa_life_time_seconds, sa_data_size_kilobytes, ipsec_encryption,
                                       ipsec_integrity, ike_encryption, ike_integrity, dh_group, pfs_group,
                                       no_wait=False):
    client = network_client_route_table_factory(cmd.cli_ctx).vpn_server_configurations
    IpsecPolicy = cmd.get_models('IpsecPolicy')
    vpn_server_config = client.get(resource_group_name, vpn_server_configuration_name)
    vpn_server_config.vpn_client_ipsec_policies.append(
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
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, vpn_server_configuration_name, vpn_server_config)
    if no_wait:
        return poller
    from azure.cli.core.commands import LongRunningOperation
    return LongRunningOperation(cmd.cli_ctx)(poller).vpn_client_ipsec_policies


def list_vpn_server_config_ipsec_policies(cmd, resource_group_name, vpn_server_configuration_name):
    client = network_client_route_table_factory(cmd.cli_ctx).vpn_server_configurations
    vpn_server_config = client.get(resource_group_name, vpn_server_configuration_name)
    return vpn_server_config.vpn_client_ipsec_policies


# pylint: disable=inconsistent-return-statements
def remove_vpn_server_config_ipsec_policy(cmd, resource_group_name, vpn_server_configuration_name, index, no_wait=False):
    client = network_client_route_table_factory(cmd.cli_ctx).vpn_server_configurations
    vpn_server_config = client.get(resource_group_name, vpn_server_configuration_name)
    try:
        vpn_server_config.vpn_client_ipsec_policies.pop(index)
    except IndexError:
        raise CLIError('invalid index: {}. Index can range from 0 to {}'.format(index, len(vpn_server_config.vpn_client_ipsec_policies) - 1))
    poller = sdk_no_wait(no_wait, client.create_or_update,
                         resource_group_name, vpn_server_configuration_name, vpn_server_config)
    if no_wait:
        return poller
    from azure.cli.core.commands import LongRunningOperation
    return LongRunningOperation(cmd.cli_ctx)(poller).vpn_client_ipsec_policies


def create_p2s_vpn_gateway(cmd, resource_group_name, gateway_name, virtual_hub,
                           scale_unit, location=None, tags=None, p2s_conn_config_name='P2SConnectionConfigDefault',
                           vpn_server_config=None, address_space=None, no_wait=False):
    client = network_client_route_table_factory(cmd.cli_ctx).p2s_vpn_gateways
    (P2SVpnGateway,
     SubResource,
     P2SConnectionConfiguration,
     AddressSpace) = cmd.get_models('P2SVpnGateway',
                                    'SubResource',
                                    'P2SConnectionConfiguration',
                                    'AddressSpace')
    gateway = P2SVpnGateway(
        location=location,
        tags=tags,
        virtual_hub=SubResource(id=virtual_hub) if virtual_hub else None,
        vpn_gateway_scale_unit=scale_unit,
        vpn_server_configuration=SubResource(id=vpn_server_config) if vpn_server_config else None,
        p2_sconnection_configurations=[
            P2SConnectionConfiguration(
                vpn_client_address_pool=AddressSpace(
                    address_prefixes=address_space
                ),
                name=p2s_conn_config_name
            )
        ]
    )
    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name, gateway_name, gateway)


def update_p2s_vpn_gateway(instance, cmd, tags=None, scale_unit=None,
                           vpn_server_config=None, address_space=None, p2s_conn_config_name=None,):
    (SubResource,
     P2SConnectionConfiguration,
     AddressSpace) = cmd.get_models('SubResource',
                                    'P2SConnectionConfiguration',
                                    'AddressSpace')
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
        c.update_param('vpn_gateway_scale_unit', scale_unit, False)
        c.update_param('vpn_server_configuration', SubResource(id=vpn_server_config) if vpn_server_config else None, True)
        c.update_param('p2_sconnection_configurations', [
            P2SConnectionConfiguration(
                vpn_client_address_pool=AddressSpace(
                    address_prefixes=address_space
                ),
                name=p2s_conn_config_name
            )
        ], False)

    return instance


def list_p2s_vpn_gateways(cmd, resource_group_name=None):
    client = network_client_route_table_factory(cmd.cli_ctx).p2s_vpn_gateways
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def _load_cert_file(file_path):
    cer_data = None
    pem_data = None
    if os.path.splitext(file_path)[1] in ['.pem']:
        with open(file_path, "rb") as f:
            pem_data = f.read()
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, pem_data)
            cer_data = crypto.dump_certificate(crypto.FILETYPE_ASN1, x509)
    elif os.path.splitext(file_path)[1] in ['.cer', '.cert']:
        with open(file_path, "rb") as f:
            cer_data = f.read()
            x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cer_data)
            pem_data = crypto.dump_certificate(crypto.FILETYPE_PEM, x509)
    return cer_data, pem_data


def _load_certificates_and_build_name_and_thumbprint(model, file_paths_list):
    if file_paths_list is None:
        return None
    certificates = []
    for file_path in file_paths_list:
        kwargs = {}
        cer_data, _ = _load_cert_file(file_path)
        kwargs['name'] = os.path.splitext(os.path.basename(file_path))[0]
        kwargs['thumbprint'] = hashlib.sha1(cer_data).hexdigest()
        certificates.append(model(**kwargs))
    return certificates


def _load_certificates_and_build_name_and_public_cert_data(model, file_paths_list):
    if file_paths_list is None:
        return None
    certificates = []
    for file_path in file_paths_list:
        if not os.path.exists(file_path):
            continue
        kwargs = {}
        _, pem_data = _load_cert_file(file_path)
        kwargs['name'] = os.path.splitext(os.path.basename(file_path))[0]
        match = re.search(r'\-+BEGIN CERTIFICATE.+\-+(?P<public>[^-]+)\-+END CERTIFICATE.+\-+',
                          pem_data.decode(), re.I)
        kwargs['public_cert_data'] = match.group('public').strip()
        certificates.append(model(**kwargs))
    return certificates
# endregion
