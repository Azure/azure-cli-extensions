# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):

    with self.argument_context('ssh vm') as c:
        c.argument('vm_name', options_list=['--vm-name', '-n'], help='The name of the VM')
        c.argument('ssh_ip', options_list=['--ip'], help='The public IP address (or hostname) of the VM')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'], help='The RSA private key file path')

    with self.argument_context('ssh config') as c:
        c.argument('config_path', options_list=['--file', '-f'], help='The file path to write the SSH config to')
        c.argument('vm_name', options_list=['--vm-name', '-n'], help='The name of the VM')
        c.argument('ssh_ip', options_list=['--ip'], help='The public IP address (or hostname) of the VM')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'], help='The RSA private key file path')

    with self.argument_context('ssh cert') as c:
        c.argument('cert_path', options_list=['--file', '-f'],
                   help='The file path to write the SSH cert to, defaults to public key path with -aadcert.pub appened')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
