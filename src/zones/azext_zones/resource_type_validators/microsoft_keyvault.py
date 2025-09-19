# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


# pylint: disable=too-few-public-methods
@register_resource_type("microsoft.keyvault")
class microsoft_keyvault:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_keyvault")
        _logger.debug(
            "Validating Microsoft.keyvault resource type: %s", resourceSubType
        )

        # Key Vaults
        if resourceSubType == "vaults":
            # Key vaults are zone redundant by default
            # https://learn.microsoft.com/azure/key-vault/general/disaster-recovery-guidance#failover-across-regions
            return ZoneRedundancyValidationResult.Always

        return ZoneRedundancyValidationResult.Unknown
