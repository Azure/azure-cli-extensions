# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_cosmosdb_pitr._help import helps  # pylint: disable=unused-import


class Cosmosdb_pitrCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_cosmosdb_pitr._client_factory import cf_cosmosdb_pitr
        cosmosdb_pitr_custom = CliCommandType(
            operations_tmpl='azext_cosmosdb_pitr.custom#{}',
            client_factory=cf_cosmosdb_pitr)
        super(Cosmosdb_pitrCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                          custom_command_type=cosmosdb_pitr_custom)

    def load_command_table(self, args):
        from azext_cosmosdb_pitr.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_cosmosdb_pitr._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = Cosmosdb_pitrCommandsLoader
