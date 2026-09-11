# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    trace_association_custom = CliCommandType(
        operations_tmpl='azext_monitor_trace_association.custom#{}')

    with self.command_group('monitor trace-association',
                            custom_command_type=trace_association_custom,
                            is_preview=True) as g:
        g.custom_command('create', 'create_trace_association')
        g.custom_command('update', 'update_trace_association')
        g.custom_show_command('show', 'show_trace_association')
        g.custom_command('delete', 'delete_trace_association', confirmation=True)
        g.custom_command('list', 'list_trace_association')
