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

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        super().tearDown()

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

    def setUp(self):
        """Set up test fixtures for connect tests."""
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
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

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