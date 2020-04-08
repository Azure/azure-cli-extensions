# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_hpc_cache(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.storagecache import StorageCacheManagementClient
    return get_mgmt_service_client(cli_ctx, StorageCacheManagementClient)


def cf_operations(cli_ctx, *_):
    return cf_hpc_cache(cli_ctx).operations


def cf_skus(cli_ctx, *_):
    return cf_hpc_cache(cli_ctx).skus


def cf_usage_models(cli_ctx, *_):
    return cf_hpc_cache(cli_ctx).usage_models


def cf_caches(cli_ctx, *_):
    return cf_hpc_cache(cli_ctx).caches


def cf_storage_targets(cli_ctx, *_):
    return cf_hpc_cache(cli_ctx).storage_targets
