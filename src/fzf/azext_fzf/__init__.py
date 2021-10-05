# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Initializes the azext_fzf module.
"""

from azure.cli.core import AzCommandsLoader

from azext_fzf._help import helps  # pylint: disable=unused-import


class FzfCommandsLoader(AzCommandsLoader):
    """
    Class to load the commands and arguments for the fzf extension.
    """

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        fzf_custom = CliCommandType(
            operations_tmpl='azext_fzf.custom#{}')
        super().__init__(cli_ctx=cli_ctx, custom_command_type=fzf_custom)

    def load_command_table(self, args):
        from azext_fzf.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_fzf._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = FzfCommandsLoader  # pylint: disable=invalid-name
