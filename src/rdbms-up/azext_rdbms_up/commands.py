# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.command_modules.rdbms._client_factory import cf_mysql_servers
from azext_rdbms_up._validators import process_mysql_namespace
from azext_rdbms_up._transformers import table_transform_connection_string


def load_command_table(self, _):  # pylint: disable=too-many-locals, too-many-statements
    mysql_servers_sdk = CliCommandType(
        operations_tmpl='azext_rdbms_up.vendored_sdks.azure_mgmt_rdbms.mysql.operations.servers_operations'
                        '#ServersOperations.{}',
        client_factory=cf_mysql_servers
    )

    with self.command_group('mysql', mysql_servers_sdk, client_factory=cf_mysql_servers) as g:
        g.custom_command('up', 'mysql_up', validator=process_mysql_namespace,
                         table_transformer=table_transform_connection_string)
