# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.local_context import LocalContextAttribute, LocalContextAction


def load_arguments(self, _):

    for command_group in ('mysql', 'postgres'):
        server_name_arg_type = CLIArgumentType(metavar='NAME',
                                               help="Name of the server. The name can contain only lowercase letters, numbers, and the hyphen (-) character. Minimum 3 characters and maximum 63 characters.",
                                               local_context_attribute=LocalContextAttribute(name='server_name', actions=[LocalContextAction.SET, LocalContextAction.GET], scopes=[f'{command_group} flexible-server']))

        administrator_login_arg_type = CLIArgumentType(metavar='NAME',
                                                       local_context_attribute=LocalContextAttribute(name='administrator_login', actions=[LocalContextAction.GET, LocalContextAction.SET], scopes=[f'{command_group} flexible-server']))

        database_name_arg_type = CLIArgumentType(metavar='NAME',
                                                 local_context_attribute=LocalContextAttribute(name='database_name', actions=[LocalContextAction.GET, LocalContextAction.SET], scopes=[f'{command_group} flexible-server']))

        with self.argument_context(f'{command_group} flexible-server connect') as c:
            c.argument('server_name', id_part=None, options_list=['--name', '-n'], arg_type=server_name_arg_type)
            c.argument('administrator_login', arg_group='Authentication', arg_type=administrator_login_arg_type, options_list=['--admin-user', '-u'],
                       help='The login username of the administrator.')
            c.argument('administrator_login_password', arg_group='Authentication', options_list=['--admin-password', '-p'],
                       help='The login password of the administrator.')
            c.argument('database_name', arg_type=database_name_arg_type, options_list=['--database-name', '-d'], help='The name of a database.')
            c.argument('interactive_mode', options_list=['--interactive'], action='store_true', help='Pass this parameter to connect to database in interactive mode.')
            c.argument('querytext', options_list=['--querytext', '-q'], deprecate_info=c.deprecate(redirect='execute'), help='A query to run against the flexible server.')

        with self.argument_context(f'{command_group} flexible-server execute') as c:
            c.argument('server_name', id_part=None, options_list=['--name', '-n'], arg_type=server_name_arg_type)
            c.argument('administrator_login', arg_group='Authentication', arg_type=administrator_login_arg_type, options_list=['--admin-user', '-u'],
                       help='The login username of the administrator.')
            c.argument('administrator_login_password', arg_group='Authentication', options_list=['--admin-password', '-p'],
                       help='The login password of the administrator.')
            c.argument('database_name', arg_type=database_name_arg_type, options_list=['--database-name', '-d'], help='The name of a database.')
            c.argument('querytext', options_list=['--querytext', '-q'], help='A query to run against the flexible server.')
            c.argument('file_path', options_list=['--file-path', '-f'], help='The path of the sql file to execute.')
