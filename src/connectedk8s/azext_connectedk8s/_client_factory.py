# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.core._profile import Profile
from azure.cli.core.commands.client_factory import configure_common_settings
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.graphrbac import GraphRbacManagementClient


def cf_connectedk8s(cli_ctx, *_):
    from azext_connectedk8s.vendored_sdks import ConnectedKubernetesClient
    return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient)


def cf_connected_cluster(cli_ctx, _):
    return cf_connectedk8s(cli_ctx).connected_cluster


def cf_connectedk8s_prev_2022_10_01(cli_ctx, *_):
    from azext_connectedk8s.vendored_sdks.preview_2022_10_01 import ConnectedKubernetesClient
    return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient)


def cf_connected_cluster_prev_2022_10_01(cli_ctx, _):
    return cf_connectedk8s_prev_2022_10_01(cli_ctx).connected_cluster


def cf_connectedmachine(cli_ctx, subscription_id):
    from azure.mgmt.hybridcompute import HybridComputeManagementClient
    return get_mgmt_service_client(cli_ctx, HybridComputeManagementClient, subscription_id=subscription_id).private_link_scopes


def cf_resource_groups(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                   subscription_id=subscription_id).resource_groups


def _resource_client_factory(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id)


def _resource_providers_client(cli_ctx):
    from azure.mgmt.resource import ResourceManagementClient
    return get_mgmt_service_client(cli_ctx, ResourceManagementClient).providers

    # Alternate: This should also work
    # subscription_id = get_subscription_id(cli_ctx)
    # return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id).providers


def _graph_client_factory(cli_ctx, **_):
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, tenant_id = profile.get_login_credentials(
        resource=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    client = GraphRbacManagementClient(cred, tenant_id,
                                       base_url=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    configure_common_settings(cli_ctx, client)
    return client


def get_graph_client_service_principals(cli_ctx):
    return _graph_client_factory(cli_ctx).service_principals
