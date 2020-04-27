# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_peering._help import helps  # pylint: disable=unused-import


class PeeringCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_peering._client_factory import cf_peering
        peering_custom = CliCommandType(
            operations_tmpl='azext_peering.custom#{}',
            client_factory=cf_peering)
        super(PeeringCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    custom_command_type=peering_custom)

    def load_command_table(self, args):
        from azext_peering.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_peering._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = PeeringCommandsLoader
