# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_storage-blob-preview._help import helps  # pylint: disable=unused-import


class Storage-blob-previewCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_storage-blob-preview._client_factory import cf_storage-blob-preview
        storage-blob-preview_custom = CliCommandType(
            operations_tmpl='azext_storage-blob-preview.custom#{}',
            client_factory=cf_storage-blob-preview)
        super(Storage-blob-previewCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=storage-blob-preview_custom)

    def load_command_table(self, args):
        from azext_storage-blob-preview.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_storage-blob-preview._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = Storage-blob-previewCommandsLoader
