# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_storage-blob-preview._client_factory import cf_storage-blob-preview


def load_command_table(self, _):

    # TODO: Add command type here
    # storage-blob-preview_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_storage-blob-preview)


    with self.command_group('storage-blob-preview') as g:
        g.custom_command('create', 'create_storage-blob-preview')
        # g.command('delete', 'delete')
        g.custom_command('list', 'list_storage-blob-preview')
        # g.show_command('show', 'get')
        # g.generic_update_command('update', setter_name='update', custom_func_name='update_storage-blob-preview')


    with self.command_group('storage-blob-preview', is_preview=True):
        pass

