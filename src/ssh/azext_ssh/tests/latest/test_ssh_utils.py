# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import azclierror
from unittest import mock
import unittest
import platform
import os

from azext_ssh import ssh_utils
from azext_ssh import ssh_info

class SSHUtilsTests(unittest.TestCase):   
    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch.object(ssh_utils, '_get_ssh_client_path')
    @mock.patch('subprocess.run')
    @mock.patch('os.environ.copy')
    def test_start_ssh_connection_compute(self, mock_copy_env, mock_call, mock_path, mock_terminatecleanup, mock_startcleanup):

        op_info = ssh_info.SSHSession("rg", "vm", "ip", None, None, False, "user", None, "port", None, ['arg1', 'arg2', 'arg3'], False, "Microsof.Compute", None, None)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"

        mock_call.return_value = 0
        mock_path.return_value = 'ssh'
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        mock_startcleanup.return_value = 'log', ['arg1', 'arg2', 'arg3', '-E', 'log', '-v'], 'cleanup process'
        expected_command = ['ssh', 'user@ip', '-i', 'priv', '-o', 'CertificateFile=\"cert\"', '-p', 'port', 'arg1', 'arg2', 'arg3', '-E', 'log', '-v']
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3'}

        ssh_utils.start_ssh_connection(op_info, True, True)

        mock_path.assert_called_once_with('ssh', 'client')
        mock_startcleanup.assert_called_with('cert', 'priv', 'pub', False, True, True, ['arg1', 'arg2', 'arg3'])
        mock_call.assert_called_once_with(expected_command, env=expected_env, stderr=mock.ANY, text=True)
        mock_terminatecleanup.assert_called_once_with(True, True, False, 'cleanup process', 'cert', 'priv', 'pub', 'log', 0)
    
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch('os.environ.copy')
    @mock.patch.object(ssh_utils, '_get_ssh_client_path')
    @mock.patch('subprocess.run')
    @mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    def test_start_ssh_connection_arc(self, mock_relay_str, mock_call, mock_path, mock_copy_env, mock_terminatecleanup):
        
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, "user", None, "port", None, ['arg1'], False, "Microsoft.HybridCompute", None, None)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"
        op_info.proxy_path = "proxy"
        op_info.relay_info = "relay"
        
        mock_call.return_value = 0
        mock_relay_str.return_value = 'relay_string'
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        mock_path.return_value = 'ssh'
        expected_command = ['ssh', 'user@vm', '-o', 'ProxyCommand=\"proxy\" -p port', '-i', 'priv', '-o', 'CertificateFile=\"cert\"', 'arg1']
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3', 'SSHPROXY_RELAY_INFO':'relay_string'}

        ssh_utils.start_ssh_connection(op_info, False, False)

        mock_relay_str.assert_called_once_with('relay')
        mock_path.assert_called_once_with('ssh', 'client')
        mock_call.assert_called_once_with(expected_command, env=expected_env, stderr=mock.ANY, text=True)
        mock_terminatecleanup.assert_called_once_with(False, False, False, None, 'cert', 'priv', 'pub', None, 0)
    
    
    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    @mock.patch('os.path.abspath')
    def test_write_ssh_config_ip_and_vm_compute_append(self, mock_abspath, mock_warning):
        op_info = ssh_info.ConfigSession("config", "rg", "vm", "ip", None, None, False, False, "user", None, "port", "Microsoft.Compute", None, None, "client")
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
        op_info = ssh_info.ConfigSession("config", "rg", "vm", None, None, None, True, False, "user", None, "port", "Microsoft.HybridCompute", None, None, "client")
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
    def test_get_ssh_client_path_not_found(self, mock_isfile, mock_system, mock_join):
        mock_join.return_value = "ssh_path"
        mock_system.return_value = "Mac"
        mock_isfile.return_value = False
        path = ssh_utils._get_ssh_client_path("ssh", "folder")
        self.assertEqual(path, "ssh")
    
    @mock.patch('os.path.join')
    @mock.patch('platform.system')
    @mock.patch('os.path.isfile')
    def test_get_ssh_client_path_found(self, mock_isfile, mock_system, mock_join):
        mock_join.return_value = "ssh_path"
        mock_system.return_value = "Windows"
        mock_isfile.return_value = True
        path = ssh_utils._get_ssh_client_path("ssh-keygen", "folder")
        self.assertEqual(path, "ssh_path.exe")
    
    def test_get_ssh_client_preinstalled(self):
        path = ssh_utils._get_ssh_client_path("ssh-keygen", None)
        self.assertEqual(path, "ssh-keygen")