# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

from ._client_factory import network_client_factory

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


# pylint: disable=unused-argument
def create_express_route_connection(cmd, resource_group_name, express_route_gateway_name, connection_name,
                                    peering, circuit_name=None, authorization_key=None, routing_weight=None):
    ExpressRouteConnection, SubResource = cmd.get_models('ExpressRouteConnection', 'SubResource')
    client = network_client_factory(cmd.cli_ctx).express_route_connections
    connection = ExpressRouteConnection(
        name=connection_name,
        express_route_circuit_peering=SubResource(id=peering) if peering else None,
        authorization_key=authorization_key,
        routing_weight=routing_weight
    )
    return client.create_or_update(resource_group_name, express_route_gateway_name, connection_name, connection)


# pylint: disable=unused-argument
def update_express_route_connection(instance, cmd, circuit_name=None, peering=None, authorization_key=None,
                                    routing_weight=None):
    SubResource = cmd.get_models('SubResource')
    if peering is not None:
        instance.express_route_connection_id = SubResource(id=peering)
    if authorization_key is not None:
        instance.authorization_key = authorization_key
    if routing_weight is not None:
        instance.routing_weight = routing_weight
    return instance


def create_express_route_gateway(cmd, resource_group_name, express_route_gateway_name, location=None, tags=None,
                                 min_val=2, max_val=None, virtual_hub=None):
    ExpressRouteGateway, SubResource = cmd.get_models('ExpressRouteGateway', 'SubResource')
    client = network_client_factory(cmd.cli_ctx).express_route_gateways
    gateway = ExpressRouteGateway(
        location=location,
        tags=tags,
        virtual_hub=SubResource(id=virtual_hub) if virtual_hub else None
    )
    if min or max:
        gateway.auto_scale_configuration = {'bounds': {'min': min_val, 'max': max_val}}
    return client.create_or_update(resource_group_name, express_route_gateway_name, gateway)


def update_express_route_gateway(instance, cmd, tags=None, min_val=None, max_val=None):

    def _ensure_autoscale():
        if not instance.auto_scale_configuration:
            ExpressRouteGatewayPropertiesAutoScaleConfiguration, \
                ExpressRouteGatewayPropertiesAutoScaleConfigurationBounds = cmd.get_models(
                    'ExpressRouteGatewayPropertiesAutoScaleConfiguration',
                    'ExpressRouteGatewayPropertiesAutoScaleConfigurationBounds')
            instance.auto_scale_configuration = ExpressRouteGatewayPropertiesAutoScaleConfiguration(
                bounds=ExpressRouteGatewayPropertiesAutoScaleConfigurationBounds(min=min, max=max))

    if tags is not None:
        instance.tags = tags
    if min is not None:
        _ensure_autoscale()
        instance.auto_scale_configuration.bounds.min = min_val
    if max is not None:
        _ensure_autoscale()
        instance.auto_scale_configuration.bounds.max = max_val
    return instance


def list_express_route_gateways(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).express_route_gateways
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


def create_express_route_port(cmd, resource_group_name, express_route_port_name, location=None, tags=None,
                              peering_location=None, bandwidth_in_gbps=None, encapsulation=None):
    client = network_client_factory(cmd.cli_ctx).express_route_ports
    ExpressRoutePort = cmd.get_models('ExpressRoutePort')
    port = ExpressRoutePort(
        location=location,
        tags=tags,
        peering_location=peering_location,
        bandwidth_in_gbps=int(bandwidth_in_gbps),
        encapsulation=encapsulation
    )
    return client.create_or_update(resource_group_name, express_route_port_name, port)


def update_express_route_port(instance, tags=None, peering_location=None, bandwidth_in_gbps=None):
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
        c.update_param('peeringLocation', peering_location, False)
        c.update_param('bandwidthInGbps', int(bandwidth_in_gbps), False)
    return instance


def list_express_route_ports(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).express_route_ports
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


# override ER create to add ports
def create_express_route(cmd, circuit_name, resource_group_name, bandwidth_in_mbps, peering_location=None,
                         service_provider_name=None, location=None, tags=None, no_wait=False,
                         sku_family=None, sku_tier=None, allow_global_reach=None, express_route_port=None):
    ExpressRouteCircuit, ExpressRouteCircuitSku, ExpressRouteCircuitServiceProviderProperties, SubResource = \
        cmd.get_models(
            'ExpressRouteCircuit', 'ExpressRouteCircuitSku', 'ExpressRouteCircuitServiceProviderProperties',
            'SubResource')
    from azure.cli.core.util import sdk_no_wait
    client = network_client_factory(cmd.cli_ctx).express_route_circuits
    sku_name = '{}_{}'.format(sku_tier, sku_family)
    circuit = ExpressRouteCircuit(
        location=location, tags=tags,
        service_provider_properties=ExpressRouteCircuitServiceProviderProperties(
            service_provider_name=service_provider_name,
            peering_location=peering_location,
            bandwidth_in_mbps=bandwidth_in_mbps if not express_route_port else None),
        sku=ExpressRouteCircuitSku(name=sku_name, tier=sku_tier, family=sku_family),
        allow_global_reach=allow_global_reach,
        express_route_port=SubResource(id=express_route_port) if express_route_port else None,
        bandwidth_in_gbps=(int(bandwidth_in_mbps) / 1000) if express_route_port else None
    )
    if express_route_port:
        circuit.service_provider_properties = None
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, circuit_name, circuit)


def update_express_route(instance, cmd, bandwidth_in_mbps=None, peering_location=None,
                         service_provider_name=None, sku_family=None, sku_tier=None, tags=None,
                         allow_global_reach=None, express_route_port=None):

    if peering_location is not None:
        instance.service_provider_properties.peering_location = peering_location

    if service_provider_name is not None:
        instance.service_provider_properties.service_provider_name = service_provider_name

    if express_route_port is not None:
        SubResource = cmd.get_models('SubResource')
        instance.express_route_port = SubResource(id=express_route_port)
        instance.service_provider_properties = None

    if bandwidth_in_mbps is not None:
        if not instance.express_route_port:
            instance.service_provider_properties.bandwith_in_mbps = float(bandwidth_in_mbps)
        else:
            instance.bandwidth_in_gbps = (float(bandwidth_in_mbps) / 1000)

    if sku_family is not None:
        instance.sku.family = sku_family

    if sku_tier is not None:
        instance.sku.tier = sku_tier

    if tags is not None:
        instance.tags = tags

    if allow_global_reach is not None:
        instance.allow_global_reach = allow_global_reach

    return instance


def _generic_list(cli_ctx, operation_name, resource_group_name):
    ncf = network_client_factory(cli_ctx)
    operation_group = getattr(ncf, operation_name)
    if resource_group_name:
        return operation_group.list(resource_group_name)

    return operation_group.list_all()


def list_express_route_circuits(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'express_route_circuits', resource_group_name)
