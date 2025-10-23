# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from typing import List


def getFeatureNameArgument(featurename_required_override=None):
    """
    Returns feature name argument.
    If featurename_required_override is not None, it will override the required value in the featureName dict.
    Default value of required is True.
    """
    featureName = feature_name
    featureName["required"] = True
    if featurename_required_override is not None:
        featureName["required"] = featurename_required_override
    return featureName


def getNameArgument(name_help_override=None):
    """
    Returns name argument.
    If name_help_override is not None, it will override the help value in the name dict.
    """
    nameArg = name
    if name_help_override is not None:
        nameArg["help"] = name_help_override
    return nameArg


def getResourceGroupArgument(rg_help_override=None):
    """
    Returns resource group argument.
    If rg_help_override is not None, it will override the help value in the resource group dict.
    """
    rgArg = resource_group
    if rg_help_override is not None:
        rgArg["help"] = rg_help_override
    return rgArg


def get_machine_name_argument(machineName_required_override=None):
    """
    Returns machine name argument.
    If machineName_required_override is not None, it will override the required value in the machine name dict.
    """
    machineName = machine_name
    machineName["required"] = True
    if machineName_required_override is not None:
        machineName["required"] = machineName_required_override
    return machineName


def parse_skip_instances(value: str) -> List[str]:
    """
    Parses the input of skip-instances parameter.
    """
    return value.split(",")


# These are Reusable argument dicts for all Sqlarc command groups, if the argument you are adding can not be used by 2 or more command groups do not add them here
name = {
    "argument_dest": "name",
    "options_list": ["--name", "-n"],
    "required": True,
    # Must add the help for this argument in the def that loads it as it is different in almost every context
}
resource_group = {
    "argument_dest": "resource_group",
    "options_list": ["--resource-group", "-g"],
    "help": "Name of the resource group where the Arc-enabled SQL Server instance is located.",
    "required": True,
}
yes = {
    "argument_dest": "yes",
    "options_list": ["--yes", "-y"],
    "help": "Do not prompt for confirmation.",
    "default": False,
    "action": "store_true",
}
backups_full_backup_days = {
    "argument_dest": "backups_full_backup_days",
    "options_list": ["--full-backup-days"],
    "help": "Interval, in days, at which a new full backup should be performed. Valid values – 0-7.",
    "type": int,
}
backups_diff_backup_hours = {
    "argument_dest": "backups_diff_backup_hours",
    "options_list": ["--diff-backup-hours"],
    "help": "Interval, in hours, at which differential backups should be performed. Valid values – 12 or 24.",
    "type": int,
}
backups_tlog_backup_mins = {
    "argument_dest": "backups_tlog_backup_mins",
    "options_list": ["--tlog-backup-mins"],
    "help": "Interval, in minutes, at which transactional backups should be performed. Valid values – 0 to 60.",
    "type": int,
}
backups_default_policy = {
    "argument_dest": "backups_default_policy",
    "options_list": ["--default-policy"],
    "help": "Set the default policy of weekly retention period, weekly full, daily differential, and 5 min transaction log backups.",
    "default": False,
    "action": "store_true",
}
backups_retention_days = {
    "argument_dest": "backups_retention_days",
    "options_list": ["--retention-days"],
    "help": "Number of days to keep the backups for. Valid values 0-35.",
    "type": int,
}
feature_name = {
    "argument_dest": "name",
    "options_list": ["--name", "-n"],
    "help": "Name of the feature.",
}
feature_flag_value = {
    "argument_dest": "enable",
    "options_list": ["--enable"],
    "help": "Set true to enable and false to disable.",
    "required": True,
}
machine_name = {
    "argument_dest": "machine_name",
    "options_list": ["--machine-name", "-m"],
    "help": "Name of the connected machine.",
    "required": True,
}
sql_server_arc_name = {
    "argument_dest": "sql_server_arc_name",
    "options_list": ["--sql-server-arc-name"],
    "help": "Name of the sql server instance.",
}
skip_instances = {
    "argument_dest": "skip_instances",
    "options_list": ["--skip-instances"],
    "type": parse_skip_instances,
    "help": "Comma separated string of instances that are excluded from arc onboarding operations.",
}
esu_enabled = {
    "argument_dest": "esu_enabled",
    "options_list": ["--esu-enabled"],
    "help": "Status of extended security updates.",
}
license_type = {
    "argument_dest": "license_type",
    "options_list": ["--license-type"],
    "help": "License type of the arc server.",
}
