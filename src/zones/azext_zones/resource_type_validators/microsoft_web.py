from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.web')
class microsoft_web:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_web")   
        _logger.debug("Validating Microsoft.web resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'serverfarms':
                # App Service Plans are zone redundant if they have zone redundancy enabled and have more than one instance
                # https://learn.microsoft.com/azure/reliability/reliability-app-service?pivots=free-shared-basic#availability-zone-support
                zrEnabled = resource['properties'].get('zoneRedundant', False)
                instanceCount = resource['sku'].get('capacity', 0)
                return ZoneRedundancyValidationResult.Yes if zrEnabled and instanceCount > 1 else ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown