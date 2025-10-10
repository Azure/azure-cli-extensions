# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import pydash as _
from azext_arcdata.sqlarc.common.validators import *
from azext_arcdata.arm_sdk.swagger.swagger_latest.models import BackupPolicy

# Reads the Backup Policy and checks if it is enabled
def is_backups_enabled(arm_model):
    return arm_model.properties.backup_policy.retention_period_days == 0


# Resets all values to harcoded default values
def setup_default_values(arm_model):
    arm_model.properties.backup_policy.retention_period_days = 7
    arm_model.properties.backup_policy.full_backup_days = 7
    arm_model.properties.backup_policy.differential_backup_hours = 24
    arm_model.properties.backup_policy.transaction_log_backup_minutes = 5


# Takes a Backups policy and applies changes to it based on user input
def apply_policy_changes_to_backups_policy(cvo, arm_model):
    if cvo.backups_default_policy:
        setup_default_values(arm_model)

    if cvo.backups_full_backup_days != None:
        arm_model.properties.backup_policy.full_backup_days = (
            cvo.backups_full_backup_days
        )

    if cvo.backups_diff_backup_hours != None:
        arm_model.properties.backup_policy.differential_backup_hours = (
            cvo.backups_diff_backup_hours
        )

    if cvo.backups_tlog_backup_mins != None:
        arm_model.properties.backup_policy.transaction_log_backup_minutes = (
            cvo.backups_tlog_backup_mins
        )

    if cvo.backups_retention_days != None:
        arm_model.properties.backup_policy.retention_period_days = (
            cvo.backups_retention_days
        )


# Make a Displayable version of the backups policy, In essence it hides certain Null values from the user and any other information not intented to be for the user.
def displayable_backups_policy_config(
    arm_model, instance_name, database_name="", policy_level=""
):
    backups_policy_config = {}
    if database_name:
        backups_policy_config["databaseName"] = database_name
        backups_policy_config["backupPolicyLevel"] = policy_level

    backups_policy_config["instanceName"] = instance_name

    backups_policy_config[
        "retentionPeriodDays"
    ] = arm_model.properties.backup_policy.retention_period_days

    backups_policy_config[
        "fullBackupDays"
    ] = arm_model.properties.backup_policy.full_backup_days

    backups_policy_config[
        "differentialBackupHours"
    ] = arm_model.properties.backup_policy.differential_backup_hours

    backups_policy_config[
        "transactionLogBackupMinutes"
    ] = arm_model.properties.backup_policy.transaction_log_backup_minutes

    return backups_policy_config


def create_backups_policy_config(arm_model):
    arm_model.properties.backup_policy = BackupPolicy()
    setup_default_values(arm_model)


def delete_backups_policy_config(arm_model):
    arm_model.properties.backup_policy = None


# This function is not exposed to the user; it is can be used for quickly changing license types for manual testing reasons.
def delete_backups_policy(arm_model):
    arm_model.properties.backup_policy = None
