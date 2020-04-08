# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_logic.generated._help import helps  # pylint: disable=unused-import


class LogicManagementClientCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_logic.generated._client_factory import cf_logic
        logic_custom = CliCommandType(
            operations_tmpl='azext_logic.custom#{}',
            client_factory=cf_logic)
        super(LogicManagementClientCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                                  custom_command_type=logic_custom)

    def load_command_table(self, args):
        from azext_logic.generated.commands import load_command_table
        load_command_table(self, args)
        try:
            from azext_logic.manual.commands import load_command_table as load_command_table_manual
            load_command_table_manual(self, args)
        except ImportError:
            pass
        return self.command_table

    def load_arguments(self, command):
        from azext_logic.generated._params import load_arguments
        load_arguments(self, command)
        try:
            from azext_logic.manual._params import load_arguments as load_arguments_manual
            load_arguments_manual(self, command)
        except ImportError:
            pass


COMMAND_LOADER_CLS = LogicManagementClientCommandsLoader
