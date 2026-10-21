# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
"""Reusable assertion message builders for scenario tests."""


def expected_actual_message(context, field_name, expected, actual, payload=None):
    """Build a consistent expected-vs-actual assertion message."""
    message = (
        f"{context}: unexpected value for '{field_name}'. "
        f"Expected {expected!r}, got {actual!r}."
    )
    if payload is not None:
        message += f" Payload: {payload!r}"
    return message


def missing_field_message(context, field_name, payload=None):
    """Build a consistent message for missing required field assertions."""
    message = f"{context}: missing required field '{field_name}'."
    if payload is not None:
        message += f" Payload: {payload!r}"
    return message


def invalid_value_message(context, field_name, actual, expectation_text, payload=None):
    """Build a consistent message for predicate-based assertions."""
    message = (
        f"{context}: invalid value for '{field_name}'. "
        f"Actual: {actual!r}. Expected: {expectation_text}."
    )
    if payload is not None:
        message += f" Payload: {payload!r}"
    return message


def properties_key_mismatch_message(key_name):
    """Return only the properties key for concise mismatch output."""
    return key_name
