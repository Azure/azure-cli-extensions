# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import ResourceType

def cf_resource(cli_ctx, subscription_id=None, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id).resources

def cf_storage_container(cli_ctx, *_):
    from azure.cli.core.profiles import get_sdk
    return get_sdk(cli_ctx, ResourceType.DATA_STORAGE_BLOB, '_container_client#ContainerClient')