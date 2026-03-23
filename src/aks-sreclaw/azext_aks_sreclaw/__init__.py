# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_aks_sreclaw._client_factory import CUSTOM_MGMT_AKS

# pylint: disable=unused-import
from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type


def register_aks_sreclaw_resource_type():
    register_resource_type(
        "latest",
        CUSTOM_MGMT_AKS,
        None,
    )


class ContainerServiceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        register_aks_sreclaw_resource_type()

        aks_sreclaw_custom = CliCommandType(operations_tmpl='azext_aks_sreclaw.custom#{}')
        super().__init__(
            cli_ctx=cli_ctx,
            custom_command_type=aks_sreclaw_custom,
        )

    def load_command_table(self, args):
        super().load_command_table(args)
        from azext_aks_sreclaw.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super().load_arguments(command)
        from azext_aks_sreclaw._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ContainerServiceCommandsLoader
