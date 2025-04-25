from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.notificationhubs')
class microsoft_notificationhubs:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_notificationhubs")   
        _logger.debug("Validating Microsoft.notificationhubs resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'namespaces':
                # In a region that supports availability zones, Notification Hubs supports a zone-redundant deployment by default.
                # https://learn.microsoft.com/azure/reliability/reliability-notification-hubs#availability-zone-support
                return ZoneRedundancyValidationResult.Yes if resource['properties'].get('zoneRedundancy', '') == 'Enabled' else ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
