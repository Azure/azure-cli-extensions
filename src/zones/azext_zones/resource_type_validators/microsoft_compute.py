from .._resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
from knack.log import get_logger


@register_resource_type('microsoft.compute')
class microsoft_compute:

    @staticmethod
    def validate(resource):
        resourceType = resource['type']
        resourceSubType = resourceType[resourceType.index('/') + 1:]

        _logger = get_logger("microsoft_compute")
        _logger.debug(
            "Validating Microsoft.Compute resource type: %s",
            resourceSubType)

        match resourceSubType:
            case 'disks':
                zones = resource.get('zones') or []
                if len(zones) > 1:
                    return ZoneRedundancyValidationResult.Yes 
                else:
                    return ZoneRedundancyValidationResult.No

            case 'virtualmachinescalesets':
                # VMSS is ZR if deployed to more than one zone
                zones = resource.get('zones') or []
                if len(zones) > 1:
                    return ZoneRedundancyValidationResult.Yes 
                else:
                    return ZoneRedundancyValidationResult.No

            case 'virtualmachines':
                # VM is ZR if deployed to more than one zone
                zones = resource.get('zones') or []
                if len(zones) > 1:
                    return ZoneRedundancyValidationResult.Yes 
                else:
                    return ZoneRedundancyValidationResult.No

            case 'virtualmachines/extensions':
                # VM extensions are zone redundant if the VM they are attached
                # to is zone redundant
                return ZoneRedundancyValidationResult.Dependent

        return ZoneRedundancyValidationResult.Unknown
