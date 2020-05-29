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

    from azext_costmanagement.generated._client_factory import cf_export
    costmanagement_export = CliCommandType(
        operations_tmpl='azext_costmanagement.vendored_sdks.costmanagement.operations._export_operations#ExportOperatio'
        'ns.{}',
        client_factory=cf_export)
    with self.command_group('costmanagement export', costmanagement_export, client_factory=cf_export,
                            is_experimental=True) as g:
        g.custom_command('list', 'costmanagement_export_list')
        g.custom_show_command('show', 'costmanagement_export_show')
        g.custom_command('create', 'costmanagement_export_create')
        g.custom_command('update', 'costmanagement_export_update')
        g.custom_command('delete', 'costmanagement_export_delete', confirmation=True)
