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
@register_resource_type("microsoft.chaos")
class microsoft_chaos:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_chaos")
        _logger.debug("Validating Microsoft.chaos resource type: %s", resourceSubType)

        # chaos profiles are always zone redundant
        # https://learn.microsoft.com/azure/reliability/reliability-chaos-studio#availability-zone-support
        return ZoneRedundancyValidationResult.Always
