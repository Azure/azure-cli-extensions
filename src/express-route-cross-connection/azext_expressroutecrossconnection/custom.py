# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._client_factory import network_client_factory


def list_express_route_cross_connections(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).express_route_cross_connections
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def update_express_route_cross_connection(instance, provisioning_state=None, notes=None):

    if notes is not None:
        instance.service_provider_notes = notes

    if provisioning_state is not None:
        instance.service_provider_provisioning_state = provisioning_state

    return instance


def create_express_route_cross_connection_peering(
        cmd, client, resource_group_name, cross_connection_name, peering_type, peer_asn, vlan_id,
        primary_peer_address_prefix, secondary_peer_address_prefix, shared_key=None,
        advertised_public_prefixes=None, customer_asn=None, routing_registry_name=None):
    (ExpressRouteCrossConnectionPeering, ExpressRouteCircuitPeeringConfig, ExpressRoutePeeringType) = \
        cmd.get_models('ExpressRouteCrossConnectionPeering', 'ExpressRouteCircuitPeeringConfig',
                       'ExpressRoutePeeringType')

    peering = ExpressRouteCrossConnectionPeering(
        peering_type=peering_type, peer_asn=peer_asn, vlan_id=vlan_id,
        primary_peer_address_prefix=primary_peer_address_prefix,
        secondary_peer_address_prefix=secondary_peer_address_prefix,
        shared_key=shared_key)

    if peering_type == ExpressRoutePeeringType.microsoft_peering.value:
        peering.microsoft_peering_config = ExpressRouteCircuitPeeringConfig(
            advertised_public_prefixes=advertised_public_prefixes,
            customer_asn=customer_asn,
            routing_registry_name=routing_registry_name)

    return client.create_or_update(resource_group_name, cross_connection_name, peering_type, peering)


def _create_or_update_ipv6_peering(cmd, config, primary_peer_address_prefix, secondary_peer_address_prefix,
                                   advertised_public_prefixes, customer_asn, routing_registry_name):
    if config:
        # update scenario
        if primary_peer_address_prefix:
            config.primary_peer_address_prefix = primary_peer_address_prefix

        if secondary_peer_address_prefix:
            config.secondary_peer_address_prefix = secondary_peer_address_prefix

        if advertised_public_prefixes:
            config.microsoft_peering_config.advertised_public_prefixes = advertised_public_prefixes

        if customer_asn:
            config.microsoft_peering_config.customer_asn = customer_asn

        if routing_registry_name:
            config.microsoft_peering_config.routing_registry_name = routing_registry_name
    else:
        # create scenario

        IPv6Config, MicrosoftPeeringConfig = cmd.get_models(
            'Ipv6ExpressRouteCircuitPeeringConfig', 'ExpressRouteCircuitPeeringConfig')
        microsoft_config = MicrosoftPeeringConfig(advertised_public_prefixes=advertised_public_prefixes,
                                                  customer_asn=customer_asn,
                                                  routing_registry_name=routing_registry_name)
        config = IPv6Config(primary_peer_address_prefix=primary_peer_address_prefix,
                            secondary_peer_address_prefix=secondary_peer_address_prefix,
                            microsoft_peering_config=microsoft_config)

    return config


def update_express_route_peering(cmd, instance, peer_asn=None, primary_peer_address_prefix=None,
                                 secondary_peer_address_prefix=None, vlan_id=None, shared_key=None,
                                 advertised_public_prefixes=None, customer_asn=None,
                                 routing_registry_name=None, ip_version='IPv4'):

    # update settings common to all peering types
    if peer_asn is not None:
        instance.peer_asn = peer_asn

    if vlan_id is not None:
        instance.vlan_id = vlan_id

    if shared_key is not None:
        instance.shared_key = shared_key

    if ip_version == 'IPv6':
        # update is the only way to add IPv6 peering options
        instance.ipv6_peering_config = _create_or_update_ipv6_peering(cmd, instance.ipv6_peering_config,
                                                                      primary_peer_address_prefix,
                                                                      secondary_peer_address_prefix,
                                                                      advertised_public_prefixes, customer_asn,
                                                                      routing_registry_name)
    else:
        # IPv4 Microsoft Peering (or non-Microsoft Peering)
        if primary_peer_address_prefix is not None:
            instance.primary_peer_address_prefix = primary_peer_address_prefix

        if secondary_peer_address_prefix is not None:
            instance.secondary_peer_address_prefix = secondary_peer_address_prefix

        try:
            if advertised_public_prefixes is not None:
                instance.microsoft_peering_config.advertised_public_prefixes = advertised_public_prefixes

            if customer_asn is not None:
                instance.microsoft_peering_config.customer_asn = customer_asn

            if routing_registry_name is not None:
                instance.microsoft_peering_config.routing_registry_name = routing_registry_name
        except AttributeError:
            from knack.util import CLIError
            raise CLIError('--advertised-public-prefixes, --customer-asn and --routing-registry-name are only '
                           'applicable for Microsoft Peering.')

    return instance
