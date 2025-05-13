# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


@register_resource_type("microsoft.iothub")
class microsoft_iothub:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_iothub")
        _logger.debug("Validating Microsoft.iothub resource type: %s", resourceSubType)

        # Zone Redundancy is enabled by default for IoT Hubs
        # https://learn.microsoft.com/azure/iot-hub/iot-hub-ha-dr#availability-zones
        return ZoneRedundancyValidationResult.Always
