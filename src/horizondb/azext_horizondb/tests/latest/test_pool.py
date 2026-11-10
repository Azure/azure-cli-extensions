# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import TestCase
from unittest.mock import Mock, patch

from azure.core.exceptions import HttpResponseError
from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand
from azext_horizondb.aaz.latest.horizondb.cluster.pool import Create as PoolCreate
from azext_horizondb.aaz.latest.horizondb.cluster.pool import custom as pool_custom
from azext_horizondb.aaz.latest.horizondb.cluster.pool.custom import PoolCreate as CustomPoolCreate, PoolUpdate


class PoolTests(TestCase):

    def setUp(self):
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Unit tests must not use Azure credentials or HTTP clients.')
        )
        http_client.start()
        self.addCleanup(http_client.stop)
        self.cli_ctx = get_default_cli()
        self.args = {
            'subscription': '00000000-0000-0000-0000-000000000001',
            'resource_group': 'test-rg',
            'cluster_name': 'test-cluster',
            'compute_generation': 1,
            'compute_processor': 'Intel',
            'v_cores': 2,
            'node_count': 1,
            'high_availability_mode': 'Disabled',
        }
        self.pool_update_args = {
            name: self.args[name] for name in ['subscription', 'resource_group', 'cluster_name']
        }
        self.pool_update_args.update(pool_name='my-pool', node_count=3)

    def test_pool_create_does_not_expose_parameter_group_arguments(self):
        command = CustomPoolCreate(cli_ctx=self.cli_ctx)
        command.load_arguments()
        self.assertNotIn('parameter_group_resource_id', command.arguments)
        self.assertNotIn('parameter_group_apply_method', command.arguments)

    def test_pool_update_supports_short_and_original_parameter_group_options(self):
        command = PoolUpdate(cli_ctx=self.cli_ctx)
        command.load_arguments()
        for name, options in {
            'parameter_group_apply_method': [
                '--parameter-group-apply-method', '--param-group-apply',
            ],
            'parameter_group_resource_id': ['--parameter-group-resource-id', '--param-group-id'],
        }.items():
            with self.subTest(argument=name):
                self.assertCountEqual(command.arguments[name].type.settings['options_list'], options)

    def test_pool_commands_do_not_expose_scheduled_maintenance(self):
        for command_type in [CustomPoolCreate, PoolUpdate]:
            with self.subTest(command=command_type.__name__):
                command = command_type(cli_ctx=self.cli_ctx)
                command.load_arguments()
                self.assertNotIn('scheduled_maintenance', command.arguments)
                self.assertIn('node_count', command.arguments)
                self.assertIn('no_wait', command.arguments)

    def test_pool_update_sends_only_node_count_in_patch(self):
        command = PoolUpdate(cli_ctx=self.cli_ctx)
        AAZCommand._handler(command, self.pool_update_args)  # pylint: disable=protected-access
        with patch.object(command.ctx, 'get_http_client'):
            operation = command.PoolsUpdate(ctx=command.ctx)
        self.assertEqual(operation.method, 'PATCH')
        self.assertEqual(operation.content, {'properties': {'nodeCount': 3}})

    def test_pool_update_gets_final_pool_after_empty_polling_result(self):
        command = PoolUpdate(cli_ctx=self.cli_ctx)
        events = []
        polling = Mock()
        polling.run.side_effect = lambda: events.append('polling')
        polling.resource.return_value = None
        updated_pool = {'name': 'my-pool', 'nodeCount': 3, 'provisioningState': 'Succeeded'}

        def show_pool(command_args):
            events.append('get')
            self.assertEqual(command_args, {
                name: self.pool_update_args[name]
                for name in ['cluster_name', 'pool_name', 'resource_group', 'subscription']
            })
            return updated_pool

        with patch.object(command, 'PoolsUpdate') as update, \
                patch.object(pool_custom, '_PoolShow') as show:
            update.return_value.return_value = polling
            show.return_value.side_effect = show_pool
            result = command(command_args=self.pool_update_args).result()

        self.assertEqual(events, ['polling', 'get'])
        self.assertEqual(result, updated_pool)
        self.assertFalse(hasattr(command.ctx.vars, 'instance'))
        show.return_value.assert_called_once()

    def test_pool_update_no_wait_does_not_get_pool(self):
        command = PoolUpdate(cli_ctx=self.cli_ctx)
        polling = Mock()
        with patch.object(command, 'PoolsUpdate') as update, \
                patch.object(pool_custom, '_PoolShow') as show:
            update.return_value.return_value = polling
            result = command(command_args=dict(self.pool_update_args, no_wait=True))
        self.assertIsNone(result)
        polling.run.assert_not_called()
        show.assert_not_called()

    def test_failed_pool_update_does_not_get_pool(self):
        command = PoolUpdate(cli_ctx=self.cli_ctx)
        polling = Mock()
        polling.run.side_effect = HttpResponseError('Update failed')
        with patch.object(command, 'PoolsUpdate') as update, \
                patch.object(pool_custom, '_PoolShow') as show:
            update.return_value.return_value = polling
            with self.assertRaisesRegex(HttpResponseError, 'Update failed'):
                command(command_args=self.pool_update_args).result()
        show.assert_not_called()

    def test_pool_update_reports_final_get_failure(self):
        command = PoolUpdate(cli_ctx=self.cli_ctx)
        polling = Mock()
        polling.resource.return_value = None
        with patch.object(command, 'PoolsUpdate') as update, \
                patch.object(pool_custom, '_PoolShow') as show:
            update.return_value.return_value = polling
            show.return_value.side_effect = HttpResponseError('Cannot read updated pool')
            with self.assertRaisesRegex(HttpResponseError, 'Cannot read updated pool'):
                command(command_args=self.pool_update_args).result()

    def test_pool_request_sets_provisioned_type_and_omits_parameter_group(self):
        command = CustomPoolCreate(cli_ctx=self.cli_ctx)
        args = dict(self.args, pool_name='defaultpool')
        AAZCommand._handler(command, args)  # pylint: disable=protected-access
        with patch.object(command.ctx, 'get_http_client'):
            operation = command.PoolsCreateOrReplace(ctx=command.ctx)
        content = operation.content
        self.assertEqual(content, {
            'properties': {
                'computeModel': {
                    'type': 'Provisioned',
                    'computeGeneration': 1,
                    'computeProcessor': 'Intel',
                    'vCores': 2,
                },
                'highAvailability': {'mode': 'Disabled'},
                'nodeCount': 1,
            },
        })
        self.assertEqual(operation.url_parameters, {
            'subscriptionId': self.args['subscription'],
            'resourceGroupName': 'test-rg',
            'clusterName': 'test-cluster',
            'poolName': 'defaultpool',
        })
        self.assertFalse(PoolCreate.get_arguments_schema().node_count._required)  # pylint: disable=protected-access
