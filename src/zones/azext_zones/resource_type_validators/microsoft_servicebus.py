from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.servicebus')
class microsoft_servicebus:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_servicebus")
        _logger.debug(
            "Validating Microsoft.servicebus resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'namespaces':
                # servicebus namespaces are always zone redundant
                return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown
