# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught
import json
import os
import re
from knack.log import get_logger
from .helper._constants import (CONTINUOUSPATCH_CONFIG_SCHEMA_V1, CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT,
                                CONTINUOSPATCH_ALL_TASK_NAMES, ERROR_MESSAGE_INVALID_TIMESPAN, RESOURCE_GROUP)
from .helper._constants import CSSCTaskTypes, ERROR_MESSAGE_INVALID_TASK, RECOMMENDATION_CADENCE
from azure.mgmt.core.tools import (parse_resource_id)
from azure.cli.core.azclierror import InvalidArgumentValueError
from ._client_factory import cf_acr_tasks
logger = get_logger(__name__)


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
        logger.debug("Error validating the continuous patch config file: %s", e)
        raise InvalidArgumentValueError("File used for --config is not a valid config JSON file. Use --help to see the schema of the config file.")
    finally:
        f.close()


def check_continuous_task_exists(cmd, registry):
    exists = False
    for task_name in CONTINUOSPATCH_ALL_TASK_NAMES:
        exists = exists or _check_task_exists(cmd, registry, task_name)
    return exists


def _check_task_exists(cmd, registry, task_name=""):
    acrtask_client = cf_acr_tasks(cmd.cli_ctx)
    resourceid = parse_resource_id(registry.id)
    resource_group = resourceid[RESOURCE_GROUP]

    try:
        task = acrtask_client.get(resource_group, registry.name, task_name)
    except Exception as exception:
        logger.debug("Failed to find task %s from registry %s : %s", task_name, registry.name, exception)
        return False

    if task is not None:
        return True
    return False


def _validate_cadence(cadence):
    # during update, cadence can be null if we are only updating the config
    if cadence is None:
        return
    # Extract the numeric value and unit from the timespan expression
    match = re.match(r'(\d+)(d)$', cadence)
    if not match:
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN, recommendation=RECOMMENDATION_CADENCE)
    if match is not None:
        value = int(match.group(1))
        unit = match.group(2)
    if unit == 'd' and value > 30:  # day of the month
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN, recommendation=RECOMMENDATION_CADENCE)


def validate_inputs(cadence, config_file_path=None):
    _validate_cadence(cadence)
    if config_file_path is not None:
        validate_continuouspatch_config_v1(config_file_path)


def validate_task_type(task_type):
    if (task_type not in [item.value for item in CSSCTaskTypes]):
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TASK)


def validate_cssc_optional_inputs(cssc_config_path, cadence):
    if cssc_config_path is None and cadence is None:
        raise InvalidArgumentValueError(error_msg="Provide at least one parameter to update: --cadence or --config")
