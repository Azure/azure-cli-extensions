# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_copilot._help import helps  # pylint: disable=unused-import


class CopilotCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_copilot._client_factory import cf_copilot
        copilot_custom = CliCommandType(
            operations_tmpl='azext_copilot.custom#{}',
            client_factory=cf_copilot)
        super(CopilotCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=copilot_custom)

    def load_command_table(self, args):
        from azext_copilot.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_copilot._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = CopilotCommandsLoader
