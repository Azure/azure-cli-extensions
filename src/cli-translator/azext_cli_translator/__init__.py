# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_cli_translator._help import helps   # pylint: disable=unused-import


class CLITranslatorCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        cli_translator_custom = CliCommandType(operations_tmpl='azext_cli_translator.custom#{}')
        super(CLITranslatorCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=cli_translator_custom)

    def load_command_table(self, args):
        from azext_cli_translator.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_cli_translator._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = CLITranslatorCommandsLoader
