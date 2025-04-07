# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import azclierror
from unittest import mock
import unittest
from azext_ssh import ssh_utils
from azext_ssh import ssh_info


class SSHUtilsTests(unittest.TestCase):
    @mock.patch.object(ssh_utils, 'do_cleanup')
    @mock.patch.object(ssh_utils, '_check_ssh_logs_for_common_errors')
    @mock.patch.object(ssh_utils, 'get_ssh_client_path')
    @mock.patch('subprocess.Popen')
    @mock.patch('os.environ.copy')
    @mock.patch('platform.system')
    def test_start_ssh_connection_compute_aad_windows(self, mock_system, mock_copy_env, mock_call, mock_path, mock_read, mock_cleanup):

        op_info = ssh_info.SSHSession("rg", "vm", "ip", None, None, False, "user", None, "port", None, ['arg1', 'arg2', 'arg3'], False, "Microsof.Compute/virtualMachines", None, None, False, False)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"

        ssh_process = mock.Mock()
        ssh_process.poll.return_value = 0

        mock_system.return_value = 'Windows'
        mock_call.return_value = 0
        mock_path.return_value = 'ssh'
        mock_call.return_value = ssh_process
        mock_copy_env.return_value = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'}
        expected_command = ['ssh', 'ip', '-l', 'user', '-i', 'priv', '-o', 'CertificateFile=\"cert\"', '-p', 'port', '-v', 'arg1', 'arg2', 'arg3']
        expected_env = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'}

        ssh_utils.start_ssh_connection(op_info, True, True)

        mock_path.assert_called_once_with('ssh', 'client')
        mock_call.assert_called_once_with(expected_command, stderr=mock.ANY, env=expected_env, encoding='utf-8')
        mock_read.assert_called_once_with(ssh_process, op_info, True, True)
        mock_cleanup.assert_called_once_with(True, True, False, 'cert', 'priv', 'pub')

    @mock.patch.object(ssh_utils, 'do_cleanup')
    @mock.patch.object(ssh_utils, '_wait_to_delete_credentials')
    @mock.patch.object(ssh_utils, 'get_ssh_client_path')
    @mock.patch('subprocess.Popen')
    @mock.patch('os.environ.copy')
    @mock.patch('platform.system')
    def test_start_ssh_connection_compute_local_linux(self, mock_system, mock_copy_env, mock_call, mock_path, mock_wait, mock_cleanup):

        op_info = ssh_info.SSHSession("rg", "vm", "ip", None, None, False, "user", None, "port", None, ['arg1', 'arg2', 'arg3'], False, "Microsoft.Compute/virtualMachines", None, None, False, False)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"

        ssh_process = mock.Mock()
        ssh_process.poll.return_value = 0

        mock_system.return_value = 'Linux'
        mock_call.return_value = 0
        mock_path.return_value = 'ssh'
        mock_call.return_value = ssh_process
        mock_copy_env.return_value = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'}
        expected_command = ['ssh', 'ip', '-l', 'user', '-i', 'priv', '-o', 'CertificateFile=\"cert\"', '-p', 'port', 'arg1', 'arg2', 'arg3']
        expected_env = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'}

        ssh_utils.start_ssh_connection(op_info, False, False)

        mock_path.assert_called_once_with('ssh', 'client')
        mock_call.assert_called_once_with(expected_command, env=expected_env, encoding='utf-8')
        mock_wait.assert_called_once_with(ssh_process, op_info, False, False)
        mock_cleanup.assert_called_once_with(False, False, False, 'cert', 'priv', 'pub')

    @mock.patch.object(ssh_utils, 'do_cleanup')
    @mock.patch.object(ssh_utils, '_check_ssh_logs_for_common_errors')
    @mock.patch.object(ssh_utils, 'get_ssh_client_path')
    @mock.patch('os.environ.copy')
    @mock.patch('subprocess.Popen')
    @mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    @mock.patch('platform.system')
    def test_start_ssh_connection_arc_aad_windows(self, mock_platform, mock_relay_str, mock_call, mock_copy_env, mock_path, mock_read, mock_cleanup):

        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, "user", None, "port", None, ['arg1'], False, "Microsoft.HybridCompute/machines", None, None, False, False)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"
        op_info.proxy_path = "proxy"
        op_info.relay_info = "relay"

        ssh_process = mock.Mock()
        ssh_process.poll.return_value = 0

        mock_platform.return_value = 'Windows'
        mock_call.return_value = ssh_process
        mock_relay_str.return_value = 'relay_string'
        mock_copy_env.return_value = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'}
        mock_path.return_value = 'ssh'
        expected_command = ['ssh', 'vm', '-l', 'user', '-o', 'ProxyCommand=\"proxy\" -p port', '-i', 'priv', '-o', 'CertificateFile=\"cert\"', '-v', 'arg1']
        expected_env = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3', 'SSHPROXY_RELAY_INFO': 'relay_string'}

        ssh_utils.start_ssh_connection(op_info, True, True)

        mock_relay_str.assert_called_once_with('relay')
        mock_path.assert_called_once_with('ssh', 'client')
        mock_call.assert_called_once_with(expected_command, stderr=mock.ANY, env=expected_env, encoding='utf-8')
        mock_cleanup.assert_called_once_with(True, True, False, 'cert', 'priv', 'pub')
        mock_read.assert_called_once_with(ssh_process, op_info, True, True)

    @mock.patch.object(ssh_utils, 'do_cleanup')
    @mock.patch.object(ssh_utils, '_wait_to_delete_credentials')
    @mock.patch.object(ssh_utils, 'get_ssh_client_path')
    @mock.patch('os.environ.copy')
    @mock.patch('subprocess.Popen')
    @mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    @mock.patch('platform.system')
    def test_start_ssh_connection_arc_local_linux(self, mock_platform, mock_relay_str, mock_call, mock_copy_env, mock_path, mock_wait, mock_cleanup):
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, "user", None, "port", None, ['arg1'], False, "Microsoft.HybridCompute/machines", None, None, False, False)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"
        op_info.proxy_path = "proxy"
        op_info.relay_info = "relay"

        ssh_process = mock.Mock()
        ssh_process.poll.return_value = 0

        mock_platform.return_value = 'Linux'
        mock_call.return_value = ssh_process
        mock_relay_str.return_value = 'relay_string'
        mock_copy_env.return_value = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'}
        mock_path.return_value = 'ssh'
        expected_command = ['ssh', 'vm', '-l', 'user', '-o', 'ProxyCommand=\"proxy\" -p port', '-i', 'priv', '-o', 'CertificateFile=\"cert\"', 'arg1']
        expected_env = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3', 'SSHPROXY_RELAY_INFO': 'relay_string'}

        ssh_utils.start_ssh_connection(op_info, False, False)

        mock_relay_str.assert_called_once_with('relay')
        mock_path.assert_called_once_with('ssh', 'client')
        mock_call.assert_called_once_with(expected_command, env=expected_env, encoding='utf-8')
        mock_cleanup.assert_called_once_with(False, False, False, 'cert', 'priv', 'pub')
        mock_wait.assert_called_once_with(ssh_process, op_info, False, False)

    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    @mock.patch('os.path.abspath')
    def test_write_ssh_config_ip_and_vm_compute_append(self, mock_abspath, mock_warning):
        op_info = ssh_info.ConfigSession("config", "rg", "vm", "ip", None, None, False, False, "user", None, "port", "Microsoft.Compute/virtualMachines", None, None, "client", False)
        op_info.config_path = "config"
        op_info.ssh_client_folder = "client"
        op_info.private_key_file = "priv"
        op_info.public_key_file = "pub"
        op_info.cert_file = "cert"
        expected_lines = [
            "",
            "Host rg-vm",
            "\tUser user",
            "\tHostName ip",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"priv\"",
            "\tPort port",
            "Host ip",
            "\tUser user",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"priv\"",
            "\tPort port"
        ]

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            ssh_utils.write_ssh_config(
                op_info, True, True)

        mock_warning.assert_called_once_with(True, True, False, "cert", None, "client")
        mock_open.assert_called_once_with("config", 'a', encoding='utf-8')
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))

    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    @mock.patch('os.path.abspath')
    @mock.patch.object(ssh_info.ConfigSession, '_create_relay_info_file')
    def test_write_ssh_config_arc_overwrite(self, mock_create_file, mock_abspath, mock_warning):
        op_info = ssh_info.ConfigSession("config", "rg", "vm", None, None, None, True, False, "user", None, "port", "Microsoft.HybridCompute/machines", None, None, "client", False)
        op_info.config_path = "config"
        op_info.ssh_client_folder = "client"
        op_info.private_key_file = "priv"
        op_info.public_key_file = "pub"
        op_info.cert_file = "cert"
        op_info.proxy_path = "proxy"
        mock_create_file.return_value = "relay"
        expected_lines = [
            "",
            "Host rg-vm",
            "\tHostName vm",
            "\tUser user",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"priv\"",
            "\tProxyCommand \"proxy\" -r \"relay\" -p port"
        ]

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            ssh_utils.write_ssh_config(
                op_info, True, True)

        mock_warning.assert_called_once_with(True, True, True, "cert", "relay", "client")
        mock_open.assert_called_once_with("config", 'w', encoding='utf-8')
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))

    @mock.patch('os.path.join')
    @mock.patch('platform.system')
    @mock.patch('os.path.isfile')
    def test_get_ssh_client_path_with_client_folder_non_windows(self, mock_isfile, mock_system, mock_join):
        mock_join.return_value = "ssh_path"
        mock_system.return_value = "Linux"
        mock_isfile.return_value = True
        actual_path = ssh_utils.get_ssh_client_path(ssh_client_folder='/client/folder')
        self.assertEqual(actual_path, "ssh_path")
        mock_join.assert_called_once_with('/client/folder', 'ssh')
        mock_isfile.assert_called_once_with("ssh_path")

    @mock.patch('os.path.join')
    @mock.patch('platform.system')
    @mock.patch('os.path.isfile')
    def test_get_ssh_client_path_with_client_folder_windows(self, mock_isfile, mock_system, mock_join):
        mock_join.return_value = "ssh_keygen_path"
        mock_system.return_value = "Windows"
        mock_isfile.return_value = True
        actual_path = ssh_utils.get_ssh_client_path(ssh_command='ssh-keygen', ssh_client_folder='/client/folder')
        self.assertEqual(actual_path, "ssh_keygen_path.exe")
        mock_join.assert_called_once_with('/client/folder', 'ssh-keygen')
        mock_isfile.assert_called_once_with("ssh_keygen_path.exe")

    @mock.patch('os.path.join')
    @mock.patch('platform.system')
    @mock.patch('os.path.isfile')
    def test_get_ssh_client_path_with_client_folder_no_file(self, mock_isfile, mock_system, mock_join):
        mock_join.return_value = "ssh_path"
        mock_system.return_value = "Mac"
        mock_isfile.return_value = False
        actual_path = ssh_utils.get_ssh_client_path(ssh_client_folder='/client/folder')
        self.assertEqual(actual_path, "ssh")
        mock_join.assert_called_once_with('/client/folder', 'ssh')
        mock_isfile.assert_called_once_with("ssh_path")

    @mock.patch('platform.system')
    def test_get_ssh_client_preinstalled_non_windows(self, mock_system):
        mock_system.return_value = "Mac"
        actual_path = ssh_utils.get_ssh_client_path()
        self.assertEqual('ssh', actual_path)
        mock_system.assert_called_once_with()

    def test_get_ssh_client_preinstalled_windows_32bit(self):
        self._test_get_ssh_client_path_preinstalled_windows('32bit', 'x86', 'System32')

    def test_get_ssh_client_preinstalled_windows_64bitOS_32bitPlatform(self):
        self._test_get_ssh_client_path_preinstalled_windows('32bit', 'x64', 'SysNative')

    def test_get_ssh_client_preinstalled_windows_64bitOS_64bitPlatform(self):
        self._test_get_ssh_client_path_preinstalled_windows('64bit', 'x64', 'System32')

    @mock.patch('platform.system')
    @mock.patch('platform.architecture')
    @mock.patch('platform.machine')
    @mock.patch('os.path.join')
    @mock.patch('os.environ')
    @mock.patch('os.path.isfile')
    def _test_get_ssh_client_path_preinstalled_windows(self, platform_arch, os_arch, expected_sysfolder, mock_isfile, mock_environ, mock_join, mock_machine, mock_arch, mock_system):
        mock_system.return_value = "Windows"
        mock_arch.return_value = (platform_arch, "foo", "bar")
        mock_machine.return_value = os_arch
        mock_environ.__getitem__.return_value = "rootpath"
        mock_join.side_effect = ["system32path", "sshfilepath"]
        mock_isfile.return_value = True

        expected_join_calls = [
            mock.call("rootpath", expected_sysfolder),
            mock.call("system32path", "openSSH", "ssh.exe")
        ]

        actual_path = ssh_utils.get_ssh_client_path()

        self.assertEqual("sshfilepath", actual_path)
        mock_system.assert_called_once_with()
        mock_arch.assert_called_once_with()
        mock_environ.__getitem__.assert_called_once_with("SystemRoot")
        mock_join.assert_has_calls(expected_join_calls)
        mock_isfile.assert_called_once_with("sshfilepath")

    @mock.patch('platform.system')
    @mock.patch('platform.architecture')
    @mock.patch('platform.machine')
    @mock.patch('os.environ')
    @mock.patch('os.path.isfile')
    def test_get_ssh_path_windows_ssh_preinstalled_not_found(self, mock_isfile, mock_environ, mock_machine, mock_arch, mock_sys):
        mock_sys.return_value = "Windows"
        mock_arch.return_value = ("32bit", "foo", "bar")
        mock_machine.return_value = "x64"
        mock_environ.__getitem__.return_value = "rootpath"
        mock_isfile.return_value = False

        self.assertRaises(azclierror.UnclassifiedUserFault, ssh_utils.get_ssh_client_path)
