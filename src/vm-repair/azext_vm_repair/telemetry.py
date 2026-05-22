# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import hashlib
import json
import re

from azure.cli.core import telemetry as telemetry_core

EXTENSION_NAME = 'vm-repair'

# Patterns for scrubbing PII from error messages and stack traces
_EMAIL_RE = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
_HOME_DIR_RE = re.compile(r'(?:/home/|C:\\Users\\)[^\s/\\]+')


def _scrub_pii(value):
    """Remove emails and home directory usernames from a string."""
    if not isinstance(value, str) or not value:
        return value
    value = _EMAIL_RE.sub('[REDACTED_EMAIL]', value)
    value = _HOME_DIR_RE.sub('[REDACTED_PATH]', value)
    return value


def _hash_value(value):
    """One-way hash a single value, preserving type for non-strings."""
    if value is None or value == '':
        return value
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()[:16]


# Parameter keys whose values are Azure resource identifiers and should be
# hashed rather than sent in cleartext.  Keys not in this set are kept as-is
# (booleans, enums, flags, etc.).
_RESOURCE_ID_KEYS = frozenset([
    'vm_name', 'resource_group_name', 'subscription_id',
    'repair_vm_name', 'repair_group_name', 'copy_disk_name',
    'disk_name', 'repair_vm_id',
])


def _hash_resource_params(parameters):
    """Return a copy of *parameters* with resource identifiers hashed."""
    if not isinstance(parameters, dict):
        return parameters
    sanitized = {}
    for key, value in parameters.items():
        if key in _RESOURCE_ID_KEYS and value and value != '********':
            sanitized[key] = _hash_value(value)
        else:
            sanitized[key] = value
    return sanitized


def _hash_result_json(result_json):
    """Return a copy of *result_json* with known resource fields hashed."""
    if not isinstance(result_json, dict):
        return result_json
    _result_resource_keys = {
        'repair_vm_name', 'copied_disk_name', 'copied_disk_uri',
        'repair_resource_group', 'repair_vm_id',
    }
    sanitized = {}
    for key, value in result_json.items():
        if key in _result_resource_keys and isinstance(value, str) and value:
            sanitized[key] = _hash_value(value)
        else:
            sanitized[key] = value
    return sanitized


def _generate_user_hash(cmd):
    """Generate a one-way pseudonymous identifier for the current caller.

    Combines subscription_id + user principal with a namespace prefix, then
    SHA-256 hashes it.  The 16-hex-char result is deterministic (same
    user = same hash across sessions) but irreversible.
    """
    try:
        from azure.cli.core._profile import Profile
        profile = Profile(cli_ctx=cmd.cli_ctx)
        account = profile.get_subscription()
        user_identity = account.get('user', {}).get('name', '')
        sub_id = account.get('id', '')
    except Exception:  # pylint: disable=broad-except
        return 'unknown'
    raw = f"vmrepair:{sub_id}:{user_identity}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def _build_base_properties(command_name, status, message, error_message, error_stack_trace, duration, context=None):
    """Build the common property dict shared by all telemetry functions."""
    props = {
        'Context.Default.AzureCLI.VmRepairCommandName': command_name,
        'Context.Default.AzureCLI.VmRepairStatus': status,
        'Context.Default.AzureCLI.VmRepairMessage': _scrub_pii(message),
        'Context.Default.AzureCLI.VmRepairErrorMessage': _scrub_pii(error_message),
        'Context.Default.AzureCLI.VmRepairErrorStackTrace': _scrub_pii(error_stack_trace),
        'Context.Default.AzureCLI.VmRepairCommandDuration': duration
    }
    if context:
        for key, value in context.items():
            props[f'Context.Default.AzureCLI.VmRepair{key}'] = value
    return props


def _track_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, result_json, context=None):  # pylint: disable=unused-argument
    properties = _build_base_properties(command_name, status, message, error_message, error_stack_trace, duration, context)
    properties['Context.Default.AzureCLI.VmRepairParameters'] = json.dumps(_hash_resource_params(parameters))
    properties['Context.Default.AzureCLI.VmRepairResultJson'] = json.dumps(_hash_result_json(result_json))
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)


def _track_run_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, result_json, script_run_id, script_status, script_output, script_duration, context=None):  # pylint: disable=unused-argument
    properties = _build_base_properties(command_name, status, message, error_message, error_stack_trace, duration, context)
    properties['Context.Default.AzureCLI.VmRepairParameters'] = json.dumps(_hash_resource_params(parameters))
    properties['Context.Default.AzureCLI.VmRepairResultJson'] = json.dumps(_hash_result_json(result_json))
    properties['Context.Default.AzureCLI.VmRepairScriptRunId'] = script_run_id
    properties['Context.Default.AzureCLI.VmRepairScriptStatus'] = script_status
    properties['Context.Default.AzureCLI.VmRepairScriptOutput'] = _scrub_pii(script_output)
    properties['Context.Default.AzureCLI.VmRepairScriptDuration'] = script_duration
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)


def _track_command_telemetry_repair_and_restore(logger, command_name, status, message, error_message, error_stack_trace, duration, context=None):  # pylint: disable=unused-argument
    properties = _build_base_properties(command_name, status, message, error_message, error_stack_trace, duration, context)
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)
