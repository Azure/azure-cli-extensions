# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

# Put any arguments dicts that are exclusively for SQL Arc Database here,
# if the argument can be reused for other SQL Arc commands put it in
# Common/argument_dicts instead of here
import datetime
from azext_arcdata.sqlarc.common.argument_loading_defs import (
    name
)


def getNameArg(name_help_override=None):
    namedatabase = name
    namedatabase["help"] = "Name of the SQL database"
    if name_help_override:
        namedatabase["help"] = name_help_override
    return namedatabase


server = {
    "argument_dest": "server",
    "options_list": ["--server", "-s"],
    "help": "Name of the Arc-enabled SQL Server instance.",
    "required": True,
}
dest_name = {
    "argument_dest": "dest_name",
    "options_list": ["--dest-name "],
    "help": "Name of the database that will be created as the restore destination. ",
    "required": True,
}
time = {
    "argument_dest": "time",
    "options_list": ["--time", "-t"],
    "help": (
        "The point in time of the source database that will be restored to "
        "create the new database. Must be more recent than or equal to the "
        "source database's earliest restore date/time value. Time should be "
        "in following format: YYYY-MM-DDTHH:MM:SSZ . The given time value "
        "must be in UTC. If no time is provided, the most recent backup "
        "will be restored. The given time value must be in UTC."
    ),
}
dry_run = {
    "argument_dest": "dry_run",
    "options_list": ["--dry-run"],
    "help": (
        "Validates if the restore operation can be successful or not by "
        "returning earliest and latest restore time window. "
    ),
    "action": "store_true",
}
no_wait = {
    "argument_dest": "no_wait",
    "options_list": ["--no-wait"],
    "help": "Enabling this will make it so the command does not wait for completion",
    "action": "store_true",
}
