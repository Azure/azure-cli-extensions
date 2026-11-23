# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import TestCase
from unittest.mock import patch

from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand
from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_horizondb import HorizonDBCommandsLoader
from azext_horizondb.aaz.latest.horizondb.cluster.custom import ClusterUpdate


class ClusterUpdateTests(TestCase):

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
        }
        self.identity_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test-rg'
            '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-identity'
        )

    def build_operation(self, **changes):
        command = ClusterUpdate(cli_ctx=self.cli_ctx)
        AAZCommand._handler(command, dict(self.args, **changes))  # pylint: disable=protected-access
        command.pre_operations()
        with patch.object(command.ctx, 'get_http_client'):
            return command.ClustersUpdate(ctx=command.ctx)

    def test_loader_registers_update_with_separate_encryption_arguments(self):
        loader = HorizonDBCommandsLoader(cli_ctx=self.cli_ctx)
        table = loader.load_command_table(['horizondb', 'cluster', 'update'])
        command = table['horizondb cluster update']
        self.assertIsInstance(command, ClusterUpdate)
        command.load_arguments()
        self.assertNotIn('data_encryption', command.arguments)
        for name, options in {
            'primary_key_uri': ['--primary-key-uri'],
            'primary_user_assigned_identity_id': ['--primary-user-assigned-identity-id', '--primary-user-id'],
        }.items():
            with self.subTest(argument=name):
                self.assertEqual(command.arguments[name].type.settings['options_list'], options)

    def test_update_sends_only_supplied_encryption_fields(self):
        key_uri = 'https://test.vault.azure.net/keys/new-key'
        for changes, encryption in [
                ({'primary_key_uri': key_uri}, {'primaryKeyUri': key_uri}),
                ({'primary_user_assigned_identity_id': self.identity_id},
                 {'primaryUserAssignedIdentityId': self.identity_id}),
                ({'primary_key_uri': key_uri, 'primary_user_assigned_identity_id': self.identity_id},
                 {'primaryKeyUri': key_uri, 'primaryUserAssignedIdentityId': self.identity_id})]:
            with self.subTest(changes=changes):
                operation = self.build_operation(**changes)
                self.assertEqual(operation.method, 'PATCH')
                self.assertEqual(operation.content, {'properties': {'dataEncryption': encryption}})
                self.assertEqual(operation.url_parameters, {
                    'subscriptionId': self.args['subscription'],
                    'resourceGroupName': 'test-rg',
                    'clusterName': 'test-cluster',
                })

    def test_other_updates_do_not_send_encryption_settings(self):
        operation = self.build_operation(backup_retention_days=14, tags={'environment': 'test'})
        self.assertEqual(operation.content, {
            'properties': {'backup': {'retentionDays': 14}},
            'tags': {'environment': 'test'},
        })

    def test_empty_encryption_arguments_are_rejected(self):
        for name in ['primary_key_uri', 'primary_user_assigned_identity_id']:
            with self.subTest(argument=name):
                with self.assertRaisesRegex(InvalidArgumentValueError, '--primary-'):
                    self.build_operation(**{name: ''})
