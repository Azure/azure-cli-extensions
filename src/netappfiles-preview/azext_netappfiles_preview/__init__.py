# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from ._help import helps  # pylint: disable=unused-import


class NetAppExtensionCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        netapp_custom = CliCommandType(operations_tmpl='azext_netappfiles_preview.custom#{}')
        super(NetAppExtensionCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                            custom_command_type=netapp_custom)

    def load_command_table(self, args):
        super(NetAppExtensionCommandsLoader, self).load_command_table(args)
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super(NetAppExtensionCommandsLoader, self).load_arguments(command)
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = NetAppExtensionCommandsLoader
