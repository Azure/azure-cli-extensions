# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('fidalgo project list') as c:
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo pool list') as c:
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo pool show') as c:
        c.argument('pool_name', options_list=['--name', '-n', '--pool-name'], type=str, help='The name of a pool of '
                   'virtual machines.')
        c.argument('project_name', options_list=['--project-name', '--project'], type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine list') as c:
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine show') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine create') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('pool_name', type=str, help='The name of the virtual machine pool this machine belongs to.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine delete') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine assign') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('new_owner', type=str, help='Identifier of new owner')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine get-rdp-file-content') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine start') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo virtual-machine stop') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('devcenter', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')