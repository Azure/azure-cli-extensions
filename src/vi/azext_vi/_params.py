# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from . import consts

def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    vi_name_type = CLIArgumentType(options_list='--vi-name-name', help='Name of the Vi.', id_part='name')

    with self.argument_context(consts.EXTENSION_NAME) as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('vi_name', vi_name_type, options_list=['--name', '-n'])

    with self.argument_context(f"{consts.EXTENSION_NAME} extension show") as c:
        c.argument('connected_cluster', 
                   options_list=['--connected-cluster', '-c'],
                   help='Name of the Kubernetes connected cluster')
    
    with self.argument_context(f"{consts.EXTENSION_NAME} extension troubleshoot") as c:
        c.argument('connected_cluster', 
                   options_list=['--connected-cluster', '-c'],
                   help='Name of the Kubernetes connected cluster')

    with self.argument_context(f"{consts.EXTENSION_NAME} camera list") as c:
        c.argument('connected_cluster', 
                   options_list=['--connected-cluster', '-c'],
                   help='Name of the Kubernetes connected cluster')
