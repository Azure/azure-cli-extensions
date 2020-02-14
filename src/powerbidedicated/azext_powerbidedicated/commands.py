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
    powerbidedicated_capacities = CliCommandType(
        operations_tmpl='azext_powerbidedicated.vendored_sdks.powerbidedicated.operations._capacities_operations#CapacitiesOperations.{}',
        client_factory=cf_capacities)
    with self.command_group('powerbi embedded-capacity', powerbidedicated_capacities, client_factory=cf_capacities) as g:
        g.custom_command('create', 'create_powerbi_embedded_capacity')
        g.custom_command('update', 'update_powerbi_embedded_capacity')
        g.custom_command('delete', 'delete_powerbi_embedded_capacity')
        g.custom_show_command('show', 'get_powerbi_embedded_capacity')
        g.custom_command('list', 'list_powerbi_embedded_capacity')
