# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only

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
             '--location "centraluseuap" '
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
             '--location "centraluseuap" '
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
             '--custom "provisioningState==\'Completed\'"',
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


# Step: Delete the target cluster
@try_manual
def step_cluster_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise delete -y '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Delete the source cache
@try_manual
def step_source_redis_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redis delete -y '
             '--name "{source_redis}" '
             '--resource-group "{rg}"',
             checks=checks)


def call_migration_scenario(test, rg):
    step_source_redis_create(test, checks=[
        test.check("name", "{source_redis}"),
        test.check("provisioningState", "Succeeded"),
    ])
    step_target_cluster_create(test, checks=[
        test.check("name", "default"),
        test.check("provisioningState", "Succeeded"),
    ])
    # NOTE: `az redisenterprise migration validate` is intentionally skipped (commented out).
    # It currently fails with HTTP 400 InvalidRequestBody because the deployed Redis Enterprise
    # RP requires a `properties` envelope on the validate action body, while the swagger (and
    # therefore the generated CLI) sends a flat, ARM-correct body. This is a server-side (RP)
    # contract bug, NOT a CLI bug, tracked in ADO #38848036 (validate envelope mismatch) and
    # ADO #38847788 (validate `forceMigrate` ignored / hardcoded false). We deliberately do NOT
    # add a CLI-side workaround, since sending the wrapped body would be non-ARM-conforming and
    # would break once the RP is fixed. Re-enable this step once the RP accepts the flat body.
    # step_migration_validate(test, checks=[])
    step_migration_start(test, checks=[
        test.check("sourceType", "AzureCacheForRedis"),
        test.check("sourceResourceId", "{source_id}", case_sensitive=False),
    ])
    step_migration_wait(test, checks=[])
    step_migration_list(test, checks=[
        test.check("length(@)", 1),
        test.check("[0].sourceType", "AzureCacheForRedis"),
        test.check("[0].sourceResourceId", "{source_id}", case_sensitive=False),
    ])
    step_migration_show(test, checks=[
        test.check("sourceType", "AzureCacheForRedis"),
        test.check("sourceResourceId", "{source_id}", case_sensitive=False),
        test.check("targetResourceId", "{target_id}", case_sensitive=False),
        test.check("provisioningState", "Completed"),
    ])
    step_migration_undo(test, checks=[])
    step_cluster_delete(test, checks=[])
    step_source_redis_delete(test, checks=[])


class RedisEnterpriseMigrationScenarioTest(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(RedisEnterpriseMigrationScenarioTest, self).__init__(*args, **kwargs)
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-mig-', length=21),
            'source_redis': self.create_random_name(prefix='clitest-src-', length=21),
        })

    # Marked live_only because there is no committed playback recording yet: the live recording
    # is blocked on a transient AMR cluster provisioning failure (the `validate` step is also
    # skipped pending RP bugs #38848036 / #38847788). This mirrors test_test_connection.py.
    # Once a clean live run is recorded, remove @live_only() and commit the sanitized cassette.
    @live_only()
    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-mig-', key='rg', parameter_name='rg',
                           location='centraluseuap', random_name_length=34)
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
