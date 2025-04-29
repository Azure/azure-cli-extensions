from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.storage')
class microsoft_storage:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_storage")
        _logger.debug(
            "Validating Microsoft.Storage resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'storageaccounts':
                # Storage accounts are zone redundant if they are in the ZRS
                # SKU
                if resource['sku']['name'] == 'Standard_ZRS':
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
