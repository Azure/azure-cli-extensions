# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from azext_rdbms._client_factory import (
    cf_mysql_servers,
    cf_postgres_servers)


# pylint: disable=too-many-locals, too-many-statements, line-too-long
def load_command_table(self, _):

    mysql_servers_sdk = CliCommandType(
        operations_tmpl='azext_rdbms.mysql.operations.servers_operations#ServersOperations.{}',
        client_arg_name='self',
        client_factory=cf_mysql_servers
    )

    postgres_servers_sdk = CliCommandType(
        operations_tmpl='azext_rdbms.postgresql.operations.servers_operations#ServersOperations.{}',
        client_arg_name='self',
        client_factory=cf_postgres_servers
    )

    with self.command_group('mysql server', mysql_servers_sdk, client_factory=cf_mysql_servers) as g:
        g.custom_command('create', '_server_create')
        g.custom_command('georestore', '_server_georestore', supports_no_wait=True)

    with self.command_group('postgres server', postgres_servers_sdk, client_factory=cf_postgres_servers) as g:
        g.custom_command('create', '_server_create')
        g.custom_command('georestore', '_server_georestore', supports_no_wait=True)
