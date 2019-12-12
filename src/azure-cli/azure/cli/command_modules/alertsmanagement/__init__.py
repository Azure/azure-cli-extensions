# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_alertsmanagement._help import helps  # pylint: disable=unused-import


class AlertsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_alertsmanagement._client_factory import cf_alertsmanagement
        alertsmanagement_custom = CliCommandType(
            operations_tmpl='azext_alertsmanagement.custom#{}',
            client_factory=cf_alertsmanagement)
        super(AlertsCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                   custom_command_type=alertsmanagement_custom)

    def load_command_table(self, args):
        from azext_alertsmanagement.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_alertsmanagement._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AlertsCommandsLoader
