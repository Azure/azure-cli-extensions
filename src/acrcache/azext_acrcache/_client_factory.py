# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def cf_acrcache(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_acrcache.vendored_sdks.containerregistry.v2023_11_01_preview._container_registry_management_client import ContainerRegistryManagementClient
    return get_mgmt_service_client(cli_ctx, ContainerRegistryManagementClient).cache_rules

def cf_acrreg(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_acrcache.vendored_sdks.containerregistry.v2023_11_01_preview._container_registry_management_client import ContainerRegistryManagementClient
    return get_mgmt_service_client(cli_ctx, ContainerRegistryManagementClient)


