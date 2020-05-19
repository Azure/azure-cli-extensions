# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_costmanagement.generated._client_factory import cf_query
    costmanagement_query = CliCommandType(
        operations_tmpl='azext_costmanagement.vendored_sdks.costmanagement.operations.'
                        '_query_operations#QueryOperations.{}',
        client_factory=cf_query)
    with self.command_group('costmanagement', costmanagement_query,
                            client_factory=cf_query, is_experimental=True) as g:
        g.custom_command('query', 'costmanagement_query')
