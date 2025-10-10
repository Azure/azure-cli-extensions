# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
from azext_arcdata.sqlarc.database.argument_dicts import *  # Note: this implicitly adds common argument_dicts

# These arguments should be neccessary for all commands in this file
def load_common_arc_database_arguments(
    arg_context, name_help_override="Name of the database."
):
    arguments(
        arg_context, [getNameArg(name_help_override), server, resource_group]
    )


def load_restore_arc_database_arguments(arg_context):
    arguments(arg_context, [dest_name, dry_run, time])


def load_arguments(self, _):
    from knack.arguments import ArgumentsContext

    # Disabled until GNU has been added to Arcee
    with ArgumentsContext(self, "sql db-arc restore") as arg_context:
        load_common_arc_database_arguments(
            arg_context,
            "Name of the source database from where the backups should be retrieved.",
        )
        load_restore_arc_database_arguments(arg_context)

    with ArgumentsContext(self, "sql db-arc backups-policy set") as arg_context:
        load_common_arc_database_arguments(arg_context)
        load_backups_policy_set_arguments(arg_context)

    with ArgumentsContext(
        self, "sql db-arc backups-policy delete"
    ) as arg_context:
        load_common_arc_database_arguments(arg_context)
        load_confirmation_argument(arg_context)

    with ArgumentsContext(
        self, "sql db-arc backups-policy show"
    ) as arg_context:
        load_common_arc_database_arguments(
            arg_context,
        )
