# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def _webpubsub_client_factory(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.azure_mgmt_webpubsub import WebPubSubManagementClient
    return get_mgmt_service_client(cli_ctx, WebPubSubManagementClient)


def cf_webpubsub(cli_ctx, *_):
    return _webpubsub_client_factory(cli_ctx).web_pub_sub


def cf_webpubsubhub(cli_ctx, *_):
    return _webpubsub_client_factory(cli_ctx).web_pub_sub_hubs


def cf_webpubsubhub_usage(cli_ctx, *_):
    return _webpubsub_client_factory(cli_ctx).usages


def cf_webpubsub_replicas(cli_ctx, *_):
    return _webpubsub_client_factory(cli_ctx).web_pub_sub_replicas
