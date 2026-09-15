# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import get_sdk, ResourceType
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from .helper._constants import (
    ACR_API_VERSION_2023_01_01_PREVIEW,
    ACR_API_VERSION_2019_06_01_PREVIEW
)

from azure.mgmt.authorization import AuthorizationManagementClient


def _get_acr_tasks_client(cli_ctx):
    tasks_resource_type = getattr(ResourceType, "MGMT_CONTAINERREGISTRYTASKS", None)
    if tasks_resource_type is not None:
        return get_mgmt_service_client(cli_ctx, tasks_resource_type)

    return get_mgmt_service_client(
        cli_ctx,
        ResourceType.MGMT_CONTAINERREGISTRY,
        api_version=ACR_API_VERSION_2019_06_01_PREVIEW)


def get_acr_tasks_models(cli_ctx):
    tasks_resource_type = getattr(
        ResourceType,
        "MGMT_CONTAINERREGISTRYTASKS",
        ResourceType.MGMT_CONTAINERREGISTRY)
    return get_sdk(cli_ctx, tasks_resource_type, "models")


def cf_acr(cli_ctx, *_) -> ContainerRegistryManagementClient:
    return get_mgmt_service_client(cli_ctx,
                                   ResourceType.MGMT_CONTAINERREGISTRY,
                                   api_version=ACR_API_VERSION_2023_01_01_PREVIEW)


def cf_acr_registries(cli_ctx, *_) -> ContainerRegistryManagementClient:
    return get_mgmt_service_client(cli_ctx,
                                   ResourceType.MGMT_CONTAINERREGISTRY,
                                   api_version=ACR_API_VERSION_2023_01_01_PREVIEW).registries


def cf_acr_tasks(cli_ctx, *_):
    return _get_acr_tasks_client(cli_ctx).tasks


def cf_acr_registries_tasks(cli_ctx, *_):
    return _get_acr_tasks_client(cli_ctx).registries


def cf_acr_taskruns(cli_ctx, *_):
    return _get_acr_tasks_client(cli_ctx).task_runs


def cf_acr_runs(cli_ctx, *_):
    return _get_acr_tasks_client(cli_ctx).runs


def cf_resources(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx,
                                   ResourceType.MGMT_RESOURCE_RESOURCES,
                                   subscription_id=subscription_id)


def cf_authorization(cli_ctx, subscription_id=None) -> AuthorizationManagementClient:
    return get_mgmt_service_client(cli_ctx,
                                   ResourceType.MGMT_AUTHORIZATION,
                                   subscription_id=subscription_id, api_version="2022-04-01")
