# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import tags_type, get_location_type, get_enum_type
from azext_db_up.vendored_sdks.azure_mgmt_rdbms.mysql.models.my_sql_management_client_enums import (
    SslEnforcementEnum, GeoRedundantBackup
)


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements
    for scope in ('mysql', 'postgres', 'sql'):
        with self.argument_context('{} up'.format(scope)) as c:
            c.argument('location', arg_type=get_location_type(self.cli_ctx))
            c.argument('server_name', options_list=['--server-name', '-s'], help='Name of the server.')
            c.argument('administrator_login', options_list=['--admin-user', '-u'], arg_group='Authentication',
                       help='The login username of the administrator.')
            c.argument('administrator_login_password', options_list=['--admin-password', '-p'],
                       arg_group='Authentication',
                       help='The login password of the administrator. Minimum 8 characters and maximum 128 characters. '
                       'Password must contain characters from three of the following categories: English uppercase '
                       'letters, English lowercase letters, numbers, and non-alphanumeric characters.'
                       'Your password cannot contain all or part of the login name. Part of a login name is defined '
                       'as three or more consecutive alphanumeric characters.')
            c.extra('generate_password', help='Generate a password.', arg_group='Authentication')
            c.argument('database_name', options_list=['--database-name', '-d'],
                       help='The name of a database to initialize.')
            c.argument('tags', tags_type)

        if scope != 'sql':  # SQL alreaady has a core command for displaying connection strings
            with self.argument_context('{} show-connection-string'.format(scope)) as c:
                c.argument('server_name', options_list=['--server-name', '-s'], help='Name of the server.')
                c.argument('database_name', options_list=['--database-name', '-d'], help='The name of a database.')
                c.argument('administrator_login', options_list=['--admin-user', '-u'],
                           help='The login username of the administrator.')
                c.argument('administrator_login_password', options_list=['--admin-password', '-p'],
                           help='The login password of the administrator.')

        with self.argument_context('{} down'.format(scope)) as c:
            c.argument('server_name', options_list=['--server-name', '-s'], help='Name of the server.')
            c.argument('delete_group', action='store_true', help="Delete the resource group.")

    for scope in ('mysql', 'postgres'):
        with self.argument_context('{} up'.format(scope)) as c:
            c.argument('sku_name', options_list=['--sku-name'], default='GP_Gen5_2',
                       help='The name of the sku, typically, tier + family + cores, e.g. B_Gen4_1, GP_Gen5_8.')
            c.argument('backup_retention', type=int, help='The number of days a backup is retained.')
            c.argument('geo_redundant_backup', arg_type=get_enum_type(GeoRedundantBackup),
                       default=GeoRedundantBackup.disabled.value, help='Enable Geo-redundant or not for server backup.')
            c.argument('storage_mb', options_list=['--storage-size'], type=int,
                       help='The max storage size of the server. Unit is megabytes.')
            c.argument('ssl_enforcement', arg_type=get_enum_type(SslEnforcementEnum),
                       default=SslEnforcementEnum.enabled.value,
                       help='Enable ssl enforcement or not when connect to server.')

    with self.argument_context('mysql up') as c:
        c.argument('version', help='Server version', default='5.7')

    with self.argument_context('postgres up') as c:
        c.argument('version', help='Server version', default='10')

    with self.argument_context('sql up') as c:
        c.argument('version', help='Server version', default='12.0')
