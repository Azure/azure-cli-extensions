# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_connectedvmware._help import helps  # pylint: disable=unused-import


# pylint: disable=C0415
class ConnectedvmwareCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_connectedvmware._client_factory import cf_connectedvmware
        connectedvmware_custom = CliCommandType(
            operations_tmpl='azext_connectedvmware.custom#{}',
            client_factory=cf_connectedvmware,
        )
        # pylint: disable=R1725
        super(ConnectedvmwareCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=connectedvmware_custom
        )

    def load_command_table(self, args):
        from azext_connectedvmware.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_connectedvmware._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ConnectedvmwareCommandsLoader
