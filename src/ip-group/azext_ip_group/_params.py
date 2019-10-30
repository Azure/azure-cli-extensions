# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import tags_type, get_location_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    # region IpGroup
    with self.argument_context('network ip-group', min_api='2019-09-01') as c:
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('ip_groups_name', options_list=['--name', '-n'], help='Name of the IpGroup')

    for verb in ['create', 'update']:
        with self.argument_context('network ip-group {}'.format(verb), min_api='2019-09-01') as c:
            c.argument('ip_addresses', nargs='+', help='Space-separated list of IpAddress or IpAddressPrefix.')
    # endregion
