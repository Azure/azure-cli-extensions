# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def network_client_factory(cli_ctx, aux_subscriptions=None, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .profiles import CUSTOM_VNET_TAP
    return get_mgmt_service_client(cli_ctx, CUSTOM_VNET_TAP, aux_subscriptions=aux_subscriptions,
                                   api_version='2018-08-01')


def cf_virtual_network_taps(cli_ctx, _):
    return network_client_factory(cli_ctx).virtual_network_taps


def cf_load_balancers(cli_ctx, _):
    return network_client_factory(cli_ctx).load_balancers


def cf_nics(cli_ctx, _):
    return network_client_factory(cli_ctx).network_interfaces


def cf_nic_tap_config(cli_ctx, _):
    return network_client_factory(cli_ctx).network_interface_tap_configurations
