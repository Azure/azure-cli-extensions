# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_vi._client_factory import cf_vi, cf_vi_extensions, cf_vi_cameras
from . import consts

def load_command_table(self, _):

    # vi_extension_sdk = CliCommandType(
    #    operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations#ExtensionOperations{}',
    #    client_factory=cf_vi_extensions)

    with self.command_group(consts.EXTENSION_NAME, client_factory=cf_vi, is_experimental=True) \
            as g:
        g.custom_command('my', 'my_vi_command')
       
    with self.command_group(f"{consts.EXTENSION_NAME} extension", client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_command('show', 'show_vi_extension')
        g.custom_command('troubleshoot', 'troubleshoot_vi_extension')

    with self.command_group(f"{consts.EXTENSION_NAME} camera", client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_command('list', 'list_cameras')



