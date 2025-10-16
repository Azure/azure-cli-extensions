# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import pydash as _
import regex as re
from azext_arcdata.core.exceptions import CLIError
from datetime import datetime, timezone, timedelta
from knack.log import get_logger

logger = get_logger(__name__)


def validate_database_name(database_name):
    # Define the regular expression pattern
    pattern = (
        r"^(?!.*--)(?!.*__$)[\p{L}\p{N}][\p{L}\p{N}_-]{0,126}[\p{L}\p{N}]$"
    )
    regex = re.compile(pattern)

    if regex.match(database_name):
        pass
    else:
        raise CLIError(
            'The database name "{0}" is invalid. We support the regular identifiers found at https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers?view=sql-server-ver16#rules-for-regular-identifiers with the exclusion of the following characters[@,#,$]'.format(
                database_name
            )
        )


def validate_restore_arguments(namespace):
    validate_database_name(namespace.dest_name)
    partially_validate_time(namespace.time)


# We do not have the Restore Window, but we can check that the date is not in the future which is 1 of the 2 bounds for the restore window. And we can check it is in the correct format.
def partially_validate_time(given_time):
    if given_time is None:
        return
    current_time = datetime.now(timezone.utc)
    try:
        time_format = "%Y-%m-%dT%H:%M:%SZ"
        given_time = datetime.strptime(given_time, time_format)
    except Exception:
        raise CLIError(
            "The given time '{0}' does not follow the following format 'YYYY-MM-DDTHH:MM:SSZ'".format(
                given_time
            )
        )

    # Specify the desired timezone as an offset
    desired_timezone = timezone(timedelta(hours=0))

    # Add the timezone information to the datetime object
    given_time = given_time.replace(tzinfo=desired_timezone)

    if given_time is not None and given_time > current_time:
        raise CLIError(
            "The selected time is invalid as it is currently set for the future. Given time: '{0}' Current time: '{1}'".format(
                given_time, current_time
            )
        )


def validate_time(backup_information, given_time):
    if (
        backup_information is None
        or backup_information.last_full_backup is None
    ):
        raise ValueError("There are no backups available for this database.")
    if given_time is None:
        return
    last_full_backup_time = backup_information.last_full_backup
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    desired_timezone = timezone(timedelta(hours=0))
    given_time = datetime.strptime(given_time, time_format).replace(
        tzinfo=desired_timezone
    )
    if given_time < last_full_backup_time:
        raise ValueError(
            "The selected time is invalid as it is prior to the Last Full Backup. Given time: '{0}' Last Full Backup time: '{1}'".format(
                given_time, last_full_backup_time
            )
        )


def validate_backups_are_active(
    instance_backups_policy, database_backups_policy
):
    if instance_backups_policy is None and database_backups_policy is None:
        raise ValueError(
            "There is no backups policy currently set for this SQL database or SQL Server instance."
        )
    elif database_backups_policy is None and instance_backups_policy is not None:
        if instance_backups_policy.retention_period_days == 0:
            raise ValueError(
                "The backups policy for this database is currently disabled by the SQL Server instance's backup policy."
            )
    elif database_backups_policy is not None:
        if database_backups_policy.retention_period_days == 0:
            raise ValueError(
                "The backups policy is currently disabled on this SQL database."
            )
