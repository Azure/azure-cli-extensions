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
@register_resource_type("microsoft.botservice")
class microsoft_botservice:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_botservice")
        _logger.debug(
            "Validating Microsoft.botservice resource type: %s", resourceSubType
        )

        # Bot Services
        if resourceSubType == "botservices":
            # Bot services are ZR only in west europe and
            #  only if they are configured as a regional (not global) bot.
            if resource["location"] == "westeurope":
                # https://learn.microsoft.com/azure/reliability/reliability-bot
                _logger.warning(
                    "Your bot service resource in westeurope may be zone redundant, \
                    but only if it's configured as a regional (not global) bot. Please check manually."
                )
                return ZoneRedundancyValidationResult.Unknown
            # Bot services cannot be ZR in any other region
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
