# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_ags._client_factory import cf_ags


def load_command_table(self, _):

    # TODO: Add command type here
    # ags_sdk = CliCommandType(
    #    operations_tmpl='<PATH>.operations#None.{}',
    #    client_factory=cf_ags)

    # TODO: ensure HTTP doc url in the help

    with self.command_group('grafana', is_preview=True) as g:
        g.custom_command('create', 'create_grafana')
        g.custom_command('delete', 'delete_grafana')
        g.custom_command('list', 'list_grafana')
        g.custom_command('show', 'show_grafana')
        # g.custom_command('update', 'update_grafana')
        g.custom_command('get-short-url', 'get_short_url')   # TODO

    with self.command_group('grafana dashboard') as g:
        g.custom_command('create', 'create_dashboard')  # TODO need examples
        g.custom_command('delete', 'delete_dashboard')
        g.custom_command('list', 'list_dashboards')
        g.custom_command('show', 'show_dashboard')  # TODO handle HOME dashboard
        g.custom_command('update', 'update_dashboard')  # TODO
        # g.custom_command('get-tags', 'get_dashboard_tags')  # TODO handle HOME dashboard

    #with self.command_group('grafana data-source') as g:
    #    g.custom_command('create', 'create_data_source')  # TODO
    #    g.custom_command('list', 'list_data_sources')
    #    g.custom_command('show', 'show_data_source')  # TODO handle both id, uid, name
    #    g.custom_command('delete', 'delete_data_source')  # TODO handle both id, uid, name
    #    g.custom_command('query', 'query_data_source')  # TODO handle both id, uid, name
    #    g.custom_command('test', 'test_data_source')   # TODO

    #with self.command_group('grafana user'):
    #    g.custom_command('list', 'list_users')  # TODO
    #    g.custom_command('show', 'show_user')  # TODO
    #    g.custom_command('actual-user', 'get_actual_user')  # TODO
    #    g.custom_command('star-dashboard', 'star_dashboard')  # TODO consider to move under "dashboard"
    #    g.custom_command('unstar-dashboard', 'unstar_dashboard')  # TODO consider to move under "dashboard"

    #with self.command_group('grafana alert'):
    #    g.custom_command('list', 'list_alerts')
    #    g.custom_command('show', 'show-alert')
    #    g.custom_command('pause', 'pause_alert')  # TODO handle "pause-all"

    #with self.command_group('grafana alert notification-channel'):
    #    g.custom_command('create', 'create_notification_channel')  # TODO
    #    g.custom_command('list', 'list_notification_channels')  # TODO handle look up modes
    #    g.custom_command('show', 'show_notification_channel')  # TODO handle both uid and id
    #    g.custom_command('delete', 'delete_notification_channel')  # TODO handle both uid and id
    #    g.custom_command('update', 'update_notification_channel')  # TODO handle both uid and id
    #    g.custom_command('test', 'test_notification_channel')  # TODO handle both uid and id

    #with self.command_group('grafana annotation'):
    #    g.custom_command('create', 'create_annotation')  # TODO
    #    g.custom_command('create', 'list_annotation')  # TODO (find)
    #    g.custom_command('update', 'update_annotation')  # TODO
    #    g.custom_command('patch', 'patch_annotation')  # TODO
    #    g.custom_command('delete', 'delete_annotation')  # TODO
    #    g.custom_command('find-tags', 'find_annotation_tags')  # TODO
