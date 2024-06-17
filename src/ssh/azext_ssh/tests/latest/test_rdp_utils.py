# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_ssh import rdp_utils
from azext_ssh import ssh_info
from azext_ssh import ssh_utils


class RDPUtilsTest(unittest.TestCase):
    @mock.patch('os.environ.copy')
    @mock.patch.object(ssh_utils, 'get_ssh_client_path')
    @mock.patch('azext_ssh.custom.connectivity_utils.format_relay_info_string')
    @mock.patch("subprocess.Popen")
    def test_start_ssh_tunnel(self, mock_popen, mock_relay, mock_path, mock_env):
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, "user", None, "port", None, ['arg1', 'arg2', '-v'], False, "Microsoft.HybridCompute/machines", None, None, True, None)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"
        op_info.proxy_path = "proxy"
        op_info.relay_info = "relay"

        mock_env.return_value = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3'}
        mock_path.return_value = 'ssh'
        mock_relay.return_value = 'relay_string'
        mock_popen.return_value = 'ssh_process'

        expected_command = ['ssh', "vm", '-l', 'user', '-o', 'ProxyCommand=\"proxy\" -p port', '-i', 'priv', '-o', 'CertificateFile=\"cert\"', 'arg1', 'arg2', '-v']
        expected_env = {'var1': 'value1', 'var2': 'value2', 'var3': 'value3', 'SSHPROXY_RELAY_INFO': 'relay_string'}

        ssh_sub, print_logs = rdp_utils.start_ssh_tunnel(op_info)

        self.assertEqual(ssh_sub, 'ssh_process')
        self.assertEqual(print_logs, True)
        mock_popen.assert_called_once_with(expected_command, shell=True, stderr=mock.ANY, env=expected_env, encoding='utf-8')
        mock_relay.assert_called_once_with("relay")
        mock_path.assert_called_once_with('ssh', 'client')

    @mock.patch('platform.system')
    @mock.patch('platform.architecture')
    @mock.patch('os.environ')
    @mock.patch('os.path.join')
    @mock.patch('os.path.isfile')
    def test_get_rdp_path(self, mock_isfile, mock_join, mock_env, mock_arch, mock_sys):
        mock_env.__getitem__.return_value = "root"
        mock_join.side_effect = ['root/sys', 'root/sys/rdp']
        mock_arch.return_value = '32bit'
        mock_sys.return_value = 'Windows'
        mock_isfile.return_value = True

        expected_join_calls = [
            mock.call("root", 'System32'),
            mock.call("root/sys", "mstsc.exe")
        ]

        rdp_utils._get_rdp_path()

        mock_join.assert_has_calls(expected_join_calls)
        mock_isfile.assert_called_once_with('root/sys/rdp')

    # start rdp connection
    @mock.patch.object(rdp_utils, '_get_open_port')
    @mock.patch.object(rdp_utils, 'is_local_port_open')
    @mock.patch.object(rdp_utils, 'start_ssh_tunnel')
    @mock.patch.object(rdp_utils, 'wait_for_ssh_connection')
    @mock.patch.object(rdp_utils, 'call_rdp')
    @mock.patch.object(rdp_utils, 'terminate_ssh')
    def test_start_rdp_connection(self, mock_terminate, mock_rdp, mock_wait, mock_tunnel, mock_isopen, mock_getport):
        op_info = ssh_info.SSHSession("rg", "vm", None, None, None, False, "user", None, "port", None, ['arg1', 'arg2'], False, "Microsoft.HybridCompute/machines", None, None, True, None)
        op_info.public_key_file = "pub"
        op_info.private_key_file = "priv"
        op_info.cert_file = "cert"
        op_info.ssh_client_folder = "client"
        op_info.proxy_path = "proxy"
        op_info.relay_info = "relay"

        mock_getport.return_value = 1020
        mock_isopen.return_value = True
        ssh_pro = mock.Mock()
        # ssh_pro.return_value.poll.return_value = None
        mock_tunnel.return_value = ssh_pro, False
        mock_wait.return_value = True, [], False

        rdp_utils.start_rdp_connection(op_info, True, True)

        mock_terminate.assert_called_once_with(ssh_pro, [], False)
        # mock_rdp.assert_called_once_with(1020)
        mock_tunnel.assert_called_once_with(op_info)
        mock_wait.assert_called_once_with(ssh_pro, False)


if __name__ == '__main__':
    unittest.main()
