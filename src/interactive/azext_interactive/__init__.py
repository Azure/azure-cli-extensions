# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader


def start_shell(cmd, style=None):
    from .azclishell.app import AzInteractiveShell
    AzInteractiveShell(cmd.cli_ctx, style)()


class InteractiveCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(InteractiveCommandsLoader, self).__init__(cli_ctx=cli_ctx)

    def load_command_table(self, _):
        return self.command_table

    def load_arguments(self, _):
        pass


COMMAND_LOADER_CLS = InteractiveCommandsLoader
