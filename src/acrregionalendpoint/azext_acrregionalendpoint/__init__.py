# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import ResourceType


class AcrregionalendpointCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(AcrregionalendpointCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            resource_type=ResourceType.MGMT_CONTAINERREGISTRY,
            operation_group="registries")

    def load_command_table(self, args):
        # Load commands from Azure CLI command
        from azure.cli.command_modules.acr.commands import load_command_table
        load_command_table(self, args)
        # Load extra commands for Regional Endpoint Feature
        from azext_acrregionalendpoint.commands import load_command_table_preview
        load_command_table_preview(self, args)
        return self.command_table

    def load_arguments(self, command):
        # Load arguments from Azure CLI command
        from azure.cli.command_modules.acr._params import load_arguments
        load_arguments(self, command)
        # Load extra arguments for Regional Endpoint Feature
        from azext_acrregionalendpoint._params import load_arguments_preview
        load_arguments_preview(self, command)


COMMAND_LOADER_CLS = AcrregionalendpointCommandsLoader
