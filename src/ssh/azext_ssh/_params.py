# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=too-many-statements
def load_arguments(self, _):

    with self.argument_context('ssh vm') as c:
        c.argument('vm_name', options_list=['--vm-name', '--name', '-n'], help='The name of the VM')
        c.argument('ssh_ip', options_list=['--ip', '--hostname'],
                   help='The public (or reachable private) IP address (or hostname) of the VM')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'], help='The RSA private key file path')
        c.argument('use_private_ip', options_list=['--prefer-private-ip'],
                   help='Will prefer private IP.  Requires connectivity to the private IP.')
        c.argument('local_user', options_list=['--local-user'],
                   help='The username for a local user')
        c.argument('cert_file', options_list=['--certificate-file', '-c'],
                   help='Path to a certificate file used for authentication when using local user credentials.')
        c.argument('port', options_list=['--port'], help='SSH port')
        c.argument('resource_type', options_list=['--resource-type'],
                   help=('Resource type should be either Microsoft.Compute/virtualMachines, '
                         'Microsoft.HybridCompute/machines, '
                         'or Microsoft.ConnectedVMwareSphere/virtualMachines.'),
                   completer=['Microsoft.Compute/virtualMachines', 'Microsoft.HybridCompute/machines',
                              'Microsoft.ConnectedVMwareSphere/virtualMachines'])
        c.argument('ssh_client_folder', options_list=['--ssh-client-folder'],
                   help='Folder path that contains ssh executables (ssh.exe, ssh-keygen.exe, etc). '
                   'Default to ssh pre-installed if not provided.')
        c.argument('delete_credentials', options_list=['--force-delete-credentials', '--delete-private-key'],
                   help=('This is an internal argument. This argument is used by Azure Portal to '
                         'provide a one click SSH login experience in Cloud shell.'),
                   deprecate_info=c.deprecate(hide=True), action='store_true')
        c.argument('ssh_proxy_folder', options_list=['--ssh-proxy-folder'],
                   help=('Path to the folder where the ssh proxy should be saved. '
                         'Default to .clientsshproxy folder in user\'s home directory if not provided.'))
        c.argument('winrdp', options_list=['--winrdp', '--rdp'], help=('Start RDP connection over SSH.'),
                   action='store_true')
        c.argument('yes_without_prompt', options_list=['--yes-without-prompt', '--yes', '-y'],
                   help='Update service configuration without prompting user')
        c.positional('ssh_args', nargs='*', help='Additional arguments passed to OpenSSH')

    with self.argument_context('ssh config') as c:
        c.argument('config_path', options_list=['--file', '-f'], help='The file path to write the SSH config to')
        c.argument('vm_name', options_list=['--vm-name', '--name', '-n'], help='The name of the VM')
        c.argument('ssh_ip', options_list=['--ip'], help='The public IP address (or hostname) of the VM')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'], help='The RSA private key file path')
        c.argument('use_private_ip', options_list=['--prefer-private-ip'],
                   help='Will use a private IP if available. By default only public IPs are used.')
        c.argument('local_user', options_list=['--local-user'],
                   help='The username for a local user')
        c.argument('overwrite', action='store_true', options_list=['--overwrite'],
                   help='Overwrites the config file if this flag is set')
        c.argument('credentials_folder', options_list=['--keys-destination-folder', '--keys-dest-folder'],
                   help='Folder where new generated keys will be stored.')
        c.argument('port', options_list=['--port'], help='SSH Port')
        c.argument('resource_type', options_list=['--resource-type'],
                   help=('Resource type should be either Microsoft.Compute/virtualMachines, '
                         'Microsoft.HybridCompute/machines, '
                         'or Microsoft.ConnectedVMwareSphere/virtualMachines.'),
                   completer=['Microsoft.Compute/virtualMachines', 'Microsoft.HybridCompute/machines',
                              'Microsoft.ConnectedVMwareSphere/virtualMachines'])
        c.argument('cert_file', options_list=['--certificate-file', '-c'], help='Path to certificate file')
        c.argument('ssh_proxy_folder', options_list=['--ssh-proxy-folder'],
                   help=('Path to the folder where the ssh proxy should be saved. '
                         'Default to .clientsshproxy folder in user\'s home directory if not provided.'))
        c.argument('ssh_client_folder', options_list=['--ssh-client-folder'],
                   help='Folder path that contains ssh executables (ssh.exe, ssh-keygen.exe, etc). '
                   'Default to ssh pre-installed if not provided.')
        c.argument('yes_without_prompt', options_list=['--yes-without-prompt', '--yes', '-y'],
                   help='Update service configuration without prompting user')

    with self.argument_context('ssh cert') as c:
        c.argument('cert_path', options_list=['--file', '-f'],
                   help='The file path to write the SSH cert to, defaults to public key path with -aadcert.pub appened')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'],
                   help='The RSA public key file path. If not provided, '
                   'generated key pair is stored in the same directory as --file.')
        c.argument('ssh_client_folder', options_list=['--ssh-client-folder'],
                   help='Folder path that contains ssh executables (ssh.exe, ssh-keygen.exe, etc). '
                   'Default to ssh pre-installed if not provided.')

    with self.argument_context('ssh arc') as c:
        c.argument('vm_name', options_list=['--vm-name', '--name', '-n'], help='The name of the Arc Server')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'], help='The RSA public key file path')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'], help='The RSA private key file path')
        c.argument('local_user', options_list=['--local-user'],
                   help='The username for a local user')
        c.argument('cert_file', options_list=['--certificate-file', '-c'], help='Path to certificate file')
        c.argument('port', options_list=['--port'], help='Port to connect to on the remote host.')
        c.argument('resource_type', options_list=['--resource-type'],
                   help=('Resource type should be either Microsoft.HybridCompute/machines '
                         'or Microsoft.ConnectedVMwareSphere/virtualMachines.'),
                   completer=['Microsoft.HybridCompute/machines',
                              'Microsoft.ConnectedVMwareSphere/virtualMachines'])
        c.argument('ssh_client_folder', options_list=['--ssh-client-folder'],
                   help='Folder path that contains ssh executables (ssh.exe, ssh-keygen.exe, etc). '
                   'Default to ssh pre-installed if not provided.')
        c.argument('delete_credentials', options_list=['--force-delete-credentials', '--delete-private-key'],
                   help=('This is an internal argument. This argument is used by Azure Portal to '
                         'provide a one click SSH login experience in Cloud shell.'),
                   deprecate_info=c.deprecate(hide=True), action='store_true')
        c.argument('ssh_proxy_folder', options_list=['--ssh-proxy-folder'],
                   help=('Path to the folder where the ssh proxy should be saved. '
                         'Default to .clientsshproxy folder in user\'s home directory if not provided.'))
        c.argument('winrdp', options_list=['--winrdp', '--rdp'], help=('Start RDP connection over SSH.'),
                   action='store_true')
        c.argument('yes_without_prompt', options_list=['--yes-without-prompt', '--yes', '-y'],
                   help='Update service configuration without prompting user')
        c.positional('ssh_args', nargs='*', help='Additional arguments passed to OpenSSH')
