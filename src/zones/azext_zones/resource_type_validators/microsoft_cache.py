from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.cache')
class microsoft_cache:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_cache")   
        _logger.debug("Validating Microsoft.cache resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'redis':
                # Redis caches are zone redundant if they are premium SKU and have more than one zone set
                # https://learn.microsoft.com/azure/azure-cache-for-redis/cache-high-availability#zone-redundancy
                return ZoneRedundancyValidationResult.Yes if resource['zones'] is not None \
                    and len(resource['zones']) > 1 \
                    and resource['sku']['name'] == 'Premium' \
                    else ZoneRedundancyValidationResult.No

            case 'redisenterprise':
                return ZoneRedundancyValidationResult.Yes if resource['zones'] is not None \
                    and len(resource['zones']) > 1 \
                    else ZoneRedundancyValidationResult.No
            
        return ZoneRedundancyValidationResult.Unknown