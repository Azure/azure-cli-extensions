from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.app')
class microsoft_app:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_app")   
        _logger.debug("Validating Microsoft.app resource type: %s", resourceSubType)
        
        match resourceSubType:
            case 'containerapps':
                # Container apps are zone redundant if they are hosted on a zone redundant managedEnvironment
                return ZoneRedundancyValidationResult.Dependent
            
            case 'managedenvironments':
                # Managed Environments are zone redundant if the zoneRedundant property is set to true
                # https://learn.microsoft.com/azure/reliability/reliability-azure-container-apps#availability-zone-support
                return ZoneRedundancyValidationResult.Yes if resource['properties'].get('zoneRedundant', {}) == True \
                    else ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
