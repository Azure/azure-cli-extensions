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
@register_resource_type("microsoft.machinelearningservices")
class microsoft_machinelearningservices:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_machinelearningservices")
        _logger.debug(
            "Validating Microsoft.machinelearningservices resource type: %s",
            resourceSubType,
        )

        # Azure Machine Learning
        if resourceSubType == "workspaces":
            return ZoneRedundancyValidationResult.Never

        return ZoneRedundancyValidationResult.Unknown
