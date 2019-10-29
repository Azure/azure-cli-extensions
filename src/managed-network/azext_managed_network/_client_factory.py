# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_managed_network(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.managednetwork import ManagedNetworkManagementClient
    return get_mgmt_service_client(cli_ctx, ManagedNetworkManagementClient)


def cf_managed_networks(cli_ctx, *_):
    return cf_managed_network(cli_ctx).managed_networks


def cf_scope_assignments(cli_ctx, *_):
    return cf_managed_network(cli_ctx).scope_assignments


def cf_managed_network_groups(cli_ctx, *_):
    return cf_managed_network(cli_ctx).managed_network_groups


def cf_managed_network_peering_policies(cli_ctx, *_):
    return cf_managed_network(cli_ctx).managed_network_peering_policies


def cf_operations(cli_ctx, *_):
    return cf_managed_network(cli_ctx).operations
