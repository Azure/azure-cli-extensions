# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_vi
from . import consts


def load_command_table(self, _):

    vi_sdk = CliCommandType(
        operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations#ViOperations.{}',
        client_factory=cf_vi)

    with self.command_group(f"{consts.EXTENSION_NAME} extension", vi_sdk, client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_show_command('show', 'show_vi_extension')
        g.custom_command('troubleshoot', 'troubleshoot_vi_extension')

    with self.command_group(f"{consts.EXTENSION_NAME} camera", vi_sdk, client_factory=cf_vi, is_preview=True) \
            as g:
        g.custom_command('list', 'list_cameras')
