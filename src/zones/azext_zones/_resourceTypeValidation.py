# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from enum import Enum

resource_type_validators = {}


# This is the decorator to register resource type validators:
def register_resource_type(resourceType):
    def decorator(cls):
        resource_type_validators[resourceType] = cls
        return cls
    return decorator


# This is the factory class to get the appropriate validator based on resource type:
def getResourceTypeValidator(resourceType):
    validator_class = resource_type_validators.get(resourceType)
    if validator_class:
        return validator_class()
    return None


# This is the base class for all resource type validators:
class ResourceTypeValidator(ABC):  # pylint: disable=too-few-public-methods`
    @abstractmethod
    def validate(self):
        pass


class ZoneRedundancyValidationResult(Enum):
    Unknown = 1             # Unable to verify status
    Yes = 2                 # Resource is configured for zone redundancy
    Always = 3              # Resource is always zone redundant
    No = 4                  # Resource is not configured for zone redundancy
    Never = 5               # Resource cannot be configured for zone redundancy
    Dependent = 6           # Resource is zone redundant if parent or related resource is zone redundant
    NoZonesInRegion = 7     # Resource is not zone redundant because the region does not support zones

    @staticmethod
    def to_string(value):
        try:
            # Attempt to create an enum member from the value
            result = ZoneRedundancyValidationResult(value)
            return result.name
        except ValueError:
            # If the value doesn't correspond to any enum member, return "Unknown"
            return "Unknown"
