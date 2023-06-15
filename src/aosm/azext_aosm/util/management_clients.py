# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Clients for the python SDK along with useful caches."""

from azure.mgmt.resource import ResourceManagementClient
from knack.log import get_logger

from azext_aosm.vendored_sdks import HybridNetworkManagementClient

logger = get_logger(__name__)


class ApiClients:
    """A class for API Clients needed throughout."""

    def __init__(
        self,
        aosm_client: HybridNetworkManagementClient,
        resource_client: ResourceManagementClient,
    ):
        """Initialise with clients."""
        self.aosm_client = aosm_client
        self.resource_client = resource_client
