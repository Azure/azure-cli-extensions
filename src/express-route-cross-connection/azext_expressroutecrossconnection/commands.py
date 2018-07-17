# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from ._client_factory import (
    cf_express_route_cross_connection_peerings, cf_express_route_cross_connections)


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_er_cc_sdk = CliCommandType(
        operations_tmpl='azext_expressroutecrossconnection.vendored_sdks.operations.express_route_cross_connections_operations#ExpressRouteCrossConnectionsOperations.{}',
        client_factory=cf_express_route_cross_connections,
        min_api='2018-04-01'
    )

    network_er_cc_peering_sdk = CliCommandType(
        operations_tmpl='azext_expressroutecrossconnection.vendored_sdks.operations.express_route_cross_connection_peerings_operations#ExpressRouteCrossConnectionPeeringsOperations.{}',
        client_factory=cf_express_route_cross_connection_peerings,
        min_api='2018-04-01'
    )

    with self.command_group('network cross-connection', network_er_cc_sdk) as g:
        g.show_command('show', 'get')
        g.command('list-arp-tables', 'list_arp_table')
        g.command('list-route-tables', 'list_routes_table')
        g.command('summarize-route-table', 'list_routes_table_summary')
        g.custom_command('list', 'list_express_route_cross_connections')
        g.generic_update_command('update', custom_func_name='update_express_route_cross_connection', supports_no_wait=True)
        g.wait_command('wait')

    with self.command_group('network cross-connection peering', network_er_cc_peering_sdk) as g:
        g.custom_command('create', 'create_express_route_cross_connection_peering', client_factory=cf_express_route_cross_connection_peerings)
        g.command('delete', 'delete')
        g.show_command('show', 'get')
        g.command('list', 'list')
        g.generic_update_command('update', setter_arg_name='peering_parameters', custom_func_name='update_express_route_peering')
