# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_storagesync._help import helps  # pylint: disable=unused-import


class MicrosoftStorageSyncCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_storagesync._client_factory import cf_storagesync
        storagesync_custom = CliCommandType(
            operations_tmpl='azext_storagesync.custom#{}',
            client_factory=cf_storagesync)
        super(MicrosoftStorageSyncCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                                 custom_command_type=storagesync_custom)

    def load_command_table(self, args):
        from azext_storagesync.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_storagesync._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = MicrosoftStorageSyncCommandsLoader
