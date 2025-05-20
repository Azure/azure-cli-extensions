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
@register_resource_type("microsoft.signalrservice")
class microsoft_signalrservice:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_signalrservice")
        _logger.debug(
            "Validating Microsoft.signalrservice resource type: %s", resourceSubType
        )

        # SignalR Service
        if resourceSubType == "signalr":
            # SignalR is zone redundant by default on premium tiers
            # https://learn.microsoft.com/azure/azure-signalr/availability-zones
            if resource["sku"]["name"] == "Premium":
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
