# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_appservice_kube._help import helps  # pylint: disable=unused-import


class AppserviceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azure.cli.core.profiles import ResourceType
        appservice_custom = CliCommandType(operations_tmpl='azext_appservice_kube.custom#{}')
        super().__init__(cli_ctx=cli_ctx,
                         custom_command_type=appservice_custom,
                         resource_type=ResourceType.MGMT_APPSERVICE)

    def load_command_table(self, args):
        super().load_command_table(args)
        from azext_appservice_kube.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super().load_arguments(command)
        from azext_appservice_kube._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AppserviceCommandsLoader
