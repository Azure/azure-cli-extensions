from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.documentdb')
class microsoft_documentdb:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_documentdb")
        _logger.debug(
            "Validating Microsoft.documentdb resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'databaseaccounts':
                # https://learn.microsoft.com/en-us/azure/reliability/reliability-cosmos-db-nosql
                # CosmosDB databases are zone redundant if then have the
                # setting enabled on the region
                return ZoneRedundancyValidationResult.Yes if resource['properties'][
                    'locations'][0]['isZoneRedundant'] else ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
