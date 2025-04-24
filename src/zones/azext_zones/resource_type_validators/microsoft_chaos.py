from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.chaos')
class microsoft_chaos:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_chaos")   
        _logger.debug("Validating Microsoft.chaos resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'experiments':
                # chaos profiles are always zone redundant
                # https://learn.microsoft.com/azure/reliability/reliability-chaos-studio#availability-zone-support
                return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown
