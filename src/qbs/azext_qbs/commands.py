# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):
    with self.command_group('qbs member') as m:
        m.custom_show_command('show', 'get_show_members')
        m.custom_command('list-api-keys', 'get_member_api_keys')
        m.custom_command('regenerate-api-keys', 'get_member_regenerate_api_keys')
        m.custom_command('list', 'get_members')
        m.custom_command('pause', 'post_member_pause')
        m.custom_command('resume', 'post_member_resume')
    with self.command_group('qbs consortium') as m:
        m.custom_command('list', 'get_consortium_members')
        m.custom_command('genesis', 'get_consortium_genesis')
        m.custom_command('remove', 'delete_consortium_members')
    with self.command_group('qbs location') as m:
        m.custom_command('list', 'get_locations')
    with self.command_group('qbs invite') as m:
        m.custom_command('list', 'get_invites')
        m.custom_command('create', 'post_invites')
        m.custom_command('revoke', 'delete_invites')
        m.custom_command('validate', 'get_invites_valid')
    with self.command_group('qbs transaction-node') as m:
        m.custom_show_command('show', 'get_transaction_show')
        m.custom_command('list', 'get_transaction_list')
        m.custom_command('list-api-keys', 'get_transaction_list_api_keys')
        m.custom_command('regenerate-api-keys', 'post_transaction_regenerate_api_keys')
        m.custom_command('add', 'put_transaction')
        m.custom_command('remove', 'delete_transaction')
    with self.command_group('qbs firewall') as m:
        m.custom_command('list', 'get_firewall_list')
        m.custom_command('add', 'patch_firewall_add')
        m.custom_command('remove', 'patch_firewall_remove')
        m.custom_command('clear', 'patch_firewall_clear')
    with self.command_group('qbs scheduled-restart') as m:
        m.custom_command('list', 'get_scheduled_restarts')
        m.custom_command('remove', 'delete_scheduled_restarts')
        m.custom_command('add', 'post_scheduled_restarts')
    with self.command_group('qbs backup') as m:
        m.custom_command('list', 'get_backup')
        m.custom_command('start', 'put_backup')
