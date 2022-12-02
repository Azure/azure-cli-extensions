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
                   help="The resource ID for the database to connect to.")
        c.argument('connection_string', options_list=["--connection-string", "-c"], help="The database connection string. A connection string will be generated automatically if this argument is not present.")
        c.argument('username', options_list=["--username", "-u"], help="The username to use for authentication with the database. Not required for all databases.")
        c.argument('password', options_list=["--password", "-p"], help="The password to use for authentication with the database. Not required for all databases.")
        c.argument('mi_user_assigned', options_list=["--mi-user-assigned", "-i"], help="A resource ID for a user-assigned managed identity to use for auth with the database. Must be assigned to the Static Web App and have the right permissions on the database.")
        c.argument('mi_system_assigned', options_list=["--mi-system-assigned", "-s"], help="Use the Static Web App's system-assigned identity for auth with the database. Must be assigned to the Static Web App and have the right permissions on the database.")

    with self.argument_context('staticwebapp dbconnection show') as c:
        c.argument('detailed', options_list=['--detailed', '-d'],action='store_true',
                   default=False, help="Get detailed information on database connections")
