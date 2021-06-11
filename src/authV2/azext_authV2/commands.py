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

    with self.command_group('webapp auth config-version') as g:
        g.custom_show_command('show', 'get_config_version')
        g.custom_command('revert', 'revert_to_auth_settings')
        g.custom_command('upgrade', 'upgrade_to_auth_settings_v2')
    
    with self.command_group('webapp auth microsoft') as g:
        g.custom_show_command('show', 'get_aad_settings')
        g.custom_command('update', 'update_aad_settings')

    with self.command_group('webapp auth facebook') as g:
        g.custom_show_command('show', 'get_facebook_settings')
        g.custom_command('update', 'update_facebook_settings')
    
    with self.command_group('webapp auth github') as g:
        g.custom_show_command('show', 'get_github_settings')
        g.custom_command('update', 'update_github_settings')
    
    with self.command_group('webapp auth google') as g:
        g.custom_show_command('show', 'get_google_settings')
        g.custom_command('update', 'update_google_settings')
    
    with self.command_group('webapp auth twitter') as g:
        g.custom_show_command('show', 'get_twitter_settings')
        g.custom_command('update', 'update_twitter_settings')
    
    with self.command_group('webapp auth apple') as g:
        g.custom_show_command('show', 'get_apple_settings')
        g.custom_command('update', 'update_apple_settings')
    
    with self.command_group('webapp auth-classic') as g:
        g.custom_show_command('show', 'get_auth_settings')
        g.custom_command('update', 'update_auth_settings')

