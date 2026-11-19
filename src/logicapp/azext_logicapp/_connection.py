# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Local connection authoring.

Per D135 the secret value never appears on the command line: ``--secret`` names an
app setting and the value arrives on standard input. Per the D135 item 3 ruling the
local store is ``local.settings.json`` ``Values``, which ``deployment package``
already excludes as ``secret``.
"""

import copy
import json
import os
import re
import shutil
import subprocess
from urllib.parse import urlparse

# pylint: disable=import-error,no-name-in-module
from azure.cli.core.azclierror import CLIError, ClientRequestError, FileOperationError, HTTPError, InvalidArgumentValueError, ResourceNotFoundError, ValidationError

from ._constants import LOGICAPP_REDACTION_SENTINEL
from ._args import flatten_repeatable
from ._json import json_equal
from ._paging import slice_items
from ._workflow import abs_path, write_json_file
from ._managed_api import parse_retry_after, response_headers_from_error, response_status_from_error
from ._runtime_client import SiteRuntimeClient, SiteVfsClient, operation_groups_path, validate_file_etag
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from knack.log import get_logger

logger = get_logger(__name__)


CONNECTIONS_FILE = "connections.json"
LOCAL_SETTINGS_FILE = "local.settings.json"
GITIGNORE_FILE = ".gitignore"

# A parameter value that is *only* an app setting reference names a setting; it
# does not carry the setting's value. Redacting it destroyed the main diagnostic
# for a misconfigured connection -- you could not see which setting was expected,
# let alone that it was missing. Anchored on both ends on purpose: a value that
# merely contains a reference may also carry a literal secret, so it stays hidden.
_APP_SETTING_REFERENCE = re.compile(
    r"^\s*@\{?\s*appsetting\(\s*'[^']*'\s*\)\s*\}?\s*$", re.IGNORECASE)

# Markers that indicate a caller pasted a credential where a *name* was expected.
# Deliberately broader than the context check: Service Bus connection strings use
# SharedAccessKey, which that list does not carry.
SECRET_SHAPED_MARKERS = (
    "accountkey=",
    "sharedaccesskey=",
    "sharedaccesssignature=",
    "client_secret",
    "endpoint=sb://",
    "password=",
    "?sig=",
    "&sig=",
)

APP_SETTING_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
CONNECTION_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def reject_secret_shaped_name(value, flag, advice=None):
    """Fail if a credential was passed where a name belongs (D135, enforced as an error)."""
    lowered = str(value or "").lower()
    if any(marker in lowered for marker in SECRET_SHAPED_MARKERS):
        raise InvalidArgumentValueError(
            "{} must not carry a secret value. {} "
            "Re-run without the credential on the command line, and rotate it if it reached your shell history.".format(
                flag, advice or "It takes a name, and the value is read from standard input."))


def normalize_connector_id(connector):
    if not connector:
        raise InvalidArgumentValueError("--connector is required.")
    text = str(connector).strip()
    if text.startswith("/serviceProviders/"):
        name = text[len("/serviceProviders/"):]
    elif "/" in text:
        raise InvalidArgumentValueError(
            "Connector '{}' is not a service provider id. Use a name such as 'serviceBus' or '/serviceProviders/serviceBus'.".format(connector))
    else:
        name = text
    if not CONNECTION_NAME.match(name):
        raise InvalidArgumentValueError("Connector name '{}' is not valid.".format(connector))
    return "/serviceProviders/{}".format(name), name


def validate_connection_name(name):
    if not name or not CONNECTION_NAME.match(name):
        raise InvalidArgumentValueError("Connection name '{}' is not valid.".format(name))


def validate_app_setting_name(name):
    if not name or not APP_SETTING_NAME.match(name):
        raise InvalidArgumentValueError(
            "App setting name '{}' is not valid. Use letters, digits, underscore, dot or hyphen, starting with a letter or underscore.".format(name))


def read_json_file(path, expected):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except ValueError as ex:
        raise ValidationError("{} is not valid JSON: {}".format(path, ex)) from ex
    except OSError as ex:
        raise FileOperationError("Could not read {}".format(path)) from ex
    if not isinstance(payload, expected):
        raise ValidationError("{} must contain a JSON object.".format(path))
    return payload


def require_project(root):
    root = abs_path(root)
    if not os.path.isfile(os.path.join(root, "host.json")):
        raise ResourceNotFoundError(
            "Logic Apps project not found at '{root}'. Run 'az logicapp project create --path {root}' first.".format(root=root))
    return root


def _split_assignment(raw, flag):
    """Split a NAME=VALUE pair, keeping '=' characters inside the value intact."""
    text = str(raw)
    if "=" not in text:
        raise ValidationError(
            "{} expects NAME=VALUE, got '{}'.".format(flag, text))
    key, _, value = text.partition("=")
    key = key.strip()
    if not key:
        raise ValidationError("{} is missing a name before '='.".format(flag))
    return key, value


def _assign_path(target, dotted_path, value, flag):
    """Write value into target at a dotted path, creating intermediate objects.

    The connector metadata nests parameters with a propertyPath, so
    'authProvider.Type' has to become {"authProvider": {"Type": ...}} rather
    than a flat key. A flat key is silently accepted by the runtime and then
    ignored, which is why this is worth getting right.
    """
    segments = [s.strip() for s in str(dotted_path).split(".")]
    if not all(segments):
        raise ValidationError(
            "{} has an empty path segment in '{}'.".format(flag, dotted_path))
    cursor = target
    for segment in segments[:-1]:
        existing = cursor.get(segment)
        if existing is None:
            existing = {}
            cursor[segment] = existing
        elif not isinstance(existing, dict):
            raise ValidationError(
                "{0} cannot nest '{1}': '{2}' is already a value, not an object.".format(
                    flag, dotted_path, segment))
        cursor = existing
    cursor[segments[-1]] = value


def create_local_connection(root, name, connector, secret_setting=None, secret_value=None,
                            secret_parameter="connectionString", parameter_set="connectionString",
                            parameters=None, app_settings=None, force=False, manage_gitignore=True):
    root = require_project(root)
    # azure-cli wraps string defaults taken from the function signature in a str
    # subclass that serializes as {"isDefault": true}. Coerce so the emitted JSON
    # and the written file agree.
    secret_parameter = str(secret_parameter)
    parameter_set = str(parameter_set)
    validate_connection_name(name)
    connector_id, _ = normalize_connector_id(connector)

    parameters = flatten_repeatable(parameters)
    app_settings = flatten_repeatable(app_settings)
    if not secret_setting and not parameters:
        raise ValidationError(
            "Nothing to write. Supply --secret for a credential, or --parameter NAME=VALUE "
            "for an identity-based connection.")
    if secret_setting:
        validate_app_setting_name(secret_setting)
        if not secret_value:
            raise ValidationError("The secret value read from standard input was empty.")

    connections_path = os.path.join(root, CONNECTIONS_FILE)
    settings_path = os.path.join(root, LOCAL_SETTINGS_FILE)

    connections = read_json_file(connections_path, dict) or {}
    service_provider = connections.setdefault("serviceProviderConnections", {})
    if not isinstance(service_provider, dict):
        raise ValidationError("serviceProviderConnections in {} must be an object.".format(connections_path))
    if name in service_provider and not force:
        raise ValidationError(
            "Connection '{}' already exists in {}. Use --force to replace it.".format(name, connections_path))
    connections.setdefault("managedApiConnections", {})

    parameter_values = {}
    for raw in parameters:
        key, value = _split_assignment(raw, "--parameter")
        reject_secret_shaped_name(value, "--parameter",
                                  advice="Use --secret to name an app setting and pipe the credential in on standard input.")
        _assign_path(parameter_values, key, value, "--parameter")
    if secret_setting:
        _assign_path(parameter_values, secret_parameter,
                     "@appsetting('{}')".format(secret_setting), "--secret-parameter")

    service_provider[name] = {
        "displayName": name,
        "parameterSetName": parameter_set,
        "parameterValues": parameter_values,
        "serviceProvider": {"id": connector_id},
    }

    settings = read_json_file(settings_path, dict)
    if settings is None:
        raise ResourceNotFoundError(
            "{} not found. It holds the secret value and is created by 'az logicapp project create'.".format(settings_path))
    values = settings.setdefault("Values", {})
    if not isinstance(values, dict):
        raise ValidationError("Values in {} must be an object.".format(settings_path))

    written_settings = []
    for raw in app_settings:
        key, value = _split_assignment(raw, "--app-setting")
        validate_app_setting_name(key)
        reject_secret_shaped_name(value, "--app-setting",
                                  advice="Use --secret to name an app setting and pipe the credential in on standard input.")
        if key in values and not force:
            raise ValidationError(
                "App setting '{}' already exists in {}. Use --force to replace it.".format(key, settings_path))
        values[key] = value
        written_settings.append(key)

    setting_existed = False
    if secret_setting:
        setting_existed = secret_setting in values
        if setting_existed and not force:
            raise ValidationError(
                "App setting '{}' already exists in {}. Use --force to replace it.".format(secret_setting, settings_path))
        values[secret_setting] = secret_value

    files = []
    item = write_json_file(connections_path, connections, force=True)
    item["class"] = "connections"
    files.append(item)
    item = write_json_file(settings_path, settings, force=True)
    item["class"] = "localSettings"
    item["containsSecret"] = bool(secret_setting)
    files.append(item)

    protection = protect_local_settings(root) if manage_gitignore else None

    return {
        "name": name,
        "connector": connector_id,
        "parameterSet": parameter_set,
        "parameterValues": parameter_values,
        "appSetting": secret_setting,
        "appSettingReplaced": setting_existed,
        "appSettings": written_settings,
        "secretStore": LOCAL_SETTINGS_FILE if secret_setting else None,
        "excludedFromPackage": True,
        "files": files,
        "protection": protection,
    }


def protect_local_settings(root):
    """Keep the plaintext secret out of source control, and say so if it is already in."""
    gitignore_path = os.path.join(root, GITIGNORE_FILE)
    existing = []
    if os.path.isfile(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as handle:
                existing = handle.read().splitlines()
        except OSError as ex:
            raise FileOperationError("Could not read {}".format(gitignore_path)) from ex
    already = any(line.strip() in (LOCAL_SETTINGS_FILE, "/" + LOCAL_SETTINGS_FILE) for line in existing)
    action = "present"
    if not already:
        lines = list(existing)
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("# Holds local secrets. Never commit.")
        lines.append(LOCAL_SETTINGS_FILE)
        try:
            with open(gitignore_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(lines).rstrip("\n") + "\n")
        except OSError as ex:
            raise FileOperationError("Could not write {}".format(gitignore_path)) from ex
        action = "created" if not existing else "updated"
    tracked = is_tracked_by_git(root, LOCAL_SETTINGS_FILE)
    return {
        "gitignore": os.path.abspath(gitignore_path),
        "action": action,
        "trackedByGit": tracked,
        "warning": (
            "{file} is tracked by git. .gitignore does not untrack a file that is already committed. "
            "Run 'git rm --cached {file}' and rotate the secret.".format(file=LOCAL_SETTINGS_FILE)
            if tracked else None),
    }


def is_tracked_by_git(root, relative):
    """True/False when git can answer, None when it cannot."""
    git = shutil.which("git")
    if not git:
        return None
    try:
        completed = subprocess.run(
            [git, "ls-files", "--error-unmatch", relative],
            cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except OSError:
        return None
    if completed.returncode == 0:
        return True
    return False if completed.returncode == 1 else None


# --------------------------- deployed connection reads ---------------------------

_CONNECTION_CLASSES = ("serviceProviderConnections", "managedApiConnections")
_SITE_PROVIDER = "/providers/Microsoft.Web/sites/"
_ARM_CONNECTION_API_VERSION = "2018-07-01-preview"
_TEST_PATH_NONE = "none"
_TEST_PATH_MANAGED_LINK = "managedArmTestLink"
_TEST_PATH_MANAGED_FALLBACK = "managedArmTestRequestFallback"
_TEST_PATH_SERVICE_PROVIDER = "serviceProviderRuntime"


def connection_list(cmd, resource_group_name, name, max_items=None, next_token=None, show_runtime_urls=False, client=None):
    """List app-wired connections from connections.json through the ARM VFS proxy."""
    client = client or _vfs_client(cmd, resource_group_name, name)
    payload = client.get(CONNECTIONS_FILE)
    items = [_redacted_deployed_connection(class_name, entry_name, entry, show_runtime_urls)
             for class_name, entry_name, entry in _connection_entries(payload)]
    page, continuation = _slice_deployed_items(items, next_token=next_token, max_items=max_items)
    return {"value": page, "nextContinuationToken": continuation}


def connection_show(cmd, resource_group_name, name, connection, connection_class=None, show_runtime_urls=False, client=None):
    """Show one app-wired connection from connections.json through the ARM VFS proxy."""
    client = client or _vfs_client(cmd, resource_group_name, name)
    payload = client.get(CONNECTIONS_FILE)
    return _connection_show_response(payload, connection, connection_class=connection_class,
                                     show_runtime_urls=show_runtime_urls)


def connection_test(cmd, resource_group_name, name, connection, connection_class=None, sender=None,
                    vfs_client=None, runtime_client=None, exit_on_nonzero=True):
    """Test a configured connection and classify the observed platform outcome."""
    resolved = _resolve_connection_for_test(
        cmd, resource_group_name, name, connection, connection_class=connection_class,
        vfs_client=vfs_client, runtime_client=runtime_client, sender=sender)
    if resolved["class"] == "managedApiConnections":
        result = _test_managed_connection(cmd, resolved, sender=sender)
    else:
        result = _test_service_provider_connection(cmd, resolved, runtime_client=runtime_client, sender=sender)
    return _finish_connection_test(result, exit_on_nonzero=exit_on_nonzero)


def connection_delete(cmd, resource_group_name, name, connection, connection_class=None,
                      keep_resource=False, client=None, sender=None):
    """Remove a connection from a deployed app, and the ARM resource when the app owns it.

    User-assigned or unverified identities never establish exclusive ownership:
    their access policies and ARM resource remain, even without --keep-resource.
    Read-only ARM preflight precedes removal; verified file unlink still precedes
    every ARM mutation, with fresh ownership/shared-reference evidence. A
    lingering ARM connection that nothing references costs money and clutter; a
    connections.json entry pointing at a deleted connection breaks every workflow
    that uses it. If this is going to fail part way, it must fail on the harmless side.
    """
    from ._managed_connection import _access_policy_id, _read_connections_file

    client = client or _vfs_client(cmd, resource_group_name, name)
    payload, _, _ = _read_connections_file(client)
    class_name, entry_name, entry = _resolve_connection_entry(payload, connection, connection_class)

    arm_id = _nested(entry, "connection", "id") if class_name == "managedApiConnections" else None
    if class_name == "managedApiConnections":
        arm_id = _managed_cleanup_id(cmd, resource_group_name, arm_id)
        _managed_delete_plan(cmd, resource_group_name, name, arm_id,
                             keep_resource=keep_resource, sender=sender, entry=entry,
                             referenced_elsewhere=_other_connection_reference(payload, arm_id, entry_name))
    observed = _remove_connections_entry(client, payload, class_name, entry_name)
    plan = _managed_delete_plan(cmd, resource_group_name, name, arm_id,
                                keep_resource=keep_resource, sender=sender, entry=entry,
                                referenced_elsewhere=_other_connection_reference(
                                    observed, arm_id, entry_name)) if arm_id else None

    removed_policies = []
    resource_removed = False
    if plan:
        for policy_name in plan["ownPolicies"]:
            try:
                _send_arm(cmd, "DELETE", _with_connection_api_version(
                    _access_policy_id(arm_id, policy_name)), sender=sender)
                removed_policies.append(policy_name)
            except ResourceNotFoundError:
                continue
        if plan["deleteResource"]:
            try:
                _send_arm(cmd, "DELETE", _with_connection_api_version(arm_id), sender=sender)
                resource_removed = True
            except ResourceNotFoundError:
                resource_removed = True

    result = {
        "name": entry_name,
        "class": class_name,
        "app": name,
        "connectionsJson": {"removed": True},
    }
    if class_name == "managedApiConnections":
        result["resource"] = {
            "id": arm_id,
            "removed": resource_removed,
            "retained": (not resource_removed) or None,
            "reason": None if resource_removed else (plan or {}).get("retainReason"),
        }
        result["accessPolicies"] = {"removed": removed_policies,
                                    "retained": (plan or {}).get("otherPolicies") or []}
    else:
        orphans = _referenced_app_settings(entry)
        result["orphanedAppSettings"] = orphans
        if orphans:
            logger.warning(
                "App settings %s were referenced only by this connection entry and are now unused. "
                "They were not deleted, because other connections or workflows may still read them. "
                "Remove them with 'az logicapp config appsettings delete' once you have confirmed "
                "nothing else uses them.", ", ".join(orphans))
    return result


def _canonical_managed_id(value):
    from ._managed_connection import _valid_access_policy_name

    parts = value.split("/") if isinstance(value, str) else []
    if (len(parts) != 9 or parts[0]
            or [parts[index].casefold() for index in (1, 3, 5, 6, 7)] != [
                "subscriptions", "resourcegroups", "providers", "microsoft.web", "connections"]
            or not all(_valid_access_policy_name(parts[index]) for index in (2, 4, 8))
            or not CONNECTION_NAME.fullmatch(parts[8])):
        raise ValidationError(
            "A canonical relative Microsoft.Web/connections resource ID is required. "
            "No connection-resource ARM request or connections.json change was attempted.")
    return value


def _managed_cleanup_id(cmd, resource_group_name, value):
    from azure.cli.core.commands import client_factory

    value = _canonical_managed_id(value)
    parts = value.split("/")
    subscription = client_factory.get_subscription_id(cmd.cli_ctx)
    if (not isinstance(subscription, str) or not isinstance(resource_group_name, str)
            or parts[2].casefold() != subscription.casefold()
            or parts[4].casefold() != resource_group_name.casefold()):
        raise ValidationError(
            "Managed cleanup is limited to the selected subscription and resource group. "
            "Cross-scope connections must be inspected and managed explicitly; connections.json was not changed.")
    return value


def _resolve_connection_entry(payload, connection, connection_class=None):
    """Locate exactly one connections.json entry, refusing an ambiguous name."""
    if connection_class is not None and connection_class not in _CONNECTION_CLASSES:
        raise ValidationError("--class must be one of: {}".format(", ".join(_CONNECTION_CLASSES)))
    matches = [item for item in _connection_entries(payload)
               if item[1] == connection and (connection_class is None or item[0] == connection_class)]
    if not matches:
        scope = " in class '{}'".format(connection_class) if connection_class else ""
        raise ResourceNotFoundError(
            "Connection '{}' was not found{} in connections.json.".format(connection, scope))
    if len(matches) > 1:
        raise ValidationError(
            "Connection '{}' exists in multiple classes: {}. Pass --class with one of those class "
            "names.".format(connection, ", ".join(item[0] for item in matches)))
    return matches[0]


def _other_connection_reference(payload, arm_id, selected_name):
    return any(
        class_name == "managedApiConnections" and entry_name != selected_name
        and str(_nested(entry, "connection", "id") or "").rstrip("/").lower()
        == str(arm_id).rstrip("/").lower()
        for class_name, entry_name, entry in _connection_entries(payload))


def _managed_delete_plan(cmd, resource_group_name, name, arm_id,
                         keep_resource=False, sender=None, entry=None, referenced_elsewhere=False):
    """Revoke only verified exclusive access selected by this connection entry.

    Assignment to an app is not ownership: user-assigned identities can serve
    multiple apps, and an assigned identity may not be used by this entry at all.
    Only the selected system-assigned principal and matching tenant establish
    exclusive access.
    """
    from ._managed_connection import _policy_principal_matches, _valid_access_policy_name

    authentication = _nested(entry, "authentication")
    authentication = authentication if isinstance(authentication, dict) else {}
    managed_identity = str(authentication.get("type") or "").lower() == "managedserviceidentity"
    explicit_identity = authentication.get("identity") is not None
    system_principal = (_app_system_principal(cmd, resource_group_name, name, sender=sender)
                        if managed_identity and not explicit_identity and not referenced_elsewhere else None)
    own_policies, other_policies = [], []
    unverified_policies = False
    try:
        listed = _send_arm(cmd, "GET", _with_connection_api_version(
            "{}/accessPolicies".format(arm_id)), sender=sender)
    except ResourceNotFoundError:
        listed = {}
    if (not isinstance(listed, dict) or not isinstance(listed.get("value"), list)
            or listed.get("nextLink") not in (None, "")):
        unverified_policies = True
    policies, names, duplicate_names = [], set(), set()
    for item in _value(listed):
        policy_name = item.get("name") if isinstance(item, dict) else None
        if not _valid_access_policy_name(policy_name):
            unverified_policies = True
            continue
        normalized_name = policy_name.casefold()
        if normalized_name in names:
            duplicate_names.add(normalized_name)
        names.add(normalized_name)
        policies.append((policy_name, _nested(item, "properties", "principal")))
    incomplete_policies = unverified_policies
    for policy_name, principal in policies:
        if incomplete_policies or policy_name.casefold() in duplicate_names:
            unverified_policies = True
            other_policies.append(policy_name)
        elif system_principal and _policy_principal_matches(principal, system_principal):
            own_policies.append(policy_name)
        else:
            other_policies.append(policy_name)

    reasons = []
    if keep_resource:
        reasons.append("--keep-resource was given.")
    if referenced_elsewhere:
        reasons.append(
            "Another connections.json entry in this app still references the ARM connection. "
            "All access policies and the ARM resource were retained.")
    elif not managed_identity:
        reasons.append(
            "The connection entry does not establish exclusive system-assigned identity ownership. "
            "All access policies and the ARM resource were retained.")
    elif explicit_identity:
        reasons.append(
            "The connection entry selects a user-assigned or unresolved managed identity, which may "
            "be shared by other apps. All access policies and the ARM resource were retained.")
    elif not system_principal:
        reasons.append(
            "The app's system-assigned principal and tenant could not be verified. "
            "All access policies and the ARM resource were retained.")
    elif other_policies:
        reasons.append(
            "The connection also grants access through {} access policy entries not exclusively owned "
            "by this entry, so it is shared. Only this app's connections.json entry and any "
            "verified exclusive system-assigned access policies were removed. "
            "Delete the connection itself with 'az resource delete --ids {}' once you have "
            "confirmed nothing else uses it.".format(len(other_policies), arm_id))
    elif not own_policies:
        reasons.append(
            "No access policy proves exclusive ownership by this connection entry's system-assigned "
            "identity. Only this app's connections.json entry was removed.")
    if unverified_policies:
        reasons.append(
            "The complete access policy list could not be verified, so the ARM resource was retained.")
    if duplicate_names:
        reasons.append(
            "Duplicate access policy names have ambiguous ownership; all affected policies were retained.")
    reason = " ".join(reasons) or None
    return {
        "ownPolicies": own_policies,
        "otherPolicies": other_policies,
        "deleteResource": reason is None,
        "retainReason": reason,
    }


def _app_system_principal(cmd, resource_group_name, name, sender=None):
    """Read the exclusive system principal and tenant from the selected site."""
    from ._identity import get_identity

    try:
        identity = get_identity(cmd, resource_group_name, name, sender=sender)
    except (ResourceNotFoundError, ValidationError):
        return None
    identity_types = {part.strip().lower() for part in str(identity.get("type") or "").split(",")}
    if "systemassigned" not in identity_types:
        return None
    principal = identity.get("principalId")
    tenant = identity.get("tenantId")
    if not all(isinstance(value, str) and value.strip() and value == value.strip()
               for value in (principal, tenant)):
        return None
    return {"objectId": principal.casefold(), "tenantId": tenant.casefold()}


def _remove_connections_entry(client, payload, class_name, entry_name):
    from ._managed_connection import _read_connections_file

    try:
        current, _, etag = _read_connections_file(client)
    except (CLIError, OSError, ValueError, TypeError) as error:
        raise ClientRequestError(
            "The connections.json file could not be reread. No removal or ARM cleanup was attempted.") from error
    section = current.get(class_name) if isinstance(current, dict) else None
    if (not isinstance(section, dict) or entry_name not in section
            or not json_equal(section[entry_name], payload[class_name][entry_name])):
        raise ValidationError(
            "The selected connections.json entry changed before removal. "
            "No removal or ARM cleanup was attempted; inspect the current file.")
    etag = validate_file_etag(etag, description=CONNECTIONS_FILE)
    current = copy.deepcopy(current)
    del current[class_name][entry_name]
    try:
        receipt = client.put_raw(
            CONNECTIONS_FILE, json.dumps(current, indent=2, allow_nan=False).encode("utf-8"), if_match=etag)
    except (CLIError, OSError, ValueError, TypeError) as error:
        if response_status_from_error(error) == 412:
            raise ClientRequestError(
                "The connections.json revision changed before removal. The runtime rejected the ETag; "
                "no retry or ARM cleanup was attempted. Inspect the current file.") from error
        raise ClientRequestError(
            "The connections.json removal request failed and its outcome may be uncertain. "
            "No ARM cleanup was attempted; inspect the file before retrying.") from error
    if isinstance(receipt, dict) and receipt.get("statusCode") == 412:
        raise ClientRequestError(
            "The connections.json revision changed before removal. The runtime rejected the ETag; "
            "no retry or ARM cleanup was attempted. Inspect the current file.")
    if not isinstance(receipt, dict) or receipt.get("statusCode") not in (200, 201, 204):
        raise ClientRequestError(
            "The connections.json removal did not return a completed write receipt. "
            "No ARM cleanup was attempted; inspect the file before retrying.")
    try:
        observed, observed_raw, _ = _read_connections_file(client)
    except (CLIError, OSError, ValueError, TypeError) as error:
        raise ClientRequestError(
            "The connections.json write was acknowledged, but removal readback failed. "
            "No ARM cleanup was attempted; inspect the file before retrying.") from error
    remaining = observed.get(class_name, {}) if isinstance(observed, dict) else None
    if observed_raw is None or not isinstance(remaining, dict) or entry_name in remaining:
        raise ClientRequestError(
            "The connections.json write was acknowledged, but selected-entry removal could not be "
            "verified. No ARM cleanup was attempted; inspect the file before retrying.")
    return observed


def _referenced_app_settings(entry):
    """App setting names this entry referenced, so a caller can spot the leftovers."""
    found = []

    def walk(value):
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            match = re.search(r"appsetting\(\s*'([^']+)'\s*\)", value, re.IGNORECASE)
            if match and match.group(1) not in found:
                found.append(match.group(1))

    walk(entry)
    return found


def connection_list_table_format(result):
    if not result:
        return []
    return [_connection_table_row(item) for item in result.get("value", [])]


def connection_show_table_format(result):
    if not result:
        return []
    return [_connection_table_row(result)]


def _connection_show_response(payload, connection, connection_class=None, show_runtime_urls=False):
    class_name, entry_name, entry = _resolve_connection_entry(payload, connection, connection_class)
    return _redacted_deployed_connection(class_name, entry_name, entry, show_runtime_urls)


def _connection_entries(payload):
    if not isinstance(payload, dict):
        return []
    entries = []
    for class_name in _CONNECTION_CLASSES:
        class_map = payload.get(class_name)
        if not isinstance(class_map, dict):
            continue
        for name, entry in class_map.items():
            if isinstance(entry, dict):
                entries.append((class_name, name, entry))
    return entries


def _redacted_deployed_connection(class_name, name, entry, show_runtime_urls=False):
    result = dict(entry)
    result["name"] = name
    result["class"] = class_name
    if "parameterValues" in result:
        result["parameterValues"] = _redact_parameter_values(result.get("parameterValues"))
    if not show_runtime_urls and "connectionRuntimeUrl" in result:
        result["connectionRuntimeUrl"] = _redact_runtime_url(result.get("connectionRuntimeUrl"))
    return result


def _redact_parameter_values(value):
    if isinstance(value, dict):
        return {key: _redact_parameter_values(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_redact_parameter_values(item) for item in value]
    if isinstance(value, str) and _APP_SETTING_REFERENCE.match(value):
        return value
    return LOGICAPP_REDACTION_SENTINEL


def _redact_runtime_url(value):
    if isinstance(value, dict):
        result = dict(value)
        if "value" in result:
            result["value"] = LOGICAPP_REDACTION_SENTINEL
        if "uri" in result:
            result["uri"] = LOGICAPP_REDACTION_SENTINEL
        return result
    if value is None:
        return None
    return LOGICAPP_REDACTION_SENTINEL


def _connection_table_row(item):
    return {
        "Name": item.get("name"),
        "Class": item.get("class"),
        "DisplayName": item.get("displayName"),
        "ProviderId": _nested(item, "serviceProvider", "id") or _nested(item, "api", "id"),
        "ConnectionId": _nested(item, "connection", "id") if item.get("class") == "managedApiConnections" else None,
    }


def _resolve_connection_for_test(cmd, resource_group_name, name, connection, connection_class=None,
                                 vfs_client=None, runtime_client=None, sender=None):
    if connection_class is not None and connection_class not in _CONNECTION_CLASSES:
        raise ValidationError("--class must be one of: {}".format(", ".join(_CONNECTION_CLASSES)))
    if str(connection or "").startswith("/"):
        arm = _get_arm_connection(cmd, str(connection), sender=sender)
        return _managed_test_target(None, arm, arm.get("id") or str(connection))
    client = vfs_client or _vfs_client(cmd, resource_group_name, name)
    payload = client.get(CONNECTIONS_FILE)
    entry = _connection_show_response(payload, connection, connection_class=connection_class, show_runtime_urls=True)
    if entry.get("class") == "serviceProviderConnections":
        return {"name": entry.get("name"), "id": None, "class": "serviceProviderConnections", "entry": entry,
                "cmd": cmd, "resourceGroup": resource_group_name, "app": name, "runtimeClient": runtime_client}
    arm_id = _nested(entry, "connection", "id")
    if arm_id:
        return _managed_test_target(entry.get("name"), _get_arm_connection(cmd, arm_id, sender=sender), arm_id)
    return _managed_test_target(entry.get("name"), entry, None)


def _managed_test_target(name, payload, arm_id):
    connection_name = name or payload.get("name") if isinstance(payload, dict) else name
    return {"name": connection_name, "id": arm_id, "class": "managedApiConnections", "entry": payload}


def _test_managed_connection(cmd, target, sender=None):
    props = _properties(target.get("entry"))
    links = props.get("testLinks") if isinstance(props.get("testLinks"), list) else []
    requests = props.get("testRequests") if isinstance(props.get("testRequests"), list) else []
    connection = _connection_identity(target)
    if not links:
        return _connection_test_result(
            "noTestAvailable", connection, _TEST_PATH_NONE, None, None, None,
            "No test endpoint is advertised for connection '{}'; the connection was not verified.".format(
                connection.get("name") or connection.get("id") or "<unknown>"), None)
    link = links[0]
    try:
        return _invoke_test_request(cmd, connection, link, _TEST_PATH_MANAGED_LINK, sender=sender)
    except Exception as ex:  # pylint: disable=broad-except
        if not requests:
            return _exception_test_result(connection, link, _TEST_PATH_MANAGED_LINK, ex)
    try:
        return _invoke_test_request(cmd, connection, requests[0], _TEST_PATH_MANAGED_FALLBACK, sender=sender)
    except Exception as ex:  # pylint: disable=broad-except
        return _exception_test_result(connection, requests[0], _TEST_PATH_MANAGED_FALLBACK, ex)


def _test_service_provider_connection(cmd, target, runtime_client=None, sender=None):
    entry = target.get("entry") or {}
    connector_id = _nested(entry, "serviceProvider", "id")
    connection = _connection_identity(target)
    client = runtime_client or _runtime_client(cmd, target.get("resourceGroup"), target.get("app"))
    operation_group = _find_operation_group(client.get(operation_groups_path()), connector_id)
    props = _properties(operation_group)
    url = props.get("testConnectionUrl")
    if not url:
        return _connection_test_result(
            "noTestAvailable", connection, _TEST_PATH_NONE, None, None, None,
            "No test endpoint is advertised for connection '{}'; the connection was not verified.".format(
                connection.get("name") or "<unknown>"), None)
    request = {"method": "GET", "requestUri": url}
    try:
        return _invoke_test_request(cmd, connection, request, _TEST_PATH_SERVICE_PROVIDER, sender=sender)
    except Exception as ex:  # pylint: disable=broad-except
        return _exception_test_result(connection, request, _TEST_PATH_SERVICE_PROVIDER, ex)


def _invoke_test_request(cmd, connection, request, test_path, sender=None):
    method = str(request.get("method") or "GET").upper()
    uri = request.get("requestUri")
    body = request.get("body")
    if not uri:
        return _connection_test_result(
            "noTestAvailable", connection, _TEST_PATH_NONE, None, None, None,
            "No test endpoint is advertised for connection '{}'; the connection was not verified.".format(
                connection.get("name") or connection.get("id") or "<unknown>"), None)
    send = sender or send_raw_request
    try:
        response = send(
            cmd.cli_ctx, method, uri, headers=["Content-Type=application/json"],
            body=json.dumps(body) if body is not None else None)
        status = getattr(response, "status_code", None)
        headers = getattr(response, "headers", {}) or {}
    except HTTPError as ex:
        status = response_status_from_error(ex)
        headers = response_headers_from_error(ex)
    return _status_test_result(connection, test_path, status, method, uri, headers)


def _status_test_result(connection, test_path, status, method, uri, headers):
    retry_after = parse_retry_after(headers)
    if status is not None and 200 <= int(status) < 300:
        return _connection_test_result("passed", connection, test_path, status, method, uri, "Connection test passed.", None)
    if status == 429:
        return _connection_test_result(
            "couldNotReach", connection, test_path, status, method, uri,
            "Connection test was throttled by the platform; retry later.", retry_after)
    if status in (401, 403):
        # The platform answered and refused the *test* operation. That is a different
        # fact from "this connection does not work": a connector's generic test
        # operation routinely needs broader rights than the operations a workflow
        # actually calls, so a sender-only identity fails the test while sending fine.
        return _connection_test_result(
            "authorizationFailed", connection, test_path, status, method, uri,
            "The connection's test operation was refused with HTTP status {}. This reports the "
            "permissions of the test operation, which are often broader than the operations a "
            "workflow uses, so the connection may still work for its intended actions. Verify by "
            "running the workflow.".format(status),
            retry_after)
    message = "Connection test failed with HTTP status {}.".format(status if status is not None else "unknown")
    if test_path == _TEST_PATH_SERVICE_PROVIDER and status == 400:
        message += (" A built-in connector's test operation can require permissions beyond those "
                    "the workflow itself needs, so this does not by itself prove the connection is "
                    "unusable. Verify by running the workflow.")
    return _connection_test_result("failed", connection, test_path, status, method, uri, message, retry_after)


def _exception_test_result(connection, request, test_path, ex):
    status = response_status_from_error(ex)
    headers = response_headers_from_error(ex)
    if status is not None:
        return _status_test_result(
            connection, test_path, status, str(request.get("method") or "GET").upper(), request.get("requestUri"), headers)
    return _connection_test_result(
        "couldNotReach", connection, test_path, None, str(request.get("method") or "GET").upper(),
        request.get("requestUri"), "Connection test request could not reach the platform: {}".format(ex), None)


def _connection_test_result(outcome, connection, test_path, http_status, method, request_uri, message, retry_after):
    return {
        "outcome": outcome,
        "connection": connection,
        "testPath": test_path,
        "httpStatus": http_status,
        "method": method,
        "requestUri": _redact_uri(request_uri),
        "message": message,
        "retryAfter": retry_after,
    }


def _connection_identity(target):
    return {"name": target.get("name"), "id": target.get("id"), "class": target.get("class")}


def _finish_connection_test(result, exit_on_nonzero=True):
    if result.get("outcome") == "passed":
        return result
    if not exit_on_nonzero:
        return result
    print(json.dumps(result, sort_keys=True))
    if result.get("outcome") == "noTestAvailable":
        raise ResourceNotFoundError(result.get("message"))
    raise CLIError(result.get("message"))


def _get_arm_connection(cmd, connection_id, sender=None):
    connection_id = _canonical_managed_id(connection_id)
    return _send_arm(cmd, "GET", _with_connection_api_version(connection_id), sender=sender)


def _send_arm(cmd, method, url, body=None, sender=None):
    send = sender or send_raw_request
    try:
        response = send(
            cmd.cli_ctx, method, url, headers=["Content-Type=application/json"],
            body=json.dumps(body) if body is not None else None)
    except HTTPError as ex:
        if response_status_from_error(ex) == 404:
            raise ResourceNotFoundError(str(ex)) from ex
        raise
    content = getattr(response, "content", None)
    if not content:
        return {}
    try:
        from ._json import strict_json_loads
        payload = strict_json_loads(content)
    except (ValueError, TypeError, RecursionError):
        raise ClientRequestError("The ARM connection service returned invalid JSON.") from None
    return payload


def _with_connection_api_version(connection_id):
    separator = "&" if "?" in connection_id else "?"
    return "{}{}api-version={}".format(connection_id, separator, _ARM_CONNECTION_API_VERSION)


def _vfs_client(cmd, resource_group_name, name):
    return SiteVfsClient(cmd, _site_resource_id(cmd, resource_group_name, name))


def _runtime_client(cmd, resource_group_name, name):
    return SiteRuntimeClient(cmd, _site_resource_id(cmd, resource_group_name, name))


def _site_resource_id(cmd, resource_group_name, name):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return "/subscriptions/{}/resourceGroups/{}{}{}".format(
        subscription_id, resource_group_name, _SITE_PROVIDER, name)


def _properties(raw):
    if not isinstance(raw, dict):
        return {}
    props = raw.get("properties")
    return props if isinstance(props, dict) else raw


def _find_operation_group(payload, connector):
    wanted = str(connector or "").strip().lower()
    for item in _value(payload):
        if not isinstance(item, dict):
            continue
        candidates = [item.get("name"), item.get("id")]
        item_id = item.get("id")
        if isinstance(item_id, str):
            candidates.append(item_id.rstrip("/").split("/")[-1])
        if any(isinstance(candidate, str) and candidate.strip().lower() == wanted for candidate in candidates):
            return item
    return None


def _value(payload):
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        value = payload.get("value")
        return value if isinstance(value, list) else []
    return []


def _nested(source, *keys):
    current = source
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _slice_deployed_items(items, next_token=None, max_items=None):
    return slice_items(items, next_token=next_token, max_items=max_items)


def _redact_uri(uri):
    if not uri:
        return None
    parsed = urlparse(str(uri))
    sensitive = ("sig=", "code=", "access_token=", "client_secret=")
    if any(marker in parsed.query.lower() for marker in sensitive):
        return "{}://{}{}?{}".format(parsed.scheme, parsed.netloc, parsed.path, LOGICAPP_REDACTION_SENTINEL)
    return str(uri)
