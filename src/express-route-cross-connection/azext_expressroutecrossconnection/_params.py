# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from argcomplete.completers import FilesCompleter

import six

from knack.arguments import CLIArgumentType, ignore_type

from azure.cli.core.commands.parameters import (get_location_type, get_resource_name_completion_list,
                                                tags_type, zone_type,
                                                file_type, get_resource_group_completion_list,
                                                get_three_state_flag, get_enum_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.template_create import get_folded_parameter_help_string
from azure.cli.command_modules.network._validators import (
    dns_zone_name_type,
    validate_auth_cert, validate_cert, validate_inbound_nat_rule_id_list,
    validate_address_pool_id_list, validate_inbound_nat_rule_name_or_id,
    validate_address_pool_name_or_id, load_cert_file, validate_metadata,
    validate_peering_type, validate_dns_record_type, validate_route_filter, validate_target_listener,
    validate_private_ip_address,
    get_servers_validator, get_public_ip_validator, get_nsg_validator, get_subnet_validator,
    get_network_watcher_from_vm, get_network_watcher_from_location,
    get_asg_validator, get_vnet_validator, validate_ip_tags, validate_ddos_name_or_id)
from azure.mgmt.network.models import ApplicationGatewaySslProtocol
from azure.mgmt.trafficmanager.models import MonitorProtocol, ProfileStatus
from azure.cli.command_modules.network._completers import (
    subnet_completion_list, get_lb_subresource_completion_list, get_ag_subresource_completion_list,
    ag_url_map_rule_completion_list, tm_endpoint_completion_list)
from azure.cli.core.util import get_json_object


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    sku_family_type = CLIArgumentType(help='Chosen SKU family of ExpressRoute circuit.', arg_type=get_enum_type(ExpressRouteCircuitSkuFamily), default=ExpressRouteCircuitSkuFamily.metered_data.value)
    sku_tier_type = CLIArgumentType(help='SKU Tier of ExpressRoute circuit.', arg_type=get_enum_type(ExpressRouteCircuitSkuTier), default=ExpressRouteCircuitSkuTier.standard.value)
    with self.argument_context('network express-route') as c:
        c.argument('circuit_name', circuit_name_type, options_list=('--name', '-n'))
        c.argument('sku_family', sku_family_type)
        c.argument('sku_tier', sku_tier_type)
        c.argument('bandwidth_in_mbps', options_list=('--bandwidth',), help="Bandwidth in Mbps of the circuit.")
        c.argument('service_provider_name', options_list=('--provider',), help="Name of the ExpressRoute Service Provider.")
        c.argument('peering_location', help="Name of the peering location.")
        c.argument('device_path', options_list=('--path',), arg_type=get_enum_type(device_path_values))
        c.argument('vlan_id', type=int)
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    with self.argument_context('network express-route update') as c:
        c.argument('sku_family', sku_family_type, default=None)
        c.argument('sku_tier', sku_tier_type, default=None)

    with self.argument_context('network express-route auth') as c:
        c.argument('circuit_name', circuit_name_type)
        c.argument('authorization_name', name_arg_type, id_part='child_name_1', help='Authorization name')

    with self.argument_context('network express-route auth create') as c:
        c.argument('authorization_parameters', ignore_type)
        c.extra('cmd')

    with self.argument_context('network express-route peering') as c:
        # Using six.integer_types so we get int for Py3 and long for Py2
        c.argument('peer_asn', help='Autonomous system number of the customer/connectivity provider.', type=six.integer_types[-1])
        c.argument('vlan_id', help='Identifier used to identify the customer.')
        c.argument('circuit_name', circuit_name_type)
        c.argument('peering_name', name_arg_type, id_part='child_name_1')
        c.argument('peering_type', validator=validate_peering_type, arg_type=get_enum_type(ExpressRoutePeeringType), help='BGP peering type for the circuit.')
        c.argument('sku_family', arg_type=get_enum_type(ExpressRouteCircuitSkuFamily))
        c.argument('sku_tier', arg_type=get_enum_type(ExpressRouteCircuitSkuTier))
        c.argument('primary_peer_address_prefix', options_list=['--primary-peer-subnet'], help='/30 subnet used to configure IP addresses for primary interface.')
        c.argument('secondary_peer_address_prefix', options_list=['--secondary-peer-subnet'], help='/30 subnet used to configure IP addresses for secondary interface.')
        c.argument('advertised_public_prefixes', arg_group='Microsoft Peering', nargs='+', help='Space-separated list of prefixes to be advertised through the BGP peering.')
        c.argument('customer_asn', arg_group='Microsoft Peering', help='Autonomous system number of the customer.')
        c.argument('routing_registry_name', arg_group='Microsoft Peering', arg_type=get_enum_type(routing_registry_values), help='Internet Routing Registry / Regional Internet Registry')
        c.argument('route_filter', min_api='2016-12-01', arg_group='Microsoft Peering', help='Name or ID of a route filter to apply to the peering settings.', validator=validate_route_filter)
        c.argument('ip_version', min_api='2017-06-01', help='The IP version to update Microsoft Peering settings for.', arg_group='Microsoft Peering', arg_type=get_enum_type(['IPv4', 'IPv6']))
        c.argument('shared_key', help='Key for generating an MD5 for the BGP session.')

    for scope in ['express-route auth', 'express-route peering']:
        with self.argument_context('network {} list'.format(scope)) as c:
            c.argument('circuit_name', id_part=None)
