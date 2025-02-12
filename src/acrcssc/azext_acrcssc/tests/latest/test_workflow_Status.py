# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from azure.cli.core.mock import DummyCli
from azext_acrcssc.helper._workflow_status import WorkflowTaskStatus, WorkflowTaskState


class TestWorkflowTaskStatus(unittest.TestCase):

    def setUp(self):
        self.image = "repository:tag"
        self.workflow_task_status = WorkflowTaskStatus(self.image)

    def test_init(self):
        self.assertEqual(self.workflow_task_status.repository, "repository")
        self.assertEqual(self.workflow_task_status.tag, "tag")
        self.assertIsNone(self.workflow_task_status.scan_task)
        self.assertEqual(self.workflow_task_status.scan_logs, "")
        self.assertIsNone(self.workflow_task_status.patch_task)
        self.assertEqual(self.workflow_task_status.patch_logs, "")

    def test_image(self):
        self.assertEqual(self.workflow_task_status.image(), "repository:tag")

    def test__task_status_to_workflow_status(self):
        from azext_acrcssc.helper._constants import TaskRunStatus
        task = mock.MagicMock()
        task.status = TaskRunStatus.Succeeded.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.SUCCEEDED.value)
        task.status = TaskRunStatus.Running.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.RUNNING.value)
        task.status = TaskRunStatus.Started.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.RUNNING.value)
        task.status = TaskRunStatus.Queued.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.QUEUED.value)
        task.status = TaskRunStatus.Canceled.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.CANCELED.value)
        task.status = TaskRunStatus.Failed.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.FAILED.value)
        task.status = TaskRunStatus.Error.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.FAILED.value)
        task.status = TaskRunStatus.Timeout.value
        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(task), WorkflowTaskState.FAILED.value)

        self.assertEqual(WorkflowTaskStatus._task_status_to_workflow_status(None), WorkflowTaskState.UNKNOWN.value)

    def test_workflow_status(self):
        from azext_acrcssc.helper._constants import TaskRunStatus
        workflow = WorkflowTaskStatus("mock_repo:mock_tag")
        workflow.scan_task = mock.MagicMock()
        workflow.patch_task = mock.MagicMock()

        workflow.scan_task.status = TaskRunStatus.Succeeded.value
        workflow.patch_task.status = TaskRunStatus.Succeeded.value
        self.assertEqual(workflow.status(), WorkflowTaskState.SUCCEEDED.value)

        workflow.scan_task.status = TaskRunStatus.Succeeded.value
        workflow.patch_task.status = TaskRunStatus.Failed.value
        self.assertEqual(workflow.status(), WorkflowTaskState.FAILED.value)

        workflow.scan_task.status = TaskRunStatus.Succeeded.value
        workflow.patch_task.status = TaskRunStatus.Running.value
        self.assertEqual(workflow.status(), WorkflowTaskState.RUNNING.value)

        workflow.scan_task.status = TaskRunStatus.Canceled.value
        workflow.patch_task = None
        self.assertEqual(workflow.status(), WorkflowTaskState.CANCELED.value)

        workflow.scan_task.status = TaskRunStatus.Succeeded.value
        workflow.patch_task = None
        self.assertEqual(workflow.status(), WorkflowTaskState.SUCCEEDED.value)

        workflow.scan_task = None
        workflow.patch_task = None
        self.assertEqual(workflow.status(), WorkflowTaskState.UNKNOWN.value)

    def test_get_image_from_tasklog(self):
        logs = "Scanning image for vulnerability and patch mock-repo:mock-tag for tag mock-tag"
        self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog(logs), "mock-repo:mock-tag")

        logs = "Scanning repo: mock-repo, Tag:mock-tag, OriginalTag:mock-tag"
        self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog(logs), "mock-repo:mock-tag")

        # logs = "Scan, Upload scan report and Schedule Patch for mock-repo:mock-tag"
        # self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog(logs), "mock-repo:mock-tag")

        logs = "Patching OS vulnerabilities for image mock-repo:mock-tag"
        self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog(logs), "mock-repo:mock-tag")

    def test_get_patch_error_reason_from_tasklog(self):
        #test with a more complicated log, and test different regex that we have
        error_logs = """2025/02/11 23:46:22 Launching container with name: patch-image
#1 resolve image config for docker-image://graycsscsec.azurecr.io/import:openmpi-4.1.5-1-azl3.0.20240727-amd64
Error: unsupported osType azurelinux specified
2025/02/11 23:46:23 Container failed during run: patch-image. No retries remaining.
failed to run step ID: patch-image: exit status 1

Run ID: dt2rw failed after 37s. Error: failed during run, err: exit status 1"""

        assert_error_log = """Error: failed during run, err: exit status 1
Error: unsupported osType azurelinux specified"""
        error_output = self.workflow_task_status._get_errors_from_tasklog(error_logs)
        self.assertEqual(error_output, assert_error_log)

    @patch('src.acrcssc.azext_acrcssc.helper._workflow_status.WorkflowTaskStatus.generate_logs')
    @patch('src.acrcssc.azext_acrcssc.helper._workflow_status.parse_resource_id')
    def test_retrieve_all_tasklogs(self, mock_parse_resource_id, mock_generate_logs):
        #this might be the 'get_logs' in the other test file, check if it can be enriched
        mock_parse_resource_id.return_value = {"resource_group": "resource_group"}
        taskrun_client = MagicMock()
        registry = MagicMock(id="id")
        taskruns = [MagicMock(run_id="run_id")]
        WorkflowTaskStatus._retrieve_all_tasklogs("cmd", taskrun_client, registry, taskruns)
        self.assertTrue(mock_generate_logs.called)

    @patch('src.acrcssc.azext_acrcssc.helper._workflow_status.WorkflowTaskStatus._retrieve_all_tasklogs')
    def test_from_taskrun(self, mock_retrieve_all_tasklogs):
        # this one, has to be tested to make sure it loops through the tasks, and retrieves what it needs
        taskrun_client = MagicMock()
        registry = MagicMock()
        scan_taskruns = [MagicMock()]
        patch_taskruns = [MagicMock()]
        result = WorkflowTaskStatus.from_taskrun("cmd", taskrun_client, registry, scan_taskruns, patch_taskruns)
        self.assertIsInstance(result, list)

    @mock.patch('azure.cli.core.profiles.get_sdk')
    @mock.patch('azext_acrcssc.helper._workflow_status.get_sdk')
    @mock.patch('azext_acrcssc.helper._workflow_status.WorkflowTaskStatus._download_logs')
    def test_generate_logs(self, mock_core_get_sdk, mock_wf_get_sdk, mock_download_logs):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        client = mock.MagicMock()
        run_id = "cgb5"
        registry_name = "myregistry"
        resource_group_name = "myresourcegroup"

        # Mock the response from client.get_log_sas_url()
        response = mock.MagicMock()
        response.log_link = "https://example.com/logs"
        client.get_log_sas_url.return_value = response

        run_response = mock.MagicMock()
        run_response.status = "Succeeded"
        client.get.return_value = run_response

        # Create a mock for the blob client
        mock_blob_client = mock.MagicMock()
        mock_blob_client.from_blob_url.return_value = "mock_blob_client"
        mock_blob_client.download_blob.return_value = mock.MagicMock(content_as_text=lambda: "mocked content")

        mock_core_get_sdk.return_value = mock_blob_client
        mock_download_logs.return_value = "mock logs"

        # Call the function
        WorkflowTaskStatus.generate_logs(cmd, client, run_id, registry_name, resource_group_name)

        # Assert the function calls
        # client.get_log_sas_url.assert_called_once_with(resource_group_name=resource_group_name, registry_name=registry_name, run_id=run_id)
        # client.get.assert_called_once_with(resource_group_name, registry_name, run_id)
