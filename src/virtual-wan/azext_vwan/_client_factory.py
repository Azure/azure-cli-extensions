# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def network_client_factory(cli_ctx, aux_subscriptions=None, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .profiles import CUSTOM_VWAN
    return get_mgmt_service_client(cli_ctx, CUSTOM_VWAN, aux_subscriptions=aux_subscriptions,
                                   api_version='2022-07-01')


def cf_virtual_wans(cli_ctx, _):
    return network_client_factory(cli_ctx).virtual_wans


def cf_virtual_hubs(cli_ctx, _):
    return network_client_factory(cli_ctx).virtual_hubs


def cf_virtual_hub_bgpconnection(cli_ctx, _):
    return network_client_factory(cli_ctx).virtual_hub_bgp_connection


def cf_virtual_hub_bgpconnections(cli_ctx, _):
    return network_client_factory(cli_ctx).virtual_hub_bgp_connections


def cf_virtual_hub_route_table_v2s(cli_ctx, _):
    return network_client_factory(cli_ctx).virtual_hub_route_table_v2_s


def cf_vpn_server_config(cli_ctx, _):
    return network_client_factory(cli_ctx).vpn_server_configurations


def cf_p2s_vpn_gateways(cli_ctx, _):
    return network_client_factory(cli_ctx).p2_svpn_gateways


def cf_vpn_sites(cli_ctx, _):
    return network_client_factory(cli_ctx).vpn_sites


def cf_vpn_site_configs(cli_ctx, _):
    return network_client_factory(cli_ctx).vpn_sites_configuration


def cf_vpn_gateways(cli_ctx, _):
    return network_client_factory(cli_ctx).vpn_gateways


def cf_vpn_gateway_connection(cli_ctx, _):
    return network_client_factory(cli_ctx).vpn_connections
