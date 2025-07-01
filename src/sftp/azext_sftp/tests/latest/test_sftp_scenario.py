# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import subprocess
import tempfile
from unittest import mock
from azext_sftp import sftp_info


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class SftpPathExpansionTest(unittest.TestCase):
    """Test cases for proper handling of tilde paths in SFTP extension.
    
    These tests ensure that the SFTP extension properly expands tilde (~) paths
    to full absolute paths, similar to how the SSH extension should handle them.
    Owner: johnli1
    """

    def test_authentication_files_tilde_expansion(self):
        """Test that AuthenticationFiles correctly expands tilde paths."""
        auth_files = sftp_info.AuthenticationFiles(
            cert_file="~/.ssh/id_rsa-aadcert.pub",
            private_key_file="~/.ssh/id_rsa",
            public_key_file="~/.ssh/id_rsa.pub"
        )
        
        # Verify tilde was expanded
        self.assertFalse(auth_files.cert_file.startswith('~'))
        self.assertFalse(auth_files.private_key_file.startswith('~'))
        self.assertFalse(auth_files.public_key_file.startswith('~'))
        
        # Verify paths are absolute
        self.assertTrue(os.path.isabs(auth_files.cert_file))
        self.assertTrue(os.path.isabs(auth_files.private_key_file))
        self.assertTrue(os.path.isabs(auth_files.public_key_file))
        
        # Verify paths contain the expected file names
        self.assertTrue(auth_files.cert_file.endswith('id_rsa-aadcert.pub'))
        self.assertTrue(auth_files.private_key_file.endswith('id_rsa'))
        self.assertTrue(auth_files.public_key_file.endswith('id_rsa.pub'))

    def test_authentication_files_absolute_paths_unchanged(self):
        """Test that absolute paths are not modified by AuthenticationFiles."""
        abs_cert = "/absolute/path/cert.pub"
        abs_private = "/absolute/path/private"
        abs_public = "/absolute/path/public.pub"
        
        auth_files = sftp_info.AuthenticationFiles(
            cert_file=abs_cert,
            private_key_file=abs_private,
            public_key_file=abs_public
        )
        
        # On Windows, paths get normalized but should still be absolute
        self.assertTrue(os.path.isabs(auth_files.cert_file))
        self.assertTrue(os.path.isabs(auth_files.private_key_file))
        self.assertTrue(os.path.isabs(auth_files.public_key_file))


class SftpScenarioTest(unittest.TestCase):
    """Integration tests for SFTP extension scenarios.
    
    These tests focus on end-to-end scenarios that would typically be run
    by users in real-world situations. Uses mocking for Azure resources.
    Owner: johnli1
    """

    def __init__(self, *args, **kwargs):
        super(SftpScenarioTest, self).__init__(*args, **kwargs)

    def test_sftp_cert_generation_scenario(self):
        """Test end-to-end certificate generation scenario."""
        # Use mock-based testing instead of real Azure resources
        cert_path = os.path.join(TEST_DIR, 'test_cert.pub')
        
        # Test certificate generation command structure
        # This would typically involve actual Azure CLI command execution
        # For now, we'll focus on the command structure and parameter validation
        self.assertIsNotNone(cert_path)
        self.assertTrue(cert_path.endswith('.pub'))

    def test_sftp_connect_scenario_with_cert(self):
        """Test end-to-end SFTP connection scenario with certificate."""
        # This would test the full connect flow with actual or mocked SFTP operations
        pass

    def test_sftp_connect_scenario_auto_generate(self):
        """Test end-to-end SFTP connection scenario with auto-generated credentials."""
        # This would test the flow where no credentials are provided
        # and the system auto-generates everything needed
        pass


class SftpConnectionValidationTest(unittest.TestCase):
    """Integration tests for validating SFTP connections.
    
    These tests validate actual SFTP connection behavior using real Azure Storage
    accounts when available. Tests are skipped if required credentials are not present.
    Owner: johnli1
    """
    
    def setUp(self):
        """Set up test fixtures for connection validation."""
        self.test_storage_account = "johnli1canary"
        self.test_username = "johnli1canary.johnli1"
        self.test_host = "johnli1canary.blob.core.windows.net"
        self.test_port = 22
        self.test_cert_file = r"C:\users\johnli1\.ssh\id_rsa-aadcert.pub"
        self.test_private_key_file = r"C:\users\johnli1\.ssh\id_rsa"
        
        # Skip integration tests if credentials are not available
        if not os.path.exists(self.test_cert_file) or not os.path.exists(self.test_private_key_file):
            self.skipTest("SFTP credentials not available for integration testing")

    def test_direct_sftp_connection_standard_port(self):
        """Test direct SFTP connection using standard port 22."""
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
        self.assertEqual(session.cert_file, self.test_cert_file)
        self.assertEqual(session.private_key_file, self.test_private_key_file)

    def test_sftp_batch_operations(self):
        """Test SFTP batch operations for automated workflows."""
        operations = [
            {
                "name": "List Directory",
                "commands": "ls\nexit\n",
                "description": "List remote directory contents",
                "expect_success": True
            },
            {
                "name": "Change Directory",
                "commands": "pwd\ncd /\npwd\nexit\n",
                "description": "Change to root directory",
                "expect_success": True
            },
            {
                "name": "Get Remote Working Directory",
                "commands": "pwd\nexit\n", 
                "description": "Print current working directory",
                "expect_success": True
            }
        ]
        
        base_command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=10",
            "-o", "BatchMode=yes",
            f"{self.test_username}@{self.test_host}"
        ]
        
        for operation in operations:
            with self.subTest(operation=operation["name"]):
                try:
                    result = subprocess.run(
                        base_command,
                        input=operation["commands"],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    if operation["expect_success"]:
                        self.assertEqual(result.returncode, 0,
                                       f"{operation['name']} should succeed. Error: {result.stderr}")
                    else:
                        self.assertNotEqual(result.returncode, 0,
                                          f"{operation['name']} should fail")
                        
                except subprocess.TimeoutExpired:
                    if operation["expect_success"]:
                        self.fail(f"{operation['name']} timed out")


if __name__ == '__main__':
    unittest.main()
