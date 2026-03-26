# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile
import unittest
from unittest import mock
from azure.cli.core.mock import DummyCli
from azext_acrcssc.helper._taskoperations import (create_update_continuous_patch_v1, delete_continuous_patch_v1, list_continuous_patch_v1, acr_cssc_dry_run, cancel_continuous_patch_runs, track_scan_progress)


class TestCreateContinuousPatchV1(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.cmd = self._setup_cmd()
        self.registry = mock.MagicMock()
        self.registry.name = "mockregistry"
        self.registry.id = f"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mockrg/providers/Microsoft.ContainerRegistry/registries/{self.registry.name}"
        self.config = mock.MagicMock()
    
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._eval_trigger_run")
    def test_create_continuous_patch_v1(self, mock_eval_trigger_run, mock_validate_and_deploy_template, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = False, []
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"

        # Call the function
        create_update_continuous_patch_v1(self.cmd, self.registry, temp_file_path, "1d", False, False)

        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("1d")
        mock_create_oci_artifact_continuous_patch.assert_called_once()
        mock_validate_and_deploy_template.assert_called_once()
        mock_eval_trigger_run.assert_called_once()
        
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._eval_trigger_run")
    def test_create_continuous_patch_v1_create_run_immediately_triggers_task(self, mock_eval_trigger_run, mock_validate_and_deploy_template, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = False, []
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"

        # Call the function
        create_update_continuous_patch_v1(self.cmd, self.registry, temp_file_path, "1d", False, True)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("1d")
        mock_create_oci_artifact_continuous_patch.assert_called_once()
        mock_validate_and_deploy_template.assert_called_once()
        mock_eval_trigger_run.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations._update_task_schedule")
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._eval_trigger_run")
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_acr_tasks')
    def test_update_continuous_patch_v1_schedule_update_should_not_update_config(self, mock_cf_acr_tasks, mock_eval_trigger_run, mock_validate_and_deploy_template, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists, mock_update_task_schedule):
        # Mock the necessary dependencies
        mock_acr_tasks_client = mock.MagicMock()
        mock_cf_acr_tasks.return_value = mock_acr_tasks_client
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = True, []
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"

        # Call the function
        create_update_continuous_patch_v1(self.cmd, self.registry, None, "2d", False, False, False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("2d")
        mock_create_oci_artifact_continuous_patch.assert_not_called()
        mock_validate_and_deploy_template.assert_not_called()
        mock_eval_trigger_run.assert_called_once()
        mock_update_task_schedule.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    def test_update_continuous_patch_v1__update_without_tasks_workflow_should_fail(self, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = False, []
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"

        # Call the function
        self.assertRaises(Exception,create_update_continuous_patch_v1, self.cmd, self.registry, None, "2d", False, False, False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("2d")
        mock_create_oci_artifact_continuous_patch.assert_not_called()
        
    @mock.patch("azext_acrcssc.helper._taskoperations._update_task_schedule")
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._eval_trigger_run")
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_acr_tasks')
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_authorization')
    def test_update_continuous_patch_v1_schedule_update_run_immediately_triggers_task(self, mock_cf_authorization, mock_cf_acr_tasks, mock_eval_trigger_run, mock_validate_and_deploy_template, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists, mock_update_task_schedule):
        # Mock the necessary dependencies
        mock_acr_tasks_client = mock.MagicMock()
        mock_cf_acr_tasks.return_value = mock_acr_tasks_client
        mock_role_client = mock.MagicMock()
        mock_cf_authorization.return_value = mock_role_client
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = True, []
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"

        # Call the function
        create_update_continuous_patch_v1(self.cmd, self.registry, None, "2d", False, True, False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("2d")
        mock_create_oci_artifact_continuous_patch.assert_not_called()
        mock_validate_and_deploy_template.assert_not_called()
        mock_eval_trigger_run.assert_called_once()
        mock_update_task_schedule.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations._cancel_task_runs")
    @mock.patch("azext_acrcssc.helper._taskoperations.WorkflowTaskStatus.get_taskruns_with_filter")
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_config_exists")
    @mock.patch('azext_acrcssc.helper._taskoperations.delete_oci_artifact_continuous_patch')
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.cf_acr_runs")
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_acr_tasks')
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_authorization')
    def test_delete_continuous_patch_v1(self, mock_cf_authorization, mock_cf_acr_tasks, mock_cf_acr_runs, mock_check_continuoustask_exists, mock_delete_oci_artifact_continuous_patch, mock_check_continuous_task_config_exists, mock_get_taskruns_with_filter, mock_cancel_task_runs):
        # Mock the necessary dependencies
        mock_check_continuoustask_exists.return_value = True, []
        mock_check_continuous_task_config_exists.return_value = True
        mock_resource_group = mock.MagicMock()
        mock_resource_group.name = 'resource_group_name'
        mock_acr_tasks_client = mock.MagicMock()
        mock_cf_acr_tasks.return_value = mock_acr_tasks_client
        mock_role_client = mock.MagicMock()
        mock_cf_authorization.return_value = mock_role_client
        mock_acr_run_client = mock.MagicMock()
        mock_cf_acr_runs.return_value = mock_acr_run_client
        mock_task = mock.MagicMock()
        mock_task.identity = mock.MagicMock()(principal_id='principal_id')
        mock_acr_tasks_client.get.return_value = mock_task
        mock_get_taskruns_with_filter.return_value = [mock.MagicMock()]

        delete_continuous_patch_v1(self.cmd, self.registry, yes=True)
        ## Assert here
        mock_delete_oci_artifact_continuous_patch.assert_called_once()
        mock_cancel_task_runs.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._eval_trigger_run")
    def test_create_continuous_patch_v1_dryrun(self, mock_eval_trigger_run, mock_validate_and_deploy_template, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuous_task_exists):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuous_task_exists.return_value = False, []
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"

        # Call the function
        create_update_continuous_patch_v1(self.cmd, self.registry, temp_file_path, "1d", True, False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("1d")
        mock_create_oci_artifact_continuous_patch.assert_called_once()
        mock_validate_and_deploy_template.assert_called_once()
        mock_eval_trigger_run.assert_called_once()


    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations._transform_task_list")
    def test_list_continuous_patch_v1(self, mock_transform_task_list, mock_check_continuous_task_exists):
        # Mock the necessary dependencies
        mock_check_continuous_task_exists.return_value = True, []
        mock_transform_task_list.return_value = []

        # Call the function
        result = list_continuous_patch_v1(self.cmd, self.registry)

        # Assert that the dependencies were called with the correct arguments
        mock_check_continuous_task_exists.assert_called_once()
        mock_transform_task_list.assert_called_once()
        self.assertEqual(result, [])

    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.WorkflowTaskStatus.generate_logs")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_temporary_dry_run_file")
    @mock.patch("azext_acrcssc.helper._taskoperations.delete_temporary_dry_run_file")
    @mock.patch("azext_acrcssc.helper._taskoperations.prepare_source_location")
    @mock.patch("azext_acrcssc.helper._taskoperations.cf_acr_registries_tasks")
    @mock.patch("azext_acrcssc.helper._taskoperations.cf_acr_runs")
    @mock.patch('azext_acrcssc._validators.cf_acr_tasks')
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_acr_tasks')
    @mock.patch("azext_acrcssc.helper._taskoperations.LongRunningOperation")
    def test_acr_cssc_dry_run(self, mock_LongRunningOperation, mock_cf_acr_tasks_taskoperations, mock_cf_acr_tasks_validator, mock_cf_acr_runs, mock_cf_acr_registries_tasks, mock_prepare_source_location, mock_delete_temporary_dry_run_file, mock_create_temporary_dry_run_file, mock_generate_logs, mock_check_continuous_task_exists):
        # Mock the necessary dependencies
        config_file_path = "test_config_file_path"
        mock_acr_registries_task_client = mock.MagicMock()
        mock_cf_acr_registries_tasks.return_value = mock_acr_registries_task_client
        mock_acr_run_client = mock.MagicMock()
        mock_cf_acr_runs.return_value = mock_acr_run_client
        mock_acr_task_client = mock.MagicMock()
        mock_cf_acr_tasks_validator.return_value = mock_acr_task_client
        mock_cf_acr_tasks_taskoperations.return_value = mock_acr_task_client
        mock_LongRunningOperation.return_value.return_value.run_id = "test_run_id"
        mock_generate_logs.return_value = "mock_logs"
        mock_check_continuous_task_exists.return_value = False, []

        # Call the function
        result = acr_cssc_dry_run(self.cmd, self.registry, config_file_path)

        # Assert that the dependencies were called with the correct arguments
        mock_create_temporary_dry_run_file.assert_called_once_with(config_file_path, mock.ANY)
        mock_prepare_source_location.assert_called_once()
        mock_LongRunningOperation.assert_called_once()
        mock_delete_temporary_dry_run_file.assert_called_once()
        mock_generate_logs.assert_called_once()
        self.assertIsNotNone(result)

    @mock.patch("azext_acrcssc.helper._taskoperations.WorkflowTaskStatus.get_taskruns_with_filter")
    @mock.patch("azext_acrcssc.helper._taskoperations.cf_acr_runs")
    def test_cancel_continuous_patch_runs(self, mock_cf_acr_runs, mock_get_taskruns_with_filter):
        # Mock the necessary dependencies
        resource_group_name = "test_rg"
        registry_name = "test_registry"
        mock_acr_task_run_client = mock.MagicMock()
        mock_cf_acr_runs.return_value = mock_acr_task_run_client
        mock_get_taskruns_with_filter.return_value = [mock.MagicMock()]

        # Call the function
        cancel_continuous_patch_runs(self.cmd, resource_group_name, registry_name)

        # Assert that the dependencies were called with the correct arguments
        mock_get_taskruns_with_filter.assert_called_once()
        mock_acr_task_run_client.begin_cancel.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.get_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations._retrieve_logs_for_image")
    def test_track_scan_progress(self, mock_retrieve_logs_for_image, mock_get_oci_artifact_continuous_patch, mock_check_continuous_task_exists):
        # Mock the necessary dependencies
        mock_check_continuous_task_exists.return_value = True, []
        resource_group_name = "test_rg"
        status = "test_status"
        mock_get_oci_artifact_continuous_patch.return_value = mock.MagicMock(schedule="1d"), mock.MagicMock()

        # Call the function
        result = track_scan_progress(self.cmd, resource_group_name, self.registry, status)

        # Assert that the dependencies were called with the correct arguments
        mock_check_continuous_task_exists.assert_called_once()
        mock_get_oci_artifact_continuous_patch.assert_called_once()
        mock_retrieve_logs_for_image.assert_called_once()
        self.assertIsNotNone(result)

    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        return cmd
