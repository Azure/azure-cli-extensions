# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Client factory for the ``az aimanager`` command group.

The vendored ``azure-mgmt-containerserviceaimanager`` SDK is registered as a custom
resource type so models can be resolved via ``cmd.get_models`` (see ``aimanager.py``),
mirroring how ``managed_namespaces`` uses ``CUSTOM_MGMT_AKS_PREVIEW``.
"""

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import CustomResourceType

CUSTOM_MGMT_AIMANAGER = CustomResourceType(
    'azext_aks_preview.aimanager.vendored_sdk',
    'ContainerServiceAIManagerMgmtClient')


def get_aimanager_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_AIMANAGER, subscription_id=subscription_id)


def cf_ai_managers(cli_ctx, *_):
    return get_aimanager_client(cli_ctx).ai_managers


def cf_ai_manager_namespaces(cli_ctx, *_):
    return get_aimanager_client(cli_ctx).ai_manager_namespaces
