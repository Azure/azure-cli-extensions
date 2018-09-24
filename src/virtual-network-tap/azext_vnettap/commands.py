# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_virtual_network_taps, cf_nic_tap_config


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_vnet_tap_sdk = CliCommandType(
        operations_tmpl='azext_vnettap.vendored_sdks.operations.virtual_network_taps_operations#VirtualNetworkTapsOperations.{}',
        client_factory=cf_virtual_network_taps,
        min_api='2018-08-01'
    )

    network_nic_tap_config_sdk = CliCommandType(
        operations_tmpl='azext_vnettap.vendored_sdks.operations.network_interface_tap_configurations_operations#NetworkInterfaceTapConfigurationsOperations.{}',
        client_factory=cf_nic_tap_config,
        min_api='2018-08-01'
    )

    with self.command_group('network vnet tap', network_vnet_tap_sdk) as g:
        g.custom_command('create', 'create_vnet_tap')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_vnet_taps')
        g.show_command('show', 'get')
        g.generic_update_command('update')

    with self.command_group('network nic vtap-config', network_nic_tap_config_sdk) as g:
        g.custom_command('create', 'create_vtap_config')
        g.command('delete', 'delete')
        g.command('list', 'list')
        g.show_command('show', 'get')
