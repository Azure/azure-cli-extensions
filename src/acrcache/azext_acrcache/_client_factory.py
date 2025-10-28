# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

def cf_acrcache(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
    from azext_acrcache.vendored_sdks.containerregistry.v2025_09_01_preview.generated.container_registry_management_client import ContainerRegistryManagementClient
    subscription_id = get_subscription_id(cli_ctx)
    return get_mgmt_service_client(cli_ctx, ContainerRegistryManagementClient, subscription_id=subscription_id).cache_rules

def cf_acrreg(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
    from azext_acrcache.vendored_sdks.containerregistry.v2025_09_01_preview.generated.container_registry_management_client import ContainerRegistryManagementClient
    subscription_id = get_subscription_id(cli_ctx)
    return get_mgmt_service_client(cli_ctx, ContainerRegistryManagementClient, subscription_id=subscription_id).registries
