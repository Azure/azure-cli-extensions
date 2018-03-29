# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_resource_name_completion_list, tags_type, get_location_type, get_enum_type   # pylint: disable=line-too-long
from azext_rdbms import mysql, postgresql


def load_arguments(self, _):    # pylint: disable=too-many-statements
    for scope in ['mysql server georestore', 'postgres server georestore']:
        with self.argument_context(scope) as c:
            c.argument('location', arg_type=get_location_type(self.cli_ctx), required=True, help='Location. You can configure the default location using `az configure --defaults location=<location>`.')
            c.argument('sku_name', options_list=['--sku-name'], required=False, help='The name of the sku, typically, tier + family + cores, e.g. B_Gen4_1, GP_Gen5_8.')
            c.argument('source_server', options_list=['--source-server', '-s'], required=True, help='The name or ID of the source server to restore from.')
            c.argument('server_name', options_list=['--name', '-n'], id_part='name', required=True, help='Name of the server.')
            c.argument('backup_retention_days', options_list=['--backup-retention'], type=int, help='The max days of retention, unit is days.')
