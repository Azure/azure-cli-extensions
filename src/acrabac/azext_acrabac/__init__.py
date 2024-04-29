# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import ResourceType


class AcrabacCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        super(AcrabacCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            resource_type=ResourceType.MGMT_CONTAINERREGISTRY,
            # TODO: @m5i: can we get rid of this? use custom_command_type
            operation_group="webhooks",
        )

    def load_command_table(self, args):
        from azext_acrabac.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        # Load arguments from Azure CLI command
        from azure.cli.command_modules.acr._params import load_arguments
        load_arguments(self, command)
        # Load extra arguments for ABAC Repo Permission
        from azext_acrabac._params import load_arguments_preview
        load_arguments_preview(self, command)


COMMAND_LOADER_CLS = AcrabacCommandsLoader
