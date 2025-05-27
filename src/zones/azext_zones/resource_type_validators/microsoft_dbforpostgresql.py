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
@register_resource_type("microsoft.dbforpostgresql")
class microsoft_dbforpostgresql:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_dbforpostgresql")
        _logger.debug(
            "Validating Microsoft.dbforpostgresql resource type: %s", resourceSubType
        )

        # PostgreSQL Flexible Servers
        if resourceSubType == "flexibleservers":
            if (
                resource["properties"].get("highAvailability", {}).get("mode", {})
                == "ZoneRedundant"
            ):
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # PostgreSQL Single Servers
        if resourceSubType == "servers":
            # Zone redundancy is not supported for PostgreSQL Single Servers
            # https://learn.microsoft.com/azure/reliability/reliability-postgresql-flexible-server
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
