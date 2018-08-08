# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_dms.vendored_sdks.datamigration.models import (MigrationValidationOptions,
                                                          MigrateSqlServerSqlDbDatabaseInput,
                                                          MigrateMySqlAzureDbForMySqlSyncDatabaseInput,
                                                          MigrateSqlServerSqlDbTaskInput,
                                                          MigrateMySqlAzureDbForMySqlSyncTaskInput)


def get_migrate_sql_server_to_sqldb_input(database_options_json,
                                          source_connection_info,
                                          target_connection_info,
                                          enable_schema_validation,
                                          enable_data_integrity_validation,
                                          enable_query_analysis_validation):
    validation_options = MigrationValidationOptions(enable_schema_validation=enable_schema_validation,
                                                    enable_data_integrity_validation=enable_data_integrity_validation,
                                                    enable_query_analysis_validation=enable_query_analysis_validation)

    database_options = []

    for d in database_options_json:
        database_options.append(MigrateSqlServerSqlDbDatabaseInput(
            name=d.get('name', None),
            target_database_name=d.get('target_database_name', None),
            make_source_db_read_only=d.get('make_source_db_read_only', None),
            table_map=d.get('table_map', None)))

    return MigrateSqlServerSqlDbTaskInput(source_connection_info=source_connection_info,
                                          target_connection_info=target_connection_info,
                                          selected_databases=database_options,
                                          validation_options=validation_options)


def get_migrate_mysql_to_azuredbformysql_sync_input(database_options_json,
                                                    source_connection_info,
                                                    target_connection_info):
    database_options = []

    for d in database_options_json:
        database_options.append(MigrateMySqlAzureDbForMySqlSyncDatabaseInput(
            name=d.get('name', None),
            target_database_name=d.get('target_database_name', None)))

    return MigrateMySqlAzureDbForMySqlSyncTaskInput(source_connection_info=source_connection_info,
                                                    target_connection_info=target_connection_info,
                                                    selected_databases=database_options)
