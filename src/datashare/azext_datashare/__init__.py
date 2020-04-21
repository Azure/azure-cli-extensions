# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=unused-argument
# pylint: disable=unused-import

from azure.cli.core import AzCommandsLoader
from azext_datashare._help import helps


class DataShareManagementClientCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_datashare.generated._client_factory import cf_datashare
        datashare_custom = CliCommandType(
            operations_tmpl='azext_datashare.manual.custom#{}',  # modified
            client_factory=cf_datashare)
        super(DataShareManagementClientCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                                      custom_command_type=datashare_custom)

    def load_command_table(self, args):
        try:
            from azext_datashare.generated.commands import load_command_table
            load_command_table(self, args)
        except ImportError:
            pass
        try:
            from azext_datashare.manual.commands import load_command_table as load_command_table_manual
            load_command_table_manual(self, args)
        except ImportError:
            pass
        return self.command_table

    def load_arguments(self, command):
        try:
            from azext_datashare.generated._params import load_arguments
            load_arguments(self, command)
        except ImportError:
            pass
        try:
            from azext_datashare.manual._params import load_arguments as load_arguments_manual
            load_arguments_manual(self, command)
        except ImportError:
            pass


COMMAND_LOADER_CLS = DataShareManagementClientCommandsLoader
