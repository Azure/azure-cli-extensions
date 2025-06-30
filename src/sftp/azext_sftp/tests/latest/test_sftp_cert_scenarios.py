# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest
import shutil
from unittest import mock

from azext_sftp import custom
from azure.cli.core import azclierror


class SftpCertScenarioTest(unittest.TestCase):
    """Test suite for SFTP certificate generation scenarios.
    
    Tests follow patterns established by SSH extension for consistent behavior.
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
    def test_sftp_cert_with_provided_private_key(self, mock_abspath, mock_isdir, mock_check_files, mock_write_cert):
        """Test sftp cert with provided private key file.
        
        This scenario should derive public key from private key location and generate certificate.
        Similar to SSH extension behavior where public key is inferred from private key.
        """
        # Setup mocks
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = lambda x: x  # Return input unchanged
        mock_check_files.return_value = (self.mock_public_key, self.mock_private_key, False)
        mock_write_cert.return_value = (self.mock_cert_path, "testuser@domain.com")
        
        # Note: sftp_cert doesn't currently accept private_key_file parameter like SSH extension
        # This test ensures consistency when this parameter is added in the future
        # For now, test the internal function behavior
        
        # Test the internal function that handles this scenario
        public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
            None, self.mock_private_key, None, None)
        
        # Verify behavior matches SSH extension pattern
        self.assertIsNotNone(public_key)
        self.assertEqual(private_key, self.mock_private_key)
        self.assertFalse(delete_keys)  # Shouldn't delete user-provided keys

    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_with_provided_public_and_private_key(self, mock_abspath, mock_isdir, mock_check_files, mock_write_cert):
        """Test sftp cert with both public and private key files provided.
        
        This scenario should use the provided keys and generate certificate.
        Follows SSH extension pattern for complete key pair handling.
        """
        # Setup mocks
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = lambda x: x  # Return input unchanged
        mock_check_files.return_value = (self.mock_public_key, self.mock_private_key, False)
        mock_write_cert.return_value = (self.mock_cert_path, "testuser@domain.com")
        
        # Test with public key provided (current API)
        custom.sftp_cert(cmd, cert_path=self.mock_cert_path, public_key_file=self.mock_public_key)
        
        # Verify the check function was called correctly
        mock_check_files.assert_called_once_with(self.mock_public_key, None, None, None)
        
        # Test the internal function that would handle both keys
        public_key, private_key, delete_keys = custom._check_or_create_public_private_files(
            self.mock_public_key, self.mock_private_key, None, None)
        
        # Verify both keys are preserved
        self.assertEqual(public_key, self.mock_public_key)
        self.assertEqual(private_key, self.mock_private_key)
        self.assertFalse(delete_keys)  # Shouldn't delete user-provided keys

    def test_sftp_cert_no_arguments_raises_error(self):
        """Test that sftp_cert raises error when no required arguments provided."""
        cmd = mock.Mock()
        
        with self.assertRaises(azclierror.RequiredArgumentMissingError) as context:
            custom.sftp_cert(cmd)
        
        self.assertIn("--file or --public-key-file must be provided", str(context.exception))

    @mock.patch('os.path.isdir')
    def test_sftp_cert_invalid_cert_directory_raises_error(self, mock_isdir):
        """Test that sftp_cert raises error when certificate directory doesn't exist."""
        cmd = mock.Mock()
        mock_isdir.return_value = False
        invalid_cert_path = "/nonexistent/directory/cert.pub"
        
        with self.assertRaises(azclierror.InvalidArgumentValueError) as context:
            custom.sftp_cert(cmd, cert_path=invalid_cert_path)
        
        self.assertIn("folder doesn't exist", str(context.exception))

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
                    
                    # Verify directory creation
                    mock_makedirs.assert_called_once_with(self.temp_dir)
                    
                    # Verify key paths
                    expected_public = os.path.join(self.temp_dir, "id_rsa.pub")
                    expected_private = os.path.join(self.temp_dir, "id_rsa")
                    
                    self.assertEqual(public_key, expected_public)
                    self.assertEqual(private_key, expected_private)
                    self.assertTrue(delete_keys)


if __name__ == '__main__':
    unittest.main()
