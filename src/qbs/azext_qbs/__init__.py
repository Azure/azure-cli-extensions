# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType
from azext_qbs._help import helps  # pylint: disable=unused-import
from azext_qbs._params import load_arguments as az_load_args
from azext_qbs.commands import load_command_table as az_load_commands


class QbsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        qbs_custom = CliCommandType(operations_tmpl='azext_qbs.custom#{}')
        super().__init__(cli_ctx=cli_ctx, custom_command_type=qbs_custom)

    def load_command_table(self, args):
        az_load_commands(self, args)
        return self.command_table

    def load_arguments(self, command):
        az_load_args(self, command)


COMMAND_LOADER_CLS = QbsCommandsLoader
