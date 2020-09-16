# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_db_up._client_factory import cf_mysql_servers, cf_postgres_servers, cf_sql_servers
from azext_db_up._validators import db_up_namespace_processor, db_down_namespace_processor
from azext_db_up._transformers import table_transform_connection_string


def load_command_table(self, _):  # pylint: disable=too-many-locals, too-many-statements
    mysql_servers_sdk = CliCommandType(
        operations_tmpl='azext_db_up.vendored_sdks.azure_mgmt_rdbms.mysql.operations.servers_operations'
                        '#ServersOperations.{}',
        client_factory=cf_mysql_servers
    )

    postgres_servers_sdk = CliCommandType(
        operations_tmpl='azext_db_up.vendored_sdks.azure_mgmt_rdbms.postgresql.operations.servers_operations'
                        '#ServersOperations.{}',
        client_factory=cf_postgres_servers
    )

    sql_servers_sdk = CliCommandType(
        operations_tmpl='azext_db_up.vendored_sdks.azure_mgmt_sql.sql.operations.servers_operations'
                        '#ServersOperations.{}',
        client_factory=cf_sql_servers
    )

    with self.command_group('mysql', mysql_servers_sdk, client_factory=cf_mysql_servers) as g:
        from ._exception_handler import password_handler
        g.custom_command('up', 'mysql_up', validator=db_up_namespace_processor('mysql'),
                         table_transformer=table_transform_connection_string,
                         exception_handler=password_handler)
        g.custom_command('down', 'server_down', validator=db_down_namespace_processor('mysql'), supports_no_wait=True,
                         confirmation=True)
        g.custom_command('show-connection-string', 'create_mysql_connection_string')

    with self.command_group('postgres', postgres_servers_sdk, client_factory=cf_postgres_servers) as g:
        g.custom_command('up', 'postgres_up', validator=db_up_namespace_processor('postgres'),
                         table_transformer=table_transform_connection_string)
        g.custom_command('down', 'server_down', validator=db_down_namespace_processor('postgres'),
                         supports_no_wait=True, confirmation=True)
        g.custom_command('show-connection-string', 'create_postgresql_connection_string')

    with self.command_group('sql', sql_servers_sdk, client_factory=cf_sql_servers) as g:
        g.custom_command('up', 'sql_up', validator=db_up_namespace_processor('sql'),
                         table_transformer=table_transform_connection_string)
        g.custom_command('down', 'server_down', validator=db_down_namespace_processor('sql'),
                         supports_no_wait=True, confirmation=True)
