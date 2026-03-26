# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock
from unittest.mock import MagicMock
from azure.cli.core.mock import DummyCli
from azext_acrcssc.helper._constants import TaskRunStatus
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

    def test_task_status_to_workflow_status(self):
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
        error_logs = """2025/02/11 23:46:22 Launching container with name: patch-image
#1 resolve image config for docker-image://test.azurecr.io/repo:tag-9.9.99.20202020-amd64
Error: unsupported osType azurelinux specified
2025/02/11 23:46:23 Container failed during run: patch-image. No retries remaining.
failed to run step ID: patch-image: exit status 1

Run ID: dt2rw failed after 37s. Error: failed during run, err: exit status 1"""

        assert_error_log = """Error: failed during run, err: exit status 1
Error: unsupported osType azurelinux specified"""
        error_output = self.workflow_task_status._get_errors_from_tasklog(error_logs)
        self.assertEqual(error_output, assert_error_log)

    @mock.patch('azext_acrcssc.helper._workflow_status.WorkflowTaskStatus._get_missing_taskrun')
    @mock.patch('azext_acrcssc.helper._workflow_status.WorkflowTaskStatus._retrieve_all_tasklogs')
    def test_from_taskrun(self, mock_retrieve_all_tasklogs, mock_get_missing_taskrun):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        taskrun_client = MagicMock()
        registry = MagicMock()
        scan_taskruns = [self._generate_test_taskrun(True, repository="mock1"), self._generate_test_taskrun(True, repository="mock2"), self._generate_test_taskrun(True, repository="mock3")]
        patch_taskruns = []

        mock_retrieve_all_tasklogs.return_value = scan_taskruns
        mock_get_missing_taskrun.return_value = None

        # Test with 3 simple scan tasks and no patch tasks
        result = WorkflowTaskStatus.from_taskrun(cmd, taskrun_client, registry, scan_taskruns, patch_taskruns)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(scan_taskruns))
        self.assertTrue(all("patch_status" in workflow for workflow in result))
        self.assertTrue(all(workflow["patch_status"] == WorkflowTaskState.SKIPPED.value for workflow in result))
        self.assertTrue(all(workflow["scan_status"] == WorkflowTaskState.SUCCEEDED.value for workflow in result))
        self.assertTrue(all("patch_skipped_reason" in workflow for workflow in result))
        self.assertTrue(all("scan_error_reason" not in workflow for workflow in result))
        self.assertTrue(all("patch_error_reason" not in workflow for workflow in result))

        # Test with 1 scan task and 1 failed patch task
        patch_task = self._generate_test_taskrun(True, status=TaskRunStatus.Failed.value)
        scan_taskruns = [self._generate_test_taskrun(True, patch_taskid_in_scan=patch_task.run_id)]
        patch_taskruns = [patch_task]
        result = WorkflowTaskStatus.from_taskrun(cmd, taskrun_client, registry, scan_taskruns, patch_taskruns)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertTrue(all("patch_status" in workflow for workflow in result))
        self.assertTrue(all(workflow["patch_status"] == WorkflowTaskState.FAILED.value for workflow in result))
        self.assertTrue(all(workflow["scan_status"] == WorkflowTaskState.SUCCEEDED.value for workflow in result))
        self.assertTrue(all("scan_error_reason" not in workflow for workflow in result))
        self.assertTrue(all("patch_error_reason" in workflow for workflow in result))

        # Test where the patch task is missing, but mentioned in the scan task logs
        patch_task = self._generate_test_taskrun(True, status=TaskRunStatus.Succeeded.value)
        scan_taskruns = [self._generate_test_taskrun(True, patch_taskid_in_scan=patch_task.run_id)]
        patch_taskruns = []
        mock_get_missing_taskrun.return_value = patch_task
        result = WorkflowTaskStatus.from_taskrun(cmd, taskrun_client, registry, scan_taskruns, patch_taskruns)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(scan_taskruns))
        mock_get_missing_taskrun.assert_called_once()
        self.assertTrue("patch_status" in result[0])
        self.assertTrue("patch_task_ID" in result[0])
        self.assertTrue("last_patched_image" in result[0])
        self.assertTrue(not result[0]["last_patched_image"].startswith("---"))
        self.assertTrue(result[0]["patch_status"] == WorkflowTaskState.SUCCEEDED.value)

        # Test with mixed scan and patch tasks status
        patch_taskruns = [self._generate_test_taskrun(False, status=TaskRunStatus.Succeeded.value, tag="tag0"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Canceled.value, tag="tag1"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Queued.value, tag="tag2"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Running.value, tag="tag3"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Failed.value, tag="tag4")]

        scan_taskruns = [self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[0].run_id, tag="tag0"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[1].run_id, tag="tag1"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[2].run_id, tag="tag2"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[3].run_id, tag="tag3"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[4].run_id, tag="tag4"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Failed.value, tag="tag5"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Canceled.value, tag="tag6"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Queued.value, tag="tag7"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Running.value, tag="tag8"),]

        mock_get_missing_taskrun.return_value = patch_task
        result = WorkflowTaskStatus.from_taskrun(cmd, taskrun_client, registry, scan_taskruns, patch_taskruns)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(scan_taskruns))
        self.assertTrue(all("patch_status" in workflow for workflow in result))
        self.assertTrue(all("scan_status" in workflow for workflow in result))
        self.assertTrue(all("image" in workflow for workflow in result))
        self.assertTrue(all("scan_date" in workflow for workflow in result))
        self.assertTrue(all("scan_task_ID" in workflow for workflow in result))
        self.assertTrue(all("patch_date" in workflow for workflow in result))
        self.assertTrue(all("patch_task_ID" in workflow for workflow in result))
        self.assertTrue(all("last_patched_image" in workflow for workflow in result))
        self.assertTrue(all("workflow_type" in workflow for workflow in result))
        self.assertTrue(all(True if workflow["patch_status"] != TaskRunStatus.Failed.value or "patch_error_reason" in workflow else False for workflow in result))
        self.assertTrue(all(True if workflow["scan_status"] != TaskRunStatus.Failed.value or "scan_error_reason" in workflow else False for workflow in result))
        # test that a successful patch has a patched image reference
        self.assertTrue(all(True if workflow["patch_status"] != TaskRunStatus.Succeeded.value or not workflow["last_patched_image"].startswith("---") else False for workflow in result))


    @mock.patch('azext_acrcssc.helper._workflow_status.WorkflowTaskStatus._get_missing_taskrun')
    @mock.patch('azext_acrcssc.helper._workflow_status.WorkflowTaskStatus._retrieve_all_tasklogs')
    def test_from_taskrun_with_filter(self, mock_retrieve_all_tasklogs, mock_get_missing_taskrun):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        taskrun_client = MagicMock()
        registry = MagicMock()
        scan_taskruns = []
        patch_taskruns = []

        mock_retrieve_all_tasklogs.return_value = scan_taskruns
        mock_get_missing_taskrun.return_value = None
        
         # Test with mixed scan and patch tasks status
        patch_taskruns = [self._generate_test_taskrun(False, status=TaskRunStatus.Succeeded.value, tag="tag0"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Canceled.value, tag="tag1"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Queued.value, tag="tag2"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Running.value, tag="tag3"),
                          self._generate_test_taskrun(False, status=TaskRunStatus.Failed.value, tag="tag4")]

        scan_taskruns = [self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[0].run_id, tag="tag0"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[1].run_id, tag="tag1"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[2].run_id, tag="tag2"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[3].run_id, tag="tag3"),
                         self._generate_test_taskrun(True, patch_taskid_in_scan=patch_taskruns[4].run_id, tag="tag4"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Failed.value, tag="tag5"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Canceled.value, tag="tag6"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Queued.value, tag="tag7"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Running.value, tag="tag8"),
                         self._generate_test_taskrun(True, status=TaskRunStatus.Succeeded.value, tag="tag9")]
        
        result = WorkflowTaskStatus.from_taskrun(cmd,
                                                 taskrun_client,
                                                 registry,
                                                 scan_taskruns,
                                                 patch_taskruns,
                                                 workflow_status_filter=WorkflowTaskState.SUCCEEDED.value)
        self.assertTrue(len(result) > 0)
        self.assertTrue(all(workflow["scan_status"] == WorkflowTaskState.SUCCEEDED.value 
                            for workflow in result))
        self.assertTrue(all(workflow["patch_status"] == WorkflowTaskState.SUCCEEDED.value or 
                            workflow["patch_status"] == WorkflowTaskState.SKIPPED.value
                            for workflow in result))

        result = WorkflowTaskStatus.from_taskrun(cmd,
                                                 taskrun_client,
                                                 registry,
                                                 scan_taskruns,
                                                 patch_taskruns,
                                                 workflow_status_filter=WorkflowTaskState.FAILED.value)
        self.assertTrue(len(result) > 0)
        self.assertTrue(all(workflow["scan_status"] == WorkflowTaskState.FAILED.value or 
                            workflow["patch_status"] == WorkflowTaskState.FAILED.value 
                            for workflow in result))
        
        result = WorkflowTaskStatus.from_taskrun(cmd,
                                                 taskrun_client,
                                                 registry,
                                                 scan_taskruns,
                                                 patch_taskruns,
                                                 workflow_status_filter=WorkflowTaskState.RUNNING.value)
        self.assertTrue(len(result) > 0)
        self.assertTrue(all(workflow["scan_status"] == WorkflowTaskState.RUNNING.value or
                            workflow["patch_status"] == WorkflowTaskState.RUNNING.value or
                            workflow["scan_status"] == WorkflowTaskState.QUEUED.value or
                            workflow["patch_status"] == WorkflowTaskState.QUEUED.value
                            for workflow in result))
        
        result = WorkflowTaskStatus.from_taskrun(cmd,
                                                 taskrun_client,
                                                 registry,
                                                 scan_taskruns,
                                                 patch_taskruns,
                                                 workflow_status_filter=WorkflowTaskState.CANCELED.value)
        self.assertTrue(len(result) > 0)
        self.assertTrue(all(workflow["scan_status"] == WorkflowTaskState.CANCELED.value or
                            workflow["patch_status"] == WorkflowTaskState.CANCELED.value
                            for workflow in result))
        
        result = WorkflowTaskStatus.from_taskrun(cmd,
                                                 taskrun_client,
                                                 registry,
                                                 scan_taskruns,
                                                 patch_taskruns,
                                                 workflow_status_filter=WorkflowTaskState.SKIPPED.value)
        self.assertTrue(len(result) > 0)
        self.assertTrue(all(workflow["scan_status"] == WorkflowTaskState.SUCCEEDED.value and
                            workflow["patch_status"] == WorkflowTaskState.SKIPPED.value
                            for workflow in result))


    # generate a random scan or patch taskrun with the desired properties
    def _generate_test_taskrun(self, scan_task=True, status=TaskRunStatus.Succeeded.value, repository="mock-repo", tag="mock-tag", patch_taskid_in_scan=""):
        import random
        import string
        import datetime
        taskrun = MagicMock()
        taskrun.status = status
        taskrun.create_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        letters = ''.join(random.choices(string.ascii_lowercase, k=3))
        number = random.randint(0, 9)
        taskrun.run_id = f"{letters}{number}"
        task_log_result = ""

        if scan_task:
            task_log_result = f"Scanning image for vulnerability and patch {repository}:{tag} for tag {tag}"
            task_log_result += f"\nScanning repo: {repository}, Tag:{tag}, OriginalTag:{tag}"
            if taskrun.status == TaskRunStatus.Failed.value or taskrun.status == TaskRunStatus.Error.value:
                task_log_result += "\nerror: mock error on scan"
            elif taskrun.status == TaskRunStatus.Succeeded.value:
                task_log_result += "\nmock patch logs"
            else:
                task_log_result += "\ngeneric mock scan logs"
            if patch_taskid_in_scan != "":
                task_log_result += f"\nPATCHING task scheduled for image {repository}:{tag}, new patch tag will be {tag}-patched"
                task_log_result += f"\nWARNING: Queued a run with ID: {patch_taskid_in_scan}"

        else:
            task_log_result += f"Patching OS vulnerabilities for image {repository}:{tag}"
            if taskrun.status == TaskRunStatus.Failed.value or taskrun.status == TaskRunStatus.Error.value:
                task_log_result += "\nerror: mock error on patch"
            elif taskrun.status == TaskRunStatus.Succeeded.value:
                task_log_result += f"\nPATCHING task scheduled for image {repository}:{tag}, new patch tag will be {tag}-patched"
            else:
                task_log_result += "\nmock patch logs"

        taskrun.task_log_result = task_log_result

        return taskrun

    @mock.patch('azext_acrcssc.helper._workflow_status.WorkflowTaskStatus._download_logs')
    @mock.patch('azext_acrcssc.helper._workflow_status.get_sdk')
    @mock.patch('azure.cli.core.profiles.get_sdk')
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
        #mock_blob_client.from_blob_url = mock.MagicMock()
        mock_blob_client.from_blob_url.return_value = "mock_blob_client"

        mock_core_get_sdk.return_value = mock_blob_client
        mock_wf_get_sdk.return_value = mock_blob_client
        mock_download_logs.return_value = "mock logs"

        # Call the function
        result = WorkflowTaskStatus.generate_logs(cmd, client, run_id, registry_name, resource_group_name)

        # Assert the function calls
        mock_download_logs.assert_called()
        mock_blob_client.from_blob_url.assert_called()
        client.get_log_sas_url.assert_called()
        self.assertEqual(result, "mock logs")
