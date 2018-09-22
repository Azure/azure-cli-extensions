# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list, tags_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._validators import validate_vnet_tap


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    tap_name_arg_type = CLIArgumentType(options_list='--tap-name', metavar='NAME', help='Name of the VNet TAP.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/virtualNetworkTaps'))

    with self.argument_context('network vnet tap') as c:
        c.argument('tap_name', tap_name_arg_type, options_list=['--name', '-n'])
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)

    with self.argument_context('network vnet tap create', arg_group='Destination') as c:
        c.argument('destination', help='ID of the ILB or NIC IP configuration to receive the tap.')
        c.argument('port', help='The VXLAN port that will receive the tapped traffic.')

    with self.argument_context('network nic vtap-config') as c:
        c.argument('network_interface_name', options_list='--nic-name', help='Name of the network interface (NIC).', id_part='name')
        c.argument('vnet_tap', help='Name or ID of the virtual network tap.', validator=validate_vnet_tap)
        for dest in ['vtap_config_name', 'tap_configuration_name']:
            c.argument(dest, options_list=['--name', '-n'], help='Name of the virtual network tap configuration.', id_part='child_name_1')
