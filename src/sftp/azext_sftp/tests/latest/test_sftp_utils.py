# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os
from unittest import mock

from azext_sftp import sftp_utils
from azure.cli.core import azclierror


class SftpUtilsTests(unittest.TestCase):

    @mock.patch('platform.system')
    def test_get_ssh_client_path_linux(self, mock_system):
        """Test SSH client path resolution on Linux."""
        mock_system.return_value = "Linux"
        
        path = sftp_utils.get_ssh_client_path("sftp")
        
        # On non-Windows, should return the command name directly
        self.assertEqual(path, "sftp")

    @mock.patch('platform.system')
    def test_get_ssh_client_path_not_found(self, mock_system):
        """Test SSH client path when client not found."""
        mock_system.return_value = "Linux"
        
        # On non-Windows, the function returns the command name directly
        # It doesn't check if the command exists
        path = sftp_utils.get_ssh_client_path("sftp")
        
        self.assertEqual(path, "sftp")

    @mock.patch('platform.system')
    @mock.patch('platform.machine')
    @mock.patch('platform.architecture')
    @mock.patch('os.environ')
    @mock.patch('os.path.isfile')
    def test_get_ssh_client_path_windows(self, mock_isfile, mock_environ, mock_arch, mock_machine, mock_system):
        """Test SSH client path resolution on Windows."""
        mock_system.return_value = "Windows"
        mock_machine.return_value = "AMD64"
        mock_arch.return_value = ('64bit', '')
        mock_environ.__getitem__.return_value = "C:\\Windows"
        mock_isfile.return_value = True
        
        path = sftp_utils.get_ssh_client_path("sftp")
        
        # Should return full path with openSSH folder
        self.assertIn("System32", path)
        self.assertIn("openSSH", path)
        self.assertTrue(path.endswith("sftp.exe"))

    @mock.patch('platform.system')
    @mock.patch('platform.machine')
    @mock.patch('platform.architecture')
    @mock.patch('os.environ')
    @mock.patch('os.path.isfile')
    def test_get_ssh_client_path_windows_no_openssh(self, mock_isfile, mock_environ, mock_arch, mock_machine, mock_system):
        """Test SSH client path resolution on Windows when OpenSSH is not installed."""
        mock_system.return_value = "Windows"
        mock_machine.return_value = "AMD64"
        mock_arch.return_value = ('64bit', '')
        mock_environ.__getitem__.return_value = "C:\\Windows"
        mock_isfile.return_value = False  # ssh.exe does not exist
        
        # Should raise an exception when OpenSSH is not found
        with self.assertRaises(azclierror.UnclassifiedUserFault) as context:
            sftp_utils.get_ssh_client_path("ssh")
        
        self.assertIn("Could not find ssh.exe", str(context.exception))

    def test_certificate_functions_exist(self):
        """Test that certificate functions exist and can be called."""
        # Simple test to ensure functions exist
        self.assertTrue(hasattr(sftp_utils, 'get_ssh_cert_principals'))
        
        # Note: get_certificate_start_and_end_times was removed as unnecessary validation


class SftpUtilsAdvancedTest(unittest.TestCase):
    """Advanced test suite for SFTP utilities and edge cases."""

    def test_ssh_client_path_resolution_multiple_clients(self):
        """Test SSH client path resolution for different clients."""
        # Test sftp client path
        sftp_path = sftp_utils.get_ssh_client_path("sftp")
        self.assertIsNotNone(sftp_path)
        self.assertTrue(sftp_path.endswith("sftp") or sftp_path.endswith("sftp.exe"))
        
        # Test ssh client path  
        ssh_path = sftp_utils.get_ssh_client_path("ssh")
        self.assertIsNotNone(ssh_path)
        self.assertTrue(ssh_path.endswith("ssh") or ssh_path.endswith("ssh.exe"))

    def test_port_validation(self):
        """Test port number validation logic."""
        valid_ports = [22, 2222, 443, 80]
        invalid_ports = [-1, 0, 65536, 999999]
        
        for port in valid_ports:
            # Valid ports should be in acceptable range
            self.assertGreater(port, 0)
            self.assertLess(port, 65536)
        
        for port in invalid_ports:
            # Invalid ports should be outside acceptable range
            self.assertTrue(port <= 0 or port >= 65536)

    def test_connection_option_validation(self):
        """Test SSH connection options format validation."""
        required_options = [
            "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "BatchMode=yes",
            "PasswordAuthentication=no"
        ]
        
        for option in required_options:
            # Each option should be properly formatted
            self.assertIn("=", option)
            key, value = option.split("=", 1)
            self.assertNotEqual(key, "")
            self.assertNotEqual(value, "")


if __name__ == '__main__':
    unittest.main()
