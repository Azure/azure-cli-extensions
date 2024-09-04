# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught
# pylint: disable=logging-fstring-interpolation
import json
import os
import re
from knack.log import get_logger
from azure.cli.command_modules.acr.repository import acr_repository_show
from .helper._constants import (
    BEARER_TOKEN_USERNAME,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOUSPATCH_CONFIG_SCHEMA_V1,
    CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT,
    CONTINUOUSPATCH_CONFIG_SUPPORTED_VERSIONS,
    CONTINUOSPATCH_ALL_TASK_NAMES,
    ERROR_MESSAGE_INVALID_TIMESPAN_FORMAT,
    ERROR_MESSAGE_INVALID_TIMESPAN_VALUE,
    RESOURCE_GROUP,
    SUBSCRIPTION)
from .helper._constants import CSSCTaskTypes, ERROR_MESSAGE_INVALID_TASK, RECOMMENDATION_SCHEDULE
from .helper._ociartifactoperations import _get_acr_token
from azure.mgmt.core.tools import (parse_resource_id)
from azure.cli.core.azclierror import InvalidArgumentValueError
from ._client_factory import cf_acr_tasks
logger = get_logger(__name__)


def validate_continuouspatch_config_v1(config_path):
    _validate_continuouspatch_file(config_path)
    config = _validate_continuouspatch_json(config_path)
    _validate_continuouspatch_config(config)


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
            return config
    except Exception as e:
        logger.debug(f"Error validating the continuous patch config file: {e}")
        raise InvalidArgumentValueError("File used for --config is not a valid config JSON file. Use --help to see the schema of the config file.")
    finally:
        f.close()


def _validate_continuouspatch_config(config):
    if not isinstance(config, dict):
        raise InvalidArgumentValueError("Config file is not a valid JSON file. Use --help to see the schema of the config file.")
    for repository in config.get("repositories", []):
        for tag in repository.get("tags", []):
            if re.match(r'.*-patched$', tag) or re.match(r'.*-[0-9]{1,3}$', tag):
                raise InvalidArgumentValueError(f"Configuration error: Repository {repository['repository']} Tag {tag} is not allowed. Tags ending with '*-patched' (floating tag) or '*-[0-9]\\{{1,3}}' (incremental tag) are reserved for internal use.")
            if tag == "*" and len(repository.get("tags", [])) > 1:
                raise InvalidArgumentValueError("Configuration error: Tag '*' is not allowed with other tags in the same repository. Use '*' as the only tag in the repository to avoid overlaps.")
    if config.get("version","") not in CONTINUOUSPATCH_CONFIG_SUPPORTED_VERSIONS:
        raise InvalidArgumentValueError(f"Configuration error: Version {config.get('version','')} is not supported. Supported versions are {CONTINUOUSPATCH_CONFIG_SUPPORTED_VERSIONS}")


def check_continuous_task_exists(cmd, registry):
    exists = False
    for task_name in CONTINUOSPATCH_ALL_TASK_NAMES:
        exists = exists or _check_task_exists(cmd, registry, task_name)
    return exists


def check_continuous_task_config_exists(cmd, registry):
    # A client cannot be used in this situation because the 'show registry/image'
    # is a data plane operation and the az cli does not include the data plane API.
    subscription = parse_resource_id(registry.id)[SUBSCRIPTION]
    try:
        token = _get_acr_token(registry.name, subscription)
        acr_repository_show(
            cmd=cmd,
            registry_name=registry.name,
            repository=f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG}",
            username=BEARER_TOKEN_USERNAME,
            password=token)
    except Exception as exception:
        if hasattr(exception, 'status_code') and exception.status_code == 404:
            return False
        # report on the error only if we get something other than 404
        logger.debug(f"Failed to find config {CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG} from registry {registry.name} : {exception}")
        raise
    return True


def _check_task_exists(cmd, registry, task_name=""):
    acrtask_client = cf_acr_tasks(cmd.cli_ctx)
    resourceid = parse_resource_id(registry.id)
    resource_group = resourceid[RESOURCE_GROUP]

    try:
        task = acrtask_client.get(resource_group, registry.name, task_name)
    except Exception as exception:
        logger.debug(f"Failed to find task {task_name} from registry {registry.name} : {exception}")
        return False

    if task is not None:
        return True
    return False


def _validate_schedule(schedule):
    # during update, schedule can be null if we are only updating the config
    if schedule is None:
        return
    # Extract the numeric value and unit from the timespan expression
    match = re.match(r'(\d+)(d)$', schedule)
    if not match:
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN_FORMAT, recommendation=RECOMMENDATION_SCHEDULE)
    if match is not None:
        value = int(match.group(1))
        unit = match.group(2)
    if unit == 'd' and (value < 1 or value > 30):  # day of the month
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN_VALUE, recommendation=RECOMMENDATION_SCHEDULE)


def validate_inputs(schedule, config_file_path=None):
    _validate_schedule(schedule)
    if config_file_path is not None:
        validate_continuouspatch_config_v1(config_file_path)


def validate_task_type(task_type):
    if (task_type not in [item.value for item in CSSCTaskTypes]):
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TASK)


def validate_cssc_optional_inputs(cssc_config_path, schedule):
    if cssc_config_path is None and schedule is None:
        raise InvalidArgumentValueError(error_msg="Provide at least one parameter to update: --schedule or --config")
