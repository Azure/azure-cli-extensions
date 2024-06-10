# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
import re
from datetime import ( datetime, timezone )
from .helper._constants import CONTINUOUSPATCH_CONFIG_SCHEMA_V1, CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT, CONTINUOSPATCH_ALL_TASK_NAMES, ERROR_MESSAGE_INVALID_TIMESPAN
from .helper._constants import CSSCTaskTypes, ERROR_MESSAGE_INVALID_TASK, RECOMMENDATION_CADENCE
from azure.mgmt.core.tools import ( parse_resource_id )
from azure.cli.core.azclierror import InvalidArgumentValueError, AzCLIError
from ._client_factory import cf_acr_tasks

def validate_continuouspatch_config_v1(config_path):
    _validate_continuouspatch_file(config_path)
    _validate_continuouspatch_json(config_path)

def _validate_continuouspatch_file(config_path):
    if not os.path.exists(config_path):
        raise InvalidArgumentValueError(f"Config path file: {config_path} does not exist in the path specified")
    if not os.path.isfile(config_path):
        raise InvalidArgumentValueError(f"Config path file: {config_path} is not a valid file")
    if os.path.getsize(config_path) > CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT:
        raise InvalidArgumentValueError(f"Config path file: {config_path} is too large. Max size limit is 10 MB")
    if os.path.getsize(config_path) == 0:
        raise InvalidArgumentValueError(f"Config path file: {config_path} is empty")
    if not os.access(config_path, os.R_OK):
        raise InvalidArgumentValueError(f"Config path file: '{config_path}' is not readable")

def _validate_continuouspatch_json(config_path):
    from jsonschema import validate
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            validate(config, CONTINUOUSPATCH_CONFIG_SCHEMA_V1)
    except Exception as e:
        raise AzCLIError(f"Error validating the continuous patch config file: {e}")
    finally:
        f.close()

def check_continuous_task_exists(cmd, registry):
    exists = False
    for task_name in CONTINUOSPATCH_ALL_TASK_NAMES:
        exists = exists or _check_task_exists(cmd, registry, task_name)
    return exists

def _check_task_exists(cmd, registry, task_name = ""):
    acrtask_client = cf_acr_tasks(cmd.cli_ctx)
    resourceid = parse_resource_id(registry.id)
    resource_group = resourceid["resource_group"]

    try:
        task = acrtask_client.get(resource_group, registry.name, task_name)
    except:
        return False

    if task is not None:
        return True
    return False

def _validate_cadence(cadence, allow_null=False):
    # during update, cadence can be null if we are only updating the config
    if allow_null and cadence is None:
        return
    # Extract the numeric value and unit from the timespan expression
    match = re.match(r'(\d+)([d])', cadence)
    if not match:
        raise InvalidArgumentValueError(error_msg= ERROR_MESSAGE_INVALID_TIMESPAN)
    if(match is not None):
        value = int(match.group(1))
        unit = match.group(2)
    if unit == 'd' and value > 30: #day of the month
        raise InvalidArgumentValueError(error_msg= ERROR_MESSAGE_INVALID_TIMESPAN)

# def validate_and_convert_timespan_to_cron(timespan, date_time=None, do_not_run_immediately=True):

#     # Regex to look for pattern 1d, 2d, 3d, etc.
#     match = re.match(r'(\d+)([d])', timespan)
#     value = int(match.group(1))
#     unit = match.group(2)

#     if(date_time is None):
#         date_time = datetime.now(timezone.utc)

#     cron_hour = date_time.hour
#     cron_minute = date_time.minute

#     # commenting below logic to set offset, as we are manually triggerring the task in case it needs to be run immediately
#     # offset_minute = 2
#     # if do_not_run_immediately:
#     #     difference_minute = date_time.minute - offset_minute
#     #     cron_minute = difference_minute + 60 if difference_minute < 0 else difference_minute
#     #     cron_hour = cron_hour - 1 if difference_minute < 0 else cron_hour
#     # else:
#     #     over_minute = date_time.minute + offset_minute
#     #     cron_minute = over_minute - 60 if over_minute > 60 else over_minute
#     #     cron_hour = cron_hour + 1 if over_minute > 60 else cron_hour

#     if unit == 'd': #day of the month
#         if value > 30:
#             raise InvalidArgumentValueError(error_msg= ERROR_MESSAGE_INVALID_TIMESPAN)
#         cron_expression = f'{cron_minute} {cron_hour} */{value} * *'
    
#     return cron_expression

def validate_inputs(cadence, allow_null_cadence=False):
    _validate_cadence(cadence, allow_null_cadence)

def validate_task_type(task_type):
    if task_type in CSSCTaskTypes._value2member_map_:
        if (task_type != CSSCTaskTypes.ContinuousPatchV1.value):
            raise InvalidArgumentValueError(error_msg= ERROR_MESSAGE_INVALID_TASK)

def validate_cssc_update_input(cssc_config_path, cadence):
    if(cssc_config_path is None and cadence is None):
        raise InvalidArgumentValueError(error_msg = "Provide atleast one parameter to update: Cadence or Configuration file path")
    if(cadence is not None):
        _validate_cadence(cadence)
