# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_capacities
    powerbidedicated_custom_capacities = CliCommandType(
        operations_tmpl='azext_powerbidedicated.custom#{}',
        client_factory=cf_capacities)

    with self.command_group('powerbi', is_preview=True) as g:
        pass

    with self.command_group('powerbi embedded-capacity', powerbidedicated_custom_capacities, is_preview=True,
                            client_factory=cf_capacities) as g:
        g.custom_command('create', 'create_powerbi_embedded_capacity', supports_no_wait=True)
        g.custom_command('update', 'update_powerbi_embedded_capacity', supports_no_wait=True)
        g.custom_command('delete', 'delete_powerbi_embedded_capacity', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_powerbi_embedded_capacity')
        g.custom_command('list', 'list_powerbi_embedded_capacity')
        g.wait_command('wait', getter_name='get_powerbi_embedded_capacity',
                       getter_type=powerbidedicated_custom_capacities)
