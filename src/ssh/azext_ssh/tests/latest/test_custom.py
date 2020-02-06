# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import profiles
import io
from knack import util
import mock
from msrestazure import azure_exceptions
import paramiko
import unittest

from azext_ssh import custom

class SshCustomCommandTest(unittest.TestCase):

    @mock.patch('azext_ssh.custom._get_ssh_ip')
    @mock.patch('azext_ssh.custom._get_modulus_exponent')
    @mock.patch('azext_ssh.custom._get_paramiko_key')
    @mock.patch('azext_ssh.custom.client_factory')
    @mock.patch('azext_ssh.custom.ssh_credential_factory')
    def test_ssh_vm_success_provided_keys(self, mock_ssh_factory,
        mock_client_factory, mock_get_key, mock_get_modexp, mock_get_ip):

        mock_compute = mock.Mock()
        mock_network = mock.Mock()
        def get_client(_, resource):
            if resource == profiles.ResourceType.MGMT_COMPUTE:
                return mock_compute
            elif resource == profiles.ResourceType.MGMT_NETWORK:
                return mock_network
            raise ValueError()

        mock_client_factory.get_mgmt_service_client.side_effect = get_client
        mock_get_ip.return_value = '1.2.3.4'
        mod, exp = (mock.Mock(), mock.Mock())
        mock_get_modexp.return_value = mod, exp

        cmd = mock.Mock()
        mock_ssh_client = mock.Mock()
        with mock.patch.object(paramiko, 'SSHClient') as mock_ssh_client_class:
            with mock.patch.object(paramiko, 'AutoAddPolicy') as mock_auto_add_policy:
                mock_ssh_client_class.return_value.__enter__.return_value = mock_ssh_client
                custom.ssh_vm(cmd, "rg", "vm", "public", "private")

        mock_client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        mock_client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
        mock_get_ip.assert_called_once_with("rg", "vm", mock_compute, mock_network)
        mock_get_modexp.assert_called_once_with("public")
        mock_get_key.assert_called_once_with("private")
        mock_ssh_factory.get_ssh_credentials.assert_called_once_with(cmd.cli_ctx, mod, exp)
        mock_get_key.return_value.load_certificate.assert_called_once_with(
            mock_ssh_factory.get_ssh_credentials.return_value.certificate
        )
        mock_ssh_client.set_missing_host_key_policy.assert_called_once_with(mock_auto_add_policy.return_value)
        mock_ssh_client.connect.assert_called_once_with('1.2.3.4',
            username=mock_ssh_factory.get_ssh_credentials.return_value.username,
            pkey=mock_get_key.return_value
        )
        
    @mock.patch('io.StringIO')
    @mock.patch('paramiko.RSAKey.from_private_key')
    @mock.patch('azext_ssh.custom.rsa_generator.RSAGenerator')
    @mock.patch('azext_ssh.custom._get_ssh_ip')
    @mock.patch('azext_ssh.custom.client_factory')
    @mock.patch('azext_ssh.custom.ssh_credential_factory')
    def test_ssh_vm_success_generated_keys(self, mock_ssh_factory,
        mock_client_factory, mock_get_ip, mock_rsa_generator, mock_from_pk, mock_io):

        mock_compute = mock.Mock()
        mock_network = mock.Mock()
        def get_client(_, resource):
            if resource == profiles.ResourceType.MGMT_COMPUTE:
                return mock_compute
            elif resource == profiles.ResourceType.MGMT_NETWORK:
                return mock_network
            raise ValueError()

        mock_client_factory.get_mgmt_service_client.side_effect = get_client
        mock_get_ip.return_value = '1.2.3.4'
        mock_generator = mock.Mock()
        mock_rsa_generator.return_value = mock_generator
        public, private = mock.Mock(), mock.Mock()
        mod, exp = mock.Mock(), mock.Mock()
        mock_generator.generate.return_value = public, private
        mock_rsa_generator.public_key_to_base64_modulus_exponent.return_value = mod, exp

        cmd = mock.Mock()
        mock_ssh_client = mock.Mock()
        with mock.patch.object(paramiko, 'SSHClient') as mock_ssh_client_class:
            with mock.patch.object(paramiko, 'AutoAddPolicy') as mock_auto_add_policy:
                mock_ssh_client_class.return_value.__enter__.return_value = mock_ssh_client
                custom.ssh_vm(cmd, "rg", "vm", None, None)

        mock_client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        mock_client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
        mock_get_ip.assert_called_once_with("rg", "vm", mock_compute, mock_network)
        mock_generator.generate.assert_called_once_with()
        mock_rsa_generator.public_key_to_base64_modulus_exponent.assert_called_once_with(public)
        mock_io.assert_called_once_with(private)
        mock_from_pk.assert_called_once_with(mock_io.return_value)
        mock_ssh_factory.get_ssh_credentials.assert_called_once_with(cmd.cli_ctx, mod, exp)
        mock_from_pk.return_value.load_certificate.assert_called_once_with(
            mock_ssh_factory.get_ssh_credentials.return_value.certificate
        )
        mock_ssh_client.set_missing_host_key_policy.assert_called_once_with(mock_auto_add_policy.return_value)
        mock_ssh_client.connect.assert_called_once_with('1.2.3.4',
            username=mock_ssh_factory.get_ssh_credentials.return_value.username,
            pkey=mock_from_pk.return_value
        )

    @mock.patch('azext_ssh.custom._get_ssh_ip')
    @mock.patch('azext_ssh.custom.client_factory')
    def test_ssh_vm_no_public_ip(self, mock_client_factory, mock_get_ip):
        mock_compute = mock.Mock()
        mock_network = mock.Mock()
        def get_client(_, resource):
            if resource == profiles.ResourceType.MGMT_COMPUTE:
                return mock_compute
            elif resource == profiles.ResourceType.MGMT_NETWORK:
                return mock_network
            raise ValueError()

        mock_client_factory.get_mgmt_service_client.side_effect = get_client
        mock_get_ip.return_value = None

        cmd = mock.Mock()
        self.assertRaises(util.CLIError, custom.ssh_vm,
            cmd, "rg", "vm", "public", "private")

        mock_client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        mock_client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_NETWORK)
        mock_get_ip.assert_called_once_with("rg", "vm", mock_compute, mock_network)

    def test_ssh_vm_private_key_no_public(self):
        cmd = mock.Mock()
        self.assertRaises(util.CLIError, custom.ssh_vm,
            cmd, "rg", "vm", None, "private")

    def test_ssh_vm_public_key_no_private(self):
        cmd = mock.Mock()
        self.assertRaises(util.CLIError, custom.ssh_vm,
            cmd, "rg", "vm", "public", None)

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

    @mock.patch('os.path.isfile')
    @mock.patch('paramiko.RSAKey.from_private_key')
    def test_get_paramiko_key_success(self, mock_from_pk, mock_isfile):
        mock_isfile.return_value = True

        private_key = custom._get_paramiko_key('file')

        self.assertEqual(private_key, mock_from_pk.return_value)
        mock_isfile.assert_called_once_with('file')
        mock_from_pk.assert_called_once_with('file')

    @mock.patch('os.path.isfile')
    def test_get_paramiko_key_file_not_found(self, mock_isfile):
        mock_isfile.return_value = False

        self.assertRaises(util.CLIError, custom._get_paramiko_key, 'file')

    @mock.patch('os.path.isfile')
    @mock.patch('getpass.getpass')
    @mock.patch('paramiko.RSAKey.from_private_key')
    def test_get_paramiko_key_with_password(self, mock_from_pk, mock_getpass, mock_isfile):
        mock_getpass.return_value = 'foo'
        mock_isfile.return_value = True
        mock_private_key = mock.Mock()
        mock_from_pk.side_effect = [paramiko.PasswordRequiredException, mock_private_key]
        key_file = 'file'

        private_key = custom._get_paramiko_key(key_file)

        self.assertEqual(mock_private_key, private_key)
        mock_from_pk.assert_any_call(key_file)
        mock_from_pk.assert_any_call(key_file, password='foo')
        mock_isfile.assert_called_once_with(key_file)
        mock_getpass.assert_called_once()

if __name__ == '__main__':
    unittest.main()
