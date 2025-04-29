from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.apimanagement')
class microsoft_apimanagement:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_apimanagement")
        _logger.debug(
            "Validating Microsoft.apimanagement resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'gateways':
                # ZR state of the gateway is defined on the service level
                return ZoneRedundancyValidationResult.Dependent

            case 'service':
                # API Management instances are zone redundant if they are premium and have more than one zone
                # https://learn.microsoft.com/azure/api-management/high-availability#availability-zones
                zones = resource.get('zones') or []
                if len(zones) > 1 and resource['sku']['name'] == 'Premium':
                    return ZoneRedundancyValidationResult.Yes
                else:
                    return ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
