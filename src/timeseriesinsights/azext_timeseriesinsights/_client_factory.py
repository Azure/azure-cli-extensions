# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def cf_timeseriesinsights_cl(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.timeseriesinsights import TimeSeriesInsightsClient
    return get_mgmt_service_client(cli_ctx,
                                   TimeSeriesInsightsClient)


def cf_event_source(cli_ctx, *_):
    return cf_timeseriesinsights_cl(cli_ctx).event_sources
