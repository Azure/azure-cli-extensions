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
import logging
from knack.log import get_logger
from knack.util import CLIError
from ._constants import (
    CONTINUOUSPATCH_DEPLOYMENT_NAME,
    CONTINUOUSPATCH_DEPLOYMENT_TEMPLATE,
    CONTINUOUSPATCH_ALL_TASK_NAMES,
    CONTINUOUSPATCH_TASK_DEFINITION,
    CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME,
    RESOURCE_GROUP,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1,
    TMP_DRY_RUN_FILE_NAME,
    CONTINUOUS_PATCHING_WORKFLOW_NAME,
    ERROR_MESSAGE_WORKFLOW_TASKS_DOES_NOT_EXIST,
    ERROR_MESSAGE_WORKFLOW_TASKS_ALREADY_EXISTS,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME,
    CONTINUOUSPATCH_TASK_SCANIMAGE_NAME,
    DESCRIPTION,
    WORKFLOW_VALIDATION_MESSAGE,
    TaskRunStatus)
from azure.cli.core.azclierror import AzCLIError, InvalidArgumentValueError, ResourceNotFoundError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.progress import IndeterminateProgressBar
from azure.cli.command_modules.acr._utils import prepare_source_location
from azure.cli.command_modules.acr._archive_utils import logger as acr_archive_utils_logger
from azure.core.exceptions import HttpResponseError
from azure.mgmt.core.tools import parse_resource_id
from azext_acrcssc._client_factory import cf_acr_tasks, cf_authorization, cf_acr_registries_tasks, cf_acr_runs
from azext_acrcssc.helper._deployment import validate_and_deploy_template
from azext_acrcssc._validators import check_continuous_task_exists, check_continuous_task_config_exists
from datetime import datetime, timezone, timedelta
from ._utility import convert_timespan_to_cron, convert_cron_to_schedule, create_temporary_dry_run_file, delete_temporary_dry_run_file
from azext_acrcssc.helper._ociartifactoperations import create_oci_artifact_continuous_patch, get_oci_artifact_continuous_patch, delete_oci_artifact_continuous_patch
from ._workflow_status import WorkflowTaskStatus

logger = get_logger(__name__)


def create_update_continuous_patch_v1(cmd,
                                      registry,
                                      cssc_config_file,
                                      schedule,
                                      dryrun,
                                      run_immediately,
                                      is_create_workflow=True):

    logger.debug(f"Entering continuousPatchV1_creation {cssc_config_file} {dryrun} {run_immediately}")

    resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]
    schedule_cron_expression = None
    cssc_tasks_exists, task_list = check_continuous_task_exists(cmd, registry)

    if schedule:
        schedule_cron_expression = convert_timespan_to_cron(schedule)
        logger.debug(f"converted schedule {schedule} to cron expression: {schedule_cron_expression}")

    if is_create_workflow:
        if cssc_tasks_exists:
            raise AzCLIError(f"{ERROR_MESSAGE_WORKFLOW_TASKS_ALREADY_EXISTS}")

        create_oci_artifact_continuous_patch(registry, cssc_config_file, dryrun)
        logger.debug(f"Uploading of {cssc_config_file} for create completed successfully.")

        _create_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dryrun)
    else:
        if not cssc_tasks_exists:
            raise AzCLIError(f"{ERROR_MESSAGE_WORKFLOW_TASKS_DOES_NOT_EXIST}")

        if cssc_config_file:
            create_oci_artifact_continuous_patch(registry, cssc_config_file, dryrun)
            logger.debug(f"Uploading of {cssc_config_file} for update completed successfully.")

        _update_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dryrun, task_list)

    # on 'update' schedule is optional
    if schedule is None:
        trigger_task = next(task for task in task_list if task.name == CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME)
        trigger = trigger_task.trigger
        if trigger and trigger.timer_triggers:
            schedule_cron_expression = trigger.timer_triggers[0].schedule

    _eval_trigger_run(cmd, registry, resource_group, run_immediately)
    next_date = get_next_date(schedule_cron_expression)
    print(f"Continuous Patching workflow scheduled to run next at: {next_date} UTC")


def _create_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dry_run, silent_execution=False):
    parameters = {
        "AcrName": {"value": registry.name},
        "AcrLocation": {"value": registry.location},
        "taskSchedule": {"value": schedule_cron_expression}
    }

    for task in CONTINUOUSPATCH_TASK_DEFINITION:
        encoded_task = {"value": _create_encoded_task(CONTINUOUSPATCH_TASK_DEFINITION[task]["template_file"])}
        param_name = CONTINUOUSPATCH_TASK_DEFINITION[task]["parameter_name"]
        parameters[param_name] = encoded_task

    validate_and_deploy_template(
        cmd.cli_ctx,
        registry,
        resource_group,
        CONTINUOUSPATCH_DEPLOYMENT_NAME,
        CONTINUOUSPATCH_DEPLOYMENT_TEMPLATE,
        parameters,
        dry_run
    )

    if not silent_execution:
        print(f"Deployment of {CONTINUOUS_PATCHING_WORKFLOW_NAME} tasks completed successfully.")


def _update_cssc_workflow(cmd, registry, schedule_cron_expression, resource_group, dry_run, task_list):
    # compare the task definition to the existing tasks, if there is a difference, we need to update the tasks
    # if we need to update the tasks, we will update the cron expression from it
    # if not we just update the cron expression from the given parameter
    acr_task_client = cf_acr_tasks(cmd.cli_ctx)
    for task in task_list:
        deployed_task = task.step.encoded_task_content
        extension_task = _create_encoded_task(CONTINUOUSPATCH_TASK_DEFINITION[task.name]["template_file"])
        if deployed_task != extension_task:
            logger.debug(f"Task {task.name} is different from the extension task, updating the task")
            _update_task_yaml(acr_task_client, registry, resource_group, task, extension_task)

    if schedule_cron_expression:
        _update_task_schedule(acr_task_client, registry, resource_group, schedule_cron_expression, dry_run)


def _eval_trigger_run(cmd, registry, resource_group, run_immediately):
    if run_immediately:
        logger.warning(f'Triggering the {CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME} to run immediately')
        # Seen Managed Identity taking time, see if there can be an alternative (one alternative is to schedule the cron expression with delay)
        # NEED TO SKIP THE TIME.SLEEP IN UNIT TEST CASE OR FIND AN ALTERNATIVE SOLUITION TO MI COMPLETE
        time.sleep(30)
        _trigger_task_run(cmd, registry, resource_group, CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME)


def delete_continuous_patch_v1(cmd, registry, yes):
    logger.debug("Entering delete_continuous_patch_v1")
    cssc_tasks_exists, cssc_task_list = check_continuous_task_exists(cmd, registry)
    task_list_names = [task.name for task in cssc_task_list]
    cssc_config_exists = check_continuous_task_config_exists(cmd, registry)

    acr_run_client = cf_acr_runs(cmd.cli_ctx)
    resource_group_name = parse_resource_id(registry.id)[RESOURCE_GROUP]
    running_tasks = WorkflowTaskStatus.get_taskruns_with_filter(
        acr_run_client,
        registry_name=registry.name,
        resource_group_name=resource_group_name,
        status_filter=[TaskRunStatus.Running.value, TaskRunStatus.Queued.value, TaskRunStatus.Started.value],
        taskname_filter=[CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME, CONTINUOUSPATCH_TASK_SCANIMAGE_NAME, CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME])
    if running_tasks:
        from knack.prompting import prompt_y_n
        if yes or prompt_y_n("There are currently running tasks for this workflow. Do you want to cancel their execution?"):
            _cancel_task_runs(acr_run_client, registry.name, resource_group_name, running_tasks)

    if cssc_tasks_exists:
        cssc_tasks = ', '.join(task_list_names)
        logger.warning(f"All of these tasks will be deleted: {cssc_tasks}")
    else:
        logger.warning(f"{ERROR_MESSAGE_WORKFLOW_TASKS_DOES_NOT_EXIST}")
        if task_list_names:
            logger.warning("An attempt will be made to delete any dangling workflow tasks and the configuration file.")

    for taskname in task_list_names:
        _delete_task(cmd, registry, taskname)
        logger.warning(f"Task {taskname} deleted.")

    if cssc_config_exists:
        logger.warning(f"Deleting {CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}")
        delete_oci_artifact_continuous_patch(cmd, registry)


def list_continuous_patch_v1(cmd, registry):
    logger.debug("Entering list_continuous_patch_v1")
    cssc_tasks_exists, task_list = check_continuous_task_exists(cmd, registry)
    if not cssc_tasks_exists:
        logger.error(f"{ERROR_MESSAGE_WORKFLOW_TASKS_DOES_NOT_EXIST}")
        return

    filtered_cssc_tasks = _transform_task_list(task_list)
    return filtered_cssc_tasks


def acr_cssc_dry_run(cmd, registry, config_file_path, is_create=True, remove_internal_statements=True):
    logger.debug(f"Entering acr_cssc_dry_run with parameters: {registry} {config_file_path}")
    cssc_tasks_exists, _ = check_continuous_task_exists(cmd, registry)

    if is_create and cssc_tasks_exists:
        raise AzCLIError(f"{ERROR_MESSAGE_WORKFLOW_TASKS_ALREADY_EXISTS}")

    if config_file_path is None:
        if not cssc_tasks_exists:
            raise InvalidArgumentValueError("--config parameter is needed to perform dry-run check.")

        # attempt to get the config file from the registry, since the configuration should exist
        logger.debug("Retrieving the configuration file from the registry.")
        _, config_file_path = get_oci_artifact_continuous_patch(cmd, registry)
        if config_file_path is None:
            raise AzCLIError("Failed to retrieve the configuration file from the registry.")

    file_name = None
    tmp_folder = None
    acr_archive_utils_logger_level = acr_archive_utils_logger.getEffectiveLevel()
    try:
        file_name = os.path.basename(config_file_path)
        tmp_folder = os.path.join(os.getcwd(), tempfile.mkdtemp(prefix="cli_temp_cssc"))
        create_temporary_dry_run_file(config_file_path, tmp_folder)

        resource_group_name = parse_resource_id(registry.id)[RESOURCE_GROUP]
        acr_registries_task_client = cf_acr_registries_tasks(cmd.cli_ctx)
        acr_run_client = cf_acr_runs(cmd.cli_ctx)

        # This removes the internal logging from the acr module, reenables it after the setup is completed.
        # Because it is an external logger, the only way to control the output is by changing the level
        try:
            if remove_internal_statements:
                acr_archive_utils_logger.setLevel(logging.ERROR)

            source_location = prepare_source_location(
                cmd,
                tmp_folder,
                acr_registries_task_client,
                registry.name,
                resource_group_name)

        except CLIError as cli_error:
            raise AzCLIError(f"Failed to prepare source to trigger ACR task: {cli_error}")
        finally:
            if remove_internal_statements:
                acr_archive_utils_logger.setLevel(acr_archive_utils_logger_level)

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
            credentials=_get_custom_registry_credentials(cmd),
            agent_pool_name=None,
            log_template=None
        )
        queued = LongRunningOperation(cmd.cli_ctx, start_msg=WORKFLOW_VALIDATION_MESSAGE)(acr_registries_task_client.begin_schedule_run(
            resource_group_name=resource_group_name,
            registry_name=registry.name,
            run_request=request))
        run_id = queued.run_id
        logger.info("Performing dry-run check for filter policy using acr task run id: %s", run_id)
        return WorkflowTaskStatus.remove_internal_acr_statements(
            WorkflowTaskStatus.generate_logs(
                cmd,
                acr_run_client,
                run_id,
                registry.name,
                resource_group_name,
                await_task_run=True,
                await_task_message=WORKFLOW_VALIDATION_MESSAGE))
    finally:
        delete_temporary_dry_run_file(tmp_folder)


def cancel_continuous_patch_runs(cmd, resource_group_name, registry_name):
    logger.debug("Entering cancel_continuous_patch_v1")
    acr_task_run_client = cf_acr_runs(cmd.cli_ctx)
    running_tasks = WorkflowTaskStatus.get_taskruns_with_filter(
        acr_task_run_client,
        registry_name=registry_name,
        resource_group_name=resource_group_name,
        status_filter=[TaskRunStatus.Running.value, TaskRunStatus.Queued.value, TaskRunStatus.Started.value],
        taskname_filter=[CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME, CONTINUOUSPATCH_TASK_SCANIMAGE_NAME, CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME])

    _cancel_task_runs(acr_task_run_client, registry_name, resource_group_name, running_tasks)
    logger.warning("All active running workflow tasks have been cancelled.")


def _cancel_task_runs(acr_task_run_client, registry_name, resource_group_name, running_tasks):
    for task in running_tasks:
        try:
            logger.warning("Sending request to cancel task %s", task.name)
            logger.debug("Cancel Task run, name %s run id: %s", task.name, task.run_id)
            acr_task_run_client.begin_cancel(resource_group_name, registry_name, task.name)
        except Exception as exception:
            logger.error(f"Failed to cancel task {task.name} from registry {registry_name}: {exception}")


def track_scan_progress(cmd, resource_group_name, registry, status=None):
    logger.debug("Entering track_scan_progress")

    cssc_tasks_exists, _ = check_continuous_task_exists(cmd, registry)
    if not cssc_tasks_exists:
        logger.warning(f"{ERROR_MESSAGE_WORKFLOW_TASKS_DOES_NOT_EXIST}")
        return

    config, _ = get_oci_artifact_continuous_patch(cmd, registry)

    image_status = _retrieve_logs_for_image(cmd, registry, resource_group_name, config.schedule, status)
    print(f"Listing images that have been scanned and/or patched in the last {config.schedule} days")
    print(f"Total images: {len(image_status) if image_status else 0}")
    return image_status


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
    scan_taskruns = WorkflowTaskStatus.get_taskruns_with_filter(
        acr_task_run_client,
        registry.name,
        resource_group_name,
        taskname_filter=[CONTINUOUSPATCH_TASK_SCANIMAGE_NAME],
        date_filter=previous_date_filter)

    patch_taskruns = WorkflowTaskStatus.get_taskruns_with_filter(
        acr_task_run_client,
        registry.name,
        resource_group_name,
        taskname_filter=[CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME],
        date_filter=previous_date_filter)

    start_time = time.time()

    progress_indicator = IndeterminateProgressBar(cmd.cli_ctx, message="Retrieving logs for images")
    progress_indicator.begin()

    image_status = WorkflowTaskStatus.from_taskrun(cmd,
                                                   acr_task_run_client,
                                                   registry,
                                                   scan_taskruns,
                                                   patch_taskruns,
                                                   progress_indicator=progress_indicator,
                                                   workflow_status_filter=workflow_status)

    end_time = time.time()
    execution_time = end_time - start_time
    logger.debug(f"Execution time: {execution_time} seconds / tasks filtered: {len(scan_taskruns)} + {len(patch_taskruns)}")

    progress_indicator.end()

    return image_status


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


def _update_task_yaml(acr_task_client, registry, resource_group_name, task, encoded_task):
    logger.debug("Entering update_task_yaml for task %s", task.name)
    try:
        taskUpdateParameters = acr_task_client.models.TaskUpdateParameters(
            step=acr_task_client.models.EncodedTaskStepUpdateParameters(
                encoded_task_content=encoded_task))

        acr_task_client.begin_update(resource_group_name,
                                     registry.name,
                                     task.name,
                                     taskUpdateParameters)

        logger.debug(f"Task {task.name} updated successfully")
    except HttpResponseError as exception:
        logger.warning(f"Failed to update task {task.name} in registry {registry.name}: {exception}")


def _update_task_schedule(acr_task_client, registry, resource_group_name, cron_expression, dryrun):
    logger.debug(f"Using cron_expression: {cron_expression}")
    taskUpdateParameters = acr_task_client.models.TaskUpdateParameters(
        trigger=acr_task_client.models.TriggerUpdateParameters(
            timer_triggers=[
                acr_task_client.models.TimerTriggerUpdateParameters(
                    name='azcli_defined_schedule',
                    schedule=cron_expression)
            ]))

    if dryrun:
        logger.debug("Dry run, skipping the update of the task schedule")
        return
    try:
        acr_task_client.begin_update(resource_group_name,
                                     registry.name,
                                     CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME,
                                     taskUpdateParameters)
        print("Schedule has been successfully updated.")
    except HttpResponseError as exception:
        raise AzCLIError(f"Failed to update the task schedule: {exception}")


def _delete_task(cmd, registry, task_name):
    logger.debug("Entering delete_task")
    resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]

    try:
        acr_tasks_client = cf_acr_tasks(cmd.cli_ctx)
        _delete_task_role_assignment(cmd.cli_ctx, acr_tasks_client, registry, resource_group, task_name)

        logger.debug(f"Deleting task {task_name}")
        LongRunningOperation(cmd.cli_ctx)(
            acr_tasks_client.begin_delete(
                resource_group,
                registry.name,
                task_name))
        logger.debug(f"Task {task_name} deleted successfully")

    except AzCLIError as exception:
        logger.error(f"Failed to delete task {task_name} from registry {registry.name} : {exception}")


def _delete_task_role_assignment(cli_ctx, acrtask_client, registry, resource_group, task_name):
    role_client = cf_authorization(cli_ctx)

    try:
        task = acrtask_client.get(resource_group, registry.name, task_name)
    except ResourceNotFoundError:
        logger.debug(f"Task {task_name} does not exist in registry {registry.name}")
        logger.debug("Continuing with deletion")
        return None

    identity = task.identity

    if not identity or not identity.principal_id:
        logger.debug(f"Task {task_name} has no associated managed identity. Skipping role assignment deletion.")
        return None

    try:
        assigned_roles = role_client.role_assignments.list_for_scope(
            registry.id,
            filter=f"principalId eq '{identity.principal_id}'"
        )
    except ResourceNotFoundError:
        logger.debug(f"Role assignments for principal ID {identity.principal_id} do not exist in registry {registry.name}")
        return None

    for role in assigned_roles:
        try:
            logger.debug(f"Deleting role assignments of task {task_name} from the registry")
            role_client.role_assignments.delete(
                scope=registry.id,
                role_assignment_name=role.name
            )
        except ResourceNotFoundError:
            logger.debug(f"Role assignment {role.name} does not exist in registry {registry.name}")
        except AzCLIError as exception:
            logger.error(f"Failed to delete role assignment {role.name} from registry {registry.name} : {exception}")


def _transform_task_list(tasks):
    transformed = []
    for task in tasks:
        if task.name not in CONTINUOUSPATCH_ALL_TASK_NAMES:
            continue

        transformed_obj = {
            "creationDate": task.creation_date,
            "location": task.location,
            "name": task.name,
            "provisioningState": task.provisioning_state,
            "systemData": task.system_data,
            "schedule": None,
            "description": CONTINUOUSPATCH_TASK_DEFINITION[task.name][DESCRIPTION]
        }

        trigger = task.trigger
        if trigger and trigger.timer_triggers:
            # convert the cron expression to a 'days' format to keep consistent with the command's options
            transformed_obj["schedule"] = convert_cron_to_schedule(trigger.timer_triggers[0].schedule)

            # add a 'nextOccurrence' field to the task, only for the scheduling task
            transformed_obj["nextOccurrence"] = get_next_date(task.trigger.timer_triggers[0].schedule)
        transformed.append(transformed_obj)

    return transformed


def _get_custom_registry_credentials(cmd):
    acr_tasks_client = cf_acr_tasks(cmd.cli_ctx)
    return acr_tasks_client.models.Credentials(
        source_registry=None,
        custom_registries=None
    )


def get_next_date(cron_expression):
    from croniter import croniter
    now = datetime.now(timezone.utc)
    cron = croniter(cron_expression, now, expand_from_start_time=False)
    next_date = cron.get_next(datetime)
    return str(next_date)
