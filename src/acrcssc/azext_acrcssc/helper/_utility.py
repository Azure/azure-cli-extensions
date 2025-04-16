# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import re
from knack.log import get_logger
from datetime import (datetime, timezone)
import shutil
from azure.cli.core.azclierror import AzCLIError, InvalidArgumentValueError, ResourceNotFoundError
from azure.mgmt.core.tools import parse_resource_id
from ._constants import (
    CONTINUOUSPATCH_SCHEDULE_MIN_DAYS,
    CONTINUOUSPATCH_SCHEDULE_MAX_DAYS,
    ERROR_MESSAGE_INVALID_TIMESPAN_VALUE,
    RESOURCE_GROUP,
    TMP_DRY_RUN_FILE_NAME,
    RECOMMENDATION_SCHEDULE)
from .._client_factory import cf_acr_tasks

logger = get_logger(__name__)
# pylint: disable=logging-fstring-interpolation


def convert_timespan_to_cron(schedule, date_time=None):
    # Regex to look for pattern 1d, 2d, 3d, etc.
    match = re.match(r'(\d+)(d)$', schedule)
    if match is None:
        raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN_VALUE,
                                        recommendation=RECOMMENDATION_SCHEDULE)

    value = int(match.group(1))
    unit = match.group(2)

    if date_time is None:
        date_time = datetime.now(timezone.utc)

    cron_hour = date_time.hour
    cron_minute = date_time.minute
    cron_expression = ""

    if unit == 'd':  # day of the month
        if value < CONTINUOUSPATCH_SCHEDULE_MIN_DAYS or value > CONTINUOUSPATCH_SCHEDULE_MAX_DAYS:
            raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN_VALUE,
                                            recommendation=RECOMMENDATION_SCHEDULE)
        cron_expression = f'{cron_minute} {cron_hour} */{value} * *'

    return cron_expression


def convert_cron_to_schedule(cron_expression, just_days=False):
    try:
        parts = cron_expression.split()
        # The third part of the cron expression for 'day of the month'
        third_part = parts[2]

        match = re.search(r'^\*/(\d+)$', third_part)

        if match:
            if just_days:
                return match.group(1)
            return match.group(1) + 'd'

        return None
    except IndexError:
        return None


def create_temporary_dry_run_file(file_location, tmp_folder):
    templates_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "../templates"))
    logger.debug(f"templates_path: {templates_path}")

    try:
        os.makedirs(tmp_folder, exist_ok=True)
        file_template_copy = os.path.join(templates_path, TMP_DRY_RUN_FILE_NAME)

        if not os.path.exists(file_template_copy):
            raise AzCLIError(f"Template file {file_template_copy} does not exist")

        shutil.copy2(file_template_copy, tmp_folder)
        shutil.copy2(file_location, tmp_folder)
        folder_contents = os.listdir(tmp_folder)
        logger.debug(f"Copied dry run file {folder_contents}")
    except Exception as exception:
        raise AzCLIError(f"Failed to copy dry run file: {exception}")


def delete_temporary_dry_run_file(tmp_folder):
    if tmp_folder is None or not os.path.exists(tmp_folder):
        return
    logger.debug(f"Deleting contents and directory {tmp_folder}")
    shutil.rmtree(tmp_folder)


def get_task(cmd, registry, task_name, task_client=None):
    if task_client is None:
        task_client = cf_acr_tasks(cmd.cli_ctx)

    resourceid = parse_resource_id(registry.id)
    resource_group = resourceid[RESOURCE_GROUP]

    try:
        return task_client.get(resource_group, registry.name, task_name)
    except ResourceNotFoundError as exception:
        logger.debug("Failed to find task %s from registry %s : %s", task_name, registry.name, exception)
        return None
