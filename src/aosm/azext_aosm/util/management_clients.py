# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Clients for the python SDK along with useful caches."""

from knack.log import get_logger
from dataclasses import dataclass
from azure.mgmt.resource import ResourceManagementClient
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from typing import Dict, Optional
from azure.mgmt.resource.resources.v2022_09_01.models import Provider

logger = get_logger(__name__)


@dataclass
class ProviderInfo:
    """Class to return Provider Info information."""

    namespace: str
    resource_type: str


class ApiClientsAndCaches:
    """A cache for API Clients and API versions for various resources."""

    def __init__(
        self,
        aosm_client: HybridNetworkManagementClient,
        resource_client: ResourceManagementClient,
    ):
        self.aosm_client = aosm_client
        self.resource_client = resource_client

        # We need to find an Azure API version relevant to each resource type. This is
        # used in resource finding. We just use the latest and cache these as they are
        # expensive to query.
        self.resource_type_api_versions_cache: Dict[str, str] = {}
        self.providers_cache: Dict[str, Provider] = {}

    def find_latest_api_ver_for_resource_type(
        self, resource_type: str
    ) -> Optional[str]:
        """
        Copied from virtutils.  Turns out maybe not needed yet. Expect we will need
        when we want to delete resources.

        Find the latest Azure API version for a given resource.

        We do this querying the Azure Providers API

        We just use the latest and cache these as they are expensive to query.

        param: resource_type: String in the format that the providers API uses e.g.
        Microsoft.Compute/disks or Microsoft.Compute/virtualMachines/extensions

        Find the namespace and resource type in the format that the providers
        API uses by splitting the resource type returned from list_by_resource_group
        at the first forward-slash (/),
        e.g. Microsoft.Compute/disks would give us namespace Microsoft.Compute and
        provider resource type disks
        whereas Microsoft.Compute/virtualMachines/extensions would give us
        namespace Microsoft.Compute and provicer resource type
        virtualMachines/extensions.  This seems to match what the provider API
        uses.

        We cache values as this can take a few seconds to return.

        :param resource: A resource, as returned from list_by_resource_group
        :raises RuntimeError: If no provider found in Azure for this resource
        :raises RuntimeError: If the resource type is an unexpected format
        """
        logger.debug(f"Find API version for {resource_type}")
        # We need to find an API version relevant to the resource.
        if resource_type in self.resource_type_api_versions_cache.keys():
            # We have one cached, just return that
            logger.debug("Return cached API version")
            return self.resource_type_api_versions_cache.get(resource_type)

        # Start with e.g. Microsoft.Compute/disks (resource_type)
        assert resource_type is not None
        prov_info = self.get_provider_info(resource_type)
        # We now have Microsoft.Compute and disks
        if prov_info.namespace not in self.providers_cache.keys():
            # Get the provider e.g. Microsoft.Compute
            logger.debug(f"Find provider {prov_info.namespace}")
            try:
                provider = self.resource_client.providers.get(prov_info.namespace)
            except Exception as provEx:
                raise RuntimeError(
                    f"Could not find provider {prov_info.namespace} required "
                    f"to query resource of type {resource_type}. Aborting"
                ) from provEx

            self.providers_cache[prov_info.namespace] = provider
        else:
            # Resource type that we haven't found before but the provider is cached
            # so use that.
            provider = self.providers_cache[prov_info.namespace]

        # Iterate through the providers resource types and find the one
        # we want, e.g. disks or virtualMachines/extensions
        for res_type in provider.resource_types:
            if res_type.resource_type == prov_info.resource_type:
                # Find the latest API version and cache it
                # The first index appears to always be the latest version
                api_version = res_type.api_versions[0]
                logger.debug(f"Use API version {api_version} for {resource_type}")

                assert resource_type is not None
                self.resource_type_api_versions_cache[resource_type] = api_version
                return api_version

        raise RuntimeError(
            f"Azure API did not return an API version for {resource_type}."
            f"Cannot query API version"
        )

    def get_provider_info(self, resource_type: str) -> ProviderInfo:
        """
        Find provider namespace and resource_type, given a full resource_type.

        param: resource_type: String in the format that the providers API uses e.g.
        Microsoft.Compute/disks or Microsoft.Compute/virtualMachines/extensions

        Find the namespace and resource type in the format that the providers
        API uses by splitting the resource type returned from list_by_resource_group
        at the first forward-slash (/),
        e.g. Microsoft.Compute/disks would give us namespace Microsoft.Compute and
        provider resource type disks
        whereas Microsoft.Compute/virtualMachines/extensions would give us
        namespace Microsoft.Compute and provicer resource type
        virtualMachines/extensions.  This seems to match what the provider API
        uses.
        """
        prov_namespace_type = resource_type.split("/", 1)
        if len(prov_namespace_type) != 2:
            raise RuntimeError(
                f"Azure resource type {resource_type} "
                "is in unexpected format. Cannot find API version."
            )
        # print(f"Namespace {prov_namespace_type[0]} type {prov_namespace_type[1]}")
        return ProviderInfo(prov_namespace_type[0], prov_namespace_type[1])
