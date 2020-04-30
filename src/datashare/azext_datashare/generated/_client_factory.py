# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_datashare(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from ..vendored_sdks.datashare import DataShareManagementClient
    return get_mgmt_service_client(cli_ctx, DataShareManagementClient)


def cf_account(cli_ctx, *_):
    return cf_datashare(cli_ctx).account


def cf_consumer_invitation(cli_ctx, *_):
    return cf_datashare(cli_ctx).consumer_invitation


def cf_data_set(cli_ctx, *_):
    return cf_datashare(cli_ctx).data_set


def cf_data_set_mapping(cli_ctx, *_):
    return cf_datashare(cli_ctx).data_set_mapping


def cf_invitation(cli_ctx, *_):
    return cf_datashare(cli_ctx).invitation


def cf_share(cli_ctx, *_):
    return cf_datashare(cli_ctx).share


def cf_provider_share_subscription(cli_ctx, *_):
    return cf_datashare(cli_ctx).provider_share_subscription


def cf_share_subscription(cli_ctx, *_):
    return cf_datashare(cli_ctx).share_subscription


def cf_consumer_source_data_set(cli_ctx, *_):
    return cf_datashare(cli_ctx).consumer_source_data_set


def cf_synchronization_setting(cli_ctx, *_):
    return cf_datashare(cli_ctx).synchronization_setting


def cf_trigger(cli_ctx, *_):
    return cf_datashare(cli_ctx).trigger
