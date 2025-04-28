from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.maps')
class microsoft_maps:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_maps")
        _logger.debug(
            "Validating Microsoft.maps resource type: %s",
            resourceSubType)

        # maps resources are zone redundant by default
        return ZoneRedundancyValidationResult.Always
