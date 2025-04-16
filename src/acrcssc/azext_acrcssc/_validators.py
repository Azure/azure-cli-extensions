# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught
# pylint: disable=logging-fstring-interpolation
import os
import re
from knack.log import get_logger
from azure.cli.command_modules.acr.repository import acr_repository_show
from .helper._constants import (
    BEARER_TOKEN_USERNAME,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    CONTINUOUSPATCH_IMAGE_LIMIT,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT,
    CONTINUOUSPATCH_ALL_TASK_NAMES,
    ERROR_MESSAGE_INVALID_TIMESPAN_FORMAT,
    SUBSCRIPTION)
from .helper._constants import CSSCTaskTypes, ERROR_MESSAGE_INVALID_TASK
from .helper._ociartifactoperations import _get_acr_token, ContinuousPatchConfig
from azure.mgmt.core.tools import (parse_resource_id)
from azure.cli.core.azclierror import InvalidArgumentValueError
from ._client_factory import cf_acr_tasks
from .helper._utility import get_task, convert_timespan_to_cron

logger = get_logger(__name__)


def validate_continuouspatch_config_v1(config_path):
    _validate_continuouspatch_file(config_path)
    config = validate_continuouspatch_json(config_path)
    _validate_continuouspatch_config(config)


def _validate_continuouspatch_file(config_path):
    if not os.path.exists(config_path):
        raise InvalidArgumentValueError(f"Config path file: {config_path} does not exist in the path specified")
    if not os.path.isfile(config_path):
        raise InvalidArgumentValueError(f"Config path file: {config_path} is not a valid file")
    if os.path.getsize(config_path) > CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT:
        raise InvalidArgumentValueError(f"Config path file: {config_path} is too large. Max size limit is {CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT / (1024 * 1024)} MB")
    if os.path.getsize(config_path) == 0:
        raise InvalidArgumentValueError(f"Config path file: {config_path} is empty")
    if not os.access(config_path, os.R_OK):
        raise InvalidArgumentValueError(f"Config path file: '{config_path}' is not readable")


def validate_continuouspatch_json(config_path):
    config = ContinuousPatchConfig().from_file(file_path=config_path)
    if not config:
        raise InvalidArgumentValueError(f"Config path file: {config_path} is not a valid JSON file. Use --help to see the schema of the config file.")
    return config


def _validate_continuouspatch_config(config):
    if not isinstance(config, ContinuousPatchConfig):
        raise InvalidArgumentValueError("Config file is not a valid JSON file. Use --help to see the schema of the config file.")
    for repository in config.repositories:
        for tag in repository.tags:
            if re.match(r'.*-patched$', tag) or re.match(r'.*-[0-9]{1,3}$', tag):
                raise InvalidArgumentValueError(f"Configuration error: Repository '{repository.repository}' with tag '{tag}' is not allowed. Tags ending with '*-patched' (floating tag) or '*-0' to '*-999' (incremental tag) are reserved for internal use.")
            if tag == "*" and len(repository.tags) > 1:
                raise InvalidArgumentValueError("Configuration error: Tag '*' is not allowed with other tags in the same repository. Use '*' as the only tag in the repository to avoid overlaps.")


# to save on API calls, we use task_list to return a list of CSSC tasks found in the registry
def check_continuous_task_exists(cmd, registry):
    task_list = []
    missing_tasks = []

    acrtask_client = cf_acr_tasks(cmd.cli_ctx)
    for task_name in CONTINUOUSPATCH_ALL_TASK_NAMES:
        try:
            task = get_task(cmd, registry, task_name, acrtask_client)
            if task is None:
                missing_tasks.append(task_name)
            else:
                task_list.append(task)
        except Exception as exception:
            logger.debug(f"Failed to find tasks from registry {registry.name} : {exception}")
            missing_tasks.append(task_name)

    if missing_tasks:
        logger.debug(f"Failed to find tasks {', '.join(missing_tasks)} from registry {registry.name}")
        return False, task_list

    return True, task_list


def check_continuous_task_config_exists(cmd, registry):
    # A client cannot be used in this situation because the 'show registry/image'
    # is a data plane operation and the az cli does not include the data plane API.
    subscription = parse_resource_id(registry.id)[SUBSCRIPTION]
    try:
        token = _get_acr_token(registry.name, subscription)
        acr_repository_show(
            cmd=cmd,
            registry_name=registry.name,
            repository=f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}",
            username=BEARER_TOKEN_USERNAME,
            password=token)
    except Exception as exception:
        if hasattr(exception, 'status_code') and exception.status_code == 404:
            return False
        # report on the error only if we get something other than 404
        logger.error(f"Failed to find config {CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG} from registry {registry.name} : {exception}")
        raise
    return True


def _validate_schedule(schedule):
    # during update, schedule can be null if we are only updating the config
    if schedule is None:
        return
    # the convertion to cron will raise an error if the format is invalid
    cron = convert_timespan_to_cron(schedule)
    if not cron:
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN_FORMAT)


def validate_inputs(schedule, config_file_path=None, dryrun=False, run_immediately=False):
    _validate_schedule(schedule)
    if config_file_path:
        validate_continuouspatch_config_v1(config_file_path)
    validate_run_type(dryrun, run_immediately)


def validate_run_type(dryrun, run_immediately):
    if dryrun and run_immediately:
        raise InvalidArgumentValueError(error_msg="The --dryrun and --run-immediately options cannot be used together. Use one or the other.")


def validate_task_type(task_type):
    if (task_type not in [item.value for item in CSSCTaskTypes]):
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TASK % task_type)


def validate_cssc_optional_inputs(cssc_config_path, schedule):
    if cssc_config_path is None and schedule is None:
        raise InvalidArgumentValueError(error_msg="Provide at least one parameter to update: --schedule or --config")


def validate_continuous_patch_v1_image_limit(dryrun_log):
    match = re.search(r"Matches found: (\d+)", dryrun_log)
    if match is None:
        # the quick task did not return the expected output, we cannot validate the image limit but cannot block the operation
        logger.error("Failed to parse the image limit from the dry run log. Execution will continue.")
        logger.debug("Dry run log: %s", dryrun_log)
        return

    image_limit = int(match.group(1))

    if image_limit > CONTINUOUSPATCH_IMAGE_LIMIT:
        # these expressions remove all the Task related output from the log, and only leaves the listing of repositories and tags
        pattern_prefix = "Listing repositories and tags matching the filter"
        result = re.sub(r'^(.*\n)*?' + re.escape(pattern_prefix), pattern_prefix, dryrun_log, flags=re.MULTILINE)

        pattern_postfix = "Adjust the JSON filter to limit the number of images."
        result = re.sub(r'(?s)' + re.escape(pattern_postfix) + r'.*', pattern_postfix, result)

        raise InvalidArgumentValueError(error_msg=result)

    if image_limit == 0:
        # when no matching images are found, we should relay the information to the user
        # extract everything between and including the target lines
        match = re.search(r'No matching repository and tag found!.*?Matches found: 0', dryrun_log, re.DOTALL)
        if match:
            logger.warning(match.group())
