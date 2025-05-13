# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


@register_resource_type("microsoft.eventgrid")
class microsoft_eventgrid:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_eventgrid")
        _logger.debug(
            "Validating Microsoft.eventgrid resource type: %s", resourceSubType
        )

        # EventGrid resources are zone redundant by default
        # https://learn.microsoft.com/azure/reliability/reliability-event-grid#availability-zone-support
        # return ZoneRedundancyValidationResult.Always
        return ZoneRedundancyValidationResult.Always
