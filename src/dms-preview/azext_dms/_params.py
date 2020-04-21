# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import resource_group_name_type, tags_type


def load_arguments(self, _):
    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    with self.argument_context('dms task') as c:
        c.argument('group_name', resource_group_name_type)
        c.argument('service_name', options_list=['--service-name'], help="The name of the Service.")
        c.argument('task_name', name_arg_type,
                   help='The name of the Task. A DMS Task is the activity that performs service-level \
related work. There could be multiple Tasks associated with a service. ')

    with self.argument_context('dms task list') as c:
        c.argument('service_name', name_arg_type, help='The name of the Service.')

    with self.argument_context('dms project') as c:
        c.argument('service_name', options_list=['--service-name'],
                   help="The name of the Service. DMS Service is an Azure instance that performs database migrations.")
        c.argument('project_name', name_arg_type,
                   help='The name of the Project. DMS Project is a logical grouping that encompasses \
source database connection, target database connection and a list of databases to migrate.')
        c.argument('tags', tags_type, help='A space-delimited list of tags in tag1[=value1]" format.')

    with self.argument_context('dms project task') as c:
        c.argument('service_name', options_list=['--service-name'])
        c.argument('project_name', options_list=['--project-name'])
        c.argument('task_name', name_arg_type,
                   help='The name of the Task. A DMS Project Task is the activity that performs migration \
related work. There could be multiple Tasks associated with a Project. ')
