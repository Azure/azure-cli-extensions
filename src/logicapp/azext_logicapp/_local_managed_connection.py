# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Local managed-connection scope and guarded, non-transactional file publication."""

import copy
import json
import os
import re
import stat
import tempfile
from uuid import UUID

# pylint: disable=import-error,no-name-in-module
from azure.cli.core._profile import Profile
from azure.cli.core.azclierror import FileOperationError, RequiredArgumentMissingError, ValidationError

from ._connection import is_tracked_by_git, require_project
from ._context import _cloud_coordinate, _store_lock
from ._json import strict_json_loads
from ._managed_api import _managed_api_id, _quote_segment

MAX_FILE_BYTES = 1024 * 1024
SCOPE_SETTINGS = {
    "subscription": "WORKFLOWS_SUBSCRIPTION_ID",
    "resourceGroup": "WORKFLOWS_RESOURCE_GROUP_NAME",
    "location": "WORKFLOWS_LOCATION_NAME",
}


def _safe_path(path):
    current = path
    while True:
        if os.path.lexists(current):
            info = os.lstat(current)
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValidationError("Local managed connection paths must not contain links or reparse points.")
        parent = os.path.dirname(current)
        if parent == current:
            return
        current = parent


def _snapshot(path, required=False):
    try:
        _safe_path(path)
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValidationError("Local managed connection files must be regular, unaliased files.")
        flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        with os.fdopen(os.open(path, flags), "rb") as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise ValidationError("Local managed connection files must be regular, unaliased files.")
            data = handle.read(MAX_FILE_BYTES + 1)
            after = os.fstat(handle.fileno())
        if len(data) > MAX_FILE_BYTES or _identity(before) != _identity(after):
            raise ValidationError("A local managed connection file is oversized or changed during reading.")
        _safe_path(path)
        if _identity(os.stat(path)) != _identity(after):
            raise ValidationError("A local managed connection file changed during reading.")
        return _identity(after), data
    except FileNotFoundError:
        if not required:
            return None
        raise RequiredArgumentMissingError(
            "Local managed connections require an existing host.json and unencrypted local.settings.json.") from None
    except OSError:
        raise FileOperationError("Could not read local managed connection files; inspect the project before retrying.") from None


def _identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _document(snapshot, label):
    if snapshot is None:
        return {}
    try:
        payload = strict_json_loads(snapshot[1].decode("utf-8-sig"))
    except (ValueError, UnicodeError, RecursionError):
        raise ValidationError("{} must contain valid JSON; its contents were not changed.".format(label)) from None
    if not isinstance(payload, dict):
        raise ValidationError("{} must contain a JSON object.".format(label))
    return payload


def _coordinate(explicit, values, field, flag):
    value = explicit if explicit is not None else values.get(SCOPE_SETTINGS[field])
    if value is None or value == "":
        raise RequiredArgumentMissingError(
            "Local managed connections require {} or local.settings.json Values.{}.".format(
                flag, SCOPE_SETTINGS[field]))
    if not isinstance(value, str) or value != value.strip():
        raise ValidationError("{} must be a literal, non-empty Azure coordinate.".format(flag))
    if field == "subscription":
        try:
            if str(UUID(value)).casefold() != value.casefold():
                raise ValueError()
        except ValueError:
            source = flag if explicit is not None else SCOPE_SETTINGS[field]
            raise ValidationError(
                "{} must resolve to a subscription UUID; sign in and check the subscription ID or name.".format(
                    source)) from None
        return value
    _cloud_coordinate(value)
    if field == "resourceGroup" and (not re.fullmatch(r"[\w().-]+", value) or value.endswith(".")):
        raise ValidationError("--resource-group or WORKFLOWS_RESOURCE_GROUP_NAME must be a literal resource group name.")
    if field == "location" and not re.fullmatch(r"[A-Za-z0-9]+", value):
        raise ValidationError("--location or WORKFLOWS_LOCATION_NAME must be an Azure location name, such as eastus.")
    return value


class LocalConnectionsFile:  # pylint: disable=too-many-instance-attributes
    def __init__(self, cmd, root, name, resource_group=None, location=None, force=False):
        self.root = require_project(root)
        self.name = name
        self.key_setting = name + "-connectionKey"
        self.paths = {filename: os.path.join(self.root, filename)
                      for filename in ("host.json", "local.settings.json", "connections.json", ".gitignore")}
        self.before = {filename: _snapshot(path, required=filename in ("host.json", "local.settings.json"))
                       for filename, path in self.paths.items()}
        _document(self.before["host.json"], "host.json")
        self.settings = _document(self.before["local.settings.json"], "local.settings.json")
        if self.settings.get("IsEncrypted") is not False:
            raise ValidationError("Local managed connections require local.settings.json IsEncrypted=false.")
        values = self.settings.get("Values")
        if not isinstance(values, dict) or any(not isinstance(value, str) for value in values.values()):
            raise ValidationError("local.settings.json Values must be an object of string values.")
        subscription = _coordinate(cmd.cli_ctx.data.get("subscription_id"), values, "subscription", "--subscription")
        self.resource_group = _coordinate(resource_group, values, "resourceGroup", "--resource-group")
        self.location = _coordinate(location, values, "location", "--location")
        account = Profile(cli_ctx=cmd.cli_ctx).get_subscription(subscription=subscription)
        if not isinstance(account.get("id"), str) or account["id"].casefold() != subscription.casefold():
            raise ValidationError("The selected Azure CLI account does not match the project's subscription.")
        self.subscription = account["id"]
        self.connection_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/connections/{}".format(
            self.subscription, _quote_segment(self.resource_group), _quote_segment(name))
        self.connections = _document(self.before["connections.json"], "connections.json")
        entries = self.connections.get("managedApiConnections", {})
        if not isinstance(entries, dict):
            raise ValidationError("connections.json managedApiConnections must be an object.")
        if not force and (name in entries or self.key_setting in values):
            raise ValidationError(
                "Local managed connection wiring or its key setting already exists; use --force to replace it.")
        try:
            self.ignore = (self.before[".gitignore"][1].decode("utf-8-sig")
                           if self.before[".gitignore"] is not None else "")
        except UnicodeError:
            raise ValidationError(".gitignore must be readable UTF-8 before a local connection key is saved.") from None
        self.tracked = is_tracked_by_git(self.root, "local.settings.json")
        if self.tracked:
            raise ValidationError(
                "local.settings.json is tracked by Git. Untrack it before storing a development connection key.")
        self.lock_path = os.path.join(self.root, ".azurelogicapps", "managed-connections")
        _safe_path(self.lock_path)
        _safe_path(self.lock_path + ".lock")
        if os.path.exists(os.path.dirname(self.lock_path)) and not os.path.isdir(os.path.dirname(self.lock_path)):
            raise ValidationError(".azurelogicapps must be a directory, not a file.")

    def connector_id(self, cmd, connector):
        if not isinstance(connector, str) or connector != connector.strip() or any(
                character in connector for character in ("?", "#", "%", "\\")):
            raise ValidationError("--connector must be a literal managed API name or resource ID, without query or fragment.")
        resolved = _managed_api_id(cmd, connector, self.location, subscription=self.subscription)
        expected = "/subscriptions/{}/providers/Microsoft.Web/locations/{}/managedApis/".format(
            self.subscription, self.location)
        if not resolved.casefold().startswith(expected.casefold()):
            raise ValidationError("The managed API ID must match the selected subscription and location.")
        name = resolved[len(expected):]
        if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
            raise ValidationError("The managed API ID must identify one literal connector.")
        return resolved

    def check_unchanged(self):
        for filename, path in self.paths.items():
            if _snapshot(path) != self.before[filename]:
                raise ValidationError(
                    "Local project files changed during connection creation; no further local files were written. "
                    "Inspect retained Azure resources and local files before retrying.")

    def _publish(self, filename, path, data):
        # Not a multi-file transaction or CAS against noncooperating writers.
        self.check_unchanged()
        os.replace(path, self.paths[filename])
        self.before[filename] = _snapshot(self.paths[filename], required=True)
        if self.before[filename][1] != data:
            raise ValidationError("Local connection publication could not be verified; inspect local files.")

    def write(self, entry, key):
        settings = copy.deepcopy(self.settings)
        settings["Values"][self.key_setting] = key
        connections = copy.deepcopy(self.connections)
        connections.setdefault("managedApiConnections", {})[self.name] = entry
        rules = [line.rstrip() for line in self.ignore.splitlines()
                 if line.rstrip() and not line.startswith("#")]
        ignored = (len(rules) >= 2 and rules[-2] == "/.azurelogicapps/"
                   and rules[-1] in ("local.settings.json", "/local.settings.json"))
        payloads = {}
        if not ignored:
            payloads[".gitignore"] = (
                self.ignore.rstrip("\r\n") +
                "\n# Holds local secrets. Never commit.\n/.azurelogicapps/\nlocal.settings.json\n").encode("utf-8")
        payloads.update({
            "local.settings.json": (json.dumps(settings, indent=2, allow_nan=False) + "\n").encode("utf-8"),
            "connections.json": (json.dumps(connections, indent=2, allow_nan=False) + "\n").encode("utf-8"),
        })
        if any(len(data) > MAX_FILE_BYTES for data in payloads.values()):
            raise ValidationError("Local managed connection output exceeds the supported file-size limit.")
        temporary = []
        try:
            _safe_path(self.lock_path)
            with _store_lock(self.lock_path, label="Local managed connection files"):
                self.check_unchanged()
                for filename, data in payloads.items():
                    self.check_unchanged()
                    handle, path = tempfile.mkstemp(prefix=".managed-connection-", dir=os.path.dirname(self.lock_path))
                    temporary.append((filename, path))
                    with os.fdopen(handle, "wb") as stream:
                        stream.write(data)
                        stream.flush()
                        os.fsync(stream.fileno())
                    if filename == ".gitignore":
                        # Exclude private staging before any credential bytes are written.
                        self._publish(filename, path, data)
                self.check_unchanged()
                for filename, path in temporary:
                    if filename != ".gitignore":
                        self._publish(filename, path, payloads[filename])
        except OSError:
            raise FileOperationError(
                "Could not finish local managed connection publication. Files may be partially updated; "
                "inspect the project and retained Azure connection before retrying.") from None
        finally:
            cleanup_failed = False
            for _, path in temporary:
                try:
                    os.unlink(path)
                except FileNotFoundError:
                    pass
                except OSError:
                    cleanup_failed = True
            if cleanup_failed:
                raise FileOperationError(
                    "Could not remove a private managed connection temporary file; inspect .azurelogicapps.")
        return True
