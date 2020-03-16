# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_account(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import _get_mgmt_service_client
    from ..vendored_sdks.subscription import SubscriptionClient
    return _get_mgmt_service_client(cli_ctx, SubscriptionClient,
                                    subscription_bound=False,
                                    base_url_bound=False)[0]


def cf_subscription(cli_ctx, *_):
    return cf_account(cli_ctx).subscription


def cf_subscription_operation(cli_ctx, *_):
    return cf_account(cli_ctx).subscription_operation


def cf_operation(cli_ctx, *_):
    return cf_account(cli_ctx).operation
