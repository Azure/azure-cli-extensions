# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType
from azext_horizondb.utils._context import HorizonDBArgumentContext
from azext_horizondb._help import helps  # pylint: disable=unused-import


class HorizonDBCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        horizondb_custom = CliCommandType(
            operations_tmpl='azext_horizondb.commands.custom_commands#{}')
        super().__init__(
            cli_ctx=cli_ctx,
            custom_command_type=horizondb_custom,
            argument_context_cls=HorizonDBArgumentContext)

    def load_command_table(self, args):
        from azext_horizondb.cluster_commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_horizondb._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = HorizonDBCommandsLoader
