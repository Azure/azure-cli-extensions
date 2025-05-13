# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


@register_resource_type("microsoft.dashboard")
class microsoft_dashboard:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_dashboard")
        _logger.debug(
            "Validating Microsoft.dashboard resource type: %s", resourceSubType
        )

        # Azure Managed Grafana
        if resourceSubType == "grafana":
            zr = resource.get("properties", {}).get("zoneRedundancy", "")
            if zr == "Enabled":
                return ZoneRedundancyValidationResult.Yes
            else:
                return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
