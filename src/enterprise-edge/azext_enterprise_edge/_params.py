# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import resource_group_name_type, get_enum_type

def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    with self.argument_context('staticwebapp enterprise-edge') as c:
        c.argument("name", arg_type=name_arg_type)
        c.argument("resource_group_name", arg_type=resource_group_name_type)

    with self.argument_context('staticwebapp enterprise-edge wait') as c:
        c.argument("status", arg_type=get_enum_type(['Enabling', 'Disabling', 'Enabled', 'Disabled']))
