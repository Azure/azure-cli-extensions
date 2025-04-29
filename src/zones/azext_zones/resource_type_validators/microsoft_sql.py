from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.sql')
class microsoft_sql:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_sql")
        _logger.debug(
            "Validating Microsoft.sql resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'servers/databases':
                # https://learn.microsoft.com/azure/azure-sql/database/high-availability-sla-local-zone-redundancy#high-availability-through-zone-redundancy
                if resource['properties']['zoneRedundant']:
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

            case 'servers':
                # Zone Redundancy for SQL is set at the database level, see
                # above
                return ZoneRedundancyValidationResult.Dependent

        return ZoneRedundancyValidationResult.Unknown
