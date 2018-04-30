# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_resource_name_completion_list, tags_type, get_location_type, get_enum_type   # pylint: disable=line-too-long


def load_arguments(self, _):    # pylint: disable=too-many-statements

    server_completers = {
        'mysql': get_resource_name_completion_list('Microsoft.DBForMySQL/servers'),
        'postgres': get_resource_name_completion_list('Microsoft.DBForPostgreSQL/servers')
    }

    def _complex_params(command_group):
        with self.argument_context('{} server create'.format(command_group)) as c:
            c.argument('sku_name', options_list=['--sku-name'], required=True, help='The name of the sku, typically, tier + family + cores, e.g. B_Gen4_1, GP_Gen5_8.')

            c.argument('backup_retention', type=int, options_list=['--backup-retention'], help='The number of days a backup is retained.')
            c.argument('geo_redundant_backup', options_list=['--geo-redundant-backup'], help='Enable Geo-redundant or not for server backup.')
            c.argument('storage_size', options_list=['--storage-size'], type=int, help='The max storage size of the server. Unit is megabytes.')

            c.argument('administrator_login', required=True, arg_group='Authentication')
            c.argument('administrator_login_password', arg_group='Authentication')

            c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False)
            c.argument('version', help='Server version')

        with self.argument_context('{} server georestore'. format(command_group)) as c:
            c.argument('location', arg_type=get_location_type(self.cli_ctx), required=True)
            c.argument('sku_name', options_list=['--sku-name'], required=False, help='The name of the sku, typically, tier + family + cores, e.g. B_Gen4_1, GP_Gen5_8.')
            c.argument('source_server', options_list=['--source-server', '-s'], required=True, help='The name or ID of the source server to restore from.')
            c.argument('backup_retention', options_list=['--backup-retention'], type=int, help='The max days of retention, unit is days.')
            c.argument('geo_redundant_backup', options_list=['--geo-redundant-backup'], help='Enable Geo-redundant or not for server backup.')

        with self.argument_context('{} server wait'.format(command_group)) as c:
            c.ignore('created', 'deleted', 'updated')

    _complex_params('mysql')
    _complex_params('postgres')

    for scope in ['mysql', 'postgres']:
        with self.argument_context(scope) as c:
            c.argument('name', options_list=['--sku-name'], required=True)
            c.argument('server_name', completer=server_completers[scope], options_list=['--server-name', '-s'], help='Name of the server.')

    for scope in ['mysql server', 'postgres server']:
        with self.argument_context(scope) as c:
            c.ignore('size', 'family', 'capacity', 'tier')

            c.argument('server_name', options_list=['--name', '-n'], id_part='name', help='Name of the server.')
            c.argument('administrator_login', options_list=['--admin-user', '-u'])
            c.argument('administrator_login_password', options_list=['--admin-password', '-p'], help='The password of the administrator login.')
            c.argument('ssl_enforcement', arg_type=get_enum_type(['Enabled', 'Disabled']), options_list=['--ssl-enforcement'], help='Enable ssl enforcement or not when connect to server.')
            c.argument('tier', arg_type=get_enum_type(['Basic', 'GeneralPurpose', 'MemoryOptimized']), options_list=['--performance-tier'], help='The performance tier of the server.')
            c.argument('capacity', options_list=['--vcore'], type=int, help='Number of vcore.')
            c.argument('family', options_list=['--family'], arg_type=get_enum_type(['Gen4', 'Gen5']), help='Hardware generation.')
            c.argument('storage_mb', options_list=['--storage-size'], type=int, help='The max storage size of the server. Unit is megabytes.')
            c.argument('backup_retention_days', options_list=['--backup-retention'], type=int, help='The number of days a backup is retained.')
            c.argument('tags', tags_type)
