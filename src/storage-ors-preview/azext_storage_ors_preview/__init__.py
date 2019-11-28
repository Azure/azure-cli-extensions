# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_storage-ors-preview._help import helps  # pylint: disable=unused-import


class Storage-ors-previewCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_storage-ors-preview._client_factory import cf_storage-ors-preview
        storage-ors-preview_custom = CliCommandType(
            operations_tmpl='azext_storage-ors-preview.custom#{}',
            client_factory=cf_storage-ors-preview)
        super(Storage-ors-previewCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=storage-ors-preview_custom)

    def load_command_table(self, args):
        from azext_storage-ors-preview.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_storage-ors-preview._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = Storage-ors-previewCommandsLoader
