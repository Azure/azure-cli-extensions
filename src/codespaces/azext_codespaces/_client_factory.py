# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._config import get_rp_api_version


def cf_codespaces(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.codespaces.codespaces_client import CodespacesClient
    custom_api_version = get_rp_api_version(cli_ctx)
    return get_mgmt_service_client(cli_ctx, CodespacesClient, api_version=custom_api_version)


def cf_codespaces_plan(cli_ctx, *_):
    return cf_codespaces(cli_ctx).plan
