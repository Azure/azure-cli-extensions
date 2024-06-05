import tempfile
import unittest
from unittest import mock
from azure.cli.core.mock import DummyCli
from azext_acrcssc.helper._taskoperations import create_continuous_patch_v1, delete_continuous_patch_v1

class TestCreateContinuousPatchV1(unittest.TestCase):
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuoustask_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_convert_timespan_to_cron")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_continuouspatch_config_v1")
    @mock.patch("azext_acrcssc.helper._taskoperations.create_oci_artifact_continuous_patch")
    @mock.patch("azext_acrcssc.helper._taskoperations.parse_resource_id")
    @mock.patch("azext_acrcssc.helper._taskoperations.validate_and_deploy_template")
    @mock.patch("azext_acrcssc.helper._taskoperations._trigger_task_run")
    def test_create_continuous_patch_v1(self, mock_trigger_task_run, mock_validate_and_deploy_template, mock_parse_resource_id, mock_create_oci_artifact_continuous_patch, mock_validate_continuouspatch_config_v1, mock_validate_and_convert_timespan_to_cron, mock_check_continuoustask_exists):
        # Mock the necessary dependencies
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        mock_check_continuoustask_exists.return_value = False
        mock_validate_and_convert_timespan_to_cron.return_value = "0 0 * * *"
        mock_parse_resource_id.return_value = {"resource_group": "test_rg"}
        cmd = self._setup_cmd()
        registry = mock.MagicMock()
        registry.id = "/subscriptions/11111111-0000-0000-0000-0000000000006/resourceGroups/test-rg/providers/Microsoft.ContainerRegistry/registries/testregistry"

        # Call the function
        create_continuous_patch_v1(cmd, registry, temp_file_path, "1d", False)
        
        # Assert that the dependencies were called with the correct arguments
        mock_check_continuoustask_exists.assert_called_once()
        mock_validate_and_convert_timespan_to_cron.assert_called_once_with("1d")
        mock_validate_continuouspatch_config_v1.assert_called_once_with(temp_file_path)
        mock_create_oci_artifact_continuous_patch.assert_called_once()
        mock_validate_and_deploy_template.assert_called_once()
        mock_trigger_task_run.assert_called_once()

    @mock.patch("azext_acrcssc.helper._taskoperations.parse_resource_id")
    @mock.patch("azext_acrcssc.helper._taskoperations.check_continuoustask_exists")
    @mock.patch("azext_acrcssc.helper._taskoperations.delete_oci_artifact_continuous_patch")
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_acr_tasks')
    @mock.patch('azext_acrcssc.helper._taskoperations.cf_authorization')
    def test_delete_continuous_patch_v1(self, mock_delete_oci_artifact, mock_cf_authorization, mock_cf_acr_tasks, mock_check_continuoustask_exists, mock_parse_resource_id):
        # Mock the necessary dependencies
        cmd = self._setup_cmd()
        mock_registry = mock.MagicMock()
        mock_dryrun = False
        mock_check_continuoustask_exists.return_value = True
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
        
    
    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        return cmd