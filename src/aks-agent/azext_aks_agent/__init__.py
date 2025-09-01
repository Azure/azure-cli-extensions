# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core import AzCommandsLoader

# pylint: disable=unused-import
import azext_aks_agent._help


class ContainerServiceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        aks_agent_custom = CliCommandType(operations_tmpl='azext_aks_agent.custom#{}')
        super().__init__(
            cli_ctx=cli_ctx,
            custom_command_type=aks_agent_custom,
        )

    def load_command_table(self, args):
        super().load_command_table(args)
        from azext_aks_agent.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super().load_arguments(command)
        from azext_aks_agent._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ContainerServiceCommandsLoader
