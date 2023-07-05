# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, import-error, broad-except
import json
from applicationinsights import TelemetryClient
from .repair_utils import _get_current_vmrepair_version

# For test releases and testing
TEST_KEY = 'a6bdff92-33b5-426f-9123-33875d0ae98b'
PROD_KEY = '3e7130f2-759b-41d4-afb8-f1405d1d7ed9'

tc = TelemetryClient(PROD_KEY)
tc.context.application.ver = _get_current_vmrepair_version()


def _track_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, subscription_id, result_json):
    try:
        properties = {
            'command_name': command_name,
            'parameters': json.dumps(parameters),
            'command_status': status,
            'message': message,
            'error_message': error_message,
            'error_stack_trace': error_stack_trace,
            'subscription_id': subscription_id,
            'result_json': json.dumps(result_json)
        }
        measurements = {'command_duration': duration}
        tc.track_event(command_name, properties, measurements)
        tc.flush()
    except Exception as exception:
        logger.error('Unexpected error sending telemetry with exception: %s', str(exception))


def _track_run_command_telemetry(logger, command_name, parameters, status, message, error_message, error_stack_trace, duration, subscription_id, result_json, script_run_id, script_status, script_output, script_duration):
    try:
        properties = {
            'command_name': command_name,
            'parameters': json.dumps(parameters),
            'command_status': status,
            'message': message,
            'error_message': error_message,
            'error_stack_trace': error_stack_trace,
            'subscription_id': subscription_id,
            'result_json': json.dumps(result_json),
            'script_run_id': script_run_id,
            'script_status': script_status,
            'script_output': script_output
        }
        measurements = {'command_duration': duration, 'script_duration': script_duration}
        tc.track_event(command_name, properties, measurements)
        tc.flush()
    except Exception as exception:
        logger.error('Unexpected error sending telemetry with exception: %s', str(exception))
