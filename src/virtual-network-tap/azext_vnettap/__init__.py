# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

import azext_vnettap._help  # pylint: disable=unused-import


class VirtualNetworkTapCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from .profiles import CUSTOM_VNET_TAP
        register_resource_type('latest', CUSTOM_VNET_TAP, '2018-08-01')

        super(VirtualNetworkTapCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            custom_command_type=CliCommandType(operations_tmpl='azext_vnettap.custom#{}'),
            resource_type=CUSTOM_VNET_TAP
        )

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, args):
        from ._params import load_arguments
        load_arguments(self, args)


COMMAND_LOADER_CLS = VirtualNetworkTapCommandsLoader
