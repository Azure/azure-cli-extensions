# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import io
import unittest
from unittest import mock
from azext_ssh import custom
from azext_ssh import rdp_utils
from azext_ssh import ssh_utils
from azext_ssh import connectivity_utils

from azure.cli.core import azclierror


class SshConnectivityUtilsCommandTest(unittest.TestCase):

    @mock.patch('platform.machine')
    def test_get_client_architecture_arm64(self, mock_plat):
        mock_plat.return_value = 'arm64'
        arch = connectivity_utils._get_client_architeture()
        self.assertEqual(arch, 'arm64')
    
    @mock.patch('platform.machine')
    def test_get_client_architecture_aarch64(self, mock_plat):
        mock_plat.return_value = 'aarch64'
        arch = connectivity_utils._get_client_architeture()
        self.assertEqual(arch, 'arm64')
    
    @mock.patch('platform.machine')
    def test_get_client_architecture_amd64(self, mock_plat):
        mock_plat.return_value = 'AMD64'
        arch = connectivity_utils._get_client_architeture()
        self.assertEqual(arch, 'amd64')

    @mock.patch('platform.machine')
    def test_get_client_architecture_x86(self, mock_plat):
        mock_plat.return_value = 'x64_86'
        arch = connectivity_utils._get_client_architeture()
        self.assertEqual(arch, '386')

    @mock.patch('platform.machine')
    def test_get_client_architecture_empty(self, mock_plat):
        mock_plat.return_value = ''
        with self.assertRaises(azclierror.BadRequestError):
            arch = connectivity_utils._get_client_architeture()

    @mock.patch('platform.machine')
    def test_get_client_architecture_unsupported(self, mock_plat):
        mock_plat.return_value = 'blabla'
        with self.assertRaises(azclierror.BadRequestError):
            arch = connectivity_utils._get_client_architeture()

    @mock.patch('platform.system')
    def test_get_client_os_unsupported(self, mock_plat):
        mock_plat.return_value = 'blabla'
        with self.assertRaises(azclierror.BadRequestError):
            arch = connectivity_utils._get_client_operating_system()
    
    def test_get_proxy_filename_windows(self):
        name = connectivity_utils._get_proxy_filename('Windows', 'amd64')
        self.assertEqual(name, 'sshProxy_windows_amd64_1_3_026973.exe')

    def test_get_proxy_filename_linux(self):
        name = connectivity_utils._get_proxy_filename('Linux', 'arm64')
        self.assertEqual(name, 'sshProxy_linux_arm64_1_3_026973')