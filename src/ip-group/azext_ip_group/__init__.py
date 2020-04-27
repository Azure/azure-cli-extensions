# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

from ._help import helps  # pylint: disable=unused-import


class IpGroupsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from ._client_factory import cf_ip_groups
        from .profiles import CUSTOM_IP_GROUPS

        register_resource_type('latest', CUSTOM_IP_GROUPS, '2019-09-01')

        ip_groups_custom = CliCommandType(
            operations_tmpl='azext_ip_group.custom#{}',
            client_factory=cf_ip_groups)

        super(IpGroupsCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                     custom_command_type=ip_groups_custom,
                                                     resource_type=CUSTOM_IP_GROUPS)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = IpGroupsCommandsLoader
