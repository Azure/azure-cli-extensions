# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught
# pylint: disable=logging-fstring-interpolation
import base64
import os
import tempfile
import time
from knack.log import get_logger
from ._constants import (
    CONTINUOSPATCH_DEPLOYMENT_NAME,
    CONTINUOSPATCH_DEPLOYMENT_TEMPLATE,
    CONTINUOSPATCH_ALL_TASK_NAMES,
    CONTINUOSPATCH_TASK_DEFINITION,
    CONTINUOSPATCH_TASK_SCANREGISTRY_NAME,
    RESOURCE_GROUP,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1,
    TMP_DRY_RUN_FILE_NAME,
    CONTINUOUS_PATCHING_WORKFLOW_NAME,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    CONTINUOSPATCH_TASK_PATCHIMAGE_NAME,
    CONTINUOSPATCH_TASK_SCANIMAGE_NAME,
    DESCRIPTION,
    TaskRunStatus)
from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.command_modules.acr._utils import prepare_source_location
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.core.tools import parse_resource_id
from azext_acrcssc._client_factory import cf_acr_tasks, cf_authorization, cf_acr_registries_tasks, cf_acr_runs
from azext_acrcssc.helper._deployment import validate_and_deploy_template
from azext_acrcssc._validators import check_continuous_task_exists, check_continuous_task_config_exists
from datetime import datetime, timezone, timedelta
from ._utility import convert_timespan_to_cron, transform_cron_to_schedule, create_temporary_dry_run_file, delete_temporary_dry_run_file
from azext_acrcssc.helper._ociartifactoperations import create_oci_artifact_continuous_patch, get_oci_artifact_continuous_patch, delete_oci_artifact_continuous_patch
from ._workflow_status import WorkflowTaskStatus
from azure.cli.core.commands.progress import IndeterminateProgressBar

logger = get_logger(__name__)


def create_update_continuous_patch_v1(cmd, registry, cssc_config_file, schedule, dryrun, run_immediately, is_create_workflow=True):
    logger.debug(f"Entering continuousPatchV1_creation {cssc_config_file} {dryrun} {run_immediately}")
    resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]
    schedule_cron_expression = None
    if schedule is not None:
        schedule_cron_expression = convert_timespan_to_cron(schedule)
    logger.debug(f"converted schedule to cron expression: {schedule_cron_expression}")
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
        create_oci_artifact_continuous_patch(registry, cssc_config_file, dryrun)
        logger.debug(f"Uploading of {cssc_config_file} completed successfully.")

    _eval_trigger_run(cmd, registry, resource_group, run_immediately)

    # on 'update' schedule is optional
    if schedule is None:
        task = get_task(cmd, registry, CONTINUOSPATCH_TASK_SCANREGISTRY_NAME)
        trigger = task.trigger
        if trigger and trigger.timer_triggers:
            schedule_cron_expression = trigger.timer_triggers[0].schedule

    next_date = get_next_date(schedule_cron_expression)
    print(f"Continuous Patching workflow scheduled to run next at: {next_date} UTC")


def _create_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dry_run):
    parameters = {
        "AcrName": {"value": registry.name},
        "AcrLocation": {"value": registry.location},
        "taskSchedule": {"value": schedule_cron_expression}
    }

    for task in CONTINUOSPATCH_TASK_DEFINITION:
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

    logger.warning(f"Deployment of {CONTINUOUS_PATCHING_WORKFLOW_NAME} tasks completed successfully.")


def _update_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dry_run):
    if schedule_cron_expression is not None:
        _update_task_schedule(cmd, registry, schedule_cron_expression, resource_group, dry_run)


def _eval_trigger_run(cmd, registry, resource_group, run_immediately):
    if run_immediately:
        logger.warning(f'Triggering the {CONTINUOSPATCH_TASK_SCANREGISTRY_NAME} to run immediately')
        # Seen Managed Identity taking time, see if there can be an alternative (one alternative is to schedule the cron expression with delay)
        # NEED TO SKIP THE TIME.SLEEP IN UNIT TEST CASE OR FIND AN ALTERNATIVE SOLUITION TO MI COMPLETE
        time.sleep(30)
        _trigger_task_run(cmd, registry, resource_group, CONTINUOSPATCH_TASK_SCANREGISTRY_NAME)


def delete_continuous_patch_v1(cmd, registry, dryrun):
    logger.debug("Entering delete_continuous_patch_v1")
    cssc_tasks_exists = check_continuous_task_exists(cmd, registry)
    cssc_config_exists = check_continuous_task_config_exists(cmd, registry)
    if not dryrun and (cssc_tasks_exists or cssc_config_exists):
        cssc_tasks = ', '.join(CONTINUOSPATCH_ALL_TASK_NAMES)
        logger.warning(f"All of these tasks will be deleted: {cssc_tasks}")
        for taskname in CONTINUOSPATCH_ALL_TASK_NAMES:
            # bug: if one of the deletion fails, the others will not be attempted, we need to attempt to delete all of them
            _delete_task(cmd, registry, taskname, dryrun)
            logger.warning(f"Task {taskname} deleted.")
        logger.warning(f"Deleting {CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}")
        delete_oci_artifact_continuous_patch(cmd, registry, dryrun)

    if not cssc_tasks_exists:
        logger.warning(f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow does not exist")


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


def acr_cssc_dry_run(cmd, registry, config_file_path, is_create=True):
    logger.debug(f"Entering acr_cssc_dry_run with parameters: {registry} {config_file_path}")

    if config_file_path is None:
        logger.error("--config parameter is needed to perform dry-run check.")
        return
    if is_create and check_continuous_task_exists(cmd, registry):
        raise AzCLIError(f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow task already exists. Use 'az acr supply-chain workflow update' command to perform updates.")
    try:
        file_name = os.path.basename(config_file_path)
        tmp_folder = os.path.join(os.getcwd(), tempfile.mkdtemp(prefix="cli_temp_cssc"))
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
        return WorkflowTaskStatus.remove_internal_acr_statements(WorkflowTaskStatus.generate_logs(cmd, acr_run_client, run_id, registry.name, resource_group_name))
    finally:
        delete_temporary_dry_run_file(tmp_folder)


def cancel_continuous_patch_runs(cmd, resource_group_name, registry_name):
    logger.debug("Entering cancel_continuous_patch_v1")
    acr_task_run_client = cf_acr_runs(cmd.cli_ctx)
    running_tasks = _get_taskruns_with_filter(
        acr_task_run_client,
        registry_name=registry_name,
        resource_group_name=resource_group_name,
        status_filter=[TaskRunStatus.Running.value, TaskRunStatus.Queued.value, TaskRunStatus.Started.value],
        taskname_filter=[CONTINUOSPATCH_TASK_SCANREGISTRY_NAME, CONTINUOSPATCH_TASK_SCANIMAGE_NAME, CONTINUOSPATCH_TASK_PATCHIMAGE_NAME])

    for task in running_tasks:
        logger.warning("Sending request to cancel task %s", task.name)
        acr_task_run_client.begin_cancel(resource_group_name, registry_name, task.name)
    logger.warning("All active running workflow tasks have been cancelled.")


def track_scan_progress(cmd, resource_group_name, registry, status):
    logger.debug("Entering track_scan_progress")

    config = get_oci_artifact_continuous_patch(cmd, registry)

    return _retrieve_logs_for_image(cmd, registry, resource_group_name, config.schedule, status)


def _retrieve_logs_for_image(cmd, registry, resource_group_name, schedule, workflow_status=None):
    image_status = []
    acr_task_run_client = cf_acr_runs(cmd.cli_ctx)

    # get all the tasks executed since the last schedule, add a day to make sure we are not running into and edge case with the date
    today = datetime.now(timezone.utc)
    # delta = datetime.timedelta(days=int(schedule) + 1)
    delta = timedelta(days=int(schedule))  # use the schedule as is, we are running into issues we are querying too much and take time to filter
    previous_date = today - delta
    previous_date_filter = previous_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    # th API returns an iterator, if we want to be able to modify it, we need to convert it to a list
    scan_taskruns = _get_taskruns_with_filter(
        acr_task_run_client,
        registry.name,
        resource_group_name,
        taskname_filter=[CONTINUOSPATCH_TASK_SCANIMAGE_NAME],
        date_filter=previous_date_filter)

    patch_taskruns = _get_taskruns_with_filter(
        acr_task_run_client,
        registry.name,
        resource_group_name,
        taskname_filter=[CONTINUOSPATCH_TASK_PATCHIMAGE_NAME],
        date_filter=previous_date_filter)

    start_time = time.time()

    progress_indicator = IndeterminateProgressBar(cmd.cli_ctx)
    progress_indicator.begin()

    image_status = WorkflowTaskStatus.from_taskrun(cmd, acr_task_run_client, registry, scan_taskruns, patch_taskruns, progress_indicator=progress_indicator)
    if workflow_status:
        filtered_image_status = [image for image in image_status if image.status() == workflow_status]
        image_status = filtered_image_status

    end_time = time.time()
    execution_time = end_time - start_time
    logger.debug(f"Execution time: {execution_time} seconds / tasks filtered: {len(scan_taskruns)} + {len(patch_taskruns)}")

    progress_indicator.end()

    return image_status


def _get_taskruns_with_filter(acr_task_run_client, registry_name, resource_group_name, taskname_filter=None, date_filter=None, status_filter=None, top=1000):
    # filters based on OData, found in ACR.BuildRP.DataModels - RunFilter.cs
    filter = ""
    if taskname_filter:
        taskname_filter_str = "', '".join(taskname_filter)
        filter += f"TaskName in ('{taskname_filter_str}')"

    if date_filter:
        if filter != "":
            filter += " and "
        filter += f"createTime ge {date_filter}"

    if status_filter:
        if filter != "":
            filter += " and "
        status_filter_str = "', '".join(status_filter)
        filter += f"Status in ('{status_filter_str}')"

    taskruns = acr_task_run_client.list(resource_group_name, registry_name, filter=filter, top=top)
    return list(taskruns)


def _trigger_task_run(cmd, registry, resource_group, task_name):
    acr_task_registries_client = cf_acr_registries_tasks(cmd.cli_ctx)
    request = acr_task_registries_client.models.TaskRunRequest(
        task_id=f"{registry.id}/tasks/{task_name}")
    queued_run = LongRunningOperation(cmd.cli_ctx)(
        acr_task_registries_client.begin_schedule_run(
            resource_group,
            registry.name,
            request))
    run_id = queued_run.run_id
    print(f"Queued {CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow task '{task_name}' with run ID: {run_id}. Use 'az acr task logs --registry {registry.name} --run-id {run_id}' to view the logs.")


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
    logger.debug(f"converted schedule to cron_expression: {cron_expression}")
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
        print("Schedule has been successfully updated.")
    except Exception as exception:
        raise AzCLIError(f"Failed to update the task schedule: {exception}")


def _delete_task(cmd, registry, task_name, dryrun):
    logger.debug("Entering delete_task")
    resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]

    try:
        acr_tasks_client = cf_acr_tasks(cmd.cli_ctx)
        _delete_task_role_assignment(cmd.cli_ctx, acr_tasks_client, registry, resource_group, task_name, dryrun)

        if dryrun:
            logger.debug(f"Dry run, skipping deletion of the task: {task_name}")
            return None
        logger.debug(f"Deleting task {task_name}")
        LongRunningOperation(cmd.cli_ctx)(
            acr_tasks_client.begin_delete(
                resource_group,
                registry.name,
                task_name))

    except Exception as exception:
        raise AzCLIError(f"Failed to delete task {task_name} from registry {registry.name} : {exception}")

    logger.debug(f"Task {task_name} deleted successfully")


def _delete_task_role_assignment(cli_ctx, acrtask_client, registry, resource_group, task_name, dryrun):
    role_client = cf_authorization(cli_ctx)
    acrtask_client = cf_acr_tasks(cli_ctx)

    try:
        task = acrtask_client.get(resource_group, registry.name, task_name)
    except ResourceNotFoundError:
        logger.debug(f"Task {task_name} does not exist in registry {registry.name}")
        logger.debug("Continuing with deletion")
        return None

    identity = task.identity

    if identity:
        assigned_roles = role_client.role_assignments.list_for_scope(
            registry.id,
            filter=f"principalId eq '{identity.principal_id}'"
        )

        for role in assigned_roles:
            if dryrun:
                logger.debug(f"Dry run, skipping deletion of role assignments, task: {task_name}, role name: {role.name}")
                return None
            logger.debug(f"Deleting role assignments of task {task_name} from the registry")
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
            "schedule": None,
            "description": CONTINUOSPATCH_TASK_DEFINITION[task.name][DESCRIPTION]
        }

        # Extract schedule from trigger.timerTriggers if available
        trigger = task.trigger
        if trigger and trigger.timer_triggers:
            transformed_obj["schedule"] = transform_cron_to_schedule(trigger.timer_triggers[0].schedule)
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


def get_next_date(cron_expression):
    from croniter import croniter
    now = datetime.now(timezone.utc)
    cron = croniter(cron_expression, now, expand_from_start_time=False)
    next_date = cron.get_next(datetime)
    return str(next_date)


def get_task(cmd, registry, task_name=""):
    acrtask_client = cf_acr_tasks(cmd.cli_ctx)
    resourceid = parse_resource_id(registry.id)
    resource_group = resourceid[RESOURCE_GROUP]

    try:
        return acrtask_client.get(resource_group, registry.name, task_name)
    except Exception as exception:
        logger.debug(f"Failed to find task {task_name} from registry {registry.name} : {exception}")
        return None
