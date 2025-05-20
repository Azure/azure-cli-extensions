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
@register_resource_type("microsoft.web")
class microsoft_web:
    @staticmethod
    def validate(resource):  # pylint: disable=too-many-return-statements
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_web")
        _logger.debug("Validating Microsoft.web resource type: %s", resourceSubType)

        # App Service Plans
        if resourceSubType == "serverfarms":
            # App Service Plans are zone redundant if they have zone redundancy enabled and have more than one instance
            # https://learn.microsoft.com/azure/reliability/reliability-app-service?pivots=free-shared-basic#availability-zone-support
            zrEnabled = resource["properties"].get("zoneRedundant", False)
            instanceCount = resource["sku"].get("capacity", 0)
            if zrEnabled and instanceCount > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # App Services
        if resourceSubType == "sites":
            # Web Apps are zone redundant if they are hosted on a zone
            # redundant App Service Plan
            return ZoneRedundancyValidationResult.Dependent

        # Static Web Apps Hosting Environments
        if resourceSubType == "hostingenvironments":
            zrStatus = resource["properties"].get("zoneRedundant", False)
            if zrStatus:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Static Web Apps
        if resourceSubType == "staticsites":
            # Static Web Apps are always zone redundant
            return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown
