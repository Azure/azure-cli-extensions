# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_monitor_trace_association._help import helps  # pylint: disable=unused-import


class MonitorTraceAssociationCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_command_type = CliCommandType(
            operations_tmpl='azext_monitor_trace_association.custom#{}')
        super().__init__(cli_ctx=cli_ctx,
                         custom_command_type=custom_command_type)

    def load_command_table(self, args):
        from azext_monitor_trace_association.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_monitor_trace_association._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = MonitorTraceAssociationCommandsLoader
