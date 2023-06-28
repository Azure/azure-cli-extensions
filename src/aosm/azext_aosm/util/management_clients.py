# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Clients for the python SDK along with useful caches."""

from azure.mgmt.resource import ResourceManagementClient
from knack.log import get_logger

from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from typing import Optional


logger = get_logger(__name__)


class ApiClients:
    """A class for API Clients needed throughout."""

    def __init__(
        self,
        aosm_client: HybridNetworkManagementClient,
        resource_client: ResourceManagementClient,
        container_registry_client: Optional[ContainerRegistryManagementClient] = None,
    ):
        """Initialise with clients."""
        self.aosm_client = aosm_client
        self.resource_client = resource_client
        self.container_registry_client = container_registry_client
