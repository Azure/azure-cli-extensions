# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import re

from knack.util import CLIError


# Workspace scopes are ARM resource identifiers. The service accepts a
# subscription, resource group, individual resource, or service group (the
# backend has no scope-type allow-list — it accepts any parseable ARM ID).
# We accept the two structural roots that cover all of those:
#   - ``/subscriptions/<guid>[/...]``  → subscription, resource group, resource
#   - ``/providers/Microsoft.Management/serviceGroups/<name>`` → service group
_ARM_SCOPE_PATTERN = re.compile(
    r'^/subscriptions/'
    r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    r'(/.*)?$'
)
_SERVICE_GROUP_SCOPE_PATTERN = re.compile(
    r'^/providers/Microsoft\.Management/serviceGroups/[^/]+/?$',
    re.IGNORECASE,
)


def _is_valid_scope(scope):
    """Return True if *scope* is a workspace-targetable ARM resource ID."""
    return bool(
        scope
        and (_ARM_SCOPE_PATTERN.match(scope)
             or _SERVICE_GROUP_SCOPE_PATTERN.match(scope))
    )


def validate_scope(namespace):
    """Validate that --scopes values are well-formed ARM resource IDs.

    Accepts either a subscription-rooted ARM ID (``/subscriptions/<guid>`` and
    optionally deeper — resource group or individual resource) or a
    service-group ARM ID (``/providers/Microsoft.Management/serviceGroups/
    <name>``). The error message advertises only the portal-supported scope
    types (subscription, resource group, service group); deeper
    subscription-rooted IDs (individual resources) are accepted but not
    surfaced, to stay aligned with the portal without going out of our way to
    block what the service accepts.
    """
    scopes = getattr(namespace, 'scopes', None)
    if not scopes:
        return
    for scope in scopes:
        if not _is_valid_scope(scope):
            raise CLIError(
                f"Invalid ARM resource ID: '{scope}'. Each scope must be a "
                "fully qualified ARM resource ID for a subscription "
                "('/subscriptions/<subscription-id>'), resource group "
                "('/subscriptions/<subscription-id>/resourceGroups/<name>'), "
                "or service group "
                "('/providers/Microsoft.Management/serviceGroups/<name>')."
            )


def validate_user_assigned(namespace):
    """Validate that --user-assigned values are user-assigned identity IDs.

    Each value must be a fully qualified ARM resource ID for a
    ``Microsoft.ManagedIdentity/userAssignedIdentities`` resource.
    """
    identities = getattr(namespace, 'user_assigned', None)
    if not identities:
        return
    for identity in identities:
        if (not identity
                or not _ARM_SCOPE_PATTERN.match(identity)
                or 'microsoft.managedidentity/userassignedidentities/'
                not in identity.lower()):
            raise CLIError(
                f"Invalid user-assigned identity ID: '{identity}'. Each value "
                "must be a fully qualified ARM resource ID of the form "
                "'/subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/"
                "Microsoft.ManagedIdentity/userAssignedIdentities/<name>'."
            )


_PARAMETERS_FORMAT_HINT = (
    "Expected a JSON array of {key, value} objects, e.g. "
    "--parameters \"[{key:duration,value:PT10M}]\", or a file reference "
    "--parameters @params.json containing that array. Note: a bare "
    "key=value string or a JSON object ({...}) is not accepted."
)


def validate_parameters_json(namespace):
    """Validate and parse the --parameters argument.

    Accepts either ``@filename.json`` (file reference) or a raw JSON string
    that decodes to a JSON array of ``{key, value}`` objects. The parsed Python
    object replaces the raw string on *namespace.parameters* so downstream code
    receives a list, not a string. Surfaces a format hint on every failure so
    the accepted shape is discoverable from the error alone.
    """
    value = getattr(namespace, 'parameters', None)
    if not value:
        return

    if value.startswith('@'):
        file_path = value[1:]
        if not os.path.isfile(file_path):
            raise CLIError(
                f"Parameters file not found: '{file_path}'. "
                f"{_PARAMETERS_FORMAT_HINT}"
            )
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                parsed = json.load(f)
            except json.JSONDecodeError as exc:
                raise CLIError(
                    f"Invalid JSON in parameters file '{file_path}': {exc}. "
                    f"{_PARAMETERS_FORMAT_HINT}"
                ) from exc
    else:
        # Catch the most common non-JSON mistake (key=value) with a targeted
        # message before the generic JSON parse error.
        if '=' in value and not value.lstrip().startswith(('[', '{')):
            raise CLIError(
                f"Invalid --parameters value: '{value}'. "
                f"{_PARAMETERS_FORMAT_HINT}"
            )
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise CLIError(
                f"Invalid JSON for --parameters: {exc}. "
                f"{_PARAMETERS_FORMAT_HINT}"
            ) from exc

    if not isinstance(parsed, list) or not all(
        isinstance(item, dict) and 'key' in item and 'value' in item
        for item in parsed
    ):
        raise CLIError(
            f"Invalid --parameters shape. {_PARAMETERS_FORMAT_HINT}"
        )
    namespace.parameters = parsed
