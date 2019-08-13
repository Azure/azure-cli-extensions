# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azext_dms.vendored_sdks.datamigration.models import (MigrateMySqlAzureDbForMySqlSyncDatabaseInput,
                                                          MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput,
                                                          MigrateMySqlAzureDbForMySqlSyncTaskInput,
                                                          MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput,
                                                          MongoDbMigrationSettings,
                                                          MigrateOracleAzureDbPostgreSqlSyncDatabaseInput,
                                                          MigrateOracleAzureDbPostgreSqlSyncTaskInput)


def get_migrate_mysql_to_azuredbformysql_sync_input(database_options_json,
                                                    source_connection_info,
                                                    target_connection_info):
    database_options = []

    for d in database_options_json:
        database_options.append(MigrateMySqlAzureDbForMySqlSyncDatabaseInput(
            name=d.get('name', None),
            target_database_name=d.get('target_database_name', None),
            migration_setting=d.get('migrationSetting', None),
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
        database_options.append(MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput(
            name=d.get('name', None),
            target_database_name=d.get('target_database_name', None),
            migration_setting=d.get('migrationSetting', None),
            source_setting=d.get('sourceSetting', None),
            target_setting=d.get('targetSetting', None)))

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


def get_migrate_oracle_to_azuredbforpostgresql_sync_input(database_options_json,
                                                          source_connection_info,
                                                          target_connection_info):
    database_options = []

    for d in database_options_json:
        case_manipulation = d.get('caseManipulation', None)
        schema_name = d.get('schemaName', None)
        table_map = d.get('tableMap', None)

        # Check that both schemaName and tableMap are not empty
        if (not schema_name) and (not table_map):
            raise CLIError("Either schemaName or tableMap must be provided.")
        # Check that caseManipulation is not present if tableMap is provided
        if case_manipulation and table_map is not None:
            raise CLIError("When providing tableMap, caseManipulation can not be defined.")
        # Check that schemaName and tableMap are not both provided
        if schema_name and table_map:
            raise CLIError("Only provide either schemaName or tableMap to define the scope of migration. Not both.")

        database_options.append(MigrateOracleAzureDbPostgreSqlSyncDatabaseInput(
            case_manipulation=case_manipulation if case_manipulation else None,
            # This is the pipe name required for Attunity but does not need to be input by user.
            name=schema_name if schema_name else d.get('targetDatabaseName', 'CliPipeName'),
            schema_name=schema_name if schema_name else None,
            table_map=table_map if table_map else None,
            target_database_name=d.get('targetDatabaseName', None),
            migration_setting=d.get('migrationSetting', None),
            source_setting=d.get('sourceSetting', None),
            target_setting=d.get('targetSetting', None)))

    return MigrateOracleAzureDbPostgreSqlSyncTaskInput(source_connection_info=source_connection_info,
                                                       target_connection_info=target_connection_info,
                                                       selected_databases=database_options)
