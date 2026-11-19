# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import errno
import json
import math
import os
import stat
import tempfile
import time
from collections import OrderedDict
from contextlib import contextmanager

# pylint: disable=import-error,no-name-in-module
from azure.cli.core.azclierror import (
    CLIError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError,
    ResourceNotFoundError, ValidationError)
from azure.cli.core.util import user_confirmation
from azure.cli.core._environment import get_config_dir

from ._json import json_equal
from ._workflow import abs_path


STORE_DIRNAME = "logicapp"
STORE_FILENAME = "contexts.json"
LOCK_TIMEOUT = 5
TARGET_FIELDS = ("kind", "path", "port", "resourceGroup", "logicAppName")
_MAX_STORE_DEPTH = 128


def store_path():
    return os.path.abspath(os.path.join(get_config_dir(), STORE_DIRNAME, STORE_FILENAME))


def load_store():
    path = store_path()
    try:
        _regular_file(path)
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except FileNotFoundError:
        return {"active": None, "contexts": {}}
    except (OSError, ValueError, RecursionError):
        raise CLIError("Logic Apps context store is unreadable: {}".format(path)) from None
    try:
        _validate_store(data)
    except ValidationError as ex:
        raise CLIError("Logic Apps context store has an invalid or unsupported schema: {}".format(path)) from ex
    data.setdefault("active", None)
    return data


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate context store field.")
        result[key] = value
    return result


def _invalid_constant(_value):
    raise ValueError("Non-finite numbers are not valid context store JSON.")


def _regular_file(path, label="Logic Apps context storage"):
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode):
        raise CLIError("{} must be a regular file, not a link or directory.".format(label))


def _text(value, label):
    if (not isinstance(value, str) or not value.strip() or value != value.strip()
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise ValidationError("{} must be a non-empty string without surrounding whitespace or control characters.".format(label))
    reject_secret_shaped_value(value)
    return value


def _port(value):
    if type(value) is not int or not 1 <= value <= 65535:  # pylint: disable=unidiomatic-typecheck
        raise ValidationError("--port must be an integer between 1 and 65535.")
    return value


def _cloud_coordinate(value):
    value = _text(value, "Cloud target coordinate")
    if (value in (".", "..") or not value.isprintable()
            or any(char in value for char in "/\\%?#")):
        raise ValidationError("Cloud targets require literal single-segment names, not resource IDs, URLs or escaped values.")
    return value


def _validate_target(target):
    if not isinstance(target, dict):
        raise ValidationError("A context target must be an object.")
    kind = target.get("kind")
    if kind == "local":
        path = _text(target.get("path"), "Local context path")
        if not os.path.isabs(path):
            raise ValidationError("Local context path must be absolute.")
        _port(target.get("port"))
        if target.get("resourceGroup") is not None or target.get("logicAppName") is not None:
            raise ValidationError("Local contexts cannot contain cloud coordinates.")
    elif kind == "cloud":
        for field in ("resourceGroup", "logicAppName"):
            _cloud_coordinate(target.get(field))
        if target.get("path") is not None or target.get("port") is not None:
            raise ValidationError("Cloud contexts cannot contain local coordinates.")
    else:
        raise ValidationError("Context target kind must be local or cloud.")


def _validate_store(data):
    pending = [(data, 0)]
    while pending:
        value, depth = pending.pop()
        if depth > _MAX_STORE_DEPTH:
            raise ValidationError("Context store exceeds the supported nesting limit.")
        if isinstance(value, dict):
            pending.extend((item, depth + 1) for item in value.values())
        elif isinstance(value, list):
            pending.extend((item, depth + 1) for item in value)
        elif isinstance(value, float) and not math.isfinite(value):
            raise ValidationError("Non-finite numbers are not valid context store JSON.")
    if not isinstance(data, dict) or not isinstance(data.get("contexts"), dict):
        raise ValidationError("A context store must contain a contexts object.")
    if "version" in data and (type(data["version"]) is not int or data["version"] != 1):  # pylint: disable=unidiomatic-typecheck
        raise ValidationError("Unsupported context store version.")
    for name, context in data["contexts"].items():
        _text(name, "Context name")
        if not isinstance(context, dict) or context.get("name") != name:
            raise ValidationError("Context record name must match its saved key.")
        _validate_target(context.get("target"))
    active = data.get("active")
    if active is not None:
        _text(active, "Active context name")
        if active not in data["contexts"]:
            raise ValidationError("Active context must reference a saved context.")


@contextmanager
def _store_lock(path, label="Logic Apps context store"):
    lock_path = path + ".lock"
    handle = None
    locked = False
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.lexists(lock_path):
            _regular_file(lock_path, label)
        handle = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        if not stat.S_ISREG(os.fstat(handle).st_mode):
            raise CLIError("{} lock must be a regular file.".format(label))
        deadline = time.monotonic() + LOCK_TIMEOUT
        while not locked:
            try:
                _lock_file(handle)
                locked = True
            except OSError as ex:
                if ex.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if time.monotonic() >= deadline:
                    raise CLIError("{} is busy. Retry after the other writer finishes.".format(label)) from ex
                time.sleep(0.05)
        yield
    except OSError as ex:
        raise CLIError("Could not lock or write {}: {}".format(label, path)) from ex
    finally:
        if handle is not None:
            try:
                if locked:
                    _unlock_file(handle)
            finally:
                os.close(handle)


def _lock_file(handle):
    if os.name == "nt":
        import msvcrt  # pylint: disable=import-outside-toplevel
        os.lseek(handle, 0, os.SEEK_SET)
        msvcrt.locking(handle, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl  # pylint: disable=import-outside-toplevel,import-error
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(handle):
    if os.name == "nt":
        import msvcrt  # pylint: disable=import-outside-toplevel
        os.lseek(handle, 0, os.SEEK_SET)
        msvcrt.locking(handle, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl  # pylint: disable=import-outside-toplevel,import-error
        fcntl.flock(handle, fcntl.LOCK_UN)


def save_store(data, expected=None):
    _validate_store(data)
    if expected is None:
        raise ValidationError("Context writes require the previously read store snapshot.")
    path = store_path()
    with _store_lock(path):
        if not json_equal(load_store(), expected):
            raise CLIError("Logic Apps context store changed during this operation. No context change was written; inspect it and retry.")
        if not json_equal(data, expected):
            _publish_store(path, data)
    return path


def _publish_store(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=os.path.dirname(path),
                                         prefix=".contexts-", suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            json.dump(data, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    except (OSError, ValueError) as ex:
        raise CLIError("Could not publish Logic Apps context store; the previous store was not replaced: {}".format(path)) from ex
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            except OSError as ex:
                raise CLIError(
                    "Could not publish Logic Apps context store; the previous store was not replaced. "
                    "Temporary-file cleanup also failed; inspect: {}".format(temporary)) from ex


def reject_secret_shaped_value(value):
    lowered = str(value or "").lower()
    if any(marker in lowered for marker in (
            "accountkey=", "sharedaccesskey=", "sharedaccesssignature=", "sig=", "client_secret",
            "bearer ", "password=", "access_token=")):
        raise ValidationError("Context values must not contain credentials.")


def get_context(name=None):
    data = load_store()
    return _select_context(name, data), data


def _select_context(name, data):
    if name is not None:
        _text(name, "Context name")
    target_name = name if name is not None else data.get("active")
    if not target_name:
        return None
    context = data["contexts"].get(target_name)
    if context is None:
        raise ResourceNotFoundError("Logic Apps context '{}' was not found.".format(target_name))
    return context


def context_result(context, data=None):
    data = load_store() if data is None else data
    target = context.get("target", {})
    return {
        "name": context.get("name"),
        "active": data.get("active") == context.get("name"),
        "store": store_path(),
        "target": {
            "kind": target.get("kind"),
            "path": target.get("path"),
            "port": target.get("port"),
            "resourceGroup": target.get("resourceGroup"),
            "logicAppName": target.get("logicAppName"),
        }
    }


def _local_target(path, port):
    _text(path, "--path")
    target = {"kind": "local", "path": abs_path(path), "port": _port(port),
              "resourceGroup": None, "logicAppName": None}
    _validate_target(target)
    return target


def _cloud_target(resource_group_name, logic_app_name):
    target = {"kind": "cloud", "path": None, "port": None,
              "resourceGroup": resource_group_name, "logicAppName": logic_app_name}
    _validate_target(target)
    return target


def create_context(name, path=None, resource_group_name=None, logic_app_name=None, port=7071, use=False):
    _text(name, "Context name")
    local_mode = path is not None
    cloud_mode = resource_group_name is not None or logic_app_name is not None
    if local_mode and cloud_mode:
        raise MutuallyExclusiveArgumentError("--path cannot be used with --resource-group or --logic-app-name.")
    if not local_mode and not cloud_mode:
        raise RequiredArgumentMissingError("A local --path or cloud --resource-group and --logic-app-name target is required.")
    if cloud_mode and (not resource_group_name or not logic_app_name):
        raise RequiredArgumentMissingError("--resource-group and --logic-app-name are required for a cloud context.")
    target = _local_target(path, port) if local_mode else _cloud_target(resource_group_name, logic_app_name)
    original = load_store()
    data = copy.deepcopy(original)
    existing = data["contexts"].get(name)
    if existing is not None:
        if any(existing["target"].get(field) != target[field] for field in TARGET_FIELDS):
            raise ValidationError("Context '{}' already exists with a different target.".format(name))
        context = existing
    else:
        context = {"name": name, "target": target}
        data["contexts"][name] = context
    if use:
        data["active"] = name
    save_store(data, expected=original)
    return context_result(context, data)


def use_context(name):
    context, original = get_context(name)
    data = copy.deepcopy(original)
    data["active"] = name
    save_store(data, expected=original)
    return context_result(context, data)


def list_contexts():
    data = load_store()
    return [context_result(data["contexts"][name], data) for name in sorted(data["contexts"])]


def show_context(name=None):
    context, data = get_context(name)
    if context is None:
        raise ResourceNotFoundError("No active Logic Apps context. Use --name to inspect a saved context.")
    return context_result(context, data)


def _updated_target(current, kind, path, port, resource_group_name, logic_app_name):
    selected_kind = kind if kind is not None else current["kind"]
    if selected_kind not in ("local", "cloud"):
        raise ValidationError("--kind must be local or cloud.")
    transition = selected_kind != current["kind"]
    if selected_kind == "local":
        if resource_group_name is not None or logic_app_name is not None:
            raise MutuallyExclusiveArgumentError("Local updates cannot contain --resource-group or --logic-app-name; use --kind cloud with both coordinates to switch.")
        if transition and (path is None or port is None):
            raise RequiredArgumentMissingError("Switching to local requires --kind local, --path and --port.")
        values = _local_target(path if path is not None else current["path"],
                               port if port is not None else current["port"])
    else:
        if path is not None or port is not None:
            raise MutuallyExclusiveArgumentError("Cloud updates cannot contain --path or --port; use --kind local with both coordinates to switch.")
        if transition and (resource_group_name is None or logic_app_name is None):
            raise RequiredArgumentMissingError("Switching to cloud requires --kind cloud, --resource-group and --logic-app-name.")
        values = _cloud_target(resource_group_name if resource_group_name is not None else current["resourceGroup"],
                               logic_app_name if logic_app_name is not None else current["logicAppName"])
    updated = copy.deepcopy(current)
    updated.update(values)
    return updated


def update_context(cmd, name, kind=None, path=None, port=None, resource_group_name=None, logic_app_name=None, yes=False):
    del cmd
    if all(value is None for value in (kind, path, port, resource_group_name, logic_app_name)):
        raise RequiredArgumentMissingError("Supply at least one target field to update.")
    context, original = get_context(name)
    data = copy.deepcopy(original)
    updated = data["contexts"][name]
    updated["target"] = _updated_target(context["target"], kind, path, port, resource_group_name, logic_app_name)
    _validate_store(data)
    changed = not json_equal(data, original)
    if changed and original["active"] == name:
        user_confirmation(
            "Update active Logic Apps context '{}'? Future commands will use {}.".format(
                name, json.dumps({field: updated["target"][field] for field in TARGET_FIELDS}, sort_keys=True)),
            yes=yes)
    save_store(data, expected=original)
    result = context_result(updated, data)
    result["action"] = "updated" if changed else "unchanged"
    return result


def delete_context(cmd, name, yes=False):
    del cmd
    context, original = get_context(name)
    was_active = original["active"] == name
    user_confirmation(
        "Delete saved Logic Apps context '{}' only? No project or Azure resource is deleted.{}".format(
            name, " The active selection will be cleared; no replacement will be chosen." if was_active else ""),
        yes=yes)
    data = copy.deepcopy(original)
    del data["contexts"][name]
    if was_active:
        data["active"] = None
    save_store(data, expected=original)
    result = context_result(context, original)
    result.update({"action": "deleted", "active": False, "wasActive": was_active, "activeContext": data["active"]})
    return result


def context_show_table_format(result):
    target = result["target"]
    return OrderedDict((key, value) for key, value in (
        ("Name", result["name"]), ("Active", result["active"]), ("Kind", target["kind"]),
        ("Path", target["path"]), ("Port", target["port"]),
        ("ResourceGroup", target["resourceGroup"]), ("LogicAppName", target["logicAppName"])))


def context_list_table_format(result):
    return [context_show_table_format(item) for item in result]
