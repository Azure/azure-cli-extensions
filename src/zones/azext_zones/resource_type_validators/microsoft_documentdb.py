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
@register_resource_type("microsoft.documentdb")
class microsoft_documentdb:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_documentdb")
        _logger.debug(
            "Validating Microsoft.documentdb resource type: %s", resourceSubType
        )

        # CosmosDB SQL API Accounts
        if resourceSubType == "databaseaccounts":
            # https://learn.microsoft.com/en-us/azure/reliability/reliability-cosmos-db-nosql
            # CosmosDB databases are zone redundant if then have the
            # setting enabled on the region
            if resource["properties"]["locations"][0]["isZoneRedundant"]:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # CosmosDB MongoDB API Accounts
        if resourceSubType == "mongoClusters":
            # https://learn.microsoft.com/azure/reliability/reliability-cosmos-mongodb#availability-zone-support
            highAvailability = resource["properties"].get("highAvailability", "")
            if highAvailability.get("targetMode", "") == "ZoneRedundantPreferred":
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
