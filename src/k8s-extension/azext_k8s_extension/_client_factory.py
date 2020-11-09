# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType


def cf_k8s_extension(cli_ctx, *_):
    from azext_k8s_extension.vendored_sdks import K8sExtensionClient
    return get_mgmt_service_client(cli_ctx, K8sExtensionClient)


def cf_k8s_extension_operation(cli_ctx, _):
    return cf_k8s_extension(cli_ctx).k8s_extensions


def cf_resource_groups(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                   subscription_id=subscription_id).resource_groups


def cf_resources(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                   subscription_id=subscription_id).resources


def cf_log_analytics(cli_ctx, subscription_id=None):
    from azure.mgmt.loganalytics import LogAnalyticsManagementClient
    return get_mgmt_service_client(cli_ctx, LogAnalyticsManagementClient, subscription_id=subscription_id)
