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
@register_resource_type("microsoft.containerregistry")
class microsoft_containerregistry:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_containerregistry")
        _logger.debug(
            "Validating Microsoft.containerregistry resource type: %s", resourceSubType
        )

        # Container Registry
        if resourceSubType == "registries":
            # Container registries are zone redundant if the setting enabled
            # https://learn.microsoft.com/azure/container-registry/zone-redundancy
            if resource["properties"]["zoneRedundancy"] == "Enabled":
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Registry Regional Replications
        if resourceSubType == "registries/replications":
            if resource["properties"]["zoneRedundancy"] == "Enabled":
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
