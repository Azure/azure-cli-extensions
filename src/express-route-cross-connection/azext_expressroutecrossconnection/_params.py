# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import six

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (get_resource_name_completion_list, get_enum_type)
from azure.cli.command_modules.network._validators import validate_peering_type


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    ExpressRoutePeeringType = self.get_models('ExpressRoutePeeringType')

    name_arg_type = CLIArgumentType(options_list=('--name', '-n'), metavar='NAME')
    cross_connection_name_type = CLIArgumentType(options_list=('--cross-connection-name',), metavar='NAME', help='ExpressRoute cross-connection name.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/expressRouteCrossConnections'))
    routing_registry_values = ['ARIN', 'APNIC', 'AFRINIC', 'LACNIC', 'RIPENCC', 'RADB', 'ALTDB', 'LEVEL3']

    with self.argument_context('network cross-connection') as c:
        c.argument('cross_connection_name', cross_connection_name_type, options_list=('--name', '-n'))

    with self.argument_context('network cross-connection update') as c:
        c.argument('notes', help='Service provider notes.')
        c.argument('provisioning_state', arg_type=get_enum_type(['Provisioning', 'Provisioned', 'NotProvisioned']), help='Provisioning state of the customer ExpressRoute circuit.')

    with self.argument_context('network cross-connection peering') as c:
        # Using six.integer_types so we get int for Py3 and long for Py2
        c.argument('peer_asn', help='Autonomous system number of the customer/connectivity provider.', type=six.integer_types[-1])
        c.argument('vlan_id', help='Identifier used to identify the customer.', type=int)
        c.argument('cross_connection_name', cross_connection_name_type)
        c.argument('peering_name', name_arg_type, id_part='child_name_1')
        c.argument('peering_type', validator=validate_peering_type, arg_type=get_enum_type(ExpressRoutePeeringType), help='BGP peering type for the circuit.')
        c.argument('primary_peer_address_prefix', options_list=['--primary-peer-subnet'], help='/30 subnet used to configure IP addresses for primary interface.')
        c.argument('secondary_peer_address_prefix', options_list=['--secondary-peer-subnet'], help='/30 subnet used to configure IP addresses for secondary interface.')
        c.argument('advertised_public_prefixes', arg_group='Microsoft Peering', nargs='+', help='Space-separated list of prefixes to be advertised through the BGP peering.')
        c.argument('customer_asn', arg_group='Microsoft Peering', help='Autonomous system number of the customer.')
        c.argument('routing_registry_name', arg_group='Microsoft Peering', arg_type=get_enum_type(routing_registry_values), help='Internet Routing Registry / Regional Internet Registry')
        c.argument('ip_version', min_api='2017-06-01', help='The IP version to update Microsoft Peering settings for.', arg_group='Microsoft Peering', arg_type=get_enum_type(['IPv4', 'IPv6']))
        c.argument('shared_key', help='Key for generating an MD5 for the BGP session.')

    with self.argument_context('network cross-connection peering list') as c:
        c.argument('cross_connection_name', id_part=None)
