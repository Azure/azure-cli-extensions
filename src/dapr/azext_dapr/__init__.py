# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_dapr._help import helps


class DaprCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_dapr._client_factory import cf_dapr
        dapr_custom = CliCommandType(
            operations_tmpl='azext_dapr.custom#{}',
            client_factory=cf_dapr)
        super(DaprCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=dapr_custom)

    def load_command_table(self, args):
        from azext_dapr.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_dapr._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = DaprCommandsLoader
