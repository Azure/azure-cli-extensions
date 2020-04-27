# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from .generated._help import helps  # pylint: disable=unused-import


class ImportExportCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from .generated._client_factory import cf_import_export
        import_export_custom = CliCommandType(
            operations_tmpl='azext_import_export.custom#{}',
            client_factory=cf_import_export)
        super(ImportExportCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=import_export_custom)

    def load_command_table(self, args):
        from .generated.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from .generated._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ImportExportCommandsLoader
