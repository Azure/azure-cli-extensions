# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list, tags_type, get_location_type, get_three_state_flag, get_enum_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._validators import (
    validate_express_route_peering, validate_virtual_hub, validate_express_route_port,
    validate_circuit_bandwidth)


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    ExpressRoutePortsEncapsulation, ExpressRouteCircuitSkuFamily, ExpressRouteCircuitSkuTier = self.get_models(
        'ExpressRoutePortsEncapsulation', 'ExpressRouteCircuitSkuFamily', 'ExpressRouteCircuitSkuTier')

    er_circuit_name_type = CLIArgumentType(options_list=('--circuit-name',), metavar='NAME', help='ExpressRoute circuit name.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/expressRouteCircuits'))
    er_gateway_name_type = CLIArgumentType(options_list=('--gateway-name',), metavar='NAME', help='ExpressRoute gateway name.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/expressRouteGateways'))
    er_port_name_type = CLIArgumentType(options_list=('--port-name',), metavar='NAME', help='ExpressRoute port name.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/expressRoutePorts'))

    with self.argument_context('network express-route') as c:
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    with self.argument_context('network express-route gateway') as c:
        c.argument('express_route_gateway_name', er_gateway_name_type, options_list=['--name', '-n'])
        c.argument('min_val', help='Minimum number of scale units deployed for gateway.', type=int, arg_group='Autoscale')
        c.argument('max_val', help='Maximum number of scale units deployed for gateway.', type=int, arg_group='Autoscale')
        c.argument('virtual_hub', help='Name or ID of the virtual hub to associate with the gateway.', validator=validate_virtual_hub)

    with self.argument_context('network express-route gateway connection') as c:
        c.argument('express_route_gateway_name', er_gateway_name_type)
        c.argument('connection_name', options_list=['--name', '-n'], help='ExpressRoute connection name.', id_part='child_name_1')
        c.argument('routing_weight', help='Routing weight associated with the connection.', type=int)
        c.argument('authorization_key', help='Authorization key to establish the connection.')

    with self.argument_context('network express-route gateway connection', arg_group='Peering') as c:
        c.argument('peering', help='Name or ID of an ExpressRoute peering.', validator=validate_express_route_peering)
        c.argument('circuit_name', er_circuit_name_type, id_part=None)

    with self.argument_context('network express-route gateway connection list') as c:
        c.argument('express_route_gateway_name', er_gateway_name_type, id_part=None)

    with self.argument_context('network express-route port') as c:
        c.argument('express_route_port_name', er_port_name_type, options_list=['--name', '-n'])
        c.argument('encapsulation', arg_type=get_enum_type(ExpressRoutePortsEncapsulation), help='Encapsulation method on physical ports.')
        c.argument('bandwidth', help='Bandwidth of procured ports in Gbps', nargs='+')
        c.argument('peering_location', help='The name of the peering location that the port is mapped to physically.')

    with self.argument_context('network express-route port link') as c:
        c.argument('express_route_port_name', er_port_name_type)
        c.argument('link_name', options_list=['--name', '-n'], id_part='child_name_1')

    with self.argument_context('network express-route port link list') as c:
        c.argument('express_route_port_name', er_port_name_type, id_part=None)

    with self.argument_context('network express-route port location') as c:
        c.argument('location_name', options_list=['--location', '-l'])

    # region ExpressRoutes
    device_path_values = ['primary', 'secondary']
    sku_family_type = CLIArgumentType(help='Chosen SKU family of ExpressRoute circuit.', arg_type=get_enum_type(ExpressRouteCircuitSkuFamily), default=ExpressRouteCircuitSkuFamily.metered_data.value)
    sku_tier_type = CLIArgumentType(help='SKU Tier of ExpressRoute circuit.', arg_type=get_enum_type(ExpressRouteCircuitSkuTier), default=ExpressRouteCircuitSkuTier.standard.value)
    with self.argument_context('network express-route') as c:
        c.argument('circuit_name', er_circuit_name_type, options_list=('--name', '-n'))
        c.argument('sku_family', sku_family_type)
        c.argument('sku_tier', sku_tier_type)
        c.argument('bandwidth_in_mbps', nargs='+', options_list='--bandwidth', help='Bandwidth of the circuit. Should be Mbps for service providers or Gbps for ExpressRoute ports. Usage: INT {Mbps,Gbps}', validator=validate_circuit_bandwidth)
        c.argument('service_provider_name', options_list=('--provider',), help="Name of the ExpressRoute Service Provider.")
        c.argument('peering_location', help="Name of the peering location.")
        c.argument('device_path', options_list=('--path',), arg_type=get_enum_type(device_path_values))
        c.argument('vlan_id', type=int)
        c.argument('allow_global_reach', arg_type=get_three_state_flag(), min_api='2018-07-01', help='Enable global reach on the circuit.')

    with self.argument_context('network express-route') as c:
        c.argument('express_route_port', help='Name or ID of an ExpressRoute port.', validator=validate_express_route_port)

    with self.argument_context('network express-route update') as c:
        c.argument('sku_family', sku_family_type, default=None)
        c.argument('sku_tier', sku_tier_type, default=None)
    # endregion
