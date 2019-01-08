# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=ungrouped-imports
from azure.cli.core import AzCommandsLoader
from azure.cli.command_modules.appservice.commands import ex_handler_factory
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (get_enum_type, get_resource_name_completion_list)
# pylint: disable=unused-import

import azext_mysql._help


class MysqlCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        mysql_custom = CliCommandType(
            operations_tmpl='azext_mysql.custom#{}')
        super(MysqlCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=mysql_custom,
                                                  min_profile="2017-03-10-profile")

    def load_command_table(self, args):
        super(MysqlCommandsLoader, self).load_command_table(args)
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super(MysqlCommandsLoader, self).load_arguments(command)
        from ._params import load_arguments
        load_arguments(self, command)

COMMAND_LOADER_CLS = MysqlCommandsLoader
