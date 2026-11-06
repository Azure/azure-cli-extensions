# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import TestCase
from unittest.mock import patch

from knack.util import CLIError
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand
from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_horizondb import HorizonDBCommandsLoader
from azext_horizondb.aaz.latest.horizondb.cluster import custom as cluster_custom
from azext_horizondb.aaz.latest.horizondb.cluster.custom import ClusterCreate
from azext_horizondb.aaz.latest.horizondb.cluster.pool.custom import PoolCreate as CustomPoolCreate, PoolUpdate


class ClusterCreateTests(TestCase):

    def setUp(self):
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Unit tests must not use Azure credentials or HTTP clients.')
        )
        http_client.start()
        self.addCleanup(http_client.stop)
        self.command = ClusterCreate(cli_ctx=get_default_cli())
        self.args = {
            'subscription': '00000000-0000-0000-0000-000000000001',
            'resource_group': 'test-rg',
            'cluster_name': 'test-cluster',
            'location': 'japaneast',
        }
        self.cluster = {'name': 'test-cluster', 'location': 'japaneast'}
        self.identity_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test-rg'
            '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-identity'
        )
        show_cluster = patch.object(cluster_custom, '_ClusterShow')
        self.show_cluster = show_cluster.start().return_value
        self.addCleanup(show_cluster.stop)
        self.show_cluster.return_value = dict(self.cluster, provisioningState='Succeeded')

    def build_content(self, **overrides):
        args = dict(self.args, geo_redundancy='Disabled', **overrides)
        AAZCommand._handler(self.command, args)  # pylint: disable=protected-access
        self.command.pre_operations()
        with patch.object(self.command.ctx, 'get_http_client'):
            operation = self.command.ClustersCreateOrReplace(ctx=self.command.ctx)
        return operation.content

    def test_loader_registers_custom_commands(self):
        loader = HorizonDBCommandsLoader(cli_ctx=self.command.cli_ctx)
        table = loader.load_command_table(['horizondb', 'cluster', 'create'])
        self.assertIsInstance(table['horizondb cluster create'], ClusterCreate)
        self.assertIsInstance(table['horizondb cluster pool create'], CustomPoolCreate)
        self.assertIsInstance(table['horizondb cluster pool update'], PoolUpdate)

    def test_cluster_create_does_not_expose_pool_arguments(self):
        self.command.load_arguments()
        for name in [
                'compute_generation', 'compute_processor', 'v_cores',
                'node_count', 'high_availability_mode', 'pool_name']:
            with self.subTest(argument=name):
                self.assertNotIn(name, self.command.arguments)
        for argument in self.command.arguments.values():
            for option in argument.type.settings.get('options_list', []):
                self.assertFalse(option.startswith('--pool-'), option)

    def test_create_exposes_separate_encryption_arguments(self):
        self.command.load_arguments()
        self.assertNotIn('data_encryption', self.command.arguments)
        for name, options in {
            'primary_key_uri': ['--primary-key-uri'],
            'primary_user_assigned_identity_id': ['--primary-user-assigned-identity-id', '--primary-user-id'],
        }.items():
            with self.subTest(argument=name):
                self.assertEqual(self.command.arguments[name].type.settings['options_list'], options)

    def test_create_without_encryption_arguments_omits_data_encryption(self):
        self.assertNotIn('dataEncryption', self.build_content()['properties'])

    def test_create_enables_key_vault_encryption_with_both_arguments(self):
        content = self.build_content(
            primary_key_uri='https://test.vault.azure.net/keys/test-key',
            primary_user_assigned_identity_id=self.identity_id,
        )
        self.assertEqual(content['properties']['dataEncryption'], {
            'type': 'AzureKeyVault',
            'primaryKeyUri': 'https://test.vault.azure.net/keys/test-key',
            'primaryUserAssignedIdentityId': self.identity_id,
        })

    def test_incomplete_or_empty_encryption_arguments_prevent_create(self):
        for changes in [
                {'primary_key_uri': 'https://test.vault.azure.net/keys/test-key'},
                {'primary_user_assigned_identity_id': self.identity_id},
                {'primary_key_uri': '', 'primary_user_assigned_identity_id': self.identity_id}]:
            with self.subTest(changes=changes):
                command = ClusterCreate(cli_ctx=self.command.cli_ctx)
                with patch.object(command, 'ClustersCreateOrReplace') as create:
                    with self.assertRaisesRegex(InvalidArgumentValueError, '--primary-key-uri'):
                        command(command_args=dict(self.args, **changes))
                create.assert_not_called()
        self.show_cluster.assert_not_called()

    def test_pool_commands_keep_compute_and_availability_arguments(self):
        expected_options = {
            'compute_generation': ['--compute-generation'],
            'compute_processor': ['--compute-processor'],
            'v_cores': ['--v-cores'],
            'node_count': ['--node-count'],
            'high_availability_mode': ['--high-availability-mode'],
        }
        for command_type in [CustomPoolCreate, PoolUpdate]:
            command = command_type(cli_ctx=self.command.cli_ctx)
            command.load_arguments()
            for name, options in expected_options.items():
                with self.subTest(command=command_type.__name__, argument=name):
                    self.assertEqual(command.arguments[name].type.settings['options_list'], options)

    def test_creates_cluster_without_pool_then_gets_current_cluster(self):
        events = []
        not_found = ResourceNotFoundError('Cluster is not visible yet')
        not_found.status_code = 404
        states = iter([not_found, 'Creating', 'Succeeded', 'final-get'])
        updated_cluster = dict(self.cluster, provisioningState='Succeeded')

        def show_cluster(command_args):
            self.assertEqual(command_args, {
                name: self.args[name] for name in ['cluster_name', 'resource_group', 'subscription']
            })
            state = next(states)
            events.append(state if isinstance(state, str) else 'not-found')
            if isinstance(state, ResourceNotFoundError):
                raise state
            if state == 'final-get':
                return updated_cluster
            return dict(self.cluster, provisioningState=state)

        self.show_cluster.side_effect = show_cluster

        with patch.object(self.command, 'ClustersCreateOrReplace') as cluster_operation, \
                patch('time.sleep') as sleep, \
                patch.object(cluster_custom, 'logger') as logger:
            cluster_operation.return_value.side_effect = lambda: events.append('cluster')
            result = self.command(command_args=self.args)

        self.assertEqual(events, ['cluster', 'not-found', 'Creating', 'Succeeded', 'final-get'])
        cluster_operation.return_value.assert_called_once_with()
        self.assertEqual(sleep.call_count, 2)
        logger.warning.assert_called_once_with(
            "Waiting for cluster '%s' provisioning to complete...", 'test-cluster'
        )
        self.assertEqual(result, updated_cluster)

    def test_cluster_failure_does_not_poll(self):
        with patch.object(self.command, 'ClustersCreateOrReplace') as cluster_operation:
            cluster_operation.return_value.side_effect = CLIError('cluster failed')
            with self.assertRaisesRegex(CLIError, 'cluster failed'):
                self.command(command_args=self.args)
        self.show_cluster.assert_not_called()

    def test_failed_cluster_provisioning_is_reported(self):
        self.show_cluster.return_value = dict(self.cluster, provisioningState='Failed')
        with patch.object(self.command, 'ClustersCreateOrReplace'):
            with self.assertRaisesRegex(CLIError, 'operation failed'):
                self.command(command_args=self.args)

    def test_cluster_polling_error_is_reported(self):
        error = HttpResponseError('Access denied')
        error.status_code = 403
        self.show_cluster.side_effect = error
        with patch.object(self.command, 'ClustersCreateOrReplace'):
            with self.assertRaisesRegex(HttpResponseError, 'Access denied'):
                self.command(command_args=self.args)

    def test_cluster_provisioning_timeout_is_reported(self):
        with patch.object(self.command, 'ClustersCreateOrReplace'), \
                patch.object(cluster_custom.WaitCommandOperation, 'wait',
                      return_value=CLIError('Wait operation timed-out')) as wait:
            with self.assertRaisesRegex(CLIError, 'timed-out'):
                self.command(command_args=self.args)
        self.assertTrue(wait.call_args.kwargs['command_args']['created'])
        self.show_cluster.assert_not_called()

    def test_cluster_create_reports_final_get_failure(self):
        self.show_cluster.side_effect = [
            dict(self.cluster, provisioningState='Succeeded'),
            HttpResponseError('Cannot read completed cluster'),
        ]
        with patch.object(self.command, 'ClustersCreateOrReplace'):
            with self.assertRaisesRegex(HttpResponseError, 'Cannot read completed cluster'):
                self.command(command_args=self.args)
        self.assertEqual(self.show_cluster.call_count, 2)
