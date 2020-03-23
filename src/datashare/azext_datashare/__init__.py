# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from ._help import helps


class DataShareManagementClientCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from .generated._client_factory import cf_datashare
        datashare_custom = CliCommandType(
            operations_tmpl='azext_datashare.custom#{}',
            client_factory=cf_datashare)
        super(DataShareManagementClientCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                                      custom_command_type=datashare_custom)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = DataShareManagementClientCommandsLoader
