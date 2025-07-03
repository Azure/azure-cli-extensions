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
    WORKFLOW_STATUS_PATCH_NOT_AVAILABLE
)
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.progress import IndeterminateProgressBar
from azure.core.exceptions import HttpResponseError
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.azclierror import AzCLIError, ResourceNotFoundError
from azure.core.polling import PollingMethod
from azure.mgmt.core.tools import parse_resource_id
from knack.log import get_logger
from enum import Enum


logger = get_logger(__name__)


class WorkflowTaskState(Enum):
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    QUEUED = "Queued"
    SKIPPED = "Skipped"
    CANCELED = "Canceled"
    UNKNOWN = "Unknown"


class WorkflowTaskStatus:
    def __init__(self, image):
        repo = image.split(':')
        # string to represent the repository
        self.repository = repo[0]

        # string to represent the tag
        self.tag = repo[1]

        # latest taskrun object for the scan task. If none, means no scan task has been run
        self.scan_task = None

        # not sure if we should be proactive to get the logs for the scan task, but it will also be that we don't
        # know that the scan task has been run until we check for logs
        self.scan_logs = ""

        # latest taskrun object for the patch task, if none, means no patch task has been run
        self.patch_task = None

        # ditto for patch logs, we don't know if the patch task has been run until we check for logs
        self.patch_logs = ""

    def image(self):
        return f"{self.repository}:{self.tag}"

    # task run status from src\ACR.Build.Contracts\src\Status.cs
    @staticmethod
    def _task_status_to_workflow_status(task):
        if task is None:
            return WorkflowTaskState.UNKNOWN.value

        status = task.status.lower()
        status_mapping = {
            TaskRunStatus.Succeeded.value.lower(): WorkflowTaskState.SUCCEEDED.value,
            TaskRunStatus.Running.value.lower(): WorkflowTaskState.RUNNING.value,
            TaskRunStatus.Started.value.lower(): WorkflowTaskState.RUNNING.value,
            TaskRunStatus.Queued.value.lower(): WorkflowTaskState.QUEUED.value,
            TaskRunStatus.Canceled.value.lower(): WorkflowTaskState.CANCELED.value,
            TaskRunStatus.Failed.value.lower(): WorkflowTaskState.FAILED.value,
            TaskRunStatus.Error.value.lower(): WorkflowTaskState.FAILED.value,
            TaskRunStatus.Timeout.value.lower(): WorkflowTaskState.FAILED.value,
        }

        return status_mapping.get(status, WorkflowTaskState.UNKNOWN.value)

    @staticmethod
    def _workflow_status_to_task_status(status):
        status_mapping = {
            WorkflowTaskState.SUCCEEDED.value: [TaskRunStatus.Succeeded.value],
            WorkflowTaskState.SKIPPED.value: [TaskRunStatus.Succeeded.value],
            WorkflowTaskState.RUNNING.value: [TaskRunStatus.Running.value,
                                              TaskRunStatus.Started.value],
            WorkflowTaskState.QUEUED.value: [TaskRunStatus.Queued.value],
            WorkflowTaskState.CANCELED.value: [TaskRunStatus.Canceled.value],
            WorkflowTaskState.FAILED.value: [TaskRunStatus.Failed.value,
                                             TaskRunStatus.Error.value,
                                             TaskRunStatus.Timeout.value],
        }

        return status_mapping.get(status, None)

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

    # this extracts the image from the copacetic task logs, using this when we only have a repository
    # name and a wildcard tag
    @staticmethod
    def _get_image_from_tasklog(logs):
        match = re.search(r'Scanning repo: (\S+), Tag:\S+, OriginalTag:(\S+)', logs)
        if match:
            repository = match.group(1)
            original_tag = match.group(2)
            return f"{repository}:{original_tag}"

        match = re.search(r'Scanning image for vulnerability(?: and patch)? (\S+) for tag (\S+)', logs)
        if match:
            patched_image = match.group(1)
            original_tag = match.group(2)
            repository = patched_image.split(':')[0]
            return f"{repository}:{original_tag}"

        match = re.search(r'Patching OS vulnerabilities for image (\S+):(\S+)', logs)
        if match:
            repository = match.group(1)
            original_tag = match.group(2)
            return f"{repository}:{original_tag}"
        return None

    def get_patch_task_from_scan_tasklog(self):
        if self.scan_task is None:
            return None

        match = re.search(r'WARNING: Queued a run with ID: (\S+)', self.scan_logs)
        if match:
            return match.group(1)
        return None

    def _get_scanning_repo_from_scan_task(self):
        if self.scan_task is None:
            return None

        if self.patch_status() == WorkflowTaskState.SKIPPED.value or \
           self.patch_status() == WorkflowTaskState.SUCCEEDED.value:
            match = re.search(
                r'PATCHING task scheduled for image (\S+):(\S+), new patch tag will be (\S+)',
                self.scan_logs)
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

    def _get_patch_skip_reason_from_tasklog(self):
        if self.scan_task is None:
            return None
        match = re.search(r'PATCHING will be skipped as (.+)\n', self.scan_logs)
        if match:
            return match.group(1)
        return None

    def _get_patch_error_reason_from_tasklog(self):
        if self.patch_task is None:
            return None
        return self._get_errors_from_tasklog(self.patch_logs)

    def _get_scan_error_reason_from_tasklog(self):
        if self.scan_task is None:
            return None
        return self._get_errors_from_tasklog(self.scan_logs)

    def _get_errors_from_tasklog(self, tasklog):
        match = re.findall(r'(?i)\b(error\b.*)', tasklog)
        # TODO: should we filter out any error?
        if match:
            # retrieve only unique errors, sort them to make the output deterministic
            return str.join("\n", sorted(set(match)))
        return None

    def _get_patched_image_name_from_tasklog(self):
        if self.scan_task is None:
            return None

        repository, patched_tag, _ = self._get_scanning_repo_from_scan_task()
        if repository and patched_tag:
            return f"{repository}:{patched_tag}"

        if self.patch_task:
            match = re.search(r'Patched image pushed to (\S+)', self.patch_logs)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _latest_task(this_task, this_log, that_task, that_log):
        if this_task is None:
            return that_task, that_log
        if that_task is None:
            return this_task, this_log
        return (this_task, this_log) if this_task.create_time > that_task.create_time else (that_task, that_log)

    @staticmethod
    def _retrieve_all_tasklogs(cmd, taskrun_client, registry, taskruns, progress_indicator=None):
        import concurrent.futures
        resource_group = parse_resource_id(registry.id)[RESOURCE_GROUP]

        def process_taskrun(taskrun):
            try:
                tasklog = WorkflowTaskStatus.generate_logs(cmd,
                                                           taskrun_client,
                                                           taskrun.run_id,
                                                           registry.name,
                                                           resource_group,
                                                           await_task_run=False)
                if tasklog == "":
                    logger.debug("Taskrun: %s has no logs, silent failure", taskrun.run_id)
                taskrun.task_log_result = tasklog
            except ResourceNotFoundError as e:
                logger.debug("Failed to get logs for taskrun: %s with exception: %s", taskrun.run_id, e)
            except HttpResponseError as e:
                logger.debug("An unexpected exception has occurred for taskrun: %s with exception: %s",
                             taskrun.run_id, e)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for taskrun in taskruns:
                if progress_indicator:
                    progress_indicator.update_progress()

                future = executor.submit(process_taskrun, taskrun)
                futures.append(future)

            # Wait for all threads to complete
            while not all(future.done() for future in futures):
                if progress_indicator:
                    progress_indicator.update_progress()
                time.sleep(0.5)

    @staticmethod
    def from_taskrun(cmd,
                     taskrun_client,
                     registry,
                     scan_taskruns,
                     patch_taskruns,
                     progress_indicator=None,
                     workflow_status_filter=None):
        WorkflowTaskStatus._retrieve_all_tasklogs(cmd, taskrun_client, registry, scan_taskruns, progress_indicator)
        all_status = {}

        # we only retrieve logs for scan taskruns in the begining, we will need to retrieved the logs for
        # failed patch taskruns to populate patch_error_reason. It will be faster to retrieve in a batch
        failed_patch_tasklog_retrieval = []

        for scan in scan_taskruns:
            if progress_indicator:
                progress_indicator.update_progress()
                if hasattr(progress_indicator, 'hook') and \
                    hasattr(progress_indicator.hook, 'active_progress') and \
                        hasattr(progress_indicator.hook.active_progress, 'spinner'):
                    progress_indicator.hook.active_progress.spinner.step(label=progress_indicator.message)
            if not hasattr(scan, 'task_log_result'):
                logger.debug("Scan Taskrun: %s has no logs, silent failure", scan.run_id)
                continue

            image = WorkflowTaskStatus._get_image_from_tasklog(scan.task_log_result)

            if not image:
                continue

            # need to check if we have the latest scan task
            if image in all_status:
                all_status[image].scan_task, all_status[image].scan_logs = WorkflowTaskStatus._latest_task(
                    all_status[image].scan_task,
                    all_status[image].scan_logs,
                    scan,
                    scan.task_log_result)
            else:
                all_status[image] = WorkflowTaskStatus(image)
                all_status[image].scan_task = scan
                all_status[image].scan_logs = scan.task_log_result

            patch_task_id = all_status[image].get_patch_task_from_scan_tasklog()
            # missing the patch task id means that the scan either failed, or succeeded and patching is not needed.
            # this is important, because patching status depends on both the patching task status (if it exists)
            # and the scan task status
            if patch_task_id:
                # it is possible for the patch task to be mentioned in the logs, but the API has not returned the
                # taskrun for it yet, attempt to retrieve it from client
                patch_task = next((task for task in patch_taskruns if task.run_id == patch_task_id), None)
                if patch_task is None:
                    patch_task = WorkflowTaskStatus._get_missing_taskrun(taskrun_client, registry, patch_task_id)

                all_status[image].patch_task = patch_task
                if patch_task and WorkflowTaskStatus._task_status_to_workflow_status(
                    patch_task
                ) == WorkflowTaskState.FAILED.value:
                    failed_patch_tasklog_retrieval.append(all_status[image])

        if failed_patch_tasklog_retrieval:
            taskrunList = [task.patch_task for task in failed_patch_tasklog_retrieval if task.patch_task]
            WorkflowTaskStatus._retrieve_all_tasklogs(cmd, taskrun_client, registry, taskrunList, progress_indicator)
            for workflow_status in failed_patch_tasklog_retrieval:
                workflow_status.patch_logs = workflow_status.patch_task.task_log_result

        return [status.get_status()
                for status in WorkflowTaskStatus._filter_taskruns(all_status, workflow_status_filter).values()]

    @staticmethod
    def _filter_taskruns(workflows, workflow_status_filter=None):
        if not workflows:
            return {}

        if not workflow_status_filter:
            return workflows

        # SKIPPED is a special case, because it means that the patch task does not exist,
        # but the scan task succeeded. Another special case that is not explicit here is SUCCEEDED,
        # which will include both scan and patch tasks that succeeded, or the scan task succeeded
        # and the patch task is skipped
        if workflow_status_filter == WorkflowTaskState.SKIPPED.value:
            filtered_workflow = {key: workflow
                                 for key, workflow in workflows.items()
                                 if workflow.scan_status() == WorkflowTaskState.SUCCEEDED.value and
                                 workflow.patch_status() == WorkflowTaskState.SKIPPED.value}
            return filtered_workflow

        filtered_workflow = {
            key: workflow
            for key, workflow in workflows.items()
            if workflow.status() == workflow_status_filter}
        return filtered_workflow

    def get_status(self):
        scan_status = self.scan_status()
        scan_date = WORKFLOW_STATUS_NOT_AVAILABLE if self.scan_task is None else self.scan_task.create_time
        scan_task_id = WORKFLOW_STATUS_NOT_AVAILABLE if self.scan_task is None else self.scan_task.run_id
        patch_status = self.patch_status()
        patch_date = WORKFLOW_STATUS_NOT_AVAILABLE if self.patch_task is None else self.patch_task.create_time
        patch_task_id = WORKFLOW_STATUS_NOT_AVAILABLE if self.patch_task is None else self.patch_task.run_id
        patched_image = self._get_patched_image_name_from_tasklog()
        workflow_type = CSSCTaskTypes.ContinuousPatchV1.value
        # Initialize reasons only if needed
        patch_skipped_reason = self._get_patch_skip_reason_from_tasklog() \
            if self.patch_status() == WorkflowTaskState.SKIPPED.value else ""

        scan_error_reason = self._get_scan_error_reason_from_tasklog() \
            if self.scan_status() == WorkflowTaskState.FAILED.value else ""

        patch_error_reason = self._get_patch_error_reason_from_tasklog() \
            if self.patch_status() == WorkflowTaskState.FAILED.value else ""

        if patched_image == self.image():
            patched_image = WORKFLOW_STATUS_PATCH_NOT_AVAILABLE

        result = {
            "image": f"{self.repository}:{self.tag}",
            "scan_status": scan_status,
            "scan_date": scan_date,
            "scan_task_ID": scan_task_id,
            "patch_status": patch_status,
            "patch_date": patch_date,
            "patch_task_ID": patch_task_id,
            "last_patched_image": patched_image,
            "workflow_type": workflow_type
        }

        if patch_skipped_reason != "":
            result["patch_skipped_reason"] = patch_skipped_reason

        if scan_error_reason != "":
            result["scan_error_reason"] = scan_error_reason

        if patch_error_reason != "":
            result["patch_error_reason"] = patch_error_reason

        return result

    def __str__(self) -> str:
        status = self.get_status()
        result = f"image: {status.repository}:{status.tag}\n" \
                 f"\tscan status: {status.scan_status}\n" \
                 f"\tscan date: {status.scan_date}\n" \
                 f"\tscan task ID: {status.scan_task_id}\n"

        if hasattr(status, "scan_error_reason"):
            result += f"\tscan error reason: {status.scan_error_reason}\n"

        result += f"\tpatch status: {status.patch_status}\n"

        if hasattr(status, "patch_error_reason"):
            result += f"\tpatch error reason: {status.patch_error_reason}\n"

        if hasattr(status, "patch_skipped_reason"):
            result += f"\tpatch skipped reason: {status.patch_skipped_reason}\n"

        result += f"\tpatch date: {status.patch_date}\n" \
                  f"\tpatch task ID: {status.patch_task_id}\n" \
                  f"\tlast patched image: {status.patched_image}\n" \
                  f"\tworkflow type: {status.workflow_type}"

        return result

    @staticmethod
    def generate_logs(cmd,
                      client,
                      run_id,
                      registry_name,
                      resource_group_name,
                      await_task_run=True,
                      await_task_message=None):

        log_file_sas = None
        error_msg = "Could not get logs for ID: {}".format(run_id)
        try:
            response = client.get_log_sas_url(
                resource_group_name=resource_group_name,
                registry_name=registry_name,
                run_id=run_id)
            log_file_sas = response.log_link
        except (AttributeError, HttpResponseError) as e:
            logger.debug("%s Exception: %s", error_msg, e)
            raise AzCLIError(error_msg)
        except ResourceNotFoundError as e:
            logger.debug("log file not found for run_id: %s, registry: %s, "
                         "resource_group: %s -- exception: %s",
                         run_id, registry_name, resource_group_name, e)
            return ""

        if await_task_run:
            try:
                polling_method = WorkflowLogPollingMethod(client,
                                                          resource_group_name,
                                                          registry_name,
                                                          run_id)
                result = LongRunningOperation(
                    cmd.cli_ctx,
                    progress_bar=IndeterminateProgressBar(cmd.cli_ctx, message=await_task_message),
                    poller_done_interval_ms=1500  # every poller call will do a call to the API
                )(polling_method)
                logger.debug("Task result: %s", result)
            except TimeoutError:
                logger.debug("Timeout waiting for task run to complete, workflow task run ID: %s", run_id)
                logger.debug("An attempt to retrieve the logs will be done, if there are any")

        blobClient = get_sdk(cmd.cli_ctx, ResourceType.DATA_STORAGE_BLOB, '_blob_client#BlobClient')
        return WorkflowTaskStatus._download_logs(blobClient.from_blob_url(log_file_sas))

    @staticmethod
    def evaluate_task_run_nonterminal_state(run_status):
        return run_status != TaskRunStatus.Succeeded.value and run_status != TaskRunStatus.Failed.value

    @staticmethod
    def get_run_status_local(client, resource_group_name, registry_name, run_id):
        try:
            response = client.get(resource_group_name, registry_name, run_id)
            return response.status
        except (AttributeError, HttpResponseError):
            return None

    @staticmethod
    def _download_logs(blob_service):
        try:
            blob = blob_service.download_blob()
            blob_text = blob.readall().decode('utf-8')
            return blob_text
        except AzCLIError as e:
            logger.debug("Failed to download logs from blob: %s", e)
            return ""

    @staticmethod
    def remove_internal_acr_statements(blob_content):
        logger.debug("Removing internal ACR statements from logs, blob content size: %s", len(blob_content))
        lines = blob_content.splitlines()
        starting_identifier = "DRY RUN mode enabled"
        terminating_identifier = "Total matches found"
        print_line = False
        output = ""

        for line in lines:
            if line.strip().startswith(starting_identifier):
                print_line = True
            elif line.strip().startswith(terminating_identifier):
                output += "\n" + line
                print_line = False

            if print_line:
                output += "\n" + line

        return output

    @staticmethod
    def _get_missing_taskrun(taskrun_client, registry, run_id):
        try:
            resourceid = parse_resource_id(registry.id)
            resource_group = resourceid[RESOURCE_GROUP]
            runs = WorkflowTaskStatus.get_taskruns_with_filter(taskrun_client,
                                                               registry_name=registry.name,
                                                               resource_group_name=resource_group,
                                                               runId_filter=run_id)
            return runs[0]
        except ResourceNotFoundError as e:
            logger.debug("Failed to find taskrun %s from registry %s: %s", run_id, registry.name, e)
            return None

    @staticmethod
    def get_taskruns_with_filter(acr_task_run_client,
                                 registry_name,
                                 resource_group_name,
                                 taskname_filter=None,
                                 runId_filter=None,
                                 date_filter=None,
                                 status_filter=None,
                                 top=1000):
        # filters based on OData, found in ACR.BuildRP.DataModels - RunFilter.cs
        filter_str = ""
        if taskname_filter:
            taskname_filter_str = "', '".join(taskname_filter)
            filter_str += f"TaskName in ('{taskname_filter_str}')"

        if runId_filter:
            if filter_str != "":
                filter_str += " and "
            filter_str += f"runId eq '{runId_filter}'"

        if date_filter:
            if filter_str != "":
                filter_str += " and "
            filter_str += f"createTime ge {date_filter}"

        if status_filter:
            if filter_str != "":
                filter_str += " and "
            status_filter_str = "', '".join(status_filter)
            filter_str += f"Status in ('{status_filter_str}')"

        taskruns = acr_task_run_client.list(resource_group_name, registry_name, filter=filter_str, top=top)
        return list(taskruns)


# this is a polling method that will poll the taskrun status until it is done
# or the timeout is reached. It does not download the logs nor run the task
class WorkflowLogPollingMethod(PollingMethod):
    def __init__(self, client, resource_group_name, registry_name, run_id):
        self.client = client
        self.resource_group_name = resource_group_name
        self.registry_name = registry_name
        self.run_id = run_id
        self.run_status = TaskRunStatus.Running.value
        self.start_time = time.time()
        self.timeout = 10 * 60  # 10 minutes

    def initialize(self, client, initial_response, deserialization_callback):
        pass

    def _timeout(self):
        return (time.time() - self.start_time) >= self.timeout

    def run(self):
        pass

    def status(self):
        return self.run_status

    def finished(self):
        if self._timeout():
            raise TimeoutError("Timeout waiting for task run to complete")

        self.run_status = WorkflowTaskStatus.get_run_status_local(self.client,
                                                                  self.resource_group_name,
                                                                  self.registry_name,
                                                                  self.run_id)

        return not WorkflowTaskStatus.evaluate_task_run_nonterminal_state(self.status())

    def done(self):
        return self.finished()

    def result(self):
        return self.status()

    def resource(self):
        return self.status()
