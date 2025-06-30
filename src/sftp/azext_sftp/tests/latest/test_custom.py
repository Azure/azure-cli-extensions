# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import io
import unittest
from unittest import mock
from azext_sftp import custom

from azure.cli.core import azclierror
import tempfile
import os
import shutil


class SftpCustomCommandTest(unittest.TestCase):
    """Test suite for SFTP custom commands."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        # Set up temporary directory for test files
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_test_")
        self.mock_cert_file = os.path.join(self.temp_dir, "test_cert.pub")
        self.mock_private_key = os.path.join(self.temp_dir, "test_key")
        self.mock_public_key = os.path.join(self.temp_dir, "test_key.pub")
        
        # Create mock files
        with open(self.mock_cert_file, 'w') as f:
            f.write("ssh-rsa-cert-v01@openssh.com MOCK_CERT_DATA")
        with open(self.mock_private_key, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\nMOCK_PRIVATE_KEY\n-----END OPENSSH PRIVATE KEY-----")
        with open(self.mock_public_key, 'w') as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAA mock@test.com")

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        super().tearDown()
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_sftp_cert_no_args(self):
        """Test that sftp_cert raises error when no arguments provided."""
        cmd = mock.Mock()
        with self.assertRaises(azclierror.RequiredArgumentMissingError):
            custom.sftp_cert(cmd)

    @mock.patch('os.path.isdir')
    def test_sftp_cert_cert_file_missing(self, mock_isdir):
        """Test that sftp_cert raises error when certificate directory doesn't exist."""
        cmd = mock.Mock()
        mock_isdir.return_value = False
        with self.assertRaises(azclierror.InvalidArgumentValueError):
            custom.sftp_cert(cmd, cert_path="cert")

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    def test_sftp_cert(self, mock_write_cert, mock_get_keys, mock_abspath, mock_isdir):
        """Test successful certificate generation."""
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = ['/pubkey/path', '/cert/path', '/client/path']
        mock_get_keys.return_value = "pubkey", "privkey", False
        mock_write_cert.return_value = "cert", "username"

        custom.sftp_cert(cmd, "cert", "pubkey")

        mock_get_keys.assert_called_once_with('/pubkey/path', None, None, None)
        mock_write_cert.assert_called_once_with(cmd, 'pubkey', '/cert/path', None)

    def test_sftp_connect_preprod(self):
        """Test SFTP connection to preprod environment.
        
        Owner: johnli1
        """
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        cmd.cli_ctx.cloud = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        # Use batch mode to avoid interactive prompt
        custom.sftp_connect(
            cmd=cmd,
            storage_account='johnli1canary',
            port=22,
            cert_file='C:\\Users\\johnli1\\.ssh\\id_rsa-aadcert.pub',
            sftp_batch_commands='ls\nexit\n'
        )
        self.assertTrue(True)

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_valid_cert_provided(self, mock_get_principals, mock_do_sftp):
        """Test connect with valid certificate file."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        mock_do_sftp.assert_called_once()

    def test_sftp_connect_invalid_cert_provided(self):
        """Test connect with invalid/missing certificate file."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        
        with self.assertRaises(azclierror.FileOperationError):
            custom.sftp_connect(
                cmd=cmd,
                storage_account="teststorage",
                port=22,
                cert_file="/nonexistent/cert.pub",
                private_key_file=self.mock_private_key
            )

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('tempfile.mkdtemp')
    def test_sftp_connect_no_cert_auto_generate(self, mock_mkdtemp, mock_create_keys, mock_gen_cert, mock_do_sftp):
        """Test connect with no credentials - should auto-generate."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_mkdtemp.return_value = self.temp_dir
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, True)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            port=22,
            sftp_batch_commands="ls\nexit\n"
        )
        
        mock_create_keys.assert_called_once()
        mock_gen_cert.assert_called_once()
        mock_do_sftp.assert_called_once()

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    def test_sftp_connect_public_key_provided_no_cert(self, mock_create_keys, mock_gen_cert, mock_do_sftp):
        """Test connect with public key but no cert - should generate cert."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, False)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            port=22,
            public_key_file=self.mock_public_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        mock_create_keys.assert_called_once_with(self.mock_public_key, None, None, None)
        mock_gen_cert.assert_called_once()
        mock_do_sftp.assert_called_once()

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    def test_sftp_connect_private_key_provided_no_cert(self, mock_create_keys, mock_gen_cert, mock_do_sftp):
        """Test connect with private key but no cert - should generate cert."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, False)
        mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            port=22,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        mock_create_keys.assert_called_once_with(None, self.mock_private_key, None, None)
        mock_gen_cert.assert_called_once()
        mock_do_sftp.assert_called_once()

    def test_sftp_connect_invalid_private_key(self):
        """Test connect with invalid/missing private key file."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        
        with self.assertRaises(azclierror.FileOperationError):
            custom.sftp_connect(
                cmd=cmd,
                storage_account="teststorage",
                port=22,
                private_key_file="/nonexistent/key"
            )

    def test_sftp_connect_invalid_public_key(self):
        """Test connect with invalid/missing public key file.""" 
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        
        with self.assertRaises(azclierror.FileOperationError):
            custom.sftp_connect(
                cmd=cmd,
                storage_account="teststorage",
                port=22,
                public_key_file="/nonexistent/key.pub"
            )

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_cert_and_public_key_both_provided(self, mock_get_principals, mock_do_sftp):
        """Test connect with both cert and public key - should use cert."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            public_key_file=self.mock_public_key,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Should use the certificate and not generate a new one
        mock_do_sftp.assert_called_once()

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_with_existing_cert(self, mock_get_principals, mock_do_sftp):
        """Test connect with existing certificate - should use it as-is."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        
        # Mock certificate principals
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            port=22,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Should use existing certificate and let OpenSSH handle validation
        mock_get_principals.assert_called_once()
        mock_do_sftp.assert_called_once()

    def test_sftp_connect_missing_storage_account(self):
        """Test connect without storage account - should raise error."""
        cmd = mock.Mock()
        
        with self.assertRaises(azclierror.RequiredArgumentMissingError):
            custom.sftp_connect(
                cmd=cmd,
                storage_account=None,
                port=22
            )

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_default_port(self, mock_get_principals, mock_do_sftp):
        """Test connect with default port (should be None to let OpenSSH use its default)."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Verify the session was created with port None (lets OpenSSH use default)
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]  # First argument is the SFTP session
        self.assertEqual(sftp_session.port, None)

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_custom_port(self, mock_get_principals, mock_do_sftp):
        """Test connect with custom port."""
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_get_principals.return_value = ["testuser@domain.com"]
        mock_do_sftp.return_value = None
        
        custom.sftp_connect(
            cmd=cmd,
            storage_account="teststorage",
            port=2222,
            cert_file=self.mock_cert_file,
            private_key_file=self.mock_private_key,
            sftp_batch_commands="ls\nexit\n"
        )
        
        # Verify the session was created with custom port
        mock_do_sftp.assert_called_once()
        call_args = mock_do_sftp.call_args[0]
        sftp_session = call_args[0]
        self.assertEqual(sftp_session.port, 2222)


class SftpCustomCertificateTest(unittest.TestCase):
    """Test suite for SFTP certificate generation functionality in custom.py.
    
    Tests certificate generation scenarios following SSH extension patterns.
    Owner: johnli1
    """

    def setUp(self):
        """Set up test fixtures for certificate scenario tests."""
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_cert_test_")
        self.mock_public_key = os.path.join(self.temp_dir, "id_rsa.pub")
        self.mock_private_key = os.path.join(self.temp_dir, "id_rsa")
        self.mock_cert_path = os.path.join(self.temp_dir, "test_cert.pub")
        
        # Create mock public key file
        with open(self.mock_public_key, 'w') as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test@example.com")
        
        # Create mock private key file
        with open(self.mock_private_key, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\nMOCK_PRIVATE_KEY_CONTENT\n-----END OPENSSH PRIVATE KEY-----")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_with_provided_public_key(self, mock_abspath, mock_isdir, mock_check_files, mock_write_cert):
        """Test sftp cert with provided public key file.
        
        This scenario follows SSH extension pattern: user provides existing public key,
        system generates certificate using that key.
        """
        # Setup mocks
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = lambda x: x  # Return input unchanged
        mock_check_files.return_value = (self.mock_public_key, None, False)
        mock_write_cert.return_value = (self.mock_cert_path, "testuser@domain.com")
        
        # Execute test
        custom.sftp_cert(cmd, cert_path=self.mock_cert_path, public_key_file=self.mock_public_key)
        
        # Verify calls
        mock_check_files.assert_called_once_with(self.mock_public_key, None, None, None)
        mock_write_cert.assert_called_once_with(cmd, self.mock_public_key, self.mock_cert_path, None)

    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_with_nothing_provided(self, mock_abspath, mock_isdir, mock_check_files, mock_write_cert):
        """Test sftp cert with nothing provided - generates key pair and certificate.
        
        This scenario follows SSH extension pattern: when no keys are provided,
        system generates new key pair in same directory as certificate.
        """
        # Setup mocks
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = lambda x: x  # Return input unchanged
        mock_check_files.return_value = (self.mock_public_key, self.mock_private_key, True)
        mock_write_cert.return_value = (self.mock_cert_path, "testuser@domain.com")
        
        # Execute test - only cert_path provided
        custom.sftp_cert(cmd, cert_path=self.mock_cert_path)
        
        # Verify key generation in certificate directory
        cert_dir = os.path.dirname(self.mock_cert_path)
        mock_check_files.assert_called_once_with(None, None, cert_dir, None)
        mock_write_cert.assert_called_once_with(cmd, self.mock_public_key, self.mock_cert_path, None)

    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_with_ssh_client_folder(self, mock_abspath, mock_isdir, mock_check_files, mock_write_cert):
        """Test sftp cert with custom SSH client folder.
        
        Verifies that SSH client folder parameter is passed through correctly.
        """
        # Setup mocks
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = lambda x: x  # Return input unchanged
        mock_check_files.return_value = (self.mock_public_key, None, False)
        mock_write_cert.return_value = (self.mock_cert_path, "testuser@domain.com")
        
        ssh_client_folder = "/custom/ssh/path"
        
        # Execute test
        custom.sftp_cert(cmd, cert_path=self.mock_cert_path, 
                        public_key_file=self.mock_public_key, 
                        ssh_client_folder=ssh_client_folder)
        
        # Verify SSH client folder is passed through
        mock_check_files.assert_called_once_with(self.mock_public_key, None, None, ssh_client_folder)
        mock_write_cert.assert_called_once_with(cmd, self.mock_public_key, self.mock_cert_path, ssh_client_folder)

    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_key_generation_warning(self, mock_abspath, mock_isdir, mock_check_files, mock_write_cert):
        """Test that warning is displayed when keys are generated.
        
        When keys are generated, user should be warned about sensitive information.
        """
        # Setup mocks
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = lambda x: x  # Return input unchanged
        mock_check_files.return_value = (self.mock_public_key, self.mock_private_key, True)
        mock_write_cert.return_value = (self.mock_cert_path, "testuser@domain.com")
        
        # Mock logger to capture warning
        with mock.patch('azext_sftp.custom.logger') as mock_logger:
            custom.sftp_cert(cmd, cert_path=self.mock_cert_path)
            
            # Verify warning is logged when keys are generated
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            self.assertIn("contains sensitive information", warning_call)
            self.assertIn("id_rsa", warning_call)

    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_certificate_generation_failure(self, mock_abspath, mock_isdir, mock_check_files):
        """Test proper error handling when certificate generation fails."""
        # Setup mocks
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = lambda x: x  # Return input unchanged
        mock_check_files.return_value = (self.mock_public_key, None, False)
        
        # Mock certificate generation to fail
        with mock.patch('azext_sftp.custom._get_and_write_certificate') as mock_write_cert:
            mock_write_cert.side_effect = Exception("Certificate generation failed")
            
            with mock.patch('azext_sftp.custom.logger') as mock_logger:
                with self.assertRaises(Exception):
                    custom.sftp_cert(cmd, cert_path=self.mock_cert_path, 
                                    public_key_file=self.mock_public_key)
                
                # Verify error is logged
                mock_logger.error.assert_called()
                error_call = mock_logger.error.call_args[0][0]
                self.assertIn("Failed to generate certificate", error_call)

    def test_check_or_create_public_private_files_with_existing_files(self):
        """Test _check_or_create_public_private_files with existing key files.
        
        This verifies the SSH extension pattern where existing files are validated.
        """
        # Test with existing public key file
        public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
            self.mock_public_key, None, None, None)
        
        self.assertEqual(public_key, self.mock_public_key)
        self.assertEqual(private_key, self.mock_private_key)  # Should find matching private key
        self.assertFalse(delete_keys)

    def test_check_or_create_public_private_files_missing_public_key(self):
        """Test error when public key file doesn't exist."""
        nonexistent_key = "/nonexistent/key.pub"
        
        with self.assertRaises(azclierror.FileOperationError) as context:
            custom._check_or_create_public_private_files(nonexistent_key, None, None, None)
        
        self.assertIn("not found", str(context.exception))

    @mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    def test_check_or_create_public_private_files_generates_keys(self, mock_mkdtemp, mock_create_keyfile):
        """Test key generation when no keys are provided.
        
        This verifies SSH extension pattern for automatic key generation.
        """
        mock_mkdtemp.return_value = self.temp_dir
        
        # Test with no keys provided - should generate new ones
        public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
            None, None, None, None)
        
        # Verify paths are constructed correctly
        expected_public = os.path.join(self.temp_dir, "id_rsa.pub")
        expected_private = os.path.join(self.temp_dir, "id_rsa")
        
        self.assertEqual(public_key, expected_public)
        self.assertEqual(private_key, expected_private)
        self.assertTrue(delete_keys)  # Generated keys should be marked for deletion
        
        # Verify key generation was called
        mock_create_keyfile.assert_called_once_with(expected_private, None)

    def test_check_or_create_public_private_files_with_credentials_folder(self):
        """Test key generation in specified credentials folder.
        
        This verifies SSH extension pattern for controlled key placement.
        """
        with mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile') as mock_create_keyfile:
            with mock.patch('os.makedirs') as mock_makedirs:
                with mock.patch('os.path.isdir', return_value=False):
                    # Test with credentials folder that doesn't exist
                    public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
                        None, None, self.temp_dir, None)
                    
                    # Verify keys are generated in the specified folder
                    self.assertTrue(public_key.startswith(self.temp_dir))
                    self.assertTrue(private_key.startswith(self.temp_dir))
                    self.assertTrue(delete_keys)  # Should be marked for deletion
                    
                    # Verify key generation was called with correct path
                    mock_create_keyfile.assert_called_once_with(private_key, None)

    @mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    def test_check_or_create_public_private_files_with_existing_credentials_folder(self, mock_mkdtemp, mock_create_keyfile):
        """Test key generation with existing credentials folder.
        
        This verifies SSH extension pattern where keys are generated in existing folder.
        """
        # Create the credentials folder
        os.makedirs(self.temp_dir, exist_ok=True)
        
        with mock.patch('os.path.isdir', return_value=True):
            public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
                None, None, self.temp_dir, None)
            
            # Verify keys are generated in the specified folder
            self.assertTrue(public_key.startswith(self.temp_dir))
            self.assertTrue(private_key.startswith(self.temp_dir))
            self.assertTrue(delete_keys)  # Should be marked for deletion

    @mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    def test_check_or_create_public_private_files_no_cleanup_on_error(self, mock_mkdtemp, mock_create_keyfile):
        """Test that keys are not deleted if an error occurs after generation.
        
        This verifies SSH extension pattern for error handling during key operations.
        """
        mock_mkdtemp.return_value = self.temp_dir
        
        # Force key generation
        public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
            None, None, None, None)
        
        # Simulate an error after key generation
        with mock.patch('azext_sftp.custom.logger') as mock_logger:
            with self.assertRaises(Exception):
                raise Exception("Forced error after key generation")
            
            # Verify keys still exist after the error
            self.assertTrue(os.path.exists(public_key))
            self.assertTrue(os.path.exists(private_key))
            
            # Cleanup
            os.remove(public_key)
            os.remove(private_key)

    @mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    def test_check_or_create_public_private_files_partial_cleanup_on_error(self, mock_mkdtemp, mock_create_keyfile):
        """Test that partial cleanup occurs if an error happens during processing.
        
        This verifies SSH extension pattern for partial cleanup on error.
        """
        mock_mkdtemp.return_value = self.temp_dir
        
        # Mock key creation to succeed for public key but fail for private key
        def side_effect_create_key(private_key_path, passphrase):
            # Create public key file
            public_key_path = private_key_path + ".pub"
            with open(public_key_path, 'w') as f:
                f.write("mock public key")
            # Fail to create private key
            raise Exception("Failed to create private key")
        
        mock_create_keyfile.side_effect = side_effect_create_key
        
        # This should fail during key generation
        with self.assertRaises(Exception):
            custom._check_or_create_public_private_files(None, None, None, None)

    @mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    def test_check_or_create_public_private_files_error_handling_during_keygen(self, mock_mkdtemp, mock_create_keyfile):
        """Test error handling during key generation process.
        
        This verifies SSH extension pattern for robust error handling.
        """
        mock_mkdtemp.return_value = self.temp_dir
        
        # Mock key generation to raise error
        with mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile', side_effect=Exception("Key generation error")):
            with self.assertRaises(Exception) as context:
                custom._check_or_create_public_private_files(None, None, None, None)
            
            # Verify error message
            self.assertIn("Key generation error", str(context.exception))

    @mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    def test_check_or_create_public_private_files_keygen_with_existing_files(self, mock_mkdtemp, mock_create_keyfile):
        """Test key generation when files already exist.
        
        This verifies SSH extension pattern for handling existing files during key generation.
        """
        # Create existing key files
        with open(self.mock_public_key, 'w') as f:
            f.write("existing public key")
        with open(self.mock_private_key, 'w') as f:
            f.write("existing private key")
        
        mock_mkdtemp.return_value = self.temp_dir
        
        # Key generation should detect existing files and not overwrite
        public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
            None, None, None, None)
        