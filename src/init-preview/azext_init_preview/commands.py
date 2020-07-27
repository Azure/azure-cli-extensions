# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    # TODO: Add command type here
    # init-preview_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_init-preview)

    with self.command_group('storage') as g:
        g.custom_command('init', 'storage_init', is_preview=True)

