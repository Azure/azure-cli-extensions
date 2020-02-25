# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
from enum import Enum
from knack.log import get_logger
from knack.prompting import prompt, prompt_pass
from knack.util import CLIError
from azure.cli.core.util import get_file_json, shell_safe_json_parse
from azure.cli.command_modules.dms._client_factory import dms_cf_projects
from azure.cli.command_modules.dms.custom import (create_or_update_project as core_create_or_update_project,
                                                  create_task as core_create_task)
from azext_dms.vendored_sdks.datamigration.models import (Project,
                                                          MySqlConnectionInfo,
                                                          PostgreSqlConnectionInfo,
                                                          MigrateSyncCompleteCommandInput,
                                                          MigrateMySqlAzureDbForMySqlSyncTaskProperties,
                                                          MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties,
                                                          MigrateSyncCompleteCommandProperties,
                                                          MigrateMongoDbTaskProperties,
                                                          MongoDbConnectionInfo,
                                                          MongoDbCancelCommand,
                                                          MongoDbCommandInput,
                                                          MongoDbFinishCommand,
                                                          MongoDbFinishCommandInput,
                                                          MongoDbRestartCommand,
                                                          ValidateMongoDbTaskProperties,
                                                          OracleConnectionInfo,
                                                          MigrateOracleAzureDbForPostgreSqlSyncTaskProperties,
                                                          CheckOCIDriverTaskProperties,
                                                          UploadOCIDriverTaskProperties,
                                                          InstallOCIDriverTaskProperties)
from azext_dms.scenario_inputs import (get_migrate_mysql_to_azuredbformysql_sync_input,
                                       get_migrate_postgresql_to_azuredbforpostgresql_sync_input,
                                       get_mongo_to_mongo_input,
                                       get_migrate_oracle_to_azuredbforpostgresql_sync_input,
                                       get_check_oci_driver_input,
                                       get_upload_oci_driver_input,
                                       get_install_oci_driver_input)

logger = get_logger(__name__)


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
    scenario_handled_in_extension = extension_handles_scenario(source_platform, target_platform)

    # Validation: Test scenario eligibility
    if not scenario_handled_in_extension:
        # If not an extension scenario, run CLI core method
        # TODO: We currently don't have any CLI core code to perform any validations
        # because of this we need to raise the error here.

        # TODO: Remove this check after validations are added to core
        if source_platform != "sql" or target_platform != "sqldb":
            raise CLIError("The provided source-platform, target-platform combination is not appropriate. \n\
Please refer to the help file 'az dms project create -h' for the supported scenarios.")

        return core_create_or_update_project(
            client,
            project_name,
            service_name,
            resource_group_name,
            location,
            source_platform,
            target_platform,
            tags)

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
        cmd,
        client,
        resource_group_name,
        service_name,
        project_name,
        task_name,
        task_type,
        source_connection_json,
        target_connection_json,
        database_options_json,
        enable_schema_validation=False,
        enable_data_integrity_validation=False,
        enable_query_analysis_validation=False,
        validate_only=False,
        validated_task_name=None):

    # Get source and target platform abd set inputs to lowercase
    source_platform, target_platform = get_project_platforms(cmd,
                                                             project_name=project_name,
                                                             service_name=service_name,
                                                             resource_group_name=resource_group_name)
    task_type = task_type.lower()
    scenario_handled_in_extension = extension_handles_scenario(source_platform,
                                                               target_platform,
                                                               task_type)

    # Validation: Test scenario eligibility
    if not scenario_handled_in_extension:
        # If not an extension scenario, run CLI core method

        # TODO: Remove this check after validations are added to core
        if source_platform != "sql" or target_platform != "sqldb":
            raise CLIError("The combination of the provided task-type and the project's \
source-platform and target-platform is not appropriate. \n\
Please refer to the help file 'az dms project task create -h' \
for the supported scenarios.")

        # TODO: Calling this validates our inputs. Remove this check after this function is added to core
        transform_json_inputs(source_connection_json,
                              source_platform,
                              target_connection_json,
                              target_platform,
                              database_options_json)

        return core_create_task(client,
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

    RequireValidationScenarios = [
        ScenarioType.mongo_mongo_offline,
        ScenarioType.mongo_mongo_online]

    # Mongo migrations require users to validate their migrations first
    # Once the migration settings have been attempted, if all database and collection objects aren't in a 'Failed'
    # state continue creating the task
    if get_scenario_type(source_platform, target_platform, task_type) in RequireValidationScenarios:
        if validate_only is False and validated_task_name is None:
            raise CLIError(
                "When not validating a MongoDB task, you must supply a previously run 'validate_only' task name.")

        if validate_only is False and validated_task_name is not None:
            # Though getting the task's properties is pretty quick, we want to let the user know something is happening
            logger.warning("Reviewing validation...")
            v_result = client.get(group_name=resource_group_name,
                                  service_name=service_name,
                                  project_name=project_name,
                                  task_name=validated_task_name,
                                  expand="output")
            if not mongo_validation_succeeded(v_result.properties.output[0]):
                raise CLIError("Not all collections passed during the validation task. Fix your settings, \
validate those settings, and try again. \n\
To view the errors use 'az dms project task show' with the '--expand output' argument on your previous \
validate-only task.")

    # Get json inputs
    source_connection_info, target_connection_info, database_options_json = \
        transform_json_inputs(source_connection_json,
                              source_platform,
                              target_connection_json,
                              target_platform,
                              database_options_json)

    # Get the task properties
    properties_model = get_task_validation_properties if validate_only else get_task_migration_properties
    task_properties = properties_model(database_options_json,
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
        cmd,
        client,
        resource_group_name,
        service_name,
        project_name,
        task_name,
        object_name=None,
        immediate=False):
    # If object name is empty, treat this as cutting over the entire online migration.
    # Otherwise, for scenarios that support it, just cut over the migration on the specified object.
    # 'input' is a built in function. Even though we can technically use it, it's not recommended.
    # https://stackoverflow.com/questions/20670732/is-input-a-keyword-in-python

    source_platform, target_platform = get_project_platforms(cmd,
                                                             project_name=project_name,
                                                             service_name=service_name,
                                                             resource_group_name=resource_group_name)
    st = get_scenario_type(source_platform, target_platform, "onlinemigration")

    if st in [ScenarioType.mysql_azuremysql_online,
              ScenarioType.postgres_azurepostgres_online,
              ScenarioType.oracle_azurepostgres_online]:
        if object_name is None:
            raise CLIError("The argument 'object_name' must be present for this task type.")
        command_input = MigrateSyncCompleteCommandInput(database_name=object_name)
        command_properties_model = MigrateSyncCompleteCommandProperties
    elif st == ScenarioType.mongo_mongo_online:
        command_input = MongoDbFinishCommandInput(object_name=object_name, immediate=immediate)
        command_properties_model = MongoDbFinishCommand
    else:
        raise CLIError("The supplied project's source and target do not support cutting over the migration.")

    run_command(client,
                command_input,
                command_properties_model,
                resource_group_name,
                service_name,
                project_name,
                task_name)


def restart_task(
        cmd,
        client,
        resource_group_name,
        service_name,
        project_name,
        task_name,
        object_name=None):
    # For scenarios that support it, restart the entire migration if object name is empty,
    # otherwise restart the specified object.
    source_platform, target_platform = get_project_platforms(cmd,
                                                             project_name=project_name,
                                                             service_name=service_name,
                                                             resource_group_name=resource_group_name)
    st = get_scenario_type(source_platform, target_platform, "offlinemigration")

    if st in [ScenarioType.mongo_mongo_offline]:
        command_input = MongoDbCommandInput(object_name=object_name)
        command_properties_model = MongoDbRestartCommand
    else:
        raise CLIError("The supplied project's source and target do not support restarting the migration.")

    run_command(client,
                command_input,
                command_properties_model,
                resource_group_name,
                service_name,
                project_name,
                task_name)


def stop_task(
        cmd,
        client,
        resource_group_name,
        service_name,
        project_name,
        task_name,
        object_name=None):

    # If object name is empty, treat this as stopping/cancelling the entire task.
    if object_name is None:
        client.cancel(group_name=resource_group_name,
                      service_name=service_name,
                      project_name=project_name,
                      task_name=task_name)
    # Otherwise, for scenarios that support it, just stop migration on the specified object.
    else:
        source_platform, target_platform = get_project_platforms(cmd,
                                                                 project_name=project_name,
                                                                 service_name=service_name,
                                                                 resource_group_name=resource_group_name)
        st = get_scenario_type(source_platform, target_platform, "offlinemigration")

        if st in [ScenarioType.mongo_mongo_offline]:
            command_input = MongoDbCommandInput(object_name=object_name)
            command_properties_model = MongoDbCancelCommand
        else:
            raise CLIError("The supplied project's source and target does not support \
cancelling at the object level. \n\
To cancel this task do not supply the object-name parameter.")

        run_command(client,
                    command_input,
                    command_properties_model,
                    resource_group_name,
                    service_name,
                    project_name,
                    task_name)
# endregion


# region Service Task
def create_service_task(
        client,
        resource_group_name,
        service_name,
        task_name,
        task_type,
        task_options_json):

    task_type = task_type.lower()

    task_options_json = get_file_or_parse_json(task_options_json, "task-options-json")

    task_properties = get_service_task_properties(task_options_json,
                                                  task_type)

    return client.create_or_update(group_name=resource_group_name,
                                   service_name=service_name,
                                   task_name=task_name,
                                   properties=task_properties)
# endregion


# region Helper Methods
def get_project_platforms(cmd, project_name, service_name, resource_group_name):
    client = dms_cf_projects(cmd.cli_ctx)
    proj = client.get(group_name=resource_group_name, service_name=service_name, project_name=project_name)
    return (proj.source_platform.lower(), proj.target_platform.lower())


def extension_handles_scenario(
        source_platform,
        target_platform,
        task_type=""):
    # Remove scenario types from this list when moving them out of this extension (preview) and into the core CLI (GA)
    ExtensionScenarioTypes = [
        ScenarioType.sql_sqldb_online,
        ScenarioType.mysql_azuremysql_online,
        ScenarioType.postgres_azurepostgres_online,
        ScenarioType.mongo_mongo_offline,
        ScenarioType.mongo_mongo_online,
        ScenarioType.oracle_azurepostgres_online]
    return get_scenario_type(source_platform, target_platform, task_type) in ExtensionScenarioTypes


def transform_json_inputs(
        source_connection_json,
        source_platform,
        target_connection_json,
        target_platform,
        database_options_json):
    # Source connection info
    source_connection_json = get_file_or_parse_json(source_connection_json, "source-connection-json")
    source_connection_info = create_connection(source_connection_json, "Source Database ", source_platform)

    # Target connection info
    target_connection_json = get_file_or_parse_json(target_connection_json, "target-connection-json")
    target_connection_info = create_connection(target_connection_json, "Target Database ", target_platform)

    # Database options
    database_options_json = get_file_or_parse_json(database_options_json, "database-options-json")

    return (source_connection_info, target_connection_info, database_options_json)


def get_file_or_parse_json(value, value_type):
    if os.path.exists(value):
        return get_file_json(value)

    # Test if provided value is a valid json
    try:
        json_parse = shell_safe_json_parse(value)
    except:
        raise CLIError("The supplied input for '" + value_type + "' is not a valid file path or a valid json object.")
    else:
        return json_parse


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

    if "postgres" in typeOfInfo:
        database_name = connection_info_json.get('databaseName', "postgres")
        port = connection_info_json.get('port', 5432)
        return PostgreSqlConnectionInfo(user_name=user_name,
                                        password=password,
                                        server_name=server_name,
                                        database_name=database_name,
                                        port=port)

    if "mongo" in typeOfInfo:
        connection_string = connection_info_json['connectionString']
        # Strip out the username and password from the connection string (if they exist) to store them securely.
        rex_conn_string = re.compile(r'^(mongodb://|mongodb\+srv://|http://|https://)(.*:.*@)?(.*)')
        connection_string_match = rex_conn_string.search(connection_string)
        connection_string = connection_string_match.group(1) + connection_string_match.group(3)
        if connection_string_match.group(2) is not None and not user_name and not password:
            rex_un_pw = re.compile('^(.*):(.*)@')
            un_pw_match = rex_un_pw.search(connection_string_match.group(2))
            user_name = un_pw_match.group(1)
            password = un_pw_match.group(2)
        return MongoDbConnectionInfo(connection_string=connection_string,
                                     user_name=user_name,
                                     password=password)

    if "oracle" in typeOfInfo:
        data_source = connection_info_json['dataSource']
        return OracleConnectionInfo(user_name=user_name,
                                    password=password,
                                    data_source=data_source)

    # If no match, Pass the connection info through
    return connection_info_json


def get_task_migration_properties(
        database_options_json,
        source_platform,
        target_platform,
        task_type,
        source_connection_info,
        target_connection_info):
    st = get_scenario_type(source_platform, target_platform, task_type)
    if st.name == "mysql_azuremysql_online":
        TaskProperties = MigrateMySqlAzureDbForMySqlSyncTaskProperties
        GetInput = get_migrate_mysql_to_azuredbformysql_sync_input
    elif st.name == "postgres_azurepostgres_online":
        TaskProperties = MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties
        GetInput = get_migrate_postgresql_to_azuredbforpostgresql_sync_input
    elif "mongo_mongo" in st.name:
        TaskProperties = MigrateMongoDbTaskProperties
        GetInput = get_mongo_to_mongo_input
    elif "oracle_azurepostgres" in st.name:
        TaskProperties = MigrateOracleAzureDbForPostgreSqlSyncTaskProperties
        GetInput = get_migrate_oracle_to_azuredbforpostgresql_sync_input
    else:
        raise CLIError("The supplied source, target, and task type is not supported for migration.")

    return get_task_properties(GetInput,
                               TaskProperties,
                               database_options_json,
                               source_connection_info,
                               target_connection_info)


def get_task_validation_properties(
        database_options_json,
        source_platform,
        target_platform,
        task_type,
        source_connection_info,
        target_connection_info):
    st = get_scenario_type(source_platform, target_platform, task_type)
    if "mongo_mongo" in st.name:
        input_func = get_mongo_to_mongo_input
        task_properties_type = ValidateMongoDbTaskProperties
    else:
        raise CLIError("The supplied source, target, and task type is not supported for validation.")

    return get_task_properties(input_func,
                               task_properties_type,
                               database_options_json,
                               source_connection_info,
                               target_connection_info)


def get_service_task_properties(
        task_options_json,
        task_type):
    if task_type == "checkocidriver":
        input_func = get_check_oci_driver_input
        task_properties_type = CheckOCIDriverTaskProperties
    elif task_type == "uploadocidriver":
        input_func = get_upload_oci_driver_input
        task_properties_type = UploadOCIDriverTaskProperties
    elif task_type == "installocidriver":
        input_func = get_install_oci_driver_input
        task_properties_type = InstallOCIDriverTaskProperties
    else:
        raise CLIError("The supplied service task type is not supported.")

    return get_task_properties(input_func,
                               task_properties_type,
                               task_options_json,
                               None,
                               None)


def get_task_properties(input_func,
                        task_properties_type,
                        options_json,
                        source_connection_info,
                        target_connection_info):
    if source_connection_info is None and target_connection_info is None:
        task_input = input_func(options_json)
    else:
        task_input = input_func(
            options_json,
            source_connection_info,
            target_connection_info)

    task_properties_params = {'input': task_input}

    return task_properties_type(**task_properties_params)


def run_command(client,
                command_input,
                command_properties_model,
                resource_group_name,
                service_name,
                project_name,
                task_name):

    command_properties_params = {'input': command_input}
    command_properties = command_properties_model(**command_properties_params)

    client.command(group_name=resource_group_name,
                   service_name=service_name,
                   project_name=project_name,
                   task_name=task_name,
                   parameters=command_properties)


def get_scenario_type(source_platform, target_platform, task_type=""):
    if source_platform == "sql" and target_platform == "sqldb":
        scenario_type = ScenarioType.sql_sqldb_online if "online" in task_type else ScenarioType.sql_sqldb_offline
    elif source_platform == "sql" and target_platform == "sqlmi":
        scenario_type = ScenarioType.sql_sqlmi_online if "online" in task_type else ScenarioType.sql_sqlmi_offline
    elif source_platform == "mysql" and target_platform == "azuredbformysql":
        scenario_type = ScenarioType.mysql_azuremysql_online if "online" in task_type else \
            ScenarioType.mysql_azuremysql_offline
    elif source_platform == "postgresql" and target_platform == "azuredbforpostgresql":
        # PG is one of the few that doesn't have an offline scenario. But a project doesn't pass a task type so we
        # need to accommodate for projects and making sure a task is set to online.
        scenario_type = ScenarioType.postgres_azurepostgres_online if not task_type or "online" in task_type else \
            ScenarioType.postgres_azurepostgres_offline
    elif source_platform == "mongodb" and target_platform == "mongodb":
        scenario_type = ScenarioType.mongo_mongo_validation if "validation" in task_type else \
            ScenarioType.mongo_mongo_online if "online" in task_type else ScenarioType.mongo_mongo_offline
    elif source_platform == "oracle" and target_platform == "azuredbforpostgresql":
        # Allow a project to be created for Oracle to PGSQL even though no task type is passed in
        scenario_type = ScenarioType.oracle_azurepostgres_online if "online" in task_type or not task_type else \
            ScenarioType.oracle_azurepostgres_offline
    else:
        scenario_type = ScenarioType.unknown

    return scenario_type


def mongo_validation_succeeded(migration_progress):
    for dummy_key1, db in migration_progress.databases.items():
        if db.state == "Failed" or any(c.state == "Failed" for dummy_key2, c in db.collections.items()):
            return False

    return True


class ScenarioType(Enum):

    unknown = 0
    # SQL to SQLDB
    sql_sqldb_offline = 1
    sql_sqldb_online = 2
    # SQL to SQLMI
    sql_sqlmi_offline = 10
    sql_sqlmi_online = 11
    # MySQL to Azure for MySQL
    mysql_azuremysql_offline = 20
    mysql_azuremysql_online = 21
    # PostgresSQL to Azure for PostgreSQL
    postgres_azurepostgres_offline = 30
    postgres_azurepostgres_online = 31
    # MongoDB to MongoDB (including Cosmos DB using MongoDB API)
    mongo_mongo_offline = 40
    mongo_mongo_online = 41
    mongo_mongo_validation = 42
    # Oracle to Azure for PostgreSQL
    oracle_azurepostgres_offline = 43
    oracle_azurepostgres_online = 44

# endregion
