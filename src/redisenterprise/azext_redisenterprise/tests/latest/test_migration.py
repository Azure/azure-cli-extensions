# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime

from azure.core.exceptions import HttpResponseError
from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .recording_processors import RedisEnterpriseKeyReplacer


class RedisEnterpriseMigrationScenarioTest(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_processors.append(RedisEnterpriseKeyReplacer())
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-mig-', length=21),
            'source_redis': self.create_random_name(prefix='clitest-src-', length=21),
            'location': 'eastus2euap',
        })

    def _create_target(self):
        self.cmd('redisenterprise create -g {rg} --cluster-name {cluster} '
                 '--location {location} --sku Balanced_B1 --clustering-policy NoCluster '
                 '--high-availability Disabled --minimum-tls-version 1.2 --eviction-policy NoEviction '
                 '--access-keys-auth Enabled --public-network-access Enabled', checks=[
                     self.check('name', 'default'),
                     self.check('provisioningState', 'Succeeded'),
                 ])

    def _prepare_oss_migration(self):
        self.cmd('redis create -g {rg} -n {source_redis} --location {location} '
                 '--sku Basic --vm-size C0 --minimum-tls-version 1.2', checks=[
                     self.check('provisioningState', 'Succeeded'),
                 ])
        self._create_target()
        self.kwargs.update({
            'source_id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Cache/redis/{}'.format(
                self.get_subscription_id(), self.kwargs['rg'], self.kwargs['source_redis']),
            'target_id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Cache/redisEnterprise/{}'.format(
                self.get_subscription_id(), self.kwargs['rg'], self.kwargs['cluster']),
        })
        self.cmd('redisenterprise migration validate -g {rg} --cluster-name {cluster} '
                 '--source-resource-id {source_id} --skip-data-migration true', checks=[
                     self.check('isValid', True),
                     self.check('length(errors[].disparities[])', 0),
                     self.check('length(warnings[].disparities[])', 0),
                 ])

    def _assert_migration_timestamps(self, properties, rollback_eligible):
        created = datetime.fromisoformat(properties['creationTime'].replace('Z', '+00:00'))
        modified = datetime.fromisoformat(properties['lastModifiedTime'].replace('Z', '+00:00'))
        self.assertGreaterEqual(modified, created)
        if rollback_eligible:
            deadline = datetime.fromisoformat(properties['rollbackEligibleUntil'].replace('Z', '+00:00'))
            self.assertGreater(deadline, modified)
        else:
            self.assertIsNone(properties.get('rollbackEligibleUntil'))

    def _start_migration(self, no_wait=False):
        command = ('redisenterprise migration start -g {rg} --cluster-name {cluster} '
                   '--source-resource-id {source_id} --skip-data-migration true '
                   '--switch-dns true --force-migrate true')
        self.cmd(command + (' --no-wait' if no_wait else ''))
        self.cmd('redisenterprise migration wait -g {rg} --cluster-name {cluster} '
                 '--custom "properties.provisioningState==\'Succeeded\'" --timeout 1800 --interval 10')
        migration = self.cmd('redisenterprise migration show -g {rg} --cluster-name {cluster}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.sourceType', 'AzureCacheForRedis'),
            self.check('properties.sourceResourceId', '{source_id}', case_sensitive=False),
            self.check('properties.targetResourceId', '{target_id}', case_sensitive=False),
            self.check('properties.skipDataMigration', True),
            self.check('properties.switchDns', True),
        ]).get_output_in_json()
        self._assert_migration_timestamps(migration['properties'], rollback_eligible=True)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-undo-', location='eastus2euap')
    def test_redisenterprise_migration_rollback(self, resource_group):
        self._prepare_oss_migration()
        self._start_migration(no_wait=True)
        self.cmd('redisenterprise migration list -g {rg} --cluster-name {cluster}', checks=[
            self.check('length(@)', 1),
            self.check('[0].properties.sourceResourceId', '{source_id}', case_sensitive=False),
            self.check('[0].properties.provisioningState', 'Succeeded'),
        ])
        self.cmd('redisenterprise migration undo -g {rg} --cluster-name {cluster} --rollback-reason testing')
        migration = self.cmd('redisenterprise migration show -g {rg} --cluster-name {cluster}', checks=[
            self.check('properties.provisioningState', 'Cancelled'),
            self.check('properties.sourceResourceId', '{source_id}', case_sensitive=False),
            self.check('properties.targetResourceId', '{target_id}', case_sensitive=False),
        ]).get_output_in_json()
        self._assert_migration_timestamps(migration['properties'], rollback_eligible=False)
        self.cmd('redis show -g {rg} -n {source_redis}', checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-unlink-', location='eastus2euap')
    def test_redisenterprise_migration_unlink(self, resource_group):
        self._prepare_oss_migration()
        self._start_migration()
        for command in (
                'redisenterprise migration unlink-migrated-endpoint -g {rg} --cluster-name {cluster}',
                'redisenterprise unlink-migrated-endpoint -g {rg} --cluster-name {cluster}'):
            with self.assertRaises(HttpResponseError) as error:
                self.cmd(command)
            self.assertEqual(error.exception.status_code, 400)
            self.assertEqual(error.exception.error.code, 'BadRequest')
        # Unlink is allowed only after the migrated OSS source has been deleted.
        self.cmd('redis delete -g {rg} -n {source_redis} -y')
        self.cmd('redisenterprise migration unlink-migrated-endpoint -g {rg} --cluster-name {cluster} '
                 '--no-wait')
        self.cmd('redisenterprise migration wait -g {rg} --cluster-name {cluster} '
                 '--custom "properties.provisioningState==\'Unlinked\'" --timeout 1800 --interval 10')
        migration = self.cmd('redisenterprise migration show -g {rg} --cluster-name {cluster}', checks=[
            self.check('properties.provisioningState', 'Unlinked'),
            self.check('properties.sourceType', 'AzureCacheForRedis'),
            self.check('properties.targetResourceId', '{target_id}', case_sensitive=False),
        ]).get_output_in_json()
        self._assert_migration_timestamps(migration['properties'], rollback_eligible=False)
        self.cmd('redisenterprise database show -g {rg} --cluster-name {cluster}', checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-acre-', location='eastus2euap')
    def test_redisenterprise_cluster_unlink(self, resource_group):
        self.cmd('redisenterprise create -g {rg} --cluster-name {cluster} --location {location} '
                 '--sku Enterprise_E1 --capacity 2 --clustering-policy EnterpriseCluster '
                 '--access-keys-auth Enabled --public-network-access Enabled', checks=[
                     self.check('provisioningState', 'Succeeded'),
                 ])
        original = self.cmd('redisenterprise show -g {rg} --cluster-name {cluster}', checks=[
            self.check('hostName', '{cluster}.{location}.redisenterprise.cache.azure.net'),
        ]).get_output_in_json()
        self.kwargs['original_host'] = original['hostName']
        migrated = self.cmd('redisenterprise update -g {rg} --cluster-name {cluster} '
                            '--sku Balanced_B1 --tags amr-migration-data-preserve=false', checks=[
                                self.check('sku.name', 'Balanced_B1'),
                                self.check('provisioningState', 'Succeeded'),
                                self.check('hostName', '{cluster}.{location}.redis.azure.net'),
                                self.check('migratedEndpoint', '{original_host}:10000'),
                            ]).get_output_in_json()
        self.kwargs['migrated_host'] = migrated['hostName']
        self.cmd('redisenterprise unlink-migrated-endpoint -g {rg} --cluster-name {cluster}')
        self.cmd('redisenterprise show -g {rg} --cluster-name {cluster}', checks=[
            self.check('sku.name', 'Balanced_B1'),
            self.check('provisioningState', 'Succeeded'),
            self.check("migratedEndpoint || ''", ''),
            self.check('hostName', '{migrated_host}'),
        ])
        self.cmd('redisenterprise database show -g {rg} --cluster-name {cluster}', checks=[
            self.check('provisioningState', 'Succeeded'),
        ])
