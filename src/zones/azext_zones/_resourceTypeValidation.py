# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum
from knack.log import get_logger

resource_type_validators = {}
__logger = get_logger(__name__)


# This is the decorator to register resource type validators:
def register_resource_type(resourceType):
    __logger.debug("Registering resource type validator for %s", resourceType)

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


def load_validators():
    # Import all the resource type validator modules dynamically:
    validators_dir = Path(__file__).parent / "resource_type_validators"
    __logger.debug("Starting resource type validator module import from %s", validators_dir)

    if len(resource_type_validators) > 0:
        __logger.debug("Resource type validators already loaded, skipping import.")
        return

    try:
        if validators_dir.exists():
            for file in validators_dir.glob("*.py"):
                if file.name != "__init__.py":
                    try:
                        __logger.debug("Importing resource type validator module: %s", file.name)
                        module_name = f".resource_type_validators.{file.stem}"
                        importlib.import_module(module_name, package=__package__)
                    except ImportError as e:
                        __logger.warning("Failed to import module %s: %s", module_name, str(e))
        else:
            __logger.error("Resource type validators directory not found: %s", validators_dir)

    except Exception as e:  # pylint: disable=broad-except
        __logger.warning("Error scanning for resource type validator modules: %s", str(e))


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
