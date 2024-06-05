# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
from azure.cli.core.azclierror import AzCLIError
from .helper._constants import (
    CONTINUOUSPATCH_CONFIG_SCHEMA_V1,
    CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT,
    CONTINUOSPATCH_ALL_TASK_NAMES,
    ERROR_MESSAGE_INVALID_TIMESPAN
)
from ._client_factory import cf_acr_tasks

from azure.mgmt.core.tools import (
    parse_resource_id
)

#wrapper to allow the distinct validation functions to be called from the same place
def validate_continuouspatch_config_v1(config_path):
    _validate_continuouspatch_file(config_path)
    _validate_continuouspatch_json(config_path)

#validate the file itself, that we can read it, the size, anything that might indicate that it is malicous
def _validate_continuouspatch_file(config_path):
    if not os.path.exists(config_path):
        raise AzCLIError(f"File {config_path} does not exist")
    if not os.path.isfile(config_path):
        raise AzCLIError(f"{config_path} is not a file")
    if os.path.getsize(config_path) > CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT:
        raise AzCLIError(f"{config_path} is too large, max size is 10MB")
    if os.path.getsize(config_path) == 0:
        raise AzCLIError(f"{config_path} is empty")
    if not os.access(config_path, os.R_OK):
        raise AzCLIError(f"{config_path} is not readable")

#validate the json structure of the file
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

def check_continuoustask_exists(cmd, registry):
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
        # the GET call will throw an exception if the task does not exist
        return False

    if task is not None:
        return True
    return False

def validate_and_convert_timespan_to_cron(timespan, date_time=None, do_not_run_immediately=True):
    import re
    from datetime import (
        datetime,
        timezone
    )

    # Extract the numeric value and unit from the timespan expression
    match = re.match(r'(\d+)([d])', timespan)
    if not match:
        raise ValueError('Invalid timespan expression')

    value = int(match.group(1))
    unit = match.group(2)

    # get current hour and minute and use that as the minute for the cron expression
    if(date_time is None):
        date_time = datetime.now(timezone.utc)

    offset_minute = 2
    cron_hour = date_time.hour
    cron_minute = date_time.minute

    if do_not_run_immediately:
        difference_minute = date_time.minute - offset_minute
        cron_minute = difference_minute + 60 if difference_minute < 0 else difference_minute
        cron_hour = cron_hour - 1 if difference_minute < 0 else cron_hour
    else:
        over_minute = date_time.minute + offset_minute
        cron_minute = over_minute - 60 if over_minute > 60 else over_minute
        cron_hour = cron_hour + 1 if over_minute > 60 else cron_hour

    # Adjust the cron expression based on the numeric value
    if unit == 'd': #day of the month
        if value > 30:
            raise ValueError(ERROR_MESSAGE_INVALID_TIMESPAN)
        cron_expression = f'{cron_minute} {cron_hour} */{value} * *'
    # elif unit == 'w': #day of the week
    #     if value > 6:
    #         raise ValueError(ERROR_MESSAGE_INVALID_TIMESPAN)
    #     cron_expression = f'{cron_minute} {cron_hour} * * {value}'
    # elif unit == 'M': #month of the year
    #     if value > 12:
    #         raise ValueError(ERROR_MESSAGE_INVALID_TIMESPAN)
    #     cron_expression = f'{cron_minute} {cron_hour} 1 */{value} *'

    return cron_expression
