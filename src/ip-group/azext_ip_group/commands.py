# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_ip_groups


def load_command_table(self, _):

    network_ip_groups_sdk = CliCommandType(
        operations_tmpl='azext_ip_group.vendored_sdks.operations#IpGroupsOperations.{}',
        client_factory=cf_ip_groups,
        min_api='2019-09-01'
    )

    # region IpGroups
    with self.command_group('network ip-group', network_ip_groups_sdk, min_api='2019-09-01') as g:
        g.custom_command('create', 'create_ip_groups')
        g.generic_update_command('update', custom_func_name='update_ip_groups')
        g.custom_command('list', 'list_ip_groups')
        g.command('delete', 'delete')
        g.show_command('show', 'get')
    # endregion
