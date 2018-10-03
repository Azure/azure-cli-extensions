# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from ._client_factory import (
    cf_express_route_gateways, cf_express_route_connections, cf_express_route_ports, cf_express_route_port_locations,
    cf_express_route_links, cf_express_route_circuits)


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_er_sdk = CliCommandType(
        operations_tmpl='azext_express_route.vendored_sdks.operations.express_route_circuits_operations#ExpressRouteCircuitsOperations.{}',
        client_factory=cf_express_route_circuits,
        min_api='2016-09-01'
    )

    network_er_connection_sdk = CliCommandType(
        operations_tmpl='azext_express_route.vendored_sdks.operations.express_route_connections_operations#ExpressRouteConnectionsOperations.{}',
        client_factory=cf_express_route_connections,
        min_api='2018-08-01'
    )

    network_er_gateway_sdk = CliCommandType(
        operations_tmpl='azext_express_route.vendored_sdks.operations.express_route_gateways_operations#ExpressRouteGatewaysOperations.{}',
        client_factory=cf_express_route_gateways,
        min_api='2018-08-01'
    )

    network_er_ports_sdk = CliCommandType(
        operations_tmpl='azext_express_route.vendored_sdks.operations.express_route_ports_operations#ExpressRoutePortsOperations.{}',
        client_factory=cf_express_route_ports,
        min_api='2018-08-01'
    )

    network_er_port_locations_sdk = CliCommandType(
        operations_tmpl='azext_express_route.vendored_sdks.operations.express_route_ports_locations_operations#ExpressRoutePortsLocationsOperations.{}',
        client_factory=cf_express_route_port_locations,
        min_api='2018-08-01'
    )

    network_er_links_sdk = CliCommandType(
        operations_tmpl='azext_express_route.vendored_sdks.operations.express_route_links_operations#ExpressRouteLinksOperations.{}',
        client_factory=cf_express_route_links,
        min_api='2018-08-01'
    )

    with self.command_group('network express-route gateway', network_er_gateway_sdk) as g:
        g.custom_command('create', 'create_express_route_gateway')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_express_route_gateways')
        g.show_command('show', 'get')
        g.generic_update_command('update', custom_func_name='update_express_route_gateway', setter_arg_name='put_express_route_gateway_parameters')

    with self.command_group('network express-route gateway connection', network_er_connection_sdk) as g:
        g.custom_command('create', 'create_express_route_connection')
        g.command('delete', 'delete')
        g.command('list', 'list')
        g.show_command('show', 'get')
        g.generic_update_command('update', custom_func_name='update_express_route_connection', setter_arg_name='put_express_route_connection_parameters')

    with self.command_group('network express-route port', network_er_ports_sdk) as g:
        g.custom_command('create', 'create_express_route_port')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_express_route_ports')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_express_route_port')

    with self.command_group('network express-route port link', network_er_links_sdk) as g:
        g.command('list', 'list')
        g.show_command('show')

    with self.command_group('network express-route port location', network_er_port_locations_sdk) as g:
        g.command('list', 'list')
        g.show_command('show')

    with self.command_group('network express-route', network_er_sdk) as g:
        g.show_command('show', 'get')
        g.custom_command('create', 'create_express_route', supports_no_wait=True)
        g.custom_command('list', 'list_express_route_circuits')
        g.generic_update_command('update', custom_func_name='update_express_route', supports_no_wait=True)
