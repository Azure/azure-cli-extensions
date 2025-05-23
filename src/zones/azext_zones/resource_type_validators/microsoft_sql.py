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
@register_resource_type("microsoft.sql")
class microsoft_sql:
    @staticmethod
    def validate(resource):  # pylint: disable=too-many-return-statements
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_sql")
        _logger.debug("Validating Microsoft.sql resource type: %s", resourceSubType)

        # SQL Databases
        if resourceSubType == "servers/databases":
            # https://learn.microsoft.com/azure/azure-sql/database/high-availability-sla-local-zone-redundancy#high-availability-through-zone-redundancy
            if resource["properties"]["zoneRedundant"]:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # SQL Servers
        if resourceSubType == "servers":
            # Zone Redundancy for SQL is set at the database level, see
            # above
            return ZoneRedundancyValidationResult.Dependent

        # SQL Managed Instances
        if resourceSubType == "managedinstances":
            # SQL MI can be zone redundant if this has been enabled on the resource
            # https://learn.microsoft.com/azure/azure-sql/managed-instance/high-availability-sla-local-zone-redundancy?view=azuresql#zone-redundant-availability
            if resource["properties"].get("zoneRedundant", {}) is True:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # SQL Managed Instance Pools
        if resourceSubType == "instancepools":
            # Instance pools depend on the managed instances within them to
            # be zone redundant
            return ZoneRedundancyValidationResult.Dependent

        return ZoneRedundancyValidationResult.Unknown
