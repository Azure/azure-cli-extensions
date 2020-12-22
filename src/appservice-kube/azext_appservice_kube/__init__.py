# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

from azext_appservice_kube._help import helps  # pylint: disable=unused-import
from azext_appservice_kube._client_factory import CUSTOM_MGMT_APPSERVICE


class AppserviceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        register_resource_type('latest', CUSTOM_MGMT_APPSERVICE, '2020-06-01')

        appservice_kube_custom = CliCommandType(
            operations_tmpl='azext_appservice_kube.custom#{}')
        super(AppserviceCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                       custom_command_type=appservice_kube_custom,
                                                       resource_type=CUSTOM_MGMT_APPSERVICE)

    def load_command_table(self, args):
        super(AppserviceCommandsLoader, self).load_command_table(args)
        from azext_appservice_kube.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from sys import version_info
        if version_info[0] < 3:
            super(AppserviceCommandsLoader, self).load_arguments(command)
        else:
            super().load_arguments(command)
        from azext_appservice_kube._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AppserviceCommandsLoader
