# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-lines, unused-argument, protected-access

import os
import re
import hashlib

from OpenSSL import crypto
from knack.log import get_logger

from azure.cli.core.util import sdk_no_wait
from azure.cli.core.aaz import has_value
from azure.cli.core.aaz.utils import assign_aaz_list_arg
from azure.cli.core.azclierror import ArgumentUsageError, InvalidArgumentValueError
from .aaz.latest.network.vhub.connection import Create as _VHubConnectionCreate, Update as _VHubConnectionUpdate
from .aaz.latest.network.vpn_gateway.nat_rule import Create as _VPNGatewayNatRuleCreate, \
    Show as _VPNGatewayNatRuleShow, List as _VPNGatewayNatRuleList, Update as _VPNGatewayNatRuleUpdate
from ._client_factory import network_client_factory, cf_virtual_hub_bgpconnections
from ._util import _get_property

logger = get_logger(__name__)


class UpdateContext:

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

    def set_param(self, prop, value, allow_clear=True, curr_obj=None):
        curr_obj = curr_obj or self.instance
        if '.' in prop:
            prop, path = prop.split('.', 1)
            curr_obj = getattr(curr_obj, prop)
            self.set_param(path, value, allow_clear=allow_clear, curr_obj=curr_obj)
        elif value == '' and allow_clear:
            setattr(curr_obj, prop, None)
        elif value is not None:
            setattr(curr_obj, prop, value)


def _generic_list(cli_ctx, operation_name, resource_group_name):
    ncf = network_client_factory(cli_ctx)
    operation_group = getattr(ncf, operation_name)
    if resource_group_name:
        return operation_group.list_by_resource_group(resource_group_name)
    return operation_group.list()


def _get_property(items, name):
    result = next((x for x in items if x.name.lower() == name.lower()), None)
    if not result:
        raise InvalidArgumentValueError(f"Property '{name}' does not exist")
    return result


def _upsert(parent, collection_name, obj_to_add, key_name, warn=True):
    if not getattr(parent, collection_name, None):
        setattr(parent, collection_name, [])
    collection = getattr(parent, collection_name, None)

    value = getattr(obj_to_add, key_name)
    if value is None:
        raise InvalidArgumentValueError(
            f"Unable to resolve a value for key '{key_name}' with which to match.")
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
            raise InvalidArgumentValueError(f"not found: '{comp}' not found at path '{'.'.join(path_comps[:i])}'")
    return curr_item


# region VirtualWAN
def create_virtual_wan(cmd, resource_group_name, virtual_wan_name, tags=None, location=None,
                       security_provider_name=None, branch_to_branch_traffic=None,
                       office365_category=None, disable_vpn_encryption=None,
                       vwan_type=None):
    client = network_client_factory(cmd.cli_ctx).virtual_wans
    VirtualWAN = cmd.get_models('VirtualWAN')
    wan = VirtualWAN(
        tags=tags,
        location=location,
        disable_vpn_encryption=disable_vpn_encryption,
        security_provider_name=security_provider_name,
        allow_branch_to_branch_traffic=branch_to_branch_traffic,
        office365_local_breakout_category=office365_category,
        type=vwan_type
    )
    return client.begin_create_or_update(resource_group_name, virtual_wan_name, wan)


def update_virtual_wan(instance, tags=None, security_provider_name=None, branch_to_branch_traffic=None,
                       office365_category=None, disable_vpn_encryption=None, vwan_type=None):
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
        c.update_param('security_provider_name', security_provider_name, False)
        c.update_param('allow_branch_to_branch_traffic', branch_to_branch_traffic, False)
        c.update_param('office365_local_breakout_category', office365_category, False)
        c.update_param('disable_vpn_encryption', disable_vpn_encryption, False)
        c.update_param('type', vwan_type, False)
    return instance


def list_virtual_wans(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'virtual_wans', resource_group_name)
# endregion


# region VirtualHubs
def get_effective_virtual_hub_routes(cmd, resource_group_name, virtual_hub_name,
                                     virtual_wan_resource_type=None, resource_id=None, no_wait=False):
    parameters = None
    EffectiveRoutesParameters = cmd.get_models('EffectiveRoutesParameters')
    if virtual_wan_resource_type is not None or resource_id is not None:
        parameters = EffectiveRoutesParameters(
            virtual_wan_resource_type=virtual_wan_resource_type,
            resource_id=resource_id
        )

    client = network_client_factory(cmd.cli_ctx).virtual_hubs

    def raw(response, *_):
        import json
        response = response.http_response
        return json.loads(response.body())

    return sdk_no_wait(
        no_wait,
        client.begin_get_effective_virtual_hub_routes,
        resource_group_name,
        virtual_hub_name,
        parameters,
        cls=raw
    )


def update_hub_vnet_connection(instance, cmd, associated_route_table=None, propagated_route_tables=None, labels=None,
                               associated_inbound_routemap=None, associated_outbound_routemap=None):
    SubResource = cmd.get_models('SubResource')

    ids = [SubResource(id=propagated_route_table) for propagated_route_table in
           propagated_route_tables] if propagated_route_tables else None  # pylint: disable=line-too-long
    associated_route_table = SubResource(id=associated_route_table) if associated_route_table else None
    associated_inbound_routemap = SubResource(id=associated_inbound_routemap) if associated_inbound_routemap else None
    associated_outbound_routemap = SubResource(id=associated_outbound_routemap) if associated_outbound_routemap else None
    with UpdateContext(instance) as c:
        c.set_param('routing_configuration.associated_route_table', associated_route_table, False)
        c.set_param('routing_configuration.propagated_route_tables.labels', labels, False)
        c.set_param('routing_configuration.propagated_route_tables.ids', ids, False)
        c.set_param('routing_configuration.inbound_route_map', associated_inbound_routemap, False)
        c.set_param('routing_configuration.outbound_route_map', associated_outbound_routemap, False)

    return instance


# pylint: disable=too-many-locals
class VHubConnectionCreate(_VHubConnectionCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZStrArg, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.propagated_route_tables = AAZListArg(
            options=["--propagated-route-tables", "--propagated"],
            arg_group="Routing Configuration",
            help="Space-separated list of resource ID of propagated route tables.",
            is_preview=True
        )
        args_schema.propagated_route_tables.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                         "/virtualHubs/{vhub_name}/hubRouteTables/{}"
            )
        )
        args_schema.address_prefixes = AAZListArg(
            options=["--address-prefixes"],
            arg_group="Routing Configuration",
            help="Space-separated list of all address prefixes.",
            is_preview=True
        )
        args_schema.address_prefixes.Element = AAZStrArg()
        args_schema.remote_vnet._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                     "/virtualNetworks/{}"
        )
        args_schema.next_hop = AAZStrArg(
            options=["--next-hop"],
            arg_group="Routing Configuration",
            help="IP address of the next hop.",
            is_preview=True
        )
        args_schema.route_name = AAZStrArg(
            options=["--route-name"],
            arg_group="Routing Configuration",
            help="Name of the static route that is unique within a VNet route.",
            is_preview=True
        )
        args_schema.route_tables._registered = False
        args_schema.static_routes._registered = False
        args_schema.remote_vnet._required = True

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.route_tables = assign_aaz_list_arg(
            args.route_tables,
            args.propagated_route_tables,
            element_transformer=lambda _, route_table_id: {"id": route_table_id}
        )
        if has_value(args.route_name):
            static_route = {
                "route_name": args.route_name,
                "address_prefixes": args.address_prefixes if has_value(args.address_prefixes) else None,
                "next_hop": args.next_hop if has_value(args.next_hop) else None
            }
            args.static_routes = [static_route]


class VHubConnectionUpdate(_VHubConnectionUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.propagated_route_tables = AAZListArg(
            options=["--propagated-route-tables", "--propagated"],
            arg_group="Routing Configuration",
            help="Space-separated list of resource ID of propagated route tables.",
            nullable=True,
            is_preview=True
        )
        args_schema.propagated_route_tables.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                         "/virtualHubs/{vhub_name}/hubRouteTables/{}"
            ),
            nullable=True
        )
        args_schema.route_tables._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.route_tables = assign_aaz_list_arg(
            args.route_tables,
            args.propagated_route_tables,
            element_transformer=lambda _, route_table_id: {"id": route_table_id}
        )


def _bgp_connections_client(cli_ctx):
    return cf_virtual_hub_bgpconnections(cli_ctx=cli_ctx, _=None)


def create_hub_vnet_bgpconnection(cmd, client, resource_group_name, virtual_hub_name, connection_name,
                                  virtual_hub_connection=None, peer_asn=None, peer_ip=None, no_wait=False):

    (BgpConnection, SubResource) = cmd.get_models('BgpConnection', 'SubResource')
    connection = BgpConnection(
        name=connection_name,
        peer_asn=peer_asn,
        peer_ip=peer_ip,
        hub_virtual_network_connection=SubResource(id=virtual_hub_connection) if virtual_hub_connection else None
    )
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name,
                       virtual_hub_name, connection_name, connection)


def update_hub_vnet_bgpconnection(cmd, instance, resource_group_name, virtual_hub_name, connection_name,
                                  virtual_hub_connection=None, peer_asn=None, peer_ip=None):
    SubResource = cmd.get_models('SubResource')
    if peer_asn is not None:
        instance.peer_asn = peer_asn
    if peer_ip is not None:
        instance.peer_ip = peer_ip
    if virtual_hub_connection is not None:
        instance.hub_virtual_network_connection = SubResource(id=virtual_hub_connection)
    return instance


def list_hub_vnet_bgpconnection(cmd, client, resource_group_name, virtual_hub_name):
    client = _bgp_connections_client(cmd.cli_ctx)
    return client.list(resource_group_name=resource_group_name, virtual_hub_name=virtual_hub_name)


# pylint: disable=inconsistent-return-statements
def add_hub_route(cmd, resource_group_name, virtual_hub_name, address_prefixes, next_hop_ip_address, no_wait=False):
    VirtualHubRoute = cmd.get_models('VirtualHubRoute')
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    route = VirtualHubRoute(address_prefixes=address_prefixes, next_hop_ip_address=next_hop_ip_address)
    hub.route_table.routes.append(route)
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, virtual_hub_name, hub)
    try:
        return poller.result().route_table.routes
    except AttributeError:
        return


def list_hub_routes(cmd, resource_group_name, virtual_hub_name):
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    return hub.route_table.routes


def reset_hub_routes(cmd, resource_group_name, virtual_hub_name, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    if hub.routing_state == 'Failed':
        logger.warning('Reset virtual hub')
        poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                             resource_group_name, virtual_hub_name, hub)
        try:
            return poller.result().route_table.routes
        except AttributeError:
            return
    logger.warning("Virtual Hub's routing state is not `failed`. Skip this command")


# pylint: disable=inconsistent-return-statements
def remove_hub_route(cmd, resource_group_name, virtual_hub_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).virtual_hubs
    hub = client.get(resource_group_name, virtual_hub_name)
    try:
        hub.route_table.routes.pop(index - 1)
    except IndexError as exc:
        raise InvalidArgumentValueError(f"invalid index: {index}. Index can range from 1 to {len(hub.route_table.routes)}") from exc
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, virtual_hub_name, hub)
    try:
        return poller.result().route_table.routes
    except AttributeError:
        return


# pylint: disable=inconsistent-return-statements
def create_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name, destination_type=None,
                            destinations=None, next_hop_type=None, next_hop=None, route_name=None, labels=None,
                            no_wait=False):
    HubRouteTable, HubRoute = cmd.get_models('HubRouteTable', 'HubRoute')
    route_table = HubRouteTable(labels=labels)

    if route_name is not None:
        route = HubRoute(name=route_name,
                         destination_type=destination_type,
                         destinations=destinations,
                         next_hop_type=next_hop_type,
                         next_hop=next_hop)
        route_table.routes = [route]

    client = _v3_route_table_client(cmd.cli_ctx)

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name,
                       virtual_hub_name, route_table_name, route_table)


def update_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name, labels=None, no_wait=False):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    client = _v3_route_table_client(cmd.cli_ctx)
    route_table.labels = labels

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name,
                       virtual_hub_name, route_table_name, route_table)


def get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name):
    from azure.core.exceptions import ResourceNotFoundError
    try:
        return _v3_route_table_client(cmd.cli_ctx)\
            .get(resource_group_name, virtual_hub_name, route_table_name)  # Get v3 route table first.
    except ResourceNotFoundError:
        return _v2_route_table_client(cmd.cli_ctx)\
            .get(resource_group_name, virtual_hub_name, route_table_name)  # Get v2 route table.


def delete_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name, no_wait=False):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    client = _route_table_client(cmd.cli_ctx, route_table)

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, virtual_hub_name, route_table_name)


def list_vhub_route_tables(cmd, resource_group_name, virtual_hub_name):
    v2_route_tables = _v2_route_table_client(cmd.cli_ctx).list(resource_group_name, virtual_hub_name)
    v3_route_tables = _v3_route_table_client(cmd.cli_ctx).list(resource_group_name, virtual_hub_name)

    all_route_tables = list(v2_route_tables) + list(v3_route_tables)
    return all_route_tables


# pylint: disable=inconsistent-return-statements
def add_hub_routetable_route(cmd, resource_group_name, virtual_hub_name, route_table_name, destination_type,
                             destinations, next_hop_type, next_hop=None, route_name=None, no_wait=False):
    route_table = get_vhub_route_table(cmd, resource_group_name, virtual_hub_name, route_table_name)
    if next_hop is None or route_name is None:
        raise ArgumentUsageError(
            'Usage error: --next-hop and --route-name must be provided as you are adding route to v3 route table.')

    client = _v3_route_table_client(cmd.cli_ctx)
    HubRoute = cmd.get_models('HubRoute')
    route = HubRoute(name=route_name,
                     destination_type=destination_type,
                     destinations=destinations,
                     next_hop_type=next_hop_type,
                     next_hop=next_hop)
    route_table.routes.append(route)

    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
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
    except IndexError as exc:
        raise InvalidArgumentValueError(f"invalid index: {index}. Index can range from 1 to {len(route_table.routes)}") from exc

    client = _route_table_client(cmd.cli_ctx, route_table)
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
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
    return network_client_factory(cli_ctx).virtual_hub_route_table_v2_s


def _v3_route_table_client(cli_ctx):
    return network_client_factory(cli_ctx).hub_route_tables
# endregion


# region VpnGateways
def update_vpn_gateway_connection(instance, cmd, associated_route_table=None, propagated_route_tables=None,
                                  labels=None, associated_inbound_routemap=None, associated_outbound_routemap=None):
    SubResource = cmd.get_models('SubResource')

    ids = [SubResource(id=propagated_route_table) for propagated_route_table in
           propagated_route_tables] if propagated_route_tables else None
    associated_route_table = SubResource(id=associated_route_table) if associated_route_table else None
    associated_inbound_routemap = SubResource(id=associated_inbound_routemap) if associated_inbound_routemap else None
    associated_outbound_routemap = SubResource(id=associated_outbound_routemap) if associated_outbound_routemap else None
    with UpdateContext(instance) as c:
        c.set_param('routing_configuration.associated_route_table', associated_route_table, False)
        c.set_param('routing_configuration.propagated_route_tables.labels', labels, False)
        c.set_param('routing_configuration.propagated_route_tables.ids', ids, False)
        c.set_param('routing_configuration.inbound_route_map', associated_inbound_routemap, False)
        c.set_param('routing_configuration.outbound_route_map', associated_outbound_routemap, False)

    return instance


def create_vpn_gateway_connection(cmd, resource_group_name, gateway_name, connection_name,
                                  remote_vpn_site, vpn_site_link=None, routing_weight=None, protocol_type=None,
                                  connection_bandwidth=None, shared_key=None, enable_bgp=None,
                                  enable_rate_limiting=None, enable_internet_security=None, no_wait=False,
                                  associated_route_table=None, propagated_route_tables=None, with_link=None, labels=None,
                                  associated_inbound_routemap=None, associated_outbound_routemap=None):
    client = network_client_factory(cmd.cli_ctx).vpn_connections
    (VpnConnection,
     SubResource,
     RoutingConfiguration,
     PropagatedRouteTable,
     VpnSiteLinkConnection) = cmd.get_models('VpnConnection',
                                             'SubResource',
                                             'RoutingConfiguration',
                                             'PropagatedRouteTable',
                                             'VpnSiteLinkConnection')

    propagated_route_tables = PropagatedRouteTable(
        labels=labels,
        ids=[SubResource(id=propagated_route_table) for propagated_route_table in propagated_route_tables] if propagated_route_tables else None  # pylint: disable=line-too-long
    )
    routing_configuration = RoutingConfiguration(
        associated_route_table=SubResource(id=associated_route_table) if associated_route_table else None,
        propagated_route_tables=propagated_route_tables,
        inbound_route_map=SubResource(id=associated_inbound_routemap) if associated_inbound_routemap else None,
        outbound_route_map=SubResource(id=associated_outbound_routemap) if associated_outbound_routemap else None
    )

    conn = VpnConnection(
        name=connection_name,
        remote_vpn_site=SubResource(id=remote_vpn_site),
        protocol_type=protocol_type,
        enable_internet_security=enable_internet_security,
        routing_configuration=routing_configuration
    )

    if with_link:
        link_conn = VpnSiteLinkConnection(
            name=connection_name,
            routing_weight=routing_weight,
            vpn_site_link=SubResource(id=vpn_site_link),
            connection_bandwidth=connection_bandwidth,
            shared_key=shared_key,
            enable_bgp=enable_bgp,
            enable_rate_limiting=enable_rate_limiting,
        )
        conn.vpn_link_connections = [link_conn]
    else:
        conn.routing_weight = routing_weight
        conn.connection_bandwidth = connection_bandwidth
        conn.shared_key = shared_key
        conn.enable_bgp = enable_bgp
        conn.enable_rate_limiting = enable_rate_limiting

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, gateway_name, connection_name, conn)


# pylint: disable=inconsistent-return-statements
def add_vpn_gateway_connection_ipsec_policy(cmd, resource_group_name, gateway_name, connection_name,
                                            sa_life_time_seconds, sa_data_size_kilobytes, ipsec_encryption,
                                            ipsec_integrity, ike_encryption, ike_integrity, dh_group, pfs_group,
                                            no_wait=False):
    IpsecPolicy = cmd.get_models('IpsecPolicy')
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    gateway = client.get(resource_group_name, gateway_name)
    conn = _find_item_at_path(gateway, f"connections.{connection_name}")

    if conn.ipsec_policies is None:
        conn.ipsec_policies = []
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
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, gateway_name, gateway)
    try:
        return _get_property(poller.result().connections, connection_name)
    except AttributeError:
        return


def list_vpn_conn_ipsec_policies(cmd, resource_group_name, gateway_name, connection_name):
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    gateway = client.get(resource_group_name, gateway_name)
    conn = _find_item_at_path(gateway, f"connections.{connection_name}")
    return conn.ipsec_policies


# pylint: disable=inconsistent-return-statements
def remove_vpn_conn_ipsec_policy(cmd, resource_group_name, gateway_name, connection_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_gateways
    gateway = client.get(resource_group_name, gateway_name)
    conn = _find_item_at_path(gateway, f"connections.{connection_name}")
    try:
        conn.ipsec_policies.pop(index - 1)
    except IndexError as exc:
        raise InvalidArgumentValueError(f"invalid index: {index}. Index can range from 1 to {len(conn.ipsec_policies)}") from exc
    _upsert(gateway, 'connections', conn, 'name', warn=False)
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, gateway_name, gateway)
    try:
        return _get_property(poller.result().connections, connection_name)
    except AttributeError:
        return


def add_vpn_gateway_connection_vpn_site_link_conn(cmd, resource_group_name, gateway_name, connection_name,
                                                  vpn_site_link_conn_name, vpn_site_link, routing_weight=None, vpn_link_connection_mode=None,
                                                  vpn_connection_protocol_type=None, connection_bandwidth=None, shared_key=None, enable_bgp=None, enable_rate_limiting=None,
                                                  use_policy_based_traffic_selectors=None, use_local_azure_ip_address=None, no_wait=False):
    SubResource, VpnSiteLinkConnection = cmd.get_models('SubResource', 'VpnSiteLinkConnection')
    client = network_client_factory(cmd.cli_ctx).vpn_connections
    conn = client.get(resource_group_name, gateway_name, connection_name)

    if conn.vpn_link_connections is None:
        conn.vpn_link_connections = []
    conn.vpn_link_connections.append(
        VpnSiteLinkConnection(
            name=vpn_site_link_conn_name,
            routing_weight=routing_weight,
            vpn_site_link=SubResource(id=vpn_site_link),
            vpn_link_connection_mode=vpn_link_connection_mode,
            vpn_connection_protocol_type=vpn_connection_protocol_type,
            connection_bandwidth=connection_bandwidth,
            shared_key=shared_key,
            enable_bgp=enable_bgp,
            enable_rate_limiting=enable_rate_limiting,
            use_policy_based_traffic_selectors=use_policy_based_traffic_selectors,
            use_local_azure_ip_address=use_local_azure_ip_address
        )
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name, gateway_name, connection_name, conn)


def list_vpn_conn_vpn_site_link_conn(cmd, resource_group_name, gateway_name, connection_name):
    client = network_client_factory(cmd.cli_ctx).vpn_connections
    conn = client.get(resource_group_name, gateway_name, connection_name)
    return conn.vpn_link_connections


def remove_vpn_gateway_connection_vpn_site_link_conn(cmd, resource_group_name, gateway_name, connection_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_connections
    conn = client.get(resource_group_name, gateway_name, connection_name)
    try:
        conn.vpn_link_connections.pop(index - 1)
    except IndexError as exc:
        raise InvalidArgumentValueError(f"invalid index: {index}. Index can range from 1 to {len(conn.vpn_link_connections)}") from exc
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name, gateway_name, connection_name, conn)


# pylint: disable=inconsistent-return-statements
def add_vpn_gateway_connection_link_ipsec_policy(cmd, resource_group_name, gateway_name, connection_name, vpn_site_link_conn_name,
                                                 sa_life_time_seconds, sa_data_size_kilobytes, ipsec_encryption,
                                                 ipsec_integrity, ike_encryption, ike_integrity, dh_group, pfs_group,
                                                 no_wait=False):
    IpsecPolicy = cmd.get_models('IpsecPolicy')
    client = network_client_factory(cmd.cli_ctx).vpn_connections
    vpn_conn = client.get(resource_group_name, gateway_name, connection_name)
    conn = _find_item_at_path(vpn_conn, f"vpn_link_connections.{vpn_site_link_conn_name}")

    if conn.ipsec_policies is None:
        conn.ipsec_policies = []
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

    _upsert(vpn_conn, 'vpn_link_connections', conn, 'name', warn=False)
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, gateway_name, connection_name, vpn_conn)
    try:
        return _get_property(poller.result().vpn_link_connections, vpn_site_link_conn_name)
    except AttributeError:
        return


def list_vpn_conn_link_ipsec_policies(cmd, resource_group_name, gateway_name, connection_name, vpn_site_link_conn_name):
    client = network_client_factory(cmd.cli_ctx).vpn_connections
    vpn_conn = client.get(resource_group_name, gateway_name, connection_name)
    conn = _find_item_at_path(vpn_conn, f"vpn_link_connections.{vpn_site_link_conn_name}")
    return conn.ipsec_policies


# pylint: disable=inconsistent-return-statements
def remove_vpn_conn_link_ipsec_policy(cmd, resource_group_name, gateway_name, connection_name, vpn_site_link_conn_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_connections
    vpn_conn = client.get(resource_group_name, gateway_name, connection_name)
    conn = _find_item_at_path(vpn_conn, f"vpn_link_connections.{vpn_site_link_conn_name}")

    try:
        conn.ipsec_policies.pop(index - 1)
    except IndexError as exc:
        raise InvalidArgumentValueError(f"invalid index: {index}. Index can range from 1 to {len(conn.ipsec_policies)}") from exc
    _upsert(vpn_conn, 'vpn_link_connections', conn, 'name', warn=False)
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, gateway_name, connection_name, vpn_conn)
    try:
        return _get_property(poller.result().vpn_link_connections, vpn_site_link_conn_name)
    except AttributeError:
        return


# endregion


# region VpnSites
def create_vpn_site(cmd, resource_group_name, vpn_site_name, ip_address,
                    asn=None, bgp_peering_address=None,
                    virtual_wan=None, location=None, tags=None,
                    site_key=None, address_prefixes=None, is_security_site=None,
                    device_vendor=None, device_model=None, link_speed=None,
                    peer_weight=None, with_link=None, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_sites
    VpnSite, VpnSiteLink, SubResource = cmd.get_models('VpnSite', 'VpnSiteLink', 'SubResource')

    site = VpnSite(
        location=location,
        tags=tags,
        is_security_site=is_security_site,
        site_key=site_key,
        virtual_wan=SubResource(id=virtual_wan) if virtual_wan else None,
        address_space={'addressPrefixes': address_prefixes},
        device_properties={
            'deviceVendor': device_vendor,
            'deviceModel': device_model,
            'linkSpeedInMbps': link_speed
        }
    )
    if with_link:
        link = VpnSiteLink(
            name=vpn_site_name,
            bgp_properties={
                'asn': asn,
                'bgpPeeringAddress': bgp_peering_address,
                'peerWeight': peer_weight
            },
            ip_address=ip_address,
        )
        if not any([asn, bgp_peering_address, peer_weight]):
            link.bgp_properties = None

        site.vpn_site_links = [link]
    else:
        if not any([asn, bgp_peering_address, peer_weight]):
            site.bgp_properties = None
        else:
            site.bgp_properties = {
                'asn': asn,
                'bgpPeeringAddress': bgp_peering_address,
                'peerWeight': peer_weight
            }
        site.ip_address = ip_address
    return sdk_no_wait(no_wait, client.begin_create_or_update,
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


def add_vpn_site_link(cmd, resource_group_name, vpn_site_name, vpn_site_link_name, ip_address, fqdn=None,
                      link_provider_name=None, link_speed_in_mbps=None, asn=None, bgp_peering_address=None, no_wait=False):
    VpnSiteLink = cmd.get_models('VpnSiteLink')
    client = network_client_factory(cmd.cli_ctx).vpn_sites
    vpn_site = client.get(resource_group_name, vpn_site_name)

    if vpn_site.vpn_site_links is None:
        vpn_site.vpn_site_links = []

    vpn_site.vpn_site_links.append(
        VpnSiteLink(
            name=vpn_site_link_name,
            ip_address=ip_address,
            fqdn=fqdn,
            bgp_properties={
                'asn': asn,
                'bgp_peering_address': bgp_peering_address
            },
            link_properites={
                'link_provider_name': link_provider_name,
                'link_speed_in_mbps': link_speed_in_mbps
            }
        )
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name, vpn_site_name, vpn_site)


def remove_vpn_site_link(cmd, resource_group_name, vpn_site_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_sites
    vpn_site = client.get(resource_group_name, vpn_site_name)
    try:
        vpn_site.vpn_site_links.pop(index - 1)
    except IndexError as exc:
        raise InvalidArgumentValueError(f"invalid index: {index}. Index can range from 1 to {len(vpn_site.vpn_site_links)}") from exc
    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name, vpn_site_name, vpn_site)


def list_vpn_site_link(cmd, resource_group_name, vpn_site_name):
    client = network_client_factory(cmd.cli_ctx).vpn_sites
    vpn_site = client.get(resource_group_name, vpn_site_name)
    return vpn_site.vpn_site_links


# endregion


# region VPN server configuarions
# pylint: disable=line-too-long
def create_vpn_server_config(cmd, resource_group_name, vpn_server_configuration_name, location=None,
                             vpn_protocols=None, vpn_auth_types=None,
                             vpn_client_root_certs=None, vpn_client_revoked_certs=None,
                             radius_servers=None, radius_client_root_certs=None, radius_server_root_certs=None,
                             aad_tenant=None, aad_audience=None, aad_issuer=None, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_server_configurations
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

    return sdk_no_wait(no_wait, client.begin_create_or_update,
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
    client = network_client_factory(cmd.cli_ctx).vpn_server_configurations
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def add_vpn_server_config_ipsec_policy(cmd, resource_group_name, vpn_server_configuration_name,
                                       sa_life_time_seconds, sa_data_size_kilobytes, ipsec_encryption,
                                       ipsec_integrity, ike_encryption, ike_integrity, dh_group, pfs_group,
                                       no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_server_configurations
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
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, vpn_server_configuration_name, vpn_server_config)
    if no_wait:
        return poller
    from azure.cli.core.commands import LongRunningOperation
    return LongRunningOperation(cmd.cli_ctx)(poller).vpn_client_ipsec_policies


def list_vpn_server_config_ipsec_policies(cmd, resource_group_name, vpn_server_configuration_name):
    client = network_client_factory(cmd.cli_ctx).vpn_server_configurations
    vpn_server_config = client.get(resource_group_name, vpn_server_configuration_name)
    return vpn_server_config.vpn_client_ipsec_policies


# pylint: disable=inconsistent-return-statements
def remove_vpn_server_config_ipsec_policy(cmd, resource_group_name, vpn_server_configuration_name, index, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).vpn_server_configurations
    vpn_server_config = client.get(resource_group_name, vpn_server_configuration_name)
    try:
        vpn_server_config.vpn_client_ipsec_policies.pop(index)
    except IndexError as exc:
        raise InvalidArgumentValueError(f"invalid index: {index}. Index can range from 0 to {len(vpn_server_config.vpn_client_ipsec_policies)}") from exc
    poller = sdk_no_wait(no_wait, client.begin_create_or_update,
                         resource_group_name, vpn_server_configuration_name, vpn_server_config)
    if no_wait:
        return poller
    from azure.cli.core.commands import LongRunningOperation
    return LongRunningOperation(cmd.cli_ctx)(poller).vpn_client_ipsec_policies


def create_p2s_vpn_gateway(cmd, resource_group_name, gateway_name, virtual_hub,
                           scale_unit, location=None, tags=None, p2s_conn_config_name='P2SConnectionConfigDefault',
                           vpn_server_config=None, address_space=None, associated_route_table=None,
                           propagated_route_tables=None, labels=None, associated_inbound_routemap=None,
                           associated_outbound_routemap=None, no_wait=False):
    client = network_client_factory(cmd.cli_ctx).p2_svpn_gateways
    (P2SVpnGateway,
     SubResource,
     P2SConnectionConfiguration,
     AddressSpace,
     RoutingConfiguration,
     PropagatedRouteTable) = cmd.get_models('P2SVpnGateway',
                                            'SubResource',
                                            'P2SConnectionConfiguration',
                                            'AddressSpace',
                                            'RoutingConfiguration',
                                            'PropagatedRouteTable')

    propagated_route_tables = PropagatedRouteTable(
        labels=labels,
        ids=[SubResource(id=propagated_route_table) for propagated_route_table in propagated_route_tables] if propagated_route_tables else None
    )
    routing_configuration = RoutingConfiguration(
        associated_route_table=SubResource(id=associated_route_table) if associated_route_table else None,
        propagated_route_tables=propagated_route_tables,
        inbound_route_map=SubResource(id=associated_inbound_routemap) if associated_inbound_routemap else None,
        outbound_route_map=SubResource(id=associated_outbound_routemap) if associated_outbound_routemap else None
    )
    gateway = P2SVpnGateway(
        location=location,
        tags=tags,
        virtual_hub=SubResource(id=virtual_hub) if virtual_hub else None,
        vpn_gateway_scale_unit=scale_unit,
        vpn_server_configuration=SubResource(id=vpn_server_config) if vpn_server_config else None,
        p2_s_connection_configurations=[
            P2SConnectionConfiguration(
                vpn_client_address_pool=AddressSpace(
                    address_prefixes=address_space
                ),
                name=p2s_conn_config_name,
                routing_configuration=routing_configuration
            )
        ]
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, gateway_name, gateway)


def update_p2s_vpn_gateway(instance, cmd, tags=None, scale_unit=None,
                           vpn_server_config=None, address_space=None, p2s_conn_config_name=None,
                           associated_route_table=None, propagated_route_tables=None, labels=None,
                           associated_inbound_routemap=None, associated_outbound_routemap=None):
    SubResource = cmd.get_models('SubResource')
    associated_inbound_routemap = SubResource(id=associated_inbound_routemap) if associated_inbound_routemap else None
    associated_outbound_routemap = SubResource(id=associated_outbound_routemap) if associated_outbound_routemap else None
    with UpdateContext(instance) as c:
        c.set_param('tags', tags, True)
        c.set_param('vpn_gateway_scale_unit', scale_unit, False)
        c.set_param('vpn_server_configuration', SubResource(id=vpn_server_config) if vpn_server_config else None, True)
    p2_sconnection_configurations = getattr(instance, 'p2_s_connection_configurations')
    if p2_sconnection_configurations:
        with UpdateContext(p2_sconnection_configurations[0]) as c:
            c.set_param('vpn_client_address_pool.address_prefixes', address_space, False)
            c.set_param('name', p2s_conn_config_name, False)
            c.set_param('routing_configuration.associated_route_table',
                        SubResource(id=associated_route_table) if associated_route_table else None, False)
            c.set_param('routing_configuration.propagated_route_tables.labels', labels, False)
            c.set_param('routing_configuration.propagated_route_tables.ids',
                        [SubResource(id=propagated_route_table) for propagated_route_table in
                         propagated_route_tables] if propagated_route_tables else None, False)
            c.set_param('routing_configuration.inbound_route_map', associated_inbound_routemap, False)
            c.set_param('routing_configuration.outbound_route_map', associated_outbound_routemap, False)

    return instance


def list_p2s_vpn_gateways(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).p2_svpn_gateways
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def generate_vpn_profile(cmd, resource_group_name, gateway_name, authentication_method=None):
    client = network_client_factory(cmd.cli_ctx).p2_svpn_gateways
    P2SVpnProfileParameters = cmd.get_models('P2SVpnProfileParameters')
    parameters = P2SVpnProfileParameters(authentication_method=authentication_method)
    return client.begin_generate_vpn_profile(
        resource_group_name,
        gateway_name,
        parameters
    )


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


class VPNGatewayNatRuleCreate(_VPNGatewayNatRuleCreate):
    def _output(self, *args, **kwargs):
        from azure.cli.core.aaz import AAZUndefined
        if has_value(self.ctx.vars.instance):
            nat_rule = self.ctx.vars.instance.to_serialized_data()
            if 'type' in nat_rule:
                nat_rule['type'] = AAZUndefined
            self.ctx.vars.instance = nat_rule
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result


class VPNGatewayNatRuleShow(_VPNGatewayNatRuleShow):
    def _output(self, *args, **kwargs):
        from azure.cli.core.aaz import AAZUndefined
        if has_value(self.ctx.vars.instance):
            nat_rule = self.ctx.vars.instance.to_serialized_data()
            if 'type' in nat_rule:
                nat_rule['type'] = AAZUndefined
            self.ctx.vars.instance = nat_rule
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result


class VPNGatewayNatRuleList(_VPNGatewayNatRuleList):
    def _output(self, *args, **kwargs):
        from azure.cli.core.aaz import AAZUndefined
        if has_value(self.ctx.vars.instance):
            nat_rules = self.ctx.vars.instance.value.to_serialized_data()
            for nat_rule in nat_rules:
                if 'type' in nat_rule:
                    nat_rule['type'] = AAZUndefined
            self.ctx.vars.instance.value = nat_rules
        result = self.deserialize_output(self.ctx.vars.instance.value, client_flatten=True)
        next_link = self.deserialize_output(self.ctx.vars.instance.next_link)
        return result, next_link


class VPNGatewayNatRuleUpdate(_VPNGatewayNatRuleUpdate):
    def _output(self, *args, **kwargs):
        from azure.cli.core.aaz import AAZUndefined
        if has_value(self.ctx.vars.instance):
            nat_rule = self.ctx.vars.instance.to_serialized_data()
            if 'type' in nat_rule:
                nat_rule['type'] = AAZUndefined
            self.ctx.vars.instance = nat_rule
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result
# endregion
