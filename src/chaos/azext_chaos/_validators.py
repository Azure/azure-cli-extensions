# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import re

from knack.util import CLIError


# ARM resource IDs start with `/subscriptions/<guid>` and may continue
# with deeper path segments (resource group, provider, child resources).
_ARM_SCOPE_PATTERN = re.compile(
    r'^/subscriptions/'
    r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    r'(/.*)?$'
)


def validate_scope(namespace):
    """Validate that --scopes values are well-formed ARM resource IDs.

    Each scope must start with ``/subscriptions/`` followed by a subscription
    GUID and optionally deeper path segments (resource group, provider, etc.).
    """
    scopes = getattr(namespace, 'scopes', None)
    if not scopes:
        return
    for scope in scopes:
        if not scope or not _ARM_SCOPE_PATTERN.match(scope):
            raise CLIError(
                f"Invalid ARM resource ID: '{scope}'. Each scope must be a "
                "fully qualified ARM resource ID starting with "
                "'/subscriptions/<subscription-id>', where <subscription-id> "
                "is a GUID."
            )


def validate_parameters_json(namespace):
    """Validate and parse the --parameters argument.

    Accepts either ``@filename.json`` (file reference) or a raw JSON string,
    following the same convention as ``az rest --body``.  The parsed Python
    object replaces the raw string on *namespace.parameters* so downstream
    code receives a dict/list, not a string.
    """
    value = getattr(namespace, 'parameters', None)
    if not value:
        return

    if value.startswith('@'):
        file_path = value[1:]
        if not os.path.isfile(file_path):
            raise CLIError(
                f"Parameters file not found: '{file_path}'."
            )
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                namespace.parameters = json.load(f)
            except json.JSONDecodeError as exc:
                raise CLIError(
                    f"Invalid JSON in parameters file '{file_path}': {exc}"
                ) from exc
    else:
        try:
            namespace.parameters = json.loads(value)
        except json.JSONDecodeError as exc:
            raise CLIError(
                f"Invalid JSON for --parameters: {exc}"
            ) from exc
