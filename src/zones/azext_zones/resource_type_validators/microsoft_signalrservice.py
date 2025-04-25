from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.signalrservice')
class microsoft_signalrservice:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_signalrservice")   
        _logger.debug("Validating Microsoft.signalrservice resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'signalr':
                # SignalR is zone redundant by default on premium tiers
                # https://learn.microsoft.com/azure/azure-signalr/availability-zones
                return ZoneRedundancyValidationResult.Yes if resource['sku']['name'] == 'Premium' else ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown