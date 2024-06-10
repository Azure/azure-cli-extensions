# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import re
from knack.log import get_logger
from datetime import ( datetime, timezone )
import shutil
from azure.cli.core.azclierror import InvalidArgumentValueError
from ._constants import ERROR_MESSAGE_INVALID_TIMESPAN, TMP_DRY_RUN_FILE_NAME

logger = get_logger(__name__)
def convert_timespan_to_cron(cadence, date_time=None):
    # Regex to look for pattern 1d, 2d, 3d, etc.
    match = re.match(r'(\d+)([d])', cadence)
    value = int(match.group(1))
    unit = match.group(2)

    if(date_time is None):
        date_time = datetime.now(timezone.utc)

    cron_hour = date_time.hour
    cron_minute = date_time.minute

    if unit == 'd': #day of the month
        if value > 30:
            raise InvalidArgumentValueError(error_msg= ERROR_MESSAGE_INVALID_TIMESPAN)
        cron_expression = f'{cron_minute} {cron_hour} */{value} * *'
    
    return cron_expression

def transform_cron_to_cadence(cron_expression):
    parts = cron_expression.split()
    # The third part of the cron expression
    third_part = parts[2]
    
    match = re.search(r'\*/(\d+)', third_part)
    
    if match:
        return match.group(1) + 'd'
    else:
        return None
    
def create_temporary_dry_run_file(file_location):
    templates_path = os.path.dirname(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
                "../templates/"))
    logger.debug("templates_path:  %s", templates_path)
    file_folder = os.path.dirname(file_location)
    file_2_copy=templates_path+"/"+TMP_DRY_RUN_FILE_NAME
    shutil.copy2(file_2_copy, file_folder)
    folder_contents = os.listdir(file_folder)
    logger.debug("Copied dry run file %s", folder_contents)

def delete_temporary_dry_run_file(file_location):
    logger.debug("Deleting dry run file %s", file_location)
    os.remove(file_location+"/"+TMP_DRY_RUN_FILE_NAME)