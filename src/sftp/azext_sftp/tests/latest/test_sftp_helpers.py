# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Additional unit tests for SFTP helper functions and edge cases.
Tests follow Azure best practices for comprehensive coverage and error handling.
"""

import unittest
from unittest import mock
import tempfile
import os
import shutil
from azext_sftp import custom
from azure.cli.core import azclierror


class TestSftpHelperFunctions(unittest.TestCase):
    """
    Test class for SFTP helper functions and edge cases.
    Following Azure best practices for unit testing with proper mocking and cleanup.
    """

    def setUp(self):
        """Set up test fixtures with secure temporary directory."""
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_helper_test_")
        self.mock_cert_file = os.path.join(self.temp_dir, "test_cert.pub")
        self.mock_private_key = os.path.join(self.temp_dir, "test_key")
        self.mock_public_key = os.path.join(self.temp_dir, "test_key.pub")
        
        # Create mock files
        for file_path in [self.mock_cert_file, self.mock_private_key, self.mock_public_key]:
            with open(file_path, 'w') as f:
                f.write("mock content")

    def tearDown(self):
        """Clean up test fixtures securely."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_assert_args_valid_input(self):
        """Test _assert_args with valid inputs."""
        # Should not raise any exception
        custom._assert_args(
            storage_account="teststorage",
            cert_file=self.mock_cert_file,
            public_key_file=self.mock_public_key,
            private_key_file=self.mock_private_key
        )

    def test_assert_args_missing_storage_account(self):
        """Test _assert_args with missing storage account."""
        with self.assertRaises(azclierror.RequiredArgumentMissingError):
            custom._assert_args(
                storage_account=None,
                cert_file=self.mock_cert_file,
                public_key_file=self.mock_public_key,
                private_key_file=self.mock_private_key
            )

    def test_assert_args_empty_storage_account(self):
        """Test _assert_args with empty storage account."""
        with self.assertRaises(azclierror.RequiredArgumentMissingError):
            custom._assert_args(
                storage_account="",
                cert_file=self.mock_cert_file,
                public_key_file=self.mock_public_key,
                private_key_file=self.mock_private_key
            )

    def test_assert_args_missing_cert_file(self):
        """Test _assert_args with non-existent certificate file."""
        with self.assertRaises(azclierror.FileOperationError):
            custom._assert_args(
                storage_account="teststorage",
                cert_file="/nonexistent/cert.pub",
                public_key_file=None,
                private_key_file=None
            )

    def test_assert_args_missing_public_key_file(self):
        """Test _assert_args with non-existent public key file."""
        with self.assertRaises(azclierror.FileOperationError):
            custom._assert_args(
                storage_account="teststorage",
                cert_file=None,
                public_key_file="/nonexistent/key.pub",
                private_key_file=None
            )

    def test_assert_args_missing_private_key_file(self):
        """Test _assert_args with non-existent private key file."""
        with self.assertRaises(azclierror.FileOperationError):
            custom._assert_args(
                storage_account="teststorage",
                cert_file=None,
                public_key_file=None,
                private_key_file="/nonexistent/key"
            )

    @mock.patch('azext_sftp.file_utils.delete_file')
    @mock.patch('shutil.rmtree')
    def test_cleanup_credentials_delete_all(self, mock_rmtree, mock_delete_file):
        """Test _cleanup_credentials with all cleanup flags enabled."""
        custom._cleanup_credentials(
            delete_keys=True,
            delete_cert=True,
            credentials_folder=self.temp_dir,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            public_key_file=self.mock_public_key
        )
        
        # Should delete all files and folder
        self.assertEqual(mock_delete_file.call_count, 3)  # cert + private + public
        mock_rmtree.assert_called_once_with(self.temp_dir)

    @mock.patch('azext_sftp.file_utils.delete_file')
    @mock.patch('shutil.rmtree')
    def test_cleanup_credentials_delete_cert_only(self, mock_rmtree, mock_delete_file):
        """Test _cleanup_credentials with only cert deletion enabled."""
        custom._cleanup_credentials(
            delete_keys=False,
            delete_cert=True,
            credentials_folder=None,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            public_key_file=self.mock_public_key
        )
        
        # Should only delete certificate
        mock_delete_file.assert_called_once()
        mock_rmtree.assert_not_called()

    @mock.patch('azext_sftp.file_utils.delete_file')
    @mock.patch('shutil.rmtree')
    def test_cleanup_credentials_delete_keys_only(self, mock_rmtree, mock_delete_file):
        """Test _cleanup_credentials with only key deletion enabled."""
        custom._cleanup_credentials(
            delete_keys=True,
            delete_cert=False,
            credentials_folder=None,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            public_key_file=self.mock_public_key
        )
        
        # Should delete both keys
        self.assertEqual(mock_delete_file.call_count, 2)  # private + public keys
        mock_rmtree.assert_not_called()

    @mock.patch('azext_sftp.file_utils.delete_file')
    @mock.patch('shutil.rmtree')
    @mock.patch('os.path.isfile')
    def test_cleanup_credentials_missing_files(self, mock_isfile, mock_rmtree, mock_delete_file):
        """Test _cleanup_credentials with missing files (should not error)."""
        mock_isfile.return_value = False  # Simulate missing files
        
        custom._cleanup_credentials(
            delete_keys=True,
            delete_cert=True,
            credentials_folder=self.temp_dir,
            cert_file="/nonexistent/cert.pub",
            private_key_file="/nonexistent/key",
            public_key_file="/nonexistent/key.pub"
        )
        
        # Should not attempt to delete missing files
        mock_delete_file.assert_not_called()
        mock_rmtree.assert_called_once()  # But should still try to delete folder

    @mock.patch('azext_sftp.file_utils.delete_file')
    @mock.patch('shutil.rmtree')
    def test_cleanup_credentials_oserror_handling(self, mock_rmtree, mock_delete_file):
        """Test _cleanup_credentials handles OSError gracefully."""
        mock_delete_file.side_effect = OSError("Permission denied")
        mock_rmtree.side_effect = OSError("Directory busy")
        
        # Should not raise exception
        custom._cleanup_credentials(
            delete_keys=True,
            delete_cert=True,
            credentials_folder=self.temp_dir,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            public_key_file=self.mock_public_key
        )

    def test_get_storage_endpoint_suffix_azure_cloud(self):
        """Test _get_storage_endpoint_suffix for Azure Cloud."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        
        result = custom._get_storage_endpoint_suffix(cmd)
        self.assertEqual(result, "blob.core.windows.net")

    def test_get_storage_endpoint_suffix_azure_china_cloud(self):
        """Test _get_storage_endpoint_suffix for Azure China Cloud."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurechinacloud"
        
        result = custom._get_storage_endpoint_suffix(cmd)
        self.assertEqual(result, "blob.core.chinacloudapi.cn")

    def test_get_storage_endpoint_suffix_azure_government_cloud(self):
        """Test _get_storage_endpoint_suffix for Azure Government Cloud."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azureusgovernment"
        
        result = custom._get_storage_endpoint_suffix(cmd)
        self.assertEqual(result, "blob.core.usgovcloudapi.net")

    def test_get_storage_endpoint_suffix_unknown_cloud(self):
        """Test _get_storage_endpoint_suffix for unknown cloud (defaults to Azure Cloud)."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "unknowncloud"
        
        result = custom._get_storage_endpoint_suffix(cmd)
        self.assertEqual(result, "blob.core.windows.net")  # Should default

    def test_get_storage_endpoint_suffix_case_insensitive(self):
        """Test _get_storage_endpoint_suffix is case-insensitive."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "AZURECLOUD"  # Uppercase
        
        result = custom._get_storage_endpoint_suffix(cmd)
        self.assertEqual(result, "blob.core.windows.net")

    @mock.patch('azext_sftp.sftp_utils.start_sftp_connection')
    def test_do_sftp_op_success(self, mock_start_connection):
        """Test _do_sftp_op with successful operation."""
        sftp_session = mock.Mock()
        sftp_session.validate_session = mock.Mock()
        mock_start_connection.return_value = "success"
        
        result = custom._do_sftp_op(sftp_session, mock_start_connection)
        
        sftp_session.validate_session.assert_called_once()
        mock_start_connection.assert_called_once_with(sftp_session)
        self.assertEqual(result, "success")

    @mock.patch('azext_sftp.sftp_utils.start_sftp_connection')
    def test_do_sftp_op_validation_failure(self, mock_start_connection):
        """Test _do_sftp_op with session validation failure."""
        sftp_session = mock.Mock()
        sftp_session.validate_session.side_effect = Exception("Validation failed")
        
        with self.assertRaises(Exception):
            custom._do_sftp_op(sftp_session, mock_start_connection)
        
        sftp_session.validate_session.assert_called_once()
        mock_start_connection.assert_not_called()

    @mock.patch('azext_sftp.sftp_utils.start_sftp_connection')
    def test_do_sftp_op_connection_failure(self, mock_start_connection):
        """Test _do_sftp_op with connection failure."""
        sftp_session = mock.Mock()
        sftp_session.validate_session = mock.Mock()
        mock_start_connection.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            custom._do_sftp_op(sftp_session, mock_start_connection)
        
        sftp_session.validate_session.assert_called_once()
        mock_start_connection.assert_called_once_with(sftp_session)


class TestSftpCertificateGeneration(unittest.TestCase):
    """
    Test class for SFTP certificate generation functions.
    Following Azure best practices for security and error handling.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_cert_test_")
        self.mock_public_key = os.path.join(self.temp_dir, "test_key.pub")
        
        # Create mock public key file
        with open(self.mock_public_key, 'w') as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAA mock@test.com")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @mock.patch('azext_sftp.rsa_parser.RSAParser')
    def test_get_modulus_exponent_success(self, mock_parser_class):
        """Test successful modulus and exponent extraction."""
        mock_parser = mock.Mock()
        mock_parser.modulus = "test_modulus"
        mock_parser.exponent = "test_exponent"
        mock_parser_class.return_value = mock_parser
        
        modulus, exponent = custom._get_modulus_exponent(self.mock_public_key)
        
        self.assertEqual(modulus, "test_modulus")
        self.assertEqual(exponent, "test_exponent")
        mock_parser.parse.assert_called_once()

    def test_get_modulus_exponent_missing_file(self):
        """Test error handling for missing public key file."""
        with self.assertRaises(azclierror.FileOperationError):
            custom._get_modulus_exponent("/nonexistent/key.pub")

    @mock.patch('azext_sftp.rsa_parser.RSAParser')
    def test_get_modulus_exponent_parse_error(self, mock_parser_class):
        """Test error handling for public key parsing failure."""
        mock_parser = mock.Mock()
        mock_parser.parse.side_effect = Exception("Invalid key format")
        mock_parser_class.return_value = mock_parser
        
        with self.assertRaises(azclierror.FileOperationError):
            custom._get_modulus_exponent(self.mock_public_key)

    @mock.patch('oschmod.set_mode')
    def test_write_cert_file_success(self, mock_set_mode):
        """Test successful certificate file writing."""
        cert_file = os.path.join(self.temp_dir, "test_cert.pub")
        certificate_contents = "TEST_CERTIFICATE_DATA"
        
        result = custom._write_cert_file(certificate_contents, cert_file)
        
        self.assertEqual(result, cert_file)
        self.assertTrue(os.path.exists(cert_file))
        
        with open(cert_file, 'r') as f:
            content = f.read()
        self.assertIn("ssh-rsa-cert-v01@openssh.com", content)
        self.assertIn(certificate_contents, content)
        
        mock_set_mode.assert_called_once_with(cert_file, 0o644)

    @mock.patch('hashlib.sha256')
    def test_prepare_jwk_data_success(self, mock_hash):
        """Test successful JWK data preparation."""
        mock_hash_obj = mock.Mock()
        mock_hash_obj.hexdigest.return_value = "test_key_id"
        mock_hash.return_value = mock_hash_obj
        
        with mock.patch('azext_sftp.custom._get_modulus_exponent') as mock_get_mod_exp:
            mock_get_mod_exp.return_value = ("test_modulus", "test_exponent")
            
            result = custom._prepare_jwk_data(self.mock_public_key)
            
            self.assertIn("token_type", result)
            self.assertIn("req_cnf", result)
            self.assertIn("key_id", result)
            self.assertEqual(result["token_type"], "ssh-cert")
            self.assertEqual(result["key_id"], "test_key_id")


if __name__ == '__main__':
    unittest.main()
