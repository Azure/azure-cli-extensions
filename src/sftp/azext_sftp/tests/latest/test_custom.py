# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import io
import unittest
from unittest import mock
from azext_sftp import custom

from azure.cli.core import azclierror


class SftpCustomCommandTest(unittest.TestCase):

    def test_sftp_cert_no_args(self):
        cmd = mock.Mock()
        self.assertRaises(
            azclierror.RequiredArgumentMissingError, custom.sftp_cert, cmd)

    @mock.patch('os.path.isdir')
    def test_sftp_cert_cert_file_missing(self, mock_isdir):
        cmd = mock.Mock()
        mock_isdir.return_value = False
        self.assertRaises(
            azclierror.InvalidArgumentValueError, custom.sftp_cert, cmd, cert_path="cert")

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    @mock.patch('azext_sftp.custom._check_or_create_public_private_files')
    @mock.patch('azext_sftp.custom._get_and_write_certificate')
    def test_sftp_cert(self, mock_write_cert, mock_get_keys, mock_abspath, mock_isdir):
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = ['/pubkey/path', '/cert/path', '/client/path']
        mock_get_keys.return_value = "pubkey", "privkey", False
        mock_write_cert.return_value = "cert", "username"

        custom.sftp_cert(cmd, "cert", "pubkey")

        mock_get_keys.assert_called_once_with('/pubkey/path', None, None, None)
        mock_write_cert.assert_called_once_with(cmd, 'pubkey', '/cert/path', None)

    def test_sftp_connect_preprod(self):
        cmd = mock.Mock()
        # 1. start devfabric
        # 2. get host and port from df
        # 3. call sftp_connect
        # def sftp_connect(cmd, storage_account, port = 22, cert_file=None, public_key_file=None):
        print("testing")
        custom.sftp_connect(
            cmd = cmd,
            storage_account = 'accounts8dd1b07a2e1fc8f',
            port = 10122,
            cert_file = 'C:\\Users\\johnli1\\AppData\\Local\\Temp\\id_rsa.pub-aadcert.pub'
            host_override = '127.0.0.1')