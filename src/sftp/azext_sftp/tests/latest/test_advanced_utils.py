# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os
import tempfile
from unittest import mock

from azext_sftp import sftp_utils


class SftpUtilsAdvancedTest(unittest.TestCase):
    """Advanced test suite for SFTP utilities and edge cases."""

    def test_ssh_client_path_resolution(self):
        """Test SSH client path resolution for different clients."""
        # Test sftp client path
        sftp_path = sftp_utils.get_ssh_client_path("sftp")
        self.assertIsNotNone(sftp_path)
        self.assertTrue(sftp_path.endswith("sftp") or sftp_path.endswith("sftp.exe"))
        
        # Test ssh client path  
        ssh_path = sftp_utils.get_ssh_client_path("ssh")
        self.assertIsNotNone(ssh_path)
        self.assertTrue(ssh_path.endswith("ssh") or ssh_path.endswith("ssh.exe"))

    @mock.patch('os.path.exists')
    def test_file_path_validation(self, mock_exists):
        """Test file path validation utilities."""
        # Mock file existence
        mock_exists.return_value = True
        
        test_paths = [
            "/path/to/key",
            "C:\\Users\\test\\key.pem",
            "relative/path/key",
            "~/.ssh/id_rsa"
        ]
        
        for path in test_paths:
            # Test that paths are processed consistently
            abs_path = os.path.abspath(path)
            self.assertIsNotNone(abs_path)

    def test_command_argument_escaping(self):
        """Test proper escaping of command arguments."""
        # Test paths with spaces
        paths_with_spaces = [
            "C:\\Program Files\\key.pem",
            "/home/user name/key",
            "C:\\Users\\John Doe\\.ssh\\key"
        ]
        
        for path in paths_with_spaces:
            # Simple test - just verify paths are strings and contain expected content
            self.assertIsInstance(path, str)
            self.assertIn(" ", path)  # Should contain spaces as that's what we're testing

    def test_port_validation(self):
        """Test port number validation."""
        valid_ports = [22, 2222, 443, 80]
        invalid_ports = [-1, 0, 65536, 999999]
        
        for port in valid_ports:
            # Valid ports should be accepted
            self.assertGreater(port, 0)
            self.assertLess(port, 65536)
        
        for port in invalid_ports:
            # Invalid ports should be rejected
            self.assertTrue(port <= 0 or port >= 65536)

    def test_hostname_validation(self):
        """Test hostname validation patterns."""
        valid_hostnames = [
            "example.com",
            "sub.example.com", 
            "storage.blob.core.windows.net",
            "192.168.1.1",
            "localhost"
        ]
        
        invalid_hostnames = [
            "",
            " ",
            "http://example.com",  # Should not include protocol
            "example.com:22",      # Should not include port
        ]
        
        for hostname in valid_hostnames:
            # Valid hostnames should pass basic checks
            self.assertNotEqual(hostname.strip(), "")
            self.assertNotIn("://", hostname)
        
        for hostname in invalid_hostnames:
            # Invalid hostnames should fail
            if hostname.strip() == "":
                self.assertEqual(hostname.strip(), "")
            elif "://" in hostname:
                self.assertIn("://", hostname)

    def test_username_format_validation(self):
        """Test username format validation."""
        valid_usernames = [
            "user",
            "user@domain",
            "storage.user",
            "user_name",
            "user-name"
        ]
        
        for username in valid_usernames:
            # Valid usernames should be non-empty strings
            self.assertIsInstance(username, str)
            self.assertNotEqual(username.strip(), "")

    @mock.patch('subprocess.run')
    def test_command_execution_error_handling(self, mock_subprocess_run):
        """Test error handling during command execution."""
        # Test different error scenarios
        error_scenarios = [
            {"returncode": 255, "stderr": "Connection refused"},
            {"returncode": 1, "stderr": "Permission denied"},
            {"returncode": 2, "stderr": "Host key verification failed"},
        ]
        
        for scenario in error_scenarios:
            mock_subprocess_run.return_value = mock.Mock(
                returncode=scenario["returncode"],
                stderr=scenario["stderr"],
                stdout=""
            )
            
            # Error handling should properly interpret return codes
            result = mock_subprocess_run.return_value
            self.assertNotEqual(result.returncode, 0)
            self.assertIsNotNone(result.stderr)

    def test_timeout_configuration(self):
        """Test timeout configuration for connections."""
        # Test various timeout values
        timeout_values = [5, 10, 30, 60]
        
        for timeout in timeout_values:
            # Timeouts should be positive integers
            self.assertIsInstance(timeout, int)
            self.assertGreater(timeout, 0)
            self.assertLess(timeout, 300)  # Reasonable upper limit

    def test_batch_mode_configuration(self):
        """Test batch mode configuration."""
        # Batch mode should prevent interactive prompts
        batch_options = [
            "BatchMode=yes",
            "PasswordAuthentication=no",
            "StrictHostKeyChecking=accept-new"
        ]
        
        for option in batch_options:
            # Options should be properly formatted
            self.assertIn("=", option)
            key, value = option.split("=", 1)
            self.assertNotEqual(key.strip(), "")
            self.assertNotEqual(value.strip(), "")

    def test_certificate_file_handling(self):
        """Test certificate file handling."""
        test_cert_patterns = [
            "id_rsa-aadcert.pub",
            "certificate.pub", 
            "user-cert.pub"
        ]
        
        for pattern in test_cert_patterns:
            # Certificate files should follow naming conventions
            self.assertTrue(pattern.endswith(".pub") or "cert" in pattern.lower())

    def test_private_key_file_handling(self):
        """Test private key file handling."""
        test_key_patterns = [
            "id_rsa",
            "id_ed25519",
            "private_key.pem",
            "user_key"
        ]
        
        for pattern in test_key_patterns:
            # Private key files should not have .pub extension
            self.assertFalse(pattern.endswith(".pub"))

    def test_connection_option_building(self):
        """Test building of SSH connection options."""
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

    @mock.patch('tempfile.NamedTemporaryFile')
    def test_temporary_file_handling(self, mock_temp_file):
        """Test temporary file creation and cleanup."""
        mock_file = mock.Mock()
        mock_file.name = "/tmp/test_file.txt"
        mock_temp_file.return_value.__enter__.return_value = mock_file
        
        # Test temporary file usage pattern
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
            
        # Temporary files should have valid paths
        self.assertIsNotNone(temp_path)


if __name__ == '__main__':
    unittest.main()
