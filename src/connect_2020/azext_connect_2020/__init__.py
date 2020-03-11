# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_connect_2020._help import helps  # pylint: disable=unused-import


class Connect_2020CommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_connect_2020._client_factory import cf_connect_2020
        connect_2020_custom = CliCommandType(
            operations_tmpl='azext_connect_2020.custom#{}',
            client_factory=cf_connect_2020)
        super(Connect_2020CommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=connect_2020_custom)

    def load_command_table(self, args):
        from azext_connect_2020.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_connect_2020._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = Connect_2020CommandsLoader
