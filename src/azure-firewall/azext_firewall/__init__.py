# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

import azext_firewall._help  # pylint: disable=unused-import


class AzureFirewallCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from .profiles import CUSTOM_FIREWALL, CUSTOM_FIREWALL_POLICY
        register_resource_type('latest', CUSTOM_FIREWALL, '2019-11-01')
        register_resource_type('latest', CUSTOM_FIREWALL_POLICY, '2019-07-01')

        super(AzureFirewallCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            custom_command_type=CliCommandType(operations_tmpl='azext_firewall.custom#{}'),
            resource_type=CUSTOM_FIREWALL
        )

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AzureFirewallCommandsLoader
