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


# Env setup
@try_manual
def setup_test_connection_scenario(test):
    pass


# Env cleanup
@try_manual
def cleanup_test_connection_scenario(test):
    pass


# Step: Create Redis Enterprise cluster with B1 SKU, public network access, and access key auth
@try_manual
def step_create_cluster_with_b1_sku(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise create '
             '--cluster-name "{cluster}" '
             '--sku "Balanced_B1" '
             '--location "centraluseuap" '
             '--tags tag1="value1" '
             '--public-network-access "Enabled" '
             '--access-keys-auth Enabled '
             '--minimum-tls-version "1.2" '
             '--client-protocol "Encrypted" '
             '--clustering-policy "EnterpriseCluster" '
             '--eviction-policy "NoEviction" '
             '--port 10000 '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Show cluster details
@try_manual
def step_show_cluster(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise show '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: List database keys
@try_manual
def step_database_list_keys(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise database list-keys '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Step: Test connection with access-key authentication
@try_manual
def step_test_connection_access_key(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise test-connection '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}" '
             '--auth "access-key"',
             checks=checks)


# Step: Delete cluster
@try_manual
def step_delete_cluster(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az redisenterprise delete -y '
             '--cluster-name "{cluster}" '
             '--resource-group "{rg}"',
             checks=checks)


# Testcase: Test Connection Scenario
def call_test_connection_scenario(test, rg):
    setup_test_connection_scenario(test)

    # Step 1: Create Redis Enterprise cluster with B1 SKU, public network access, and access keys enabled
    step_create_cluster_with_b1_sku(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg}"),
        test.check("clientProtocol", "Encrypted"),
        test.check("clusteringPolicy", "EnterpriseCluster"),
        test.check("evictionPolicy", "NoEviction"),
        test.check("accessKeysAuthentication", "Enabled"),
        test.check("port", 10000),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise/databases")
    ])

    # Step 2: Verify the cluster is created with correct settings
    step_show_cluster(test, checks=[
        test.check("name", "{cluster}"),
        test.check("resourceGroup", "{rg}"),
        test.check("location", "Central US EUAP"),
        test.check("sku.name", "Balanced_B1"),
        test.check("tags.tag1", "value1"),
        test.check("minimumTlsVersion", "1.2"),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise"),
        test.check("databases[0].accessKeysAuthentication", "Enabled"),
        test.check("databases[0].clientProtocol", "Encrypted")
    ])

    # Step 3: Verify database keys are available
    step_database_list_keys(test, checks=[
        test.exists("primaryKey"),
        test.exists("secondaryKey")
    ])

    # Step 4: Test connection using access-key authentication
    step_test_connection_access_key(test, checks=[
        test.check("connectionStatus", "Success"),
        test.check("authMethod", "access-key"),
        test.check("clusterName", "{cluster}"),
        test.check("resourceGroup", "{rg}"),
        test.check("port", 10000),
        test.check("databaseName", "default")
    ])

    # Step 5: Cleanup - delete the cluster
    step_delete_cluster(test, checks=[])

    cleanup_test_connection_scenario(test)


# Test class for test-connection scenario
class RedisEnterpriseTestConnectionScenarioTest(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(RedisEnterpriseTestConnectionScenarioTest, self).__init__(*args, **kwargs)

        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-tc-', length=21)
        })

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-tc-', key='rg', parameter_name='rg',
                           location='eastasia', random_name_length=34)
    @live_only()
    def test_redisenterprise_test_connection(self, rg):
        call_test_connection_scenario(self, rg)
        calc_coverage(__file__)
        raise_if()


