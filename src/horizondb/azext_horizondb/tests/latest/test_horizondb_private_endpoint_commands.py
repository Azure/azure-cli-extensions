# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from azure.cli.core import get_default_cli
from knack.util import CLIError

from azext_horizondb import HorizonDBCommandsLoader
from azext_horizondb.commands.private_endpoint_commands import (
    horizondb_approve_private_endpoint_connection)
from azext_horizondb.utils.validators import validate_private_endpoint_connection_id
from azext_horizondb.vendored_sdks.operations._operations import (
    build_horizon_db_private_endpoint_connections_delete_request,
    build_horizon_db_private_endpoint_connections_update_request)


class HorizonDBPrivateEndpointCommandTests(unittest.TestCase):

    def test_private_endpoint_connection_id_commands_do_not_require_resource_group_at_parse_time(self):
        commands = [
            'horizondb private-endpoint-connection show',
            'horizondb private-endpoint-connection approve',
            'horizondb private-endpoint-connection reject',
            'horizondb private-endpoint-connection delete',
        ]

        for command in commands:
            cli = get_default_cli()
            cli.invocation = SimpleNamespace(data={'command_string': command})
            loader = HorizonDBCommandsLoader(cli_ctx=cli)
            loader.load_command_table(None)
            loader.load_arguments(None)

            resource_group_arg = loader.argument_registry.arguments[command]['resource_group_name']
            self.assertFalse(resource_group_arg.settings['required'], command)

    def test_child_list_commands_do_not_register_generic_ids_arguments(self):
        commands = [
            'horizondb private-endpoint-connection list',
            'horizondb private-link-resource list',
        ]

        for command in commands:
            cli = get_default_cli()
            cli.invocation = SimpleNamespace(data={'command_string': command})
            loader = HorizonDBCommandsLoader(cli_ctx=cli)
            loader.load_command_table(None)
            loader.load_arguments(None)

            cluster_name_arg = loader.argument_registry.arguments[command]['cluster_name']
            self.assertIsNone(cluster_name_arg.settings.get('id_part'), command)

    def test_update_request_is_cluster_scoped_put(self):
        request = build_horizon_db_private_endpoint_connections_update_request(
            resource_group_name='rg1',
            cluster_name='cluster1',
            private_endpoint_connection_name='pec1',
            subscription_id='00000000-0000-0000-0000-000000000000')

        self.assertEqual('PUT', request.method)
        self.assertIn('/providers/Microsoft.HorizonDb/clusters/cluster1/privateEndpointConnections/pec1',
                      request.url)
        self.assertNotIn('/providers/Microsoft.HorizonDb/privateEndpointConnections/pec1',
                         request.url)

    def test_delete_request_is_cluster_scoped(self):
        request = build_horizon_db_private_endpoint_connections_delete_request(
            resource_group_name='rg1',
            cluster_name='cluster1',
            private_endpoint_connection_name='pec1',
            subscription_id='00000000-0000-0000-0000-000000000000')

        self.assertEqual('DELETE', request.method)
        self.assertIn('/providers/Microsoft.HorizonDb/clusters/cluster1/privateEndpointConnections/pec1',
                      request.url)

    def test_validate_private_endpoint_connection_id_parses_horizondb_cluster_id(self):
        connection_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1'
            '/providers/Microsoft.HorizonDb/clusters/cluster1/privateEndpointConnections/pec1')
        namespace = SimpleNamespace(
            connection_id=connection_id,
            resource_group_name=None,
            cluster_name=None,
            private_endpoint_connection_name=None)

        validate_private_endpoint_connection_id(None, namespace)

        self.assertEqual('rg1', namespace.resource_group_name)
        self.assertEqual('cluster1', namespace.cluster_name)
        self.assertEqual('pec1', namespace.private_endpoint_connection_name)
        self.assertFalse(hasattr(namespace, 'connection_id'))

    def test_validate_private_endpoint_connection_id_rejects_non_horizondb_id(self):
        connection_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1'
            '/providers/Microsoft.Storage/storageAccounts/account1/privateEndpointConnections/pec1')
        namespace = SimpleNamespace(
            connection_id=connection_id,
            resource_group_name=None,
            cluster_name=None,
            private_endpoint_connection_name=None)

        with self.assertRaises(CLIError):
            validate_private_endpoint_connection_id(None, namespace)

    def test_validate_private_endpoint_connection_id_rejects_non_pec_child_id(self):
        connection_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1'
            '/providers/Microsoft.HorizonDb/clusters/cluster1/privateLinkResources/DefaultPool')
        namespace = SimpleNamespace(
            connection_id=connection_id,
            resource_group_name=None,
            cluster_name=None,
            private_endpoint_connection_name=None)

        with self.assertRaises(CLIError):
            validate_private_endpoint_connection_id(None, namespace)

    def test_validate_private_endpoint_connection_id_rejects_malformed_id(self):
        namespace = SimpleNamespace(
            connection_id='foo',
            resource_group_name=None,
            cluster_name=None,
            private_endpoint_connection_name=None)

        with self.assertRaises(CLIError):
            validate_private_endpoint_connection_id(None, namespace)

    def test_validate_private_endpoint_connection_id_rejects_extra_child_id(self):
        connection_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1'
            '/providers/Microsoft.HorizonDb/clusters/cluster1/privateEndpointConnections/pec1'
            '/extra/name')
        namespace = SimpleNamespace(
            connection_id=connection_id,
            resource_group_name=None,
            cluster_name=None,
            private_endpoint_connection_name=None)

        with self.assertRaises(CLIError):
            validate_private_endpoint_connection_id(None, namespace)

    def test_approve_private_endpoint_connection_uses_cluster_scoped_update(self):
        update_client = Mock()
        update_client.begin_update.return_value = 'poller'

        result = horizondb_approve_private_endpoint_connection(
            update_client,
            resource_group_name='rg1',
            cluster_name='cluster1',
            private_endpoint_connection_name='pec1',
            description='Approved')

        self.assertEqual('poller', result)
        update_client.begin_update.assert_called_once()
        kwargs = update_client.begin_update.call_args.kwargs
        self.assertEqual('rg1', kwargs['resource_group_name'])
        self.assertEqual('cluster1', kwargs['cluster_name'])
        self.assertEqual('pec1', kwargs['private_endpoint_connection_name'])
        self.assertEqual(
            'Approved',
            kwargs['properties'].properties.private_link_service_connection_state.status)
        self.assertEqual(
            'Approved',
            kwargs['properties'].properties.private_link_service_connection_state.description)


if __name__ == '__main__':
    unittest.main()
