# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.util import sdk_no_wait, read_file_content
from knack.log import get_logger  # pylint: disable=unused-import
from knack.util import CLIError

from azext_synapse.vendored_sdks.azure_synapse.models import ExtendedLivyBatchRequest, LivyStatementRequestBody, \
    ExtendedLivySessionRequest

from azext_synapse.vendored_sdks.azure_mgmt_synapse.models import Workspace, WorkspacePatchInfo, ManagedIdentity, \
    DataLakeStorageAccountDetails, \
    BigDataPoolResourceInfo, AutoScaleProperties, AutoPauseProperties, LibraryRequirements, NodeSize, NodeSizeFamily, \
    SqlPool, SqlPoolPatchInfo, Sku

from ._client_factory import cf_synapse_client_workspace_factory


# pylint: disable=too-many-locals, too-many-branches, too-many-statements, unused-argument, too-many-function-args
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


def create_workspace(cmd, client, resource_group_name, workspace_name, storage_account, file_system,
                     sql_admin_login_user, sql_admin_login_password, location, tags=None, no_wait=False):
    identity_type = "SystemAssigned"
    identity = ManagedIdentity(type=identity_type)
    account_url = "https://{}.dfs.{}".format(storage_account, cmd.cli_ctx.cloud.suffixes.storage_endpoint)
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
                     tags=None, no_wait=False):
    workspace_patch_info = WorkspacePatchInfo(tags=tags, sql_admin_login_password=sql_admin_login_password)
    return sdk_no_wait(no_wait, client.update, resource_group_name, workspace_name, workspace_patch_info)


def custom_check_name_availability(cmd, client, name):
    return client.check_name_availability(name, "Microsoft.Synapse/workspaces")


def get_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name):
    return client.get(resource_group_name, workspace_name, spark_pool_name)


def create_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name,
                      spark_version, node_size=NodeSize.medium.value,
                      node_size_family=NodeSizeFamily.memory_optimized.value, enable_auto_scale=None,
                      node_count=None, min_node_count=None, max_node_count=None,
                      enable_auto_pause=None, delay_in_minutes=None, spark_events_folder="/events",
                      library_requirements_file=None,
                      default_spark_log_folder="/logs", force=False, tags=None, no_wait=False):
    # get the location of the workspace
    workspace_client = cf_synapse_client_workspace_factory(cmd.cli_ctx)
    workspace_object = workspace_client.get(resource_group_name, workspace_name)
    location = workspace_object.location

    big_data_pool_info = BigDataPoolResourceInfo(location=location, spark_version=spark_version, node_size=node_size,
                                                 node_count=node_count, node_size_family=node_size_family,
                                                 spark_events_folder=spark_events_folder,
                                                 default_spark_log_folder=default_spark_log_folder, tags=tags)

    big_data_pool_info.auto_scale = AutoScaleProperties(enabled=enable_auto_scale, min_node_count=min_node_count,
                                                        max_node_count=max_node_count)

    big_data_pool_info.auto_pause = AutoPauseProperties(enabled=enable_auto_pause,
                                                        delay_in_minutes=delay_in_minutes)

    if library_requirements_file:
        library_requirements_content = read_file_content(library_requirements_file)
        big_data_pool_info.library_requirements = LibraryRequirements(filename=library_requirements_file,
                                                                      content=library_requirements_content)
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, workspace_name, spark_pool_name,
                       big_data_pool_info, force)


def update_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name,
                      node_size=None, node_count=None, enable_auto_scale=None,
                      min_node_count=None, max_node_count=None,
                      enable_auto_pause=None, delay_in_minutes=None,
                      library_requirements_file=None, tags=None, force=False, no_wait=False):
    existing_spark_pool = client.get(resource_group_name, workspace_name, spark_pool_name)

    if not existing_spark_pool:
        raise CLIError("Failed to discover the spark pool {}".format(spark_pool_name))

    if node_size:
        existing_spark_pool.node_size = node_size
    if node_count:
        existing_spark_pool.node_count = node_count

    if library_requirements_file:
        library_requirements_content = read_file_content(library_requirements_file)
        existing_spark_pool.library_requirements = LibraryRequirements(filename=library_requirements_file,
                                                                       content=library_requirements_content)
    if tags:
        existing_spark_pool.tags = tags

    if existing_spark_pool.auto_scale is not None:
        if enable_auto_scale is not None:
            existing_spark_pool.auto_scale.enabled = enable_auto_scale
        if min_node_count:
            existing_spark_pool.auto_scale.min_node_count = min_node_count
        if max_node_count:
            existing_spark_pool.auto_scale.min_node_count = max_node_count
    else:
        existing_spark_pool.auto_scale = AutoScaleProperties(enabled=enable_auto_scale, min_node_count=min_node_count,
                                                             max_node_count=max_node_count)

    if existing_spark_pool.auto_pause is not None:
        if enable_auto_pause is not None:
            existing_spark_pool.auto_pause.enabled = enable_auto_pause
        if delay_in_minutes:
            existing_spark_pool.auto_pause.delay_in_minutes = delay_in_minutes
    else:
        existing_spark_pool.auto_pause = AutoPauseProperties(enabled=enable_auto_pause,
                                                             delay_in_minutes=delay_in_minutes)

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, workspace_name, spark_pool_name,
                       existing_spark_pool, force=force)


def delete_spark_pool(cmd, client, resource_group_name, workspace_name, spark_pool_name, no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name, workspace_name, spark_pool_name)


def create_sql_pool(cmd, client, resource_group_name, workspace_name, sql_pool_name, sku_name, tags=None,
                    no_wait=False):
    # get the location of the workspace
    workspace_client = cf_synapse_client_workspace_factory(cmd.cli_ctx)
    workspace_object = workspace_client.get(resource_group_name, workspace_name)
    location = workspace_object.location

    max_size_bytes = None
    sku_tier = None
    sku = Sku(tier=sku_tier, name=sku_name)

    create_mode = 'Default'

    sql_pool_info = SqlPool(sku=sku, location=location, max_size_bytes=max_size_bytes, create_mode=create_mode,
                            tags=tags)

    return sdk_no_wait(no_wait, client.create, resource_group_name, workspace_name, sql_pool_name, sql_pool_info)


def update_sql_pool(cmd, client, resource_group_name, workspace_name, sql_pool_name, sku_name=None, tags=None):
    sku = Sku(name=sku_name)
    sql_pool_patch_info = SqlPoolPatchInfo(sku=sku, tags=tags)
    return client.update(resource_group_name, workspace_name, sql_pool_name, sql_pool_patch_info)


def create_firewall_rule(cmd, client, resource_group_name, workspace_name, rule_name, start_ip_address, end_ip_address,
                         no_wait=False):
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, workspace_name, rule_name,
                       start_ip_address=start_ip_address, end_ip_address=end_ip_address)
