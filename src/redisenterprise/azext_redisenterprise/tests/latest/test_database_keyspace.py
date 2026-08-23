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


# Step: Create the cluster (also creates the default database without keyspace events)
@try_manual
def step_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise create '
             '--cluster-name "{cluster}" '
             '--sku "Balanced_B1" '
             '--location "centraluseuap" '
             '--public-network-access "Enabled" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Show the default database and assert the keyspace-events default
@try_manual
def step_database_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database show '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Delete the default database so it can be re-created with the new flag
@try_manual
def step_database_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database delete -y '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Create a database with --notify-keyspace-events
@try_manual
def step_database_create_with_keyspace(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database create '
             '--cluster-name "{cluster}" '
             '--client-protocol "Encrypted" '
             '--clustering-policy "EnterpriseCluster" '
             '--eviction-policy "NoEviction" '
             '--notify-keyspace-events "AKE" '
             '--port 10000 '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Delete the cluster
@try_manual
def step_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise delete -y '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


def call_keyspace_scenario(test, rg):
    step_create(test, checks=[
        test.check("name", "default"),
        test.check("provisioningState", "Succeeded"),
    ])
    # Database created implicitly by cluster create has keyspace notifications disabled.
    step_database_show(test, checks=[
        test.check("name", "default"),
        test.check("notifyKeyspaceEvents", ""),
    ])
    step_database_delete(test, checks=[])
    step_database_create_with_keyspace(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg}"),
        test.check("clientProtocol", "Encrypted"),
        test.check("clusteringPolicy", "EnterpriseCluster"),
        test.check("evictionPolicy", "NoEviction"),
        test.check("notifyKeyspaceEvents", "AKE"),
        test.check("provisioningState", "Succeeded"),
    ])
    step_database_show(test, checks=[
        test.check("name", "default"),
        test.check("notifyKeyspaceEvents", "AKE"),
    ])
    step_delete(test, checks=[])


class RedisEnterpriseKeyspaceEventsScenarioTest(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(RedisEnterpriseKeyspaceEventsScenarioTest, self).__init__(*args, **kwargs)
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-ke-', length=21),
        })

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-ke-', key='rg', parameter_name='rg',
                           location='centraluseuap', random_name_length=34)
    def test_redisenterprise_notify_keyspace_events(self, rg):
        call_keyspace_scenario(self, rg)
        calc_coverage(__file__)
        raise_if()
