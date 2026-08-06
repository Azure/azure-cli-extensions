# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import CustomResourceType

CUSTOM_MGMT_AKS = CustomResourceType('azext_aks_agent.vendored_sdks.azure_mgmt_containerservice.2025_10_01',
                                     'ContainerServiceClient')

# Note: cf_xxx, as the client_factory option value of a command group at command declaration, it should ignore
# parameters other than cli_ctx; get_xxx_client is used as the client of other services in the command implementation,
# and usually accepts subscription_id as a parameter to reconfigure the subscription when sending the request


# container service clients
def get_container_service_client(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_AKS, subscription_id=subscription_id)


def cf_managed_clusters(cli_ctx, *_):
    return get_container_service_client(cli_ctx).managed_clusters
