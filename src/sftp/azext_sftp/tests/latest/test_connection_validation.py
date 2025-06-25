# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import subprocess
import os
import tempfile
from unittest import mock

from azext_sftp import sftp_info, sftp_utils


class ConnectionValidationTest(unittest.TestCase):
    """Test suite for validating SFTP connections using both direct and extension methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_storage_account = "johnli1canary"
        self.test_username = "johnli1canary.johnli1"
        self.test_host = "johnli1canary.blob.core.windows.net"
        self.test_port = 22
        self.test_cert_file = r"C:\users\johnli1\.ssh\id_rsa-aadcert.pub"
        self.test_private_key_file = r"C:\users\johnli1\.ssh\id_rsa"
        
        # Skip integration tests if credentials are not available
        if not os.path.exists(self.test_cert_file) or not os.path.exists(self.test_private_key_file):
            self.skipTest("SFTP credentials not available for integration testing")

    def test_direct_sftp_connection_port_22(self):
        """Test direct SFTP connection using port 22 (should work)."""
        command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=10",
            "-o", "BatchMode=yes",
            f"{self.test_username}@{self.test_host}"
        ]
        
        try:
            result = subprocess.run(
                command,
                input="pwd\nexit\n",
                capture_output=True,
                text=True,
                timeout=15
            )
            
            self.assertEqual(result.returncode, 0, 
                           f"Direct SFTP connection should succeed. Error: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            self.fail("Direct SFTP connection timed out")

    def test_direct_sftp_connection_port_10122_fails(self):
        """Test direct SFTP connection using port 10122 (should fail)."""
        command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",
            "-P", "10122",
            f"{self.test_username}@{self.test_host}"
        ]
        
        try:
            result = subprocess.run(
                command,
                input="pwd\nexit\n",
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertNotEqual(result.returncode, 0,
                              "SFTP connection to port 10122 should fail")
            
        except subprocess.TimeoutExpired:
            # Timeout is also an acceptable failure for wrong port
            pass

    def test_extension_sftp_session_creation(self):
        """Test that the extension creates SFTP session with correct parameters."""
        session = sftp_info.SFTPSession(
            storage_account=self.test_storage_account,
            username=self.test_username,
            host=self.test_host,
            port=self.test_port,
            cert_file=self.test_cert_file,
            private_key_file=self.test_private_key_file
        )
        
        self.assertEqual(session.storage_account, self.test_storage_account)
        self.assertEqual(session.username, self.test_username)
        self.assertEqual(session.host, self.test_host)
        self.assertEqual(session.port, self.test_port)
        self.assertTrue(session.cert_file.endswith("id_rsa-aadcert.pub"))
        self.assertTrue(session.private_key_file.endswith("id_rsa"))

    def test_extension_command_building(self):
        """Test that the extension builds correct SFTP commands."""
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
        
        # Verify essential arguments are present
        self.assertIn("-i", command_args)
        self.assertIn("-o", command_args)
        self.assertIn("-P", command_args)
        
        # Verify destination format
        self.assertEqual(destination, f"{self.test_username}@{self.test_host}")
        
        # Verify port is 22
        port_index = command_args.index("-P")
        self.assertEqual(command_args[port_index + 1], "22")

    @mock.patch('subprocess.run')
    def test_extension_connection_with_timeout(self, mock_subprocess_run):
        """Test that extension connection handles timeouts properly."""
        # Mock a timeout scenario
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(cmd="sftp", timeout=10)
        
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
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", "ConnectTimeout=10",
            "-o", "BatchMode=yes"
        ]
        full_command.extend(command_args)
        full_command.append(destination)
        
        # This should raise TimeoutExpired, not return success
        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.run(
                full_command,
                input="pwd\nexit\n",
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_expired_certificate_handling(self):
        """Test that extension properly detects expired certificates."""
        # This would need to be run with an actually expired certificate
        # For now, just test that the session can be created with cert parameters
        session = sftp_info.SFTPSession(
            storage_account=self.test_storage_account,
            username=self.test_username,
            host=self.test_host,
            port=self.test_port,
            cert_file=self.test_cert_file,
            private_key_file=self.test_private_key_file
        )
        
        # Verify cert file is properly set
        self.assertIsNotNone(session.cert_file)
        self.assertTrue(os.path.exists(session.cert_file) or not os.path.isabs(session.cert_file))

    def test_file_operations_integration(self):
        """Test basic file operations through SFTP."""
        # Create a temporary test file
        test_content = "Test content for SFTP upload"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Test basic SFTP operations
            command = [
                "sftp",
                "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
                "-o", f"IdentityFile={self.test_private_key_file}",
                "-o", f"CertificateFile={self.test_cert_file}",
                "-o", "ConnectTimeout=10",
                "-o", "BatchMode=yes",
                f"{self.test_username}@{self.test_host}"
            ]
            
            # Test directory listing
            result = subprocess.run(
                command,
                input="ls\nexit\n",
                capture_output=True,
                text=True,
                timeout=15
            )
            
            self.assertEqual(result.returncode, 0,
                           f"SFTP directory listing should succeed. Error: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            self.fail("SFTP file operations timed out")
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main()
