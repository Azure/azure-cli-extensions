# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_databricks(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.databricks import DatabricksClient
    return get_mgmt_service_client(cli_ctx, DatabricksClient)


def cf_workspaces(cli_ctx, *_):
    return cf_databricks(cli_ctx).workspaces


def cf_operations(cli_ctx, *_):
    return cf_databricks(cli_ctx).operations


def cf_vnet_peering(cli_ctx, *_):
    return cf_databricks(cli_ctx).vnet_peering
