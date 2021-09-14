# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
TestRG = 'azclitest-rg'
TestWebApp = 'azclitest-wa'
TestSpringCloudService = 'azclitest-sc-service'
TestSpringCloudApp = 'azclitest-sc-app'
TestSpringCloudDeployment = 'azclitest-sc-deployment'

TestPostgresServer = 'azclitest-pg-server'
TestPostgresDB = 'azclitest-pg-db'
TestFlexiblePostgresServer = 'azclitest-fpg-server'
TestFlexiblePostgresDB = 'azclitest-fpg-db'
TestMysqlServer = 'azclitest-ms-server'
TestMysqlDB = 'azclitest-ms-db'
TestMysqlFlexibleServer = 'azclitest-msf-server'
TestMysqlFlexibleDB = 'azclitest-msf-db'
TestSqlServer = 'azclitest-sql-server'
TestSqlDB = 'azclitest-sql-db'

TestCosmosAccount = 'azclitest-cm-account'
TestCosmosCassandraSpace = 'azclitest-cm-cas-space'
TestCosmosGremlinDB = 'azclitest-cm-gre-db'
TestCosmosGremlinGraph = 'azclitest-cm-gre-graph'
TestCosmosMongoDB = 'azclitest-cm-mon-db'
TestCosmosSqlDB = 'azclitest-cm-sql-db'
TestCosmosTableDB = 'azclitest-cm-tbl-db'

TestStorageAccount = 'azclitest-sa'
TestKeyVault = 'azclitest-kv'
TestEventHubNamespace = 'azclitest-ns'
TestAppConfig = 'azclitest-ac'


def _prepare_webapp():
    pass

def _prepare_springcloud():
    pass

def _prepare_postgres():
    pass

def _prepare_flexible_postgres():
    pass

def _prepare_keyvault():
    pass

def _prepare_cosmos_cassandra():
    pass

def _prepare_cosmos_gremlin():
    pass

def _prepare_cosmos_mongo():
    pass

def _prepare_cosmos_sql():
    pass

def _prepare_cosmos_table():
    pass

def _prepare_flexible_cosmos_sql():
    pass

def _prepare_mysql_flexible():
    pass

def _prepare_mysql_flexible():
    pass

def _prepare_mysql():
    pass

def _prepare_storage_blob():
    pass

def _prepare_storage_queue():
    pass

def _prepare_storage_file():
    pass

def _prepare_storage_table():
    pass


class WebAppConnectionScenarioTest(ScenarioTest):
    plan_resource_type = 'Microsoft.Codespaces/plans'
    default_location = 'westus2'
    rg_name_prefix = 'azclitest_'

    test_resource_group = 'azclitest_rg'

    
    @ResourceGroupPreparer(name_prefix='azclitest_', location='eastus')
    def test_webapp_storageblob_e2e(self, resource_group):
        self.kwargs.update({
            'plan': 'azclitest-plan',
            'webapp': 'azclitest-storage-app',
            'storage': 'azclitest-account'
        })

        # prepare webapp
        self.cmd('appservice plan create -g {rg} -n {plan}')
        self.cmd('webapp create -g {rg} -p {plan} -n {webapp}')

        # prepare storage
        self.cmd('storage account create -g {rg} -n {storage}')

        # create connection
        self.cmd('webapp connection create storage-blob --target-id ')