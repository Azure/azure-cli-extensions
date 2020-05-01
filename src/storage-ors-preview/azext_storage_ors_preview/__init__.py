# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

from ._help import helps  # pylint: disable=unused-import
from .profiles import CUSTOM_MGMT_STORAGE_ORS


class StorageCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        register_resource_type('latest', CUSTOM_MGMT_STORAGE_ORS, '2019-06-01')
        storage_custom = CliCommandType(operations_tmpl='azext_storage_ors_preview.custom#{}')

        super(StorageCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    resource_type=CUSTOM_MGMT_STORAGE_ORS,
                                                    custom_command_type=storage_custom)

    def load_command_table(self, args):
        super(StorageCommandsLoader, self).load_command_table(args)
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super(StorageCommandsLoader, self).load_arguments(command)
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = StorageCommandsLoader
