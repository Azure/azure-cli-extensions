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
#
#
# def cf_environment(cli_ctx, *_):
#     return cf_timeseriesinsights_cl(cli_ctx).environments
#
#
def cf_event_source(cli_ctx, *_):
    return cf_timeseriesinsights_cl(cli_ctx).event_sources
#
#
# def cf_reference_data_set(cli_ctx, *_):
#     return cf_timeseriesinsights_cl(cli_ctx).reference_data_sets
#
#
# def cf_access_policy(cli_ctx, *_):
#     return cf_timeseriesinsights_cl(cli_ctx).access_policies
