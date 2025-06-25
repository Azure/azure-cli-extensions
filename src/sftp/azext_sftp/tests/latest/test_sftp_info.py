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


if __name__ == '__main__':
    unittest.main()
