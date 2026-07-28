# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_aldo_edge_operator._help import helps  # pylint: disable=unused-import


class AldoEdgeOperatorCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_aldo_edge_operator._client_factory import cf_aldo_edge_operator
        aldo_edge_operator_custom = CliCommandType(
            operations_tmpl='azext_aldo_edge_operator.custom#{}',
            client_factory=cf_aldo_edge_operator)
        super(AldoEdgeOperatorCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                             custom_command_type=aldo_edge_operator_custom)

    def load_command_table(self, args):
        from azext_aldo_edge_operator.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_aldo_edge_operator._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AldoEdgeOperatorCommandsLoader
