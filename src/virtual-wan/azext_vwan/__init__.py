# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

import azext_vwan._help  # pylint: disable=unused-import


class VirtualWanCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from .profiles import CUSTOM_VWAN, CUSTOM_VHUB_ROUTE_TABLE
        register_resource_type('latest', CUSTOM_VWAN, '2018-08-01')
        register_resource_type('latest', CUSTOM_VHUB_ROUTE_TABLE, '2020-04-01')

        super(VirtualWanCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            custom_command_type=CliCommandType(operations_tmpl='azext_vwan.custom#{}'),
            resource_type=CUSTOM_VHUB_ROUTE_TABLE
        )

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = VirtualWanCommandsLoader
