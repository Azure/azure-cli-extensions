# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):

    with self.argument_context('ssh vm') as c:
        c.argument('vm_name', options_list=['--vm-name', '--name', '-n'], help='The name of the VM')
        c.argument('ssh_ip', options_list=['--ip', '--hostname'],
                   help='The public (or reachable private) IP address (or hostname) of the VM')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'], help='The RSA private key file path')
        c.argument('use_private_ip', options_list=['--prefer-private-ip'],
                   help='Will prefer private IP.  Requires connectivity to the private IP.')
        c.argument('port', options_list=['--port'], help='SSH port')
        c.positional('ssh_args', nargs='*', help='Additional arguments passed to OpenSSH')

    with self.argument_context('ssh config') as c:
        c.argument('config_path', options_list=['--file', '-f'], help='The file path to write the SSH config to')
        c.argument('vm_name', options_list=['--vm-name', '--name', '-n'], help='The name of the VM')
        c.argument('ssh_ip', options_list=['--ip'], help='The public IP address (or hostname) of the VM')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'], help='The RSA private key file path')
        c.argument('use_private_ip', options_list=['--prefer-private-ip'],
                   help='Will use a private IP if available. By default only public IPs are used.')
        c.argument('overwrite', action='store_true', options_list=['--overwrite'],
                   help='Overwrites the config file if this flag is set')
        c.argument('credentials_folder', options_list=['--credentials-destination-folder'],
                   help='Folder where credentials will be stored.')


    with self.argument_context('ssh cert') as c:
        c.argument('cert_path', options_list=['--file', '-f'],
                   help='The file path to write the SSH cert to, defaults to public key path with -aadcert.pub appened')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
