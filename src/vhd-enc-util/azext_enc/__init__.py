# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import ResourceType

import azext_enc._help  # pylint: disable=unused-import


class ENCCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        enc_custom = CliCommandType(
            operations_tmpl='azext_enc.custom#{}')
        super(ENCCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                custom_command_type=enc_custom)

    def load_command_table(self, _):
        with self.command_group('vm encryption') as g:
            g.custom_command('encrypt-vhd', 'client_side_encrypt')
        return self.command_table

    def load_arguments(self, _):
        # pylint: disable=line-too-long
        with self.argument_context('vm encryption encrypt-vhd') as c:
            c.argument('key_encryption_keyvault', options_list=['--key-encryption-keyvault', '--kv'], help='key vault resource id')
            c.argument('key_encryption_key', options_list=['--key-encryption-key', '--kek'], help='key vault key name or id')
            c.argument('vhd_file', options_list=['--vhd-file', '-f'], help='VHD file to encrypt')
            c.argument('blob_name', options_list=['--blob-name', '-b'], help='the name of the storage blob which the encrypted VHD get uploaded to. Default to the VHD file name ')
            c.argument('container', options_list=['--container', '-c'], help='the storage container of the VHD blob. Default to "vhds"')
            c.argument('storage_account', help='the storage account of the VHD blob')
            c.argument('vhd_file_enc', help="File name of encrypted VHD. This is required if you don't want to upload to storage")
            c.argument('no_progress', action='store_true', help="disable progress reporting")
            c.argument('max_connections', help="Maximum number of parallel connections to use to upload encrypted VHD")

COMMAND_LOADER_CLS = ENCCommandsLoader
