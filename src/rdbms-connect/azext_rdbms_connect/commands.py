# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_mysql_flexible_location_capabilities, cf_postgres_flexible_location_capabilities


def load_command_table(self, _):
    mysql_flexible_location_capabilities_sdk = CliCommandType(
        operations_tmpl='azext_rdbms_connect.vendored_sdks.operations#LocationBasedCapabilitiesOperations.{}',
        client_factory=cf_mysql_flexible_location_capabilities
    )

    postgres_flexible_location_capabilities_sdk = CliCommandType(
        operations_tmpl='azext_rdbms_connect.vendored_sdks.operations#LocationBasedCapabilitiesOperations.{}',
        client_factory=cf_postgres_flexible_location_capabilities
    )

    with self.command_group('mysql flexible-server', mysql_flexible_location_capabilities_sdk,
                            client_factory=cf_mysql_flexible_location_capabilities,
                            is_preview=True) as g:
        g.custom_command('connect', 'connect_to_flexible_server_mysql')
        g.custom_command('execute', 'execute_flexible_server_mysql')

    with self.command_group('postgres flexible-server', postgres_flexible_location_capabilities_sdk,
                            client_factory=cf_postgres_flexible_location_capabilities,
                            is_preview=True) as g:
        g.custom_command('connect', 'connect_to_flexible_server_postgres')
        g.custom_command('execute', 'execute_flexible_server_postgres')
