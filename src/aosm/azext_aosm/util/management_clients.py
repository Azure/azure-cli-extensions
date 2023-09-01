# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Clients for the python SDK along with useful caches."""

from dataclasses import dataclass

from azure.mgmt.resource import ResourceManagementClient
from knack.log import get_logger

from azext_aosm.vendored_sdks import HybridNetworkManagementClient

logger = get_logger(__name__)


@dataclass
class ApiClients:
    """A class for API Clients needed throughout."""

    aosm_client: HybridNetworkManagementClient
    resource_client: ResourceManagementClient
