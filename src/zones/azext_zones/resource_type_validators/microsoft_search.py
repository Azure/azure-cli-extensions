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
@register_resource_type("microsoft.search")
class microsoft_search:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_search")
        _logger.debug("Validating Microsoft.search resource type: %s", resourceSubType)

        # Search Services
        if resourceSubType == "searchservices":
            # Standard or higher tiers in supported regions are zone redundant if the replica count is greater than 1.
            # https://learn.microsoft.com/azure/search/search-reliability#availability-zone-support
            sku = resource["sku"]["name"] or ""
            replicaCount = resource["properties"].get("replicaCount", 0)
            if sku not in ["Free", "Basic"] and replicaCount > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
