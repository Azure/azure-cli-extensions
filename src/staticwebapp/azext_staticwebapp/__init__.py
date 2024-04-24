# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_staticwebapp._help import helps  # pylint: disable=unused-import


class StaticwebappCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        staticwebapp_custom = CliCommandType(
            operations_tmpl='azext_staticwebapp.custom#{}',
            client_factory=None)
        super(StaticwebappCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                         custom_command_type=staticwebapp_custom)

    def load_command_table(self, args):
        from azext_staticwebapp.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_staticwebapp._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = StaticwebappCommandsLoader
