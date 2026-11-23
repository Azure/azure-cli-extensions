# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module

"""Managed identity management for a deployed Logic App.

The runtime resolves identity-based connections through the site identity, so
authoring an identity connection with ``az logicapp connection create`` is only
half the story: the site still needs an identity and a role assignment. These
helpers close that gap without sending the engineer to ``az webapp``.
"""

import json

from azure.cli.core.azclierror import (
    ClientRequestError, HTTPError, RequiredArgumentMissingError, ResourceNotFoundError, ValidationError)

from ._args import flatten_repeatable
from ._managed_api import response_status_from_error
from ._json import strict_json_loads

SITE_API_VERSION = "2022-03-01"

SYSTEM_ASSIGNED = "SystemAssigned"
USER_ASSIGNED = "UserAssigned"
NONE = "None"


def site_url(cmd, resource_group_name, name):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from ._context import _cloud_coordinate

    resource_group_name = _cloud_coordinate(resource_group_name)
    name = _cloud_coordinate(name)
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return (
        "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}"
        "?api-version={}".format(subscription_id, resource_group_name, name, SITE_API_VERSION)
    )


def _send(cmd, method, url, body=None, sender=None):
    from azure.cli.core.util import send_raw_request
    send = sender or send_raw_request
    try:
        response = send(
            cmd.cli_ctx,
            method,
            url,
            body=json.dumps(body) if body is not None else None,
        )
    except HTTPError as ex:
        # Without this, only 'identity show' reported a missing site as exit 3,
        # because custom_show_command adds that mapping for show commands alone.
        # 'assign' and 'remove' exited 1 on the byte-identical ARM 404, so a
        # script could not tell "no such app" from any other failure.
        if response_status_from_error(ex) == 404:
            raise ResourceNotFoundError(str(ex)) from ex
        raise
    content = getattr(response, "content", None)
    if not content:
        return {}
    try:
        payload = strict_json_loads(content)
    except (ValueError, TypeError, RecursionError):
        raise ClientRequestError("The identity service returned invalid JSON.") from None
    if not isinstance(payload, dict):
        raise ClientRequestError("The identity service returned an invalid object envelope.")
    return payload


def get_identity(cmd, resource_group_name, name, sender=None):
    payload = _send(cmd, "GET", site_url(cmd, resource_group_name, name), sender=sender)
    return normalize_identity(payload.get("identity"))


def normalize_identity(identity):
    """Return a stable shape whether or not the site has an identity.

    ARM omits ``identity`` entirely when there is none, which reads as a
    missing field rather than an answer. Normalizing to ``type: None`` makes
    ``identity show`` say "there is no identity" instead of printing nothing.
    """
    if not isinstance(identity, dict):
        return {"type": NONE, "principalId": None, "tenantId": None, "userAssignedIdentities": {}}
    user_assigned = identity.get("userAssignedIdentities")
    return {
        "type": identity.get("type") or NONE,
        "principalId": identity.get("principalId"),
        "tenantId": identity.get("tenantId"),
        "userAssignedIdentities": user_assigned if isinstance(user_assigned, dict) else {},
    }


def _types(identity_type):
    if not identity_type or identity_type == NONE:
        return set()
    return {part.strip() for part in str(identity_type).split(",") if part.strip()}


def _compose(types):
    if SYSTEM_ASSIGNED in types and USER_ASSIGNED in types:
        return "{}, {}".format(SYSTEM_ASSIGNED, USER_ASSIGNED)
    if SYSTEM_ASSIGNED in types:
        return SYSTEM_ASSIGNED
    if USER_ASSIGNED in types:
        return USER_ASSIGNED
    return NONE


def plan_assign(current, system_assigned=False, user_assigned=None):
    """Merge the requested identities into the current ones.

    Assign is additive: asking for a user-assigned identity must not silently
    drop a system-assigned one that a running workflow already authenticates
    with.
    """
    user_assigned = flatten_repeatable(user_assigned)
    if not system_assigned and not user_assigned:
        raise RequiredArgumentMissingError(
            "Specify --system-assigned, --user-assigned, or both."
        )
    types = _types(current.get("type"))
    identities = dict(current.get("userAssignedIdentities") or {})
    if system_assigned:
        types.add(SYSTEM_ASSIGNED)
    for identity_id in user_assigned:
        _validate_user_assigned_id(identity_id)
        types.add(USER_ASSIGNED)
        identities.setdefault(identity_id, {})
    body = {"type": _compose(types)}
    if USER_ASSIGNED in types:
        body["userAssignedIdentities"] = {key: {} for key in identities}
    return body


def plan_remove(current, system_assigned=False, user_assigned=None):
    """Remove the requested identities, leaving the others in place.

    ARM removes a user-assigned identity only when the key is sent explicitly
    as ``null``; dropping the key from the map is a no-op, which is why a naive
    implementation reports success and changes nothing.
    """
    user_assigned = flatten_repeatable(user_assigned)
    if not system_assigned and not user_assigned:
        raise RequiredArgumentMissingError(
            "Specify --system-assigned, --user-assigned, or both."
        )
    types = _types(current.get("type"))
    identities = dict(current.get("userAssignedIdentities") or {})
    removals = {}
    if system_assigned:
        types.discard(SYSTEM_ASSIGNED)
    for identity_id in user_assigned:
        _validate_user_assigned_id(identity_id)
        matched = _match_user_assigned(identities, identity_id)
        if matched is None:
            raise ValidationError(
                "User-assigned identity is not assigned to this Logic App: {}".format(identity_id)
            )
        identities.pop(matched)
        removals[matched] = None
    if not identities:
        types.discard(USER_ASSIGNED)
    body = {"type": _compose(types)}
    # ARM rejects an identity map unless the resulting type still includes
    # UserAssigned, so the last user-assigned identity is dropped by the type
    # change alone rather than by an explicit null.
    if removals and USER_ASSIGNED in types:
        body["userAssignedIdentities"] = dict({key: {} for key in identities}, **removals)
    return body


def _match_user_assigned(identities, identity_id):
    for key in identities:
        if key.lower() == identity_id.lower():
            return key
    return None


def _validate_user_assigned_id(identity_id):
    lowered = str(identity_id).lower()
    if "/providers/microsoft.managedidentity/userassignedidentities/" not in lowered:
        raise ValidationError(
            "--user-assigned expects a full resource id of a user-assigned managed identity, "
            "for example /subscriptions/<sub>/resourceGroups/<rg>/providers/"
            "Microsoft.ManagedIdentity/userAssignedIdentities/<identity>. Received: {}".format(identity_id)
        )


def apply_identity(cmd, resource_group_name, name, identity_body, sender=None):
    payload = _send(
        cmd,
        "PATCH",
        site_url(cmd, resource_group_name, name),
        body={"identity": identity_body},
        sender=sender,
    )
    return normalize_identity(payload.get("identity"))
