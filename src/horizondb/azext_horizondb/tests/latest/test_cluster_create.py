# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import TestCase
from unittest.mock import patch

from knack.util import CLIError
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.cli.core import get_default_cli
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
            'compute_generation': 1,
            'compute_processor': 'Intel',
            'v_cores': 2,
            'node_count': 1,
            'high_availability_mode': 'Disabled',
        }
        self.cluster = {'name': 'test-cluster', 'location': 'japaneast'}
        show_cluster = patch.object(cluster_custom, '_ClusterShow')
        self.show_cluster = show_cluster.start().return_value
        self.addCleanup(show_cluster.stop)
        self.show_cluster.return_value = dict(self.cluster, provisioningState='Succeeded')

    def test_loader_registers_custom_commands(self):
        loader = HorizonDBCommandsLoader(cli_ctx=self.command.cli_ctx)
        table = loader.load_command_table(['horizondb', 'cluster', 'create'])
        self.assertIsInstance(table['horizondb cluster create'], ClusterCreate)
        self.assertIsInstance(table['horizondb cluster pool create'], CustomPoolCreate)
        self.assertIsInstance(table['horizondb cluster pool update'], PoolUpdate)

    def test_only_cluster_create_prefixes_pool_arguments(self):
        expected_options = {
            'compute_generation': ['--pool-compute-generation', '--pool-compute-gen'],
            'compute_processor': ['--pool-compute-processor', '--pool-compute-proc'],
            'v_cores': ['--pool-v-cores'],
            'node_count': ['--pool-node-count'],
            'high_availability_mode': ['--pool-high-availability-mode', '--pool-ha-mode'],
        }
        for command_type in [ClusterCreate, CustomPoolCreate, PoolUpdate]:
            command = command_type(cli_ctx=self.command.cli_ctx)
            command.load_arguments()
            for name, options in expected_options.items():
                with self.subTest(command=command_type.__name__, argument=name):
                    if command_type is not ClusterCreate:
                        options = [options[0].replace('--pool-', '--', 1)]
                    self.assertEqual(command.arguments[name].type.settings['options_list'], options)

    def test_creates_default_pool_then_gets_current_cluster(self):
        events = []
        schema_builder = self.command.ClustersCreateOrReplace._build_schema_on_200_201
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

        def create_cluster():
            events.append('cluster')
            self.command.ctx.set_var(
                'instance', self.cluster, schema_builder=schema_builder
            )

        def create_pool(command_args):
            events.append('pool')
            expected_args = {
                key: value for key, value in self.args.items() if key != 'location'
            }
            expected_args['pool_name'] = 'defaultpool'
            self.assertEqual(command_args, expected_args)
            return poller

        poller = object()
        with patch.object(self.command, 'ClustersCreateOrReplace') as cluster_operation, \
                patch.object(cluster_custom, 'PoolCreate') as pool_command, \
                patch.object(cluster_custom, 'LongRunningOperation') as wait, \
                patch('time.sleep') as sleep, \
                patch.object(cluster_custom, 'logger') as logger:
            cluster_operation.return_value.side_effect = create_cluster
            pool_command.return_value.side_effect = create_pool
            wait.return_value.side_effect = lambda _: events.append('pool-complete')
            result = self.command(command_args=self.args)

        self.assertEqual(events, [
            'cluster', 'not-found', 'Creating', 'Succeeded', 'pool', 'pool-complete', 'final-get',
        ])
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual(logger.warning.call_args_list[-1].args, (
            "Creating default pool 'defaultpool' for cluster '%s'...", 'test-cluster'
        ))
        wait.return_value.assert_called_once_with(poller)
        self.assertEqual(result, updated_cluster)

    def test_cluster_failure_does_not_create_pool(self):
        with patch.object(self.command, 'ClustersCreateOrReplace') as cluster_operation, \
                patch.object(cluster_custom, 'PoolCreate') as pool_command:
            cluster_operation.return_value.side_effect = CLIError('cluster failed')
            with self.assertRaisesRegex(CLIError, 'cluster failed'):
                self.command(command_args=self.args)
        pool_command.assert_not_called()
        self.show_cluster.assert_not_called()

    def test_failed_cluster_provisioning_does_not_create_pool(self):
        self.show_cluster.return_value = dict(self.cluster, provisioningState='Failed')
        with patch.object(self.command, 'ClustersCreateOrReplace'), \
                patch.object(cluster_custom, 'PoolCreate') as pool_command:
            with self.assertRaisesRegex(CLIError, 'operation failed'):
                self.command(command_args=self.args)
        pool_command.assert_not_called()

    def test_cluster_polling_error_does_not_create_pool(self):
        error = HttpResponseError('Access denied')
        error.status_code = 403
        self.show_cluster.side_effect = error
        with patch.object(self.command, 'ClustersCreateOrReplace'), \
                patch.object(cluster_custom, 'PoolCreate') as pool_command:
            with self.assertRaisesRegex(HttpResponseError, 'Access denied'):
                self.command(command_args=self.args)
        pool_command.assert_not_called()

    def test_cluster_provisioning_timeout_does_not_create_pool(self):
        with patch.object(self.command, 'ClustersCreateOrReplace'), \
                patch.object(cluster_custom, 'PoolCreate') as pool_command, \
                patch.object(cluster_custom.WaitCommandOperation, 'wait',
                      return_value=CLIError('Wait operation timed-out')) as wait:
            with self.assertRaisesRegex(CLIError, 'timed-out'):
                self.command(command_args=self.args)
        self.assertTrue(wait.call_args.kwargs['command_args']['created'])
        pool_command.assert_not_called()

    def test_pool_failure_is_reported(self):
        with patch.object(self.command, 'ClustersCreateOrReplace'), \
                patch.object(cluster_custom, 'PoolCreate'), \
                patch.object(cluster_custom, 'LongRunningOperation') as wait:
            wait.return_value.side_effect = CLIError('pool failed')
            with self.assertRaisesRegex(CLIError, 'pool failed'):
                self.command(command_args=self.args)
        self.show_cluster.assert_called_once()

    def test_cluster_create_reports_final_get_failure(self):
        self.show_cluster.side_effect = [
            dict(self.cluster, provisioningState='Succeeded'),
            HttpResponseError('Cannot read completed cluster'),
        ]
        with patch.object(self.command, 'ClustersCreateOrReplace'), \
                patch.object(cluster_custom, 'PoolCreate'), \
                patch.object(cluster_custom, 'LongRunningOperation') as wait:
            with self.assertRaisesRegex(HttpResponseError, 'Cannot read completed cluster'):
                self.command(command_args=self.args)
        wait.return_value.assert_called_once()
        self.assertEqual(self.show_cluster.call_count, 2)

    def test_invalid_pool_configuration_prevents_cluster_creation(self):
        for node_count, mode in [(1, 'AnyZone'), (1, 'ZoneRedundant'), (2, 'Disabled')]:
            with self.subTest(node_count=node_count, mode=mode), \
                    patch.object(self.command, 'ClustersCreateOrReplace') as cluster_operation:
                args = dict(self.args, node_count=node_count, high_availability_mode=mode)
                with self.assertRaisesRegex(InvalidArgumentValueError, '--pool-high-availability-mode'):
                    self.command(command_args=args)
                cluster_operation.assert_not_called()

    def test_pool_argument_ranges_are_checked_before_cluster_creation(self):
        for name, value in [
                ('compute_generation', 0),
                ('v_cores', 1), ('v_cores', 193),
                ('node_count', 0), ('node_count', 17)]:
            with self.subTest(argument=name, value=value), \
                    patch.object(self.command, 'ClustersCreateOrReplace') as cluster_operation:
                args = dict(self.args, **{name: value})
                with self.assertRaises(InvalidArgumentValueError):
                    self.command(command_args=args)
                cluster_operation.assert_not_called()

    def test_multi_node_pool_supports_both_ha_modes(self):
        for mode in ['AnyZone', 'ZoneRedundant']:
            with self.subTest(mode=mode), \
                    patch.object(self.command, 'ClustersCreateOrReplace'), \
                    patch.object(cluster_custom, 'PoolCreate') as pool_command, \
                    patch.object(cluster_custom, 'LongRunningOperation'), \
                    patch.object(self.command, '_output'):
                args = dict(self.args, node_count=16, high_availability_mode=mode,
                            compute_processor='Intel', v_cores=192)
                self.command(command_args=args)
                pool_args = pool_command.return_value.call_args.kwargs['command_args']
                self.assertEqual(pool_args['node_count'], 16)
                self.assertEqual(pool_args['high_availability_mode'], mode)
