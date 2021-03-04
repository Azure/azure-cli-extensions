# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements
from azure.cli.core.commands import CliCommandType
from azext_cosmosdb_preview._client_factory import (
    cf_db_accounts,
    cf_restorable_database_accounts,
    cf_restorable_sql_databases,
    cf_restorable_sql_containers,
    cf_restorable_sql_resources,
    cf_restorable_mongodb_databases,
    cf_restorable_mongodb_collections,
    cf_restorable_mongodb_resources,
    cf_sql_resources,
    cf_cassandra_cluster,
    cf_cassandra_data_center
)


def load_command_table(self, _):
    cosmosdb_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#DatabaseAccountsOperations.{}',
        client_factory=cf_db_accounts)

    cosmosdb_restorable_database_accounts_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableDatabaseAccountsOperations.{}',
        client_factory=cf_restorable_database_accounts)

    cosmosdb_restorable_sql_databases_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableSqlDatabasesOperations.{}',
        client_factory=cf_restorable_sql_databases)

    cosmosdb_restorable_sql_containers_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableSqlContainersOperations.{}',
        client_factory=cf_restorable_sql_containers)

    cosmosdb_restorable_sql_resources_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableSqlResourcesOperations.{}',
        client_factory=cf_restorable_sql_resources)

    cosmosdb_restorable_mongodb_databases_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableMongodbDatabasesOperations.{}',
        client_factory=cf_restorable_mongodb_databases)

    cosmosdb_restorable_mongodb_collections_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableMongodbCollectionsOperations.{}',
        client_factory=cf_restorable_mongodb_collections)

    cosmosdb_restorable_mongodb_resources_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableMongodbResourcesOperations.{}',
        client_factory=cf_restorable_mongodb_resources)

    cosmosdb_rbac_sql_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#SqlResourcesOperations.{}',
        client_factory=cf_sql_resources)

    cosmosdb_managed_cassandra_cluster_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#CassandraClusterOperations.{}',
        client_factory=cf_cassandra_cluster)

    cosmosdb_managed_cassandra_datacenter_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#CassandraDataCenterOperations.{}',
        client_factory=cf_cassandra_data_center)

    with self.command_group('cosmosdb restorable-database-account', cosmosdb_restorable_database_accounts_sdk, client_factory=cf_restorable_database_accounts, is_preview=True) as g:
        g.show_command('show', 'get_by_location')
        g.custom_command('list', 'cli_cosmosdb_restorable_database_account_list')

    with self.command_group('cosmosdb', cosmosdb_sdk, client_factory=cf_db_accounts) as g:
        g.show_command('show', 'get')
        g.custom_command('restore', 'cli_cosmosdb_restore', is_preview=True)
        g.custom_command('create', 'cli_cosmosdb_create')
        g.custom_command('update', 'cli_cosmosdb_update')
        g.custom_command('list', 'cli_cosmosdb_list')

    with self.command_group('cosmosdb sql restorable-database', cosmosdb_restorable_sql_databases_sdk, client_factory=cf_restorable_sql_databases, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb sql restorable-container', cosmosdb_restorable_sql_containers_sdk, client_factory=cf_restorable_sql_containers, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb sql restorable-resource', cosmosdb_restorable_sql_resources_sdk, client_factory=cf_restorable_sql_resources, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb mongodb restorable-database', cosmosdb_restorable_mongodb_databases_sdk, client_factory=cf_restorable_mongodb_databases, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb mongodb restorable-collection', cosmosdb_restorable_mongodb_collections_sdk, client_factory=cf_restorable_mongodb_collections, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb mongodb restorable-resource', cosmosdb_restorable_mongodb_resources_sdk, client_factory=cf_restorable_mongodb_resources, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb sql role definition', cosmosdb_rbac_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('create', 'cli_cosmosdb_sql_role_definition_create')
        g.custom_command('update', 'cli_cosmosdb_sql_role_definition_update')
        g.custom_command('exists', 'cli_cosmosdb_sql_role_definition_exists')
        g.command('list', 'list_sql_role_definitions')
        g.show_command('show', 'get_sql_role_definition')
        g.command('delete', 'delete_sql_role_definition', confirmation=True)

    with self.command_group('cosmosdb sql role assignment', cosmosdb_rbac_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('create', 'cli_cosmosdb_sql_role_assignment_create')
        g.custom_command('update', 'cli_cosmosdb_sql_role_assignment_update')
        g.custom_command('exists', 'cli_cosmosdb_sql_role_assignment_exists')
        g.command('list', 'list_sql_role_assignments')
        g.show_command('show', 'get_sql_role_assignment')
        g.command('delete', 'delete_sql_role_assignment', confirmation=True)

    with self.command_group('managed-cassandra cluster', cosmosdb_managed_cassandra_cluster_sdk, client_factory=cf_cassandra_cluster, is_preview=True) as g:
        g.custom_command('create', 'cli_cosmosdb_managed_cassandra_cluster_create')
        g.custom_command('update', 'cli_cosmosdb_managed_cassandra_cluster_update')
        g.custom_command('node-status', 'cli_cosmosdb_managed_cassandra_fetch_node_status')
        g.custom_command('list', 'cli_cosmosdb_managed_cassandra_cluster_list')
        g.show_command('show', 'get')
        g.command('delete', 'delete', confirmation=True)

    with self.command_group('managed-cassandra datacenter', cosmosdb_managed_cassandra_datacenter_sdk, client_factory=cf_cassandra_data_center, is_preview=True) as g:
        g.custom_command('create', 'cli_cosmosdb_managed_cassandra_datacenter_create')
        g.custom_command('update', 'cli_cosmosdb_managed_cassandra_datacenter_update')
        g.command('list', 'list_data_centers_method')
        g.show_command('show', 'get')
        g.command('delete', 'delete', confirmation=True)
