# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import tempfile
import os
import shutil
from unittest import mock

from azext_sftp import file_utils
from azure.cli.core import azclierror


class SftpFileUtilsTest(unittest.TestCase):
    """Test suite for SFTP file utilities.
    
    Owner: johnli1
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_file_utils_test_")

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        super().tearDown()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_delete_file_removes_existing_file(self):
        """Test delete_file removes an existing file."""
        # Arrange
        test_file = os.path.join(self.temp_dir, "test_delete.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Act
        file_utils.delete_file(test_file, "Test deletion message")
        
        # Assert
        self.assertFalse(os.path.isfile(test_file))

    def test_delete_file_with_nonexistent_file(self):
        """Test delete_file with nonexistent file does nothing."""
        # Arrange
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        
        # Act & Assert - Should not raise an exception
        file_utils.delete_file(nonexistent_file, "Test deletion message")

    @mock.patch('os.remove')
    def test_delete_file_handles_removal_error_with_warning(self, mock_remove):
        """Test delete_file handles removal errors with warning flag."""
        # Arrange
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        mock_remove.side_effect = OSError("Permission denied")
        
        # Act & Assert - Should not raise exception when warning=True
        with mock.patch('azext_sftp.file_utils.logger') as mock_logger:
            file_utils.delete_file(test_file, "Test message", warning=True)
            mock_logger.warning.assert_called_once()

    @mock.patch('os.remove')
    def test_delete_file_raises_error_without_warning(self, mock_remove):
        """Test delete_file raises error when warning=False."""
        # Arrange
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        mock_remove.side_effect = OSError("Permission denied")
        
        # Act & Assert
        with self.assertRaises(azclierror.FileOperationError):
            file_utils.delete_file(test_file, "Test message", warning=False)

class SftpFileUtilsCertificateTest(unittest.TestCase):
    """Test suite for SFTP file utilities certificate-related functions.
    
    Owner: johnli1
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.temp_dir = tempfile.mkdtemp(prefix="sftp_cert_test_")
        self.mock_public_key = os.path.join(self.temp_dir, "test_key.pub")
        
        # Create a mock public key file
        with open(self.mock_public_key, 'w') as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ test@example.com")

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        super().tearDown()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile')
    def test_check_or_create_public_private_files_generates_keys(self, mock_create_keyfile, mock_mkdtemp):
        """Test check_or_create_public_private_files generates new keys when none provided."""
        # Arrange
        mock_mkdtemp.return_value = self.temp_dir
        expected_public_key = os.path.join(self.temp_dir, "id_rsa.pub")
        expected_private_key = os.path.join(self.temp_dir, "id_rsa")
        
        # Mock the create_ssh_keyfile to create the files when called
        def create_key_files(private_key_path, ssh_client_folder):
            with open(private_key_path, 'w') as f:
                f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----")
            with open(private_key_path + ".pub", 'w') as f:
                f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ test@example.com")
        
        mock_create_keyfile.side_effect = create_key_files
        
        # Act
        public_key, private_key, delete_keys = file_utils.check_or_create_public_private_files(
            None, None, None)
        
        # Assert
        self.assertEqual(public_key, expected_public_key)
        self.assertEqual(private_key, expected_private_key)
        self.assertTrue(delete_keys)
        mock_create_keyfile.assert_called_once_with(expected_private_key, None)

    def test_check_or_create_public_private_files_with_credentials_folder(self):
        """Test key generation in specified credentials folder.
        
        This verifies SSH extension pattern for controlled key placement.
        """
        with mock.patch('azext_sftp.sftp_utils.create_ssh_keyfile') as mock_create_keyfile:
            with mock.patch('os.makedirs') as mock_makedirs:
                with mock.patch('os.path.isdir', return_value=False):
                    
                    # Mock the create_ssh_keyfile to actually create the files
                    def create_key_files(private_key_path, passphrase):
                        with open(private_key_path, 'w') as f:
                            f.write("mock private key")
                        with open(private_key_path + ".pub", 'w') as f:
                            f.write("mock public key")
                    
                    mock_create_keyfile.side_effect = create_key_files
                    
                    # Test with credentials folder that doesn't exist
                    public_key, private_key, delete_keys = file_utils.check_or_create_public_private_files(
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
        
        # Mock the create_ssh_keyfile to actually create the files
        def create_key_files(private_key_path, passphrase):
            with open(private_key_path, 'w') as f:
                f.write("mock private key")
            with open(private_key_path + ".pub", 'w') as f:
                f.write("mock public key")
        
        mock_create_keyfile.side_effect = create_key_files
        
        with mock.patch('os.path.isdir', return_value=True):
            public_key, private_key, delete_keys = file_utils.check_or_create_public_private_files(
                None, None, self.temp_dir, None)
            
            # Verify keys are generated in the specified folder
            self.assertTrue(public_key.startswith(self.temp_dir))
            self.assertTrue(private_key.startswith(self.temp_dir))
            self.assertTrue(delete_keys)  # Should be marked for deletion

    def test_check_or_create_public_private_files_with_existing_files(self):
        """Test check_or_create_public_private_files with existing key files."""
        # Arrange
        private_key = os.path.join(self.temp_dir, "existing_key")
        with open(private_key, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----")
        
        # Act
        public_key, returned_private_key, delete_keys = file_utils.check_or_create_public_private_files(
            self.mock_public_key, private_key, None)
        
        # Assert
        self.assertEqual(public_key, self.mock_public_key)
        self.assertEqual(returned_private_key, private_key)
        self.assertFalse(delete_keys)

    def test_check_or_create_public_private_files_missing_public_key_error(self):
        """Test check_or_create_public_private_files raises error when public key file missing."""
        # Arrange
        nonexistent_public_key = os.path.join(self.temp_dir, "nonexistent.pub")
        
        # Act & Assert
        with self.assertRaises(azclierror.FileOperationError) as context:
            file_utils.check_or_create_public_private_files(nonexistent_public_key, None, None)
        
        self.assertIn("not found", str(context.exception))

    def test_check_or_create_public_private_files_missing_private_key_error(self):
        """Test check_or_create_public_private_files raises error when private key file missing."""
        # Arrange
        nonexistent_private_key = os.path.join(self.temp_dir, "nonexistent")
        
        # Act & Assert
        with self.assertRaises(azclierror.FileOperationError) as context:
            file_utils.check_or_create_public_private_files(
                self.mock_public_key, nonexistent_private_key, None)
        
        self.assertIn("not found", str(context.exception))

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
                file_utils.check_or_create_public_private_files(None, None, None, None)
            
            # Verify error message
            self.assertIn("Key generation error", str(context.exception))

    @mock.patch('azext_sftp.file_utils.Profile')
    @mock.patch('azext_sftp.file_utils._prepare_jwk_data')
    @mock.patch('azext_sftp.file_utils._write_cert_file')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_get_and_write_certificate_success(self, mock_get_principals, 
                                               mock_write_cert, mock_prepare_jwk, mock_profile):
        """Test get_and_write_certificate successfully generates certificate."""
        # Arrange
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        
        mock_profile_instance = mock.Mock()
        mock_profile.return_value = mock_profile_instance
        mock_profile_instance.get_msal_token.return_value = (None, "test_certificate_data")
        
        mock_prepare_jwk.return_value = {"test": "data"}
        mock_get_principals.return_value = ["testuser@domain.com"]
        
        # Set up the cert file path that the function will generate
        expected_cert_file = str(self.mock_public_key.removesuffix(".pub")) + "-aadcert.pub"
        mock_write_cert.return_value = expected_cert_file
        
        # Act
        result_cert_file, username = file_utils.get_and_write_certificate(
            cmd, self.mock_public_key, None, None)
        
        # Assert
        self.assertEqual(result_cert_file, expected_cert_file)
        self.assertEqual(username, "testuser@domain.com")
        mock_prepare_jwk.assert_called_once_with(self.mock_public_key)
        mock_write_cert.assert_called_once_with("test_certificate_data", expected_cert_file)

    @mock.patch('azure.cli.core._profile.Profile')
    def test_get_and_write_certificate_unsupported_cloud(self, mock_profile):
        """Test get_and_write_certificate raises error for unsupported cloud."""
        # Arrange
        cmd = mock.Mock()
        cmd.cli_ctx.cloud.name = "unsupportedcloud"
        
        # Act & Assert
        with self.assertRaises(azclierror.InvalidArgumentValueError) as context:
            file_utils.get_and_write_certificate(cmd, self.mock_public_key, None, None)
        
        self.assertIn("Unsupported cloud", str(context.exception))

    @mock.patch('azext_sftp.file_utils._get_modulus_exponent')
    @mock.patch('hashlib.sha256')
    @mock.patch('json.dumps')
    def test_prepare_jwk_data_creates_correct_structure(self, mock_dumps, mock_sha256, mock_get_mod_exp):
        """Test _prepare_jwk_data creates correct JWK structure."""
        # Arrange
        mock_get_mod_exp.return_value = ("test_modulus", "test_exponent")
        mock_hash = mock.Mock()
        mock_hash.hexdigest.return_value = "test_key_id"
        mock_sha256.return_value = mock_hash
        mock_dumps.return_value = "test_jwk_json"
        
        # Act
        result = file_utils._prepare_jwk_data(self.mock_public_key)
        
        # Assert
        self.assertEqual(result["token_type"], "ssh-cert")
        self.assertEqual(result["req_cnf"], "test_jwk_json")
        self.assertEqual(result["key_id"], "test_key_id")

    def test_write_cert_file_creates_certificate(self):
        """Test _write_cert_file creates certificate file with correct format."""
        # Arrange
        cert_contents = "test_certificate_data"
        cert_file = os.path.join(self.temp_dir, "test_cert.pub")
        
        # Act
        result = file_utils._write_cert_file(cert_contents, cert_file)
        
        # Assert
        self.assertEqual(result, cert_file)
        self.assertTrue(os.path.isfile(cert_file))
        
        with open(cert_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, f"ssh-rsa-cert-v01@openssh.com {cert_contents}")
        
    @mock.patch('azext_sftp.rsa_parser.RSAParser')
    def test_get_modulus_exponent_success(self, mock_parser_class):
        """Test _get_modulus_exponent successfully extracts modulus and exponent."""
        # Arrange
        mock_parser = mock.Mock()
        mock_parser.modulus = "test_modulus"
        mock_parser.exponent = "test_exponent"
        mock_parser_class.return_value = mock_parser
        
        # Act
        modulus, exponent = file_utils._get_modulus_exponent(self.mock_public_key)
        
        # Assert
        self.assertEqual(modulus, "test_modulus")
        self.assertEqual(exponent, "test_exponent")
        
        # Verify parser was called with file contents
        with open(self.mock_public_key, 'r') as f:
            expected_content = f.read()
        mock_parser.parse.assert_called_once_with(expected_content)

    def test_get_modulus_exponent_file_not_found(self):
        """Test _get_modulus_exponent handles missing file."""
        # Arrange
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.pub")
        
        # Act & Assert
        with self.assertRaises(azclierror.FileOperationError) as context:
            file_utils._get_modulus_exponent(nonexistent_file)
        
        self.assertIn("was not found", str(context.exception))

    @mock.patch('azext_sftp.rsa_parser.RSAParser')
    def test_get_modulus_exponent_parse_error(self, mock_parser_class):
        """Test _get_modulus_exponent handles parsing errors."""
        # Arrange
        mock_parser = mock.Mock()
        mock_parser.parse.side_effect = ValueError("Invalid key format")
        mock_parser_class.return_value = mock_parser
        
        # Act & Assert
        with self.assertRaises(azclierror.FileOperationError) as context:
            file_utils._get_modulus_exponent(self.mock_public_key)
        
        self.assertIn("Could not parse public key", str(context.exception))


if __name__ == '__main__':
    unittest.main()
