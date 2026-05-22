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


def _generate_user_hash(cmd):
    """Generate a one-way pseudonymous identifier for the current caller.

    Combines subscription_id + user principal with a static salt, then
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


def _track_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, subscription_id, result_json, context=None):  # pylint: disable=unused-argument
    properties = _build_base_properties(command_name, status, message, error_message, error_stack_trace, duration, context)
    properties['Context.Default.AzureCLI.VmRepairParameters'] = json.dumps(parameters)
    properties['Context.Default.AzureCLI.VmRepairResultJson'] = json.dumps(result_json)
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)


def _track_run_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, subscription_id, result_json, script_run_id, script_status, script_output, script_duration, context=None):  # pylint: disable=unused-argument
    properties = _build_base_properties(command_name, status, message, error_message, error_stack_trace, duration, context)
    properties['Context.Default.AzureCLI.VmRepairParameters'] = json.dumps(parameters)
    properties['Context.Default.AzureCLI.VmRepairResultJson'] = json.dumps(result_json)
    properties['Context.Default.AzureCLI.VmRepairScriptRunId'] = script_run_id
    properties['Context.Default.AzureCLI.VmRepairScriptStatus'] = script_status
    properties['Context.Default.AzureCLI.VmRepairScriptOutput'] = _scrub_pii(script_output)
    properties['Context.Default.AzureCLI.VmRepairScriptDuration'] = script_duration
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)


def _track_command_telemetry_repair_and_restore(logger, command_name, status, message, error_message, error_stack_trace, duration, subscription_id, context=None):  # pylint: disable=unused-argument
    properties = _build_base_properties(command_name, status, message, error_message, error_stack_trace, duration, context)
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)
