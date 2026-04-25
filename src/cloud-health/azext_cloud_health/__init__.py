# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType

from azext_cloud_health._client_factory import cf_cloud_health


class CloudHealthCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        custom_type = CliCommandType(
            operations_tmpl='azext_cloud_health.custom#{}',
            client_factory=cf_cloud_health,
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=custom_type)

    def load_command_table(self, args):
        from azext_cloud_health.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_cloud_health._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = CloudHealthCommandsLoader
