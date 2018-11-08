# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._client_factory import network_client_factory


def create_vnet_tap(cmd, resource_group_name, tap_name, destination, port=None, tags=None, location=None):
    from msrestazure.tools import parse_resource_id
    supported_types = ['loadBalancers', 'networkInterfaces']
    client = network_client_factory(cmd.cli_ctx).virtual_network_taps
    SubResource, VTAP = cmd.get_models('SubResource', 'VirtualNetworkTap')
    dest_type = parse_resource_id(destination).get('type', None)
    if not dest_type or dest_type not in supported_types:
        from knack.util import CLIError
        raise CLIError('Unable to parse destination resource ID. Supply an IP configuration ID '
                       'for one of the following resource types: {}'.format(supported_types))
    vtap = VTAP(
        tags=tags,
        location=location,
        destination_port=port,
        destination_load_balancer_front_end_ip_configuration=SubResource(id=destination)
        if dest_type == 'loadBalancers' else None,
        destination_network_interface_ip_configuration=SubResource(id=destination)
        if dest_type == 'networkInterfaces' else None
    )
    return client.create_or_update(resource_group_name, tap_name, vtap)


def list_vnet_taps(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).virtual_network_taps
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_all()


def create_vtap_config(cmd, resource_group_name, network_interface_name, vtap_config_name, vnet_tap):
    client = network_client_factory(cmd.cli_ctx).network_interface_tap_configurations
    SubResource, NetworkInterfaceTapConfiguration = cmd.get_models(
        'SubResource', 'NetworkInterfaceTapConfiguration')
    vtap_config = NetworkInterfaceTapConfiguration(
        virtual_network_tap=SubResource(id=vnet_tap)
    )
    return client.create_or_update(resource_group_name, network_interface_name, vtap_config_name, vtap_config)


def list_nics(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).network_interfaces
    if resource_group_name:
        return client.list(resource_group_name)
    return client.list_all()
