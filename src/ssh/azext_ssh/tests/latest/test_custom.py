# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
from azure.cli.core import azclierror
from unittest import mock
import unittest


from azext_ssh import custom
from azext_ssh import ssh_info
from azext_ssh import ssh_utils


class SshCustomCommandTest(unittest.TestCase):
    '''
    @mock.patch('azext_ssh.custom._do_ssh_op')
    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('azext_ssh.ssh_info.SSHSession')
    def test_ssh_vm(self, mock_info, mock_assert, mock_do_op):      
        cmd = mock.Mock()

        cmd.cli_ctx.data = {'safe_params': []}
        
        custom.ssh_vm(cmd, "rg", "vm", "ip", "public", "private", False, "username", "cert", "port", "ssh_folder", ['-vvv'])

        mock_info.assert_called_once_with("rg", "vm", "ip", "public", "private", False, "username", "cert", "port", "ssh_folder", ['-vvv'])
        mock_assert.assert_called_once_with("rg", "vm", "ip", "cert", "username")
        mock_do_op.assert_called_once_with(cmd, mock.ANY, None, ssh_utils.start_ssh_connection)

    @mock.patch('azext_ssh.custom._do_ssh_op')
    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('azext_ssh.ssh_info.SSHSession')
    def test_ssh_vm_debug(self, mock_info, mock_assert, mock_do_op):      
        cmd = mock.Mock()

        cmd.cli_ctx.data = {'safe_params': ['--debug']}
        
        custom.ssh_vm(cmd, "rg", "vm", "ip", "public", "private", False, "username", "cert", "port", "ssh_folder", [])

        mock_info.assert_called_once_with("rg", "vm", "ip", "public", "private", False, "username", "cert", "port", "ssh_folder", ['-v'])
        mock_assert.assert_called_once_with("rg", "vm", "ip", "cert", "username")
        mock_do_op.assert_called_once_with(cmd, mock.ANY, None, ssh_utils.start_ssh_connection)

    @mock.patch('azext_ssh.custom._do_ssh_op')
    @mock.patch('azext_ssh.ssh_utils.write_ssh_config')
    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.dirname')
    @mock.patch('os.path.join')
    @mock.patch('azext_ssh.ssh_info.ConfigSession')
    def test_ssh_config(self, mock_info, mock_join, mock_dirname, mock_isdir, mock_assert, mock_ssh_utils, mock_do_op):
        cmd = mock.Mock()
        mock_dirname.return_value = "configdir"
        mock_isdir.return_value = True
        mock_join.side_effect = ['az_ssh_config/rg-vm', 'path/to/az_ssh_config/rg-vm']

        custom.ssh_config(cmd, "path/to/file", "rg", "vm", "ip", "public", "private", False, False, "username", "cert", "port", None, "client/folder")

        mock_info.assert_called_once_with("path/to/file", "rg", "vm", "ip", "public", "private", False, False, "username", "cert", "port", "client/folder")
        mock_assert.assert_called_once_with("rg", "vm", "ip", "cert", "username")
        mock_do_op.assert_called_once_with(cmd, mock.ANY, 'path/to/az_ssh_config/rg-vm', ssh_utils.write_ssh_config)

    def test_ssh_cert_no_args(self):
        cmd = mock.Mock()
        self.assertRaises(
            azclierror.RequiredArgumentMissingError, custom.ssh_cert, cmd)
    
    @mock.patch('os.path.isdir')
    def test_ssh_cert_cert_file_missing(self, mock_isdir):
        cmd = mock.Mock()
        mock_isdir.return_value = False
        self.assertRaises(
            azclierror.InvalidArgumentValueError, custom.ssh_cert, cmd, cert_path="cert")

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.custom._get_and_write_certificate')
    def test_ssh_cert(self, mock_write_cert, mock_get_keys, mock_abspath, mock_isdir):
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = ['/pubkey/path', '/cert/path', '/client/path']
        mock_get_keys.return_value = "pubkey", "privkey", False
        mock_write_cert.return_value = "cert", "username"
        
        custom.ssh_cert(cmd, "cert", "pubkey", "ssh/folder")

        mock_get_keys.assert_called_once_with('/pubkey/path', None, None, '/client/path')
        mock_write_cert.assert_called_once_with(cmd, 'pubkey', '/cert/path', '/client/path')

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.abspath')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.custom._get_and_write_certificate')
    def test_ssh_cert(self, mock_write_cert, mock_get_keys, mock_abspath, mock_isdir):
        cmd = mock.Mock()
        mock_isdir.return_value = True
        mock_abspath.side_effect = ['/pubkey/path', '/cert/path', '/client/path']
        mock_get_keys.return_value = "pubkey", "privkey", False
        mock_write_cert.return_value = "cert", "username"
        
        custom.ssh_cert(cmd, "cert", "pubkey", "ssh/folder")

        mock_get_keys.assert_called_once_with('/pubkey/path', None, None, '/client/path')
        mock_write_cert.assert_called_once_with(cmd, 'pubkey', '/cert/path', '/client/path')

    @mock.patch('azext_ssh.ssh_utils.get_ssh_cert_principals')
    @mock.patch('os.path.join')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    @mock.patch('azext_ssh.custom._get_modulus_exponent')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_ssh.custom._write_cert_file')
    def test_do_ssh_op_aad_user(self, mock_write_cert, mock_ssh_creds, mock_get_mod_exp, mock_ip,
                       mock_check_files, mock_join, mock_principal):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        cmd.cli_ctx.cloud = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"

        op_info = mock.Mock()
        op_info.ip = "1.2.3.4"
        op_info.public_key_file = "publicfile"
        op_info.private_key_file = "privatefile"
        op_info.use_private_ip = False
        op_info.local_user = None
        op_info.cert_file = None
        op_info.ssh_client_folder = "/client/folder"

        mock_op = mock.Mock()
        mock_check_files.return_value = "public", "private", False
        mock_principal.return_value = ["username"]
        mock_get_mod_exp.return_value = "modulus", "exponent"
        profile = mock_ssh_creds.return_value
        profile._adal_cache = True
        profile.get_msal_token.return_value = "username", "certificate"
        mock_join.return_value = "public-aadcert.pub"

        custom._do_ssh_op(cmd, op_info, "cred/folder", mock_op)

        mock_check_files.assert_called_once_with("publicfile", "privatefile", "cred/folder", "/client/folder")
        mock_ip.assert_not_called()
        mock_get_mod_exp.assert_called_once_with("public")
        mock_write_cert.assert_called_once_with("certificate", "public-aadcert.pub")
        mock_op.assert_called_once_with(op_info, False, True)
    
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    def test_do_ssh_op_local_user(self, mock_ip, mock_check_files):
        cmd = mock.Mock()
        mock_op = mock.Mock()
        mock_ip.return_value = "1.2.3.4"

        op_info = mock.Mock()
        op_info.resource_group_name = "rg"
        op_info.vm_name = "vm"
        op_info.ip = None
        op_info.public_key_file = "publicfile"
        op_info.private_key_file = "privatefile"
        op_info.use_private_ip = False
        op_info.local_user = "username"
        op_info.certificate = "cert"
        op_info.ssh_client_folder = "/client/folder"        

        custom._do_ssh_op(cmd, op_info, "/cred/folder", mock_op)

        mock_check_files.assert_not_called()
        mock_ip.assert_called_once_with(cmd, "rg", "vm", False)
        mock_op.assert_called_once_with(op_info, False, False)

    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    def test_do_ssh_op_no_public_ip(self, mock_ip, mock_check_files):
        cmd = mock.Mock()
        mock_op = mock.Mock()
        mock_ip.return_value = None

        op_info = mock.Mock()
        op_info.vm_name = "vm"
        op_info.resource_group_name = "rg"
        op_info.ip = None
        op_info.use_private_ip = False

        self.assertRaises(
            azclierror.ResourceNotFoundError, custom._do_ssh_op, cmd, op_info, "/cred/folder", mock_op)

        mock_check_files.assert_not_called()
        mock_ip.assert_called_once_with(cmd, "rg", "vm", False)
        mock_op.assert_not_called()

    def test_assert_args_no_ip_or_vm(self):
        self.assertRaises(azclierror.RequiredArgumentMissingError, custom._assert_args, None, None, None, None, None)

    def test_assert_args_vm_rg_mismatch(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, "rg", None, None, None, None)
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, "vm", None, None, None)

    def test_assert_args_ip_with_vm_or_rg(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, "vm", "ip", None, None)
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, "rg", "vm", "ip", None, None)
    
    def test_assert_args_cert_with_no_user(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, None, "ip", "certificate", None)

    @mock.patch('os.path.isfile')
    def test_assert_args_invalid_cert_filepath(self, mock_is_file):
        mock_is_file.return_value = False
        self.assertRaises(azclierror.FileOperationError, custom._assert_args, 'rg', 'vm', None, 'cert_path', 'username')
 
    @mock.patch('azext_ssh.ssh_utils.create_ssh_keyfile')
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    def test_check_or_create_public_private_files_defaults(self, mock_join, mock_isfile, mock_temp, mock_create):
        mock_isfile.return_value = True
        mock_temp.return_value = "/tmp/aadtemp"
        mock_join.side_effect = ['/tmp/aadtemp/id_rsa.pub', '/tmp/aadtemp/id_rsa']

        public, private, delete_key = custom._check_or_create_public_private_files(None, None, None)

        self.assertEqual('/tmp/aadtemp/id_rsa.pub', public)
        self.assertEqual('/tmp/aadtemp/id_rsa', private)
        self.assertEqual(True, delete_key)
        mock_join.assert_has_calls([
            mock.call("/tmp/aadtemp", "id_rsa.pub"),
            mock.call("/tmp/aadtemp", "id_rsa")
        ])
        mock_isfile.assert_has_calls([
            mock.call('/tmp/aadtemp/id_rsa.pub'),
            mock.call('/tmp/aadtemp/id_rsa')
        ])
        mock_create.assert_has_calls([
            mock.call('/tmp/aadtemp/id_rsa', None)
        ])

    @mock.patch('azext_ssh.ssh_utils.create_ssh_keyfile')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    def test_check_or_create_public_private_files_defaults_with_cred_folder(self,mock_join, mock_isfile, mock_isdir, mock_create):
        mock_isfile.return_value = True
        mock_isdir.return_value = True
        mock_join.side_effect = ['/cred/folder/id_rsa.pub', '/cred/folder/id_rsa']
        public, private, delete_key = custom._check_or_create_public_private_files(None, None, '/cred/folder', '/ssh/client')
        self.assertEqual('/cred/folder/id_rsa.pub', public)
        self.assertEqual('/cred/folder/id_rsa', private)
        self.assertEqual(True, delete_key)
        mock_join.assert_has_calls([
            mock.call("/cred/folder", "id_rsa.pub"),
            mock.call("/cred/folder", "id_rsa")
        ])
        mock_isfile.assert_has_calls([
            mock.call('/cred/folder/id_rsa.pub'),
            mock.call('/cred/folder/id_rsa')
        ])
        mock_create.assert_has_calls([
            mock.call('/cred/folder/id_rsa', '/ssh/client')
        ])
    
    @mock.patch('os.path.isfile')
    def test_check_or_create_public_private_files_no_public(self, mock_isfile):
        mock_isfile.side_effect = [False]
        self.assertRaises(
            azclierror.FileOperationError, custom._check_or_create_public_private_files, "public", None, None)

        mock_isfile.assert_called_once_with("public")

    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    def test_check_or_create_public_private_files_no_private(self, mock_join, mock_isfile):
        mock_isfile.side_effect = [True, False]

        self.assertRaises(
            azclierror.FileOperationError, custom._check_or_create_public_private_files, "public", "private", None)

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

        mock_open.assert_called_once_with("publickey-aadcert.pub", 'w', encoding='utf-8')
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
        mock_open.assert_called_once_with('file', 'r', encoding='utf-8')
        mock_parser.return_value.parse.assert_called_once_with('publickey')

    @mock.patch('os.path.isfile')
    def test_get_modulus_exponent_file_not_found(self, mock_isfile):
        mock_isfile.return_value = False

        self.assertRaises(azclierror.FileOperationError, custom._get_modulus_exponent, 'file')
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

        self.assertRaises(azclierror.FileOperationError, custom._get_modulus_exponent, 'file')
    '''

if __name__ == '__main__':
    unittest.main()
