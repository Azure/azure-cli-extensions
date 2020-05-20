# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_storagesync(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.storagesync import StorageSyncManagementClient
    return get_mgmt_service_client(cli_ctx, StorageSyncManagementClient)


def cf_storage_sync_services(cli_ctx, *_):
    return cf_storagesync(cli_ctx).storage_sync_services


def cf_sync_groups(cli_ctx, *_):
    return cf_storagesync(cli_ctx).sync_groups


def cf_cloud_endpoints(cli_ctx, *_):
    return cf_storagesync(cli_ctx).cloud_endpoints


def cf_server_endpoints(cli_ctx, *_):
    return cf_storagesync(cli_ctx).server_endpoints


def cf_registered_servers(cli_ctx, *_):
    return cf_storagesync(cli_ctx).registered_servers


def cf_workflows(cli_ctx, *_):
    return cf_storagesync(cli_ctx).workflows


def cf_operation_status(cli_ctx, *_):
    return cf_storagesync(cli_ctx).operation_status
