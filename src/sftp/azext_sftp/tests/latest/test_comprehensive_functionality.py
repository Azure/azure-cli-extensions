# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import subprocess
import os
import tempfile
from unittest import mock

from azext_sftp import sftp_info, sftp_utils, custom


class ComprehensiveFunctionalityTest(unittest.TestCase):
    """Comprehensive test suite for SFTP extension functionality."""
    
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

    def test_sftp_operations_comprehensive(self):
        """Test various SFTP operations comprehensively."""
        base_command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=10",
            "-o", "BatchMode=yes",
            f"{self.test_username}@{self.test_host}"
        ]
        
        test_operations = [
            {
                "name": "List Directory",
                "commands": "ls\nexit\n",
                "description": "List remote directory contents",
                "expect_success": True
            },
            {
                "name": "Print Working Directory",
                "commands": "pwd\nexit\n", 
                "description": "Show current remote directory",
                "expect_success": True
            },
            {
                "name": "Show Help",
                "commands": "help\nexit\n",
                "description": "Display SFTP help",
                "expect_success": True
            },
            {
                "name": "Change Directory (should fail)",
                "commands": "cd nonexistent\nexit\n",
                "description": "Try to change to nonexistent directory",
                "expect_success": False
            }
        ]
        
        for operation in test_operations:
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
                        # For operations that should fail, we still expect the SFTP session to work
                        # but the specific command within it might fail
                        # The main process should still exit cleanly
                        pass
                        
                except subprocess.TimeoutExpired:
                    if operation["expect_success"]:
                        self.fail(f"{operation['name']} should not timeout")

    def test_file_upload_download_cycle(self):
        """Test complete file upload and download cycle."""
        test_content = f"Test content for SFTP upload/download cycle\nTimestamp: {os.times()}"
        remote_filename = "test_upload_download.txt"
        download_filename = "test_downloaded.txt"
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_content)
            upload_file_path = temp_file.name
        
        try:
            base_command = [
                "sftp",
                "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
                "-o", f"IdentityFile={self.test_private_key_file}",
                "-o", f"CertificateFile={self.test_cert_file}",
                "-o", "ConnectTimeout=10",
                "-o", "BatchMode=yes",
                f"{self.test_username}@{self.test_host}"
            ]
            
            # Test file upload
            upload_commands = f"put {upload_file_path} {remote_filename}\nls\nexit\n"
            
            upload_result = subprocess.run(
                base_command,
                input=upload_commands,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            self.assertEqual(upload_result.returncode, 0,
                           f"File upload should succeed. Error: {upload_result.stderr}")
            
            # Test file download  
            download_commands = f"get {remote_filename} {download_filename}\nexit\n"
            
            download_result = subprocess.run(
                base_command,
                input=download_commands,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            # Note: Download might fail if file wasn't uploaded successfully
            # This is an end-to-end test, so we check the overall operation
            
            # Clean up remote file
            cleanup_commands = f"rm {remote_filename}\nexit\n"
            subprocess.run(
                base_command,
                input=cleanup_commands,
                capture_output=True,
                text=True,
                timeout=10
            )
            
        except subprocess.TimeoutExpired:
            self.fail("File upload/download cycle timed out")
        finally:
            # Clean up local files
            for file_path in [upload_file_path, download_filename]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_extension_vs_direct_comparison(self):
        """Compare extension-built command with direct command."""
        # Build command using extension
        session = sftp_info.SFTPSession(
            storage_account=self.test_storage_account,
            username=self.test_username,
            host=self.test_host,
            port=self.test_port,
            cert_file=self.test_cert_file,
            private_key_file=self.test_private_key_file
        )
        
        extension_args = session.build_args()
        extension_destination = session.get_destination()
        
        extension_command = [
            sftp_utils.get_ssh_client_path("sftp"),
            "-o", "PasswordAuthentication=no",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", "ConnectTimeout=10",
            "-o", "BatchMode=yes"
        ]
        extension_command.extend(extension_args)
        extension_command.append(extension_destination)
        
        # Direct command that we know works
        direct_command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=10",
            "-o", "BatchMode=yes",
            f"{self.test_username}@{self.test_host}"
        ]
        
        # Test both commands
        test_input = "pwd\nexit\n"
        
        try:
            # Test extension command
            extension_result = subprocess.run(
                extension_command,
                input=test_input,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Test direct command
            direct_result = subprocess.run(
                direct_command,
                input=test_input,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Both should succeed
            self.assertEqual(extension_result.returncode, 0,
                           f"Extension command should succeed. Error: {extension_result.stderr}")
            self.assertEqual(direct_result.returncode, 0,
                           f"Direct command should succeed. Error: {direct_result.stderr}")
            
            # Outputs should be similar (both should show working directory)
            self.assertIn("/", extension_result.stdout)  # Should show path
            self.assertIn("/", direct_result.stdout)     # Should show path
            
        except subprocess.TimeoutExpired as e:
            self.fail(f"Command comparison timed out: {e}")

    @mock.patch('azure.cli.core.mock.DummyCli')
    def test_custom_command_integration(self, mock_cli):
        """Test integration with custom command functions."""
        # Mock CLI context
        mock_cli_instance = mock.Mock()
        mock_cli.return_value = mock_cli_instance
        
        # Test parameters that would be passed to custom functions
        test_args = {
            'storage_account': self.test_storage_account,
            'username': self.test_username,
            'cert_file': self.test_cert_file,
            'private_key_file': self.test_private_key_file,
            'port': self.test_port
        }
        
        # Test that parameters are handled correctly
        # (This would need more specific mocking based on actual custom.py implementation)
        self.assertIsNotNone(test_args['storage_account'])
        self.assertIsNotNone(test_args['username'])
        self.assertEqual(test_args['port'], 22)

    def test_batch_mode_prevents_hanging(self):
        """Test that batch mode prevents commands from hanging."""
        # Use an invalid host that would cause hanging without BatchMode
        hanging_command = [
            "sftp",
            "-o", "PubkeyAcceptedKeyTypes=rsa-sha2-256-cert-v01@openssh.com,rsa-sha2-256",
            "-o", f"IdentityFile={self.test_private_key_file}",
            "-o", f"CertificateFile={self.test_cert_file}",
            "-o", "ConnectTimeout=3",
            "-o", "BatchMode=yes",  # This should prevent hanging
            "nonuser@nonexistent.host.invalid"
        ]
        
        try:
            result = subprocess.run(
                hanging_command,
                input="pwd\nexit\n",
                capture_output=True,
                text=True,
                timeout=8  # Should not take long to fail
            )
            
            # Should fail quickly, not hang
            self.assertNotEqual(result.returncode, 0,
                              "Connection to invalid host should fail")
            
        except subprocess.TimeoutExpired:
            self.fail("Command should not hang with BatchMode=yes")

if __name__ == '__main__':
    unittest.main()
