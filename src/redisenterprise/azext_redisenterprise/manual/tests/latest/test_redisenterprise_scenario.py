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
from .. import (
    raise_if,
    calc_coverage
)


# Testcase: scenario1
def call_scenario1(test, rg):
    from ....tests.latest import test_redisenterprise_scenario as g
    g.setup_scenario1(test, rg)
    step_create(test, rg, checks=[
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
    step_show(test, rg, checks=[
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
    g.step_list(test, rg, checks=[])
    g.step_list2(test, rg, checks=[
        test.check("length(@)", 1)
    ])
    step_database_show(test, rg, checks=[
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
    step_database_list(test, rg, checks=[
        test.check("length(@)", 1)
    ])
    step_database_list_keys(test, rg, checks=[])
    step_database_regenerate_key(test, rg, checks=[])
    step_delete(test, rg, checks=[])
    g.cleanup_scenario1(test, rg)


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
def call_scenario2(test, rg):
    from ....tests.latest import test_redisenterprise_scenario as g
    g.setup_scenario2(test, rg)
    step_create(test, rg, checks=[
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
    step_show(test, rg, checks=[
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
    g.step_list(test, rg, checks=[])
    g.step_list2(test, rg, checks=[
        test.check("length(@)", 1)
    ])
    step_database_create(test, rg, checks=[
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
    step_database_show(test, rg, checks=[
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
    step_database_list(test, rg, checks=[
        test.check("length(@)", 1)
    ])
    step_database_list_keys(test, rg, checks=[])
    step_database_regenerate_key(test, rg, checks=[])
    step_database_delete(test, rg, checks=[])
    step_delete(test, rg, checks=[])
    g.cleanup_scenario2(test, rg)


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
    def test_redisenterprise_scenario2(self, rg):
        call_scenario2(self, rg)
        calc_coverage(__file__)
        raise_if()
