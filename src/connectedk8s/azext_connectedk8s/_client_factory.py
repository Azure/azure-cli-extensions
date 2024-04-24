# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.core._profile import Profile
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ValidationError
from azure.cli.core.commands.client_factory import configure_common_settings
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.graphrbac import GraphRbacManagementClient

import os
import requests
import azext_connectedk8s._constants as consts
from collections import namedtuple

AccessToken = namedtuple("AccessToken", ["token", "expires_on"])


def cf_connectedk8s(cli_ctx, *_):
    from azext_connectedk8s.vendored_sdks import ConnectedKubernetesClient
    if os.getenv(consts.Azure_Access_Token_Variable):
        validate_custom_token()
        credential = AccessTokenCredential(access_token=os.getenv(consts.Azure_Access_Token_Variable))
        return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient,
                                       subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
                                       credential=credential)
    return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient)


def cf_connected_cluster(cli_ctx, _):
    return cf_connectedk8s(cli_ctx).connected_cluster


def cf_connectedk8s_prev_2022_10_01(cli_ctx, *_):
    from azext_connectedk8s.vendored_sdks.preview_2022_10_01 import ConnectedKubernetesClient
    if os.getenv(consts.Azure_Access_Token_Variable):
        validate_custom_token()
        credential = AccessTokenCredential(access_token=os.getenv(consts.Azure_Access_Token_Variable))
        return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient,
                                       subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
                                       credential=credential)
    return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient)


def cf_connected_cluster_prev_2022_10_01(cli_ctx, _):
    return cf_connectedk8s_prev_2022_10_01(cli_ctx).connected_cluster


def cf_connectedk8s_prev_2023_11_01(cli_ctx, *_):
    from azext_connectedk8s.vendored_sdks.preview_2023_11_01 import ConnectedKubernetesClient
    if os.getenv(consts.Azure_Access_Token_Variable):
        validate_custom_token()
        credential = AccessTokenCredential(access_token=os.getenv(consts.Azure_Access_Token_Variable))
        return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient,
                                       subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'),
                                       credential=credential)
    return get_mgmt_service_client(cli_ctx, ConnectedKubernetesClient)


def cf_connected_cluster_prev_2023_11_01(cli_ctx, _):
    return cf_connectedk8s_prev_2023_11_01(cli_ctx).connected_cluster


def cf_connectedmachine(cli_ctx, subscription_id):
    from azure.mgmt.hybridcompute import HybridComputeManagementClient
    if os.getenv(consts.Azure_Access_Token_Variable):
        credential = AccessTokenCredential(access_token=os.getenv(consts.Azure_Access_Token_Variable))
        return get_mgmt_service_client(cli_ctx, HybridComputeManagementClient,
                                       subscription_id=subscription_id,
                                       credential=credential).private_link_scopes
    return get_mgmt_service_client(cli_ctx, HybridComputeManagementClient,
                                   subscription_id=subscription_id).private_link_scopes


def cf_resource_groups(cli_ctx, subscription_id=None):
    return _resource_client_factory(cli_ctx, subscription_id).resource_groups


def _resource_client_factory(cli_ctx, subscription_id=None):
    from azure.mgmt.resource import ResourceManagementClient
    if os.getenv(consts.Azure_Access_Token_Variable):
        credential = AccessTokenCredential(access_token=os.getenv(consts.Azure_Access_Token_Variable))
        return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                       subscription_id=subscription_id, credential=credential)
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                   subscription_id=subscription_id)


def resource_providers_client(cli_ctx, subscription_id=None):
    return _resource_client_factory(cli_ctx, subscription_id).providers

    # Alternate: This should also work
    # subscription_id = get_subscription_id(cli_ctx)
    # return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
    # subscription_id=subscription_id).providers


class AccessTokenCredential:
    """Simple access token Authentication. Returns the access token as-is.
    """

    def __init__(self, access_token):
        self.access_token = access_token

    def get_token(self, *arg, **kwargs):
        import time
        # Assume the access token expires in 60 minutes
        return AccessToken(self.access_token, int(time.time()) + 3600)

    def signed_session(self, session=None):
        session = session or requests.Session()
        header = "{} {}".format('Bearer', self.access_token)
        session.headers['Authorization'] = header
        return session


def validate_custom_token():
    if os.getenv('AZURE_SUBSCRIPTION_ID') is None:
        telemetry.set_exception(exception='Required environment variables and parameters are not set',
                                fault_type=consts.Custom_Token_Environments_Fault_Type,
                                summary='Required environment variables and parameters are not set')
        raise ValidationError("Environment variable 'AZURE_SUBSCRIPTION_ID' should be set when custom access token \
            is enabled.")
