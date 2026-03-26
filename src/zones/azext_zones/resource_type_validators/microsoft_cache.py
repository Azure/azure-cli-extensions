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
@register_resource_type("microsoft.cache")
class microsoft_cache:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_cache")
        _logger.debug("Validating Microsoft.cache resource type: %s", resourceSubType)

        # Redis
        if resourceSubType == "redis":
            # Redis caches are zone redundant if they are premium SKU and have more than one zone set
            # https://learn.microsoft.com/azure/azure-cache-for-redis/cache-high-availability#zone-redundancy
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Redis Enterprise
        if resourceSubType == "redisenterprise":
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
