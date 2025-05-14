# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


@register_resource_type("microsoft.dbformysql")
class microsoft_mysql:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_dbformysql")
        _logger.debug("Validating Microsoft.mysql resource type: %s", resourceSubType)

        # Azure Database for MySQL
        if resourceSubType == "flexibleservers":
            haConfig = (
                resource["properties"].get("highAvailability", {}).get("mode", {})
            )
            if haConfig == "ZoneRedundant":
                return ZoneRedundancyValidationResult.Yes
            else:
                return ZoneRedundancyValidationResult.No

        # Azure Database for MySQL Single Servers
        if resourceSubType == "servers":
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
