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
@register_resource_type("microsoft.servicebus")
class microsoft_servicebus:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_servicebus")
        _logger.debug(
            "Validating Microsoft.servicebus resource type: %s", resourceSubType
        )

        # Service Bus Namespaces
        if resourceSubType == "namespaces":
            # servicebus namespaces are always zone redundant
            return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown
