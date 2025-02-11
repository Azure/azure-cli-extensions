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

    def test_get_workflow_task_state(self):
        #test states that map to more than one
        task = MagicMock()
        task.status = "Succeeded"
        self.assertEqual(WorkflowTaskStatus.get_workflow_task_state(task), WorkflowTaskState.SUCCEEDED.value)
        task.status = "Running"
        self.assertEqual(WorkflowTaskStatus.get_workflow_task_state(task), WorkflowTaskState.RUNNING.value)
        task.status = "UnknownStatus"
        self.assertEqual(WorkflowTaskStatus.get_workflow_task_state(task), WorkflowTaskState.UNKNOWN.value)
        self.assertEqual(WorkflowTaskStatus.get_workflow_task_state(None), WorkflowTaskState.UNKNOWN.value)

    def test_status(self):
        # test a mixed state of patch and scan tasks
        self.workflow_task_status.scan_task = MagicMock()
        self.workflow_task_status.scan_task.status = "Succeeded"
        self.assertEqual(self.workflow_task_status.status(), WorkflowTaskState.SUCCEEDED.value)
        self.workflow_task_status.patch_task = MagicMock()
        self.workflow_task_status.patch_task.status = "Succeeded"
        self.assertEqual(self.workflow_task_status.status(), WorkflowTaskState.SUCCEEDED.value)

    @patch('src.acrcssc.azext_acrcssc.helper._workflow_status.re')
    def test_get_image_from_tasklog(self, mock_re):
        mock_re.search.return_value = MagicMock(group=lambda x: "Scanning image for vulnerability and patch mock-repo:mock-tag for tag mock-tag")
        self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog("logs"), "mock-repo:mock-tag")

        mock_re.search.return_value = MagicMock(group=lambda x: "Scanning repo: mock-repo, Tag:mock-tag, OriginalTag:mock-tag")
        self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog("logs"), "mock-repo:mock-tag")

        mock_re.search.return_value = MagicMock(group=lambda x: "Scan, Upload scan report and Schedule Patch for mock-repo:mock-tag")
        self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog("logs"), "mock-repo:mock-tag")

        # mock_re.search.return_value = MagicMock(group=lambda x: "Patching OS vulnerabilities for image mock-repo:mock-tag")
        # self.assertEqual(WorkflowTaskStatus._get_image_from_tasklog("logs"), "mock-repo:mock-tag")

    @patch('src.acrcssc.azext_acrcssc.helper._workflow_status.re')
    def test_get_patch_error_reason_from_tasklog(self, mock_re):
        #test with a more complicated log, and test different regex that we have
        error_logs = """
#9 apt update
#9 0.088 runc run failed: unable to start container process: error during container init: exec: "apt": executable file not found in $PATH
Error: process "apt update" did not complete successfully: exit code: 1
2025/02/09 23:47:20 Container failed during run: patch-image. No retries remaining.
failed to run step ID: patch-image: exit status 1
        """

        assertErrorLog = """Error: failed during run, err: exit status 1
        Error: process \"apt update\" did not complete successfully: exit code: 1
        error during container init: exec: \"apt\": executable file not found in $PATH
        """
        # mock_re.findall.return_value = ["error"]
        self.assertEqual(self.workflow_task_status._get_errors_from_tasklog(error_logs), "assertErrorLog")

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
