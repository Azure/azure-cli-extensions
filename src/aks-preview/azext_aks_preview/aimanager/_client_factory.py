# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Client factory for the AI Manager commands.

Wires up the vendored ``azure-mgmt-containerserviceaimanager`` track2 client through
``get_mgmt_service_client`` (credential, subscription id, ARM endpoint and scopes) and
exposes the individual operation groups used by the custom commands.
"""

from azure.cli.core.commands.client_factory import get_mgmt_service_client

from .vendored_sdk import ContainerServiceAIManagerMgmtClient


def cf_aimanager_client(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, ContainerServiceAIManagerMgmtClient)


def cf_ai_managers(cli_ctx, *_):
    return cf_aimanager_client(cli_ctx).ai_managers


def cf_ai_manager_namespaces(cli_ctx, *_):
    return cf_aimanager_client(cli_ctx).ai_manager_namespaces
