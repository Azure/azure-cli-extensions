# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from knack.prompting import prompt, prompt_pass
from azext_dms.vendored_sdks.datamigration.models import (Project,
                                                          MySqlConnectionInfo,
                                                          PostgreSqlConnectionInfo,
                                                          MigrateSyncCompleteCommandInput,
                                                          MigrateMySqlAzureDbForMySqlSyncTaskProperties,
                                                          MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties,
                                                          MigrateSyncCompleteCommandProperties)
from azext_dms.scenario_inputs import (get_migrate_mysql_to_azuredbformysql_sync_input,
                                       get_migrate_postgresql_to_azuredbforpostgresql_sync_input)
from azure.cli.core.util import get_file_json, shell_safe_json_parse
from azure.cli.command_modules.dms.custom import (create_or_update_project as core_create_or_update_project,
                                                  create_task as core_create_task)


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

    # Set inputs to lowercase
    source_platform = source_platform.lower()
    target_platform = target_platform.lower()

    # Validation: Test scenario eligibility
    if not determine_source_target_eligibility(source_platform, target_platform):
        # If not an extension scenario, run CLI core method
        # TODO: We currently don't have any CLI core code to perform any validations
        # because of this we need to raise the error here.
        try:
            # TODO: Remove this check after validations are added to core
            if source_platform != "sql" or target_platform != "sqldb":
                raise ValueError

            core_res = core_create_or_update_project(
                client,
                project_name,
                service_name,
                resource_group_name,
                location,
                source_platform,
                target_platform,
                tags)
        except:
            raise ValueError("The provided source-platform, target-platform combination is not appropriate. \n\
                Please refer to the help file 'az dms project create -h' for the supported scenarios.")
        else:
            return core_res

    # Run extension scenario
    parameters = Project(location=location,
                         source_platform=source_platform,
                         target_platform=target_platform,
                         tags=tags)

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
        task_type,
        source_connection_json,
        target_connection_json,
        database_options_json,
        enable_schema_validation=False,
        enable_data_integrity_validation=False,
        enable_query_analysis_validation=False):

    # Set inputs to lowercase
    task_type = task_type.lower()
    source_platform = source_platform.lower()
    target_platform = target_platform.lower()

    # Validation: Test scenario eligibility
    if not determine_scenario_eligibility(source_platform, target_platform, task_type):
        # If not an extension scenario, run CLI core method
        # TODO: We currently don't have any CLI core code to perform any validations
        # because of this we need to raise the error here.
        try:
            # CLI core doesnt currently support task types - it only supports offline migrations.
            # TODO: Remove this check after task types are supported
            if source_platform != "sql" or target_platform != "sqldb" or task_type != "offlinemigration":
                raise ValueError

            core_res = core_create_task(
                client,
                resource_group_name,
                service_name,
                project_name,
                task_name,
                source_connection_json,
                target_connection_json,
                database_options_json,
                enable_schema_validation,
                enable_data_integrity_validation,
                enable_query_analysis_validation)
        except:
            raise ValueError("The provided source-platform, target-platform, and task-type \
                combination is not appropriate. \n\
                Please refer to the help file 'az dms project task create -h' for the supported scenarios.")
        else:
            return core_res

    # Run extension scenario

    # Source connection info
    if os.path.exists(source_connection_json):
        source_connection_json = get_file_json(source_connection_json)
    else:
        source_connection_json = shell_safe_json_parse(source_connection_json)
    source_connection_info = create_connection(source_connection_json, "Source Database", source_platform)

    # Target connection info
    if os.path.exists(target_connection_json):
        target_connection_json = get_file_json(target_connection_json)
    else:
        target_connection_json = shell_safe_json_parse(target_connection_json)
    target_connection_info = create_connection(target_connection_json, "Target Database", target_platform)

    # Database options
    if os.path.exists(database_options_json):
        database_options_json = get_file_json(database_options_json)
    else:
        database_options_json = shell_safe_json_parse(database_options_json)

    # Get the task properties
    task_properties = get_task_migration_properties(database_options_json,
                                                    source_platform,
                                                    target_platform,
                                                    task_type,
                                                    source_connection_info,
                                                    target_connection_info)

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
def determine_scenario_eligibility(
        source_type,
        target_type,
        task_type):
    return (source_type == "mysql" and target_type == "azuredbformysql" and task_type == "onlinemigration") or \
           (source_type == "postgresql" and target_type == "azuredbforpostgresql" and task_type == "onlinemigration")


def determine_source_target_eligibility(
        source_type,
        target_type):
    return (source_type == "mysql" and target_type == "azuredbformysql") or \
           (source_type == "postgresql" and target_type == "azuredbforpostgresql")


def create_connection(connection_info_json, prompt_prefix, typeOfInfo):
    user_name = connection_info_json.get('userName', None) or prompt(prompt_prefix + 'Username: ')
    password = connection_info_json.get('password', None) or prompt_pass(msg=prompt_prefix + 'Password: ')
    server_name = connection_info_json.get('serverName', None)
    if "mysql" in typeOfInfo:
        port = connection_info_json.get('port', 3306)
        return MySqlConnectionInfo(user_name=user_name,
                                   password=password,
                                   server_name=server_name,
                                   port=port)

    database_name = connection_info_json.get('databaseName', "postgres")
    port = connection_info_json.get('port', 5432)
    return PostgreSqlConnectionInfo(user_name=user_name,
                                    password=password,
                                    server_name=server_name,
                                    database_name=database_name,
                                    port=port)


def get_task_migration_properties(
        database_options_json,
        source_type,
        target_type,
        task_type,
        source_connection_info,
        target_connection_info):
    if source_type == 'mysql' and target_type == 'azuredbformysql' and task_type == "onlinemigration":
        TaskProperties = MigrateMySqlAzureDbForMySqlSyncTaskProperties
        GetInput = get_migrate_mysql_to_azuredbformysql_sync_input
    elif source_type == 'postgresql' and target_type == 'azuredbforpostgresql' and task_type == "onlinemigration":
        TaskProperties = MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties
        GetInput = get_migrate_postgresql_to_azuredbforpostgresql_sync_input

    task_input = GetInput(
        database_options_json,
        source_connection_info,
        target_connection_info)

    task_properties_params = {'input': task_input}
    return TaskProperties(**task_properties_params)
# endregion
