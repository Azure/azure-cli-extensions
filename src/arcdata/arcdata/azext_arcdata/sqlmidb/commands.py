# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.sqlmidb.client import beget, beget_no_namespace
from azure.cli.core.commands import CliCommandType


def load_commands(self, _):
    operations = CliCommandType(
        operations_tmpl="azext_arcdata.sqlmidb.custom#{}"
    )

    with self.command_group(
        "sql midb-arc", operations, client_factory=beget
    ) as g:
        # pylint: disable=E5001
        g.command("restore", "arc_sql_midb_restore")
