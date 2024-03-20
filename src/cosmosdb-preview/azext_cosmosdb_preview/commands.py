# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements
from azure.cli.core.commands import CliCommandType
from azext_cosmosdb_preview._client_factory import (
    cf_cassandra_cluster,
    cf_cassandra_data_center,
    cf_service,
    cf_mongo_db_resources,
    cf_sql_resources,
    cf_db_accounts,
    cf_gremlin_resources,
    cf_table_resources,
    cf_restorable_sql_containers,
    cf_restorable_mongodb_collections,
    cf_restorable_gremlin_databases,
    cf_restorable_gremlin_graphs,
    cf_restorable_gremlin_resources,
    cf_restorable_tables,
    cf_restorable_table_resources,
    cf_restorable_database_accounts,
    cf_data_transfer_job,
    cf_mongo_cluster_job
)


def load_command_table(self, _):
    cosmosdb_service_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#ServiceOperations.{}',
        client_factory=cf_service)

    cosmosdb_managed_cassandra_cluster_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#CassandraClustersOperations.{}',
        client_factory=cf_cassandra_cluster)

    cosmosdb_managed_cassandra_datacenter_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#CassandraDataCentersOperations.{}',
        client_factory=cf_cassandra_data_center)

    cosmosdb_rbac_mongo_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#MongoDBResourcesOperations.{}',
        client_factory=cf_mongo_db_resources)

    cosmosdb_sql_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.cosmosdb.operations#SqlResourcesOperations.{}',
        client_factory=cf_sql_resources)

    with self.command_group('managed-cassandra cluster', cosmosdb_managed_cassandra_cluster_sdk, client_factory=cf_cassandra_cluster) as g:
        g.custom_command('create', 'cli_cosmosdb_managed_cassandra_cluster_create', supports_no_wait=True)
        g.custom_command('update', 'cli_cosmosdb_managed_cassandra_cluster_update', supports_no_wait=True)
        g.custom_command('backup list', 'cli_cosmosdb_managed_cassandra_cluster_list_backup', is_preview=True)
        g.custom_command('backup show', 'cli_cosmosdb_managed_cassandra_cluster_show_backup', is_preview=True)
        g.custom_command('list', 'cli_cosmosdb_managed_cassandra_cluster_list')
        g.show_command('show', 'get')
        g.command('delete', 'begin_delete', confirmation=True, supports_no_wait=True)
        g.custom_command('deallocate', 'cli_cosmosdb_managed_cassandra_cluster_deallocate', supports_no_wait=True, confirmation=True)

    with self.command_group('managed-cassandra datacenter', cosmosdb_managed_cassandra_datacenter_sdk, client_factory=cf_cassandra_data_center) as g:
        g.custom_command('create', 'cli_cosmosdb_managed_cassandra_datacenter_create', supports_no_wait=True)
        g.custom_command('update', 'cli_cosmosdb_managed_cassandra_datacenter_update', supports_no_wait=True)
        g.command('list', 'list')
        g.show_command('show', 'get')
        g.command('delete', 'begin_delete', confirmation=True, supports_no_wait=True)

    with self.command_group('cosmosdb service', cosmosdb_service_sdk, client_factory=cf_service, is_preview=True) as g:
        g.custom_command('create', 'cli_cosmosdb_service_create', supports_no_wait=True)
        g.custom_command('update', 'cli_cosmosdb_service_update', supports_no_wait=True)
        g.command('list', 'list')
        g.show_command('show', 'get')
        g.command('delete', 'begin_delete', confirmation=True, supports_no_wait=True)

    with self.command_group('cosmosdb mongodb role definition', cosmosdb_rbac_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('create', 'cli_cosmosdb_mongo_role_definition_create')
        g.custom_command('update', 'cli_cosmosdb_mongo_role_definition_update')
        g.custom_command('exists', 'cli_cosmosdb_mongo_role_definition_exists')
        g.command('list', 'list_mongo_role_definitions')
        g.show_command('show', 'get_mongo_role_definition')
        g.command('delete', 'begin_delete_mongo_role_definition', confirmation=True)

    with self.command_group('cosmosdb mongodb user definition', cosmosdb_rbac_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('create', 'cli_cosmosdb_mongo_user_definition_create')
        g.custom_command('update', 'cli_cosmosdb_mongo_user_definition_update')
        g.custom_command('exists', 'cli_cosmosdb_mongo_user_definition_exists')
        g.command('list', 'list_mongo_user_definitions')
        g.show_command('show', 'get_mongo_user_definition')
        g.command('delete', 'begin_delete_mongo_user_definition', confirmation=True)

    with self.command_group('cosmosdb sql container', cosmosdb_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('create', 'cli_cosmosdb_sql_container_create')
        g.custom_command('update', 'cli_cosmosdb_sql_container_update')

    # restorable accounts api sdk
    cosmosdb_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#DatabaseAccountsOperations.{}',
        client_factory=cf_db_accounts)

    # restorable sql/mongodb apis sdk
    cosmosdb_restorable_sql_containers_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableSqlContainersOperations.{}',
        client_factory=cf_restorable_sql_containers)

    cosmosdb_restorable_mongodb_collections_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableMongodbCollectionsOperations.{}',
        client_factory=cf_restorable_mongodb_collections)

    # restorable gremlin apis sdk
    cosmosdb_restorable_gremlin_databases_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableGremlinDatabasesOperations.{}',
        client_factory=cf_restorable_gremlin_databases)

    cosmosdb_restorable_gremlin_graphs_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableGremlinGraphsOperations.{}',
        client_factory=cf_restorable_gremlin_graphs)

    cosmosdb_restorable_gremlin_resources_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableGremlinResourcesOperations.{}',
        client_factory=cf_restorable_gremlin_resources)

    # restorable table apis sdk
    cosmosdb_restorable_tables_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableTablesOperations.{}',
        client_factory=cf_restorable_tables)

    cosmosdb_restorable_table_resources_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#RestorableTableResourcesOperations.{}',
        client_factory=cf_restorable_table_resources)

    cosmosdb_restorable_database_accounts_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.cosmosdb.operations#RestorableDatabaseAccountsOperations.{}',
        client_factory=cf_restorable_database_accounts)

    # define commands
    # Restorable apis for sql,mongodb,gremlin and table
    # Provisioning/migrate Continuous 7 days accounts
    with self.command_group('cosmosdb', cosmosdb_sdk, client_factory=cf_db_accounts) as g:
        g.custom_command('restore', 'cli_cosmosdb_restore', is_preview=True)
        g.custom_command('create', 'cli_cosmosdb_create', is_preview=True)
        g.custom_command('update', 'cli_cosmosdb_update')
        g.custom_command('list', 'cli_cosmosdb_list')
        g.show_command('show', 'get')

    with self.command_group('cosmosdb sql restorable-container', cosmosdb_restorable_sql_containers_sdk, client_factory=cf_restorable_sql_containers, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb mongodb restorable-collection', cosmosdb_restorable_mongodb_collections_sdk, client_factory=cf_restorable_mongodb_collections, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb gremlin restorable-database', cosmosdb_restorable_gremlin_databases_sdk, client_factory=cf_restorable_gremlin_databases, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb gremlin restorable-graph', cosmosdb_restorable_gremlin_graphs_sdk, client_factory=cf_restorable_gremlin_graphs, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb gremlin restorable-resource', cosmosdb_restorable_gremlin_resources_sdk, client_factory=cf_restorable_gremlin_resources, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb table restorable-table', cosmosdb_restorable_tables_sdk, client_factory=cf_restorable_tables, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb table restorable-resource', cosmosdb_restorable_table_resources_sdk, client_factory=cf_restorable_table_resources, is_preview=True) as g:
        g.command('list', 'list')

    with self.command_group('cosmosdb restorable-database-account', cosmosdb_restorable_database_accounts_sdk, client_factory=cf_restorable_database_accounts) as g:
        g.custom_show_command('show', 'cli_cosmosdb_restorable_database_account_get_by_location')
        g.custom_command('list', 'cli_cosmosdb_restorable_database_account_list')

    # Retrieve backup info for gremlin
    cosmosdb_gremlin_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.cosmosdb.operations#GremlinResourcesOperations.{}',
        client_factory=cf_gremlin_resources)

    with self.command_group('cosmosdb gremlin', cosmosdb_gremlin_sdk, client_factory=cf_gremlin_resources) as g:
        g.custom_command('retrieve-latest-backup-time', 'cli_gremlin_retrieve_latest_backup_time', is_preview=True)

    # Retrieve backup info for table
    cosmosdb_table_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.cosmosdb.operations#TableResourcesOperations.{}',
        client_factory=cf_table_resources)

    with self.command_group('cosmosdb table', cosmosdb_table_sdk, client_factory=cf_table_resources) as g:
        g.custom_command('retrieve-latest-backup-time', 'cli_table_retrieve_latest_backup_time', is_preview=True)

    # Data Transfer Service
    cosmosdb_data_transfer_job = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations._data_transfer_jobs_operations#DataTransferJobsOperations.{}',
        client_factory=cf_data_transfer_job
    )

    with self.command_group('cosmosdb dts', cosmosdb_data_transfer_job, client_factory=cf_data_transfer_job, is_preview=True, deprecate_info=self.deprecate(redirect='cosmosdb copy', hide=True)) as g:
        g.custom_command('copy', 'cosmosdb_data_transfer_copy_job')
        g.command('list', 'list_by_database_account')
        g.show_command('show', 'get')
        g.command('pause', 'pause')
        g.command('resume', 'resume')
        g.command('cancel', 'cancel')

    # Data Transfer Service
    cosmosdb_copy_job = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations._data_transfer_jobs_operations#DataTransferJobsOperations.{}',
        client_factory=cf_data_transfer_job
    )

    with self.command_group('cosmosdb copy', cosmosdb_copy_job, client_factory=cf_data_transfer_job, is_preview=True) as g:
        g.custom_command('create', 'cosmosdb_copy_job')
        g.command('list', 'list_by_database_account')
        g.show_command('show', 'get')
        g.command('pause', 'pause')
        g.command('resume', 'resume')
        g.command('cancel', 'cancel')
        g.command('complete', 'complete')

    # Merge partitions for Sql containers
    cosmosdb_sql_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.cosmosdb.operations#SqlResourcesOperations.{}',
        client_factory=cf_sql_resources)

    with self.command_group('cosmosdb sql container', cosmosdb_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('merge', 'cli_begin_list_sql_container_partition_merge', is_preview=True)

    # Merge partitions for mongodb collections
    cosmosdb_mongo_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations#MongoDBResourcesOperations.{}',
        client_factory=cf_mongo_db_resources)

    with self.command_group('cosmosdb mongodb collection', cosmosdb_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('merge', 'cli_begin_list_mongo_db_collection_partition_merge', is_preview=True)

    # Retrieve partition throughput for Sql containers
    with self.command_group('cosmosdb sql container', cosmosdb_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('retrieve-partition-throughput', 'cli_begin_retrieve_sql_container_partition_throughput', is_preview=True)

    # Merge partitions for Sql databases
    with self.command_group('cosmosdb sql database', cosmosdb_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('merge', 'cli_begin_sql_database_partition_merge', is_preview=True)

    # Merge partitions for mongodb databases
    with self.command_group('cosmosdb mongodb database', cosmosdb_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('merge', 'cli_begin_mongo_db_database_partition_merge', is_preview=True)

    # Redistribute partition throughput for Sql containers
    with self.command_group('cosmosdb sql container', cosmosdb_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('redistribute-partition-throughput', 'cli_begin_redistribute_sql_container_partition_throughput', is_preview=True)

    # Retrieve partition throughput for Mongo collection
    with self.command_group('cosmosdb mongodb collection', cosmosdb_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('retrieve-partition-throughput', 'cli_begin_retrieve_mongo_container_partition_throughput', is_preview=True)

    # Redistribute partition throughput for Mongo collection
    with self.command_group('cosmosdb mongodb collection', cosmosdb_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('redistribute-partition-throughput', 'cli_begin_redistribute_mongo_container_partition_throughput', is_preview=True)

    with self.command_group('cosmosdb sql database', cosmosdb_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('restore', 'cli_cosmosdb_sql_database_restore', is_preview=True)

    with self.command_group('cosmosdb sql container', cosmosdb_sql_sdk, client_factory=cf_sql_resources) as g:
        g.custom_command('restore', 'cli_cosmosdb_sql_container_restore', is_preview=True)

    with self.command_group('cosmosdb mongodb database', cosmosdb_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('restore', 'cli_cosmosdb_mongodb_database_restore', is_preview=True)

    with self.command_group('cosmosdb mongodb collection', cosmosdb_mongo_sdk, client_factory=cf_mongo_db_resources) as g:
        g.custom_command('restore', 'cli_cosmosdb_mongodb_collection_restore', is_preview=True)

    with self.command_group('cosmosdb gremlin database', cosmosdb_gremlin_sdk, client_factory=cf_gremlin_resources) as g:
        g.custom_command('restore', 'cli_cosmosdb_gremlin_database_restore', is_preview=True)

    with self.command_group('cosmosdb gremlin graph', cosmosdb_gremlin_sdk, client_factory=cf_gremlin_resources) as g:
        g.custom_command('restore', 'cli_cosmosdb_gremlin_graph_restore', is_preview=True)

    with self.command_group('cosmosdb table', cosmosdb_table_sdk, client_factory=cf_table_resources) as g:
        g.custom_command('restore', 'cli_cosmosdb_table_restore', is_preview=True)

    # Mongo cluster operations
    cosmosdb_mongocluster_sdk = CliCommandType(
        operations_tmpl='azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.operations.#MongoClustersOperations.{}',
        client_factory=cf_mongo_cluster_job)

    # Mongo Cluster create operations
    with self.command_group('cosmosdb mongocluster', cosmosdb_mongocluster_sdk, client_factory=cf_mongo_cluster_job, is_preview=True) as g:
        g.custom_command('create', 'cli_cosmosdb_mongocluster_create', is_preview=True)
        g.custom_command('update', 'cli_cosmosdb_mongocluster_update', is_preview=True)
        g.custom_command('list', 'cli_cosmosdb_mongocluster_list', is_preview=True)
        g.custom_show_command('show', 'cli_cosmosdb_mongocluster_get', is_preview=True)
        g.custom_command('delete', 'cli_cosmosdb_mongocluster_delete', confirmation=True)

    with self.command_group('cosmosdb mongocluster firewall rule', cosmosdb_mongocluster_sdk, client_factory=cf_mongo_cluster_job, is_preview=True) as g:
        g.custom_command('create', 'cli_cosmosdb_mongocluster_firewall_rule_create', is_preview=True)
        g.custom_command('update', 'cli_cosmosdb_mongocluster_firewall_rule_update', is_preview=True)
        g.custom_command('list', 'cli_cosmosdb_mongocluster_firewall_rule_list', is_preview=True)
        g.custom_show_command('show', 'cli_cosmosdb_mongocluster_firewall_rule_get', is_preview=True)
        g.custom_command('delete', 'cli_cosmosdb_mongocluster_firewall_rule_delete', confirmation=True)
