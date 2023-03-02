# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_location_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):
    
    with self.argument_context('hybrid-appliance create') as c:
        c.argument('name', options_list=['--name', '-n'], help='')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('mode', options_list=['--mode'], help='')
        c.argument('https_proxy', options_list=['--proxy-https'], arg_group='Proxy', help='Https proxy URL to be used.')
        c.argument('http_proxy', options_list=['--proxy-http'], arg_group='Proxy', help='Http proxy URL to be used.')
        c.argument('no_proxy', options_list=['--proxy-skip-range'], arg_group='Proxy', help='List of URLs/CIDRs for which proxy should not to be used.')

    with self.argument_context('hybrid-appliance upgrade') as c:
        c.argument('name', options_list=['--name', '-n'], help='')

    with self.argument_context('hybrid-appliance delete') as c:
        c.argument('name', options_list=['--name', '-n'], help='')
        

