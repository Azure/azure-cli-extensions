# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_account(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.subscription import SubscriptionClient
    return get_mgmt_service_client(cli_ctx, SubscriptionClient)


def cf_subscriptions(cli_ctx, *_):
    return cf_account(cli_ctx).subscriptions


def cf_subscription_operation(cli_ctx, *_):
    return cf_account(cli_ctx).subscription_operation


def cf_subscription_factory(cli_ctx, *_):
    return cf_account(cli_ctx).subscription_factory


def cf_subscription_operations(cli_ctx, *_):
    return cf_account(cli_ctx).subscription_operations


def cf_operations(cli_ctx, *_):
    return cf_account(cli_ctx).operations


def cf_tenants(cli_ctx, *_):
    return cf_account(cli_ctx).tenants
