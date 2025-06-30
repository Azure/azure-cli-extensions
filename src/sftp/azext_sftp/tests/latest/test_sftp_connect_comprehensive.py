# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Comprehensive unit tests for sftp_connect function covering all credential scenarios.
Tests follow Azure best practices for error handling, security, and reliability.
"""

import unittest
from unittest import mock
import tempfile
import os
import shutil
from azext_sftp import custom
from azure.cli.core import azclierror


class TestSftpConnectCredentialScenarios(unittest.TestCase):
    """
    Test class for comprehensive SFTP connect credential scenarios.
    Following Azure best practices for unit testing with proper mocking and cleanup.
    """

    def setUp(self):
        """Set up test fixtures with secure temporary directory and mock files."""
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_connect_test_")
        self.mock_cert_file = os.path.join(self.temp_dir, "test_cert.pub")
        self.mock_private_key = os.path.join(self.temp_dir, "test_key")
        self.mock_public_key = os.path.join(self.temp_dir, "test_key.pub")
        
        # Create realistic mock certificate content
        self._create_mock_certificate_file()
        self._create_mock_key_files()
        
        # Mock command context for different Azure clouds
        self.mock_cmd = self._create_mock_cmd_context()

    def tearDown(self):
        """Clean up test fixtures securely."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_mock_certificate_file(self):
        """Create a realistic mock certificate file for testing."""
        cert_content = "ssh-rsa-cert-v01@openssh.com AAAAHHNzaC1yc2EtY2VydC12MDFAB3BlbnNzaC5jb20MOCK_CERT_DATA"
        with open(self.mock_cert_file, 'w', encoding='utf-8') as f:
            f.write(cert_content)
        # Set appropriate permissions
        os.chmod(self.mock_cert_file, 0o644)

    def _create_mock_key_files(self):
        """Create realistic mock key files for testing."""
        # Mock private key
        private_key_content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtcn
MOCK_PRIVATE_KEY_DATA
-----END OPENSSH PRIVATE KEY-----"""
        with open(self.mock_private_key, 'w', encoding='utf-8') as f:
            f.write(private_key_content)
        os.chmod(self.mock_private_key, 0o600)  # Secure permissions
        
        # Mock public key  
        public_key_content = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7hr mock@test.com"
        with open(self.mock_public_key, 'w', encoding='utf-8') as f:
            f.write(public_key_content)
        os.chmod(self.mock_public_key, 0o644)

    def _create_mock_cmd_context(self, cloud_name="azurecloud"):
        """Create mock command context for different Azure clouds."""
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        cmd.cli_ctx.cloud = mock.Mock()
        cmd.cli_ctx.cloud.name = cloud_name
        return cmd

    # Test Scenario 1: Valid certificate provided
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_valid_certificate_provided(self, mock_get_principals, mock_do_sftp):
        """Test successful connection with valid certificate file."""
        # Arrange
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]
        self.assertEqual(sftp_session.storage_account, "teststorage")
        self.assertEqual(sftp_session.username, "teststorage.testuser")

    # Test Scenario 2: Invalid certificate file
    def test_invalid_certificate_file(self):
        """Test error handling for non-existent certificate file."""
        with self.assertRaises(azclierror.FileOperationError) as context:
            custom.sftp_connect(
                cmd=self.mock_cmd,
                storage_account="teststorage",
                port=22,
                cert_file="/nonexistent/cert.pub"
            )
        self.assertIn("Certificate file", str(context.exception))

    # Test Scenario 3: No credentials - auto-generate
    @mock.patch('azext_sftp.custom._cleanup_credentials')
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('tempfile.mkdtemp')
    def test_no_credentials_auto_generate(self, mock_mkdtemp, mock_create_keys, 
                                        mock_gen_cert, mock_do_sftp, mock_cleanup):
        """Test auto-generation of credentials when none provided."""
        # Arrange
        mock_mkdtemp.return_value = self.temp_dir
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, True)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_create_keys.assert_called_once_with(None, None, mock.ANY, None)
        mock_gen_cert.assert_called_once()
        mock_do_sftp.assert_called_once()
        mock_cleanup.assert_called_once()

    # Test Scenario 4: Public key only - generate certificate
    @mock.patch('azext_sftp.custom._cleanup_credentials')
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    def test_public_key_only_generate_cert(self, mock_create_keys, mock_gen_cert, 
                                         mock_do_sftp, mock_cleanup):
        """Test certificate generation when only public key provided."""
        # Arrange
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, False)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            public_key_file=self.mock_public_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_create_keys.assert_called_once_with(self.mock_public_key, None, None, None)
        mock_gen_cert.assert_called_once_with(self.mock_cmd, self.mock_public_key, None, None)
        mock_do_sftp.assert_called_once()
        mock_cleanup.assert_called_once()

    # Test Scenario 5: Private key only - generate certificate
    @mock.patch('azext_sftp.custom._cleanup_credentials')
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    def test_private_key_only_generate_cert(self, mock_create_keys, mock_gen_cert, 
                                          mock_do_sftp, mock_cleanup):
        """Test certificate generation when only private key provided."""
        # Arrange
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, False)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_create_keys.assert_called_once_with(None, self.mock_private_key, None, None)
        mock_gen_cert.assert_called_once()
        mock_do_sftp.assert_called_once()

    # Test Scenario 5.5: Both public and private key provided - generate certificate
    @mock.patch('azext_sftp.custom._cleanup_credentials')
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    def test_both_public_and_private_key_generate_cert(self, mock_create_keys, mock_gen_cert, 
                                                      mock_do_sftp, mock_cleanup):
        """Test certificate generation when both public and private key provided.
        
        This scenario follows SSH extension pattern: when both keys are provided,
        system uses them to generate certificate and connects.
        Owner: johnli1
        """
        # Arrange
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, False)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            public_key_file=self.mock_public_key,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_create_keys.assert_called_once_with(self.mock_public_key, self.mock_private_key, None, None)
        mock_gen_cert.assert_called_once_with(self.mock_cmd, self.mock_public_key, None, None)
        mock_do_sftp.assert_called_once()
        mock_cleanup.assert_called_once()

    # Test Scenario 6: Existing certificate - use as-is (let OpenSSH handle validation)
    @mock.patch('azext_sftp.custom._cleanup_credentials')
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_existing_certificate_use_as_is(self, mock_get_principals, mock_do_sftp, mock_cleanup):
        """Test using existing certificate without validation - let OpenSSH handle it."""
        # Arrange
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_get_principals.assert_called_once()  # Should extract username from certificate
        mock_do_sftp.assert_called_once()  # Should proceed with connection
        # No certificate regeneration should occur - let OpenSSH validate

    # Test Scenario 7: Missing storage account
    def test_missing_storage_account(self):
        """Test error handling for missing storage account."""
        with self.assertRaises(azclierror.RequiredArgumentMissingError) as context:
            custom.sftp_connect(
                cmd=self.mock_cmd,
                storage_account=None,
                port=22
            )
        self.assertIn("Storage account name is required", str(context.exception))

    # Test Scenario 8: Port variations
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_custom_port(self, mock_get_principals, mock_do_sftp):
        """Test connection with custom port number."""
        # Arrange
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage", 
            port=2222,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]
        self.assertEqual(sftp_session.port, 2222)

    # Test Scenario 9: Both certificate and public key provided
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_cert_and_public_key_both_provided(self, mock_get_principals, mock_do_sftp):
        """Test preference for certificate when both cert and public key provided."""
        # Arrange
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            public_key_file=self.mock_public_key,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert - Should use certificate, not generate new one
        mock_do_sftp.assert_called_once()

    # Test Scenario 11: Different Azure cloud environments
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_azure_china_cloud_environment(self, mock_get_principals, mock_do_sftp):
        """Test connection in Azure China Cloud environment."""
        # Arrange
        china_cmd = self._create_mock_cmd_context("azurechinacloud")
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=china_cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]
        # Should use China cloud storage endpoint
        self.assertIn("chinacloudapi.cn", sftp_session.host)

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_azure_government_cloud_environment(self, mock_get_principals, mock_do_sftp):
        """Test connection in Azure Government Cloud environment."""
        # Arrange
        gov_cmd = self._create_mock_cmd_context("azureusgovernment")
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=gov_cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]
        # Should use Government cloud storage endpoint
        self.assertIn("usgovcloudapi.net", sftp_session.host)

    # Test Scenario 12: Username processing (UPN vs simple username)
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_upn_username_processing(self, mock_get_principals, mock_do_sftp):
        """Test proper handling of UPN usernames (extracting username part)."""
        # Arrange
        mock_get_principals.return_value = ["testuser@contoso.com"]  # UPN format
        mock_do_sftp.return_value = None
        
        # Act
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]
        # Should extract username part from UPN
        self.assertEqual(sftp_session.username, "teststorage.testuser")

    # Test Scenario 13: Error cleanup scenarios
    @mock.patch('azext_sftp.custom._cleanup_credentials')
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('tempfile.mkdtemp')
    def test_error_cleanup_on_connection_failure(self, mock_mkdtemp, mock_create_keys, 
                                               mock_gen_cert, mock_do_sftp, mock_cleanup):
        """Test proper cleanup when connection fails after credential generation."""
        # Arrange
        mock_mkdtemp.return_value = self.temp_dir
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, True)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.side_effect = Exception("Connection failed")
        
        # Act & Assert
        with self.assertRaises(Exception):
            custom.sftp_connect(
                cmd=self.mock_cmd,
                storage_account="teststorage",
                port=22,
                sftp_batch_commands="ls\nexit\n"
            )
        
        # Assert cleanup was called on error (called twice: once on error, once in finally)
        self.assertEqual(mock_cleanup.call_count, 2)

    # Test Scenario 14: Invalid public key file
    def test_invalid_public_key_file(self):
        """Test error handling for non-existent public key file."""
        with self.assertRaises(azclierror.FileOperationError) as context:
            custom.sftp_connect(
                cmd=self.mock_cmd,
                storage_account="teststorage",
                port=22,
                public_key_file="/nonexistent/key.pub"
            )
        self.assertIn("Public key file", str(context.exception))

    # Test Scenario 15: Invalid private key file  
    def test_invalid_private_key_file(self):
        """Test error handling for non-existent private key file."""
        with self.assertRaises(azclierror.FileOperationError) as context:
            custom.sftp_connect(
                cmd=self.mock_cmd,
                storage_account="teststorage",
                port=22,
                private_key_file="/nonexistent/key"
            )
        self.assertIn("Private key file", str(context.exception))

    # Test Scenario 16: Edge case - empty storage account name
    def test_empty_storage_account_name(self):
        """Test error handling for empty storage account name."""
        with self.assertRaises(azclierror.RequiredArgumentMissingError):
            custom.sftp_connect(
                cmd=self.mock_cmd,
                storage_account="",
                port=22
            )

    # Test Scenario 17: Default port behavior
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')  
    def test_default_port_22(self, mock_get_principals, mock_do_sftp):
        """Test that default port is None when not specified (SFTP session handles default)."""
        # Arrange
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        # Act - Don't specify port
        custom.sftp_connect(
            cmd=self.mock_cmd,
            storage_account="teststorage",
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Assert
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]
        # Should be None when not specified (SFTP session will handle default)
        self.assertIsNone(sftp_session.port)


if __name__ == '__main__':
    unittest.main()
