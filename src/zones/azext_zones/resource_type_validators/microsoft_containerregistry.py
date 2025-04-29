from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.containerregistry')
class microsoft_containerregistry:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_containerregistry")
        _logger.debug(
            "Validating Microsoft.containerregistry resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'registries':
                # Container registries are zone redundant if the setting enabled
                # https://learn.microsoft.com/azure/container-registry/zone-redundancy
                if resource['properties']['zoneRedundancy'] == 'Enabled':
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

            case 'registries/replications':
                return ZoneRedundancyValidationResult.Dependent

        return ZoneRedundancyValidationResult.Unknown
