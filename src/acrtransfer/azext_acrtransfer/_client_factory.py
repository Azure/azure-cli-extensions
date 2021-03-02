# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def cf_acrtransfer(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_acrtransfer.vendored_sdks.containerregistry.v2019_12_01_preview._container_registry_management_client import ContainerRegistryManagementClient
    return get_mgmt_service_client(cli_ctx, ContainerRegistryManagementClient)
