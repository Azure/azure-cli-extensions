# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os
from unittest import mock

from azext_sftp import sftp_utils


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

    def test_certificate_functions_exist(self):
        """Test that certificate functions exist and can be called."""
        # Simple test to ensure functions exist
        self.assertTrue(hasattr(sftp_utils, 'get_ssh_cert_principals'))
        
        # Note: get_certificate_start_and_end_times was removed as unnecessary validation


if __name__ == '__main__':
    unittest.main()
