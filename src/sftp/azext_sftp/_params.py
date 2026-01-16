# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):

    with self.argument_context('sftp cert') as c:
        c.argument('cert_path', options_list=['--file', '-f'],
                   help='The file path to write the SSH cert to, defaults to public key path with -aadcert.pub appended')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'],
                   help='The RSA public key file path. If not provided, '
                   'generated key pair is stored in the same directory as --file.')
        c.argument('ssh_client_folder', options_list=['--ssh-client-folder'],
                   help='Folder path that contains ssh executables (ssh-keygen, ssh). '
                   'Default to ssh executables in your PATH or C:\\Windows\\System32\\OpenSSH on Windows.')

    with self.argument_context('sftp connect') as c:
        c.argument('storage_account', options_list=['--storage-account', '-s'],
                   help='Azure Storage Account name for SFTP connection. Must have SFTP enabled.')
        c.argument('port', options_list=['--port'],
                   help='SFTP port. If not specified, uses SSH default port (typically 22).',
                   type=int)
        c.argument('cert_file', options_list=['--certificate-file', '-c'],
                   help='Path to SSH certificate file for authentication. '
                   'Must be generated with "az sftp cert" or compatible Azure AD certificate. '
                   'If not provided, certificate will be generated automatically.')
        c.argument('private_key_file', options_list=['--private-key-file', '-i'],
                   help='Path to RSA private key file. If provided without certificate, '
                   'a certificate will be generated automatically from this key.')
        c.argument('public_key_file', options_list=['--public-key-file', '-p'],
                   help='Path to RSA public key file. If provided without certificate, '
                   'a certificate will be generated automatically from this key.')
        c.argument('sftp_args', options_list=['--sftp-args'],
                   help='Additional arguments to pass to the SFTP client. '
                   'Example: "-v" for verbose output, "-b batchfile.txt" for batch commands, '
                   '"-o ConnectTimeout=30" for custom timeout.')
        c.argument('ssh_client_folder', options_list=['--ssh-client-folder'],
                   help='Path to folder containing SSH client executables (ssh, sftp, ssh-keygen). '
                   'Default: Uses executables from PATH or C:\\Windows\\System32\\OpenSSH on Windows.')
