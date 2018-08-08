# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.core.util import get_file_json, shell_safe_json_parse
from knack.prompting import prompt, prompt_pass
from azext_dms.vendored_sdks.datamigration.models import (Project,
                                                          SqlConnectionInfo,
                                                          MySqlConnectionInfo,
                                                          MigrateSyncCompleteCommandInput,
                                                          MigrateSqlServerSqlDbTaskProperties,
                                                          MigrateMySqlAzureDbForMySqlSyncTaskProperties,
                                                          MigrateSyncCompleteCommandProperties)
from azext_dms.scenarios import (get_migrate_sql_server_to_sqldb_input,
                                 get_migrate_mysql_to_azuredbformysql_sync_input)


# region Project
def create_or_update_project(
        client,
        project_name,
        service_name,
        resource_group_name,
        location,
        source_platform,
        target_platform,
        tags=None):

    # Validation: Test scenario eligibility
    if not determine_scenario_eligibility(source_platform, target_platform):
        raise ValueError('The provided source-platform and target-platform combination is not appropriate. \n\
           The only supported scenarios are: \n\
               1) Sql -> SqlDb \n\
               2) MySql -> AzureDbForMySql')

    # Get the data movement type
    data_movement_type = get_data_movement_type(source_platform, target_platform)

    parameters = Project(location=location,
                         source_platform=source_platform,
                         target_platform=target_platform,
                         tags=tags,
                         data_movement=data_movement_type)

    return client.create_or_update(parameters=parameters,
                                   group_name=resource_group_name,
                                   service_name=service_name,
                                   project_name=project_name)
# endregion


# region Task
def create_task(
        client,
        resource_group_name,
        service_name,
        project_name,
        task_name,
        source_platform,
        target_platform,
        source_connection_json,
        target_connection_json,
        database_options_json,
        enable_schema_validation=False,
        enable_data_integrity_validation=False,
        enable_query_analysis_validation=False):

    # Validation: Test scenario eligibility
    if not determine_scenario_eligibility(source_platform, target_platform):
        raise ValueError('The provided source-platform and target-platform combination is not appropriate. \n\
           The only supported scenarios are: \n\
               1) Sql -> SqlDb \n \
               2) MySql -> AzureDbForMySql')

    if os.path.exists(source_connection_json):
        source_connection_json = get_file_json(source_connection_json)
    else:
        source_connection_json = shell_safe_json_parse(source_connection_json)
    source_connection_info = create_connection(source_connection_json, "Source Database", source_platform)

    if os.path.exists(target_connection_json):
        target_connection_json = get_file_json(target_connection_json)
    else:
        target_connection_json = shell_safe_json_parse(target_connection_json)
    target_connection_info = create_connection(target_connection_json, "Target Database", target_platform)

    if os.path.exists(database_options_json):
        database_options_json = get_file_json(database_options_json)
    else:
        database_options_json = shell_safe_json_parse(database_options_json)

    task_properties = get_task_migration_properties(database_options_json,
                                                    source_platform,
                                                    target_platform,
                                                    source_connection_info,
                                                    target_connection_info,
                                                    enable_schema_validation,
                                                    enable_data_integrity_validation,
                                                    enable_query_analysis_validation)

    return client.create_or_update(group_name=resource_group_name,
                                   service_name=service_name,
                                   project_name=project_name,
                                   task_name=task_name,
                                   properties=task_properties)


def cutover_sync_task(
        client,
        resource_group_name,
        service_name,
        project_name,
        task_name,
        database_name):
    sync_input = MigrateSyncCompleteCommandInput(database_name=database_name)

    # 'input' is a built in function. Even though we can technically use it, it's not recommended.
    # https://stackoverflow.com/questions/20670732/is-input-a-keyword-in-python
    sync_properties_params = {'input': sync_input}
    sync_properties = MigrateSyncCompleteCommandProperties(**sync_properties_params)

    client.command(group_name=resource_group_name,
                   service_name=service_name,
                   project_name=project_name,
                   task_name=task_name,
                   parameters=sync_properties)

# endregion


# region Helper Methods
def determine_scenario_eligibility(source_raw, target_raw):
    source_type = source_raw.lower()
    target_type = target_raw.lower()

    return (source_type == "sql" and target_type == "sqldb") or \
           (source_type == "mysql" and target_type == "azuredbformysql")


# As of now, we dont expose Sql continuous migrations.
# So we'll hard code the data movement type to simplify user interaction.
# In the future, we can remove this method and add a validation in its stead.
def get_data_movement_type(source_type, target_type):
    source_type = source_type.lower()
    target_type = target_type.lower()
    oneTime = "OneTimeMigration"
    cont = "Continuous"

    if source_type == "sql" and target_type == "sqldb":
        return oneTime
    return cont


def create_connection(connection_info_json, prompt_prefix, typeOfInfo):
    typeOfInfo = typeOfInfo.lower()

    user_name = connection_info_json.get('userName', None) or prompt(prompt_prefix + 'Username: ')
    password = connection_info_json.get('password', None) or prompt_pass(msg=prompt_prefix + 'Password: ')
    server_name = connection_info_json.get('serverName', None)
    if "mysql" in typeOfInfo:
        port = connection_info_json.get('port', 3306)
        return MySqlConnectionInfo(user_name=user_name,
                                   password=password,
                                   server_name=server_name,
                                   port=port)
    data_source = connection_info_json.get('dataSource', None)
    authentication = connection_info_json.get('authentication', None)
    encrypt_connection = connection_info_json.get('encryptConnection', None)
    trust_server_certificate = connection_info_json.get('trustServerCertificate', None)
    additional_settings = connection_info_json.get('additionalSettings', None)
    return SqlConnectionInfo(user_name=user_name,
                             password=password,
                             data_source=data_source,
                             authentication=authentication,
                             encrypt_connection=encrypt_connection,
                             trust_server_certificate=trust_server_certificate,
                             additional_settings=additional_settings)


def get_task_migration_properties(
        database_options_json,
        source_raw,
        target_raw,
        source_connection_info,
        target_connection_info,
        enable_schema_validation,
        enable_data_integrity_validation,
        enable_query_analysis_validation):
    source_type = source_raw.lower()
    target_type = target_raw.lower()

    if source_type == 'sql' and target_type == 'sqldb':
        TaskProperties = MigrateSqlServerSqlDbTaskProperties
        task_input = get_migrate_sql_server_to_sqldb_input(
            database_options_json,
            source_connection_info,
            target_connection_info,
            enable_schema_validation,
            enable_data_integrity_validation,
            enable_query_analysis_validation)
    elif source_type == 'mysql' and target_type == 'azuredbformysql':
        TaskProperties = MigrateMySqlAzureDbForMySqlSyncTaskProperties
        task_input = get_migrate_mysql_to_azuredbformysql_sync_input(
            database_options_json,
            source_connection_info,
            target_connection_info)

    return TaskProperties(input=task_input)
# endregion
