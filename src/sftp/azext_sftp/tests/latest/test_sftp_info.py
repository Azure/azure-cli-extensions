# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
import os
from unittest import mock
from azure.cli.core import azclierror
from azext_sftp import sftp_info


class SftpInfoTests(unittest.TestCase):

    def test_sftp_session_explicit_port(self):
        """Test that SFTPSession respects explicitly set port."""
        session = sftp_info.SFTPSession(
            storage_account="teststorage",
            username="test.user", 
            host="test.blob.core.windows.net",
            port=2222
        )
        
        self.assertEqual(session.port, 2222, "SFTPSession should use explicitly set port")
        self.assertIn("-P", session.build_args(), "build_args should include -P flag for non-standard port")
        port_index = session.build_args().index("-P")
        self.assertEqual(session.build_args()[port_index + 1], "2222", "Port value should follow -P flag")

    def test_build_args_excludes_port_for_none(self):
        """Test that build_args excludes -P flag if port is not specified by user."""
        session = sftp_info.SFTPSession(
            storage_account="teststorage",
            username="test.user",
            host="test.blob.core.windows.net"
        )
        
        args = session.build_args()
        
        self.assertNotIn("-P", args, "build_args should not include -P flag for standard port 22")

    @mock.patch('os.path.isfile')
    @mock.patch('os.path.abspath')
    def test_validate_session_with_valid_files(self, mock_abspath, mock_isfile):
        """Test session validation with valid certificate and key files."""
        mock_isfile.return_value = True
        # Make abspath return a predictable path for testing
        mock_abspath.side_effect = lambda x: os.path.normpath(x)
        
        session = sftp_info.SFTPSession(
            storage_account="teststorage",
            username="test.user",
            host="test.blob.core.windows.net",
            cert_file="/path/to/cert.pub",
            private_key_file="/path/to/key"
        )
        
        # Should not raise an exception
        session.validate_session()
        
        # Verify files were checked (using normalized paths)
        mock_isfile.assert_called()

    @mock.patch('os.path.isfile')
    def test_validate_session_with_missing_cert(self, mock_isfile):
        """Test session validation fails with missing certificate file."""
        def side_effect(path):
            return "/path/to/key" in path  # Only key file exists
        
        mock_isfile.side_effect = side_effect
        
        session = sftp_info.SFTPSession(
            storage_account="teststorage",
            username="test.user",
            host="test.blob.core.windows.net",
            cert_file="/path/to/cert.pub",
            private_key_file="/path/to/key"
        )
        
        with self.assertRaises(Exception):
            session.validate_session()

    def test_get_destination(self):
        """Test destination string generation."""
        session = sftp_info.SFTPSession(
            storage_account="teststorage",
            username="test.user",
            host="test.blob.core.windows.net"
        )
        
        destination = session.get_destination()
        expected = "test.user@test.blob.core.windows.net"        
        self.assertEqual(destination, expected, "Destination should be username@host")

    def test_resolve_connection_info_validates_host(self):
        """Test that resolve_connection_info validates host is set."""
        session = sftp_info.SFTPSession(
            storage_account="teststorage",
            username="test.user"
            # No host set
        )
        
        with self.assertRaises(azclierror.ValidationError) as context:
            session.resolve_connection_info()
        
        self.assertIn("Host must be set", str(context.exception))


class SftpInfoErrorHandlingTest(unittest.TestCase):
    """Test suite for SFTP session error handling and edge cases."""

    def setUp(self):
        """Set up test fixtures for error handling tests."""
        self.test_storage_account = "teststorage"
        self.test_username = "test.user"
        self.test_host = "test.blob.core.windows.net"
        self.test_port = 22
        self.test_cert_file = "/path/to/cert.pub"
        self.test_private_key_file = "/path/to/key"

    def test_missing_certificate_file_handling(self):
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
        
        # Session should still be created, but validation should fail
        self.assertEqual(session.cert_file, os.path.abspath(missing_cert))

    def test_missing_private_key_file_handling(self):
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
        
        # Session should still be created, but validation should fail
        self.assertEqual(session.private_key_file, os.path.abspath(missing_key))

    def test_invalid_hostname_handling(self):
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

    def test_invalid_port_handling(self):
        """Test behavior with invalid port numbers."""
        invalid_ports = [0, -1, 99999]
        
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
                if "-P" in command_args:
                    port_index = command_args.index("-P")
                    # Port should be converted to string
                    self.assertIsInstance(command_args[port_index + 1], str)

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
        self.assertEqual(session.cert_file, os.path.abspath(self.test_cert_file))
        self.assertEqual(session.private_key_file, os.path.abspath(self.test_private_key_file))

if __name__ == '__main__':
    unittest.main()
