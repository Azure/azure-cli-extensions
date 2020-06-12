# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_codespaces(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.vsonline.vs_online_client import VSOnlineClient
    return get_mgmt_service_client(cli_ctx, VSOnlineClient)


def cf_codespaces_plan(cli_ctx, *_):
    return cf_codespaces(cli_ctx).plan
