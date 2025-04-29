from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.dbforpostgresql')
class microsoft_dbforpostgresql:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_dbforpostgresql")
        _logger.debug(
            "Validating Microsoft.dbforpostgresql resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'flexibleservers':

                if resource['properties'].get('highAvailability', {}).get(
                        'mode', {}) == 'ZoneRedundant':
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
