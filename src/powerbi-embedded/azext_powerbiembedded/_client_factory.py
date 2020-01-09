# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_powerbiembedded(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.powerbiembedded import PowerBIEmbeddedManagementClient
    return get_mgmt_service_client(cli_ctx, PowerBIEmbeddedManagementClient)


def cf_workspace_collections(cli_ctx, *_):
    return cf_powerbiembedded(cli_ctx).workspace_collections


def cf_workspaces(cli_ctx, *_):
    return cf_powerbiembedded(cli_ctx).workspaces
