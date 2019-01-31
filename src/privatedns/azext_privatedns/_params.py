# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import get_enum_type
from knack.arguments import CLIArgumentType
from azext_privatedns._validators import (privatedns_zone_name_type, get_vnet_validator, validate_metadata)


def load_arguments(self, _):
    name_arg_type = CLIArgumentType(options_list=('--name', '-n'), metavar='NAME')

    with self.argument_context('network privatedns') as c:
        c.argument('record_set_name', name_arg_type, help='The name of the record set, relative to the name of the Private DNS zone.')
        c.argument('relative_record_set_name', name_arg_type, help='The name of the record set, relative to the name of the Private DNS zone.')
        c.argument('private_zone_name', options_list=('--zone-name', '-z'), help='The name of the Private DNS zone.', type=privatedns_zone_name_type)
        c.argument('metadata', nargs='+', help='Metadata in space-separated key=value pairs. This overwrites any existing metadata.', validator=validate_metadata)

    with self.argument_context('network privatedns zone') as c:
        c.argument('private_zone_name', name_arg_type)
        c.ignore('location')
