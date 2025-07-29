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
@register_resource_type("microsoft.managedidentity")
class microsoft_managedidentity:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_managedidentity")
        _logger.debug(
            "Validating Microsoft.managedidentity resource type: %s", resourceSubType
        )

        # managedidentity resources are zone redundant by default
        return ZoneRedundancyValidationResult.Always
