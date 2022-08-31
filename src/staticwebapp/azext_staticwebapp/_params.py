# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import resource_group_name_type

    with self.argument_context('staticwebapp dbconnection') as c:
        c.argument('name', options_list=['--name', '-n'], help="Name of the Static Web App")
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment', help="Name of the environment of Static Web App.", default="default",
                   options_list=["--environment", "-e"])

    with self.argument_context('staticwebapp dbconnection create') as c:
        c.argument('db_resource_id', options_list=['--db-resource-id', '-d'],
                   help="Get detailed information on database connections")
        c.argument('use_connection_string', options_list=['--use-connection-string', '-c'], action='store_true',
                   default=False, help="Force the usage of connection string")

    with self.argument_context('staticwebapp dbconnection show') as c:
        c.argument('detailed', options_list=['--detailed', '-d'],action='store_true',
                   default=False, help="Get detailed information on database connections")

