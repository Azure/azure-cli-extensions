# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_vi._client_factory import cf_vi
from . import consts

def load_command_table(self, _):

    vi_sdk = CliCommandType(
       operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations._vi_operations#VIOperations{}',
       client_factory=cf_vi)


    with self.command_group(consts.EXTENSION_NAME, vi_sdk, client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_command('create', 'create_vi')
        g.custom_command('update', 'update_vi')
        g.custom_command('list', 'list_vi')
        g.custom_show_command('show', 'show_vi')
        g.custom_command('troubleshoot', 'troubleshoot_vi')
        g.custom_command('cameras list', 'list_cameras')

    with self.command_group(consts.EXTENSION_NAME + " extension", vi_sdk, client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_command('get', 'get_vi_extension')



