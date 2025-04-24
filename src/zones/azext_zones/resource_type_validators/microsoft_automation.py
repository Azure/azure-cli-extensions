from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.automation')
class microsoft_automation:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_automation")   
        _logger.debug("Validating Microsoft.automation resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'automationaccounts':
                # Automation accounts are zone redundant by default
                # https://learn.microsoft.com/azure/automation/automation-availability-zones
                return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown