# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import CustomResourceType

CUSTOM_MGMT_AIMANAGER = CustomResourceType(
    'azext_aimanager.vendored_sdks.v2026_05_02_preview',
    'ContainerServiceAIManagerMgmtClient')


def get_aimanager_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_AIMANAGER, subscription_id=subscription_id)


def cf_ai_managers(cli_ctx, *_):
    return get_aimanager_client(cli_ctx).ai_managers


def cf_ai_manager_namespaces(cli_ctx, *_):
    return get_aimanager_client(cli_ctx).ai_manager_namespaces


def cf_model_deployments(cli_ctx, *_):
    return get_aimanager_client(cli_ctx).model_deployments


def cf_ai_models(cli_ctx, *_):
    return get_aimanager_client(cli_ctx).ai_models


def cf_model_sources(cli_ctx, *_):
    return get_aimanager_client(cli_ctx).model_sources
