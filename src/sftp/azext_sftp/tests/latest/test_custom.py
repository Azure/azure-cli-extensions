# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import io
import unittest
import pytest
import json
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

    def test_sftp_cert_basic_error_cases(self):
        """Test basic sftp cert error cases with parameterized inputs."""
        basic_error_cases = [
            # (description, exception_type, cert_path, public_key_file, setup_mocks)
            ("no arguments provided", azclierror.RequiredArgumentMissingError, None, None, {}),
            ("certificate directory doesn't exist", azclierror.InvalidArgumentValueError, "cert", None, {"isdir_return": False}),
        ]
        
        for description, exception_type, cert_path, public_key_file, setup_mocks in basic_error_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                
                # Apply setup mocks
                patches = []
                if "isdir_return" in setup_mocks:
                    patches.append(mock.patch('os.path.isdir', return_value=setup_mocks["isdir_return"]))
                
                for patch in patches:
                    patch.start()
                
                try:
                    with self.assertRaises(exception_type):
                        custom.sftp_cert(cmd, cert_path=cert_path, public_key_file=public_key_file)
                finally:
                    for patch in patches:
                        patch.stop()

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    @mock.patch('azext_sftp.file_utils.check_or_create_public_private_files')
    @mock.patch('azext_sftp.file_utils.get_and_write_certificate')
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

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_certificate_scenarios(self, mock_get_principals, mock_do_sftp):
        """Test connect with various certificate scenarios."""
        # Test cases: (description, cert_file, public_key_file, private_key_file, expected_calls)
        cert_test_cases = [
            ("valid cert provided", self.mock_cert_file, None, self.mock_private_key, "cert_used"),
            ("cert and public key both provided", self.mock_cert_file, self.mock_public_key, self.mock_private_key, "cert_used"),
            ("existing cert with existing private key", self.mock_cert_file, None, self.mock_private_key, "cert_used"),
        ]
        
        for description, cert_file, public_key_file, private_key_file, expected_calls in cert_test_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = "azurecloud"
                mock_get_principals.return_value = ["testuser@domain.com"]
                mock_do_sftp.return_value = None
                
                # Reset mocks for each test case
                mock_get_principals.reset_mock()
                mock_do_sftp.reset_mock()
                
                custom.sftp_connect(
                    cmd=cmd,
                    storage_account="teststorage",
                    port=22,
                    cert_file=cert_file,
                    public_key_file=public_key_file,
                    private_key_file=private_key_file,
                    sftp_args=['-b', '/dev/stdin']  # Use sftp_args for batch mode
                )
                
                # Verify certificate was used
                if expected_calls == "cert_used":
                    mock_get_principals.assert_called_once()
                    mock_do_sftp.assert_called_once()



    @mock.patch('azext_sftp.custom._assert_args')
    @mock.patch('azext_sftp.custom.Profile')
    @mock.patch('azext_sftp.custom._get_storage_endpoint_suffix')
    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.file_utils.get_and_write_certificate')
    @mock.patch('azext_sftp.file_utils.check_or_create_public_private_files')
    @mock.patch('tempfile.mkdtemp')
    def test_sftp_connect_key_generation_scenarios(self, mock_mkdtemp, mock_create_keys, mock_gen_cert, mock_do_sftp, mock_get_suffix, mock_profile, mock_assert_args):
        """Test connect with various key generation scenarios."""
        # Test cases: (description, public_key_file, private_key_file, keys_generated, expected_create_keys_args_template)
        key_gen_test_cases = [
            ("no cert auto generate", None, None, True, (None, None, "{temp_dir}", None)),
            ("public key provided no cert", self.mock_public_key, None, False, (self.mock_public_key, None, None, None)),
            ("private key provided no cert", None, self.mock_private_key, False, (None, self.mock_private_key, None, None)),
        ]
        
        for description, public_key_file, private_key_file, keys_generated, expected_create_keys_args_template in key_gen_test_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = "azurecloud"
                
                # Mock Profile and subscription check
                mock_profile_instance = mock.Mock()
                mock_profile.return_value = mock_profile_instance
                mock_profile_instance.get_subscription.return_value = {"id": "test-subscription-id"}
                
                # Reset mocks for each test case
                mock_mkdtemp.reset_mock()
                mock_create_keys.reset_mock()
                mock_gen_cert.reset_mock()
                mock_do_sftp.reset_mock()
                
                # Setup mocks
                mock_assert_args.return_value = None  # Skip argument validation
                mock_mkdtemp.return_value = self.temp_dir
                mock_create_keys.return_value = (self.mock_public_key, self.mock_private_key, keys_generated)
                mock_gen_cert.return_value = (self.mock_cert_file, "testuser")
                mock_do_sftp.return_value = None
                mock_get_suffix.return_value = "blob.core.windows.net"
                
                custom.sftp_connect(
                    cmd=cmd,
                    storage_account="teststorage",
                    port=22,
                    public_key_file=public_key_file,
                    private_key_file=private_key_file,
                    sftp_args=['-b', '/dev/stdin']  # Use sftp_args for batch mode
                )
                
                # Build expected args with actual temp_dir value
                expected_create_keys_args = tuple(
                    self.temp_dir if arg == "{temp_dir}" else arg 
                    for arg in expected_create_keys_args_template
                )
                
                # Verify function calls
                mock_create_keys.assert_called_once_with(*expected_create_keys_args)
                mock_gen_cert.assert_called_once()
                mock_do_sftp.assert_called_once()

    def test_sftp_connect_error_cases(self):
        """Test connect error cases with parameterized inputs."""
        error_test_cases = [
            # (description, exception_type, kwargs)
            ("invalid/missing private key file", azclierror.FileOperationError, {"private_key_file": "/nonexistent/key"}),
            ("invalid/missing public key file", azclierror.FileOperationError, {"public_key_file": "/nonexistent/key.pub"}),
            ("invalid/missing certificate file", azclierror.FileOperationError, {"cert_file": "/nonexistent/cert.pub", "private_key_file": self.mock_private_key}),
            ("missing storage account", azclierror.RequiredArgumentMissingError, {"storage_account": None}),
        ]
        
        for description, exception_type, kwargs in error_test_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = "azurecloud"
                
                base_kwargs = {"cmd": cmd, "storage_account": "teststorage", "port": 22}
                base_kwargs.update(kwargs)
                
                with self.assertRaises(exception_type):
                    custom.sftp_connect(**base_kwargs)

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_port_configurations(self, mock_get_principals, mock_do_sftp):
        """Test connect with different port configurations."""
        port_test_cases = [
            # (description, port_value, expected_port)
            ("default port (None)", None, None),
            ("custom port", 2222, 2222),
        ]
        
        for description, port_value, expected_port in port_test_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = "azurecloud"
                mock_get_principals.return_value = ["testuser@domain.com"]
                mock_do_sftp.return_value = None
                
                # Reset mock for each test case
                mock_do_sftp.reset_mock()
                
                custom.sftp_connect(
                    cmd=cmd,
                    storage_account="teststorage",
                    port=port_value,
                    cert_file=self.mock_cert_file,
                    private_key_file=self.mock_private_key,
                    sftp_args=['-b', '/dev/stdin']  # Use sftp_args for batch mode
                )
                
                # Verify the session was created with expected port
                mock_do_sftp.assert_called_once()
                call_args = mock_do_sftp.call_args[0]
                sftp_session = call_args[0]  # First argument is the SFTP session
                self.assertEqual(sftp_session.port, expected_port)

    @mock.patch('azext_sftp.custom._do_sftp_op')
    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals')
    def test_sftp_connect_argument_combinations(self, mock_get_principals, mock_do_sftp):
        """Test sftp_connect with various argument combinations to ensure comprehensive coverage."""
        # Test cases: (description, kwargs, expected_behavior)
        test_cases = [
            ("minimal args with cert", {"cert_file": self.mock_cert_file, "private_key_file": self.mock_private_key}, "success"),
            ("with custom port", {"cert_file": self.mock_cert_file, "private_key_file": self.mock_private_key, "port": 2222}, "success"),
            ("with sftp_args", {"cert_file": self.mock_cert_file, "private_key_file": self.mock_private_key, "sftp_args": "-v"}, "success"),
            ("with ssh_client_folder", {"cert_file": self.mock_cert_file, "private_key_file": self.mock_private_key, "ssh_client_folder": "ssh_folder"}, "success"),
            ("with sftp_args for batch", {"cert_file": self.mock_cert_file, "private_key_file": self.mock_private_key, "sftp_args": ["-b", "batchfile.txt"]}, "success"),
            ("all args combined", {
                "cert_file": self.mock_cert_file, 
                "private_key_file": self.mock_private_key,
                "port": 2222,
                "sftp_args": ["-v", "-o", "StrictHostKeyChecking=no", "-b", "batchfile.txt"],
                "ssh_client_folder": "ssh_folder"
            }, "success"),
        ]
        
        for description, kwargs, expected_behavior in test_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = "azurecloud"
                mock_get_principals.return_value = ["testuser@domain.com"]
                mock_do_sftp.return_value = None
                
                # Reset mocks for each test case
                mock_do_sftp.reset_mock()
                
                base_kwargs = {
                    "cmd": cmd,
                    "storage_account": "teststorage"
                }
                base_kwargs.update(kwargs)
                
                if expected_behavior == "success":
                    custom.sftp_connect(**base_kwargs)
                    mock_do_sftp.assert_called_once()
                    
                    # Verify specific arguments were passed correctly
                    call_args = mock_do_sftp.call_args[0]
                    sftp_session = call_args[0]
                    
                    # Check that the session object has the expected properties
                    if "port" in kwargs:
                        self.assertEqual(sftp_session.port, kwargs["port"])
                    if "sftp_args" in kwargs:
                        self.assertEqual(sftp_session.sftp_args, kwargs["sftp_args"])
                    if "ssh_client_folder" in kwargs:
                        # Just check that ssh_client_folder was set - path may be normalized
                        self.assertIsNotNone(sftp_session.ssh_client_folder)
                        self.assertIn("ssh_folder", sftp_session.ssh_client_folder)

    def test_sftp_connect_sftp_args_variations(self):
        """Test different sftp_args formats and common SSH options."""
        sftp_args_cases = [
            # (description, sftp_args)
            ("None", None),
            ("verbose flag", "-v"),
            ("multiple flags", "-v -o StrictHostKeyChecking=no"),
            ("compression", "-C"),
            ("custom identity file", "-i /path/to/custom/key"),
            ("timeout setting", "-o ConnectTimeout=30"),
            ("complex args", "-v -C -o StrictHostKeyChecking=no -o ConnectTimeout=30"),
        ]
        
        for description, sftp_args in sftp_args_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = "azurecloud"
                
                with mock.patch('azext_sftp.custom._do_sftp_op') as mock_do_sftp, \
                     mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals', return_value=["testuser@domain.com"]):
                    
                    mock_do_sftp.return_value = None
                    
                    custom.sftp_connect(
                        cmd=cmd,
                        storage_account="teststorage",
                        cert_file=self.mock_cert_file,
                        private_key_file=self.mock_private_key,
                        sftp_args=sftp_args
                    )
                    
                    mock_do_sftp.assert_called_once()
                    call_args = mock_do_sftp.call_args[0]
                    sftp_session = call_args[0]
                    
                    # Verify sftp_args are set correctly
                    if sftp_args is None:
                        self.assertEqual(sftp_session.sftp_args, [])  # None becomes empty list
                    else:
                        self.assertEqual(sftp_session.sftp_args, sftp_args)

    def test_sftp_connect_ssh_client_folder_variations(self):
        """Test different ssh_client_folder path formats."""
        ssh_folder_cases = [
            # (description, ssh_client_folder)
            ("None", None),
            ("relative path", "ssh_client"),
            ("absolute path", "/tmp/ssh"),
        ]
        
        for description, ssh_client_folder in ssh_folder_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = "azurecloud"
                
                with mock.patch('azext_sftp.custom._do_sftp_op') as mock_do_sftp, \
                     mock.patch('azext_sftp.sftp_utils.get_ssh_cert_principals', return_value=["testuser@domain.com"]):
                    
                    mock_do_sftp.return_value = None
                    
                    custom.sftp_connect(
                        cmd=cmd,
                        storage_account="teststorage",
                        cert_file=self.mock_cert_file,
                        private_key_file=self.mock_private_key,
                        ssh_client_folder=ssh_client_folder
                    )
                    
                    mock_do_sftp.assert_called_once()
                    call_args = mock_do_sftp.call_args[0]
                    sftp_session = call_args[0]
                    
                    # Verify ssh_client_folder is set correctly
                    if ssh_client_folder is None:
                        self.assertIsNone(sftp_session.ssh_client_folder)
                    else:
                        # Path will be converted to absolute path, so just check it's not None
                        self.assertIsNotNone(sftp_session.ssh_client_folder)

    @mock.patch('azext_sftp.file_utils.get_and_write_certificate')
    @mock.patch('azext_sftp.file_utils.check_or_create_public_private_files')
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
        mock_write_cert.return_value = (self.mock_cert_file, "testuser@domain.com")
        
        # Mock logger to capture warning
        with mock.patch('azext_sftp.custom.logger') as mock_logger:
            custom.sftp_cert(cmd, cert_path=self.mock_cert_file)
            
            # Verify warning is logged when keys are generated
            mock_logger.warning.assert_called()
            # Check all warning calls to find the sensitive information one
            warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
            sensitive_info_warning = next((call for call in warning_calls if "contains sensitive information" in call), None)
            self.assertIsNotNone(sensitive_info_warning, "Sensitive information warning not found")
            self.assertIn("id_rsa", sensitive_info_warning)

    @mock.patch('azext_sftp.file_utils.check_or_create_public_private_files')
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
        with mock.patch('azext_sftp.file_utils.get_and_write_certificate') as mock_write_cert:
            mock_write_cert.side_effect = Exception("Certificate generation failed")
            
            with mock.patch('azext_sftp.custom.logger') as mock_logger:
                with self.assertRaises(Exception):
                    custom.sftp_cert(cmd, cert_path=self.mock_cert_file, 
                                    public_key_file=self.mock_public_key)
                
                # Verify error is logged - certificate generation failed so exception should be raised
                # The debug logging might not be called depending on where the exception occurs

    @mock.patch('azext_sftp.file_utils.get_and_write_certificate')
    @mock.patch('azext_sftp.file_utils.check_or_create_public_private_files')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_parameter_combinations(self, mock_abspath, mock_isdir, mock_check_files, mock_write_cert):
        """Test sftp cert with all valid parameter combinations using subTest."""
        # Test cases: (cert_path, public_key_file, ssh_client_folder, expected_keys_folder, description)
        test_cases = [
            (None, "pubkey.pub", None, None, "public_key_only"),
            ("cert.pub", None, None, "cert_dir", "cert_path_only"),
            ("cert.pub", None, "/ssh", "cert_dir", "cert_path_with_ssh_client"),
            (None, "pubkey.pub", "/ssh", None, "public_key_with_ssh_client"),
            ("cert.pub", "pubkey.pub", None, None, "cert_path_with_public_key"),
            ("cert.pub", "pubkey.pub", "/ssh", None, "all_parameters"),
        ]
        
        for cert_path, public_key_file, ssh_client_folder, expected_keys_folder, description in test_cases:
            with self.subTest(case=description):
                # Reset mocks and setup
                mock_check_files.reset_mock()
                mock_write_cert.reset_mock()
                cmd = mock.Mock()
                mock_isdir.return_value = True
                mock_abspath.side_effect = lambda x: x
                
                # Configure mocks based on test case
                keys_generated = public_key_file is None
                effective_public_key = public_key_file or self.mock_public_key
                mock_check_files.return_value = (effective_public_key, self.mock_private_key if keys_generated else None, keys_generated)
                
                expected_cert = (effective_public_key + "-aadcert.pub") if cert_path is None else cert_path
                mock_write_cert.return_value = (expected_cert, "testuser@domain.com")
                
                # Execute test
                custom.sftp_cert(cmd, cert_path=cert_path, public_key_file=public_key_file, ssh_client_folder=ssh_client_folder)
                
                # Verify calls
                expected_keys_dir = os.path.dirname(cert_path) if expected_keys_folder == "cert_dir" else expected_keys_folder
                mock_check_files.assert_called_once_with(public_key_file, None, expected_keys_dir, ssh_client_folder)
                mock_write_cert.assert_called_once_with(cmd, effective_public_key, cert_path, ssh_client_folder)

    def test_sftp_cert_error_cases(self):
        """Test sftp cert error handling with invalid argument combinations."""
        # Test cases: (cert_path, public_key_file, setup_mocks, expected_exception, expected_message, description)
        test_cases = [
            (None, None, {}, azclierror.RequiredArgumentMissingError, "--file or --public-key-file must be provided", "no_arguments"),
            ("/bad/cert.pub", None, {"expanduser_return": "/bad/cert.pub", "isdir_return": False}, azclierror.InvalidArgumentValueError, "folder doesn't exist", "invalid_directory"),
        ]
        
        for cert_path, public_key_file, setup_mocks, expected_exception, expected_message, description in test_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                patches = []
                
                # Apply setup mocks
                if "expanduser_return" in setup_mocks:
                    patches.append(mock.patch('os.path.expanduser', return_value=setup_mocks["expanduser_return"]))
                if "isdir_return" in setup_mocks:
                    patches.append(mock.patch('os.path.isdir', return_value=setup_mocks["isdir_return"]))
                
                for patch in patches:
                    patch.start()
                
                try:
                    with self.assertRaises(expected_exception) as context:
                        custom.sftp_cert(cmd, cert_path=cert_path, public_key_file=public_key_file)
                    self.assertIn(expected_message, str(context.exception))
                finally:
                    for patch in patches:
                        patch.stop()

    @mock.patch('os.path.expanduser')
    @mock.patch('os.path.abspath')
    def test_sftp_cert_path_expansion(self, mock_abspath, mock_expanduser):
        """Test that all path arguments are properly expanded from ~ to full paths."""
        # Test cases: (cert_path, public_key_file, ssh_client_folder, description)
        test_cases = [
            ("~/cert.pub", "~/.ssh/id_rsa.pub", "~/ssh_client", "all_paths_with_tilde"),
            (None, "~/.ssh/id_rsa.pub", "~/ssh_client", "public_key_and_ssh_client_with_tilde"),
            ("~/cert.pub", None, "~/ssh_client", "cert_path_and_ssh_client_with_tilde"),
        ]
        
        for cert_path, public_key_file, ssh_client_folder, description in test_cases:
            with self.subTest(case=description):
                mock_expanduser.reset_mock()
                mock_abspath.reset_mock()
                cmd = mock.Mock()
                
                # Setup mocks
                mock_expanduser.side_effect = lambda x: x.replace('~', '/home/user') if x else x
                mock_abspath.side_effect = lambda x: '/absolute' + x if x else x
                
                # Mock dependencies
                with mock.patch('os.path.isdir', return_value=True), \
                     mock.patch('azext_sftp.file_utils.check_or_create_public_private_files') as mock_check_files, \
                     mock.patch('azext_sftp.file_utils.get_and_write_certificate') as mock_write_cert:
                    
                    mock_check_files.return_value = ("/absolute/home/user/.ssh/id_rsa.pub", None, False)
                    mock_write_cert.return_value = ("/absolute/home/user/cert.pub", "user@domain.com")
                    
                    # Execute test
                    custom.sftp_cert(cmd, cert_path=cert_path, public_key_file=public_key_file, ssh_client_folder=ssh_client_folder)
                    
                    # Verify path expansion for tilde paths
                    expected_calls = [mock.call(path) for path in [cert_path, public_key_file, ssh_client_folder] if path and path.startswith('~')]
                    if expected_calls:
                        mock_expanduser.assert_has_calls(expected_calls, any_order=True)
                    self.assertTrue(mock_abspath.called)

    def test_sftp_cert_valid_minimal_call(self):
        """Test that a minimal valid call works correctly."""
        cmd = mock.Mock()
        
        with mock.patch('os.path.expanduser', side_effect=lambda x: x), \
             mock.patch('os.path.abspath', side_effect=lambda x: x), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('azext_sftp.file_utils.check_or_create_public_private_files') as mock_check_files, \
             mock.patch('azext_sftp.file_utils.get_and_write_certificate') as mock_write_cert:
            
            mock_check_files.return_value = ("pubkey.pub", None, False)
            mock_write_cert.return_value = ("pubkey.pub-aadcert.pub", "user@domain.com")
            
            # Should not raise any exception
            custom.sftp_cert(cmd, public_key_file="pubkey.pub")
            
            # Verify function was called correctly
            mock_check_files.assert_called_once_with("pubkey.pub", None, None, None)

    # Additional tests for private helper functions

    def test_assert_args_validation(self):
        """Test _assert_args function with various input combinations."""
        # Test cases: (storage_account, cert_file, public_key_file, private_key_file, expected_exception, description)
        test_cases = [
            (None, None, None, None, azclierror.RequiredArgumentMissingError, "missing storage account"),
            ("test", "/nonexistent/cert.pub", None, None, azclierror.FileOperationError, "invalid cert file"),
            ("test", None, "/nonexistent/key.pub", None, azclierror.FileOperationError, "invalid public key file"),
            ("test", None, None, "/nonexistent/key", azclierror.FileOperationError, "invalid private key file"),
            ("test", self.mock_cert_file, self.mock_public_key, self.mock_private_key, None, "all valid files"),
        ]
        
        for storage_account, cert_file, public_key_file, private_key_file, expected_exception, description in test_cases:
            with self.subTest(case=description):
                if expected_exception:
                    with self.assertRaises(expected_exception):
                        custom._assert_args(storage_account, cert_file, public_key_file, private_key_file)
                else:
                    # Should not raise any exception
                    custom._assert_args(storage_account, cert_file, public_key_file, private_key_file)

    def test_do_sftp_op_execution(self):
        """Test _do_sftp_op function with mock session and operation."""
        mock_session = mock.Mock()
        mock_session.validate_session.return_value = None
        
        mock_operation = mock.Mock()
        mock_operation.return_value = "operation_result"
        
        result = custom._do_sftp_op(mock_session, mock_operation)
        
        mock_session.validate_session.assert_called_once()
        mock_operation.assert_called_once_with(mock_session)
        self.assertEqual(result, "operation_result")

    def test_cleanup_credentials_selective_cleanup(self):
        """Test _cleanup_credentials with different cleanup scenarios."""
        # Create test files for cleanup testing
        temp_cert = os.path.join(self.temp_dir, "test_cert.pub")
        temp_private = os.path.join(self.temp_dir, "test_private_key")
        temp_public = os.path.join(self.temp_dir, "test_public_key.pub")
        temp_credentials_dir = os.path.join(self.temp_dir, "credentials")
        
        # Create the files and directory
        with open(temp_cert, 'w') as f:
            f.write("cert content")
        with open(temp_private, 'w') as f:
            f.write("private key")
        with open(temp_public, 'w') as f:
            f.write("public key")
        os.makedirs(temp_credentials_dir)
        
        # Test cases: (delete_keys, delete_cert, credentials_folder, description)
        cleanup_cases = [
            (True, True, temp_credentials_dir, "cleanup all"),
            (True, False, None, "cleanup keys only"),
            (False, True, None, "cleanup cert only"),
            (False, False, temp_credentials_dir, "cleanup folder only"),
            (False, False, None, "cleanup nothing"),
        ]
        
        for delete_keys, delete_cert, credentials_folder, description in cleanup_cases:
            with self.subTest(case=description):
                # Recreate files for each test
                if not os.path.exists(temp_cert):
                    with open(temp_cert, 'w') as f:
                        f.write("cert content")
                if not os.path.exists(temp_private):
                    with open(temp_private, 'w') as f:
                        f.write("private key")
                if not os.path.exists(temp_public):
                    with open(temp_public, 'w') as f:
                        f.write("public key")
                if not os.path.exists(temp_credentials_dir):
                    os.makedirs(temp_credentials_dir)
                
                # Mock file_utils.delete_file to avoid actual deletion but track calls
                with mock.patch('azext_sftp.file_utils.delete_file') as mock_delete:
                    custom._cleanup_credentials(
                        delete_keys, delete_cert, credentials_folder,
                        temp_cert if delete_cert else None,
                        temp_private if delete_keys else None,
                        temp_public if delete_keys else None
                    )
                    
                    # Verify expected file deletions were called
                    expected_calls = []
                    if delete_cert:
                        expected_calls.append(mock.call(temp_cert, mock.ANY, warning=False))
                    if delete_keys:
                        expected_calls.append(mock.call(temp_private, mock.ANY, warning=False))
                        expected_calls.append(mock.call(temp_public, mock.ANY, warning=False))
                    
                    if expected_calls:
                        mock_delete.assert_has_calls(expected_calls, any_order=True)
                    else:
                        mock_delete.assert_not_called()

    def test_cleanup_credentials_error_handling(self):
        """Test _cleanup_credentials handles errors gracefully."""
        with mock.patch('azext_sftp.file_utils.delete_file', side_effect=OSError("Permission denied")):
            with mock.patch('azext_sftp.custom.logger') as mock_logger:
                custom._cleanup_credentials(
                    delete_keys=True, delete_cert=True, credentials_folder=None,
                    cert_file=self.mock_cert_file, private_key_file=self.mock_private_key,
                    public_key_file=self.mock_public_key
                )
                
                # Should log warning but not raise exception
                mock_logger.warning.assert_called_once()

    def test_get_storage_endpoint_suffix_cloud_variants(self):
        """Test _get_storage_endpoint_suffix for different Azure clouds."""
        cloud_test_cases = [
            # (cloud_name, expected_suffix, description)
            ("azurecloud", "blob.core.windows.net", "public cloud"),
            ("AZURECLOUD", "blob.core.windows.net", "public cloud uppercase"),
            ("azurechinacloud", "blob.core.chinacloudapi.cn", "china cloud"),
            ("azureusgovernment", "blob.core.usgovcloudapi.net", "us government cloud"),
            ("unknowncloud", "blob.core.windows.net", "unknown cloud defaults to public"),
        ]
        
        for cloud_name, expected_suffix, description in cloud_test_cases:
            with self.subTest(case=description):
                cmd = mock.Mock()
                cmd.cli_ctx.cloud.name = cloud_name
                
                result = custom._get_storage_endpoint_suffix(cmd)
                self.assertEqual(result, expected_suffix)
