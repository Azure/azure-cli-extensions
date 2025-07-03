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

    def test_make_dirs_for_file_creates_parent_directories(self):
        """Test make_dirs_for_file creates parent directories for a file path."""
        # Arrange
        test_file_path = os.path.join(self.temp_dir, "subdir1", "subdir2", "test_file.txt")
        
        # Act
        file_utils.make_dirs_for_file(test_file_path)
        
        # Assert
        parent_dir = os.path.dirname(test_file_path)
        self.assertTrue(os.path.isdir(parent_dir))

    def test_make_dirs_for_file_with_existing_directories(self):
        """Test make_dirs_for_file when directories already exist."""
        # Arrange
        existing_dir = os.path.join(self.temp_dir, "existing")
        os.makedirs(existing_dir)
        test_file_path = os.path.join(existing_dir, "test_file.txt")
        
        # Act & Assert - Should not raise an exception
        file_utils.make_dirs_for_file(test_file_path)
        self.assertTrue(os.path.isdir(existing_dir))

    def test_mkdir_p_creates_directory(self):
        """Test mkdir_p creates directory successfully."""
        # Arrange
        test_dir = os.path.join(self.temp_dir, "new_directory")
        
        # Act
        file_utils.mkdir_p(test_dir)
        
        # Assert
        self.assertTrue(os.path.isdir(test_dir))

    def test_mkdir_p_with_existing_directory(self):
        """Test mkdir_p with existing directory does not raise error."""
        # Arrange
        existing_dir = os.path.join(self.temp_dir, "existing")
        os.makedirs(existing_dir)
        
        # Act & Assert - Should not raise an exception
        file_utils.mkdir_p(existing_dir)
        self.assertTrue(os.path.isdir(existing_dir))

    @mock.patch('os.makedirs')
    def test_mkdir_p_handles_permission_error(self, mock_makedirs):
        """Test mkdir_p handles permission errors appropriately."""
        # Arrange
        mock_makedirs.side_effect = OSError("Permission denied")
        
        # Act & Assert
        with self.assertRaises(OSError):
            file_utils.mkdir_p("/non/existent/path")

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

    def test_delete_folder_removes_empty_directory(self):
        """Test delete_folder removes an empty directory."""
        # Arrange
        test_dir = os.path.join(self.temp_dir, "empty_dir")
        os.makedirs(test_dir)
        
        # Act
        file_utils.delete_folder(test_dir, "Test folder deletion")
        
        # Assert
        self.assertFalse(os.path.isdir(test_dir))

    def test_delete_folder_with_nonexistent_directory(self):
        """Test delete_folder with nonexistent directory does nothing."""
        # Arrange
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        
        # Act & Assert - Should not raise an exception
        file_utils.delete_folder(nonexistent_dir, "Test deletion message")

    @mock.patch('os.rmdir')
    def test_delete_folder_handles_removal_error_with_warning(self, mock_rmdir):
        """Test delete_folder handles removal errors with warning flag."""
        # Arrange
        test_dir = os.path.join(self.temp_dir, "test_dir")
        os.makedirs(test_dir)
        mock_rmdir.side_effect = OSError("Directory not empty")
        
        # Act & Assert - Should not raise exception when warning=True
        with mock.patch('azext_sftp.file_utils.logger') as mock_logger:
            file_utils.delete_folder(test_dir, "Test message", warning=True)
            mock_logger.warning.assert_called_once()

    def test_create_directory_creates_new_directory(self):
        """Test create_directory creates a new directory."""
        # Arrange
        new_dir = os.path.join(self.temp_dir, "new_created_dir")
        
        # Act
        file_utils.create_directory(new_dir, "Failed to create directory")
        
        # Assert
        self.assertTrue(os.path.isdir(new_dir))

    @mock.patch('os.makedirs')
    def test_create_directory_handles_creation_error(self, mock_makedirs):
        """Test create_directory handles creation errors."""
        # Arrange
        mock_makedirs.side_effect = OSError("Permission denied")
        
        # Act & Assert
        with self.assertRaises(azclierror.FileOperationError) as context:
            file_utils.create_directory("/invalid/path", "Test error message")
        
        self.assertIn("Test error message", str(context.exception))

    def test_write_to_file_creates_file_with_content(self):
        """Test write_to_file creates file with specified content."""
        # Arrange
        test_file = os.path.join(self.temp_dir, "test_write.txt")
        content = "Hello, SFTP world!"
        
        # Act
        file_utils.write_to_file(test_file, 'w', content, "Failed to write file")
        
        # Assert
        self.assertTrue(os.path.isfile(test_file))
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), content)

    def test_write_to_file_with_encoding(self):
        """Test write_to_file with specific encoding."""
        # Arrange
        test_file = os.path.join(self.temp_dir, "test_encoding.txt")
        content = "Unicode content: αβγδε"
        
        # Act
        file_utils.write_to_file(test_file, 'w', content, "Failed to write file", encoding='utf-8')
        
        # Assert
        with open(test_file, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), content)

    def test_write_to_file_append_mode(self):
        """Test write_to_file in append mode."""
        # Arrange
        test_file = os.path.join(self.temp_dir, "test_append.txt")
        initial_content = "Initial content\n"
        append_content = "Appended content"
        
        # Act
        file_utils.write_to_file(test_file, 'w', initial_content, "Failed to write file")
        file_utils.write_to_file(test_file, 'a', append_content, "Failed to append file")
        
        # Assert
        with open(test_file, 'r') as f:
            content = f.read()
            self.assertIn(initial_content.strip(), content)
            self.assertIn(append_content, content)

    @mock.patch('builtins.open')
    def test_write_to_file_handles_write_error(self, mock_open):
        """Test write_to_file handles write errors."""
        # Arrange
        mock_open.side_effect = OSError("Permission denied")
        
        # Act & Assert
        with self.assertRaises(azclierror.FileOperationError) as context:
            file_utils.write_to_file("/invalid/file.txt", 'w', "content", "Test error message")
        
        self.assertIn("Test error message", str(context.exception))

    def test_get_line_that_contains_finds_matching_line(self):
        """Test get_line_that_contains finds line containing substring."""
        # Arrange
        lines = [
            "This is the first line",
            "This line contains the target substring",
            "This is the third line"
        ]
        substring = "target"
        
        # Act
        result = file_utils.get_line_that_contains(substring, lines)
        
        # Assert
        self.assertEqual(result, "This line contains the target substring")

    def test_get_line_that_contains_no_match(self):
        """Test get_line_that_contains returns None when no match found."""
        # Arrange
        lines = [
            "This is the first line",
            "This is the second line",
            "This is the third line"
        ]
        substring = "nonexistent"
        
        # Act
        result = file_utils.get_line_that_contains(substring, lines)
        
        # Assert
        self.assertIsNone(result)

    def test_get_line_that_contains_empty_lines(self):
        """Test get_line_that_contains with empty lines list."""
        # Arrange
        lines = []
        substring = "target"
        
        # Act
        result = file_utils.get_line_that_contains(substring, lines)
        
        # Assert
        self.assertIsNone(result)

    def test_get_line_that_contains_case_sensitive(self):
        """Test get_line_that_contains is case sensitive."""
        # Arrange
        lines = ["This line contains TARGET", "This line contains target"]
        
        # Act
        result_upper = file_utils.get_line_that_contains("TARGET", lines)
        result_lower = file_utils.get_line_that_contains("target", lines)
        
        # Assert
        self.assertEqual(result_upper, "This line contains TARGET")
        self.assertEqual(result_lower, "This line contains target")

    def test_remove_invalid_characters_foldername_removes_invalid_chars(self):
        """Test remove_invalid_characters_foldername removes Windows invalid characters."""
        # Arrange
        folder_name_with_invalid = 'folder<name>with|invalid:chars*and?quotes"'
        
        # Act
        result = file_utils.remove_invalid_characters_foldername(folder_name_with_invalid)
        
        # Assert
        # Should remove < > | : * ? "
        expected = 'foldernamewithinvalidcharsandquotes'
        self.assertEqual(result, expected)

    def test_remove_invalid_characters_foldername_valid_name(self):
        """Test remove_invalid_characters_foldername with already valid name."""
        # Arrange
        valid_folder_name = "valid_folder-name.with_numbers123"
        
        # Act
        result = file_utils.remove_invalid_characters_foldername(valid_folder_name)
        
        # Assert
        self.assertEqual(result, valid_folder_name)

    def test_remove_invalid_characters_foldername_empty_string(self):
        """Test remove_invalid_characters_foldername with empty string."""
        # Arrange
        empty_name = ""
        
        # Act
        result = file_utils.remove_invalid_characters_foldername(empty_name)
        
        # Assert
        self.assertEqual(result, "")

    def test_remove_invalid_characters_foldername_only_invalid_chars(self):
        """Test remove_invalid_characters_foldername with only invalid characters."""
        # Arrange
        only_invalid = '<>|:*?"'
        
        # Act
        result = file_utils.remove_invalid_characters_foldername(only_invalid)
        
        # Assert
        self.assertEqual(result, "")


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
        
        # Create the expected files so they exist for the function
        with open(expected_public_key, 'w') as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ test@example.com")
        with open(expected_private_key, 'w') as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----")
        
        # Act
        public_key, private_key, delete_keys = file_utils.check_or_create_public_private_files(
            None, None, None)
        
        # Assert
        self.assertEqual(public_key, expected_public_key)
        self.assertEqual(private_key, expected_private_key)
        self.assertTrue(delete_keys)
        mock_create_keyfile.assert_called_once_with(expected_private_key, None)

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

    @mock.patch('azext_sftp.file_utils.Profile')
    @mock.patch('azext_sftp.file_utils._prepare_jwk_data')
    @mock.patch('azext_sftp.file_utils._write_cert_file')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    @mock.patch('oschmod.set_mode')
    def test_get_and_write_certificate_success(self, mock_set_mode, mock_get_principals, 
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
        expected_cert_file = str(self.mock_public_key) + "-aadcert.pub"
        mock_write_cert.return_value = expected_cert_file
        
        # Act
        result_cert_file, username = file_utils.get_and_write_certificate(
            cmd, self.mock_public_key, None, None)
        
        # Assert
        self.assertEqual(result_cert_file, expected_cert_file)
        self.assertEqual(username, "testuser@domain.com")
        mock_prepare_jwk.assert_called_once_with(self.mock_public_key)
        mock_write_cert.assert_called_once_with("test_certificate_data", expected_cert_file)
        mock_set_mode.assert_called_once_with(expected_cert_file, 0o600)

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
        with mock.patch('oschmod.set_mode') as mock_set_mode:
            result = file_utils._write_cert_file(cert_contents, cert_file)
        
        # Assert
        self.assertEqual(result, cert_file)
        self.assertTrue(os.path.isfile(cert_file))
        
        with open(cert_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, f"ssh-rsa-cert-v01@openssh.com {cert_contents}")
        
        mock_set_mode.assert_called_once_with(cert_file, 0o644)

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
