# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_maintenance._help  # pylint: disable=unused-import


class MaintenanceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        maintenance_custom = CliCommandType(operations_tmpl='azext_maintenance.custom#{}')
        super(MaintenanceCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=maintenance_custom)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = MaintenanceCommandsLoader
