# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_resource_graph
from ._validators import validate_query_args


def load_command_table(self, _):

    graph_sdk = CliCommandType(
        operations_tmpl='azext_resourcegraph.custom#{}',
        client_factory=cf_resource_graph
    )

    with self.command_group('graph', command_type=graph_sdk, client_factory=cf_resource_graph) as g:
        g.custom_command('query', 'execute_query', validator=validate_query_args)
