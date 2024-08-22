# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import re
from knack.log import get_logger
from datetime import (datetime, timezone)
import shutil
from azure.cli.core.azclierror import InvalidArgumentValueError
from ._constants import ERROR_MESSAGE_INVALID_TIMESPAN_VALUE, TMP_DRY_RUN_FILE_NAME

logger = get_logger(__name__)
# pylint: disable=logging-fstring-interpolation


def convert_timespan_to_cron(cadence, date_time=None):
    # Regex to look for pattern 1d, 2d, 3d, etc.
    match = re.match(r'(\d+)([d])', cadence)
    value = int(match.group(1))
    unit = match.group(2)

    if date_time is None:
        date_time = datetime.now(timezone.utc)

    cron_hour = date_time.hour
    cron_minute = date_time.minute

    if unit == 'd':  # day of the month
        if value < 1 or value > 30:
            raise InvalidArgumentValueError(error_msg=ERROR_MESSAGE_INVALID_TIMESPAN_VALUE)
        cron_expression = f'{cron_minute} {cron_hour} */{value} * *'

    return cron_expression


def transform_cron_to_cadence(cron_expression):
    parts = cron_expression.split()
    # The third part of the cron expression
    third_part = parts[2]

    match = re.search(r'\*/(\d+)', third_part)

    if match:
        return match.group(1) + 'd'
    return None


def create_temporary_dry_run_file(file_location, tmp_folder):
    templates_path = os.path.dirname(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            "../templates/"))
    logger.debug(f"templates_path:  {templates_path}")

    os.makedirs(tmp_folder, exist_ok=True)
    file_template_copy = templates_path + "/" + TMP_DRY_RUN_FILE_NAME

    shutil.copy2(file_template_copy, tmp_folder)
    shutil.copy2(file_location, tmp_folder)
    folder_contents = os.listdir(tmp_folder)
    logger.debug(f"Copied dry run file {folder_contents}")


def delete_temporary_dry_run_file(tmp_folder):
    logger.debug(f"Deleting contents and directory {tmp_folder}")
    shutil.rmtree(tmp_folder)
