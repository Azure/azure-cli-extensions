# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def frontdoor_client_factory(cli_ctx, aux_subscriptions=None, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_front_door.vendored_sdks import FrontDoorManagementClient
    return get_mgmt_service_client(cli_ctx, FrontDoorManagementClient, aux_subscriptions=aux_subscriptions)


def cf_frontdoor(cli_ctx, _):
    return frontdoor_client_factory(cli_ctx).front_doors


def cf_fd_endpoints(cli_ctx, _):
    return frontdoor_client_factory(cli_ctx).endpoints


def cf_fd_frontend_endpoints(cli_ctx, _):
    return frontdoor_client_factory(cli_ctx).frontend_endpoints


def cf_fd_rules_engines(cli_ctx, _):
    return frontdoor_client_factory(cli_ctx).rules_engines


def cf_fd_policies(cli_ctx, _):
    return frontdoor_client_factory(cli_ctx).policies


def cf_waf_policies(cli_ctx, _):
    return frontdoor_client_factory(cli_ctx).policies


def cf_waf_managed_rules(cli_ctx, _):
    return frontdoor_client_factory(cli_ctx).managed_rule_sets
