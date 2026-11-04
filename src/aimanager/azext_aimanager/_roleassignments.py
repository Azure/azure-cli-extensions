# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import json
import uuid

from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from knack.log import get_logger

from azext_aimanager.constants import AIMANAGER_ROLE_NAMES

logger = get_logger(__name__)


def _get_caller_identity(cli_ctx):
    """Return the caller's Entra object ID and a best-guess principal type from the token.

    The caller already exists in the directory, so there is no propagation delay to wait on.
    Returns (None, None) if the object ID cannot be read.
    """
    from azure.cli.core._profile import Profile
    try:
        cred, _, _ = Profile(cli_ctx=cli_ctx).get_raw_token()
        payload = cred[1].split('.')[1]
        payload += '=' * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
    except Exception:  # pylint: disable=broad-except
        return None, None
    # 'idtyp' == 'app' identifies an app-only (service principal) token; otherwise it is a user.
    principal_type = 'ServicePrincipal' if claims.get('idtyp') == 'app' else 'User'
    return claims.get('oid'), principal_type


def assign_caller_roles(cmd, scope, role_definition_ids):
    """Best-effort: grant the caller the given built-in roles on the scope.

    Single attempt per role (the caller already exists, so the AAD-propagation retry the shared
    AKS helper performs is unnecessary and would hang the create for ~2 minutes on the common
    permission-denied path). Never raises: creating an AI Manager or namespace must not fail just
    because the caller lacks permission to assign roles (that requires Owner or User Access
    Administrator).
    """
    object_id, principal_type = _get_caller_identity(cmd.cli_ctx)
    if not object_id:
        logger.warning(
            "Could not determine the caller's object ID; skipping role assignment on %s.", scope)
        return

    try:
        subscription_id = get_subscription_id(cmd.cli_ctx)
        role_assignment_create_parameters = get_sdk(
            cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION,
            'RoleAssignmentCreateParameters', mod='models', operation_group='role_assignments')
        assignments_client = get_mgmt_service_client(
            cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION).role_assignments
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning("Could not set up role assignment on %s: %s", scope, ex)
        return
    # The caller is a user or a service principal. Start with the token's hint and fall back to
    # the other type if ARM reports a principal-type mismatch, rather than guessing wrong.
    principal_types = [principal_type] + [t for t in ('User', 'ServicePrincipal') if t != principal_type]

    for role_id in role_definition_ids:
        matched_type = _assign_role(assignments_client, role_assignment_create_parameters,
                                    subscription_id, scope, role_id, object_id, principal_types)
        # Once we learn the caller's real type, try it first for the remaining roles.
        if matched_type and principal_types[0] != matched_type:
            principal_types = [matched_type] + [t for t in principal_types if t != matched_type]


def _assign_role(assignments_client, params_model, subscription_id, scope, role_id,
                 object_id, principal_types):
    """Create one role assignment, trying each principal type. Returns the type that worked, or
    None if the assignment could not be created."""
    role_definition_id = (
        f"/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Authorization/roleDefinitions/{role_id}")
    last = len(principal_types) - 1
    for index, principal_type in enumerate(principal_types):
        try:
            assignments_client.create(scope, str(uuid.uuid4()), params_model(
                role_definition_id=role_definition_id,
                principal_id=object_id,
                principal_type=principal_type))
            return principal_type
        except ResourceExistsError:
            return principal_type  # already assigned; idempotent
        except HttpResponseError as ex:
            message = ex.message or ""
            code = getattr(getattr(ex, 'error', None), 'code', None)
            if code == 'RoleAssignmentExists' or 'already exists' in message.lower():
                return principal_type
            if 'UnmatchedPrincipalType' in message and index < last:
                continue  # wrong guess; try the next principal type
            _warn_assignment_failed(scope, role_id, object_id)
            return None
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("Skipping role assignment '%s' on %s: %s", role_id, scope, ex)
            return None
    return None


def _role_name(role_id):
    # Fall back to the raw GUID (which `az role assignment create --role` also accepts) so the
    # best-effort warning path never raises on a role id that is not in AIMANAGER_ROLE_NAMES.
    return AIMANAGER_ROLE_NAMES.get(role_id, role_id)


def _role_assignment_command(assignee, role_id, scope):
    """Build the exact 'az role assignment create' command that grants one role to the caller."""
    return (f'az role assignment create --assignee-object-id {assignee} '
            f'--role "{_role_name(role_id)}" --scope {scope}')


def _warn_assignment_failed(scope, role_id, object_id):
    logger.warning(
        "Could not assign '%s' to the caller on %s. This is expected if you are not an Owner or "
        "User Access Administrator. An administrator can grant it with:\n  %s",
        _role_name(role_id), scope,
        _role_assignment_command(object_id, role_id, scope))


def warn_roles_skipped_no_wait(cmd, scope, role_definition_ids):
    """--no-wait skipped the automatic grant (success cannot be confirmed before the command
    returns). Print the exact 'az role assignment create' commands so the caller can grant the
    roles themselves."""
    object_id, _ = _get_caller_identity(cmd.cli_ctx)
    assignee = object_id or "<caller-object-id>"
    commands = "\n".join(
        "  " + _role_assignment_command(assignee, role_id, scope)
        for role_id in role_definition_ids)
    logger.warning(
        "--no-wait was set, so the caller's role assignments on %s were skipped. Grant them once "
        "the create succeeds (requires Owner or User Access Administrator; data-plane access can "
        "take a few minutes to take effect):\n%s", scope, commands)
