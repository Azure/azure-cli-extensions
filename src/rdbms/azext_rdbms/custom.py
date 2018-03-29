# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import resource_id, is_valid_resource_id, parse_resource_id  # pylint: disable=import-error
from azext_rdbms.mysql.operations.servers_operations import ServersOperations
from ._client_factory import get_mysql_management_client, get_postgresql_management_client

SKU_TIER_MAP = {'Basic': 'b', 'GeneralPurpose': 'gp', 'MemoryOptimized': 'mo'}


# need to replace source server name with source server id, so customer server georestore function
# The parameter list should be the same as that in factory to use the ParametersContext
# auguments and validators
def _server_georestore(cmd, client, resource_group_name, server_name, sku_name, location, source_server, backup_retention=None, no_wait=False, **kwargs):
    provider = 'Microsoft.DBForMySQL' if isinstance(client, ServersOperations) else 'Microsoft.DBforPostgreSQL'
    parameters = None
    if provider == 'Microsoft.DBForMySQL':
        from azext_rdbms import mysql
        parameters = mysql.models.ServerForCreate(
            sku=mysql.models.Sku(name=sku_name),
            properties=mysql.models.ServerPropertiesForGeoRestore(
                backup_retention_days=backup_retention
            ),
            storage_profile=mysql.models.StorageProfile())
    elif provider == 'Microsoft.DBforPostgreSQL':
        from azext_rdbms import postgresql
        parameters = postgresql.models.ServerForCreate(
            sku=postgresql.models.Sku(name=sku_name),
            properties=postgresql.models.ServerPropertiesForGeoRestore())

    if not is_valid_resource_id(source_server):
        if len(source_server.split('/')) == 1:
            source_server = resource_id(subscription=get_subscription_id(cmd.cli_ctx),
                                        resource_group=resource_group_name,
                                        namespace=provider,
                                        type='servers',
                                        name=source_server)
        else:
            raise ValueError('The provided source-server {} is invalid.'.format(source_server))

    parameters.properties.source_server_id = source_server
    parameters.location = location

    source_server_id_parts = parse_resource_id(source_server)
    try:
        source_server_object = client.get(source_server_id_parts['resource_group'], source_server_id_parts['name'])
        if parameters.sku.name is None:
            parameters.sku.name = source_server_object.sku.name
    except Exception as e:
        raise ValueError('Unable to get source server: {}.'.format(str(e)))

    return client.create(resource_group_name, server_name, parameters, raw=no_wait)
