# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from ._help import helps  # pylint: disable=unused-import


class ManagementGroupsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from ._client_factory import management_groups_client_factory
        from ._exception_handler import managementgroups_exception_handler
        managementgroups_customs = CliCommandType(
            operations_tmpl='azext_managementgroups.custom#{}',
            client_factory=management_groups_client_factory,
            exception_handler=managementgroups_exception_handler)
        super(
            ManagementGroupsCommandsLoader,
            self).__init__(
                cli_ctx=cli_ctx,
                custom_command_type=managementgroups_customs)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ManagementGroupsCommandsLoader
