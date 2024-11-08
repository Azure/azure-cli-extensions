# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest import mock
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
    
    def test_get_proxy_filename_amd_windows(self):
        name = connectivity_utils._get_proxy_filename('Windows', 'amd64')
        self.assertEqual(name, 'sshProxy_windows_amd64_1_3_026973.exe')

    def test_get_proxy_filename_arm_linux(self):
        name = connectivity_utils._get_proxy_filename('Linux', 'arm64')
        self.assertEqual(name, 'sshProxy_linux_arm64_1_3_026973')

    def test_get_proxy_filename_arm_Darwin(self):
        name = connectivity_utils._get_proxy_filename('Darwin', 'arm64')
        self.assertEqual(name, 'sshProxy_darwin_arm64_1_3_026973')

    def test_get_proxy_filename_386_linuux(self):
        name = connectivity_utils._get_proxy_filename('Linux', '386')
        self.assertEqual(name, 'sshProxy_linux_386_1_3_026973')
    
    def test_get_proxy_filename_386_darwin(self):
        with self.assertRaises(azclierror.BadRequestError):
            name = connectivity_utils._get_proxy_filename('Darwin', '386')
    
    @mock.patch('os.path.isfile')
    def test_check_proxy_is_installed_fail(self, mock_isfile):
        mock_isfile.side_effect = [False, True, True]
        with self.assertRaises(azclierror.CLIInternalError):
            connectivity_utils._check_proxy_installation("/dir/", "proxy")
    
    @mock.patch('os.path.isfile')
    def test_check_proxy_is_installed_sucess(self, mock_isfile):
        mock_isfile.side_effect = [True, True, True]
        connectivity_utils._check_proxy_installation("/dir/", "proxy")

    @mock.patch('os.path.isfile')
    def test_check_proxy_is_installed_fail_licenses(self, mock_isfile):
        mock_isfile.side_effect = [True, False, False]
        connectivity_utils._check_proxy_installation("/dir/", "proxy")
    
    @mock.patch('tarfile.open')
    def test_extract_proxy_from_tar(self, mock_open):
        mock_tar = mock_open.return_value.__enter__.return_value

        mock_file1 = mock.Mock()
        mock_file1.name = "dir/sshproxy"
        mock_file1.isfile = mock.Mock(return_value=True)
        
        mock_file2 = mock.Mock()
        mock_file2.name = "dir/license.txt"
        mock_file2.isfile = mock.Mock(return_value=True)
        
        mock_file3 = mock.Mock()
        mock_file3.name = "dir/thirdpartynotice.txt"
        mock_file3.isfile = mock.Mock(return_value=True)
        
        mock_file4 = mock.Mock()
        mock_file4.name = "dir"
        mock_file4.isfile = mock.Mock(return_value=False)
        
        mock_tar.getmembers.return_value = [mock_file1, mock_file2, mock_file3, mock_file4]

        connectivity_utils._extract_proxy_tar_files("proxy_package.tar.gz", "/tmp/install", "my_proxy")

        mock_tar.extractall.assert_called_once_with(members=[mock_file1, mock_file2, mock_file3], path="/tmp/install")

        self.assertEqual(mock_file1.name, "my_proxy")
        self.assertEqual(mock_file2.name, "license.txt")
        self.assertEqual(mock_file3.name, "thirdpartynotice.txt")

    @mock.patch('os.path.isfile')
    @mock.patch('platform.machine')
    @mock.patch('platform.system')
    @mock.patch('azext_ssh.connectivity_utils._get_proxy_install_dir')
    @mock.patch('os.path.join')
    @mock.patch('azext_ssh.file_utils.create_directory')
    @mock.patch('azext_ssh.connectivity_utils._download_proxy_from_MCR')
    @mock.patch('azext_ssh.connectivity_utils._check_proxy_installation')
    def test_install_proxy_create_dir(self, mock_check, mock_download, mock_dir, mock_join, mock_get_proxy_dir, mock_sys, mock_machine, mock_isfile):
        mock_machine.return_value = 'aarch64'
        mock_sys.return_value = 'linux'
        mock_get_proxy_dir.return_value = "/dir/proxy"
        mock_isfile.return_value = False

        connectivity_utils.install_client_side_proxy(None)

        mock_dir.assert_called_once_with("/dir/proxy", "Failed to create client proxy directory \'/dir/proxy\'.")
        mock_download.assert_called_once_with("/dir/proxy", "sshProxy_linux_arm64_1_3_026973", "linux", "arm64")
        mock_check.assert_called_once_with("/dir/proxy", "sshProxy_linux_arm64_1_3_026973")
