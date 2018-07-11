# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands import DeploymentOutputLongRunningOperation
from azure.cli.core.commands.arm import deployment_validate_table_format, handle_template_based_exception
from azure.cli.core.commands import CliCommandType
from azure.cli.core.util import empty_on_404

from azure.cli.command_modules.network._client_factory import (
    network_client_factory, cf_express_route_cross_connection_peerings, cf_express_route_cross_connections)

# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_er_cc_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.network.operations.express_route_circuits_operations#ExpressRouteCircuitsOperations.{}',
        client_factory=cf_express_route_cross_connections,
        min_api='2018-04-01'
    )

    network_er_cc_peering_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.network.operations.express_route_circuit_peerings_operations#ExpressRouteCircuitPeeringsOperations.{}',
        client_factory=cf_express_route_cross_connection_peerings,
        min_api='2018-04-01'
    )

    cc_custom = CliCommandType(operations_tmpl='azext_expressroutecrossconnection.custom#{}')

    with self.command_group('network cross-connection', network_er_cc_sdk) as g:
        g.show_command('show', 'get')
        g.command('list-arp-tables', 'list_arp_table')
        g.command('list-route-tables', 'list_routes_table')
        g.custom_command('list', 'list_express_route_circuits')
        g.generic_update_command('update', custom_func_name='update_express_route', supports_no_wait=True)
        g.generic_wait_command('wait')

    with self.command_group('network express-route peering', network_er_cc_peering_sdk) as g:
        g.custom_command('create', 'create_express_route_peering', client_factory=cf_express_route_cross_connection_peerings)
        g.command('delete', 'delete')
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.generic_update_command('update', setter_arg_name='peering_parameters', custom_func_name='update_express_route_peering')
    