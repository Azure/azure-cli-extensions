# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .. import (
    try_manual,
    raise_if,
    calc_coverage
)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# Step: Create the source Azure Cache for Redis instance to migrate from
@try_manual
def step_source_redis_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redis create '
             '--name "{source_redis}" '
             '--sku "Premium" '
             '--vm-size "P1" '
             '--location "centralindia" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Create the target Azure Managed Redis (redisenterprise) cluster
@try_manual
def step_target_cluster_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise create '
             '--cluster-name "{cluster}" '
             '--sku "Balanced_B1" '
             '--location "centralindia" '
             '--clustering-policy "NoCluster" '
             '--public-network-access "Enabled" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Validate the migration
@try_manual
def step_migration_validate(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise migration validate '
             '--cluster-name "{cluster}" '
             '--source-resource-id "{source_id}" '
             '--skip-data-migration true '
             '--force-migrate true '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Start the migration (flat source args from the custom flatten override)
@try_manual
def step_migration_start(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise migration start '
             '--cluster-name "{cluster}" '
             '--source-resource-id "{source_id}" '
             '--skip-data-migration true '
             '--switch-dns true '
             '--force-migrate true '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Wait for the migration to reach a terminal provisioning state
@try_manual
def step_migration_wait(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise migration wait '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}" '
             '--custom "properties.provisioningState==\'Succeeded\' || properties.provisioningState==\'Completed\'"',
             checks=checks)


# Step: List migrations for the cluster
@try_manual
def step_migration_list(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise migration list '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Show the migration
@try_manual
def step_migration_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise migration show '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Undo (roll back) the migration
@try_manual
def step_migration_undo(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise migration undo '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: (teardown handled by ResourceGroupPreparer)


def call_migration_scenario(test, rg):
    step_source_redis_create(test, checks=[
        test.check("name", "{source_redis}"),
        test.check("provisioningState", "Succeeded"),
    ])
    step_target_cluster_create(test, checks=[
        test.check("name", "default"),
        test.check("provisioningState", "Succeeded"),
    ])

    step_migration_validate(test, checks=[
        test.exists("isValid"),
    ])
    step_migration_start(test, checks=[
        test.check("properties.sourceType", "AzureCacheForRedis"),
        test.check("properties.sourceResourceId", "{source_id}", case_sensitive=False),
        test.check("properties.provisioningState", "Succeeded"),
    ])
    step_migration_wait(test, checks=[])
    step_migration_list(test, checks=[
        test.check("length(@)", 1),
        test.check("[0].properties.sourceType", "AzureCacheForRedis"),
        test.check("[0].properties.sourceResourceId", "{source_id}", case_sensitive=False),
    ])
    step_migration_show(test, checks=[
        test.check("properties.sourceType", "AzureCacheForRedis"),
        test.check("properties.sourceResourceId", "{source_id}", case_sensitive=False),
        test.check("properties.targetResourceId", "{target_id}", case_sensitive=False),
        test.check("properties.provisioningState", "Succeeded"),
    ])
    step_migration_undo(test, checks=[])


class RedisEnterpriseMigrationScenarioTest(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(RedisEnterpriseMigrationScenarioTest, self).__init__(*args, **kwargs)
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-mig-', length=21),
            'source_redis': self.create_random_name(prefix='clitest-src-', length=21),
        })

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-mig-', key='rg', parameter_name='rg',
                           location='centralindia', random_name_length=34)
    def test_redisenterprise_migration(self, rg):
        subscription = self.get_subscription_id()
        self.kwargs.update({
            'source_id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Cache/redis/{}'.format(
                subscription, self.kwargs['rg'], self.kwargs['source_redis']),
            'target_id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Cache/redisEnterprise/{}'.format(
                subscription, self.kwargs['rg'], self.kwargs['cluster']),
        })
        call_migration_scenario(self, rg)
        calc_coverage(__file__)
        raise_if()
