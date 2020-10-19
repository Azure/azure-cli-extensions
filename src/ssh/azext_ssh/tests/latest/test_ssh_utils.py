# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack import util
import mock
import unittest
import platform

from azext_ssh import ssh_utils


class SSHUtilsTests(unittest.TestCase):
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    def test_start_ssh_connection(self, mock_call, mock_build, mock_host, mock_path):
        mock_path.return_value = "ssh"
        mock_host.return_value = "user@ip"
        mock_build.return_value = ['-i', 'file', '-o', 'option']
        expected_command = ["ssh", "user@ip", "-i", "file", "-o", "option"]

        ssh_utils.start_ssh_connection("ip", "user", "cert", "private")

        mock_path.assert_called_once_with()
        mock_host.assert_called_once_with("user", "ip")
        mock_build.assert_called_once_with("cert", "private")
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows')

    @mock.patch('azext_ssh.ssh_utils.file_utils.make_dirs_for_file')
    def test_write_ssh_config_ip_and_vm(self, mock_make_dirs):
        expected_lines = [
            "Host rg-vm",
            "\tUser username",
            "\tHostName 1.2.3.4",
            "\tCertificateFile cert",
            "\tIdentityFile privatekey",
            "Host 1.2.3.4",
            "\tUser username",
            "\tCertificateFile cert",
            "\tIdentityFile privatekey"
        ]

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            ssh_utils.write_ssh_config(
                "path/to/file", "rg", "vm", "1.2.3.4", "username", "cert", "privatekey"
            )

        mock_make_dirs.assert_called_once_with("path/to/file")
        mock_open.assert_called_once_with("path/to/file", "w")
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))

    @mock.patch('azext_ssh.ssh_utils.file_utils.make_dirs_for_file')
    def test_write_ssh_config_ip_only(self, mock_make_dirs):
        expected_lines = [
            "Host 1.2.3.4",
            "\tUser username",
            "\tCertificateFile cert",
            "\tIdentityFile privatekey"
        ]

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            ssh_utils.write_ssh_config(
                "path/to/file", None, None, "1.2.3.4", "username", "cert", "privatekey"
            )

        mock_make_dirs.assert_called_once_with("path/to/file")
        mock_open.assert_called_once_with("path/to/file", "w")
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))

    @mock.patch('platform.system')
    def test_get_ssh_path_non_windows(self, mock_system):
        mock_system.return_value = "Mac"

        actual_path = ssh_utils._get_ssh_path()
        self.assertEqual('ssh', actual_path)
        mock_system.assert_called_once_with()

    def test_get_ssh_path_windows_32bit(self):
        self._test_ssh_path_windows('32bit', 'SysNative')

    def test_get_ssh_path_windows_64bit(self):
        self._test_ssh_path_windows('64bit', 'System32')

    @mock.patch('platform.system')
    @mock.patch('platform.architecture')
    @mock.patch('os.environ')
    @mock.patch('os.path.isfile')
    def test_get_ssh_path_windows_ssh_not_found(self, mock_isfile, mock_environ, mock_arch, mock_sys):
        mock_sys.return_value = "Windows"
        mock_arch.return_value = ("32bit", "foo", "bar")
        mock_environ.__getitem__.return_value = "rootpath"
        mock_isfile.return_value = False

        self.assertRaises(util.CLIError, ssh_utils._get_ssh_path)

    def test_get_host(self):
        actual_host = ssh_utils._get_host("username", "10.0.0.1")
        self.assertEqual("username@10.0.0.1", actual_host)

    def test_build_args(self):
        actual_args = ssh_utils._build_args("cert", "privatekey")
        expected_args = ["-i", "privatekey", "-o", "CertificateFile=cert"]
        self.assertEqual(expected_args, actual_args)

    @mock.patch('platform.system')
    @mock.patch('platform.architecture')
    @mock.patch('os.path.join')
    @mock.patch('os.environ')
    @mock.patch('os.path.isfile')
    def _test_ssh_path_windows(self, arch, expected_sys_path, mock_isfile, mock_environ, mock_join, mock_arch, mock_system):
        mock_system.return_value = "Windows"
        mock_arch.return_value = (arch, "foo", "bar")
        mock_environ.__getitem__.return_value = "rootpath"
        mock_join.side_effect = ["system32path", "sshfilepath"]
        mock_isfile.return_value = True
        expected_join_calls = [
            mock.call("rootpath", expected_sys_path),
            mock.call("system32path", "openSSH", "ssh.exe")
        ]

        actual_path = ssh_utils._get_ssh_path()

        self.assertEqual("sshfilepath", actual_path)
        mock_system.assert_called_once_with()
        mock_arch.assert_called_once_with()
        mock_environ.__getitem__.assert_called_once_with("SystemRoot")
        mock_join.assert_has_calls(expected_join_calls)
        mock_isfile.assert_called_once_with("sshfilepath")
