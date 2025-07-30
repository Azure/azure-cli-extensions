# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,too-many-statements


def load_command_table(self, _):

    with self.command_group('grafana') as g:
        from .custom import GrafanaCreate, GrafanaDelete, GrafanaUpdate
        self.command_table['grafana create'] = GrafanaCreate(loader=self)
        self.command_table['grafana delete'] = GrafanaDelete(loader=self)
        self.command_table['grafana update'] = GrafanaUpdate(loader=self)
        g.custom_command('backup', 'backup_grafana', is_preview=True)
        g.custom_command('restore', 'restore_grafana', is_preview=True)
        g.custom_command('migrate', 'migrate_grafana', is_preview=True)

    with self.command_group('grafana dashboard') as g:
        g.custom_command('create', 'create_dashboard')
        g.custom_command('delete', 'delete_dashboard')
        g.custom_command('list', 'list_dashboards')
        g.custom_show_command('show', 'show_dashboard')
        g.custom_command('update', 'update_dashboard')
        g.custom_command('import', 'import_dashboard')
        g.custom_command('sync', 'sync_dashboard', is_preview=True)

    with self.command_group('grafana data-source') as g:
        g.custom_command('create', 'create_data_source')
        g.custom_command('list', 'list_data_sources')
        g.custom_show_command('show', 'show_data_source')
        g.custom_command('delete', 'delete_data_source')
        g.custom_command('query', 'query_data_source')
        g.custom_command('update', 'update_data_source')

    with self.command_group('grafana notification-channel', deprecate_info=self.deprecate()) as g:
        g.custom_command('list', 'list_notification_channels')
        g.custom_show_command('show', 'show_notification_channel')
        g.custom_command('create', 'create_notification_channel')
        g.custom_command('update', 'update_notification_channel')
        g.custom_command('delete', 'delete_notification_channel')
        g.custom_command('test', 'test_notification_channel')

    with self.command_group('grafana folder') as g:
        g.custom_command('create', 'create_folder')
        g.custom_command('list', 'list_folders')
        g.custom_show_command('show', 'show_folder')
        g.custom_command('delete', 'delete_folder')
        g.custom_command('update', 'update_folder')

    with self.command_group('grafana user') as g:
        g.custom_command('list', 'list_users')
        g.custom_show_command('show', 'show_user')
        g.custom_command('actual-user', 'get_actual_user')

    with self.command_group('grafana api-key', deprecate_info=self.deprecate()) as g:
        g.custom_command('create', 'create_api_key')
        g.custom_command('list', 'list_api_keys')
        g.custom_command('delete', 'delete_api_key')

    with self.command_group('grafana service-account') as g:
        g.custom_command('create', 'create_service_account')
        g.custom_command('list', 'list_service_accounts')
        g.custom_show_command('show', 'show_service_account')
        g.custom_command('delete', 'delete_service_account')
        g.custom_command('update', 'update_service_account')

    with self.command_group('grafana service-account token') as g:
        g.custom_command('create', 'create_service_account_token')
        g.custom_command('list', 'list_service_account_tokens')
        g.custom_command('delete', 'delete_service_account_token')

    with self.command_group('grafana integrations monitor') as g:
        g.custom_command('add', 'link_monitor', is_preview=True)
        g.custom_command('list', 'list_monitors', is_preview=True)
        g.custom_command('delete', 'unlink_monitor', is_preview=True)
