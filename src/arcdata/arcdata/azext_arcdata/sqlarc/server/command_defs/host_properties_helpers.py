# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.sqlarc.common.helpers import convert_string_to_bool
from azext_arcdata.sqlarc.server.constants import (
    valid_license_types
)


def update_license_type(config, value):
    """
    This function updates extension config for license type.
    """
    # Validate the provided license type value
    if value not in valid_license_types:
        valid_license_types_str = ", ".join(valid_license_types)
        raise ValueError(
            f"Invalid license type. The valid license types are: {valid_license_types_str}."
        )

    if not is_host_property_present(config, "LicenseType"):
        config["properties"]["settings"]["LicenseType"] = ""

    # Update the license type in the configuration
    config["properties"]["settings"]["LicenseType"] = value

    # Checking for esu and license type compatibility
    check_license_type_and_esu_compatible(config)

    return config


def update_esu_enabled(config, value):
    """
    This function updates extension config for esu.
    """
    value = value.lower().strip()

    if value != "true" and value != "false":
        raise ValueError("ESU value must be 'true' or 'false'.")

    if not is_host_property_present(config, "enableExtendedSecurityUpdates"):
        config["properties"]["settings"][
            "enableExtendedSecurityUpdates"
        ] = False

    # Update the value of esu enabled in the configuration
    value = convert_string_to_bool(value)
    config["properties"]["settings"]["enableExtendedSecurityUpdates"] = value

    # Checking for esu and license type compatibility
    check_license_type_and_esu_compatible(config)

    return config


def update_excluded_instances_list(config, value):
    """
    This function updates extension config for excluded instances list.
    """
    # Ensure the skip_instances field exists in the config
    if not is_host_property_present(config, "ExcludedSqlInstances"):
        config["properties"]["settings"]["ExcludedSqlInstances"] = []

    # Append new instances to the existing list, avoiding duplicates
    for instance in value:
        if (
            instance
            not in config["properties"]["settings"]["ExcludedSqlInstances"]
        ):
            config["properties"]["settings"]["ExcludedSqlInstances"].append(
                instance
            )

    return config


def check_license_type_and_esu_compatible(config):
    """
    This function checks if the provided license type is compatible with the ESU setting.
    """
    license_type = "Undefined"
    esu_enabled = False

    # Check if the LicenseType property is present in the settings
    if is_host_property_present(config, "LicenseType"):
        license_type = config["properties"]["settings"]["LicenseType"]

        # Check if ESU is enabled
        if is_host_property_present(config, "enableExtendedSecurityUpdates"):
            esu_enabled = config["properties"]["settings"][
                "enableExtendedSecurityUpdates"
            ]

        # If ESU is enabled and license type is LicenseOnly, raise an error
        if esu_enabled and license_type == "LicenseOnly":
            raise ValueError(
                "LicenseType 'LicenseOnly' does not support enabling Extended Security Updates (ESU)."
            )
    else:
        # If LicenseType property is not present, raise an error
        raise ValueError(
            "LicenseType property is not present in the extension configuration."
        )


def is_host_property_present(config, property_name):
    """
    This function checks if host property is present in extension config.
    Returns true of present else false.
    """
    if property_name in config["properties"]["settings"]:
        return True

    return False


def is_settings_empty(config):
    """
    This function checks if settings object is present in extension config.
    """
    if "settings" in config["properties"]:
        return False

    return True
