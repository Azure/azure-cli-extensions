# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .._resourceTypeValidation import (
    ZoneRedundancyValidationResult,
    register_resource_type,
)
from knack.log import get_logger


# pylint: disable=too-few-public-methods,too-many-return-statements
@register_resource_type("microsoft.compute")
class microsoft_compute:
    @staticmethod
    def validate(resource):
        resourceType = resource["type"]
        resourceSubType = resourceType[resourceType.index("/") + 1:]

        _logger = get_logger("microsoft_compute")
        _logger.debug("Validating Microsoft.Compute resource type: %s", resourceSubType)

        # Disks
        if resourceSubType == "disks":
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # VM ScaleSets
        if resourceSubType == "virtualmachinescalesets":
            # VMSS is ZR if deployed to more than one zone
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # Virtual Machines
        if resourceSubType == "virtualmachines":
            # VM is ZR if deployed to more than one zone
            zones = resource.get("zones") or []
            if len(zones) > 1:
                return ZoneRedundancyValidationResult.Yes
            return ZoneRedundancyValidationResult.No

        # VM Extensions
        if resourceSubType == "virtualmachines/extensions":
            # VM extensions are zone redundant if the VM they are attached
            # to is zone redundant
            return ZoneRedundancyValidationResult.Dependent

        return ZoneRedundancyValidationResult.Unknown
