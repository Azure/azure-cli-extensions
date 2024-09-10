# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    durabletask_name_type = CLIArgumentType(options_list='--durabletask-name-name', help='Name of the Durabletask.', id_part='name')
    durabletask_rg_type = CLIArgumentType(options_list='--durabletask-rg-name', help='Name of the Resource Group.', id_part='name')
    durabletask_taskhub_type = CLIArgumentType(options_list='--durabletask-taskhub-name', help='Name of the Taskhub.', id_part='name')
    durabletask_namespace_type = CLIArgumentType(options_list='--durabletask-namespace-name', help='Name of the Namespace.', id_part='name')

    with self.argument_context('durabletask') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('namespace_name', durabletask_name_type, options_list=['--name', '-n'])

    with self.argument_context('durabletask list') as c:
        c.argument('durabletask_name', durabletask_name_type, id_part=None)

    # Namespace Commands
    with self.argument_context('durabletask namespace delete') as c:
        c.argument('namespace_name', durabletask_namespace_type, options_list=['--name', '-n'])

    # Taskhub Commands
    with self.argument_context('durabletask taskhub list') as c:
        c.argument('namespace_name', durabletask_namespace_type, options_list=['--name', '-n'], id_part=None)
        c.argument('resource_group_name', durabletask_rg_type, options_list=['--resource-group', '-g'], id_part=None)

    with self.argument_context('durabletask taskhub show') as c:
        c.argument('namespace_name', durabletask_namespace_type, options_list=['--name', '-n'])
        c.argument('task_hub_name', durabletask_taskhub_type, options_list=['--task-hub-name', '-t'])

    with self.argument_context('durabletask taskhub create') as c:
        c.argument('task_hub_name', durabletask_taskhub_type, options_list=['--task-hub-name', '-t'])

    with self.argument_context('durabletask taskhub delete') as c:
        c.argument('task_hub_name', durabletask_taskhub_type, options_list=['--task-hub-name', '-t'])
