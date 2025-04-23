from ..resourceTypeValidation import ZoneRedundancyValidationResult, register_resource_type
# from knack.log import get_logger
# __logger = get_logger(__name__)

@register_resource_type('microsoft.storage')
class microsoft_storage_storageAccount:
    
    @staticmethod
    def validate(resource):
        resourceSubType = resource['type'].split('/')[1]

        resourceTypes = {
            'storageaccounts':
                # Storage accounts are zone redundant if they are in the ZRS SKU
                ZoneRedundancyValidationResult.Yes if resource['sku']['name'] == 'Standard_ZRS' else ZoneRedundancyValidationResult.No
        }

        return resourceTypes.get(resourceSubType, ZoneRedundancyValidationResult.Unknown)