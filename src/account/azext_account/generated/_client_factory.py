# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_account(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import _get_mgmt_service_client
    from ..vendored_sdks.subscription import SubscriptionClient
    return _get_mgmt_service_client(cli_ctx, SubscriptionClient,
                                    subscription_bound=False,
                                    base_url_bound=True)[0]


def cf_subscription(cli_ctx, *_):
    return cf_account(cli_ctx).subscription


def cf_tenant(cli_ctx, *_):
    return cf_account(cli_ctx).tenant


def cf_alias(cli_ctx, *_):
    return cf_account(cli_ctx).alias
