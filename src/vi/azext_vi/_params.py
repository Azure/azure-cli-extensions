# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    vi_name_type = CLIArgumentType(options_list='--vi-name-name', help='Name of the Vi.', id_part='name')

    with self.argument_context('vi') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('vi_name', vi_name_type, options_list=['--name', '-n'])

    with self.argument_context('vi cameras') as c:
        c.argument('list', vi_name_type, id_part=None)
        c.argument('name', options_list=['--name', '-n'], help='Name of the webapp to connect to')
        c.argument('scan_id', options_list=['--scan-id'], help='Unique scan id')
        c.argument('timeout', options_list=['--timeout'], help='Timeout for operation in milliseconds')
        c.argument('slot', help="Name of the deployment slot to use")
