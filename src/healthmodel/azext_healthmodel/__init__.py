# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType

from azext_healthmodel._client_factory import cf_healthmodel


class HealthModelCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        custom_type = CliCommandType(
            operations_tmpl='azext_healthmodel.custom#{}',
            client_factory=cf_healthmodel,
        )
        super().__init__(cli_ctx=cli_ctx, custom_command_type=custom_type)

    def load_command_table(self, args):
        from azext_healthmodel.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_healthmodel._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = HealthModelCommandsLoader
