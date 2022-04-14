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
        mock_abspath.side_effect = ["pub_path", "priv_path", "cert_path", "client_path"]
        expected_abspath_calls = [
            mock.call("pub"),
            mock.call("priv"),
            mock.call("cert"),
            mock.call("client/folder")
        ]
        session = ssh_info.SSHSession("rg", "vm", "ip", "pub", "priv", False, "user", "cert", "port", "client/folder", ['-v', '-E', 'path'])
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
    
    def test_ssh_session_get_host(self):
        session = ssh_info.SSHSession(None, None, "ip", None, None, False, "user", None, None, None, [])
        self.assertEqual("user@ip", session.get_host())
    
    @mock.patch('os.path.abspath')
    def test_ssh_session_build_args(self, mock_abspath):
        mock_abspath.side_effect = ["pub_path", "priv_path", "cert_path", "client_path"]
        session = ssh_info.SSHSession("rg", "vm", "ip", "pub", "priv", False, "user", "cert", "port", "client/folder", [])
        self.assertEqual(["-i", "priv_path", "-o", "CertificateFile=\"cert_path\"", "-p", "port"], session.build_args())
    
    @mock.patch('os.path.abspath')
    def test_config_session(self, mock_abspath):
        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path"]
        expected_abspath_calls = [
            mock.call("config"),
            mock.call("pub"),
            mock.call("priv"),
            mock.call("cert"),
            mock.call("client/folder")
        ]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", "port", "client/folder")
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
    
    @mock.patch('os.path.abspath')
    def test_get_rg_and_vm_entry(self, mock_abspath):
        expected_lines = [
            "Host rg-vm",
            "\tUser user",
            "\tHostName ip",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\"",
            "\tPort port",
        ]

        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path"]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", "port", "client/folder")

        self.assertEqual(session._get_rg_and_vm_entry(), expected_lines)
    
    @mock.patch('os.path.abspath')
    def test_get_ip_entry(self, mock_abspath):
        expected_lines = [
            "Host ip",
            "\tUser user",
            "\tCertificateFile \"cert_path\"",
            "\tIdentityFile \"priv_path\""
        ]

        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path"]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", None, "client/folder")

        self.assertEqual(session._get_ip_entry(), expected_lines)
    
    @mock.patch('os.path.abspath')
    def test_get_config_text(self, mock_abspath):
        expected_lines = [
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

        mock_abspath.side_effect = ["config_path", "pub_path", "priv_path", "cert_path", "client_path"]
        session = ssh_info.ConfigSession("config", "rg", "vm", "ip", "pub", "priv", False, False, "user", "cert", "port", "client/folder")

        self.assertEqual(session.get_config_text(), expected_lines)



if __name__ == '__main__':
    unittest.main()
