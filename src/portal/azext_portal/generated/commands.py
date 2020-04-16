# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    with self.command_group('stream-analytics', is_experimental=True):
        pass

    from azext_portal.generated._client_factory import cf_dashboard
    portal_dashboard = CliCommandType(
        operations_tmpl='azext_portal.vendored_sdks.portal.operations._dashboard_operations#DashboardOperations.{}',
        client_factory=cf_dashboard)
    with self.command_group('portal dashboard', portal_dashboard, client_factory=cf_dashboard) as g:
        g.custom_command('list', 'portal_dashboard_list')
        g.custom_show_command('show', 'portal_dashboard_show')
        g.custom_command('create', 'portal_dashboard_create')
        g.custom_command('update', 'portal_dashboard_update')
        g.custom_command('delete', 'portal_dashboard_delete',
                         confirmation=True)
        g.custom_command('import', 'portal_dashboard_import')
