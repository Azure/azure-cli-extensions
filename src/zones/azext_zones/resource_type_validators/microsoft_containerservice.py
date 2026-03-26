# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


# pylint: disable=too-few-public-methods
@register_resource_type("microsoft.containerservice")
class microsoft_containerservice:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_containerservice")
        _logger.debug(
            "Validating Microsoft.containerservice resource type: %s", resourceSubType
        )

        # AKS Clusters
        if resourceSubType == "managedclusters":
            # AKS clusters are zone redundant if the node pools are spread across multiple zones
            # Zone Redundancy on AKS involves a lot of configuration steps, testing is required beyond this script.
            # https://learn.microsoft.com/azure/aks/availability-zones-overview
            poolZones = (
                resource["properties"]["agentPoolProfiles"][0].get("availabilityZones")
                or []
            )
            poolZoneCount = len(poolZones)
            if poolZoneCount > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
