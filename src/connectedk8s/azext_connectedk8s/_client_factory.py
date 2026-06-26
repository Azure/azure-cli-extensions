# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import os
from collections import namedtuple
from typing import TYPE_CHECKING, Any

import requests
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ValidationError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType

import azext_connectedk8s._constants as consts

if TYPE_CHECKING:
    from azure.cli.core import AzCli
    from azure.mgmt.hybridcompute.operations import PrivateLinkScopesOperations
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.resource.resources.v2022_09_01.operations import (
        ProvidersOperations,
        ResourceGroupsOperations,
    )

    from azext_connectedk8s.vendored_sdks import ConnectedKubernetesClient
    from azext_connectedk8s.vendored_sdks.operations import ConnectedClusterOperations
    from azext_connectedk8s.vendored_sdks.preview_2025_08_01 import (
        KubernetesClient as ConnectedKubernetesClient20250801,
    )
    from azext_connectedk8s.vendored_sdks.preview_2025_08_01.operations import (
        ConnectedClusterOperations as ConnectedClusterOperations20250801,
    )

AccessToken = namedtuple("AccessToken", ["token", "expires_on"])


def cf_connectedk8s(cli_ctx: AzCli, *_: Any) -> ConnectedKubernetesClient:
    from azext_connectedk8s.vendored_sdks import ConnectedKubernetesClient

    client: ConnectedKubernetesClient
    access_token = os.getenv(consts.Azure_Access_Token_Variable)
    if access_token is not None:
        validate_custom_token()
        credential = AccessTokenCredential(access_token=access_token)
        client = get_mgmt_service_client(
            cli_ctx,
            ConnectedKubernetesClient,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
            credential=credential,
        )
        return client

    client = get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient)
    return client


def cf_connected_cluster(cli_ctx: AzCli, _: Any) -> ConnectedClusterOperations:
    return cf_connectedk8s(cli_ctx).connected_cluster


def cf_connectedk8s_prev_2025_08_01(
    cli_ctx: AzCli, *_: Any
) -> ConnectedKubernetesClient20250801:
    from azure.core.pipeline.policies import HeadersPolicy

    from azext_connectedk8s.vendored_sdks.preview_2025_08_01 import (
        KubernetesClient,
    )

    # Create custom headers policy for PUT requests
    headers_policy = HeadersPolicy({"x-ms-azurearc-cli": "true"})

    client: KubernetesClient
    access_token = os.getenv(consts.Azure_Access_Token_Variable)
    if access_token is not None:
        validate_custom_token()
        credential = AccessTokenCredential(access_token=access_token)
        client = get_mgmt_service_client(
            cli_ctx,
            KubernetesClient,
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
            credential=credential,
            per_call_policies=[headers_policy],
        )
        return client

    client = get_mgmt_service_client(
        cli_ctx,
        KubernetesClient,
        per_call_policies=[headers_policy],
    )
    return client


def cf_connected_cluster_prev_2025_08_01(
    cli_ctx: AzCli, _: Any
) -> ConnectedClusterOperations20250801:
    return cf_connectedk8s_prev_2025_08_01(cli_ctx).connected_cluster


def cf_connectedmachine(
    cli_ctx: AzCli, subscription_id: str | None
) -> PrivateLinkScopesOperations:
    from azure.mgmt.hybridcompute import HybridComputeManagementClient

    client: HybridComputeManagementClient
    access_token = os.getenv(consts.Azure_Access_Token_Variable)
    if access_token is not None:
        credential = AccessTokenCredential(access_token=access_token)
        client = get_mgmt_service_client(
            cli_ctx,
            HybridComputeManagementClient,
            subscription_id=subscription_id,
            credential=credential,
        )
        return client.private_link_scopes

    client = get_mgmt_service_client(
        cli_ctx, HybridComputeManagementClient, subscription_id=subscription_id
    )
    return client.private_link_scopes


def cf_resource_groups(
    cli_ctx: AzCli, subscription_id: str | None = None
) -> ResourceGroupsOperations:
    resource_groups: ResourceGroupsOperations = _resource_client_factory(
        cli_ctx, subscription_id
    ).resource_groups
    return resource_groups


def _resource_client_factory(
    cli_ctx: AzCli, subscription_id: str | None = None
) -> ResourceManagementClient:
    client: ResourceManagementClient

    access_token = os.getenv(consts.Azure_Access_Token_Variable)
    if access_token is not None:
        credential = AccessTokenCredential(access_token=access_token)
        client = get_mgmt_service_client(
            cli_ctx,
            ResourceType.MGMT_RESOURCE_RESOURCES,
            subscription_id=subscription_id,
            credential=credential,
        )
        return client

    client = get_mgmt_service_client(
        cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id
    )
    return client


def resource_providers_client(
    cli_ctx: AzCli, subscription_id: str | None = None
) -> ProvidersOperations:
    providers: ProvidersOperations = _resource_client_factory(
        cli_ctx, subscription_id
    ).providers
    return providers

    # Alternate: This should also work
    # subscription_id = get_subscription_id(cli_ctx)
    # return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
    # subscription_id=subscription_id).providers


class AccessTokenCredential:
    """Simple access token Authentication. Returns the access token as-is."""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def get_token(self, *arg: Any, **kwargs: Any) -> AccessToken:  # pylint: disable=unused-argument
        import time

        # Assume the access token expires in 60 minutes
        return AccessToken(self.access_token, int(time.time()) + 3600)

    def signed_session(
        self, session: requests.Session | None = None
    ) -> requests.Session:
        session = session or requests.Session()
        header = "{} {}".format("Bearer", self.access_token)
        session.headers["Authorization"] = header
        return session


def validate_custom_token() -> None:
    if os.getenv("AZURE_SUBSCRIPTION_ID") is None:
        telemetry.set_exception(
            exception="Required environment variable 'AZURE_SUBSCRIPTION_ID' is not set, when "
            "using Custom Access Token.",
            fault_type=consts.Custom_Token_Env_Var_Sub_Id_Missing_Fault_Type,
            summary="Required environment variable 'AZURE_SUBSCRIPTION_ID' is not set, when "
            "using Custom Access Token.",
        )
        raise ValidationError(
            "Environment variable 'AZURE_SUBSCRIPTION_ID' should be set when custom access token "
            "is enabled."
        )
