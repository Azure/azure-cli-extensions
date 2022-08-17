# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer
from .example_steps import step_create
from .example_steps import step_show
from .example_steps import step_database_show
from .example_steps import step_database_list
from .example_steps import step_database_list_keys
from .example_steps import step_database_regenerate_key
from .example_steps import step_delete
from .example_steps import step_database_create
from .example_steps import step_database_delete
from .example_steps import step_database_force_unlink

from .. import (
    raise_if,
    calc_coverage
)


# Testcase: scenario1
def call_scenario1(test, rg):
    from ....tests.latest import test_redisenterprise_scenario as g
    g.setup_scenario1(test)
    step_create(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg}"),
        test.check("clientProtocol", "Encrypted"),
        test.check("clusteringPolicy", "EnterpriseCluster"),
        test.check("evictionPolicy", "NoEviction"),
        test.check("length(modules)", 3),
        test.check("port", 10000),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise/databases")
    ])
    step_show(test, checks=[
        test.check("name", "{cluster}"),
        test.check("resourceGroup", "{rg}"),
        test.check("location", "East US"),
        test.check("sku.name", "Enterprise_E20"),
        test.check("sku.capacity", 4),
        test.check("tags.tag1", "value1"),
        test.check("zones", ["1", "2", "3"]),
        test.check("minimumTlsVersion", "1.2"),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise"),
        test.check("databases[0].name", "default"),
        test.check("databases[0].resourceGroup", "{rg}"),
        test.check("databases[0].clientProtocol", "Encrypted"),
        test.check("databases[0].clusteringPolicy", "EnterpriseCluster"),
        test.check("databases[0].evictionPolicy", "NoEviction"),
        test.check("length(databases[0].modules)", 3),
        test.check("databases[0].port", 10000),
        test.check("databases[0].provisioningState", "Succeeded"),
        test.check("databases[0].resourceState", "Running"),
        test.check("databases[0].type", "Microsoft.Cache/redisEnterprise/databases")
    ])
    g.step_list(test, checks=[])
    g.step_list2(test, checks=[
        test.check("length(@)", 1)
    ])
    step_database_show(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg}"),
        test.check("clientProtocol", "Encrypted"),
        test.check("clusteringPolicy", "EnterpriseCluster"),
        test.check("evictionPolicy", "NoEviction"),
        test.check("port", 10000),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise/databases")
    ])
    step_database_list(test, checks=[
        test.check("length(@)", 1)
    ])
    step_database_list_keys(test, checks=[])
    step_database_regenerate_key(test, checks=[])
    step_delete(test, checks=[])
    g.cleanup_scenario1(test)


# Test class for scenario1
class Redisenterprisescenario1Test(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(Redisenterprisescenario1Test, self).__init__(*args, **kwargs)

        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-cache1-', length=21)
        })

    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-rg1-', key='rg', parameter_name='rg',
                           location='eastus', random_name_length=34)
    def test_redisenterprise_scenario1(self, rg):
        call_scenario1(self, rg)
        calc_coverage(__file__)
        raise_if()


# Testcase: scenario2
def call_scenario2(test):
    from ....tests.latest import test_redisenterprise_scenario as g
    g.setup_scenario2(test)
    step_create(test, checks=[
        test.check("name", "{cluster}"),
        test.check("resourceGroup", "{rg}"),
        test.check("location", "East US"),
        test.check("sku.name", "EnterpriseFlash_F300"),
        test.check("sku.capacity", 3),
        test.check("tags.tag1", "value1"),
        test.check("zones", None),
        test.check("minimumTlsVersion", "1.2"),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise")
    ])
    step_show(test,checks=[
        test.check("name", "{cluster}"),
        test.check("resourceGroup", "{rg}"),
        test.check("location", "East US"),
        test.check("sku.name", "EnterpriseFlash_F300"),
        test.check("sku.capacity", 3),
        test.check("tags.tag1", "value1"),
        test.check("zones", None),
        test.check("minimumTlsVersion", "1.2"),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise"),
        test.check("length(databases)", 0),
    ])
    g.step_list(test, checks=[])
    g.step_list2(test, checks=[
        test.check("length(@)", 1)
    ])
    step_database_create(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg}"),
        test.check("clientProtocol", "Plaintext"),
        test.check("clusteringPolicy", "OSSCluster"),
        test.check("evictionPolicy", "AllKeysLRU"),
        test.check("port", 10000),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise/databases")
    ])
    step_database_show(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg}"),
        test.check("clientProtocol", "Plaintext"),
        test.check("clusteringPolicy", "OSSCluster"),
        test.check("evictionPolicy", "AllKeysLRU"),
        test.check("port", 10000),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise/databases")
    ])
    step_database_list(test, checks=[
        test.check("length(@)", 1)
    ])
    step_database_list_keys(test, checks=[])
    step_database_regenerate_key(test, checks=[])
    step_database_delete(test, checks=[])
    step_delete(test, checks=[])
    g.cleanup_scenario2(test)


# Test class for scenario2
class Redisenterprisescenario2Test(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(Redisenterprisescenario2Test, self).__init__(*args, **kwargs)

        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-cache2-', length=21),
            'no_database': True
        })

    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-rg2-', key='rg', parameter_name='rg',
                           location='eastus', random_name_length=34)
    def test_redisenterprise_scenario2(self):
        call_scenario2(self)
        calc_coverage(__file__)
        raise_if()

# Testcase: scenario3. Testing active geo-replication scenarios
def call_scenario3(test):
    from ....tests.latest import test_redisenterprise_scenario as g
    # Create first georeplicated cache
    step_create(test, checks=[
        test.check("name", "{cluster31}"),
        test.check("resourceGroup", "{rg31}"),
        test.check("sku.name", "EnterpriseFlash_F300"),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise"),
    ], cache_num=1)
    step_database_create(test, checks=[ 
        test.check("clientProtocol", "Encrypted"),
        test.check("evictionPolicy", "NoEviction"),
        test.check("clusteringPolicy", "EnterpriseCluster"),
        test.check("geoReplication.groupNickname", "groupName"),
        test.check("geoReplication.linkedDatabases[0].id", "/subscriptions/{subscription}/resourceGroups/{rg31}/providers/Microsoft.Cache/redisEnterprise/{cluster31}/databases/{database}"),
    ])
    # Create second georeplicated cache
    step_create(test, checks=[
        test.check("name", "default"),
        test.check("resourceGroup", "{rg32}"),
        test.check("provisioningState", "Succeeded"),
        test.check("resourceState", "Running"),
        test.check("type", "Microsoft.Cache/redisEnterprise/databases"),
        test.check("clientProtocol", "Encrypted"),
        test.check("evictionPolicy", "NoEviction"),
        test.check("clusteringPolicy", "EnterpriseCluster"),
        test.check("geoReplication.groupNickname", "groupName"),
        test.check("geoReplication.linkedDatabases[0].id", "/subscriptions/{subscription}/resourceGroups/{rg31}/providers/Microsoft.Cache/redisEnterprise/{cluster31}/databases/{database}"),
        test.check("geoReplication.linkedDatabases[1].id", "/subscriptions/{subscription}/resourceGroups/{rg32}/providers/Microsoft.Cache/redisEnterprise/{cluster32}/databases/{database}"),
    ], cache_num=2)
    # Force unlink database 1 from active geo-replication group
    step_database_force_unlink(test, checks=[])
    # Check if worked from database 2
    step_show(test, checks=[
        test.check("length(databases[0].geoReplication.linkedDatabases)", "1")
    ])
    # placeholders for cleanup
    step_delete(test, checks=[])


# Test class for scenario3
class Redisenterprisescenario3Test(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(Redisenterprisescenario3Test, self).__init__(*args, **kwargs)

        self.kwargs.update({
            'subscription': self.get_subscription_id(),
            'cluster31': self.create_random_name(prefix='clitest-cache31-', length=21),
            'cluster32': self.create_random_name(prefix='clitest-cache32-', length=21),
            'geo-replication': True,
            'database': 'default',
        }) 
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-rg31-', key='rg31', parameter_name='rg31',
                           location='eastus', random_name_length=34)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-rg32-', key='rg32', parameter_name='rg32',
                           location='westus', random_name_length=34)
    def test_redisenterprise_scenario3(self):
        call_scenario3(self)
        calc_coverage(__file__)
        raise_if()