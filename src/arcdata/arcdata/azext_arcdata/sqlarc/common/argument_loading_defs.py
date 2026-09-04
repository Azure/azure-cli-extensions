# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.sqlarc.common.argument_dicts import (
    backups_default_policy,
    backups_diff_backup_hours,
    backups_full_backup_days,
    backups_retention_days,
    backups_tlog_backup_mins,
    yes
)

# Place reusable argument loading functions here


def arguments(arg_context, argument_list):
    for argument in argument_list:
        arg_context.argument(**argument)


# Custom Schedule TODO: Renable parameters for custom
def load_backups_policy_set_arguments(arg_context):
    arguments(
        arg_context,
        [
            backups_full_backup_days,
            backups_diff_backup_hours,
            backups_tlog_backup_mins,
            backups_default_policy,
            backups_retention_days,
        ],
    )


def load_confirmation_argument(arg_context):
    arguments(
        arg_context,
        [yes],
    )
