# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.testsdk import (
    ScenarioTest,
    ResourceGroupPreparer,
    live_only
)
from azext_connection.manual._resource_config import (
    RESOURCE,
    SOURCE_RESOURCES,
    TARGET_RESOURCES
)


class WebAppConnectionScenarioTest(ScenarioTest):

    def test_webapp_appconfig_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-config-app',
            'app_config': 'servicelinker-app-configuration'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create app-config --source-id {} --target-id {} --system-identity --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_cosmoscassandra_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-win-group',
            'target_resource_group': 'servicelinker-test-win-group',
            'webapp': 'servicelinker-cassandra-cosmos-asp-app',
            'cosmos_account_name': 'servicelinker-cassandra-cosmos',
            'key_space': 'coredb'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create cosmos-cassandra --source-id {} --target-id {} --system-identity --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_cosmosgremlin_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-win-group',
            'target_resource_group': 'servicelinker-test-win-group',
            'webapp': 'servicelinker-gremlin-cosmos-asp-app',
            'cosmos_account_name': 'servicelinker-cassandra-cosmos',
            'db_name': 'coreDB',
            'graph_name': 'MyItem'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        # TODO: provide secret user and pw
        self.cmd('webapp connection create cosmos-gremlin --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_cosmosmongo_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-win-group',
            'target_resource_group': 'servicelinker-test-win-group',
            'webapp': 'servicelinker-mongo-cosmos-asp-app',
            'cosmos_account_name': 'servicelinker-mongo-cosmos',
            'db_name': 'coreDB'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create cosmos-mongo --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_cosmossql_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-win-group',
            'target_resource_group': 'servicelinker-test-win-group',
            'webapp': 'servicelinker-sql-cosmos-asp-app',
            'cosmos_account_name': 'servicelinker-sql-cosmos',
            'db_name': 'coreDB'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create cosmos-sql --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_cosmostable_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-win-group',
            'target_resource_group': 'servicelinker-test-win-group',
            'webapp': 'servicelinker-table-cosmos-asp-app',
            'cosmos_account_name': 'servicelinker-table-cosmos',
            'table_name': 'MyItem'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create cosmos-table --source-id {} --target-id {} --system-identity --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_eventhub_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-eventhub-app',
            'namespace': 'servicelinkertesteventhub' 
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create eventhub --source-id {} --target-id {} --system-identity --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_flexiblepostgres_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-flexiblepostgresql-app',
            'postgres': 'servicelinker-flexiblepostgresql',
            'database': 'postgres'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        # TODO: provide secret user and pw
        self.cmd('webapp connection create flexible-postgres --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_keyvault_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-keyvault-app',
            'vault_name': 'servicelinker-test-kv'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create keyvault --source-id {} --target-id {} --system-identity --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_mysql_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-mysql-app',
            'server_name': 'servicelinker-mysql',
            'db_name': 'mysqlDB'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        # TODO: provide secret user and pw
        self.cmd('webapp connection create mysql --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_mysqlflexible_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-flexiblemysql-app',
            'server_name': 'servicelinker-flexible-mysql',
            'db_name': 'mysqlDB'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        # TODO: provide secret user and pw
        self.cmd('webapp connection create mysql-flexible --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_postgres_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-postgresql-app',
            'postgres': 'servicelinker-postgresql',
            'database': 'postgres'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        # TODO: provide secret user and pw
        self.cmd('webapp connection create postgres --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_sql_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-sql-app',
            'server_name': 'servicelinker-sql',
            'db_name': 'handler-test'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        # TODO: provide secret user and pw
        self.cmd('webapp connection create sql --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_storageblob_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-storage-app',
            'storage_account_name': 'servicelinkerteststorage'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create storage-blob --source-id {} --target-id {} --system-identity --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))
    

    def test_webapp_storagequeue_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-storage-app',
            'storage_account_name': 'servicelinkerteststorage'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create storage-queue --source-id {} --target-id {} --system-identity --client-type python'.format(source_id, target_id))
        
        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_storagefile_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-storage-app',
            'storage_account_name': 'servicelinkerteststorage'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create storage-file --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))

        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))


    def test_webapp_storagetable_e2e(self):
        self.kwargs.update({
            'subscription': get_subscription_id(self.cli_ctx),
            'source_resource_group': 'servicelinker-test-linux-group',
            'target_resource_group': 'servicelinker-test-linux-group',
            'webapp': 'servicelinker-storage-app',
            'storage_account_name': 'servicelinkerteststorage'
        })

        # prepare params
        source_id = SOURCE_RESOURCES.get(RESOURCE.WebApp).format(**self.kwargs)
        target_id = TARGET_RESOURCES.get(RESOURCE.StorageBlob).format(**self.kwargs)

        # create connection
        self.cmd('webapp connection create storage-table --source-id {} --target-id {} --secret-auth-info --client-type python'.format(source_id, target_id))

        # list connection
        connections = self.cmd(
            'webapp connection list --source-id {}'.format(source_id),
            checks = [
                self.check('length(@)', 1),
                self.check('[0].authInfo.authType', 'systemAssignedIdentity'),
                self.check('[0].clientType', 'python')
            ]
        ).get_output_in_json()
        connection_id = connections[0].get('id')

        # list configuration
        self.cmd('webapp connection list-configuration --source-id {}'.format(connection_id))

        # validate connection
        self.cmd('webapp connection validate --source-id {}'.format(connection_id))

        # show connection
        self.cmd('webapp connection show --source-id {}'.format(connection_id))

        # delete connection
        self.cmd('webapp connection delete --source-id {} --yes'.format(connection_id))