# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Normalize configured values for command response assertions."""

import json

from azure.cli.core.aaz._utils import AAZShortHandSyntaxParser


def attr(test, key):
    """Return a configured assertion value without its CLI shell quoting."""
    if key not in test.kwargs or test.kwargs[key] is None:
        raise AssertionError(f"Test variable '{key}' was not set in test.kwargs.")

    value = test.kwargs[key]
    if not isinstance(value, str):
        return value

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]

    if value.startswith(("{", "[")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return AAZShortHandSyntaxParser()(value)
    return value
