# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from azext_acrcssc.helper._ociartifactoperations import create_oci_artifact_continuous_patch, delete_oci_artifact_continuous_patch, delete_trivy_db_copy, _oras_client
from azure.cli.core.mock import DummyCli


class TestCreateOciArtifactContinuousPatch(unittest.TestCase):
    @patch('azext_acrcssc.helper._ociartifactoperations._oras_client')
    @patch('azext_acrcssc.helper._ociartifactoperations.NamedTemporaryFile')
    @patch('shutil.copyfileobj')
    @patch('builtins.open')
    def test_create_oci_artifact_continuous_patch(self, mock_open, mock_copyfileobj, mock_NamedTemporaryFile, mock_oras_client):
        # Mock the necessary dependencies
        temp_artifact = MagicMock()
        temp_artifact.name = "mock_temp_file_path"
        mock_NamedTemporaryFile.return_value.__enter__.return_value = temp_artifact
        
        # Configure the open() mock to return a mock file object
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        mock_copyfileobj.return_value = None

        registry = MagicMock()
        registry.login_server = "test@azurecr.io"
        cssc_config_file = temp_artifact.name  # Use the mocked file path
        dryrun = False
        oras_client = MagicMock()
        oras_client.push = MagicMock()
        mock_oras_client.return_value = oras_client

        # Call the function
        with patch('os.path.exists', return_value=True), patch('os.remove', return_value=True):
            create_oci_artifact_continuous_patch(registry, cssc_config_file, dryrun)

        # Assert that the necessary functions were called with the correct arguments
        mock_oras_client.assert_called_once_with(registry)
        oras_client.push.assert_called_once_with(target='csscpolicies/patchpolicy:v1', files=[temp_artifact.name])

    @mock.patch('azext_acrcssc.helper._ociartifactoperations._get_acr_token')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.logger')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.parse_resource_id')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.acr_repository_delete')
    def test_delete_oci_artifact_continuous_patch(self, mock_acr_repository_delete, mock_parse_resource_id, mock_logger, mock_get_acr_token):
        # Mock the necessary dependencies
        cmd = self._setup_cmd()
        registry = MagicMock()
        mock_parse_resource_id.return_value = {
            "resource_group": "test_rg",
            "subscription": "test_subscription"
        }
        mock_get_acr_token.return_value = "test_token"

        # Call the function
        delete_oci_artifact_continuous_patch(cmd, registry)

        # Assert the function calls
        mock_parse_resource_id.assert_called_once_with(registry.id)
        mock_get_acr_token.assert_called_once_with(registry.name, "test_subscription")
        mock_acr_repository_delete.assert_called_once_with(
            cmd=cmd,
            registry_name=registry.name,
            repository="csscpolicies/patchpolicy",
            username="00000000-0000-0000-0000-000000000000",
            password="test_token",
            yes=True
        )
        mock_logger.warning.assert_not_called()
        mock_acr_repository_delete.assert_called_once()

    
    @mock.patch('azext_acrcssc.helper._ociartifactoperations._get_acr_token')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.logger')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.parse_resource_id')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.acr_repository_delete')
    def test_delete_oci_artifact_continuous_patch_exception(self, mock_acr_repository_delete, mock_parse_resource_id, mock_logger, mock_get_acr_token):
        # Mock the necessary dependencies
        cmd = self._setup_cmd()
        registry = MagicMock()
        mock_parse_resource_id.return_value = {
            "resource_group": "test_rg",
            "subscription": "test_subscription"
        }

        mock_get_acr_token.return_value = "test_token"
        mock_acr_repository_delete.side_effect = Exception("Test exception")

        # Run the function and assert the exception
        with (self.assertRaises(Exception)):
            delete_oci_artifact_continuous_patch(cmd, registry)

        # Assert the function calls
        mock_parse_resource_id.assert_called_once_with(registry.id)
        mock_get_acr_token.assert_called_once_with(registry.name, "test_subscription")
        mock_logger.warning.assert_not_called()

    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        return cmd

    @mock.patch('azext_acrcssc.helper._ociartifactoperations._get_acr_token')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.parse_resource_id')
    @mock.patch('azext_acrcssc.helper._ociartifactoperations.acr_repository_delete')
    def test_delete_trivy_db_copy_missing_repository_does_not_fail(self, mock_acr_repository_delete, mock_parse_resource_id, mock_get_acr_token):
        cmd = self._setup_cmd()
        registry = MagicMock()
        mock_parse_resource_id.return_value = {"resource_group": "test_rg", "subscription": "test_subscription"}
        mock_get_acr_token.return_value = "test_token"
        mock_acr_repository_delete.side_effect = Exception("repository not found")

        delete_trivy_db_copy(cmd, registry)

        self.assertEqual(mock_acr_repository_delete.call_args.kwargs["repository"], "csscpolicies/trivy-db")

    @mock.patch('azext_acrcssc.helper._ociartifactoperations._get_acr_token')
    def test_oras_client_ignores_docker_config_credentials(self, mock_get_acr_token):
        import base64
        import json
        import os
        import tempfile
        import oras.container
        mock_get_acr_token.return_value = "acr_refresh_token"
        registry = MagicMock()
        registry.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ContainerRegistry/registries/myreg"
        registry.name = "myreg"
        registry.login_server = "myreg.azurecr.io"
        with tempfile.TemporaryDirectory() as home_dir:
            # what `az acr login` writes: an `auth` entry with an empty password plus an identity token
            os.makedirs(os.path.join(home_dir, ".docker"))
            empty_password_auth = base64.b64encode(b"00000000-0000-0000-0000-000000000000:").decode()
            with open(os.path.join(home_dir, ".docker", "config.json"), "w") as f:
                json.dump({"auths": {"myreg.azurecr.io": {"auth": empty_password_auth, "identitytoken": "x"}}}, f)
            with mock.patch.dict(os.environ, {"HOME": home_dir}):
                client = _oras_client(registry)
                client.auth.load_configs(oras.container.Container("myreg.azurecr.io/csscpolicies/patchpolicy:v1"))
        expected = base64.b64encode(b"00000000-0000-0000-0000-000000000000:acr_refresh_token").decode()
        self.assertEqual(client.auth._basic_auth, expected)
