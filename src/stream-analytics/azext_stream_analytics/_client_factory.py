# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_stream_analytics(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.streamanalytics import StreamAnalyticsManagementClient
    return get_mgmt_service_client(cli_ctx, StreamAnalyticsManagementClient)


def cf_jobs(cli_ctx, *_):
    return cf_stream_analytics(cli_ctx).streaming_jobs


def cf_inputs(cli_ctx, *_):
    return cf_stream_analytics(cli_ctx).inputs


def cf_outputs(cli_ctx, *_):
    return cf_stream_analytics(cli_ctx).outputs


def cf_transformations(cli_ctx, *_):
    return cf_stream_analytics(cli_ctx).transformations


def cf_functions(cli_ctx, *_):
    return cf_stream_analytics(cli_ctx).functions


def cf_subscriptions(cli_ctx, *_):
    return cf_stream_analytics(cli_ctx).subscriptions
