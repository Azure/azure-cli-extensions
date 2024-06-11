# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import base64
from io import BytesIO
import os
from random import uniform
import re
import time
import colorama
from knack.log import get_logger
from ._constants import CONTINUOSPATCH_DEPLOYMENT_NAME, CONTINUOSPATCH_DEPLOYMENT_TEMPLATE, CONTINUOSPATCH_ALL_TASK_NAMES, CONTINUOSPATCH_TASK_DEFINITION, CONTINUOSPATCH_TASK_SCANREGISTRY_NAME, RESOURCE_GROUP, TMP_DRY_RUN_FILE_NAME
from azure.common import AzureHttpError
from azure.cli.core.azclierror import AzCLIError, ResourceNotFoundError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.command_modules.acr._stream_utils import stream_logs
from azure.cli.command_modules.acr._stream_utils import _stream_logs, _blob_is_not_complete, _get_run_status
from azure.cli.command_modules.acr._constants import ACR_RUN_DEFAULT_TIMEOUT_IN_SEC
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.command_modules.acr.run import acr_run
from azure.cli.command_modules.acr._azure_utils import get_blob_info
#from azure.cli.command_modules.acr._errors import DuplicateTimerTriggersNotSupported
from azure.cli.command_modules.acr._utils import get_custom_registry_credentials, prepare_source_location, get_validate_platform
from azure.mgmt.core.tools import parse_resource_id
from azext_acrcssc._client_factory import cf_acr_tasks, cf_authorization, cf_acr_registries_tasks, cf_acr_runs
from azext_acrcssc.helper._deployment import validate_and_deploy_template
from azext_acrcssc.helper._ociartifactoperations import create_oci_artifact_continuous_patch, delete_oci_artifact_continuous_patch
from azext_acrcssc._validators import validate_continuouspatch_config_v1, check_continuous_task_exists
from msrestazure.azure_exceptions import CloudError
from ._utility import convert_timespan_to_cron, transform_cron_to_cadence, create_temporary_dry_run_file, delete_temporary_dry_run_file

logger = get_logger(__name__)
DEFAULT_CHUNK_SIZE = 1024 * 4
def create_continuous_patch_v1(cmd, registry, cssc_config_file, cadence, dryrun, defer_immediate_run):
    logger.debug("Entering continuousPatchV1_creation %s %s %s", cssc_config_file, dryrun, defer_immediate_run)
    resource_group = parse_resource_id(registry.id)["resource_group"]

    if check_continuous_task_exists(cmd, registry):
        raise AzCLIError("ContinuousPatchV1 workflow already exists")

    schedule_cron_expression = convert_timespan_to_cron(cadence)
    logger.debug("task_schedule %s", schedule_cron_expression)
    validate_continuouspatch_config_v1(cssc_config_file)
    create_oci_artifact_continuous_patch(cmd, registry, cssc_config_file, dryrun)
    logger.debug("Uploading of %s completed successfully.", cssc_config_file)
    
    parameters = {
        "AcrName": {"value": registry.name},
        "AcrLocation": {"value": registry.location},
        "taskSchedule": {"value": schedule_cron_expression}
    }

    for task in CONTINUOSPATCH_TASK_DEFINITION.keys():
        encoded_task = { "value": _create_encoded_task(CONTINUOSPATCH_TASK_DEFINITION[task]["template_file"]) }
        param_name = CONTINUOSPATCH_TASK_DEFINITION[task]["parameter_name"]
        parameters[param_name] = encoded_task
 
    validate_and_deploy_template(
        cmd.cli_ctx,
        registry,
        resource_group,
        CONTINUOSPATCH_DEPLOYMENT_NAME,
        CONTINUOSPATCH_DEPLOYMENT_TEMPLATE,
        parameters,
        dryrun
    )

    logger.warning('Deployment of continuousPatchV1 creation completed successfully.')

    # force run the task after it is created
    if not dryrun and not defer_immediate_run:
        logger.warning('Triggering the continuous scanning task to run immediately')
        # Seen Managed Identity taking time, see if there can be an alternative (one alternative is to schedule the cron expression with delay)
        # NEED TO SKIP THE TIME.SLEEP IN UNIT TEST CASE OR FIND AN ALTERNATIVE SOLUITION TO MI COMPLETE
        time.sleep(30)
        _trigger_task_run(cmd, registry, resource_group, CONTINUOSPATCH_TASK_SCANREGISTRY_NAME)

def update_continuous_patch_update_v1(cmd, registry, cssc_config_file, cadence, dryrun, defer_immediate_run):
    logger.debug("Entering continuousPatchV1_update %s %s",cssc_config_file, dryrun)
    resource_group_name = parse_resource_id(registry.id)[RESOURCE_GROUP]

    if not check_continuous_task_exists(cmd, registry):
            cssc_tasks = ', '.join(CONTINUOSPATCH_ALL_TASK_NAMES)
            raise ResourceNotFoundError(f"For update operation all of these acr tasks should exists: %s {cssc_tasks}", 
                                        recommendation="Run 'az acr supply-chain workflow create' to create workflow tasks")
    
    if cadence is not None:
        _update_task_schedule(cmd, registry, cadence, resource_group_name, dryrun)
        print("Cadence has been successfully updated.")

    if(cssc_config_file is not None):
        validate_continuouspatch_config_v1(cssc_config_file)
        create_oci_artifact_continuous_patch(cmd, registry, cssc_config_file, dryrun)    
    
        if not dryrun and not defer_immediate_run:
            logger.debug('Triggering the continuous scanning task to run immediately')
            _trigger_task_run(cmd, registry, resource_group_name, CONTINUOSPATCH_TASK_SCANREGISTRY_NAME)
            
def delete_continuous_patch_v1(cmd, registry, dryrun):
    logger.debug("Entering continuousPatchV1_delete")

    cssc_tasks_exists = check_continuous_task_exists(cmd, registry)
    if not dryrun and cssc_tasks_exists:
        cssc_tasks = ', '.join(CONTINUOSPATCH_ALL_TASK_NAMES)
        logger.warning("All of these tasks will be deleted: %s", cssc_tasks)
        for taskname in CONTINUOSPATCH_ALL_TASK_NAMES:
        # bug: if one of the deletion fails, the others will not be attempted, we need to attempt to delete all of them
            _delete_task(cmd, registry, taskname, dryrun)
    
    if not cssc_tasks_exists:
        logger.warning("ContinuousPatchV1 task does not exist")

    delete_oci_artifact_continuous_patch(cmd, registry, dryrun)
    logger.debug("ContinuousPatchV1 task deleted successfully")

def list_continuous_patch_v1(cmd, registry):
    logger.debug("Entering list_continuous_patch_v1")

    if not check_continuous_task_exists(cmd, registry):
        logger.warning("ContinuousPatchV1 tasks does not exist. Run 'az acr supply-chain workflow create' to create workflow tasks")
        return
    
    acr_task_client = cf_acr_tasks(cmd.cli_ctx)
    resource_group_name = parse_resource_id(registry.id)[RESOURCE_GROUP]
    tasks_list = acr_task_client.list(resource_group_name, registry.name)
    filtered_cssc_tasks = _transform_task_list(tasks_list)
    return filtered_cssc_tasks

def acr_cssc_dry_run(cmd, registry, config_file_path):
    logger.debug("Entering acr_cssc_dry_run")

    if(config_file_path is None):
        logger.warning("--config parameter is needed to perform dry-run check.")
        return
    
    file_name = os.path.basename(config_file_path)
    config_folder_path = os.path.dirname(os.path.abspath(config_file_path))
    tmp_folder=  config_folder_path + "\\tmp"
    logger.warning(tmp_folder)
    create_temporary_dry_run_file(config_file_path, tmp_folder)
    
    resource_group_name = parse_resource_id(registry.id)[RESOURCE_GROUP]
    acr_registries_task_client = cf_acr_registries_tasks(cmd.cli_ctx)
    acr_run_client = cf_acr_runs(cmd.cli_ctx)
    source_location = prepare_source_location(
         cmd, tmp_folder, acr_registries_task_client, registry.name, resource_group_name)
    
    # TO DO: Need to find alternate command to below (doesn't run due to dependency on az context)
    #platform_os, platform_arch, platform_variant = get_validate_platform(cmd, None)

    # TO DO: Need to find alternative to below
    platform_os, platform_arch, platform_variant = "linux", None, None
    value_pair=[{"name": "CONFIGPATH", "value": f"{file_name}"}]
    request = acr_registries_task_client.models.FileTaskRunRequest(
        task_file_path=TMP_DRY_RUN_FILE_NAME,
        values_file_path=None,
        values=value_pair,
        source_location=source_location,
        timeout=None,
        platform=acr_registries_task_client.models.PlatformProperties(
            os= platform_os,
            architecture=platform_arch,
            variant= platform_variant
        ),
        credentials=_get_custom_registry_credentials(cmd, auth_mode=None),
        agent_pool_name=None,
        log_template=None
    )
    
    queued = LongRunningOperation(cmd.cli_ctx)(acr_registries_task_client.begin_schedule_run(
        resource_group_name=resource_group_name,
        registry_name=registry.name,
        run_request=request))
    run_id = queued.run_id
    logger.warning("Performing dry-run check for filter policy using acr task run id: %s", run_id)
    delete_temporary_dry_run_file(tmp_folder)
    return stream_logs(cmd, acr_run_client, run_id, registry.name, resource_group_name)

def _trigger_task_run(cmd, registry, resource_group, task_name):
    acr_task_registries_client = cf_acr_registries_tasks(cmd.cli_ctx)
    # check on the task.py file on acr's az cli on how to handle the model for other requests
    request = acr_task_registries_client.models.TaskRunRequest(
        task_id=f"{registry.id}/tasks/{task_name}"
        )
    queued_run = LongRunningOperation(cmd.cli_ctx)(
        acr_task_registries_client.begin_schedule_run(
            resource_group,
            registry.name,
            request))
    run_id = queued_run.run_id
    logger.warning("Queued a run with ID: %s", run_id)

def _create_encoded_task(task_file):
    # this is a bit of a hack, but we need to fix the path to the task's yaml,
    #relative paths don't work because we don't control where the az cli is running from
    templates_path = os.path.dirname(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
                "../templates/"))

    with open(os.path.join(templates_path, task_file), "rb") as f:
        base64_content = base64.b64encode(f.read())
        return base64_content.decode('utf-8')
    
def _update_task_schedule(cmd, registry, cadence, resource_group_name, dryrun):
        task_schedule = convert_timespan_to_cron(cadence)
        logger.debug(f"task_schedule {task_schedule}")
        acr_task_client = cf_acr_tasks(cmd.cli_ctx)
        taskUpdateParameters = acr_task_client.models.TaskUpdateParameters(
            trigger=acr_task_client.models.TriggerUpdateParameters(
                timer_triggers=[
                    acr_task_client.models.TimerTriggerUpdateParameters(
                        name='azcli_defined_schedule',
                        schedule=task_schedule
                    )
                ]
            )
        )

        if dryrun:
            logger.debug("Dry run, skipping the update of the task schedule")
            return None

        acr_task_client.begin_update(resource_group_name, registry.name, 
                                          CONTINUOSPATCH_TASK_SCANREGISTRY_NAME, taskUpdateParameters)
        
def _delete_task(cmd, registry, task_name, dryrun):
    logger.debug("Entering delete_task")
    resource_group = parse_resource_id(registry.id)["resource_group"]

    try:
        acr_tasks_client = cf_acr_tasks(cmd.cli_ctx)
        _delete_task_role_assignment(cmd.cli_ctx, acr_tasks_client, registry, resource_group, task_name, dryrun)
        if dryrun:
            logger.debug("Dry run, skipping deletion of the task: %s ", task_name)
            return None
        else:
            logger.debug(f"Deleting task {task_name}")
            LongRunningOperation(cmd.cli_ctx)(
                acr_tasks_client.begin_delete(
                    resource_group,
                    registry.name,
                    task_name))

    except Exception as exception:
        raise AzCLIError("Failed to delete task %s from registry %s : %s", task_name, registry.name, exception)

    logger.debug("Task %s deleted successfully", task_name)

def _delete_task_role_assignment(cli_ctx, acrtask_client, registry, resource_group, task_name, dryrun):
    role_client = cf_authorization(cli_ctx)
    acrtask_client = cf_acr_tasks(cli_ctx)

    task = acrtask_client.get(resource_group, registry.name, task_name)
    identity = task.identity

    if identity:
        assigned_roles = role_client.role_assignments.list_for_scope(
            registry.id,
            filter=f"principalId eq '{identity.principal_id}'"
        )

        for role in assigned_roles:
            if dryrun:
                logger.debug("Dry run, skipping deletion of role assignments, task: %s, role name: %s", task_name, role.name)
                return None
            else:
                logger.debug("Deleting role assignments of task %s from the registry", task_name)
                role_client.role_assignments.delete(
                    scope=registry.id,
                    role_assignment_name=role.name
                )

def _transform_task_list(tasks):
    transformed = []
    for obj in tasks:
        logger.debug(f"task: {dir(obj)}")
        transformed_obj = {
            "creationDate": obj.creation_date,
            "location": obj.location,
            "name": obj.name,
            "provisioningState": obj.provisioning_state,
            "systemData": obj.system_data,
            "cadence": None
        }
        logger.debug(f"transformed: {dir(transformed_obj)}")
        # Extract cadence from trigger.timerTriggers if available
        trigger = obj.trigger
        if trigger and trigger.timer_triggers:
            transformed_obj["cadence"] = transform_cron_to_cadence(trigger.timer_triggers[0].schedule)

        transformed.append(transformed_obj)

    return transformed

def _get_custom_registry_credentials(cmd,
                                    auth_mode=None,
                                    login_server=None,
                                    username=None,
                                    password=None,
                                    identity=None,
                                    is_remove=False):
    """Get the credential object from the input
    :param str auth_mode: The login mode for the source registry
    :param str login_server: The login server of custom registry
    :param str username: The username for custom registry (plain text or a key vault secret URI)
    :param str password: The password for custom registry (plain text or a key vault secret URI)
    :param str identity: The task managed identity used for the credential
    """
    acr_tasks_client = cf_acr_tasks(cmd.cli_ctx)
    # Credentials, CustomRegistryCredentials, SourceRegistryCredentials, SecretObject, \
    #     SecretObjectType = cf_acr_tasks.models.(
    #         'Credentials', 'CustomRegistryCredentials', 'SourceRegistryCredentials', 'SecretObject',
    #         'SecretObjectType',
    #         operation_group='tasks')

    source_registry_credentials = None
    if auth_mode:
        source_registry_credentials = acr_tasks_client.models.SourceRegistryCredentials(
            login_mode=auth_mode)
        
    custom_registries = None
    if login_server:
        # if null username and password (or identity), then remove the credential
        custom_reg_credential = None

        is_identity_credential = False
        if not username and not password:
            is_identity_credential = identity is not None

        if not is_remove:
            if is_identity_credential:
                custom_reg_credential = acr_tasks_client.models.CustomRegistryCredentials(
                    identity=identity
                )
            else:
                custom_reg_credential = acr_tasks_client.models.CustomRegistryCredentials(
                    user_name=acr_tasks_client.models.SecretObject(
                        type=acr_tasks_client.models.SecretObjectType.vaultsecret if _is_vault_secret(
                            cmd, username)else acr_tasks_client.models.SecretObjectType.opaque,
                        value=username
                    ),
                    password=acr_tasks_client.models.SecretObject(
                        type=acr_tasks_client.models.SecretObjectType.vaultsecret if _is_vault_secret(
                            cmd, password) else acr_tasks_client.models.SecretObjectType.opaque,
                        value=password
                    ),
                    identity=identity
                )

        custom_registries = {login_server: custom_reg_credential}

    return acr_tasks_client.models.Credentials(
        source_registry=source_registry_credentials,
        custom_registries=custom_registries
    )

def _is_vault_secret(cmd, credential):
    keyvault_dns = None
    try:
        keyvault_dns = cmd.cli_ctx.cloud.suffixes.keyvault_dns
    except Exception as e:
        return False
    if credential is not None:
        return keyvault_dns.upper() in credential.upper()
    return False

def stream_logs(cmd, client,
                run_id,
                registry_name,
                resource_group_name,
                timeout=ACR_RUN_DEFAULT_TIMEOUT_IN_SEC,
                no_format=False,
                raise_error_on_failure=False):
    log_file_sas = None
    error_msg = "Could not get logs for ID: {}".format(run_id)
    try:
        response = client.get_log_sas_url(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            run_id=run_id)
        log_file_sas = response.log_link
    except (AttributeError, CloudError) as e:
        logger.debug("%s Exception: %s", error_msg, e)
        raise AzCLIError(error_msg)

    account_name, endpoint_suffix, container_name, blob_name, sas_token = get_blob_info(
        log_file_sas)
    AppendBlobService = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE, 'blob#AppendBlobService')
    if not timeout:
        timeout = ACR_RUN_DEFAULT_TIMEOUT_IN_SEC
    # _download_logs(AppendBlobService(
    #                     account_name=account_name,
    #                     sas_token=sas_token,
    #                     endpoint_suffix=endpoint_suffix),
    #                 container_name,
    #                 blob_name)
    _stream_logs(True, DEFAULT_CHUNK_SIZE,
                    timeout,
                    AppendBlobService(
                        account_name=account_name,
                        sas_token=sas_token,
                        endpoint_suffix=endpoint_suffix),
                    container_name,
                    blob_name,
                    raise_error_on_failure)
    
def _download_logs(# pylint: disable=too-many-locals, too-many-statements, too-many-branches
                 blob_service,
                 container_name,
                 blob_name,
                 ):

    log_exist = False
    
    try:
        # Need to call "exists" API to prevent storage SDK logging BlobNotFound error
        log_exist = blob_service.exists(
            container_name=container_name, blob_name=blob_name)
        if log_exist:
            props = blob_service.get_blob_properties(
                container_name=container_name, blob_name=blob_name)
            metadata = props.metadata
            lease_state = props.properties.lease.state
        else:
            # Wait a little bit before checking the existence again
            time.sleep(1)
    except (AttributeError, AzureHttpError):
        pass
    
    while(lease_state != "available"):
        time.sleep(1)
        blob_service.get_blob_properties(
                    container_name=container_name, blob_name=blob_name)
        lease_state = props.properties.lease.state
    ## If we don't add sleep timer, it's stripping some of the text
    time.sleep(5)
    blob_text=blob_service.get_blob_to_text(
        container_name=container_name,
        blob_name=blob_name)
    #logger.warning(f"{blob_text.content}")
    _remove_internal_acr_statements(blob_text.content)

def _remove_internal_acr_statements(blob_content):
    lines = blob_content.split("\n")
    starting_identifier = "DRY RUN mode enabled"
    terminating_identifier = "Total matches found"
    print_line = False
    
    for line in lines:
        if line.startswith(starting_identifier):
            print_line = True
        elif line.startswith(terminating_identifier):
            print(line)
            print_line = False
        
        if print_line:
            print(line)
    
def _stream_logs(no_format,  # pylint: disable=too-many-locals, too-many-statements, too-many-branches
                 byte_size,
                 timeout_in_seconds,
                 blob_service,
                 container_name,
                 blob_name,
                 raise_error_on_failure):

    if not no_format:
        colorama.init()

    log_exist = False
    stream = BytesIO()
    metadata = {}
    start = 0
    end = byte_size - 1
    available = 0
    sleep_time = 1
    max_sleep_time = 15
    num_fails = 0
    num_fails_for_backoff = 3
    consecutive_sleep_in_sec = 0

    # Try to get the initial properties so there's no waiting.
    # If the storage call fails, we'll just sleep and try again after.
    try:
        # Need to call "exists" API to prevent storage SDK logging BlobNotFound error
        log_exist = blob_service.exists(
            container_name=container_name, blob_name=blob_name)

        if log_exist:
            props = blob_service.get_blob_properties(
                container_name=container_name, blob_name=blob_name)
            metadata = props.metadata
            available = props.properties.content_length
        else:
            # Wait a little bit before checking the existence again
            time.sleep(1)
    except (AttributeError, AzureHttpError):
        pass

    while (_blob_is_not_complete(metadata) or start < available):
        while start < available:
            # Success! Reset our polling backoff.
            sleep_time = 1
            num_fails = 0
            consecutive_sleep_in_sec = 0

            try:
                old_byte_size = len(stream.getvalue())
                blob_service.get_blob_to_stream(
                    container_name=container_name,
                    blob_name=blob_name,
                    start_range=start,
                    end_range=end,
                    stream=stream)

                curr_bytes = stream.getvalue()
                new_byte_size = len(curr_bytes)
                amount_read = new_byte_size - old_byte_size
                start += amount_read
                end = start + byte_size - 1

                # Only scan what's newly read. If nothing is read, default to 0.
                min_scan_range = max(new_byte_size - amount_read - 1, 0)
                for i in range(new_byte_size - 1, min_scan_range, -1):
                    if curr_bytes[i - 1:i + 1] == b'\r\n':
                        flush = curr_bytes[:i]  # won't print \n
                        stream = BytesIO()
                        stream.write(curr_bytes[i + 1:])
                        _remove_internal_acr_statements(flush.decode('utf-8', errors='ignore'))
                        #print(flush.decode('utf-8', errors='ignore'))
                        break
            except AzureHttpError as ae:
                if ae.status_code != 404:
                    raise AzCLIError(ae)
            except KeyboardInterrupt:
                curr_bytes = stream.getvalue()
                if curr_bytes:
                    _remove_internal_acr_statements(curr_bytes.decode('utf-8', errors='ignore'))
                    #print(curr_bytes.decode('utf-8', errors='ignore'))
                return

        try:
            if log_exist:
                props = blob_service.get_blob_properties(
                    container_name=container_name, blob_name=blob_name)
                metadata = props.metadata
                available = props.properties.content_length
            else:
                log_exist = blob_service.exists(
                    container_name=container_name, blob_name=blob_name)
        except AzureHttpError as ae:
            if ae.status_code != 404:
                raise AzCLIError(ae)
        except KeyboardInterrupt:
            if curr_bytes:
                _remove_internal_acr_statements(curr_bytes.decode('utf-8', errors='ignore'))
                #print(curr_bytes.decode('utf-8', errors='ignore'))
            return
        except Exception as err:
            raise AzCLIError(err)

        if consecutive_sleep_in_sec > timeout_in_seconds:
            # Flush anything remaining in the buffer - this would be the case
            # if the file has expired and we weren't able to detect any \r\n
            curr_bytes = stream.getvalue()
            if curr_bytes:
                _remove_internal_acr_statements(curr_bytes.decode('utf-8', errors='ignore'))
                #print(curr_bytes.decode('utf-8', errors='ignore'))

            logger.warning("Failed to find any new logs in %d seconds. Client will stop polling for additional logs.",
                           consecutive_sleep_in_sec)
            return

        # If no new data available but not complete, sleep before trying to process additional data.
        if (_blob_is_not_complete(metadata) and start >= available):
            num_fails += 1

            logger.debug(
                "Failed to find new content %d times in a row", num_fails)
            if num_fails >= num_fails_for_backoff:
                num_fails = 0
                sleep_time = min(sleep_time * 2, max_sleep_time)
                logger.debug("Resetting failure count to %d", num_fails)

            rnd = uniform(1, 2)  # 1.0 <= x < 2.0
            total_sleep_time = sleep_time + rnd
            consecutive_sleep_in_sec += total_sleep_time
            logger.debug("Base sleep time: %d, random delay: %d, total: %d, consecutive: %d",
                         sleep_time, rnd, total_sleep_time, consecutive_sleep_in_sec)
            time.sleep(total_sleep_time)

    # One final check to see if there's anything in the buffer to flush
    # E.g., metadata has been set and start == available, but the log file
    # didn't end in \r\n, so we were unable to flush out the final contents.
    curr_bytes = stream.getvalue()
    if curr_bytes:
        _remove_internal_acr_statements(curr_bytes.decode('utf-8', errors='ignore'))
        #print(curr_bytes.decode('utf-8', errors='ignore'))

    build_status = _get_run_status(metadata).lower()
    logger.debug("status was: '%s'", build_status)

    if raise_error_on_failure:
        if build_status in ('internalerror', 'failed'):
            raise AzCLIError("Run failed")
        if build_status == 'timedout':
            raise AzCLIError("Run timed out")
        if build_status == 'canceled':
            raise AzCLIError("Run was canceled")
