# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_cosmosdb_preview._help import helps  # pylint: disable=unused-import


class Cosmosdb_previewCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_cosmosdb_preview._client_factory import cf_cosmosdb_preview
        cosmosdb_preview_custom = CliCommandType(
            operations_tmpl='azext_cosmosdb_preview.custom#{}',
            client_factory=cf_cosmosdb_preview)
        super().__init__(cli_ctx=cli_ctx, custom_command_type=cosmosdb_preview_custom)

    def load_command_table(self, args):
        from azext_cosmosdb_preview.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_cosmosdb_preview._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = Cosmosdb_previewCommandsLoader
