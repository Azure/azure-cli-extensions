# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_three_state_flag   # pylint: disable=line-too-long
from azure.cli.command_modules.sql._validators import validate_subnet


def load_arguments(self, _):    # pylint: disable=too-many-statements

    for scope in ['mysql server vnet-rule', 'postgres server vnet-rule']:
        with self.argument_context(scope) as c:
            c.argument('server_name', options_list=['--server-name', '-s'])
            c.argument('virtual_network_rule_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the vnet rule.')
            c.argument('virtual_network_subnet_id', options_list=['--subnet'], help='Name or ID of the subnet that allows access to an Azure Postgres Server. If subnet name is provided, --vnet-name must be provided.')
            c.argument('ignore_missing_vnet_service_endpoint', options_list=['--ignore-missing-endpoint', '-i'], help='Create vnet rule before virtual network has vnet service endpoint enabled', arg_type=get_three_state_flag())

        with self.argument_context('postgres server vnet-rule create') as c:
            c.extra('vnet_name', options_list=['--vnet-name'], help='The virtual network name', validator=validate_subnet)

        with self.argument_context('postgres server vnet-rule update') as c:
            c.extra('vnet_name', options_list=['--vnet-name'], help='The virtual network name', validator=validate_subnet)

        with self.argument_context('mysql server vnet-rule create') as c:
            c.extra('vnet_name', options_list=['--vnet-name'], help='The virtual network name', validator=validate_subnet)

        with self.argument_context('mysql server vnet-rule update') as c:
            c.extra('vnet_name', options_list=['--vnet-name'], help='The virtual network name', validator=validate_subnet)
