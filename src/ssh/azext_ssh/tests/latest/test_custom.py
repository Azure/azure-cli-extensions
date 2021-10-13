# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
from azure.cli.core import azclierror
from unittest import mock
import unittest
import functools

from azext_ssh import custom
from azext_ssh import ssh_utils
#from azext_ssh.custom import _do_ssh_op 

from azure.core.exceptions import ResourceNotFoundError


class SshCustomCommandTest(unittest.TestCase):
   
    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('azext_ssh.custom._do_ssh_op')
    @mock.patch('azext_ssh.custom._decide_op_call')
    def test_ssh_vm(self, mock_decide_op, mock_do_op, mock_assert_args):
        cmd = mock.Mock()
        op_call = functools.partial(ssh_utils.start_ssh_connection, ssh_client_path='path/to/ssh', ssh_args='ssh_args', delete_privkey=False)
        mock_decide_op.return_value = functools.partial(mock_do_op, resource_group_name='rg', vm_name='vm', is_arc=True, op_call=op_call)
        custom.ssh_vm(cmd, 'rg', 'vm', 'id', 'ip', 'public', 'private', False, 'user', 'cert', 'port', 'path/to/ssh', False, 'ssh_args')
        mock_decide_op.assert_called_once_with(cmd, 'rg', 'vm', 'id', 'ip', None, None, 'path/to/ssh', 'ssh_args', False)
        mock_assert_args.assert_called_once_with('rg', 'vm', 'ip', 'id', 'cert', 'user')
        mock_do_op.assert_called_once_with(cmd, 'ip', 'public', 'private', 'user', 'cert', 'port', False, resource_group_name='rg', vm_name='vm', is_arc=True, op_call=op_call)
    
    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('azext_ssh.custom._do_ssh_op')
    @mock.patch('azext_ssh.custom._decide_op_call')
    def test_ssh_config(self, mock_decide_op, mock_do_op, mock_assert_args):
        cmd = mock.Mock()
        op_call = functools.partial(ssh_utils.write_ssh_config, config_path='config path', overwrite=False, resource_group='rg')
        mock_decide_op.return_value = functools.partial(mock_do_op, resource_group_name='rg', vm_name='vm', is_arc=False, op_call=op_call)
        custom.ssh_config(cmd, 'config path', 'rg', 'vm', 'ip', 'id', 'public', 'private', False, False, 'user', 'cert', 'port')
        mock_decide_op.assert_called_once_with(cmd, 'rg', 'vm', 'id', 'ip', 'config path', False, None, None, None)
        mock_assert_args.assert_called_once_with('rg', 'vm', 'ip', 'id', 'cert', 'user')
        mock_do_op.assert_called_once_with(cmd, 'ip', 'public', 'private', 'user', 'cert', 'port', False, resource_group_name='rg', vm_name='vm', is_arc=False, op_call=op_call)

    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('msrestazure.tools.parse_resource_id')
    @mock.patch('azext_ssh.custom._do_ssh_op')
    def test_ssh_arc_resource_id(self, mock_do_op, mock_parse_id, mock_assert_args):
        cmd = mock.Mock()
        op_call = functools.partial(ssh_utils.start_ssh_connection, ssh_client_path="path_to_ssh", ssh_args="ssh_args", delete_privkey=False)
        mock_parse_id.return_value = {'subscription': '00000000-0000-0000-0000-000000000000',
                                      'resource_group': 'rg',
                                      'resource_namespace': 'Microsoft.HybridCompute',
                                      'resource_name': 'vm'}
        custom.ssh_arc(cmd, None, None, "id", "public", "private", "user", "certificate", "port", "path/to/ssh", False, "ssh_args")
        mock_assert_args.assert_called_once_with(None, None, None, "id", "certificate", "user")
        mock_parse_id.assert_called_once_with("id")
        # This doesn't work because there is no way to compare the functools objects
        #mock_do_op.assert_called_once_with(cmd, None, "public", "private", "user", "certificate", "port", False, "rg", "vm", op_call, True)
    
    @mock.patch('azext_ssh.custom._assert_args')
    @mock.patch('msrestazure.tools.parse_resource_id')
    def test_ssh_arc_invalid_resource_provider(self, mock_parse_id, mock_assert_args):
        cmd = mock.Mock()
        mock_parse_id.return_value = {'subscription': '00000000-0000-0000-0000-000000000000',
                                      'resource_group': 'rg',
                                      'resource_namespace': 'Microsoft.Compute',
                                      'resource_name': 'vm'}
        self.assertRaises(
            azclierror.InvalidArgumentValueError, custom.ssh_arc, cmd, None, None, "id", "public", "private", "user", "cert", "port", "path", False, "args")
        mock_assert_args.assert_called_once_with(None, None, None, "id", "cert", "user")
        mock_parse_id.assert_called_once_with("id")

    def test_decide_op_call_vm_with_ip(self):
        cmd = mock.Mock()
        expected_result = functools.partial(custom._do_ssh_op, resource_group_name=None, vm_name=None, is_arc=False,  
                                            op_call=functools.partial(ssh_utils.start_ssh_connection, ssh_client_path="path", ssh_args="args", delete_privkey=True))
        result = custom._decide_op_call(cmd, None, None, None, "ip", None, None, "path", "args", True)
        self.assertEqual(expected_result.func, result.func)
        self.assertEqual(expected_result.args, result.args)
        self.assertEqual(expected_result.keywords['resource_group_name'], result.keywords['resource_group_name'])
        self.assertEqual(expected_result.keywords['vm_name'], result.keywords['vm_name'])
        self.assertEqual(expected_result.keywords['is_arc'], result.keywords['is_arc'])
        self.assertEqual(expected_result.keywords['op_call'].func, result.keywords['op_call'].func)
        self.assertEqual(expected_result.keywords['op_call'].args, result.keywords['op_call'].args)
        self.assertEqual(expected_result.keywords['op_call'].keywords, result.keywords['op_call'].keywords)

    def test_decide_op_call_config_with_ip(self):
        cmd = mock.Mock()
        expected_result = functools.partial(custom._do_ssh_op, resource_group_name=None, vm_name=None, is_arc=False,  
                                            op_call=functools.partial(ssh_utils.write_ssh_config, config_path='config_path', overwrite=True, resource_group=None))
        result = custom._decide_op_call(cmd, None, None, None, "ip", 'config_path', True, None, None, False)
        self.assertEqual(expected_result.func, result.func)
        self.assertEqual(expected_result.args, result.args)
        self.assertEqual(expected_result.keywords['resource_group_name'], result.keywords['resource_group_name'])
        self.assertEqual(expected_result.keywords['vm_name'], result.keywords['vm_name'])
        self.assertEqual(expected_result.keywords['is_arc'], result.keywords['is_arc'])
        self.assertEqual(expected_result.keywords['op_call'].func, result.keywords['op_call'].func)
        self.assertEqual(expected_result.keywords['op_call'].args, result.keywords['op_call'].args)
        self.assertEqual(expected_result.keywords['op_call'].keywords, result.keywords['op_call'].keywords)
       
    @mock.patch('msrestazure.tools.parse_resource_id')
    def test_decide_op_call_invalid_resource_id(self, mock_parse_id):
        cmd = mock.Mock()
        mock_parse_id.return_value = {'subscription': '00000000-0000-0000-0000-000000000000', 'resource_group': 'rg', 'resource_name': 'vm'}
        self.assertRaises(
            azclierror.InvalidArgumentValueError, custom._decide_op_call, cmd, None, None, "id", None, None, False, None, None, False)
   
    @mock.patch('msrestazure.tools.parse_resource_id')
    def test_decide_op_call_vm_with_resource_id(self, mock_parse_id):
        cmd = mock.Mock()
        mock_parse_id.return_value = {'subscription': '00000000-0000-0000-0000-000000000000', 'resource_group': 'rg', 'resource_namespace': 'Microsoft.HybridCompute', 'resource_name': 'vm'}
        expected_result = functools.partial(custom._do_ssh_op, resource_group_name='rg', vm_name='vm', is_arc=True,  
                                            op_call=functools.partial(ssh_utils.start_ssh_connection, ssh_client_path='path', ssh_args='args', delete_privkey=False))
        result = custom._decide_op_call(cmd, None, None, 'id', None, None, False, 'path', 'args', False)
        mock_parse_id.assert_called_once_with('id')
        self.assertEqual(expected_result.func, result.func)
        self.assertEqual(expected_result.args, result.args)
        self.assertEqual(expected_result.keywords['resource_group_name'], result.keywords['resource_group_name'])
        self.assertEqual(expected_result.keywords['vm_name'], result.keywords['vm_name'])
        self.assertEqual(expected_result.keywords['is_arc'], result.keywords['is_arc'])
        self.assertEqual(expected_result.keywords['op_call'].func, result.keywords['op_call'].func)
        self.assertEqual(expected_result.keywords['op_call'].args, result.keywords['op_call'].args)
        self.assertEqual(expected_result.keywords['op_call'].keywords, result.keywords['op_call'].keywords)
    
    @mock.patch('msrestazure.tools.parse_resource_id')
    def test_decide_op_call_config_with_resource_id(self, mock_parse_id):
        cmd = mock.Mock()
        mock_parse_id.return_value = {'subscription': '00000000-0000-0000-0000-000000000000', 'resource_group': 'rg', 'resource_namespace': 'Microsoft.Compute', 'resource_name': 'vm'}
        expected_result = functools.partial(custom._do_ssh_op, resource_group_name='rg', vm_name='vm', is_arc=False,  
                                            op_call=functools.partial(ssh_utils.write_ssh_config, config_path='config path', overwrite=True, resource_group='rg'))
        result = custom._decide_op_call(cmd, None, None, 'id', None, 'config path', True, None, None, None)
        mock_parse_id.assert_called_once_with('id')
        self.assertEqual(expected_result.func, result.func)
        self.assertEqual(expected_result.args, result.args)
        self.assertEqual(expected_result.keywords['resource_group_name'], result.keywords['resource_group_name'])
        self.assertEqual(expected_result.keywords['vm_name'], result.keywords['vm_name'])
        self.assertEqual(expected_result.keywords['is_arc'], result.keywords['is_arc'])
        self.assertEqual(expected_result.keywords['op_call'].func, result.keywords['op_call'].func)
        self.assertEqual(expected_result.keywords['op_call'].args, result.keywords['op_call'].args)
        self.assertEqual(expected_result.keywords['op_call'].keywords, result.keywords['op_call'].keywords)

    @mock.patch('azext_ssh.custom._check_if_azure_vm')
    @mock.patch('azext_ssh.custom._check_if_arc_server')
    def test_decide_op_call_vm_with_name_and_resource_group_both_true(self, mock_check_arc, mock_check_az_vm):
        cmd = mock.Mock()
        mock_check_arc.return_value = True
        mock_check_az_vm.return_value = True
        self.assertRaises(
            azclierror.BadRequestError, custom._decide_op_call, cmd, 'rg', 'vm', None, None, None, False, None, None, False)
        mock_check_arc.assert_called_once_with(cmd, 'rg', 'vm')
        mock_check_az_vm.assert_called_once_with(cmd, 'rg', 'vm')
    
    @mock.patch('azext_ssh.custom._check_if_azure_vm')
    @mock.patch('azext_ssh.custom._check_if_arc_server')
    def test_decide_op_call_vm_with_name_and_resource_group_both_false(self, mock_check_arc, mock_check_az_vm):
        cmd = mock.Mock()
        mock_check_arc.return_value = False
        mock_check_az_vm.return_value = False
        from azure.core.exceptions import ResourceNotFoundError
        self.assertRaises(
            ResourceNotFoundError, custom._decide_op_call, cmd, "rg", "vm", None, None, 'config_path', True, None, None, None)
        mock_check_arc.assert_called_once_with(cmd, 'rg', 'vm')
        mock_check_az_vm.assert_called_once_with(cmd, 'rg', 'vm')

    @mock.patch('azext_ssh.custom._check_if_azure_vm')
    @mock.patch('azext_ssh.custom._check_if_arc_server')
    def test_decide_op_call_vm_with_name_and_resource_group(self, mock_check_arc, mock_check_az_vm):
        cmd = mock.Mock()
        mock_check_arc.return_value = False
        mock_check_az_vm.return_value = True
        expected_result = functools.partial(custom._do_ssh_op, resource_group_name='rg', vm_name='vm', is_arc=False,  
                                            op_call=functools.partial(ssh_utils.start_ssh_connection, ssh_client_path='path', ssh_args='args', delete_privkey=True))
        result = custom._decide_op_call(cmd, 'rg', 'vm', None, None, None, False, "path", "args", True)
        self.assertEqual(expected_result.func, result.func)
        self.assertEqual(expected_result.args, result.args)
        self.assertEqual(expected_result.keywords['resource_group_name'], result.keywords['resource_group_name'])
        self.assertEqual(expected_result.keywords['vm_name'], result.keywords['vm_name'])
        self.assertEqual(expected_result.keywords['is_arc'], result.keywords['is_arc'])
        self.assertEqual(expected_result.keywords['op_call'].func, result.keywords['op_call'].func)
        self.assertEqual(expected_result.keywords['op_call'].args, result.keywords['op_call'].args)
        self.assertEqual(expected_result.keywords['op_call'].keywords, result.keywords['op_call'].keywords)
        mock_check_arc.assert_called_once_with(cmd, 'rg', 'vm')
        mock_check_az_vm.assert_called_once_with(cmd, 'rg', 'vm')

    @mock.patch('azext_ssh.custom._check_if_azure_vm')
    @mock.patch('azext_ssh.custom._check_if_arc_server')
    def test_decide_op_call_config_with_name_and_resource_group(self, mock_check_arc, mock_check_az_vm):
        cmd = mock.Mock()
        mock_check_arc.return_value = True
        mock_check_az_vm.return_value = False   
        expected_result = functools.partial(custom._do_ssh_op, resource_group_name='rg', vm_name='vm', is_arc=True,  
                                            op_call=functools.partial(ssh_utils.write_ssh_config, config_path='config path', overwrite=True, resource_group='rg'))
        result = custom._decide_op_call(cmd, 'rg', 'vm', None, None, 'config path', True, None, None, False)
        self.assertEqual(expected_result.func, result.func)
        self.assertEqual(expected_result.args, result.args)
        self.assertEqual(expected_result.keywords['resource_group_name'], result.keywords['resource_group_name'])
        self.assertEqual(expected_result.keywords['vm_name'], result.keywords['vm_name'])
        self.assertEqual(expected_result.keywords['is_arc'], result.keywords['is_arc'])
        self.assertEqual(expected_result.keywords['op_call'].func, result.keywords['op_call'].func)
        self.assertEqual(expected_result.keywords['op_call'].args, result.keywords['op_call'].args)
        self.assertEqual(expected_result.keywords['op_call'].keywords, result.keywords['op_call'].keywords)
        mock_check_arc.assert_called_once_with(cmd, 'rg', 'vm')
        mock_check_az_vm.assert_called_once_with(cmd, 'rg', 'vm')

    def test_assert_args_no_ip_or_id_or_vm(self):
        self.assertRaises(azclierror.RequiredArgumentMissingError, custom._assert_args, None, None, None, None, None, None)

    def test_assert_args_vm_rg_mismatch(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, "rg", None, None, None, None, None)
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, "vm", None, None, None, None)

    def test_assert_args_ip_with_vm_or_rg(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, "vm", "ip", None, None, None)
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, "rg", None, "ip", None, None, None)
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, "rg", "vm", "ip", None, None, None)
    
    def test_assert_args_id_with_vm_or_rg(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, "vm", None, "id", None, None)
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, "rg", None, None, "id", None, None)
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, "rg", "vm", None, "id", None, None)

    def test_assert_args_id_with_ip(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, None, "ip", "id", None, None)
    
    def test_assert_args_cert_with_no_user(self):
        self.assertRaises(azclierror.MutuallyExclusiveArgumentError, custom._assert_args, None, None, "ip", None, "certificate", None)

    @mock.patch('os.path.isfile')
    def test_assert_args_invalid_cert_filepath(self, mock_is_file):
        mock_is_file.return_value = False
        self.assertRaises(azclierror.FileOperationError, custom._assert_args, 'rg', 'vm', None, None, 'cert_path', 'username')

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
            azclierror.FileOperationError, custom._check_or_create_public_private_files, "public", None)

        mock_isfile.assert_called_once_with("public")

    @mock.patch('os.path.isfile')
    @mock.patch('os.path.join')
    def test_check_or_create_public_private_files_no_private(self, mock_join, mock_isfile):
        mock_isfile.side_effect = [True, False]

        self.assertRaises(
            azclierror.FileOperationError, custom._check_or_create_public_private_files, "public", "private")

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

    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    @mock.patch('azext_ssh.ssh_utils.start_ssh_connection')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.custom._get_and_write_certificate')
    @mock.patch('azext_ssh.custom._arc_get_client_side_proxy')
    @mock.patch('azext_ssh.custom._arc_list_access_details')
    def test_do_ssh_op_ip_and_local_user_compute(self, mock_get_access, mock_get_proxy, mock_get_cert, mock_check_keys, mock_start_ssh, mock_get_ip):
        cmd = mock.Mock()
        custom._do_ssh_op(cmd, 'ip', 'public', 'private', 'user', 'cert', 'port', 'False', None, None, mock_start_ssh, False)
        mock_get_ip.assert_not_called()
        mock_get_cert.assert_not_called()
        mock_check_keys.assert_not_called()
        mock_get_access.assert_not_called()
        mock_get_proxy.assert_not_called()
        mock_start_ssh.assert_called_once_with(None, None, None, 'ip', 'user', 'cert', 'private', 'port', False)

    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    def test_do_ssh_op_with_no_ip(self, mock_get_ip):
        cmd = mock.Mock()
        mock_get_ip.return_value = None
        self.assertRaises(
            azclierror.ResourceNotFoundError, custom._do_ssh_op, cmd, None, 'public', 'private', 'user', 'cert', 'port', False, 'rg', 'vm', 'op_call', False)
        mock_get_ip.assert_called_once_with(cmd, 'rg', 'vm', False)
    
    @mock.patch('azext_ssh.ssh_utils.get_ssh_cert_principals')
    @mock.patch('os.path.join')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.ip_utils.get_ssh_ip')
    @mock.patch('azext_ssh.custom._get_modulus_exponent')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_ssh.custom._write_cert_file')
    @mock.patch('azext_ssh.ssh_utils.start_ssh_connection')
    def test_do_ssh_op_rg_and_vm_and_aad_user(self, mock_start_ssh, mock_write_cert, mock_ssh_creds, mock_get_mod_exp, mock_ip, mock_check_files, 
                                              mock_join, mock_principal):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        cmd.cli_ctx.cloud = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_check_files.return_value = "public", "private"
        mock_principal.return_value = ["username"]
        mock_get_mod_exp.return_value = "modulus", "exponent"
        profile = mock_ssh_creds.return_value
        profile._adal_cache = True
        profile.get_msal_token.return_value = "username", "certificate"
        mock_join.return_value = "public-aadcert.pub"
        mock_ip.return_value = 'ip'

        custom._do_ssh_op(cmd, None, "publicfile", "privatefile", None, None, "port", False, "rg", "vm", mock_start_ssh, False)

        mock_check_files.assert_called_once_with("publicfile", "privatefile")
        mock_ip.assert_called_once_with(cmd, 'rg', 'vm', False)
        mock_get_mod_exp.assert_called_once_with("public")
        mock_write_cert.assert_called_once_with("certificate", "public-aadcert.pub")
        mock_start_ssh.assert_called_once_with(None, None, 'vm', 'ip', 'username', 'public-aadcert.pub', 'private', 'port', False)

    @mock.patch('azext_ssh.custom._arc_get_client_side_proxy')
    @mock.patch('azext_ssh.custom._arc_list_access_details')
    @mock.patch('azext_ssh.ssh_utils.start_ssh_connection')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.custom._get_and_write_certificate')
    def test_do_ssh_arc_op_local_user(self, mock_get_cert, mock_check_keys, mock_start_ssh, mock_get_relay_info, mock_get_proxy):
        cmd = mock.Mock()
        mock_get_proxy.return_value = '/path/to/proxy'
        mock_get_relay_info.return_value = 'relay'
        custom._do_ssh_op(cmd, None, 'public', 'private', 'user', 'cert', 'port', False, 'rg', 'vm', mock_start_ssh, True)
        mock_get_proxy.assert_called_once_with()
        mock_get_relay_info.assert_called_once_with(cmd, 'rg', 'vm')
        mock_start_ssh.assert_called_once_with('relay', '/path/to/proxy', 'vm', None, 'user', 'cert', 'private', 'port', True)
        mock_get_cert.assert_not_called()
        mock_check_keys.assert_not_called()
    
    @mock.patch('azext_ssh.custom._arc_get_client_side_proxy')
    @mock.patch('azext_ssh.custom._arc_list_access_details')
    @mock.patch('azext_ssh.ssh_utils.get_ssh_cert_principals')
    @mock.patch('os.path.join')
    @mock.patch('azext_ssh.custom._check_or_create_public_private_files')
    @mock.patch('azext_ssh.custom._get_modulus_exponent')
    @mock.patch('azure.cli.core._profile.Profile')
    @mock.patch('azext_ssh.custom._write_cert_file')
    @mock.patch('azext_ssh.ssh_utils.start_ssh_connection')
    def test_do_ssh_arc_op_aad_user(self, mock_start_ssh, mock_write_cert, mock_ssh_creds, mock_get_mod_exp, mock_check_files, 
                                    mock_join, mock_principal, mock_get_relay_info, mock_get_proxy):

        mock_get_proxy.return_value = '/path/to/proxy'
        mock_get_relay_info.return_value = 'relay'
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()
        cmd.cli_ctx.cloud = mock.Mock()
        cmd.cli_ctx.cloud.name = "azurecloud"
        mock_check_files.return_value = "public", "private"
        mock_principal.return_value = ["username"]
        mock_get_mod_exp.return_value = "modulus", "exponent"
        profile = mock_ssh_creds.return_value
        profile._adal_cache = True
        profile.get_msal_token.return_value = "username", "certificate"
        mock_join.return_value = "public-aadcert.pub"

        custom._do_ssh_op(cmd, None, 'publicfile', 'privatefile', None, None, 'port', False, 'rg', 'vm', mock_start_ssh, True)

        mock_check_files.assert_called_once_with("publicfile", "privatefile")
        mock_get_mod_exp.assert_called_once_with("public")
        mock_write_cert.assert_called_once_with("certificate", "public-aadcert.pub")
        mock_get_proxy.assert_called_once_with()
        mock_get_relay_info.assert_called_once_with(cmd, 'rg', 'vm')
        mock_start_ssh.assert_called_once_with('relay', '/path/to/proxy', 'vm', None, 'username', 'public-aadcert.pub', 'private', 'port', True)

    if __name__ == '__main__':
        unittest.main()
