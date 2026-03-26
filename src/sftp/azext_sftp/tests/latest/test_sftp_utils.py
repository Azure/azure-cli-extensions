# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os
import subprocess
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

    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_info')
    def test_get_certificate_start_and_end_times_valid(self, mock_cert_info):
        """Test certificate start and end times parsing with valid certificate."""
        mock_cert_info.return_value = [
            "Type: ssh-rsa-cert-v01@openssh.com user certificate",
            "Public key: RSA-SHA256:AAAAB3NzaC1yc2E...",
            "Signing CA: RSA SHA256:AAAAB3NzaC1yc2E...",
            "Key ID: \"keyid\"",
            "Serial: 123456789",
            "Valid: from 2025-07-02T10:18:23 to 2025-07-02T11:18:23",
            "Critical Options: (none)",
            "Extensions:",
            "        permit-X11-forwarding",
            "        permit-agent-forwarding"
        ]
        
        start_time, end_time = sftp_utils.get_certificate_start_and_end_times("test_cert", None)
        
        self.assertIsNotNone(start_time)
        self.assertIsNotNone(end_time)
        self.assertEqual(start_time.year, 2025)
        self.assertEqual(start_time.month, 7)
        self.assertEqual(start_time.day, 2)
        self.assertEqual(start_time.hour, 10)
        self.assertEqual(start_time.minute, 18)
        self.assertEqual(start_time.second, 23)
        
        self.assertEqual(end_time.year, 2025)
        self.assertEqual(end_time.month, 7)
        self.assertEqual(end_time.day, 2)
        self.assertEqual(end_time.hour, 11)
        self.assertEqual(end_time.minute, 18)
        self.assertEqual(end_time.second, 23)

    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_info')
    def test_get_certificate_start_and_end_times_invalid_format(self, mock_cert_info):
        """Test certificate start and end times parsing with invalid certificate format."""
        mock_cert_info.return_value = [
            "Type: ssh-rsa-cert-v01@openssh.com user certificate",
            "Public key: RSA-SHA256:AAAAB3NzaC1yc2E...",
            "Invalid validity line format"
        ]
        
        result = sftp_utils.get_certificate_start_and_end_times("test_cert", None)
        
        self.assertIsNone(result)

    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_info')
    def test_get_certificate_start_and_end_times_no_validity(self, mock_cert_info):
        """Test certificate start and end times parsing with no validity information."""
        mock_cert_info.return_value = [
            "Type: ssh-rsa-cert-v01@openssh.com user certificate",
            "Public key: RSA-SHA256:AAAAB3NzaC1yc2E...",
            "Signing CA: RSA SHA256:AAAAB3NzaC1yc2E..."
        ]
        
        result = sftp_utils.get_certificate_start_and_end_times("test_cert", None)
        
        self.assertIsNone(result)

    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_info')
    def test_get_ssh_cert_validity_found(self, mock_cert_info):
        """Test getting SSH certificate validity line when it exists."""
        mock_cert_info.return_value = [
            "Type: ssh-rsa-cert-v01@openssh.com user certificate",
            "Valid: from 2025-07-02T10:18:23 to 2025-07-02T11:18:23",
            "Critical Options: (none)"
        ]
        
        validity = sftp_utils._get_ssh_cert_validity("test_cert", None)
        
        self.assertEqual(validity, "Valid: from 2025-07-02T10:18:23 to 2025-07-02T11:18:23")

    @mock.patch('azext_sftp.sftp_utils.get_ssh_cert_info')
    def test_get_ssh_cert_validity_not_found(self, mock_cert_info):
        """Test getting SSH certificate validity line when it doesn't exist."""
        mock_cert_info.return_value = [
            "Type: ssh-rsa-cert-v01@openssh.com user certificate",
            "Public key: RSA-SHA256:AAAAB3NzaC1yc2E...",
            "Critical Options: (none)"
        ]
        
        validity = sftp_utils._get_ssh_cert_validity("test_cert", None)
        
        self.assertIsNone(validity)

    def test_get_ssh_cert_validity_no_cert_file(self):
        """Test getting SSH certificate validity with no certificate file."""
        validity = sftp_utils._get_ssh_cert_validity(None, None)
        
        self.assertIsNone(validity)

    @mock.patch('subprocess.check_output')
    def test_get_ssh_cert_info_success(self, mock_subprocess):
        """Test getting SSH certificate info successfully."""
        mock_subprocess.return_value = b"""Type: ssh-rsa-cert-v01@openssh.com user certificate
Public key: RSA-SHA256:AAAAB3NzaC1yc2E...
Signing CA: RSA SHA256:AAAAB3NzaC1yc2E...
Key ID: "keyid"
Serial: 123456789
Valid: from 2025-07-02T10:18:23 to 2025-07-02T11:18:23
Critical Options: (none)
Extensions:
        permit-X11-forwarding
        permit-agent-forwarding"""
        
        cert_info = sftp_utils.get_ssh_cert_info("test_cert", None)
        
        self.assertIsInstance(cert_info, list)
        self.assertGreater(len(cert_info), 0)
        self.assertIn("Type: ssh-rsa-cert-v01@openssh.com user certificate", cert_info)
        self.assertIn("Valid: from 2025-07-02T10:18:23 to 2025-07-02T11:18:23", cert_info)

    @mock.patch('subprocess.check_output')
    def test_get_ssh_cert_info_failure(self, mock_subprocess):
        """Test getting SSH certificate info when command fails."""
        mock_subprocess.side_effect = OSError("ssh-keygen not found")
        
        with self.assertRaises(azclierror.BadRequestError) as context:
            sftp_utils.get_ssh_cert_info("test_cert", None)
        
        self.assertIn("Failed to get certificate info", str(context.exception))

    @mock.patch('subprocess.check_output')
    def test_get_ssh_cert_principals_success(self, mock_subprocess):
        """Test getting SSH certificate principals successfully."""
        mock_subprocess.return_value = b"""Type: ssh-rsa-cert-v01@openssh.com user certificate
Public key: RSA-SHA256:AAAAB3NzaC1yc2E...
Signing CA: RSA SHA256:AAAAB3NzaC1yc2E...
Key ID: "keyid"
Serial: 123456789
Valid: from 2025-07-02T10:18:23 to 2025-07-02T11:18:23
Principals:
        user1
        user2
        user3
Critical Options: (none)"""
        
        principals = sftp_utils.get_ssh_cert_principals("test_cert", None)
        
        self.assertIsInstance(principals, list)
        self.assertEqual(principals, ["user1", "user2", "user3"])

    @mock.patch('subprocess.check_output')
    def test_get_ssh_cert_principals_no_principals(self, mock_subprocess):
        """Test getting SSH certificate principals when none exist."""
        mock_subprocess.return_value = b"""Type: ssh-rsa-cert-v01@openssh.com user certificate
Public key: RSA-SHA256:AAAAB3NzaC1yc2E...
Signing CA: RSA SHA256:AAAAB3NzaC1yc2E...
Key ID: "keyid"
Serial: 123456789
Valid: from 2025-07-02T10:18:23 to 2025-07-02T11:18:23
Critical Options: (none)"""
        
        principals = sftp_utils.get_ssh_cert_principals("test_cert", None)
        
        self.assertIsInstance(principals, list)
        self.assertEqual(len(principals), 0)

    @mock.patch('subprocess.check_output')
    def test_get_ssh_cert_principals_failure(self, mock_subprocess):
        """Test getting SSH certificate principals when command fails."""
        mock_subprocess.side_effect = OSError("ssh-keygen not found")
        
        with self.assertRaises(azclierror.BadRequestError) as context:
            sftp_utils.get_ssh_cert_principals("test_cert", None)
        
        self.assertIn("Failed to get certificate info", str(context.exception))

    def test_certificate_time_parsing_edge_cases(self):
        """Test certificate time parsing with various edge cases."""
        # Test with different date formats (should fail gracefully)
        test_cases = [
            "Valid: from invalid-date to invalid-date",
            "Valid: from 2025-07-02T10:18:23 to invalid-date",
            "Valid: from invalid-date to 2025-07-02T11:18:23",
            "Invalid validity format",
            ""
        ]
        
        for test_case in test_cases:
            with mock.patch('azext_sftp.sftp_utils.get_ssh_cert_info') as mock_cert_info:
                mock_cert_info.return_value = [test_case] if test_case else []
                try:
                    result = sftp_utils.get_certificate_start_and_end_times("test_cert", None)
                    # Should return None for invalid formats
                    self.assertIsNone(result, f"Expected None for test case: {test_case}")
                except (ValueError, TypeError):
                    # Expected behavior for invalid date formats
                    pass


class SftpCertificateIntegrationTest(unittest.TestCase):
    """Integration tests for certificate-related functionality."""
    
    def test_certificate_workflow_integration(self):
        """Test that certificate functions work together correctly."""
        # This is a mock integration test to ensure the functions are callable
        # In a real scenario, this would test with actual certificate files
        
        cert_file = "mock_cert_file"
        
        # Test that functions exist and are callable
        self.assertTrue(callable(sftp_utils.get_ssh_cert_info))
        self.assertTrue(callable(sftp_utils.get_ssh_cert_principals))
        self.assertTrue(callable(sftp_utils.get_certificate_start_and_end_times))
        self.assertTrue(callable(sftp_utils._get_ssh_cert_validity))
        
        # Test error handling with invalid file
        with self.assertRaises((azclierror.BadRequestError, FileNotFoundError, OSError, subprocess.CalledProcessError)):
            sftp_utils.get_ssh_cert_info("nonexistent_file")

    def test_ssh_client_path_for_keygen(self):
        """Test SSH client path resolution for ssh-keygen command."""
        keygen_path = sftp_utils.get_ssh_client_path("ssh-keygen")
        self.assertIsNotNone(keygen_path)
        self.assertTrue(keygen_path.endswith("ssh-keygen") or keygen_path.endswith("ssh-keygen.exe"))
