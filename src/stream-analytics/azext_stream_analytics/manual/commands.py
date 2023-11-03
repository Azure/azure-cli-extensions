# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azure.cli.core.commands import CliCommandType


def cf_stream_analytics_cl(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_stream_analytics.vendored_sdks.streamanalytics import StreamAnalyticsManagementClient
    return get_mgmt_service_client(cli_ctx, StreamAnalyticsManagementClient)


def cf_function(cli_ctx, *_):
    return cf_stream_analytics_cl(cli_ctx).functions


stream_analytics_function = CliCommandType(
    operations_tmpl=(
        "azext_stream_analytics.vendored_sdks.streamanalytics.operations._functions_operations#FunctionsOperations.{}"
    ),
    client_factory=cf_function,
)


def load_command_table(self, _):

    with self.command_group("stream-analytics function", stream_analytics_function, client_factory=cf_function) as g:
        g.custom_command("inspect", "stream_analytics_function_inspect")
