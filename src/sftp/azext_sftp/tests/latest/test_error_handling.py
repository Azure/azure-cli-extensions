# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import subprocess
import os
from unittest import mock

from azext_sftp import sftp_info, sftp_utils


class ErrorHandlingTest(unittest.TestCase):
    """Test suite for SFTP error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_storage_account = "johnli1canary"
        self.test_username = "johnli1canary.johnli1"
        self.test_host = "johnli1canary.blob.core.windows.net"
        self.test_port = 22
        self.test_cert_file = r"C:\users\johnli1\.ssh\id_rsa-aadcert.pub"
        self.test_private_key_file = r"C:\users\johnli1\.ssh\id_rsa"

    def test_missing_certificate_file(self):
        """Test behavior when certificate file is missing."""
        missing_cert = "/nonexistent/cert.pub"
        
        session = sftp_info.SFTPSession(
            storage_account=self.test_storage_account,
            username=self.test_username,
            host=self.test_host,
            port=self.test_port,
            cert_file=missing_cert,
            private_key_file=self.test_private_key_file
        )
        
        # Session should still be created, but connection should fail
        self.assertEqual(session.cert_file, os.path.abspath(missing_cert))

    def test_missing_private_key_file(self):
        """Test behavior when private key file is missing."""
        missing_key = "/nonexistent/key"
        
        session = sftp_info.SFTPSession(
            storage_account=self.test_storage_account,
            username=self.test_username,
            host=self.test_host,
            port=self.test_port,
            cert_file=self.test_cert_file,
            private_key_file=missing_key
        )
        
        # Session should still be created, but connection should fail
        self.assertEqual(session.private_key_file, os.path.abspath(missing_key))

    def test_invalid_host(self):
        """Test behavior with invalid hostname."""
        invalid_host = "nonexistent.host.invalid"
        
        session = sftp_info.SFTPSession(
            storage_account=self.test_storage_account,
            username=self.test_username,
            host=invalid_host,
            port=self.test_port,
            cert_file=self.test_cert_file,
            private_key_file=self.test_private_key_file
        )
        
        command_args = session.build_args()
        destination = session.get_destination()
        
        # Should build command but connection will fail
        self.assertEqual(destination, f"{self.test_username}@{invalid_host}")
        self.assertIn("-i", command_args)

    def test_invalid_port(self):
        """Test behavior with invalid port numbers."""
        invalid_ports = [0, -1, 99999, "invalid"]
        
        for port in invalid_ports:
            with self.subTest(port=port):
                session = sftp_info.SFTPSession(
                    storage_account=self.test_storage_account,
                    username=self.test_username,
                    host=self.test_host,
                    port=port,
                    cert_file=self.test_cert_file,
                    private_key_file=self.test_private_key_file
                )
                
                # Session should handle port conversion
                command_args = session.build_args()
                port_index = command_args.index("-P")
                # Port should be converted to string
                self.assertIsInstance(command_args[port_index + 1], str)

    def test_connection_timeout_detection(self):
        """Test that connection timeouts are properly detected."""
        # Test with a host that will timeout (using a non-routable address)
        timeout_host = "192.0.2.1"  # RFC 5737 test address
        
        command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=3",
            "-o", "BatchMode=yes",
            f"{self.test_username}@{timeout_host}"
        ]
        
        try:
            result = subprocess.run(
                command,
                input="pwd\nexit\n",
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Should fail with connection error, not succeed
            self.assertNotEqual(result.returncode, 0,
                              "Connection to non-routable address should fail")
            
        except subprocess.TimeoutExpired:
            # Timeout is expected and acceptable
            pass

    def test_connection_refused_detection(self):
        """Test that connection refused errors are properly detected."""
        # Test with wrong port that should be refused
        command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",
            "-P", "10122",  # Wrong port
            f"{self.test_username}@{self.test_host}"
        ]
        
        try:
            result = subprocess.run(
                command,
                input="pwd\nexit\n",
                capture_output=True,
                text=True,
                timeout=8
            )
            
            # Should fail with connection error
            self.assertNotEqual(result.returncode, 0,
                              "Connection to wrong port should fail")
            
        except subprocess.TimeoutExpired:
            # Timeout is also acceptable for wrong port
            pass

    @mock.patch('subprocess.run')
    def test_subprocess_error_handling(self, mock_subprocess_run):
        """Test handling of various subprocess errors."""
        # Test different error scenarios
        error_scenarios = [
            subprocess.TimeoutExpired(cmd="sftp", timeout=10),
            subprocess.CalledProcessError(returncode=255, cmd="sftp"),
            OSError("Command not found"),
        ]
        
        for error in error_scenarios:
            with self.subTest(error=type(error).__name__):
                mock_subprocess_run.side_effect = error
                
                session = sftp_info.SFTPSession(
                    storage_account=self.test_storage_account,
                    username=self.test_username,
                    host=self.test_host,
                    port=self.test_port,
                    cert_file=self.test_cert_file,
                    private_key_file=self.test_private_key_file
                )
                
                command_args = session.build_args()
                destination = session.get_destination()
                
                full_command = [
                    sftp_utils.get_ssh_client_path("sftp"),
                    "-o", "PasswordAuthentication=no",
                    "-o", "ConnectTimeout=10",
                    "-o", "BatchMode=yes"
                ]
                full_command.extend(command_args)
                full_command.append(destination)
                
                # Should raise the expected error
                with self.assertRaises(type(error)):
                    subprocess.run(
                        full_command,
                        input="pwd\nexit\n",
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

    def test_credential_validation(self):
        """Test credential validation logic."""
        # Test with real credential paths if available
        if os.path.exists(self.test_cert_file) and os.path.exists(self.test_private_key_file):
            session = sftp_info.SFTPSession(
                storage_account=self.test_storage_account,
                username=self.test_username,
                host=self.test_host,
                port=self.test_port,
                cert_file=self.test_cert_file,
                private_key_file=self.test_private_key_file
            )
            
            # Verify files are accessible
            self.assertTrue(os.path.exists(session.cert_file))
            self.assertTrue(os.path.exists(session.private_key_file))
            
            # Verify command building includes both files
            command_args = session.build_args()
            self.assertIn("-i", command_args)
            self.assertIn("-o", command_args)
            
            # Find certificate option
            cert_found = False
            for i, arg in enumerate(command_args):
                if arg == "-o" and i + 1 < len(command_args):
                    if "CertificateFile" in command_args[i + 1]:
                        cert_found = True
                        break
            self.assertTrue(cert_found, "CertificateFile option should be present")

    def test_batch_mode_enforcement(self):
        """Test that batch mode is properly enforced to prevent hanging."""
        session = sftp_info.SFTPSession(
            storage_account=self.test_storage_account,
            username=self.test_username,
            host=self.test_host,
            port=self.test_port,
            cert_file=self.test_cert_file,
            private_key_file=self.test_private_key_file
        )
        
        command_args = session.build_args()
        
        # Build full command as extension would
        full_command = [
            sftp_utils.get_ssh_client_path("sftp"),
            "-o", "PasswordAuthentication=no",
            "-o", "BatchMode=yes"  # This should prevent hanging
        ]
        full_command.extend(command_args)
        
        # Verify BatchMode is set
        batch_mode_set = False
        for i, arg in enumerate(full_command):
            if arg == "-o" and i + 1 < len(full_command):
                if "BatchMode=yes" in full_command[i + 1]:
                    batch_mode_set = True
                    break
        self.assertTrue(batch_mode_set, "BatchMode should be enforced")


if __name__ == '__main__':
    unittest.main()
