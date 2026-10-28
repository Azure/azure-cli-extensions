# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=import-error,no-name-in-module

"""Managed API connections for deployed and local Logic Apps Standard projects.

A deployed managed API connection is three coupled resources, not one. Creating the ARM
``Microsoft.Web/connections`` resource alone produces something the app cannot
use: the app reaches the connection through its own managed identity, so the
connection also needs an access policy naming that identity, and the app needs a
``managedApiConnections`` entry in ``connections.json`` pointing at both.
Local projects instead use a development runtime key referenced from protected
local settings; no deployed app identity or access-policy write is required.

Two properties of the platform shape this module and were established live
rather than read from source:

* The connection must be created with ``kind: "V2"``. A V1 connection rejects
  every access policy write with ``InvalidApiConnectionAccessPolicy``, and
  ``kind`` cannot be changed afterwards -- mutating it returns
  ``ConnectionV2KindMismatch``. A connection created without ``kind`` defaults to
  V1, so omitting it silently produces a resource that can never be wired up.
* The access policy body is ``{location, properties.principal.identity}`` with
  ``type: "ActiveDirectory"``.
"""

import base64
import copy
import json
from urllib.parse import urlsplit

from azure.cli.core.azclierror import (
    CLIError, CLIInternalError, ClientRequestError, InvalidArgumentValueError,
    RequiredArgumentMissingError, ResourceNotFoundError, ValidationError)
from requests.exceptions import RequestException as RequestsRequestException

from ._args import flatten_repeatable
from ._constants import LOGICAPP_REDACTION_SENTINEL
from ._json import json_equal, strict_json_loads
from ._managed_api import _quote_segment, response_status_from_error
from ._oauth_consent import DEFAULT_CONSENT_TIMEOUT, run_consent_flow, verify_connected
from ._runtime_client import validate_file_etag
from ._workflow_discovery import response_etag

MANAGED_CLASS = "managedApiConnections"
CONNECTIONS_FILE = "connections.json"

AUTH_MODES = ("managed-identity", "raw", "service-principal", "oauth")

# Connector metadata marks the managed-identity parameter set by giving one of its
# parameters this type, so the set name does not have to be guessed per connector.
_MANAGED_IDENTITY_PARAM_TYPE = "managedidentity"


def create_managed_connection(cmd, resource_group_name, name, connection_name, connector, location,
                              auth_mode, display_name=None, parameter=None, secret_parameter=None,
                              secret_value=None, parameter_set=None, user_assigned_identity=None,
                              force=False, no_browser=False, consent_timeout=None,
                              arm_sender=None, identity_sender=None, vfs_client=None,
                              consent_runner=None, consent_principal=None, local_project=None):
    """Create and wire a connection, preserving ARM state on failure.

    Unconditional ARM upserts cannot establish exclusive compensation ownership.
    Retain resources and ACLs for manual inspection; only guarded file restoration
    is attempted. ARM reads also omit recoverable OAuth credentials.
    """
    from ._connection import validate_connection_name, reject_secret_shaped_name

    validate_connection_name(connection_name)
    reject_secret_shaped_name(connection_name, "--connection-name")

    if auth_mode not in AUTH_MODES:
        raise InvalidArgumentValueError(
            "--auth-mode must be one of: {}.".format(", ".join(AUTH_MODES)))

    local = local_project is not None
    if local:
        if auth_mode == "managed-identity" or user_assigned_identity is not None:
            raise ValidationError(
                "Local managed connections use development runtime keys, not a deployed app identity. "
                "--auth-mode managed-identity and --user-assigned-identity require a deployed app target.")
        from ._local_managed_connection import LocalConnectionsFile
        wiring = LocalConnectionsFile(cmd, local_project, connection_name, resource_group_name, location, force)
        location = wiring.location
        connector_id = wiring.connector_id(cmd, connector)
        principal = None
    else:
        connector_id = _resolve_connector(cmd, connector, location)
        principal = _resolve_app_principal(cmd, resource_group_name, name, user_assigned_identity,
                                           sender=identity_sender)

    parameters = _parse_parameters(parameter)
    if secret_parameter:
        if secret_value is None:
            raise RequiredArgumentMissingError(
                "--secret-parameter {} expects its value on standard input.".format(secret_parameter))
        parameters[secret_parameter] = secret_value

    value_set = parameter_set
    if auth_mode == "managed-identity" and not value_set:
        value_set = _managed_identity_parameter_set(cmd, connector_id, arm_sender)

    connection_id = wiring.connection_id if local else _connection_id(cmd, resource_group_name, connection_name)
    existing = _existing_resource(cmd, connection_id, arm_sender)
    if existing is not None and not force:
        _already_exists(connection_name)

    if not local:
        wiring = _ConnectionsFile(cmd, resource_group_name, name, connection_name, vfs_client)
    policy_name = access_policy_name(name, principal["objectId"]) if not local else None
    policy_id = _access_policy_id(connection_id, policy_name) if not local else None
    if existing is not None and not local:
        _refuse_duplicate_principal(cmd, connection_id, connection_name, principal["objectId"],
                                    policy_name, arm_sender)
        existing_policy = _existing_resource(cmd, policy_id, arm_sender)
        if existing_policy is not None:
            _validate_existing_policy(existing_policy, principal)

    body = build_connection_body(location, connector_id, display_name or connection_name,
                                 parameters, value_set)
    consent = None
    connection_put_completed = False
    policy_attempted = False
    try:
        if local:
            wiring.check_unchanged()
        created = _arm(cmd, "PUT", connection_id, body, arm_sender)
        connection_put_completed = True
        if auth_mode == "oauth":
            runner = consent_runner or _default_consent_runner
            # The consent link is requested as the caller, not as the app: the
            # service only issues links for the requester's own identity.
            consenter = consent_principal or (
                _resolve_consent_principal(cmd, subscription=wiring.subscription) if local
                else _resolve_consent_principal(cmd))
            consent = runner(
                cmd, connection_id,
                object_id=consenter["objectId"], tenant_id=consenter["tenantId"],
                arm=lambda method, resource_id, payload=None: _arm(
                    cmd, method, resource_id, payload, arm_sender),
                no_browser=no_browser,
                timeout=consent_timeout or DEFAULT_CONSENT_TIMEOUT)

        policy = None
        if not local:
            _refuse_duplicate_principal(cmd, connection_id, connection_name, principal["objectId"],
                                        policy_name, arm_sender)
            current_policy = _existing_resource(cmd, policy_id, arm_sender)
            if current_policy is not None:
                _validate_existing_policy(current_policy, principal)
            policy_body = build_access_policy_body(location, principal["tenantId"], principal["objectId"])
            policy_attempted = True
            policy = _arm(cmd, "PUT", policy_id, policy_body, arm_sender)

        # Read back after the policy write so the reported state is post-ACL, not the
        # pre-ACL body the create call happened to return.
        readback = _arm(cmd, "GET", connection_id, None, arm_sender)
        if not isinstance(readback, dict) or (not local and not isinstance(policy, dict)):
            raise CLIInternalError("ARM returned an invalid connection or access policy response.")
        if auth_mode == "oauth":
            verify_connected(readback, connection_name)

        runtime_url = _runtime_url(readback) or _runtime_url(created)
        entry = build_connections_entry(connector_id, connection_id, runtime_url, user_assigned_identity)
        if local:
            written = _write_local_connection(cmd, connection_id, runtime_url, entry, wiring, arm_sender)
        else:
            written = wiring.write(entry)

        return {
            "connection": {
                "id": readback.get("id") or connection_id,
                "name": readback.get("name") or connection_name,
                "type": readback.get("type"),
                "location": readback.get("location") or location,
                "kind": readback.get("kind"),
                "status": _overall_status(readback),
            },
            "api": {"id": connector_id},
            "authMode": auth_mode,
            "consent": consent,
            "parameterValueSet": value_set,
            "accessPolicy": {
                "id": policy.get("id"),
                "name": policy.get("name") or policy_name,
                "principal": {"objectId": principal["objectId"], "tenantId": principal["tenantId"]},
            } if policy is not None else None,
            **({"localProject": wiring.root,
                "developmentKey": {"appSetting": wiring.key_setting, "validityDaysRequested": 7,
                                   "secretStore": "local.settings.json"},
                "protection": {"trackedByGit": wiring.tracked, "excludedFromPackage": True}}
               if local else {}),
            "connectionRuntimeUrl": {"value": LOGICAPP_REDACTION_SENTINEL} if runtime_url else None,
            "connectionsJson": {
                "class": MANAGED_CLASS,
                "name": connection_name,
                "updated": written,
            },
        }
    except BaseException as error:
        _handle_creation_failure(
            error, local, wiring, existing, connection_put_completed, policy_attempted, connection_name)
        raise


def _write_local_connection(cmd, connection_id, runtime_url, entry, wiring, arm_sender):
    try:
        endpoint = urlsplit(runtime_url) if isinstance(runtime_url, str) else None
        usable = (endpoint is not None and endpoint.scheme == "https" and endpoint.hostname
                  and not endpoint.username and not endpoint.password and not endpoint.fragment
                  and not any(ord(character) < 33 for character in runtime_url))
    except ValueError:
        usable = False
    if not usable:
        raise ValidationError("The managed connection did not return a usable runtime URL.")
    keys = _arm(cmd, "POST", connection_id + "/listConnectionKeys", {"validityTimeSpan": "7"}, arm_sender)
    key = keys.get("connectionKey") if isinstance(keys, dict) else None
    if not isinstance(key, str) or not key.strip() or len(key) > 65536:
        raise ValidationError("Azure did not return a valid development connection key.")
    entry["authentication"] = {
        "type": "Raw", "scheme": "Key",
        "parameter": "@appsetting('{}')".format(wiring.key_setting),
    }
    return wiring.write(entry, key)


def _handle_creation_failure(error, local, wiring, existing, connection_put_completed,
                             policy_attempted, connection_name):
    if local:
        message = (
            "Local managed connection creation did not complete. Azure connection properties or "
            "authentication may have changed and local files may be partially updated. No ARM "
            "resources were deleted, no file rollback or automatic retry was attempted. Inspect "
            "the retained Azure connection and project files before retrying.")
        if not isinstance(error, Exception):
            from knack.log import get_logger
            get_logger(__name__).error(message)
            return
        raise CLIInternalError(message) from error
    failures = []
    _try_rollback(wiring.restore, "connections.json entry", failures)
    unverified_creation = existing is None and not connection_put_completed
    message = (
        "Managed connection operation failed. No ARM connection or access policies were "
        "deleted or restored: preflight absence does not establish ownership, and an "
        "acknowledged upsert does not establish exclusive rollback ownership. Connection "
        "properties, authentication or granted access may have changed; inspect retained "
        "ARM state and perform intended manual recovery before retrying.")
    if unverified_creation:
        message += " The initial connection write was not acknowledged and may have committed."
    if policy_attempted:
        message += " An access policy write was attempted and may have granted or changed access."
    if existing is not None:
        message += (
            " The pre-existing connection '{}' was retained, not deleted. ARM does not expose "
            "all credentials, so the previous connection cannot be safely restored "
            "automatically.".format(connection_name))
    if failures:
        message += " Could not restore {}; manual recovery is required.".format(", ".join(failures))
    if isinstance(error, Exception) and (existing is not None or unverified_creation or failures):
        raise CLIInternalError(message) from error
    from knack.log import get_logger
    get_logger(__name__).error(message)


def _default_consent_runner(cmd, connection_id, object_id, tenant_id, arm, no_browser, timeout):
    del cmd  # the consent leg talks to ARM only through the injected sender
    return run_consent_flow(connection_id, object_id, tenant_id, arm,
                            no_browser=no_browser, timeout=timeout)


def _try_rollback(action, description, failures):
    try:
        action()
    except BaseException:  # Finish independent cleanup even if one leg is interrupted.
        failures.append(description)


def _validate_existing_policy(policy, expected):
    if not isinstance(policy, dict):
        raise ValidationError(
            "The existing access policy cannot be safely interpreted. No access policy update was attempted.")
    properties = policy.get("properties") or {}
    if not isinstance(properties, dict):
        raise ValidationError(
            "The existing access policy cannot be safely interpreted. No access policy update was attempted.")
    principal = properties.get("principal") or {}
    if not isinstance(principal, dict):
        raise ValidationError(
            "The existing access policy cannot be safely interpreted. No access policy update was attempted.")
    identity = principal.get("identity") or {}
    if not (isinstance(identity, dict) and policy.get("location") and
            all(isinstance(value, str) and value.strip() for value in
                (principal.get("type"), identity.get("objectId"), identity.get("tenantId")))):
        raise ValidationError(
            "The existing access policy cannot be safely interpreted. No access policy update was attempted.")
    if not _policy_principal_matches(principal, expected):
        raise ValidationError(
            "The existing access policy does not match the selected principal. "
            "It will not be overwritten; --force does not authorize replacing unrelated access.")


def _policy_principal_matches(principal, expected):
    """Require complete principal and tenant evidence for policy mutation."""
    if not isinstance(principal, dict) or not isinstance(expected, dict):
        return False
    identity = principal.get("identity")
    principal_type = principal.get("type")
    if (not isinstance(identity, dict) or not isinstance(principal_type, str)
            or principal_type.casefold() != "activedirectory"):
        return False
    return all(
        isinstance(identity.get(field), str) and isinstance(expected.get(field), str)
        and expected[field].strip() and expected[field] == expected[field].strip()
        and identity[field].casefold() == expected[field].casefold()
        for field in ("objectId", "tenantId"))


def build_connection_body(location, connector_id, display_name, parameters, parameter_set=None):
    """ARM body for the connection.

    ``kind: V2`` is not optional. Without it the service creates a V1 connection,
    which rejects the access policy this flow must write immediately afterwards,
    and the kind cannot be corrected in place.
    """
    properties = {"displayName": display_name, "api": {"id": connector_id}}
    if parameter_set:
        properties["parameterValueSet"] = {"name": parameter_set, "values": _value_entries(parameters)}
    elif parameters:
        properties["parameterValues"] = dict(parameters)
    return {"location": location, "kind": "V2", "properties": properties}


def build_access_policy_body(location, tenant_id, object_id):
    return {
        "location": location,
        "properties": {
            "principal": {
                "type": "ActiveDirectory",
                "identity": {"tenantId": tenant_id, "objectId": object_id},
            }
        },
    }


def access_policy_name(app_name, object_id):
    return "{}-{}".format(app_name, object_id)


def build_connections_entry(connector_id, connection_id, runtime_url, user_assigned_identity=None):
    authentication = {"type": "ManagedServiceIdentity"}
    if user_assigned_identity:
        authentication["identity"] = user_assigned_identity
    entry = {
        "api": {"id": connector_id},
        "connection": {"id": connection_id},
        "authentication": authentication,
    }
    if runtime_url:
        entry["connectionRuntimeUrl"] = runtime_url
    return entry


def write_connections_entry(cmd, resource_group_name, name, connection_name, entry, vfs_client=None):
    return _ConnectionsFile(cmd, resource_group_name, name, connection_name, vfs_client).write(entry)


_ABSENT = object()


def _read_connections_file(client):
    """Read strictly, retaining original bytes when the VFS supports raw reads."""
    try:
        raw_reader = getattr(client, "get_raw", None)
        if callable(raw_reader):
            response = raw_reader(CONNECTIONS_FILE)
            raw = response["content"]
            current = strict_json_loads(raw)
            etag = response_etag(response)
        else:
            current = client.get(CONNECTIONS_FILE)
            raw = json.dumps(current, indent=2, allow_nan=False).encode("utf-8")
            etag = None
    except ResourceNotFoundError:
        return {}, None, None
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise ValidationError(
            "Existing connections.json is not valid JSON; it will not be overwritten.") from error
    if not isinstance(current, dict):
        raise ValidationError("Existing connections.json must be a JSON object; it will not be overwritten.")
    if MANAGED_CLASS in current and not isinstance(current[MANAGED_CLASS], dict):
        raise ValidationError("managedApiConnections in connections.json must be an object; "
                              "it will not be overwritten.")
    return copy.deepcopy(current), raw, etag


class _ConnectionsFile:
    """Revision-bound file wiring with readback; not a cross-resource transaction."""

    def __init__(self, cmd, resource_group_name, name, connection_name, client=None):
        from ._connection import _vfs_client

        self.client = client or _vfs_client(cmd, resource_group_name, name)
        self.name = connection_name
        self.before, self.raw_before, etag = _read_connections_file(self.client)
        validate_file_etag(etag, description=CONNECTIONS_FILE)
        self.entry = _ABSENT
        self.written_etag = None

    def _entry(self, payload):
        return payload.get(MANAGED_CLASS, {}).get(self.name, _ABSENT)

    def write(self, entry):
        current, _, etag = _read_connections_file(self.client)
        etag = validate_file_etag(etag, description=CONNECTIONS_FILE)
        if not json_equal(self._entry(current), self._entry(self.before)):
            raise ValidationError(
                "The connections.json entry changed during connection creation; "
                "it will not be overwritten. Retry after reviewing the file.")
        current.setdefault(MANAGED_CLASS, {})[self.name] = copy.deepcopy(entry)
        content = json.dumps(current, indent=2, allow_nan=False).encode("utf-8")
        self.entry = copy.deepcopy(entry)
        try:
            receipt = self.client.put_raw(CONNECTIONS_FILE, content, if_match=etag)
        except (CLIError, RequestsRequestException) as error:
            if response_status_from_error(error) == 412:
                self.entry = _ABSENT
                raise ClientRequestError(
                    "The connections.json revision changed before publication. The runtime rejected "
                    "the ETag; no retry or file restoration was attempted. Inspect retained ARM state.") from error
            raise ClientRequestError(
                "The connections.json write failed; publication could not be verified. "
                "Inspect the file and retained ARM state before retrying.") from error
        if isinstance(receipt, dict) and receipt.get("statusCode") == 412:
            self.entry = _ABSENT
            raise ClientRequestError(
                "The connections.json revision changed before publication. The runtime rejected "
                "the ETag; no retry or file restoration was attempted. Inspect retained ARM state.")
        if (not isinstance(receipt, dict) or type(receipt.get("statusCode")) is not int  # pylint: disable=unidiomatic-typecheck
                or receipt["statusCode"] not in (200, 201, 204)):
            # An asynchronous or unsupported receipt does not establish completed
            # publication, including for best-effort file restoration.
            self.entry = _ABSENT
            raise ClientRequestError(
                "The connections.json write did not return a completed receipt. "
                "Publication is uncertain; inspect the file and retained ARM state before retrying.")
        self.written_etag = validate_file_etag(response_etag(receipt), description=CONNECTIONS_FILE)
        try:
            published, _, _ = _read_connections_file(self.client)
        except (CLIError, OSError, ValueError, TypeError) as error:
            raise ClientRequestError(
                "The connections.json write was acknowledged, but readback failed. "
                "Publication could not be verified; inspect the file and retained ARM state.") from error
        if not json_equal(self._entry(published), self.entry):
            raise ClientRequestError(
                "The connections.json write was acknowledged, but the selected entry did not match "
                "on readback. Publication could not be verified; inspect the file and retained ARM state.")
        return True

    def restore(self):
        if self.entry is _ABSENT:
            return
        current, _, etag = _read_connections_file(self.client)
        previous = self._entry(self.before)
        if json_equal(self._entry(current), previous):
            return
        if self.written_etag is None:
            raise ValidationError(
                "No completed connections.json write revision was established; "
                "refusing automatic restoration. Inspect the retained file and ARM state.")
        if etag != self.written_etag:
            raise ValidationError(
                "The connections.json entry changed or its owned revision was replaced; "
                "refusing to overwrite another writer during rollback.")
        if not json_equal(self._entry(current), self.entry):
            raise ValidationError("The connections.json entry changed; refusing to overwrite it during rollback.")
        etag = validate_file_etag(etag, description=CONNECTIONS_FILE)
        if previous is _ABSENT:
            del current[MANAGED_CLASS][self.name]
            if MANAGED_CLASS not in self.before and not current[MANAGED_CLASS]:
                del current[MANAGED_CLASS]
        else:
            current[MANAGED_CLASS][self.name] = copy.deepcopy(previous)

        content = (self.raw_before if json_equal(current, self.before)
                   else json.dumps(current, indent=2, allow_nan=False).encode("utf-8"))
        receipt = self.client.put_raw(CONNECTIONS_FILE, content, if_match=etag)
        if (not isinstance(receipt, dict) or type(receipt.get("statusCode")) is not int  # pylint: disable=unidiomatic-typecheck
                or receipt["statusCode"] not in (200, 201, 204)):
            raise ClientRequestError("Conditional connections.json restoration did not return a completed receipt.")


# ---- access policy commands ------------------------------------------------

def acl_list(cmd, resource_group_name, connection, sender=None):
    connection_id = _connection_id(cmd, resource_group_name, connection)
    payload = _arm(cmd, "GET", _access_policies_id(connection_id), None, sender)
    items = payload.get("value") if isinstance(payload, dict) else None
    return {"value": [_policy_view(item) for item in items or []]}


def acl_show(cmd, resource_group_name, connection, policy, sender=None):
    connection_id = _connection_id(cmd, resource_group_name, connection)
    payload = _arm(cmd, "GET", _access_policy_id(connection_id, policy), None, sender)
    return _policy_view(payload)


def acl_add(cmd, resource_group_name, connection, object_id, tenant_id=None, policy=None,
            location=None, sender=None):
    connection_id = _connection_id(cmd, resource_group_name, connection)
    policy_name = policy or object_id
    policy_id = _access_policy_id(connection_id, policy_name)
    existing = _arm(cmd, "GET", connection_id, None, sender)
    if str(existing.get("kind") or "").upper() != "V2":
        raise ValidationError(
            "Connection '{}' is kind '{}'. Only V2 connections accept access policies, and kind "
            "cannot be changed after creation. Recreate the connection with "
            "'az logicapp connection create --managed-api', which always creates V2.".format(
                connection, existing.get("kind") or "unknown"))
    resolved_location = location or existing.get("location")
    if not resolved_location:
        raise RequiredArgumentMissingError("--location is required; the connection did not report one.")
    resolved_tenant = tenant_id or _tenant_id(cmd)
    _refuse_duplicate_principal(cmd, connection_id, connection, object_id, policy_name, sender)
    body = build_access_policy_body(resolved_location, resolved_tenant, object_id)
    return _policy_view(_arm(cmd, "PUT", policy_id, body, sender))


def acl_remove(cmd, resource_group_name, connection, policy, sender=None):
    connection_id = _connection_id(cmd, resource_group_name, connection)
    _arm(cmd, "DELETE", _access_policy_id(connection_id, policy), None, sender)
    return {"connection": connection, "policy": policy, "removed": True}


def acl_list_table_format(result):
    return [_policy_row(item) for item in (result or {}).get("value", [])]


def acl_show_table_format(result):
    return [_policy_row(result or {})]


def _policy_row(item):
    principal = (item or {}).get("principal") or {}
    return {
        "Name": (item or {}).get("name"),
        "ObjectId": principal.get("objectId"),
        "TenantId": principal.get("tenantId"),
    }


def _policy_view(payload):
    if not isinstance(payload, dict):
        return {}
    identity = ((payload.get("properties") or {}).get("principal") or {}).get("identity") or {}
    principal_type = ((payload.get("properties") or {}).get("principal") or {}).get("type")
    return {
        "id": payload.get("id"),
        "name": payload.get("name"),
        "type": payload.get("type"),
        "location": payload.get("location"),
        "principal": {
            "type": principal_type,
            "objectId": identity.get("objectId"),
            "tenantId": identity.get("tenantId"),
        },
    }


# ---- helpers ---------------------------------------------------------------

def _resolve_connector(cmd, connector, location):
    from ._managed_api import _managed_api_id
    return _managed_api_id(cmd, connector, location)


def _jwt_claims(token):
    """Decode a JWT payload without verifying it.

    Only the caller's own ``oid``/``tid`` are read, and the token came from the
    local credential store, so there is nothing to verify against here -- the
    service re-validates the token on every call.
    """
    parts = (token or "").split(".")
    if len(parts) < 2:
        raise CLIInternalError("Could not read the signed-in identity from the access token.")
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
    except (ValueError, TypeError) as ex:
        raise CLIInternalError(
            "Could not read the signed-in identity from the access token.") from ex


def _resolve_consent_principal(cmd, claims_reader=None, subscription=None):
    """The object id that asks for the consent link.

    This is deliberately NOT the app's managed identity. The consent service
    refuses a link requested on behalf of anyone but the caller --
    "The client can only request consent links for their own identity" -- because
    consent is granted by the human running the command. The managed identity is
    still what the access policy names, so the two principals differ by design.
    """
    read = claims_reader or _caller_claims
    claims = read(cmd, subscription=subscription) if subscription is not None else read(cmd)
    object_id = claims.get("oid")
    if not object_id:
        raise CLIInternalError(
            "Could not determine the signed-in object id needed to request consent. Sign in with "
            "'az login' as a user or service principal and retry.")
    return {"objectId": object_id, "tenantId": claims.get("tid") or _tenant_id(cmd, subscription)}


def _caller_claims(cmd, subscription=None):
    from azure.cli.core._profile import Profile

    profile = Profile(cli_ctx=cmd.cli_ctx)
    credential, _, _ = (profile.get_raw_token(subscription=subscription) if subscription is not None
                        else profile.get_raw_token())
    return _jwt_claims(credential[1])


def _resolve_app_principal(cmd, resource_group_name, name, user_assigned_identity, sender=None):
    """The object id the access policy will name.

    A managed API connection is unusable by the app without this, so an app with
    no identity is a hard stop before anything is created in ARM rather than a
    warning after a half-built connection exists.
    """
    from ._identity import get_identity

    identity = get_identity(cmd, resource_group_name, name, sender=sender)
    tenant_id = identity.get("tenantId") or _tenant_id(cmd)
    if user_assigned_identity:
        assigned = identity.get("userAssignedIdentities") or {}
        match = None
        for key, value in assigned.items():
            if key.lower() == user_assigned_identity.lower():
                match = value
                break
        if not match:
            raise ValidationError(
                "User-assigned identity '{uami}' is not assigned to '{app}'. Assign it first with "
                "'az logicapp identity assign --user-assigned {uami}'.".format(
                    uami=user_assigned_identity, app=name))
        object_id = match.get("principalId")
        if not object_id:
            raise ValidationError(
                "User-assigned identity '{}' reported no principalId.".format(user_assigned_identity))
        return {"objectId": object_id, "tenantId": match.get("tenantId") or tenant_id}

    object_id = identity.get("principalId")
    if not object_id:
        raise ValidationError(
            "Managed API connection creation requires a managed identity on '{app}', because the "
            "app reaches the connection through an access policy naming that identity. The app "
            "currently has identity type '{kind}'. Enable one with 'az logicapp identity assign "
            "--system-assigned -g {group} -n {app}', or pass --user-assigned-identity. No ARM "
            "connection was created.".format(
                app=name, kind=identity.get("type") or "None", group=resource_group_name))
    return {"objectId": object_id, "tenantId": tenant_id}


def _managed_identity_parameter_set(cmd, connector_id, sender=None):
    """Find the connector's managed-identity parameter set from its own metadata.

    Set names differ per connector (``managedIdentityAuth`` on azureblob), so
    reading the catalogue beats hardcoding a name that is wrong elsewhere.
    """
    from ._managed_api import _send, _with_api_version

    payload = _send(cmd, "GET", _with_api_version(connector_id), sender=sender)
    sets = ((payload.get("properties") or {}).get("connectionParameterSets") or {}).get("values")
    for item in sets or []:
        for param in (item.get("parameters") or {}).values():
            if str((param or {}).get("type") or "").lower() == _MANAGED_IDENTITY_PARAM_TYPE:
                return item.get("name")
    raise ValidationError(
        "Connector '{}' advertises no managed-identity parameter set, so --auth-mode "
        "managed-identity cannot be used with it. Pass --parameter-set explicitly if you know the "
        "set name, or choose another --auth-mode.".format(connector_id.rsplit("/", 1)[-1]))


def _refuse_existing(cmd, connection_id, connection_name, sender=None):
    if _existing_resource(cmd, connection_id, sender) is not None:
        _already_exists(connection_name)


def _existing_resource(cmd, resource_id, sender=None):
    try:
        payload = _arm(cmd, "GET", resource_id, None, sender)
    except ResourceNotFoundError:
        return None
    if not isinstance(payload, dict):
        raise CLIInternalError(
            "ARM returned an invalid existing-resource response; no connection was updated.")
    return payload


def _already_exists(connection_name):
    raise ValidationError(
        "Connection '{}' already exists. Re-run with --force to overwrite it, or choose another "
        "--name (connection managed create) or --connection-name "
        "(legacy connection create).".format(connection_name))


def _refuse_duplicate_principal(cmd, connection_id, connection, object_id, policy_name, sender=None):
    """Stop a second policy for a principal that already has one.

    A connection holds at most one access policy per principal. Asking for a
    second one under a different name does not return a validation error: the
    service answers ``InternalServerError`` with a tracking id and no hint about
    the cause, so the collision is caught here instead.
    """
    try:
        payload = _arm(cmd, "GET", _access_policies_id(connection_id), None, sender)
    except ResourceNotFoundError:
        return
    wanted = str(object_id).lower()
    for item in (payload or {}).get("value") or []:
        name = item.get("name")
        if name == policy_name:
            continue
        identity = ((item.get("properties") or {}).get("principal") or {}).get("identity") or {}
        if str(identity.get("objectId") or "").lower() == wanted:
            raise ValidationError(
                "Connection '{conn}' already grants access to principal {oid} through policy "
                "'{existing}'. A connection holds at most one access policy per principal, so "
                "adding '{wanted}' would fail with an opaque server error. Remove the existing "
                "policy first with 'az logicapp connection acl remove -g <group> --connection "
                "{conn} --policy {existing}', or reuse that policy name.".format(
                    conn=connection, oid=object_id, existing=name, wanted=policy_name))


def _parse_parameters(raw):
    values = {}
    for item in flatten_repeatable(raw):
        text = str(item)
        if "=" not in text:
            raise InvalidArgumentValueError(
                "--parameter expects NAME=VALUE. Received: {}".format(text))
        key, value = text.split("=", 1)
        key = key.strip()
        if not key:
            raise InvalidArgumentValueError("--parameter expects NAME=VALUE. Received: {}".format(text))
        values[key] = value
    return values


def _value_entries(parameters):
    return {key: {"value": value} for key, value in (parameters or {}).items()}


def _overall_status(payload):
    return (payload.get("properties") or {}).get("overallStatus") if isinstance(payload, dict) else None


def _runtime_url(payload):
    if not isinstance(payload, dict):
        return None
    return (payload.get("properties") or {}).get("connectionRuntimeUrl")


def _tenant_id(cmd, subscription=None):
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    return (profile.get_subscription(subscription=subscription) if subscription is not None
            else profile.get_subscription()).get("tenantId")


def _connection_id(cmd, resource_group_name, connection_name):
    from azure.cli.core.commands.client_factory import get_subscription_id
    return "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/connections/{}".format(
        get_subscription_id(cmd.cli_ctx), resource_group_name, connection_name)


def _access_policies_id(connection_id):
    return "{}/accessPolicies".format(connection_id)


def _valid_access_policy_name(value):
    return (isinstance(value, str) and bool(value) and value == value.strip()
            and value not in (".", "..") and value.isprintable()
            and not any(character in value for character in "/\\%?#"))


def _access_policy_id(connection_id, policy_name):
    if not _valid_access_policy_name(policy_name):
        raise InvalidArgumentValueError(
            "Access policy name must be a non-empty single identifier, not a path, URL or escaped value.")
    return "{}/accessPolicies/{}".format(connection_id, _quote_segment(policy_name))


def _arm(cmd, method, resource_id, body=None, sender=None):
    from ._connection import _send_arm, _with_connection_api_version
    return _send_arm(cmd, method, _with_connection_api_version(resource_id), body=body, sender=sender)
