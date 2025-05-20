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
@register_resource_type("microsoft.automation")
class microsoft_automation:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_automation")
        _logger.debug(
            "Validating Microsoft.automation resource type: %s", resourceSubType
        )

        # Automation accounts are zone redundant by default
        # https://learn.microsoft.com/azure/automation/automation-availability-zones
        return ZoneRedundancyValidationResult.Always
