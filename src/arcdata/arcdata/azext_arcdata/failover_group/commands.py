# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_arcdata.core.cli_client import beget
import azext_arcdata.failover_group.validators as validators


def load_commands(self, _):
    operations = CliCommandType(
        operations_tmpl="azext_arcdata.failover_group.custom#{}"
    )

    with self.command_group(
        "sql instance-failover-group-arc", operations, client_factory=beget
    ) as g:
        g.command(
            "create",
            "arc_sql_mi_fog_create",
            supports_no_wait=True,
            validator=validators.validate_create,
        )
        g.command(
            "update",
            "arc_sql_mi_fog_update",
            supports_no_wait=True,
            validator=validators.validate_update,
        )
        g.command(
            "delete",
            "arc_sql_mi_fog_delete",
            validator=validators.validate_delete,
        )
        g.show_command(
            "show", "arc_sql_mi_fog_show", validator=validators.validate_show
        )
        g.show_command(
            "list", "arc_sql_mi_fog_list", validator=validators.validate_list
        )
