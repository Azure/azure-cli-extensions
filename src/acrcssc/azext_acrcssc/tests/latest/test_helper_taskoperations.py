# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile
import unittest
from unittest import mock
from azure.cli.core.mock import DummyCli
from azext_acrcssc.helper._taskoperations import (create_update_continuous_patch_v1, 
delete_continuous_patch_v1, generate_logs)

class TestCreateContinuousPatchV1(unittest.TestCase):
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.parse_resource_id")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._trigger_task_run")
    def test_create_continuous_patch_v1(self, mock_trigger_task_run, mock_validate_and_deploy_template, mock_parse_resource_id, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = False
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"
        mock_parse_resource_id.return_value = {"resource_group": "test_rg"}
        cmd = self._setup_cmd()
        registry = mock.MagicMock()
        registry.id = "/subscriptions/11111111-0000-0000-0000-0000000000006/resourceGroups/test-rg/providers/Microsoft.ContainerRegistry/registries/testregistry"

        # Call the function
        create_update_continuous_patch_v1(cmd, registry, temp_file_path, "1d", False, False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("1d")
        mock_create_oci_artifact_continuous_patch.assert_called_once()
        mock_validate_and_deploy_template.assert_called_once()
        mock_trigger_task_run.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations._update_task_schedule")
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.parse_resource_id")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._trigger_task_run")
    def test_update_continuous_patch_v1_cadence_update_should_not_update_config(self, mock_trigger_task_run, mock_validate_and_deploy_template, mock_parse_resource_id, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists, mock_update_task_schedule):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = True
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"
        mock_parse_resource_id.return_value = {"resource_group": "test_rg"}
        cmd = self._setup_cmd()
        registry = mock.MagicMock()
        registry.id = "/subscriptions/11111111-0000-0000-0000-0000000000006/resourceGroups/test-rg/providers/Microsoft.ContainerRegistry/registries/testregistry"

        # Call the function
        create_update_continuous_patch_v1(cmd, registry, None, "2d", False, False, False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("2d")
        mock_create_oci_artifact_continuous_patch.assert_not_called()
        mock_validate_and_deploy_template.assert_not_called()
        mock_trigger_task_run.assert_called_once()
        mock_update_task_schedule.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.parse_resource_id")
    def test_update_continuous_patch_v1__update_without_tasks_workflow_should_fail(self, mock_parse_resource_id, mock_create_oci_artifact_continuous_patch, mock_convert_timespan_to_cron, mock_check_continuoustask_exists):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = False
        mock_convert_timespan_to_cron.return_value = "0 0 * * *"
        mock_parse_resource_id.return_value = {"resource_group": "test_rg"}
        cmd = self._setup_cmd()
        registry = mock.MagicMock()
        registry.id = "/subscriptions/11111111-0000-0000-0000-0000000000006/resourceGroups/test-rg/providers/Microsoft.ContainerRegistry/registries/testregistry"

        # Call the function
        self.assertRaises(Exception,create_update_continuous_patch_v1,cmd, registry, None, "2d", False, False, False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_convert_timespan_to_cron.assert_called_once_with("2d")
        mock_create_oci_artifact_continuous_patch.not_called()

    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_config_exists")
    @mock.patch('azext_acrcssc.helper._taskoperations.delete_oci_artifact_continuous_patch')
    @mock.patch("azext_acrcssc.helper._taskoperations.parse_resource_id")
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuous_task_exists")
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_acr_tasks')
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_authorization')
    def test_delete_continuous_patch_v1(self, mock_cf_authorization, mock_cf_acr_tasks, mock_check_continuoustask_exists, mock_parse_resource_id, mock_delete_oci_artifact_continuous_patch, mock_check_continuous_task_config_exists):
        # Mock the necessary dependencies
        cmd = self._setup_cmd()
        mock_registry = mock.MagicMock()
        mock_dryrun = False
        mock_check_continuoustask_exists.return_value = True
        mock_check_continuous_task_config_exists.return_value = True
        mock_registry.id = 'registry_id'
        mock_resource_group = mock.MagicMock()
        mock_resource_group.name = 'resource_group_name'
        mock_registry.name = 'registry_name'
        mock_acr_tasks_client = mock.MagicMock()
        mock_cf_acr_tasks.return_value = mock_acr_tasks_client
        mock_role_client = mock.MagicMock()
        mock_cf_authorization.return_value = mock_role_client
        mock_task = mock.MagicMock()
        mock_task.identity = mock.MagicMock()(principal_id='principal_id')
        mock_acr_tasks_client.get.return_value = mock_task
        
        delete_continuous_patch_v1(cmd, mock_registry, mock_dryrun)
        ## Assert here
        mock_delete_oci_artifact_continuous_patch.assert_called_once()

    @mock.patch('azext_acrcssc.helper._taskoperations.get_blob_info')
    @mock.patch('azext_acrcssc.helper._taskoperations.get_sdk')
    def test_generate_logs(self, mock_get_sdk, mock_get_blob_info):
        cmd = mock.MagicMock()
        client = mock.MagicMock()
        run_id = "cfg5"
        registry_name = "myregistry"
        resource_group_name = "myresourcegroup"
        timeout = 60
        no_format = False
        raise_error_on_failure = False

        # Mock the response from client.get_log_sas_url()
        response = mock.MagicMock()
        response.log_link = "https://example.com/logs"
        client.get_log_sas_url.return_value = response

        run_response = mock.MagicMock()
        run_response.status = "Succeeded"
        client.get.return_value = run_response

        mock_get_blob_info.return_value = ["account_name", "endpoint_suffix", "container_name", "blob_name", "sas_token"]
        mock_blob_service = mock.MagicMock()
        mock_blob_service.get_blob_to_text.content.return_value = "sample text"
        mock_get_sdk.return_value = mock_blob_service
        # Call the function
        generate_logs(cmd, client, run_id, registry_name, resource_group_name, timeout)

        # Assert the function calls
        client.get_log_sas_url.assert_called_once_with(resource_group_name=resource_group_name, registry_name=registry_name, run_id=run_id)
        client.get.assert_called_once_with(resource_group_name, registry_name, run_id)
    
    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        return cmd