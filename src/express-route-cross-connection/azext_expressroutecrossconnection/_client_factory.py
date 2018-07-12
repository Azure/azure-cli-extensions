# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def network_client_factory(cli_ctx, aux_subscriptions=None, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .profiles import CUSTOM_ER_CC
    return get_mgmt_service_client(cli_ctx, CUSTOM_ER_CC, aux_subscriptions=aux_subscriptions)


def cf_express_route_cross_connection_peerings(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_cross_connection_peerings


def cf_express_route_cross_connections(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_cross_connections
