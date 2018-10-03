# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def network_client_factory(cli_ctx, aux_subscriptions=None, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .profiles import CUSTOM_ER
    return get_mgmt_service_client(cli_ctx, CUSTOM_ER,
                                   aux_subscriptions=aux_subscriptions)


def cf_express_route_circuits(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_circuits


def cf_express_route_connections(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_connections


def cf_express_route_gateways(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_gateways


def cf_express_route_ports(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_ports


def cf_express_route_port_locations(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_ports_locations


def cf_express_route_links(cli_ctx, _):
    return network_client_factory(cli_ctx).express_route_links
