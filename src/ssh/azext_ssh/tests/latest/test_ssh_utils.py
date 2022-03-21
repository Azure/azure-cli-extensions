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

<<<<<<< HEAD
class SSHUtilsTests(unittest.TestCase):   
    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    @mock.patch('os.environ.copy')
    #@mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    def test_start_ssh_connection_cert_azurevm(self, mock_copy_env, mock_call, mock_build, mock_host, mock_path, mock_terminatecleanup, mock_startcleanup):
        #mock_relay_string.return_value = 'relay string'
        mock_path.return_value = 'ssh'
        mock_host.return_value = 'user@ip'
        mock_build.return_value = ['-i', 'file', '-o', 'option', '-p', 'port']
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        mock_startcleanup.return_value = 'log', ['arg1', 'arg2', 'arg3', '-E', 'log', '-v'], 'cleanup process'
        expected_command = ['ssh', 'user@ip', '-i', 'file', '-o', 'option', '-p', 'port', 'arg1', 'arg2', 'arg3', '-E', 'log', '-v']
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3'}

        ssh_utils.start_ssh_connection(None, None, 'vm', 'ip', 'user', 'cert', 'private', 'port', False, True, True, 'public', None, ['arg1', 'arg2', 'arg3'], False)

        mock_path.assert_called_once_with()
        mock_host.assert_called_once_with('user', 'ip')
        mock_build.assert_called_once_with('cert', 'private', 'port')
        mock_startcleanup.assert_called_with('cert', 'private', 'public', False, True, True, ['arg1', 'arg2', 'arg3'])
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows', env=expected_env)
        mock_terminatecleanup.assert_called_once_with(True, True, False, 'cleanup process', 'cert', 'private', 'public', 'log')
    
    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    @mock.patch('os.environ.copy')
    def test_start_ssh_connection_private_key_azurevm(self, mock_copy_env, mock_call, mock_build, mock_host, mock_path, mock_terminatecleanup, mock_startcleanup):
        mock_host.return_value = 'user@ip'
        mock_build.return_value = ["-i", "private", "-p", "port"]
        expected_command = ["path", "user@ip", "-i", "private", "-p", "port", '-E', 'log', '-v']
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        mock_startcleanup.return_value = 'log', ['-E', 'log', '-v'], 'cleanup process'

        ssh_utils.start_ssh_connection(None, None, 'vm', 'ip', 'user', None, 'private', 'port', False, False, False, None, 'path', None, True)

        mock_build.assert_called_once_with(None, "private", "port")
        mock_path.assert_not_called()
        mock_host.assert_called_once_with("user", "ip")
        mock_startcleanup.assert_called_with(None, 'private', None, True, False, False, [])
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows', env=expected_env)
        mock_terminatecleanup.assert_called_once_with(False, False, True, 'cleanup process', None, 'private', None, 'log')

    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    @mock.patch('os.environ.copy')
    def test_start_ssh_connection_cert_no_private_key_azurevm(self, mock_copy_env, mock_call, mock_build, mock_host, mock_path, mock_terminatecleanup, mock_startcleanup):
        mock_path.return_value = 'ssh'
        mock_host.return_value = 'user@ip'
        mock_build.return_value = ['-o', 'option']
        mock_startcleanup.return_value = None, ['arg1', 'arg2', 'arg3'], None
        expected_command = ['ssh', 'user@ip', '-o', 'option', 'arg1', 'arg2', 'arg3']
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3'}

        ssh_utils.start_ssh_connection(None, None, 'vm', 'ip', 'user', 'cert', None, None, False, False, False, None, None, ['arg1', 'arg2', 'arg3'], False)

        mock_build.assert_called_once_with('cert', None, None)
        mock_path.assert_called_once_with()
        mock_host.assert_called_once_with('user', 'ip')
        mock_startcleanup.assert_called_with('cert', None, None, False, False, False, ['arg1', 'arg2', 'arg3'])
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows', env=expected_env)
        mock_terminatecleanup.assert_called_once_with(False, False, False, None, 'cert', None, None, None)
    
    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    @mock.patch('os.environ.copy')
    def test_start_ssh_connection_password_azurevm(self, mock_copy_env, mock_call, mock_build, mock_host, mock_path, mock_terminatecleanup, mock_startcleanup):
        mock_path.return_value = 'ssh'
        mock_host.return_value = 'user@ip'
        mock_build.return_value = ['-p', 'port']
        mock_startcleanup.return_value = None, [], None
        expected_command = ['ssh', 'user@ip', '-p', 'port']
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3'}

        ssh_utils.start_ssh_connection(None, None, 'vm', 'ip', 'user', None, None, 'port', False, False, False, None, None, None, True)

        mock_build.assert_called_once_with(None, None, 'port')
        mock_path.assert_called_once_with()
        mock_host.assert_called_once_with('user', 'ip')
        mock_startcleanup.assert_called_once_with(None, None, None, False, False, False, [])
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows', env=expected_env)
        mock_terminatecleanup.assert_called_once_with(False, False, False, None, None, None, None, None)

    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch('os.environ.copy')
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    def test_start_ssh_connection_cert_arc(self, mock_relay_str,mock_host, mock_call, mock_build, mock_path, mock_copy_env, mock_terminatecleanup, mock_startcleanup):
        mock_relay_str.return_value = 'relay_string'
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        mock_path.return_value = 'ssh'
        mock_build.return_value = ['-i', 'private', '-o', 'option']
        mock_host.return_value = 'user@vm'
        mock_startcleanup.return_value = None, ['arg1'], None
        expected_command = ['ssh', 'user@vm', '-o', 'ProxyCommand=/path/to/proxy -p port', '-i', 'private', '-o', 'option', 'arg1']
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3', 'SSHPROXY_RELAY_INFO':'relay_string'}

        ssh_utils.start_ssh_connection('relay', '/path/to/proxy', 'vm', None, 'user', 'cert', 'private', 'port', True, False, False, None, None, ['arg1'], False)

        mock_relay_str.assert_called_once_with('relay')
        mock_path.assert_called_once_with()
        mock_build.assert_called_once_with('cert', 'private', None)
        mock_host.assert_called_once_with('user', 'vm')
        mock_startcleanup.assert_called_once_with('cert', 'private', None, False, False, False, ['arg1'])
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows', env=expected_env)
        mock_terminatecleanup.assert_called_once_with(False, False, False, None, 'cert', 'private', None, None)
    
    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch('os.environ.copy')
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    def test_start_ssh_connection_private_key_arc(self, mock_relay_str, mock_host, mock_call, mock_build, mock_path, mock_copy_env, mock_terminatecleanup, mock_startcleanup):
        mock_relay_str.return_value = 'relay_string'
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        mock_build.return_value = ['-i', 'private']
        expected_command = ['path', 'user@vm', '-o', 'ProxyCommand=/path/to/proxy', '-i', 'private', 'arg1', 'arg2', 'arg3']
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3', 'SSHPROXY_RELAY_INFO':'relay_string'}
        mock_host.return_value = 'user@vm'
        mock_startcleanup.return_value = None, ['arg1', 'arg2', 'arg3'], None

        ssh_utils.start_ssh_connection('relay', '/path/to/proxy', 'vm', None, 'user', None, 'private', None, True, False, False, None, 'path', ['arg1', 'arg2', 'arg3'], False)

        mock_path.assert_not_called()
        mock_relay_str.assert_called_once_with('relay')
        mock_host.assert_called_once_with('user', 'vm')
        mock_build.assert_called_once_with(None, 'private', None)
        mock_startcleanup.assert_called_once_with(None, 'private', None, False, False, False, ['arg1', 'arg2', 'arg3'])
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows', env=expected_env)
        mock_terminatecleanup.assert_called_once_with(False, False, False, None, None, 'private', None, None)
    
    @mock.patch.object(ssh_utils, '_start_cleanup')
    @mock.patch.object(ssh_utils, '_terminate_cleanup')
    @mock.patch('os.environ.copy')
    @mock.patch.object(ssh_utils, '_get_ssh_path')
    @mock.patch.object(ssh_utils, '_build_args')
    @mock.patch('subprocess.call')
    @mock.patch.object(ssh_utils, '_get_host')
    @mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    def test_start_ssh_connection_cert_no_private_key_arc(self, mock_relay_str, mock_host, mock_call, mock_build, mock_path, mock_copy_env, mock_terminatecleanup, mock_startcleanup):
        mock_relay_str.return_value = 'relay_string'
        mock_copy_env.return_value = {'var1':'value1', 'var2':'value2', 'var3':'value3'}
        mock_path.return_value = 'ssh'
        mock_build.return_value = ['-o', 'option']
        mock_startcleanup.return_value = 'log', ['arg1', 'arg2', '-E', 'log', '-v'], 'cleanup process'
        expected_command = ['ssh', 'user@vm', '-o', 'ProxyCommand=/path/to/proxy -p port', '-o', 'option', 'arg1', 'arg2', '-E', 'log', '-v']
        expected_env = {'var1':'value1', 'var2':'value2', 'var3':'value3', 'SSHPROXY_RELAY_INFO':'relay_string'}
        mock_host.return_value = 'user@vm'

        ssh_utils.start_ssh_connection('relay', '/path/to/proxy', 'vm', None, 'user', 'cert', None, 'port', True, False, True, 'public', None, ['arg1', 'arg2'], False)

        mock_relay_str.assert_called_once_with('relay')
        mock_path.assert_called_once_with()
        mock_build.assert_called_once_with('cert', None, None)
        mock_host.assert_called_once_with('user', 'vm')
        mock_startcleanup.assert_called_once_with('cert', None, 'public', False, False, True, ['arg1', 'arg2'])
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows', env=expected_env)
        mock_terminatecleanup.assert_called_once_with(False, True, False, 'cleanup process', 'cert', None, 'public', 'log')
    
    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    def test_write_ssh_config_ip_and_vm_azurevm(self, mock_warning):
=======
class SSHUtilsTests(unittest.TestCase):
    @mock.patch('os.path.join')
    @mock.patch.object(ssh_utils, '_get_ssh_client_path')
    @mock.patch('subprocess.call')
    @mock.patch('azext_ssh.ssh_info.SSHSession.build_args')
    @mock.patch('azext_ssh.ssh_info.SSHSession.get_host')
    @mock.patch('os.path.dirname')
    @mock.patch('multiprocessing.Process.start')
    @mock.patch('azext_ssh.ssh_utils._print_error_messages_from_ssh_log')
    def test_start_ssh_connection(self, mock_print_error, mock_start, mock_dirname, mock_host, mock_build, mock_call, mock_path, mock_join):
        mock_path.return_value = "ssh"
        mock_join.return_value = "/log/file/path"
        mock_build.return_value = ['-i', 'file', '-o', 'option']
        mock_host.return_value = "user@ip"
        mock_dirname.return_value = "dirname"
        mock_call.return_value = 0

        expected_command = ["ssh", "user@ip", "-i", "file", "-o", "option", "-E", "/log/file/path", "-v"]

        op_info = mock.Mock()
        op_info.ip = "ip"
        op_info.port = "port"
        op_info.local_user = "user"
        op_info.private_key_file = "private"
        op_info.public_key_file = "public"
        op_info.cert_file = "cert"
        op_info.ssh_args = None
        op_info.ssh_client_folder = "client/folder"
        op_info.build_args = mock_build
        op_info.get_host = mock_host

        ssh_utils.start_ssh_connection(op_info, True, True)
        mock_start.assert_called_once()
        mock_print_error.assert_called_once_with("/log/file/path", 0)
        mock_path.assert_called_once_with('ssh', 'client/folder')
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows')
    
    @mock.patch.object(ssh_utils, '_get_ssh_client_path')
    @mock.patch('subprocess.call')
    @mock.patch('azext_ssh.ssh_info.SSHSession.build_args')
    @mock.patch('azext_ssh.ssh_info.SSHSession.get_host')
    def test_start_ssh_connection_with_args(self, mock_host, mock_build, mock_call, mock_path):
        mock_path.return_value = "ssh"
        mock_host.return_value = "user@ip"
        mock_build.return_value = ["-i", "private", "-o", "CertificateFile=cert", "-p", "2222"]

        expected_command = ["ssh", "user@ip", "-i", "private", "-o", "CertificateFile=cert", "-p", "2222", "--thing", "-vv"]

        op_info = mock.Mock()
        op_info.ip = "ip"
        op_info.port = "2222"
        op_info.local_user = "user"
        op_info.private_key_file = "private"
        op_info.public_key_file = "public"
        op_info.cert_file = "cert"
        op_info.ssh_args = ["--thing", "-vv"]
        op_info.ssh_client_folder = "client/folder"
        op_info.build_args = mock_build
        op_info.get_host = mock_host

        ssh_utils.start_ssh_connection(op_info, True, True)

        mock_path.assert_called_once_with('ssh', 'client/folder')
        mock_call.assert_called_once_with(expected_command, shell=platform.system() == 'Windows')

    @mock.patch.object(ssh_utils, 'get_certificate_start_and_end_times')
    @mock.patch('azext_ssh.ssh_info.ConfigSession.get_config_text')
    def test_write_ssh_config_ip_and_vm(self, mock_get_text, mock_validity):
>>>>>>> upstream/main
        expected_lines = [
            "",
            "Host rg-vm",
            "\tHostName 1.2.3.4",
            "\tUser username",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"privatekey\"",
            "\tPort port",
            "Host 1.2.3.4",
            "\tUser username",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"privatekey\"",
            "\tPort port"
        ]
        
        mock_validity.return_value = None
        mock_get_text.return_value = expected_lines

        op_info = mock.Mock()
        op_info.config_path = "path/to/file"
        op_info.resource_group_name = "rg"
        op_info.vm_name = "vm"
        op_info.overwrite = True
        op_info.port = "port"
        op_info.ip = "1.2.3.4"
        op_info.local_user = "username"
        op_info.cert_file = "cert"
        op_info.private_key_file = "privatekey"
        op_info.ssh_client_folder = "client/folder"
        op_info.get_config_text = mock_get_text

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
<<<<<<< HEAD
            ssh_utils.write_ssh_config(
                None, None, 'vm', '1.2.3.4', 'username', 'cert', 'privatekey', 'port', False, True, True, 'publickey', 'path/to/file', True, 'rg', 'cred folder')

        mock_open.assert_called_once_with("path/to/file", "w")
        mock_warning.assert_called_once_with(True, True, False, 'cert', None, None)
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))
    
    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    def test_write_ssh_config_append_azurevm(self, mock_warning):
=======
            ssh_utils.write_ssh_config(op_info, True, False)
        mock_validity.assert_called_once_with("cert", "client/folder")
        mock_open.assert_called_once_with("path/to/file", "w", encoding='utf-8')
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))


    @mock.patch.object(ssh_utils, 'get_certificate_start_and_end_times')
    @mock.patch('azext_ssh.ssh_info.ConfigSession.get_config_text')
    def test_write_ssh_config_append(self, mock_get_text, mock_validity):
>>>>>>> upstream/main
        expected_lines = [
            "",
            "Host rg-vm",
            "\tHostName 1.2.3.4",
            "\tUser username",
            "\tCertificateFile \"cert\"",
            "\tPort port",
            "Host 1.2.3.4",
            "\tUser username",
            "\tCertificateFile \"cert\"",
            "\tPort port"
        ]

<<<<<<< HEAD
=======
        mock_validity.return_value = None
        mock_get_text.return_value = expected_lines

        op_info = mock.Mock()
        op_info.config_path = "path/to/file"
        op_info.resource_group_name = "rg"
        op_info.vm_name = "vm"
        op_info.overwrite = False
        op_info.ip = "1.2.3.4"
        op_info.local_user = "username"
        op_info.cert_file = "cert"
        op_info.private_key_file = "privatekey"
        op_info.ssh_client_folder = "client/folder"
        op_info.get_config_text = mock_get_text

>>>>>>> upstream/main
        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            ssh_utils.write_ssh_config(
<<<<<<< HEAD
                None, None, 'vm', '1.2.3.4', 'username', 'cert', None, 'port', False, False, True, 'public', 'path/to/file', False, 'rg', 'cred folder')

        mock_open.assert_called_once_with("path/to/file", "a")
        mock_warning.assert_called_once_with(True, False, False, 'cert', None, None)
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))
    
    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    def test_write_ssh_config_ip_only(self, mock_warning):
        expected_lines = [
            "",
            "Host 1.2.3.4",
            "\tUser username",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"privatekey\"",
            "\tPort port"
        ]

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            ssh_utils.write_ssh_config(
                None, None, None, '1.2.3.4', 'username', 'cert', 'privatekey', 'port', False, True, True, 'public', 'path/to/file', True, None, 'cred folder')

        mock_open.assert_called_once_with("path/to/file", "w")
        mock_warning.assert_called_once_with(True, True, False, 'cert', None, None)
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))
   
    @mock.patch.object(ssh_utils, '_prepare_relay_info_file')
    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    def test_write_ssh_config_append_arc(self, mock_warning, mock_relay):
        expected_lines = [
            "",
            "Host rg-vm",
            "\tHostName vm",
            "\tUser username",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"privatekey\"",
            "\tProxyCommand \"/path/to/proxy\" -r \"/path/to/relay_info\" -p port"
        ]

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_relay.return_value = '/path/to/relay_info', 'relay name'
            ssh_utils.write_ssh_config(
                'relay_info', '/path/to/proxy', 'vm', None, 'username', 'cert', 'privatekey', 'port', True, True, True, 'publickey', 'path/to/file', False, 'rg', 'cred folder' 
            )

        mock_open.assert_called_once_with("path/to/file", "a")
        mock_file.write.assert_called_with('\n'.join(expected_lines))
        mock_relay.assert_called_once_with('relay_info', 'cred folder', 'vm', 'rg')
        mock_warning.assert_called_once_with(True, True, True, 'cert', 'relay name', '/path/to/relay_info')
    
    @mock.patch.object(ssh_utils, '_prepare_relay_info_file')
    @mock.patch.object(ssh_utils, '_issue_config_cleanup_warning')
    def test_write_ssh_config_overwrite_arc(self, mock_warning, mock_relay):
        expected_lines = [
            "",
            "Host rg-vm",
            "\tHostName vm",
            "\tUser username",
            "\tCertificateFile \"cert\"",
            "\tIdentityFile \"privatekey\"",
            "\tProxyCommand \"/path/to/proxy\" -r \"/path/to/relay_info\" -p port"
        ]

        with mock.patch('builtins.open') as mock_open:
            mock_file = mock.Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_relay.return_value = '/path/to/relay_info', 'relay name'
            ssh_utils.write_ssh_config(
                'relay_info', '/path/to/proxy', 'vm', None, 'username', 'cert', 'privatekey', 'port', True, False, False, 'publickey', 'path/to/file', True, 'rg', 'cred folder'
            )

        mock_open.assert_any_call("path/to/file", "w")
        mock_file.write.assert_called_with('\n'.join(expected_lines))
        mock_relay.assert_called_once_with('relay_info', 'cred folder', 'vm', 'rg')
        mock_warning.assert_called_once_with(False, False, True, 'cert', 'relay name', '/path/to/relay_info')
        
   
=======
                op_info, True, True
            )

        mock_validity.assert_called_once_with("cert", "client/folder")

        mock_open.assert_called_once_with("path/to/file", "a", encoding='utf-8')
        mock_file.write.assert_called_once_with('\n'.join(expected_lines))
    

    @mock.patch('os.path.join')
>>>>>>> upstream/main
    @mock.patch('platform.system')
    @mock.patch('os.path.isfile')
    def test_get_ssh_client_path_with_client_folder_non_windows(self, mock_isfile, mock_system, mock_join):
        mock_join.return_value = "ssh_path"
        mock_system.return_value = "Linux"
        mock_isfile.return_value = True
        actual_path = ssh_utils._get_ssh_client_path(ssh_client_folder='/client/folder')
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
        actual_path = ssh_utils._get_ssh_client_path(ssh_command='ssh-keygen', ssh_client_folder='/client/folder')
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
        actual_path = ssh_utils._get_ssh_client_path(ssh_client_folder='/client/folder')
        self.assertEqual(actual_path, "ssh")
        mock_join.assert_called_once_with('/client/folder', 'ssh')
        mock_isfile.assert_called_once_with("ssh_path")

    @mock.patch('platform.system')
    def test_get_ssh_client_preinstalled_non_windows(self, mock_system):
        mock_system.return_value = "Mac"
        actual_path = ssh_utils._get_ssh_client_path()
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
        
        actual_path = ssh_utils._get_ssh_client_path()

        self.assertEqual("sshfilepath", actual_path)
        mock_system.assert_called_once_with()
        mock_arch.assert_called_once_with()
        mock_environ.__getitem__.assert_called_once_with("SystemRoot")
        mock_join.assert_has_calls(expected_join_calls)
        mock_isfile.assert_called_once_with("sshfilepath")
<<<<<<< HEAD
 
=======
    

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

        self.assertRaises(azclierror.UnclassifiedUserFault, ssh_utils._get_ssh_client_path)
>>>>>>> upstream/main
