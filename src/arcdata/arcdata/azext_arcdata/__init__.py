# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_arcdata import help

__all__ = ["COMMAND_LOADER_CLS"]


class ArcDataCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        custom_type = CliCommandType(operations_tmpl="azext_arcdata#{}")
        super(ArcDataCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=custom_type
        )

    def load_command_table(self, args):
        from azext_arcdata.sqlmi.commands import load_commands as sqlmi_commands
        from azext_arcdata.dc.commands import load_commands as dc_commands
        from azext_arcdata.postgres.commands import (
            load_commands as postgres_commands,
        )
        from azext_arcdata.sqlmidb.commands import (
            load_commands as sqlmidb_commands,
        )
        from azext_arcdata.ad_connector.commands import (
            load_commands as ad_connector_commands,
        )
        from azext_arcdata.failover_group.commands import (
            load_commands as failover_group_commands,
        )

        from azext_arcdata.sqlarc.database.commands import (
            load_commands as sqlarcdb_commands,
        )
        from azext_arcdata.sqlarc.server.commands import (
            load_commands as sqlarcserver_commands,
        )

        postgres_commands(self, args)
        sqlarcdb_commands(self, args)
        sqlarcserver_commands(self, args)
        sqlmi_commands(self, args)
        sqlmidb_commands(self, args)
        dc_commands(self, args)
        ad_connector_commands(self, args)
        failover_group_commands(self, args)

        return self.command_table

    def load_arguments(self, command):
        from azext_arcdata.postgres.arguments import (
            load_arguments as postgres_arguments,
        )
        from azext_arcdata.sqlmi.arguments import (
            load_arguments as sqlmi_arguments,
        )
        from azext_arcdata.sqlmidb.arguments import (
            load_arguments as sqlmidb_arguments,
        )
        from azext_arcdata.dc.arguments import (
            load_arguments as dc_arguments,
        )
        from azext_arcdata.ad_connector.arguments import (
            load_arguments as ad_arguments,
        )
        from azext_arcdata.failover_group.arguments import (
            load_arguments as failover_group_arguments,
        )

        from azext_arcdata.sqlarc.database.arguments import (
            load_arguments as sqlarcdb_arguments,
        )
        from azext_arcdata.sqlarc.server.arguments import (
            load_arguments as sqlarcserver_arguments,
        )

        postgres_arguments(self, command)
        sqlarcdb_arguments(self, command)
        sqlarcserver_arguments(self, command)
        sqlmi_arguments(self, command)
        sqlmidb_arguments(self, command)
        dc_arguments(self, command)
        ad_arguments(self, command)
        failover_group_arguments(self, command)


COMMAND_LOADER_CLS = ArcDataCommandsLoader
