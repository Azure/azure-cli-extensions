# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_dms.vendored_sdks.datamigration.models import (MigrateMySqlAzureDbForMySqlSyncDatabaseInput,
                                                          MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput,
                                                          MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseTableInput,
                                                          MigrateMySqlAzureDbForMySqlSyncTaskInput,
                                                          MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput,
                                                          MongoDbMigrationSettings)


def get_migrate_mysql_to_azuredbformysql_sync_input(database_options_json,
                                                    source_connection_info,
                                                    target_connection_info):
    database_options = []

    for d in database_options_json:
        def_migration_setting_input = {"fullLoadSubTasks": "5",
                                       "inlineLobMaxSize": "0",
                                       "limitLOBSize": "true",
                                       "lobChunkSize": "64",
                                       "lobMaxSize": "32"}
        database_options.append(MigrateMySqlAzureDbForMySqlSyncDatabaseInput(
            name=d.get('name', None),
            target_database_name=d.get('target_database_name', None),
            migration_setting=d.get('migrationSetting', def_migration_setting_input),
            source_setting=d.get('sourceSetting', None),
            target_setting=d.get('targetSetting', None)))

    return MigrateMySqlAzureDbForMySqlSyncTaskInput(source_connection_info=source_connection_info,
                                                    target_connection_info=target_connection_info,
                                                    selected_databases=database_options)


def get_migrate_postgresql_to_azuredbforpostgresql_sync_input(database_options_json,
                                                              source_connection_info,
                                                              target_connection_info):
    database_options = []

    for d in database_options_json:
        s_t = d.get('selectedTables', None)
        t = None if s_t is None else [MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseTableInput(name=t) for t in s_t]
        database_options.append(MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput(
            name=d.get('name', None),
            target_database_name=d.get('target_database_name', None),
            migration_setting=d.get('migrationSetting', None),
            source_setting=d.get('sourceSetting', None),
            target_setting=d.get('targetSetting', None),
            selected_tables=t))

    return MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput(source_connection_info=source_connection_info,
                                                              target_connection_info=target_connection_info,
                                                              selected_databases=database_options)


def get_mongo_to_mongo_input(database_options_json,
                             source_connection_info,
                             target_connection_info):
    if 'databases' not in database_options_json or database_options_json.get('databases') is None:
        raise ValueError("'databases' must be present in 'database_options_json'.")

    if 'replication' not in database_options_json or database_options_json.get('replication') is None:
        raise ValueError("'replication' must be present and not null in 'database_options_json'.")

    return MongoDbMigrationSettings(databases=database_options_json['databases'],
                                    source=source_connection_info,
                                    target=target_connection_info,
                                    boost_rus=database_options_json.get('boostRUs', 0),
                                    replication=database_options_json['replication'],
                                    throttling=database_options_json.get('throttling', None))
