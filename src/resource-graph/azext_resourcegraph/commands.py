# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_resource_graph, cf_resource_graph_graph_query
from ._validators import validate_query_args


def load_command_table(self, _):

    graph_shared_query_sdk = CliCommandType(
        operations_tmpl='azext_resourcegraph.vendored_sdks.resourcegraph.operations#GraphQueryOperations.{}',
        client_factory=cf_resource_graph_graph_query
    )

    with self.command_group('graph', client_factory=cf_resource_graph) as g:
        g.custom_command('query', 'execute_query', validator=validate_query_args)

    with self.command_group('graph shared-query', graph_shared_query_sdk, is_experimental=True) as g:
        g.custom_command('create', 'create_shared_query')
        g.command('list', 'list')
        g.command('delete', 'delete')
        g.show_command('show', 'get')
