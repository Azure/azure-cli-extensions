# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import deepcopy
from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

from knack.util import CLIError
from azure.core.exceptions import HttpResponseError
from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand
from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_horizondb import HorizonDBCommandsLoader
from azext_horizondb.aaz.latest.horizondb.cluster import custom as cluster_custom
from azext_horizondb.aaz.latest.horizondb.cluster import custom_restore as restore_custom
from azext_horizondb.aaz.latest.horizondb.cluster.custom import ClusterCreate
from azext_horizondb.aaz.latest.horizondb.cluster.custom_restore import ClusterRestore


class ClusterRestoreTests(TestCase):

    def setUp(self):
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Unit tests must not use Azure credentials or HTTP clients.')
        )
        http_client.start()
        self.addCleanup(http_client.stop)
        self.command = ClusterRestore(cli_ctx=get_default_cli())
        self.source_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000002/resourceGroups/source-rg'
            '/providers/Microsoft.HorizonDb/clusters/source-cluster'
        )
        self.identity_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000002/resourceGroups/source-rg'
            '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/source-identity'
        )
        self.args = {
            'subscription': '00000000-0000-0000-0000-000000000001',
            'resource_group': 'target-rg',
            'cluster_name': 'restored-cluster',
            'creation_source_cluster_resource_id': self.source_id,
            'point_in_time_utc': '2026-07-27T12:00:00Z',
        }
        self.source = {
            'id': self.source_id,
            'name': 'source-cluster',
            'location': 'japaneast',
            'tags': {'environment': 'test'},
            'identity': {
                'type': 'UserAssigned',
                'userAssignedIdentities': {
                    self.identity_id: {'clientId': 'client-id', 'principalId': 'principal-id'},
                },
            },
            'properties': {
                'postgreSqlVersion': '17',
                'backup': {
                    'geoRedundancy': 'Enabled',
                    'retentionDays': 14,
                    'earliestRestorePointUtc': '2026-07-20T12:00:00Z',
                },
                'network': {'publicAccess': 'Enabled'},
                'dataEncryption': {
                    'type': 'AzureKeyVault',
                    'primaryKeyUri': 'https://source.vault.azure.net/keys/source-key',
                    'primaryUserAssignedIdentityId': self.identity_id,
                    'primaryEncryptionKeyStatus': 'Valid',
                },
                'aiModelManagement': 'Enabled',
                'creationMode': 'PointInTimeRestore',
                'pointInTimeUtc': '2026-07-21T12:00:00Z',
                'provisioningState': 'Succeeded',
                'state': 'Ready',
                'readWritePool': {'designatedPoolResourceId': 'old-pool'},
            },
        }

    def build_operation(self, **overrides):
        AAZCommand._handler(self.command, dict(self.args, **overrides))  # pylint: disable=protected-access
        with patch.object(cluster_custom._ClusterShow, '__call__', return_value=self.source) as show:
            self.command.pre_operations()
        show.assert_called_once_with(command_args={
            'subscription': '00000000-0000-0000-0000-000000000002',
            'resource_group': 'source-rg',
            'cluster_name': 'source-cluster',
        })
        with patch.object(self.command.ctx, 'get_http_client'):
            return self.command.ClustersCreateOrReplace(ctx=self.command.ctx)

    def test_loader_registers_restore_and_keeps_create_arguments_separate(self):
        loader = HorizonDBCommandsLoader(cli_ctx=self.command.cli_ctx)
        table = loader.load_command_table(['horizondb', 'cluster', 'restore'])
        self.assertIsInstance(table['horizondb cluster restore'], ClusterRestore)
        self.command.load_arguments()
        source_argument = self.command.arguments['creation_source_cluster_resource_id']
        self.assertEqual(source_argument.type.settings['options_list'], [
            '--source-cluster-id', '--creation-source-cluster-resource-id',
        ])
        self.assertNotIn('geo_redundancy', self.command.arguments)
        self.assertNotIn('version', self.command.arguments)
        self.assertNotIn('retention_days', self.command.arguments)
        self.assertNotIn('data_encryption', self.command.arguments)
        self.assertIn('primary_key_uri', self.command.arguments)
        self.assertIn('primary_user_assigned_identity_id', self.command.arguments)
        self.assertEqual(
            self.command.arguments['primary_user_assigned_identity_id'].type.settings['options_list'],
            ['--primary-user-assigned-identity-id', '--primary-user-id'],
        )
        create = ClusterCreate(cli_ctx=self.command.cli_ctx)
        create.load_arguments()
        self.assertNotIn('creation_source_cluster_resource_id', create.arguments)
        self.assertNotIn('point_in_time_utc', create.arguments)
        self.assertIn('geo_redundancy', create.arguments)
        self.assertIn('version', create.arguments)
        self.assertIn('retention_days', create.arguments)
        self.assertTrue(create.get_arguments_schema().location._required)  # pylint: disable=protected-access
        self.assertEqual(create.get_arguments_schema().retention_days._default, 7)  # pylint: disable=protected-access

    def test_restore_inherits_writable_settings_and_excludes_read_only_properties(self):
        original_source = deepcopy(self.source)
        operation = self.build_operation()
        self.assertEqual(operation.method, 'PUT')
        self.assertEqual(operation.url_parameters, {
            'subscriptionId': self.args['subscription'],
            'resourceGroupName': 'target-rg',
            'clusterName': 'restored-cluster',
        })
        self.assertEqual(operation.content, {
            'location': 'japaneast',
            'tags': {'environment': 'test'},
            'identity': {
                'type': 'UserAssigned',
                'userAssignedIdentities': {self.identity_id: {}},
            },
            'properties': {
                'backup': {'geoRedundancy': 'Enabled'},
                'network': {'publicAccess': 'Enabled'},
                'dataEncryption': {
                    'type': 'AzureKeyVault',
                    'primaryKeyUri': 'https://source.vault.azure.net/keys/source-key',
                    'primaryUserAssignedIdentityId': self.identity_id,
                },
                'aiModelManagement': 'Enabled',
                'creationMode': 'PointInTimeRestore',
                'creationSourceClusterResourceId': self.source_id,
                'creationSourceClusterLocation': 'japaneast',
                'pointInTimeUtc': '2026-07-27T12:00:00.000Z',
            },
        })
        self.assertEqual(self.source, original_source)

    def test_explicit_values_override_source_settings_and_enable_key_vault_encryption(self):
        self.source['properties']['dataEncryption'] = {'type': 'SystemManaged'}
        original_source = deepcopy(self.source)
        target_identity_id = self.identity_id.replace('source-identity', 'target-identity')
        operation = self.build_operation(
            location='eastus2', tags={},
            public_access='Disabled',
            primary_key_uri='https://target.vault.azure.net/keys/target-key',
            primary_user_assigned_identity_id=target_identity_id,
        )
        content = operation.content
        self.assertEqual(content['location'], 'eastus2')
        self.assertEqual(content['tags'], {})
        self.assertNotIn('postgreSqlVersion', content['properties'])
        self.assertEqual(content['properties']['backup'], {'geoRedundancy': 'Enabled'})
        self.assertEqual(content['properties']['network'], {'publicAccess': 'Disabled'})
        self.assertEqual(content['properties']['dataEncryption'], {
            'type': 'AzureKeyVault',
            'primaryKeyUri': 'https://target.vault.azure.net/keys/target-key',
            'primaryUserAssignedIdentityId': target_identity_id,
        })
        self.assertEqual(content['identity'], {
            'type': 'UserAssigned',
            'userAssignedIdentities': {self.identity_id: {}, target_identity_id: {}},
        })
        self.assertEqual(content['properties']['creationSourceClusterLocation'], 'japaneast')
        self.assertEqual(self.source, original_source)

    def test_restore_assigns_encryption_identity_without_source_assignments(self):
        for source_identity, expected_type in [
                (None, 'UserAssigned'),
                ({'type': 'None'}, 'UserAssigned'),
                ({'type': 'SystemAssigned'}, 'SystemAssigned, UserAssigned')]:
            with self.subTest(source_identity=source_identity):
                self.command = ClusterRestore(cli_ctx=self.command.cli_ctx)
                self.source['identity'] = source_identity
                content = self.build_operation(
                    primary_key_uri='https://target.vault.azure.net/keys/target-key',
                    primary_user_assigned_identity_id=self.identity_id,
                ).content
                self.assertEqual(content['identity'], {
                    'type': expected_type,
                    'userAssignedIdentities': {self.identity_id: {}},
                })

    def test_restore_inherits_system_managed_encryption_without_overrides(self):
        self.source['properties']['dataEncryption'] = {'type': 'SystemManaged'}
        content = self.build_operation().content
        self.assertEqual(content['properties']['dataEncryption'], {'type': 'SystemManaged'})

    def test_partial_encryption_override_fails_before_source_get_even_when_source_has_encryption(self):
        for changes in [
                {'primary_key_uri': 'https://target.vault.azure.net/keys/target-key'},
                {'primary_user_assigned_identity_id': self.identity_id}]:
            with self.subTest(changes=changes):
                command = ClusterRestore(cli_ctx=self.command.cli_ctx)
                with patch.object(cluster_custom._ClusterShow, '__call__', return_value=self.source) as show, \
                        patch.object(command, 'ClustersCreateOrReplace') as create:
                    with self.assertRaisesRegex(InvalidArgumentValueError, '--primary-key-uri'):
                        command(command_args=dict(self.args, **changes))
                show.assert_not_called()
                create.assert_not_called()

    def test_missing_optional_source_settings_are_not_fabricated(self):
        self.source = {'location': 'japaneast', 'properties': {'backup': {'geoRedundancy': 'Disabled'}}}
        content = self.build_operation().content
        self.assertEqual(content['properties']['backup'], {'geoRedundancy': 'Disabled'})
        self.assertNotIn('identity', content)
        self.assertNotIn('tags', content)
        self.assertNotIn('dataEncryption', content['properties'])

    def test_required_and_invalid_restore_arguments_fail_before_source_get(self):
        for changes in [
                {'creation_source_cluster_resource_id': None},
                {'point_in_time_utc': 'not-a-date'},
                {'creation_source_cluster_resource_id': '/subscriptions/sub/resourceGroups/rg/providers/Other/type/name'}]:
            with self.subTest(changes=changes):
                command = ClusterRestore(cli_ctx=self.command.cli_ctx)
                with patch.object(cluster_custom._ClusterShow, '__call__') as show:
                    with self.assertRaises(CLIError):
                        command(command_args=dict(self.args, **changes))
                show.assert_not_called()

    def test_restore_without_time_defaults_to_current_utc_time_once(self):
        self.args.pop('point_in_time_utc')
        with patch.object(restore_custom, 'datetime') as clock:
            clock.now.return_value = datetime(2026, 11, 2, 22, 49, 20, 138000, tzinfo=timezone.utc)
            operation = self.build_operation()
            content = operation.content
            self.assertEqual(content['properties']['pointInTimeUtc'], '2026-11-02T22:49:20.138Z')
            self.assertEqual(operation.content['properties']['pointInTimeUtc'], '2026-11-02T22:49:20.138Z')
        clock.now.assert_called_once_with(timezone.utc)
        self.assertEqual(content['properties']['creationMode'], 'PointInTimeRestore')

    def test_restore_with_null_time_defaults_to_current_utc_time(self):
        with patch.object(restore_custom, 'datetime') as clock:
            clock.now.return_value = datetime(2026, 11, 2, 22, 49, 21, tzinfo=timezone.utc)
            content = self.build_operation(point_in_time_utc=None).content
        self.assertEqual(content['properties']['pointInTimeUtc'], '2026-11-02T22:49:21.000Z')

    def test_location_requires_geo_redundancy_enabled_on_source(self):
        for geo_redundancy, location in [
                ('Disabled', 'eastus2'), ('Disabled', 'japaneast'), (None, 'eastus2')]:
            with self.subTest(geo_redundancy=geo_redundancy, location=location):
                source = deepcopy(self.source)
                if geo_redundancy is None:
                    source['properties']['backup'].pop('geoRedundancy')
                else:
                    source['properties']['backup']['geoRedundancy'] = geo_redundancy
                command = ClusterRestore(cli_ctx=self.command.cli_ctx)
                with patch.object(cluster_custom._ClusterShow, '__call__', return_value=source), \
                        patch.object(command, 'ClustersCreateOrReplace') as create:
                    with self.assertRaisesRegex(InvalidArgumentValueError, '--location.*geo-redundancy enabled'):
                        command(command_args=dict(self.args, location=location))
                create.assert_not_called()

    def test_source_get_failure_prevents_restore(self):
        with patch.object(cluster_custom._ClusterShow, '__call__',
                          side_effect=HttpResponseError('Source access denied')), \
                patch.object(self.command, 'ClustersCreateOrReplace') as create:
            with self.assertRaisesRegex(HttpResponseError, 'Source access denied'):
                self.command(command_args=self.args)
        create.assert_not_called()

    def test_restore_waits_and_returns_final_get_of_target_cluster(self):
        events = []
        restored = {'name': 'restored-cluster', 'provisioningState': 'Succeeded'}

        def show_cluster(command_args):
            events.append(command_args['cluster_name'])
            if command_args['cluster_name'] == 'source-cluster':
                return self.source
            self.assertEqual(command_args, {
                name: self.args[name] for name in ['subscription', 'resource_group', 'cluster_name']
            })
            return restored

        with patch.object(cluster_custom._ClusterShow, '__call__', side_effect=show_cluster), \
                patch.object(self.command, 'ClustersCreateOrReplace') as create:
            create.return_value.side_effect = lambda: events.append('restore')
            result = self.command(command_args=self.args)

        self.assertEqual(events, ['source-cluster', 'restore', 'restored-cluster', 'restored-cluster'])
        self.assertEqual(result, restored)
