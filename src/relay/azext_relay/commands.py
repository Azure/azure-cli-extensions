# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from azure.cli.core.commands import CliCommandType
from azext_relay._client_factory import (namespaces_mgmt_client_factory, wcfrelay_mgmt_client_factory, hydrid_connections_mgmt_client_factory)
from azext_relay.custom import empty_on_404


def load_command_table(self, _):

    relay_namespace_util = CliCommandType(
        operations_tmpl='azext_relay.relay.operations.namespaces_operations#NamespacesOperations.{}',
        client_factory=namespaces_mgmt_client_factory,
        client_arg_name='self'
    )

    relay_wcf_relay_util = CliCommandType(
        operations_tmpl='azext_relay.relay.operations.wcf_relays_operations#WCFRelaysOperations.{}',
        client_factory=wcfrelay_mgmt_client_factory,
        client_arg_name='self'
    )

    relay_hybrid_connections_util = CliCommandType(
        operations_tmpl='azext_relay.relay.operations.hybrid_connections_operations#HybridConnectionsOperations.{}',
        client_factory=hydrid_connections_mgmt_client_factory,
        client_arg_name='self'
    )

# Namespace Region
    with self.command_group('relay namespace', relay_namespace_util, client_factory=namespaces_mgmt_client_factory) as g:
        g.custom_command('create', 'cli_namespace_create')
        g.command('show', 'get', exception_handler=empty_on_404)
        g.custom_command('list', 'cli_namespace_list', exception_handler=empty_on_404)
        g.command('delete', 'delete')
        g.command('exists', 'check_name_availability_method')

    with self.command_group('relay namespace authorization-rule', relay_namespace_util, client_factory=namespaces_mgmt_client_factory) as g:
        g.custom_command('create', 'cli_namespaceautho_create')
        g.command('show', 'get_authorization_rule', exception_handler=empty_on_404)
        g.command('list', 'list_authorization_rules', exception_handler=empty_on_404)
        g.command('keys list', 'list_keys')
        g.command('keys renew', 'regenerate_keys')
        g.command('delete', 'delete_authorization_rule')

# WcfRelay Region
    with self.command_group('relay wcf-relay', relay_wcf_relay_util, client_factory=wcfrelay_mgmt_client_factory) as g:
        g.custom_command('create', 'cli_wcfrelay_create')
        g.command('show', 'get', exception_handler=empty_on_404)
        g.command('list', 'list_by_namespace', exception_handler=empty_on_404)
        g.command('delete', 'delete')

    with self.command_group('relay wcf-relay authorization-rule', relay_wcf_relay_util, client_factory=wcfrelay_mgmt_client_factory) as g:
        g.custom_command('create', 'cli_wcfrelayautho_create')
        g.command('show', 'get_authorization_rule', exception_handler=empty_on_404)
        g.command('list', 'list_authorization_rules', exception_handler=empty_on_404)
        g.command('keys list', 'list_keys')
        g.command('keys renew', 'regenerate_keys')
        g.command('delete', 'delete_authorization_rule')

# HybridConnections Region
    with self.command_group('relay hybrid-connections', relay_hybrid_connections_util, client_factory=hydrid_connections_mgmt_client_factory) as g:
        g.command('create', 'create_or_update')
        g.command('show', 'get', exception_handler=empty_on_404)
        g.command('list', 'list_by_namespace', exception_handler=empty_on_404)
        g.command('delete', 'delete')

    with self.command_group('relay hybrid-connections authorization-rule', relay_hybrid_connections_util, client_factory=hydrid_connections_mgmt_client_factory) as g:
        g.custom_command('create', 'cli_hybridconnectionsautho_create')
        g.command('show', 'get_authorization_rule', exception_handler=empty_on_404)
        g.command('list', 'list_authorization_rules', exception_handler=empty_on_404)
        g.command('keys list', 'list_keys')
        g.command('keys renew', 'regenerate_keys')
        g.command('delete', 'delete_authorization_rule')
