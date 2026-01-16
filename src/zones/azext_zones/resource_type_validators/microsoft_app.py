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
@register_resource_type("microsoft.app")
class microsoft_app:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_app")
        _logger.debug("Validating Microsoft.app resource type: %s", resourceSubType)

        # Container Apps
        if resourceSubType == "containerapps":
            # Container apps are zone redundant if they are hosted on a
            # zone redundant managedEnvironment
            return ZoneRedundancyValidationResult.Dependent

        # Container App Jobs
        if resourceSubType == "jobs":
            # Jobs are zone redundant if they are hosted on a
            # zone redundant managedEnvironment
            return ZoneRedundancyValidationResult.Dependent

        # Container Apps Environments
        if resourceSubType == "managedenvironments":
            # Managed Environments are zone redundant if the zoneRedundant property is set to true
            # https://learn.microsoft.com/azure/reliability/reliability-azure-container-apps#availability-zone-support
            if resource["properties"].get("zoneRedundant", {}) is True:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
