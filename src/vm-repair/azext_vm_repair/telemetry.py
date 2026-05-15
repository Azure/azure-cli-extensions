# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
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


def _track_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, subscription_id, result_json):
    properties = {
        'Context.Default.AzureCLI.VmRepairCommandName': command_name,
        'Context.Default.AzureCLI.VmRepairParameters': json.dumps(parameters),
        'Context.Default.AzureCLI.VmRepairStatus': status,
        'Context.Default.AzureCLI.VmRepairMessage': _scrub_pii(message),
        'Context.Default.AzureCLI.VmRepairErrorMessage': _scrub_pii(error_message),
        'Context.Default.AzureCLI.VmRepairErrorStackTrace': _scrub_pii(error_stack_trace),
        'Context.Default.AzureCLI.VmRepairResultJson': json.dumps(result_json),
        'Context.Default.AzureCLI.VmRepairCommandDuration': duration
    }
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)


def _track_run_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, subscription_id, result_json, script_run_id, script_status, script_output, script_duration):
    properties = {
        'Context.Default.AzureCLI.VmRepairCommandName': command_name,
        'Context.Default.AzureCLI.VmRepairParameters': json.dumps(parameters),
        'Context.Default.AzureCLI.VmRepairStatus': status,
        'Context.Default.AzureCLI.VmRepairMessage': _scrub_pii(message),
        'Context.Default.AzureCLI.VmRepairErrorMessage': _scrub_pii(error_message),
        'Context.Default.AzureCLI.VmRepairErrorStackTrace': _scrub_pii(error_stack_trace),
        'Context.Default.AzureCLI.VmRepairResultJson': json.dumps(result_json),
        'Context.Default.AzureCLI.VmRepairScriptRunId': script_run_id,
        'Context.Default.AzureCLI.VmRepairScriptStatus': script_status,
        'Context.Default.AzureCLI.VmRepairScriptOutput': _scrub_pii(script_output),
        'Context.Default.AzureCLI.VmRepairCommandDuration': duration,
        'Context.Default.AzureCLI.VmRepairScriptDuration': script_duration
    }
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)


def _track_command_telemetry_repair_and_restore(logger, command_name, status, message, error_message, error_stack_trace, duration, subscription_id):
    properties = {
        'Context.Default.AzureCLI.VmRepairCommandName': command_name,
        'Context.Default.AzureCLI.VmRepairStatus': status,
        'Context.Default.AzureCLI.VmRepairMessage': _scrub_pii(message),
        'Context.Default.AzureCLI.VmRepairErrorMessage': _scrub_pii(error_message),
        'Context.Default.AzureCLI.VmRepairErrorStackTrace': _scrub_pii(error_stack_trace),
        'Context.Default.AzureCLI.VmRepairCommandDuration': duration
    }
    telemetry_core.add_extension_event(EXTENSION_NAME, properties)
