from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.cdn')
class microsoft_cdn:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_cdn")   
        _logger.debug("Validating Microsoft.cdn resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'profiles':
                # Cdn profiles are a global service and are zone redundant by default
                return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown
