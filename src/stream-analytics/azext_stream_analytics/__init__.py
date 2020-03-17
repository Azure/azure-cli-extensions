# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_stream_analytics._help import helps  # pylint: disable=unused-import


class StreamAnalyticsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_stream_analytics._client_factory import cf_stream_analytics
        stream_analytics_custom = CliCommandType(
            operations_tmpl='azext_stream_analytics.custom#{}',
            client_factory=cf_stream_analytics)
        super(StreamAnalyticsCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                            custom_command_type=stream_analytics_custom)

    def load_command_table(self, args):
        from azext_stream_analytics.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_stream_analytics._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = StreamAnalyticsCommandsLoader
