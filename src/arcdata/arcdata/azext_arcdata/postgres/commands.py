# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from azext_arcdata.core.cli_client import beget
from azure.cli.core.commands import CliCommandType


def load_commands(self, _):
    operations = CliCommandType(
        operations_tmpl="azext_arcdata.postgres.custom#{}"
    )
    # --------------------------------------------------------------------------
    # Server Commands
    # --------------------------------------------------------------------------
    with self.command_group(
        "postgres server-arc",
        operations,
        client_factory=beget,
        deprecate_info=self.deprecate(redirect="", hide=True),
    ) as g:
        # pylint: disable=E5001
        g.command(
            "create",
            "postgres_server_arc_create",
            deprecate_info=g.deprecate(redirect="", hide=True),
        )
        g.command(
            "delete",
            "postgres_server_arc_delete",
            deprecate_info=g.deprecate(hide=True),
        )
        g.command(
            "restore",
            "postgres_server_arc_restore",
            deprecate_info=g.deprecate(hide=True),
        )
        g.command(
            "show",
            "postgres_server_arc_show",
            deprecate_info=g.deprecate(hide=True),
        )
        g.command(
            "list",
            "postgres_server_arc_list",
            deprecate_info=g.deprecate(hide=True),
        )
        g.command(
            "update",
            "postgres_server_arc_update",
            deprecate_info=g.deprecate(hide=True),
        )

    # --------------------------------------------------------------------------
    # Endpoint Commands
    # --------------------------------------------------------------------------
    with self.command_group(
        "postgres server-arc endpoint",
        operations,
        client_factory=beget,
        deprecate_info=self.deprecate(hide=True),
    ) as g:
        g.command(
            "list",
            "arc_postgres_endpoint_list",
            deprecate_info=g.deprecate(hide=True),
        )

    with self.command_group(
        "postgres server-arc",
        is_preview=True,
        deprecate_info=self.deprecate(hide=True),
    ):
        pass
