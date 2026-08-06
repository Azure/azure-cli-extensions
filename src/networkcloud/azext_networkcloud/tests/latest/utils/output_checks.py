# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
"""
Helper utilities for verifying command output in tests.
Provides common check patterns for Network Cloud resource operations.
"""
import json
import re

_VALID_PROVISIONING_STATES = ["Succeeded", "Accepted", "Updating", "Failed", "Canceled"]


def _raise_if_false(condition, message):
    """Raise an assertion with actionable context when a check fails."""
    if not condition:
        raise AssertionError(message)
    return True


def _id_is_resource_id(value):
    return _raise_if_false(
        value is not None and isinstance(value, str) and value.startswith("/"),
        f"Expected 'id' to be a non-empty ARM resource ID starting with '/'. Actual: {value!r}",
    )


def _type_contains_networkcloud(value):
    return _raise_if_false(
        value is not None
        and isinstance(value, str)
        and "Microsoft.NetworkCloud" in value,
        "Expected 'type' to include 'Microsoft.NetworkCloud'. " f"Actual: {value!r}",
    )


def _field_is_not_none(field_name):
    def _predicate(value):
        return _raise_if_false(
            value is not None,
            f"Expected '{field_name}' to be present and non-null. Actual: {value!r}",
        )

    return _predicate


def _valid_provisioning_state(value):
    return _raise_if_false(
        value in _VALID_PROVISIONING_STATES,
        "Expected 'provisioningState' to be one of "
        f"{_VALID_PROVISIONING_STATES}. Actual: {value!r}",
    )


def _list_or_paged_result(value):
    return _raise_if_false(
        isinstance(value, list) or (isinstance(value, dict) and "value" in value),
        "Expected list output to be either a JSON array or an object containing a 'value' array. "
        f"Actual type: {type(value).__name__}, value: {value!r}",
    )


def get_value(test, key):
    return re.sub(r"^['\"]|['\"]$", "", test.kwargs.get(key))


def get_json_string(attribute):
    raw_string = json.dumps(attribute)
    try:
        clean_string = json.loads(f'"{raw_string}"')
    except json.JSONDecodeError:
        # If it is already clean, return as-is
        clean_string = raw_string

    return clean_string


def show_properties(properties):
    """Print the show response properties for debugging test execution."""
    print("Kubernetescluster show properties:")
    print(json.dumps(properties, indent=2, sort_keys=True, default=str))


def get_resource_checks(resource_name=None):
    """Get standard checks for resource create/show operations.

    Verifies that the output contains essential resource properties.

    Args:
        resource_name: The expected resource name (if known)

    Returns:
        List of check tuples for validating resource output
    """
    checks = [
        # Verify the response has required fields
        ("id", None, _id_is_resource_id),
        ("type", None, _type_contains_networkcloud),
        ("name", None, _field_is_not_none("name")),
        ("provisioningState", None, _valid_provisioning_state),
    ]

    if resource_name:
        checks.append(("name", resource_name))

    return checks


def get_list_checks():
    """Get checks for list operations.

    Verifies that list operations return valid structure.

    Returns:
        List of check tuples for validating list output
    """
    return [
        ("[]", None, _list_or_paged_result),
    ]


def get_update_checks(updated_property=None, updated_value=None):
    """Get checks for update operations.

    Verifies that updates are applied correctly.

    Args:
        updated_property: The property that should be updated
        updated_value: The expected value after update

    Returns:
        List of check tuples for validating update output
    """
    checks = [
        ("id", None, _field_is_not_none("id")),
        ("name", None, _field_is_not_none("name")),
    ]

    if updated_property and updated_value:
        checks.append((updated_property, updated_value))

    return checks


class ResourceOutputChecker:
    """Helper class to build output verification checks for tests."""

    def __init__(self):
        self._checks = []

    def add_id_check(self):
        """Add check for resource ID."""
        self._checks.append(("id", None, _id_is_resource_id))
        return self

    def add_name_check(self, expected_name=None):
        """Add check for resource name."""
        if expected_name is not None:
            self._checks.append(("name", expected_name))
        else:
            self._checks.append(("name", None, _field_is_not_none("name")))
        return self

    def add_type_check(self, expected_type=None):
        """Add check for resource type."""
        if expected_type is not None:
            self._checks.append(("type", expected_type))
        else:
            self._checks.append(("type", None, _type_contains_networkcloud))
        return self

    def add_provisioning_state_check(self, expected_state="Succeeded"):
        """Add check for provisioning state."""
        if expected_state is not None:
            self._checks.append(("provisioningState", expected_state))
        else:
            self._checks.append(("provisioningState", None, _valid_provisioning_state))
        return self

    def add_property_check(self, property_name, expected_value=None):
        """Add check for a specific property.

        Args:
            property_name: Name of property to check (dot notation for nested: 'parent.child')
            expected_value: Expected value or None to just check existence
        """
        if expected_value is not None:
            self._checks.append((property_name, expected_value))
        else:
            self._checks.append(
                (property_name, None, _field_is_not_none(property_name))
            )
        return self

    def add_property_exists_check(self, property_name):
        """Add check to verify property exists (regardless of value)."""
        self._checks.append((property_name, None, _field_is_not_none(property_name)))
        return self

    def get_checks(self):
        """Return the accumulated checks list."""
        return self._checks

    def build_create_checks(self, resource_name=None):
        """Build standard checks for create operations."""
        self.add_id_check()
        self.add_name_check(resource_name)
        self.add_type_check()
        self.add_provisioning_state_check("Succeeded")
        return self

    def build_show_checks(self, resource_name=None):
        """Build standard checks for show operations."""
        self.add_id_check()
        self.add_name_check(resource_name)
        self.add_type_check()
        return self

    def build_update_checks(self):
        """Build standard checks for update operations."""
        self.add_id_check()
        self.add_name_check()
        self.add_type_check()
        return self
