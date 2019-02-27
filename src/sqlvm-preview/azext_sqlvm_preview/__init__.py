# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_sqlvm_preview._help  # pylint: disable=unused-import


class SqlVmCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        sqlvm_custom = CliCommandType(operations_tmpl='azext_sqlvm_preview.custom#{}')
        super(SqlVmCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=sqlvm_custom,
                                                  min_profile='2017-03-10-profile')

    def load_command_table(self, args):
        from azext_sqlvm_preview.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_sqlvm_preview._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = SqlVmCommandsLoader
