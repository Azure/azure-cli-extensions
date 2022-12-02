# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from ._clients import DbConnectionClient
from ._models import DbConnection
from ._utils import get_database_type, Sku, ConnectionType

from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, InvalidArgumentValueError
from azure.cli.command_modules.appservice.static_sites import show_staticsite

from msrestazure.tools import is_valid_resource_id


# TODO check these args against Thomas's spec
def create_dbconnection(cmd, resource_group_name, name, db_resource_id, environment=None,
                        connection_string=None, username=None, password=None,
                        mi_user_assigned=None, mi_system_assigned=False):
    if mi_system_assigned and mi_user_assigned:
        raise MutuallyExclusiveArgumentError("Cannot use both system and user assigned identities")

    connection_type = ConnectionType.CONNECTION_STRING
    if mi_user_assigned:
        if not is_valid_resource_id(mi_user_assigned):
            raise InvalidArgumentValueError("User-assigned identity must be a valid resource ID")
        connection_type = ConnectionType.MANAGED_IDENTITY_USER_ASSIGNED
    elif mi_system_assigned:
        connection_type = ConnectionType.MANAGED_IDENTITY_SYTEM_ASSIGNED

    app = show_staticsite(cmd, name, resource_group_name)
    sku = Sku.FREE if app.sku.name.lower() == "free" else Sku.STANDARD
    db_type = get_database_type(db_resource_id)
    region = db_type.get_location(cmd, db_resource_id)

    if not connection_string:
        connection_string = db_type.get_connection_string(cmd, sku, connection_type, db_resource_id, username, password)

    identity = None
    if mi_user_assigned:
        identity = mi_user_assigned
    elif mi_system_assigned:
        identity = "SystemAssigned"

    connection = DbConnection
    connection["properties"]["resourceId"] = db_resource_id
    connection["properties"]["connectionIdentity"] = identity
    connection["properties"]["connectionString"] = connection_string
    connection["properties"]["region"] = region

    return DbConnectionClient.create_or_update(cmd, resource_group_name, name, environment, db_connection=connection)


def show_dbconnection(cmd, resource_group_name, name, environment=None, detailed=None):
    return DbConnectionClient.list(cmd, resource_group_name, name, environment, detailed=detailed)


def delete_dbconnection(cmd, resource_group_name, name, environment):
    return DbConnectionClient.delete(cmd, resource_group_name, name, environment)
