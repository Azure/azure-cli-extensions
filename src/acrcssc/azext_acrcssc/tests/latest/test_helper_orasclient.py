import tempfile
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from azext_acrcssc.helper._orasclient import create_oci_artifact_continuous_patch, delete_oci_artifact_continuous_patch
from azure.cli.core.mock import DummyCli
from azure.cli.core.azclierror import AzCLIError

class TestCreateOciArtifactContinuousPatch(unittest.TestCase):
    @patch('azext_acrcssc.helper._orasclient._oras_client')
    @patch('azext_acrcssc.helper._orasclient.tempfile.NamedTemporaryFile')
    @patch('azext_acrcssc.helper._orasclient.shutil.copyfileobj')
    def test_create_oci_artifact_continuous_patch(self, mock_copyfileobj, mock_NamedTemporaryFile, mock_oras_client):
        # Mock the necessary dependencies
        cmd = self._setup_cmd()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        registry = MagicMock()
        registry.login_server = "test@azurecr.io"
        cssc_config_file = temp_file_path
        dryrun = False
        oras_client = MagicMock()
        mock_oras_client.return_value = oras_client
        temp_artifact = MagicMock()
        mock_NamedTemporaryFile.return_value = temp_artifact

        # Call the function
        with patch('os.path.exists', return_value=True), \
             patch('os.remove', return_value=True):
             create_oci_artifact_continuous_patch(cmd, registry, cssc_config_file, dryrun)

        # Assert that the necessary functions were called with the correct arguments
        mock_oras_client.assert_called_once_with(cmd, registry)
        oras_client.push.assert_called_once_with(target='continuouspatchpolicy:latest', files=[temp_artifact.name])

    @mock.patch('azext_acrcssc.helper._orasclient._get_acr_token')
    @mock.patch('azext_acrcssc.helper._orasclient.logger')
    @mock.patch('azext_acrcssc.helper._orasclient.parse_resource_id')
    @mock.patch('azext_acrcssc.helper._orasclient.acr_repository_delete')
    def test_delete_oci_artifact_continuous_patch(self, mock_acr_repository_delete, mock_parse_resource_id, mock_logger, mock_get_acr_token):
        # Mock the necessary dependencies
        cmd = self._setup_cmd()
        registry = MagicMock()
        dryrun = False
        mock_parse_resource_id.return_value = {
            "resource_group": "test_rg",
            "subscription": "test_subscription"
        }
        mock_get_acr_token.return_value = "test_token"

        # Call the function
        delete_oci_artifact_continuous_patch(cmd, registry, dryrun)

        # Assert the function calls
        mock_parse_resource_id.assert_called_once_with(registry.id)
        mock_get_acr_token.assert_called_once_with(registry.name, "test_rg", "test_subscription")
        mock_acr_repository_delete.assert_called_once_with(
            cmd=cmd,
            registry_name=registry.name,
            image="continuouspatchpolicy:latest",
            username="00000000-0000-0000-0000-000000000000",
            password="test_token",
            yes=True
        )
        mock_logger.warning.assert_not_called()

    @mock.patch('azext_acrcssc.helper._orasclient._get_acr_token')
    @mock.patch('azext_acrcssc.helper._orasclient.logger')
    @mock.patch('azext_acrcssc.helper._orasclient.parse_resource_id')
    @mock.patch('azext_acrcssc.helper._orasclient.acr_repository_delete')
    def test_delete_oci_artifact_continuous_patch_dryrun(self, mock_acr_repository_delete, mock_parse_resource_id, mock_logger, mock_get_acr_token):
        # Mock the necessary dependencies
        cmd = self._setup_cmd()
        registry = MagicMock()
        dryrun = True
        mock_parse_resource_id.return_value = {
            "resource_group": "test_rg",
            "subscription": "test_subscription"
        }
        mock_get_acr_token.return_value = "test_token"

        # Run the function
        delete_oci_artifact_continuous_patch(cmd, registry, dryrun)

        # Assert the function calls
        mock_parse_resource_id.assert_called_once_with(registry.id)
        mock_acr_repository_delete.assert_not_called()
    
    @mock.patch('azext_acrcssc.helper._orasclient._get_acr_token')
    @mock.patch('azext_acrcssc.helper._orasclient.logger')
    @mock.patch('azext_acrcssc.helper._orasclient.parse_resource_id')
    @mock.patch('azext_acrcssc.helper._orasclient.acr_repository_delete')
    def test_delete_oci_artifact_continuous_patch_exception(self, mock_acr_repository_delete, mock_parse_resource_id, mock_logger, mock_get_acr_token):
         # Mock the necessary dependencies
        cmd = self._setup_cmd()
        registry = MagicMock()
        dryrun = False
        mock_parse_resource_id.return_value = {
            "resource_group": "test_rg",
            "subscription": "test_subscription"
        }

        mock_get_acr_token.return_value = "test_token"
        mock_acr_repository_delete.side_effect = Exception("Test exception")

        # Run the function and assert the exception
        with(self.assertRaises(Exception)):
            delete_oci_artifact_continuous_patch(cmd, registry, dryrun)

        # Assert the function calls
        mock_parse_resource_id.assert_called_once_with(registry.id)
        mock_get_acr_token.assert_called_once_with(registry.name, "test_rg", "test_subscription")
        mock_logger.warning.assert_not_called()

    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        return cmd