# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger  # pylint: disable=unused-import
from knack.util import CLIError

from azext_synapse.vendored_sdks.azure_synapse.models import ExtendedLivyBatchRequest, LivyStatementRequestBody, \
    ExtendedLivySessionRequest

from azext_synapse.vendored_sdks.azure_mgmt_synapse.models import Workspace, WorkspacePatchInfo, ManagedIdentity, \
    DataLakeStorageAccountDetails, \
    BigDataPoolResourceInfo, AutoScaleProperties, AutoPauseProperties, LibraryRequirements, NodeSize, NodeSizeFamily, \
    SqlPool, Sku


# pylint: disable=too-many-locals, too-many-branches, too-many-statements, unused-argument


def list_spark_batch_jobs(cmd, client, workspace_name, spark_pool_name, from_index=None, size=None, detailed=True):
    return client.list(workspace_name, spark_pool_name, from_index, size, detailed)


def create_spark_batch_job(cmd, client, workspace_name, spark_pool_name, job_name, args, driver_memory, driver_cores,
                           executor_memory, executor_cores, num_executors, language="SCALA",
                           file=None, class_name=None, jars=None, files=None,
                           archives=None, conf=None,
                           tags=None, detailed=True):
    dotnet_file = "local:///usr/hdp/current/spark2-client/jars/microsoft-spark.jar"
    dotnet_class = "org.apache.spark.deploy.dotnet.DotnetRunner"

    if language.upper() != "DOTNET" and (not file or not class_name):
        raise CLIError('Scala and Python spark batch job must provide value for parameter file and class_name.'
                       'If you want to create a DotNet spark batch job please add `--language DOTNET`.')

    if language.upper() == "DOTNET":
        file = dotnet_file
        class_name = dotnet_class

    livy_batch_request = ExtendedLivyBatchRequest(
        tags=tags,
        name=job_name, file=file, class_name=class_name, args=args, jars=jars, files=files, archives=archives,
        conf=conf, driver_memory=driver_memory, driver_cores=driver_cores, executor_memory=executor_memory,
        executor_cores=executor_cores, num_executors=num_executors)

    return client.create(workspace_name, spark_pool_name, livy_batch_request, detailed)


def get_spark_batch_job(cmd, client, workspace_name, spark_pool_name, batch_id, detailed=True):
    return client.get(workspace_name, spark_pool_name, batch_id, detailed)


def cancel_spark_batch_job(cmd, client, workspace_name, spark_pool_name, batch_id):
    return client.delete(workspace_name, spark_pool_name, batch_id)


# Spark Session
def list_spark_session_jobs(cmd, client, workspace_name, spark_pool_name, from_index=None, size=None, detailed=True):
    return client.list(workspace_name, spark_pool_name, from_index, size, detailed)


def create_spark_session_job(cmd, client, workspace_name, spark_pool_name, driver_memory, driver_cores,
                             executor_memory, executor_cores, num_executors, job_name=None, file=None, class_name=None,
                             args=None, jars=None, files=None, archives=None, conf=None,
                             tags=None, detailed=True):
    livy_session_request = ExtendedLivySessionRequest(
        tags=tags,
        name=job_name, file=file, class_name=class_name, args=args, jars=jars, files=files, archives=archives,
        conf=conf, driver_memory=driver_memory, driver_cores=driver_cores, executor_memory=executor_memory,
        executor_cores=executor_cores, num_executors=num_executors)
    return client.create(workspace_name, spark_pool_name, livy_session_request, detailed)


def get_spark_session_job(cmd, client, workspace_name, spark_pool_name, session_id, detailed=True):
    return client.get(workspace_name, spark_pool_name, session_id, detailed)


def cancel_spark_session_job(cmd, client, workspace_name, spark_pool_name, session_id):
    return client.delete(workspace_name, spark_pool_name, session_id)


def reset_timeout(cmd, client, workspace_name, spark_pool_name, session_id):
    return client.reset_timeout(workspace_name, spark_pool_name, session_id)


def list_spark_session_statements(cmd, client, workspace_name, spark_pool_name, session_id):
    return client.list_statements(workspace_name, spark_pool_name, session_id)


def create_spark_session_statement(cmd, client, workspace_name, spark_pool_name, session_id, code, kind):
    livy_statement_request = LivyStatementRequestBody(code=code, kind=kind)
    return client.create_statement(workspace_name, spark_pool_name, session_id, livy_statement_request)


def get_spark_session_statement(cmd, client, workspace_name, spark_pool_name, session_id, statement_id):
    return client.get_statement(workspace_name, spark_pool_name, session_id, statement_id)


def cancel_spark_session_statement(cmd, client, workspace_name, spark_pool_name, session_id, statement_id):
    return client.delete_statement(workspace_name, spark_pool_name, session_id, statement_id)


def list_workspaces(cmd, client, resource_group_name=None):  # pylint: disable=unused-argument
    return client.list_by_resource_group(
        resource_group_name=resource_group_name) if resource_group_name else client.list()


def create_workspace(cmd, client, resource_group_name, workspace_name, account_url, file_system, sql_admin_login_user,
                     sql_admin_login_password, location, tags=None, identity_type="SystemAssigned", no_wait=False):
    identity = ManagedIdentity(type=identity_type)
    default_data_lake_storage = DataLakeStorageAccountDetails(account_url=account_url, filesystem=file_system)
    workspace_info = Workspace(
        identity=identity,
        default_data_lake_storage=default_data_lake_storage,
        sql_administrator_login=sql_admin_login_user,
        sql_administrator_login_password=sql_admin_login_password,
        location=location
    )
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, workspace_name, workspace_info)


def update_workspace(cmd, client, resource_group_name, workspace_name, sql_admin_login_password=None,
                     identity_type="SystemAssigned", principal_id=None, tags=None, no_wait=False):
    identity = ManagedIdentity(type=identity_type)
    workspace_patch_info = WorkspacePatchInfo(
        tags=tags,
        identity=identity,
        sql_administrator_login_password=sql_admin_login_password
    )
    return sdk_no_wait(no_wait, client.update, resource_group_name, workspace_name, workspace_patch_info)


def get_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name):
    return client.get(resource_group_name, workspace_name, spark_pool_name)


def create_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name, location,
                      spark_version, node_size=NodeSize.medium.value, node_count=3,
                      node_size_family=NodeSizeFamily.memory_optimized.value, auto_scale_enabled=True,
                      min_node_count=3,
                      max_node_count=40, auto_pause_enabled=True, delay_in_minutes=15, spark_events_folder="/events",
                      library_requirements_filename=None, library_requirements_content=None,
                      default_spark_log_folder="/logs", force=False, tags=None, no_wait=False):
    big_data_pool_info = BigDataPoolResourceInfo(location=location, spark_version=spark_version, node_size=node_size,
                                                 node_count=node_count, node_size_family=node_size_family,
                                                 spark_events_folder=spark_events_folder,
                                                 default_spark_log_folder=default_spark_log_folder, tags=tags)
    if auto_scale_enabled:
        big_data_pool_info.auto_scale = AutoScaleProperties(enabled=auto_scale_enabled, min_node_count=min_node_count,
                                                            max_node_count=max_node_count)
    if auto_pause_enabled:
        big_data_pool_info.auto_pause = AutoPauseProperties(enabled=auto_pause_enabled,
                                                            delay_in_minutes=delay_in_minutes)

    if library_requirements_filename or library_requirements_content:
        big_data_pool_info.library_requirements = LibraryRequirements(filename=library_requirements_filename,
                                                                      content=library_requirements_content)
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, workspace_name, spark_pool_name,
                       big_data_pool_info, force)


def update_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name, tags=None):
    return client.update(resource_group_name, workspace_name, spark_pool_name, tags)


def delete_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name, no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name, workspace_name, spark_pool_name)


def create_sql_pool(cmd, client, resource_group_name, workspace_name, sql_pool_name, location, sku_name,
                    sku_tier=None, max_size_bytes=None, source_database_id=None, recoverable_database_id=None,
                    create_mode=None, tags=None, no_wait=False):
    sku = Sku(tier=sku_tier, name=sku_name)
    sql_pool_info = SqlPool(sku=sku, location=location, max_size_bytes=max_size_bytes,
                            source_database_id=source_database_id, recoverable_database_id=recoverable_database_id,
                            create_mode=create_mode, tags=tags)

    return sdk_no_wait(no_wait, client.create, resource_group_name, workspace_name, sql_pool_name, sql_pool_info)
