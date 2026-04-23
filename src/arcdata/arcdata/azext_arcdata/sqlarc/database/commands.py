# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.sqlarc.common.validators import validate_backups_policy_set_arguments
from azext_arcdata.sqlarc.database.validators import validate_restore_arguments
from azext_arcdata.sqlarc.database.client import beget
from azure.cli.core.commands import CliCommandType


def load_commands(self, _):
    operations = CliCommandType(
        operations_tmpl="azext_arcdata.sqlarc.database.custom#{}"
    )
    # ------------Backup Policy Commands----------------
    with self.command_group(
        "sql db-arc backups-policy",
        operations,
        client_factory=beget,
        is_preview=True,
    ) as g:
        g.command(
            "set",
            "db_backups_policy_set",
            validator=validate_backups_policy_set_arguments,
        )
        g.show_command("show", "db_backups_policy_show")
        g.command("delete", "db_backups_policy_delete")

    # ------------Restore Commands----------------
    with self.command_group(
        "sql db-arc",
        operations,
        client_factory=beget,
        is_preview=True,
    ) as g:
        g.command("restore", "db_restore", validator=validate_restore_arguments)
