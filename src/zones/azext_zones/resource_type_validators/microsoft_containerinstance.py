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
@register_resource_type("microsoft.containerinstance")
class microsoft_containerinstance:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_containerinstance")
        _logger.debug(
            "Validating Microsoft.containerinstance resource type: %s", resourceSubType
        )

        # Container Instances
        if resourceSubType == "containergroups":
            # Container groups of container instances are zonal resources, so they are never zone redundant
            # https://learn.microsoft.com/azure/reliability/reliability-containers#availability-zone-support
            return ZoneRedundancyValidationResult.Never

        return ZoneRedundancyValidationResult.Unknown
