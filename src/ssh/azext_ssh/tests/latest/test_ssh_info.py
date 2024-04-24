# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_ssh import ssh_info


class SSHInfoTest(unittest.TestCase):
    @mock.patch('os.path.abspath')
    def test_ssh_session(self, mock_abspath):
        mock_abspath.side_effect = ["pub_path", "priv_path", "cert_path", "client_path", "proxy_path", "cred_path"]
        expected_abspath_calls = [
            mock.call("pub"),
            mock.call("priv"),
            mock.call("cert"),
            mock.call("client/folder"),
            mock.call("proxy/path"),
            mock.call("cred/path")
        ]
        session = ssh_info.SSHSession("rg", "vm", "ip", "pub", "priv", False, "user", "cert", "port", "client/folder", ['-v', '-E', 'path'], False, 'arc', 'proxy/path', 'cred/path', True, False)
        mock_abspath.assert_has_calls(expected_abspath_calls)
        self.assertEqual(session.resource_group_name, "rg")
        self.assertEqual(session.vm_name, "vm")
        self.assertEqual(session.ip, "ip")
        self.assertEqual(session.public_key_file, "pub_path")
        self.assertEqual(session.private_key_file, "priv_path")
        self.assertEqual(session.use_private_ip, False)
        self.assertEqual(session.local_user, "user")
        self.assertEqual(session.port, "port")
        self.assertEqual(session.ssh_args, ['-v', '-E', 'path'])
        self.assertEqual(session.cert_file, "cert_path")
        self.assertEqual(session.ssh_client_folder, "client_path")
        self.assertEqual(session.ssh_proxy_folder, "proxy_path")
        self.assertEqual(session.credentials_folder, "cred_path")
        self.assertEqual(session.relay_info, None)
        self.assertEqual(session.resource_type, "arc")
        self.assertEqual(session.proxy_path, None)
        self.assertEqual(session.delete_credentials, False)
        self.assertEqual(session.winrdp, True)
        self.assertEqual(session.yes_without_prompt, False)

    def test_ssh_session_get_host(self):
        session = ssh_info.SSHSession(None, None, "ip", None, None, False, "user", None, None, None, [], False, "Microsoft.Compute/virtualMachines", None, None, False, False)
        self.assertEqual("ip", session.get_host())
        session = ssh_info.SSHSession("rg", "vm", None, None, None, False, "user", None, None, None, [], False, "Microsoft.HybridCompute/machines", None, None, True, False)
        self.assertEqual("vm", session.get_host())

    @mock.patch('os.path.abspath')
    def test_ssh_session_build_args_compute(self, mock_abspath):
        mock_abspath.side_effect = ["pub_path", "priv_path", "cert_path", "client_path"]
        session = ssh_info.SSHSession("rg", "vm", "ip", "pub", "priv", False, "user", "cert", "port", "client/folder", [], None, "Microsoft.Compute/virtualMachines", None, None, False, False)
        self.assertEqual(["-i", "priv_path", "-o", "CertificateFile=\"cert_path\"", "-p", "port"], session.build_args())

    @mock.patch('os.path.abspath')
    def test_ssh_session_build_args_hyvridcompute(self, mock_abspath):
        mock_abspath.side_effect = ["pub_path", "priv_path", "cert_path", "client_path"]
        session = ssh_info.SSHSession("rg", "vm", "ip", "pub", "priv", False, "user", "cert", "port", "client/folder", [], None, "Microsoft.HybridCompute/machines", None, None, True, False)
        session.proxy_path = "proxy_path"
        self.assertEqual(["-o", "ProxyCommand=\"proxy_path\" -p port", "-i", "priv_path", "-o", "CertificateFile=\"cert_path\""], session.build_args())

    @mock.patch('os.path.abspath')
    def test_config_session(self, mock_abspath):
        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path", "proxy_path", "cred_path"]
        expected_abspath_calls = [
            mock.call("config"),
            mock.call("pub"),
            mock.call("priv"),
            mock.call("cert"),
            mock.call("client"),
            mock.call("proxy"),
            mock.call("cred")
        ]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", "port", "arc", "cred", "proxy", "client", False)
        mock_abspath.assert_has_calls(expected_abspath_calls)
        self.assertEqual(session.config_path, "config_path")
        self.assertEqual(session.resource_group_name, "rg")
        self.assertEqual(session.vm_name, "vm")
        self.assertEqual(session.ip, "ip")
        self.assertEqual(session.public_key_file, "pub_path")
        self.assertEqual(session.private_key_file, "priv_path")
        self.assertEqual(session.use_private_ip, False)
        self.assertEqual(session.overwrite, False)
        self.assertEqual(session.local_user, "user")
        self.assertEqual(session.port, "port")
        self.assertEqual(session.cert_file, "cert_path")
        self.assertEqual(session.ssh_client_folder, "client_path")
        self.assertEqual(session.resource_type, "arc")
        self.assertEqual(session.proxy_path, None)
        self.assertEqual(session.relay_info, None)
        self.assertEqual(session.relay_info_path, None)
        self.assertEqual(session.ssh_proxy_folder, "proxy_path")
        self.assertEqual(session.credentials_folder, "cred_path")
        self.assertEqual(session.yes_without_prompt, False)

    @mock.patch('os.path.abspath')
    def test_get_rg_and_vm_entry(self, mock_abspath):
        expected_lines_aad = [
            "Host rg-vm",
            "\tUser user",
            "\tHostName ip",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tPort port",
        ]
        expected_lines_local_user = [
            "Host rg-vm-user",
            "\tUser user",
            "\tHostName ip",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tPort port",
        ]
        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path", "proxy_path", "cred_path"]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", "port", "compute", "cred", "proxy", "client", False)

        self.assertEqual(session._get_rg_and_vm_entry(True), expected_lines_aad)
        self.assertEqual(session._get_rg_and_vm_entry(False), expected_lines_local_user)

    @mock.patch('os.path.abspath')
    def test_get_ip_entry(self, mock_abspath):
        expected_lines_aad = [
            "Host ip",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\""
        ]
        expected_lines_local_user = [
            "Host ip-user",
            "\tHostName ip",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\""
        ]

        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path", "cred_folder"]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", None, "compute", "cred", None, "client/folder", False)

        self.assertEqual(session._get_ip_entry(True), expected_lines_aad)
        self.assertEqual(session._get_ip_entry(False), expected_lines_local_user)

    @mock.patch('os.path.abspath')
    def test_get_arc_entry(self, mock_abspath):
        expected_lines_aad = [
            "Host rg-vm",
            "\tHostName vm",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tProxyCommand \"proxy_path\" -r \"relay_info_path\" -p port"
        ]

        expected_lines_local_user = [
            "Host rg-vm-user",
            "\tHostName vm",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tProxyCommand \"proxy_path\" -r \"relay_info_path\" -p port"
        ]

        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path", "cred_folder"]
        session = ssh_info.ConfigSession("config", "rg", "vm", None, "pub", "priv", False, False, "user", "cert", "port", "arc", "cred", None, "client/folder", False)
        session.proxy_path = "proxy_path"
        session.relay_info_path = "relay_info_path"
        self.assertEqual(session._get_arc_entry(True), expected_lines_aad)
        self.assertEqual(session._get_arc_entry(False), expected_lines_local_user)

    @mock.patch('os.path.abspath')
    def test_get_config_text_compute(self, mock_abspath):
        expected_lines_aad = [
            "",
            "Host rg-vm",
            "\tUser user",
            "\tHostName ip",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tPort port",
            "Host ip",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tPort port",
        ]

        expected_lines_local_user = [
            "",
            "Host rg-vm-user",
            "\tUser user",
            "\tHostName ip",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tPort port",
            "Host ip-user",
            "\tHostName ip",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tPort port",
        ]

        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path", "cred_path"]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", "port", "compute", "cred", None, "client/folder", False)

        self.assertEqual(session.get_config_text(True), expected_lines_aad)
        self.assertEqual(session.get_config_text(False), expected_lines_local_user)

    @mock.patch('os.path.abspath')
    @mock.patch.object(ssh_info.ConfigSession, '_create_relay_info_file')
    def test_get_config_text_arc(self, create_file, mock_abspath):
        create_file.return_value = "relay_info_path"
        expected_lines_aad = [
            "",
            "Host rg-vm",
            "\tHostName vm",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tProxyCommand \"proxy_path\" -r \"relay_info_path\""
        ]

        expected_lines_local_user = [
            "",
            "Host rg-vm-user",
            "\tHostName vm",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tProxyCommand \"proxy_path\" -r \"relay_info_path\""
        ]

        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path", "cred_path"]
        session = ssh_info.ConfigSession("config", "rg", "vm", None, "pub", "priv", False, False, "user", "cert", None, "Microsoft.HybridCompute/machines", "cred", None, "client/folder", False)
        session.proxy_path = "proxy_path"
        self.assertEqual(session.get_config_text(True), expected_lines_aad)
        self.assertEqual(session.get_config_text(False), expected_lines_local_user)


if __name__ == '__main__':
    unittest.main()
