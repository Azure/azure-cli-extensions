# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import resource_group_name_type


def load_arguments(self, _):
    staticsite_name_arg_type = CLIArgumentType(options_list=['--name', '-n'],
                                               metavar='NAME',
                                               help="name of the staticwebapp")

    with self.argument_context('staticwebapp enterprise-edge') as c:
        c.argument("name", arg_type=staticsite_name_arg_type)
        c.argument("resource_group_name", arg_type=resource_group_name_type)

    with self.argument_context('staticwebapp enterprise-edge') as c:
        c.argument("no_register", help="Don't try to register the Microsoft.CDN provider. Registration can be done manually with: az provider register --wait --namespace Microsoft.CDN", default=False)
