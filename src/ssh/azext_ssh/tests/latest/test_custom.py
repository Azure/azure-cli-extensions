# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
from knack import util
import mock
import unittest

from azext_ssh import custom


class SshCustomCommandTest(unittest.TestCase):
    @mock.patch('azext_ssh.custom._do_ssh_op')
    @mock.patch('azext_ssh.custom.ssh_utils')
    def test_ssh_vm(self, mock_ssh_utils, mock_do_op):
        cmd = mock.Mock()
        custom.ssh_vm(cmd, "rg", "vm", "ip", "public", "private")

        mock_do_op.assert_called_once_with(
            cmd, "rg", "vm", "ip", "public", "private", mock_ssh_utils.start_ssh_connection)

    @mock.patch('azext_ssh.custom._do_ssh_op')
    @mock.patch('azext_ssh.ssh_utils.write_ssh_config')
    def test_ssh_config(self, mock_ssh_utils, mock_do_op):
        cmd = mock.Mock()

        def do_op_side_effect(cmd, resource_group, vm_name, ssh_ip, public_key_file, private_key_file, op_call):
            op_call(ssh_ip, "username", "cert_file", private_key_file)

        mock_do_op.side_effect = do_op_side_effect
        custom.ssh_config(cmd, "path/to/file", "rg", "vm", "ip", "public", "private")

        mock_ssh_utils.assert_called_once_with("path/to/file", "rg", "vm", "ip", "username", "cert_file", "private")

        mock_do_op.assert_called_once_with(
            cmd, "rg", "vm", "ip", "public", "private", mock.ANY)

    @mock.patch('os.path.join')
    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    @mock.patch('azext_ssh.custom._get_modulus_exponent')
    @mock.patch('azure.cli.core._profile.Profile.get_msal_token')
    @mock.patch('azext_ssh.custom._write_cert_file')
    def test_do_ssh_op(self, mock_write_cert, mock_ssh_creds, mock_get_mod_exp, mock_ip,
                       mock_check_files, mock_assert, mock_join):
        cmd = mock.Mock()
        mock_op = mock.Mock()
        mock_check_files.return_value = "public", "private"
        mock_get_mod_exp.return_value = "modulus", "exponent"
        mock_ssh_creds.return_value = "username", "certificate"
        mock_join.return_value = "public-aadcert.pub"

        custom._do_ssh_op(cmd, None, None, "1.2.3.4", "publicfile", "privatefile", mock_op)

        mock_assert.assert_called_once_with(None, None, "1.2.3.4")
        mock_check_files.assert_called_once_with("publicfile", "privatefile")
        mock_ip.assert_not_called()
        mock_get_mod_exp.assert_called_once_with("public")
        mock_write_cert.assert_called_once_with("certificate", "public-aadcert.pub")
        mock_op.assert_called_once_with(
            "1.2.3.4", "username", mock_write_cert.return_value, "private")

    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    @mock.patch('azext_ssh.custom._get_modulus_exponent')
    def test_do_ssh_op_no_public_ip(self, mock_get_mod_exp, mock_ip, mock_check_files, mock_assert):
        cmd = mock.Mock()
        mock_op = mock.Mock()
        mock_check_files.return_value = "public", "private"
        mock_get_mod_exp.return_value = "modulus", "exponent"
        mock_ip.return_value = None

        self.assertRaises(
            util.CLIError, custom._do_ssh_op, cmd, "rg", "vm", None,
            "publicfile", "privatefile", mock_op)

        mock_assert.assert_called_once_with("rg", "vm", None)
        mock_check_files.assert_called_once_with("publicfile", "privatefile")
        mock_ip.assert_called_once_with(cmd, "rg", "vm")

    def test_assert_args_no_ip_or_vm(self):
        self.assertRaises(util.CLIError, custom._assert_args, None, None, None)

    def test_assert_args_vm_rg_mismatch(self):
        self.assertRaises(util.CLIError, custom._assert_args, "rg", None, None)
        self.assertRaises(util.CLIError, custom._assert_args, None, "vm", None)

    def test_assert_args_ip_with_vm_or_rg(self):
        self.assertRaises(util.CLIError, custom._assert_args, None, "vm", "ip")
        self.assertRaises(util.CLIError, custom._assert_args, "rg", "vm", "ip")

    @mock.patch('azext_ssh.ssh_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    def test_check_or_create_public_private_files_defaults(self, mock_join, mock_isfile, mock_temp, mock_create):
        mock_isfile.return_value = True
        mock_temp.return_value = "/tmp/aadtemp"
        mock_join.side_effect = ['/tmp/aadtemp/id_rsa.pub', '/tmp/aadtemp/id_rsa']

        public, private = custom._check_or_create_public_private_files(None, None)

        self.assertEqual('/tmp/aadtemp/id_rsa.pub', public)
        self.assertEqual('/tmp/aadtemp/id_rsa', private)
        mock_join.assert_has_calls([
            mock.call("/tmp/aadtemp", "id_rsa.pub"),
            mock.call("/tmp/aadtemp", "id_rsa")
        ])
        mock_isfile.assert_has_calls([
            mock.call('/tmp/aadtemp/id_rsa.pub'),
            mock.call('/tmp/aadtemp/id_rsa')
        ])
        mock_create.assert_has_calls([
            mock.call('/tmp/aadtemp/id_rsa')
        ])

    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    def test_check_or_create_public_private_files_no_public(self, mock_join, mock_isfile):
        mock_isfile.side_effect = [False]
        self.assertRaises(
            util.CLIError, custom._check_or_create_public_private_files, "public", None)

        mock_isfile.assert_called_once_with("public")

    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    def test_check_or_create_public_private_files_no_private(self, mock_join, mock_isfile):
        mock_isfile.side_effect = [True, False]

        self.assertRaises(
            util.CLIError, custom._check_or_create_public_private_files, "public", "private")

        mock_join.assert_not_called()
        mock_isfile.assert_has_calls([
            mock.call("public"),
            mock.call("private")
        ])

    @mock.patch('builtins.open')
    def test_write_cert_file(self, mock_open):
        mock_file = mock.Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        custom._write_cert_file("cert", "publickey-aadcert.pub")

        mock_open.assert_called_once_with("publickey-aadcert.pub", 'w')
        mock_file.write.assert_called_once_with("ssh-rsa-cert-v01@openssh.com cert")

    @mock.patch('azext_ssh.rsa_parser.RSAParser')
    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    def test_get_modulus_exponent_success(self, mock_open, mock_isfile, mock_parser):
        mock_isfile.return_value = True
        mock_open.return_value = io.StringIO('publickey')

        modulus, exponent = custom._get_modulus_exponent('file')

        self.assertEqual(mock_parser.return_value.modulus, modulus)
        self.assertEqual(mock_parser.return_value.exponent, exponent)
        mock_isfile.assert_called_once_with('file')
        mock_open.assert_called_once_with('file', 'r')
        mock_parser.return_value.parse.assert_called_once_with('publickey')

    @mock.patch('os.path.isfile')
    def test_get_modulus_exponent_file_not_found(self, mock_isfile):
        mock_isfile.return_value = False

        self.assertRaises(util.CLIError, custom._get_modulus_exponent, 'file')
        mock_isfile.assert_called_once_with('file')

    @mock.patch('azext_ssh.rsa_parser.RSAParser')
    @mock.patch('os.path.isfile')
    @mock.patch('builtins.open')
    def test_get_modulus_exponent_parse_error(self, mock_open, mock_isfile, mock_parser):
        mock_isfile.return_value = True
        mock_open.return_value = io.StringIO('publickey')
        mock_parser_obj = mock.Mock()
        mock_parser.return_value = mock_parser_obj
        mock_parser_obj.parse.side_effect = ValueError

        self.assertRaises(util.CLIError, custom._get_modulus_exponent, 'file')


if __name__ == '__main__':
    unittest.main()
