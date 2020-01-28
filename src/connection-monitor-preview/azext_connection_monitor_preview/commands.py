# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_nw_connection_monitor
from ._validators import get_network_watcher_from_location, process_nw_cm_create_namespace


def load_command_table(self, _):

    nw_connection_monitor_sdk = CliCommandType(
        operations_tmpl='azext_connection_monitor_preview.vendored_sdks.operations#ConnectionMonitorsOperations.{}',
        client_factory=cf_nw_connection_monitor,
        min_api='2019-11-01'
    )

    with self.command_group('network watcher connection-monitor',
                            nw_connection_monitor_sdk,
                            client_factory=cf_nw_connection_monitor,
                            min_api='2018-01-01') as g:
        g.custom_command('create', 'create_nw_connection_monitor', validator=process_nw_cm_create_namespace)
        g.command('delete', 'delete')
        g.show_command('show', 'get')
        g.command('stop', 'stop')
        g.command('start', 'start')
        g.command('query', 'query')
        g.command('list', 'list')

    with self.command_group('network watcher connection-monitor endpoint',
                            nw_connection_monitor_sdk,
                            min_api='2019-11-01',
                            is_preview=True) as c:
        c.custom_command('add', 'add_nw_connection_monitor_v2_endpoint', validator=get_network_watcher_from_location())

    with self.command_group('network watcher connection-monitor test-group',
                            nw_connection_monitor_sdk,
                            min_api='2019-11-01',
                            is_preview=True) as c:
        c.custom_command('add', 'add_nw_connection_monitor_v2_test_group', validator=get_network_watcher_from_location())