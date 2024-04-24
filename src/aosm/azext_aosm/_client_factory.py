# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.mgmt.containerregistry import ContainerRegistryManagementClient

from .vendored_sdks import HybridNetworkManagementClient


def cf_aosm(cli_ctx, *_) -> HybridNetworkManagementClient:
    # By default, get_mgmt_service_client() sets a parameter called 'base_url' when creating
    # the client. For us, doing so results in a key error. Setting base_url_bound=False prevents
    # that from happening
    return get_mgmt_service_client(cli_ctx, HybridNetworkManagementClient, base_url_bound=False)


def cf_resources(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(
        cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id
    )


def cf_features(cli_ctx, subscription_id=None):
    """Return the client for checking feature enablement."""
    return get_mgmt_service_client(
        cli_ctx, ResourceType.MGMT_RESOURCE_FEATURES, subscription_id=subscription_id
    )


def cf_acr_registries(cli_ctx, *_) -> ContainerRegistryManagementClient:
    """
    Returns the client for managing container registries.

    :param cli_ctx: CLI context
    :return: ContainerRegistryManagementClient object
    """
    return get_mgmt_service_client(
        cli_ctx, ResourceType.MGMT_CONTAINERREGISTRY
    ).registries
