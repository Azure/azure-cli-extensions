from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.loadtestservice')
class microsoft_loadtestservice:
    
    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_loadtestservice")   
        _logger.debug("Validating Microsoft.loadtestservice resource type: %s", resourceSubType)

        # loadtestservice resources are never zone redundant
        return ZoneRedundancyValidationResult.Never
