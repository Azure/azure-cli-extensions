# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def network_client_factory(cli_ctx, **_):
    from .profiles import CUSTOM_NW_CONNECTION_MONITOR
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, CUSTOM_NW_CONNECTION_MONITOR, api_version='2019-11-01')


def cf_nw_connection_monitor(cli_ctx, _):
    return network_client_factory(cli_ctx).connection_monitors


def cf_nw_connection_monitor_v1(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .profiles import CUSTOM_NW_CONNECTION_MONITOR_V1
    return get_mgmt_service_client(cli_ctx, CUSTOM_NW_CONNECTION_MONITOR_V1, api_version='2019-06-01')
