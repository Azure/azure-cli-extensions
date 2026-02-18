# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from . import consts

from ._help import helps  # pylint: disable=unused-import

from knack.commands import CLICommand


class ViCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from ._client_factory import cf_vi
        vi_custom = CliCommandType(
            operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.custom#{}',
            client_factory=cf_vi)
        super().__init__(cli_ctx=cli_ctx,
                         custom_command_type=vi_custom)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        command_table = self.command_table
        return command_table

    def load_arguments(self, command: CLICommand):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ViCommandsLoader
