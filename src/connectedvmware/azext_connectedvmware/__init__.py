# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType
from azext_connectedvmware._client_factory import cf_connectedvmware
from azext_connectedvmware._params import load_arguments
from azext_connectedvmware.commands import load_command_table


class ConnectedvmwareCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        connectedvmware_custom = CliCommandType(
            operations_tmpl='azext_connectedvmware.custom#{}',
            client_factory=cf_connectedvmware,
        )
        # pylint: disable=R1725
        super(ConnectedvmwareCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=connectedvmware_custom
        )

    def load_command_table(self, args):
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        load_arguments(self, command)


COMMAND_LOADER_CLS = ConnectedvmwareCommandsLoader
