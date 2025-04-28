from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.kusto')
class microsoft_kusto:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_kusto")
        _logger.debug(
            "Validating Microsoft.kusto resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'clusters':
                # AKS clusters are zone redundant if the node pools are spread across multiple zones
                # Zone Redundancy on AKS involves a lot of configuration steps, testing is required beyond this script.
                # https://learn.microsoft.com/azure/aks/availability-zones-overview
                zones = resource.get('zones') or []
                return ZoneRedundancyValidationResult.Yes if len(
                    zones) > 1 else ZoneRedundancyValidationResult.No

        return ZoneRedundancyValidationResult.Unknown
