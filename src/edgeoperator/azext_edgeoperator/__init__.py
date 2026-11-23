# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_edgeoperator._help import helps  # pylint: disable=unused-import


class AldoCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        command_type = CliCommandType(operations_tmpl="azext_edgeoperator.custom#{}")
        super().__init__(cli_ctx=cli_ctx, custom_command_type=command_type)

    def load_command_table(self, args):
        from azext_edgeoperator.commands import load_command_table

        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_edgeoperator._params import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = AldoCommandsLoader
