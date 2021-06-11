# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_authV2._client_factory import cf_authV2


def load_command_table(self, _):

    # TODO: Add command type here
    # authV2_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_authV2)
    with self.command_group('webapp auth') as g:
        g.custom_show_command('show', 'get_auth_settings_v2')
        g.custom_command('set', 'set_auth_settings_v2')
        g.custom_command('update', 'update_auth_settings_v2')
        g.custom_command('revert', 'revert_to_auth_settings')

    with self.command_group('webapp authlegacy') as g:
        g.custom_show_command('show', 'get_auth_settings')
        g.custom_command('update', 'update_auth_settings')

