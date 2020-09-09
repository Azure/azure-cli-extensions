# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_scheduled_query._help import helps  # pylint: disable=unused-import


class ScheduledQueryCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_scheduled_query._client_factory import cf_scheduled_query
        scheduled_query_custom = CliCommandType(
            operations_tmpl='azext_scheduled_query.custom#{}',
            client_factory=cf_scheduled_query)
        super(ScheduledQueryCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                           custom_command_type=scheduled_query_custom)

    def load_command_table(self, args):
        from azext_scheduled_query.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_scheduled_query._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ScheduledQueryCommandsLoader
