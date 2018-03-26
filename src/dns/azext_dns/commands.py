# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.core.util import empty_on_404
from azext_dns._client_factory import (cf_dns_mgmt_zones)
from azext_dns._format import (transform_dns_zone_table_output)


def load_command_table(self, _):

    network_dns_zone_sdk = CliCommandType(
        operations_tmpl='azext_dns.dns.operations.zones_operations#ZonesOperations.{}',
        client_factory=cf_dns_mgmt_zones
    )

    with self.command_group('network dns zone', network_dns_zone_sdk) as g:
        g.command('show', 'get', table_transformer=transform_dns_zone_table_output, exception_handler=empty_on_404)
        g.custom_command('list', 'list_dns_zones', table_transformer=transform_dns_zone_table_output)
        g.custom_command('create', 'create_dns_zone', client_factory=cf_dns_mgmt_zones)
        g.generic_update_command('update', custom_func_name='update_dns_zone')
