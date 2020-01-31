# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

from ._client_factory import cf_nw_connection_monitor
from ._help import helps  # pylint: disable=unused-import


class NWConnectionMonitorCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from .profiles import CUSTOM_NW_CONNECTION_MONITOR

        register_resource_type('latest', CUSTOM_NW_CONNECTION_MONITOR, '2019-11-01')

        nw_connection_monitor = CliCommandType(
            operations_tmpl='azext_connection_monitor_preview.custom#{}',
            client_factory=cf_nw_connection_monitor
        )

        super(NWConnectionMonitorCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                                custom_command_type=nw_connection_monitor,
                                                                resource_type=CUSTOM_NW_CONNECTION_MONITOR)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = NWConnectionMonitorCommandsLoader
