# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import base64
from io import BytesIO
import os
from random import uniform
import re
import tempfile
import time
import colorama
from knack.log import get_logger
from ._constants import (
    CONTINUOSPATCH_DEPLOYMENT_NAME,
    CONTINUOSPATCH_DEPLOYMENT_TEMPLATE,
    CONTINUOSPATCH_ALL_TASK_NAMES,
    CONTINUOSPATCH_TASK_DEFINITION,
    CONTINUOSPATCH_TASK_SCANREGISTRY_NAME,
    RESOURCE_GROUP,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1,
    TMP_DRY_RUN_FILE_NAME,
    CONTINUOUS_PATCHING_WORKFLOW_NAME,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    TASK_RUN_STATUS_FAILED,
    TASK_RUN_STATUS_SUCCESS,
    TASK_RUN_STATUS_RUNNING)
from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.command_modules.acr._stream_utils import stream_logs
from azure.cli.command_modules.acr._stream_utils import _stream_logs, _blob_is_not_complete, _get_run_status
from azure.cli.command_modules.acr._constants import ACR_RUN_DEFAULT_TIMEOUT_IN_SEC
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.command_modules.acr._azure_utils import get_blob_info
from azure.cli.command_modules.acr._utils import prepare_source_location
from azure.mgmt.core.tools import parse_resource_id
from azext_acrcssc._client_factory import cf_acr_tasks, cf_authorization, cf_acr_registries_tasks, cf_acr_runs, cf_acr_taskruns
from azext_acrcssc.helper._deployment import validate_and_deploy_template
from azext_acrcssc.helper._ociartifactoperations import create_oci_artifact_continuous_patch, delete_oci_artifact_continuous_patch
from azext_acrcssc._validators import check_continuous_task_exists
from msrestazure.azure_exceptions import CloudError
from ._utility import convert_timespan_to_cron, transform_cron_to_cadence, create_temporary_dry_run_file, delete_temporary_dry_run_file

logger = get_logger(__name__)
DEFAULT_CHUNK_SIZE = 1024 * 4


def create_update_continuous_patch_v1(cmd, registry, cssc_config_file, cadence, dryrun, defer_immediate_run, is_create_workflow=True):
    logger.debug("Entering continuousPatchV1_creation %s %s %s", cssc_config_file, dryrun, defer_immediate_run)
    resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]
    schedule_cron_expression = None
    if cadence is not None:
        schedule_cron_expression = convert_timespan_to_cron(cadence)
    logger.debug("converted cadence to cron expression: %s", schedule_cron_expression)
    cssc_tasks_exists = check_continuous_task_exists(cmd, registry)
    if is_create_workflow:
        if cssc_tasks_exists:
            raise AzCLIError(f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow task already exists. Use 'az acr supply-chain workflow update' command to perform updates.")
        _create_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dryrun)
    else:
        if not cssc_tasks_exists:
            raise AzCLIError(f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow task does not exist. Use 'az acr supply-chain workflow create' command to create {CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow.")
        _update_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dryrun)

    if cssc_config_file is not None:
        create_oci_artifact_continuous_patch(cmd, registry, cssc_config_file, dryrun)
        logger.debug("Uploading of %s completed successfully.", cssc_config_file)

    _eval_trigger_run(cmd, registry, resource_group, defer_immediate_run)


def _create_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dry_run):
    parameters = {
        "AcrName": {"value": registry.name},
        "AcrLocation": {"value": registry.location},
        "taskSchedule": {"value": schedule_cron_expression}
    }

    for task in CONTINUOSPATCH_TASK_DEFINITION.keys():
        encoded_task = {"value": _create_encoded_task(CONTINUOSPATCH_TASK_DEFINITION[task]["template_file"])}
        param_name = CONTINUOSPATCH_TASK_DEFINITION[task]["parameter_name"]
        parameters[param_name] = encoded_task

    validate_and_deploy_template(
        cmd.cli_ctx,
        registry,
        resource_group,
        CONTINUOSPATCH_DEPLOYMENT_NAME,
        CONTINUOSPATCH_DEPLOYMENT_TEMPLATE,
        parameters,
        dry_run
    )

    logger.warning("Deployment of %s tasks completed successfully.", CONTINUOUS_PATCHING_WORKFLOW_NAME)


def _update_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dry_run):
    if schedule_cron_expression is not None:
        _update_task_schedule(cmd, registry, schedule_cron_expression, resource_group, dry_run)


def _eval_trigger_run(cmd, registry, resource_group, defer_immediate_run):
    if not defer_immediate_run:
        logger.warning(f'Triggering the {CONTINUOSPATCH_TASK_SCANREGISTRY_NAME} to run immediately')
        # Seen Managed Identity taking time, see if there can be an alternative (one alternative is to schedule the cron expression with delay)
        # NEED TO SKIP THE TIME.SLEEP IN UNIT TEST CASE OR FIND AN ALTERNATIVE SOLUITION TO MI COMPLETE
        time.sleep(30)
        _trigger_task_run(cmd, registry, resource_group, CONTINUOSPATCH_TASK_SCANREGISTRY_NAME)


def delete_continuous_patch_v1(cmd, registry, dryrun):
    logger.debug("Entering delete_continuous_patch_v1")
    cssc_tasks_exists = check_continuous_task_exists(cmd, registry)
    if not dryrun and cssc_tasks_exists:
        cssc_tasks = ', '.join(CONTINUOSPATCH_ALL_TASK_NAMES)
        logger.warning("All of these tasks will be deleted: %s", cssc_tasks)
        for taskname in CONTINUOSPATCH_ALL_TASK_NAMES:
            # bug: if one of the deletion fails, the others will not be attempted, we need to attempt to delete all of them
            _delete_task(cmd, registry, taskname, dryrun)
            logger.warning("Task %s deleted.", taskname)

    if not cssc_tasks_exists:
        logger.warning(f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow task does not exist")

    logger.warning("Deleting %s/%s:%s", CSSC_WORKFLOW_POLICY_REPOSITORY, CONTINUOSPATCH_OCI_ARTIFACT_CONFIG, CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1)
    delete_oci_artifact_continuous_patch(cmd, registry, dryrun)


def list_continuous_patch_v1(cmd, registry):
    logger.debug("Entering list_continuous_patch_v1")

    if not check_continuous_task_exists(cmd, registry):
        logger.warning(f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow task does not exist. Run 'az acr supply-chain workflow create' to create workflow tasks")
        return

    acr_task_client = cf_acr_tasks(cmd.cli_ctx)
    resource_group_name = parse_resource_id(registry.id)[RESOURCE_GROUP]
    tasks_list = acr_task_client.list(resource_group_name, registry.name)
    filtered_cssc_tasks = _transform_task_list(tasks_list)
    return filtered_cssc_tasks


def acr_cssc_dry_run(cmd, registry, config_file_path):
    logger.debug("Entering acr_cssc_dry_run with parameters: %s %s", registry, config_file_path)

    if config_file_path is None:
        logger.error("--config parameter is needed to perform dry-run check.")
        return
    try:
        file_name = os.path.basename(config_file_path)
        # config_folder_path = os.path.dirname(os.path.abspath(config_file_path))
        tmp_folder = os.path.join(os.getcwd(), tempfile.mkdtemp(prefix="cli_temp_cssc"))
        print(f"Temporary directory created at: {tmp_folder}")
        create_temporary_dry_run_file(config_file_path, tmp_folder)

        resource_group_name = parse_resource_id(registry.id)[RESOURCE_GROUP]
        acr_registries_task_client = cf_acr_registries_tasks(cmd.cli_ctx)
        acr_run_client = cf_acr_runs(cmd.cli_ctx)
        source_location = prepare_source_location(
            cmd,
            tmp_folder,
            acr_registries_task_client,
            registry.name,
            resource_group_name)

        OS = acr_run_client.models.OS
        Architecture = acr_run_client.models.Architecture

        # TODO: when the extension merges back into the acr module, we need to reuse the 'get_validate_platform()' from ACR modules (src\azure-cli\azure\cli\command_modules\acr\_utils.py)
        platform_os = OS.linux.value
        platform_arch = Architecture.amd64.value
        platform_variant = None

        value_pair = [{"name": "CONFIGPATH", "value": f"{file_name}"}]
        request = acr_registries_task_client.models.FileTaskRunRequest(
            task_file_path=TMP_DRY_RUN_FILE_NAME,
            values_file_path=None,
            values=value_pair,
            source_location=source_location,
            timeout=None,
            platform=acr_registries_task_client.models.PlatformProperties(
                os=platform_os,
                architecture=platform_arch,
                variant=platform_variant
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
        return generate_logs(cmd, acr_run_client, run_id, registry.name, resource_group_name)
    finally:
        delete_temporary_dry_run_file(tmp_folder)


def _trigger_task_run(cmd, registry, resource_group, task_name):
    acr_task_registries_client = cf_acr_registries_tasks(cmd.cli_ctx)
    # check on the task.py file on acr's az cli on how to handle the model for other requests
    request = acr_task_registries_client.models.TaskRunRequest(
        task_id=f"{registry.id}/tasks/{task_name}")
    queued_run = LongRunningOperation(cmd.cli_ctx)(
        acr_task_registries_client.begin_schedule_run(
            resource_group,
            registry.name,
            request))
    run_id = queued_run.run_id
    print(f"Queued {CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow task '{task_name}' with run ID: {run_id}. Use 'az acr task logs' to view the logs.")


def _create_encoded_task(task_file):
    # this is a bit of a hack, but we need to fix the path to the task's yaml,
    # relative paths don't work because we don't control where the az cli is running from
    templates_path = os.path.dirname(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../templates/"))

    with open(os.path.join(templates_path, task_file), "rb") as f:
        base64_content = base64.b64encode(f.read())
        return base64_content.decode('utf-8')


def _update_task_schedule(cmd, registry, cron_expression, resource_group_name, dryrun):
    logger.debug(f"converted cadence to cron_expression: {cron_expression}")
    acr_task_client = cf_acr_tasks(cmd.cli_ctx)
    taskUpdateParameters = acr_task_client.models.TaskUpdateParameters(
        trigger=acr_task_client.models.TriggerUpdateParameters(
            timer_triggers=[
                acr_task_client.models.TimerTriggerUpdateParameters(
                    name='azcli_defined_schedule',
                    schedule=cron_expression
                )
            ]
        )
    )

    if dryrun:
        logger.debug("Dry run, skipping the update of the task schedule")
        return None
    try:
        acr_task_client.begin_update(resource_group_name, registry.name,
                                 CONTINUOSPATCH_TASK_SCANREGISTRY_NAME,
                                 taskUpdateParameters)
        print("Cadence has been successfully updated.")
    except Exception as exception:
        raise AzCLIError(f"Failed to update the task schedule: {exception}")


def _delete_task(cmd, registry, task_name, dryrun):
    logger.debug("Entering delete_task")
    resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]

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
    for task in tasks:
        transformed_obj = {
            "creationDate": task.creation_date,
            "location": task.location,
            "name": task.name,
            "provisioningState": task.provisioning_state,
            "systemData": task.system_data,
            "cadence": None
        }

        # Extract cadence from trigger.timerTriggers if available
        trigger = task.trigger
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
    except Exception:
        return False
    if credential is not None:
        return keyvault_dns.upper() in credential.upper()
    return False


def generate_logs(cmd,
                  client,
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

    run_status = TASK_RUN_STATUS_RUNNING
    while _evaluate_task_run_nonterminal_state(run_status):
        run_status = _get_run_status(client, resource_group_name, registry_name, run_id)
        if _evaluate_task_run_nonterminal_state(run_status):
            logger.debug(f"Waiting for the task run to complete. Current status: {run_status}")
            time.sleep(2)

    _download_logs(AppendBlobService(
        account_name=account_name,
        sas_token=sas_token,
        endpoint_suffix=endpoint_suffix),
        container_name,
        blob_name)


def _evaluate_task_run_nonterminal_state(run_status):
    return run_status != TASK_RUN_STATUS_SUCCESS and run_status != TASK_RUN_STATUS_FAILED


def _get_run_status(client, resource_group_name, registry_name, run_id):
    try:
        response = client.get(resource_group_name, registry_name, run_id)
        return response.status
    except (AttributeError, CloudError):
        return None


def _download_logs(blob_service,
                   container_name,
                   blob_name):
    blob_text = blob_service.get_blob_to_text(
        container_name=container_name,
        blob_name=blob_name)
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
