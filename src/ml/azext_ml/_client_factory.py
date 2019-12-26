# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_ml(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.machinelearning import AzureMLManagementClient
    return get_mgmt_service_client(cli_ctx, AzureMLManagementClient)


def cf_operations(cli_ctx, *_):
    return cf_ml(cli_ctx).operations


def cf_workspaces(cli_ctx, *_):
    return cf_ml(cli_ctx).workspaces
