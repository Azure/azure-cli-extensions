# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import get_enum_type
from azext_dns.dns.models import ZoneType
from azext_dns._validators import (dns_zone_name_type, get_vnet_validator, validate_metadata)
from knack.arguments import CLIArgumentType


def load_arguments(self, _):
    name_arg_type = CLIArgumentType(options_list=('--name', '-n'), metavar='NAME')

    with self.argument_context('network dns') as c:
        c.argument('record_set_name', name_arg_type, help='The name of the record set, relative to the name of the zone.')
        c.argument('relative_record_set_name', name_arg_type, help='The name of the record set, relative to the name of the zone.')
        c.argument('zone_name', options_list=('--zone-name', '-z'), help='The name of the zone.', type=dns_zone_name_type)
        c.argument('metadata', nargs='+', help='Metadata in space-separated key=value pairs. This overwrites any existing metadata.', validator=validate_metadata)

    with self.argument_context('network dns zone') as c:
        c.argument('zone_name', name_arg_type)
        c.ignore('location')

        c.argument('zone_type', help='Type of DNS zone to create.', arg_type=get_enum_type(ZoneType))
        c.argument('registration_vnets', arg_group='Private Zone', nargs='+', help='Space-separated names or IDs of virtual networks that register hostnames in this DNS zone.', validator=get_vnet_validator('registration_vnets'))
        c.argument('resolution_vnets', arg_group='Private Zone', nargs='+', help='Space-separated names or IDs of virtual networks that resolve records in this DNS zone.', validator=get_vnet_validator('resolution_vnets'))
