# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from ._validators import process_grafana_create_namespace


def load_command_table(self, _):

    with self.command_group('grafana', is_preview=True) as g:
        g.custom_command('create', 'create_grafana', validator=process_grafana_create_namespace)
        g.custom_command('delete', 'delete_grafana', confirmation=True)
        g.custom_command('list', 'list_grafana')
        g.custom_show_command('show', 'show_grafana')

    with self.command_group('grafana dashboard') as g:
        g.custom_command('create', 'create_dashboard')
        g.custom_command('delete', 'delete_dashboard')
        g.custom_command('list', 'list_dashboards')
        g.custom_show_command('show', 'show_dashboard')
        g.custom_command('update', 'update_dashboard')
        g.custom_command('import', 'import_dashboard')

    with self.command_group('grafana data-source') as g:
        g.custom_command('create', 'create_data_source')
        g.custom_command('list', 'list_data_sources')
        g.custom_show_command('show', 'show_data_source')
        g.custom_command('delete', 'delete_data_source')
        g.custom_command('query', 'query_data_source')
        g.custom_command('update', 'update_data_source')

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
