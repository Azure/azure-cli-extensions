# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from azext_rdbms_vnet._client_factory import (
    cf_mysql_virtual_network_rules_operations,
    cf_postgres_virtual_network_rules_operations)


# pylint: disable=too-many-locals, too-many-statements, line-too-long
def load_command_table(self, _):

    rdbms_custom = CliCommandType(operations_tmpl='azext_rdbms_vnet.custom#{}')

    mysql_vnet_sdk = CliCommandType(
        operations_tmpl='azext_rdbms_vnet.mysql.operations.virtual_network_rules_operations#VirtualNetworkRulesOperations.{}',
        client_arg_name='self',
        client_factory=cf_mysql_virtual_network_rules_operations
    )

    postgres_vnet_sdk = CliCommandType(
        operations_tmpl='azext_rdbms_vnet.postgresql.operations.virtual_network_rules_operations#VirtualNetworkRulesOperations.{}',
        client_arg_name='self',
        client_factory=cf_postgres_virtual_network_rules_operations
    )
    with self.command_group('mysql server vnet-rule', mysql_vnet_sdk) as g:
        g.command('create', 'create_or_update')
        g.command('delete', 'delete', confirmation=True)
        g.command('show', 'get')
        g.command('list', 'list_by_server')
        g.generic_update_command('update', getter_name='_custom_vnet_update_get', getter_type=rdbms_custom,
                                 setter_name='_custom_vnet_update_set', setter_type=rdbms_custom, setter_arg_name='parameters')

    with self.command_group('postgres server vnet-rule', postgres_vnet_sdk) as g:
        g.command('create', 'create_or_update')
        g.command('delete', 'delete', confirmation=True)
        g.command('show', 'get')
        g.command('list', 'list_by_server')
        g.generic_update_command('update',
                                 getter_name='_custom_vnet_update_get', getter_type=rdbms_custom,
                                 setter_name='_custom_vnet_update_set', setter_type=rdbms_custom, setter_arg_name='parameters')
