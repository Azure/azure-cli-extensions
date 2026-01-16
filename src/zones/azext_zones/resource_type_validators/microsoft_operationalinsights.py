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
@register_resource_type("microsoft.operationalinsights")
class microsoft_operationalinsights:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_operationalinsights")
        _logger.debug(
            "Validating Microsoft.operationalinsights resource type: %s",
            resourceSubType,
        )

        # Operational Insights workspaces
        if resourceSubType == "workspaces":
            # Operational Insights workspaces are zone redundant by default,
            # Note: Operational Insights workspaces are zone redundant by
            # default only in some regions. Check
            # https://learn.microsoft.com/azure/azure-monitor/logs/availability-zones.
            return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown
