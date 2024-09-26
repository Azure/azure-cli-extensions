# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# want it to be something where we can store the status of a image processed by the workflow
# contain both the image, scanning status and patching status

import time
import re
from ._constants import (
    RESOURCE_GROUP,
    CSSCTaskTypes,
    TaskRunStatus,
    WORKFLOW_STATUS_NOT_AVAILABLE,
    WORKFLOW_STATUS_PATCH_NOT_AVAILABLE)
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.azclierror import AzCLIError
from azure.mgmt.core.tools import parse_resource_id
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger
from enum import Enum
from msrestazure.azure_exceptions import CloudError

logger = get_logger(__name__)


class WorkflowTaskState(Enum):
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    QUEUED = "Queued"
    SKIPPED = "Skipped"
    UNKNOWN = "Unknown"


class WorkflowTaskStatus:
    def __init__(self, image):
        repo = image.split(':')
        # string to represent the repository
        self.repository = repo[0]

        # string to represent the tag, can be '*', which means all tags. in that situation the class should be able to resolve to the individual tags on the registry
        self.tag = repo[1]

        # latest taskrun object for the scan task, if none, means no scan task has been run
        self.scan_task = None

        # not sure if we should be proactive to get the logs for the scan task, but it will also be that we don't know that the scan task has been run until we check for logs
        self.scan_logs = ""

        # latest taskrun object for the patch task, if none, means no patch task has been run
        self.patch_task = None

        # ditto for patch logs, we don't know if the patch task has been run until we check for logs
        self.patch_logs = ""

    def is_wildcard(self):
        return self.tag == '*'

    def image(self):
        if self.is_wildcard():
            return self.repository
        return f"{self.repository}:{self.tag}"

    # task run status from src\ACR.Build.Contracts\src\Status.cs
    @staticmethod
    def _task_status_to_workflow_status(task):
        if task is None:
            return WorkflowTaskState.UNKNOWN.value

        status = task.status.lower()
        if status == TaskRunStatus.Succeeded.value.lower():
            return WorkflowTaskState.SUCCEEDED.value

        if status == TaskRunStatus.Running.value.lower() or status == TaskRunStatus.Started.value.lower():
            return WorkflowTaskState.RUNNING.value

        if status == TaskRunStatus.Queued.value.lower():
            return WorkflowTaskState.QUEUED.value

        if status == TaskRunStatus.Failed.value.lower() or status == TaskRunStatus.Canceled.value.lower() or status == TaskRunStatus.Error.value.lower() or status == TaskRunStatus.Timeout.value.lower():
            return WorkflowTaskState.FAILED.value

        return WorkflowTaskState.UNKNOWN.value

    @staticmethod
    def _workflow_status_to_task_status(status):
        if status == WorkflowTaskState.SUCCEEDED.value or status == WorkflowTaskState.SKIPPED.value:
            return [TaskRunStatus.Succeeded.value]
        if status == WorkflowTaskState.RUNNING.value:
            return [TaskRunStatus.Running.value, TaskRunStatus.Started.value]
        if status == WorkflowTaskState.QUEUED.value:
            return [TaskRunStatus.Queued.value]
        if status == WorkflowTaskState.FAILED.value:
            return [TaskRunStatus.Failed.value, TaskRunStatus.Canceled.value, TaskRunStatus.Error.value, TaskRunStatus.Timeout.value]
        return None

    def scan_status(self):
        return WorkflowTaskStatus._task_status_to_workflow_status(self.scan_task)

    def patch_status(self):
        # this one is a bit more complicated, because the patch status depends on the scan status
        # or more correctly, the patch status is the scan status if there is no patch task
        # and the whole workflow status is both the scan and patch status
        if self.patch_task is None and self.scan_status() == WorkflowTaskState.SUCCEEDED.value:
            return WorkflowTaskState.SKIPPED.value
        return WorkflowTaskStatus._task_status_to_workflow_status(self.patch_task)

    def status(self):
        if self.patch_task is None:
            return self.scan_status()

        return self.patch_status()

    # this extracts the image from the copacetic task logs, using this when we only have a repository name and a wildcard tag
    @staticmethod
    def _get_image_from_tasklog(logs):
        match = re.search(r'Scanning repo: (\S+), Tag:\S+, OriginalTag:(\S+)', logs)
        if match:
            repository = match.group(1)
            original_tag = match.group(2)
            return f"{repository}:{original_tag}"

        match = re.search(r'Scanning image for vulnerability and patch (\S+) for tag (\S+)', logs)
        if match:
            patched_image = match.group(1)
            original_tag = match.group(2)
            repository = patched_image.split(':')[0]
            return f"{repository}:{original_tag}"

        match = re.search(r'Scan, Upload scan report and Schedule Patch for (\S+)', logs)
        if match:
            return match.group(1)
        return None

    def _get_patch_task_from_scan_tasklog(self):
        if self.scan_task is None:
            return None

        match = re.search(r'WARNING: Queued a run with ID: (\S+)', self.scan_logs)
        if match:
            return match.group(1)
        return None

    def _get_scanning_repo_from_scan_task(self):
        if self.scan_task is None:
            return None

        if self.patch_status() == WorkflowTaskState.SKIPPED.value or self.patch_status() == WorkflowTaskState.SUCCEEDED.value:
            match = re.search(r'PATCHING task scheduled for image (\S+):(\S+), new patch tag will be (\S+)', self.scan_logs)
            if match:
                repository = match.group(1)
                original_tag = match.group(2)
                patched_tag = match.group(3)
                return repository, patched_tag, original_tag

        match = re.search(r'Scanning repo: (\S+), Tag:(\S+), OriginalTag:(\S+)', self.scan_logs)
        if match:
            repository = match.group(1)
            patched_tag = match.group(2)
            original_tag = match.group(3)
            return repository, patched_tag, original_tag
        return None

    def _get_skip_patch_reason_from_tasklog(self):
        if self.scan_task is None:
            return None
        match = re.search(r'PATCHING will be skipped as (.+)\n', self.scan_logs)
        if match:
            return match.group(1)

    def _get_patched_image_name_from_tasklog(self):
        if self.scan_task is None:
            return None

        repository, patched_tag, _ = self._get_scanning_repo_from_scan_task()
        if repository is not None and patched_tag is not None:
            return f"{repository}:{patched_tag}"

        if self.patch_task is None:
            return None

        match = re.search(r'Patched image pushed to (\S+)', self.patch_logs)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _latest_task(this_task, this_log, that_task, that_log):
        if this_task is None:
            return (that_task, that_log)
        if that_task is None:
            return (this_task, this_log)
        return (this_task, this_log) if this_task.create_time > that_task.create_time else (that_task, that_log)

    @staticmethod
    def _retrieve_all_tasklogs(cmd, taskrun_client, registry, taskruns, progress_indicator=None):
        import concurrent.futures
        resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]

        def process_taskrun(taskrun):
            try:
                tasklog = WorkflowTaskStatus.generate_logs(cmd, taskrun_client, taskrun.run_id, registry.name, resource_group, await_task_run=False)
                if tasklog == "":
                    logger.debug(f"Taskrun: {taskrun.run_id} has no logs, silent failure")
                taskrun.task_log_result = tasklog
            except Exception as e:
                logger.debug(f"Failed to get logs for taskrun: {taskrun.run_id} with exception: {e}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for taskrun in taskruns:
                if progress_indicator:
                    progress_indicator.update_progress()

                future = executor.submit(process_taskrun, taskrun)
                futures.append(future)

            # Wait for all threads to complete
            concurrent.futures.wait(futures)

    @staticmethod
    def from_taskrun(cmd, taskrun_client, registry, scan_taskruns, patch_taskruns, progress_indicator=None):
        WorkflowTaskStatus._retrieve_all_tasklogs(cmd, taskrun_client, registry, scan_taskruns, progress_indicator)
        all_status = {}

        for scan in scan_taskruns:
            if progress_indicator:
                progress_indicator.update_progress()
            if not hasattr(scan, 'task_log_result'):
                logger.debug(f"Scan Taskrun: {scan.run_id} has no logs, silent failure")
                continue

            image = WorkflowTaskStatus._get_image_from_tasklog(scan.task_log_result)

            if not image:
                continue

            # need to check if we have the latest scan task, is it better to get latest first or to get all and then get the latest?
            task = scan
            logs = scan.task_log_result

            if image in all_status:
                task, logs = WorkflowTaskStatus._latest_task(all_status[image].scan_task, all_status[image].scan_logs, scan, scan.task_log_result)
            else:
                all_status[image] = WorkflowTaskStatus(image)
            all_status[image].scan_task = task
            all_status[image].scan_logs = logs
            patch_task_id = all_status[image]._get_patch_task_from_scan_tasklog()
            # missing the patch task id means that the scan either failed, or succeeded and patching is not needed
            # this is important, because patching status depends on both the patching task status (if it exists) and the scan task status
            if patch_task_id is not None:
                patch_task = next(task for task in patch_taskruns if task.run_id == patch_task_id)
                all_status[image].patch_task = patch_task

        # don't return a list of WorkflowTaskStatus object, 
        return [status.get_status() for status in all_status.values()]

    def get_status(self):
        scan_status = self.scan_status()
        scan_date = WORKFLOW_STATUS_NOT_AVAILABLE if self.scan_task is None else self.scan_task.create_time
        scan_task_id = WORKFLOW_STATUS_NOT_AVAILABLE if self.scan_task is None else self.scan_task.run_id
        patch_status = self.patch_status()
        patch_date = WORKFLOW_STATUS_NOT_AVAILABLE if self.patch_task is None else self.patch_task.create_time
        patch_task_id = WORKFLOW_STATUS_NOT_AVAILABLE if self.patch_task is None else self.patch_task.run_id
        patched_image = self._get_patched_image_name_from_tasklog()
        workflow_type = CSSCTaskTypes.ContinuousPatchV1.value
        skipped_patch_reason = ""

        # this situation means that we don't have a patched image
        if self.patch_status() == WorkflowTaskState.SKIPPED.value:
            skipped_patch_reason = self._get_skip_patch_reason_from_tasklog()

        if patched_image == self.image():
            patched_image = WORKFLOW_STATUS_PATCH_NOT_AVAILABLE

        result = {
            "image": f"{self.repository}:{self.tag}",
            "scan_status": scan_status,
            "scan_date": scan_date,
            "scan_task_ID": scan_task_id,
            "patch_status": patch_status
        }

        if skipped_patch_reason != "":
            result["skipped_patch_reason"] = skipped_patch_reason

        result["patch_date"] = patch_date
        result["patch_task_ID"] = patch_task_id
        result["last_patched_image"] = patched_image
        result["workflow_type"] = workflow_type

        return result

    def __str__(self) -> str:
        status = self.get_status()
        result = f"image: {status.repository}:{status.tag}\n" \
                 f"\tscan status: {status.scan_status}\n" \
                 f"\tscan date: {status.scan_date}\n" \
                 f"\tscan task ID: {status.scan_task_id}\n" \
                 f"\tpatch status: {status.patch_status}\n"

        if hasattr(status, "skipped_patch_reason"):
            result += f"\tskipped patch reason: {status.skipped_patch_reason}\n"

        result += f"\tpatch date: {status.patch_date}\n" \
                  f"\tpatch task ID: {status.patch_task_id}\n" \
                  f"\tlast patched image: {status.patched_image}\n" \
                  f"\tworkflow type: {status.workflow_type}"

        return result

    @staticmethod
    def generate_logs(cmd, client, run_id, registry_name, resource_group_name, await_task_run=True):

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
        except ResourceNotFoundError as e:
            logger.debug(f"log file not found for run_id: {run_id}, registry: {registry_name}, resource_group: {resource_group_name} -- exception: {e}")

        run_status = TaskRunStatus.Running.value
        while await_task_run and WorkflowTaskStatus._evaluate_task_run_nonterminal_state(run_status):
            run_status = WorkflowTaskStatus._get_run_status_local(client, resource_group_name, registry_name, run_id)
            if WorkflowTaskStatus._evaluate_task_run_nonterminal_state(run_status):
                logger.debug("Waiting for the task run to complete. Current status: %s", run_status)
                time.sleep(2)

        blobClient = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE_BLOB, '_blob_client#BlobClient')
        return WorkflowTaskStatus._download_logs(blobClient.from_blob_url(log_file_sas))

    @staticmethod
    def _evaluate_task_run_nonterminal_state(run_status):
        return run_status != TaskRunStatus.Succeeded.value and run_status != TaskRunStatus.Failed.value

    @staticmethod
    def _get_run_status_local(client, resource_group_name, registry_name, run_id):
        try:
            response = client.get(resource_group_name, registry_name, run_id)
            return response.status
        except (AttributeError, CloudError):
            return None

    @staticmethod
    def _download_logs(blob_service):
        blob = blob_service.download_blob()
        blob_text = blob.readall().decode('utf-8')
        # return WorkflowTaskStatus._remove_internal_acr_statements(blob_text)
        # not sure what is the point of this, might only make sense when we are doing dryrun and breaks other cases
        return blob_text

    @staticmethod
    def remove_internal_acr_statements(blob_content):
        lines = blob_content.split("\n")
        starting_identifier = "DRY RUN mode enabled"
        terminating_identifier = "Total matches found"
        print_line = False
        output = ""

        for line in lines:
            if line.startswith(starting_identifier):
                print_line = True
            elif line.startswith(terminating_identifier):
                output += "\n" + line
                print_line = False

            if print_line:
                output += "\n" + line

        return output
