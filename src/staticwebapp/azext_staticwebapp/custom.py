# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from ._clients import DbConnectionClient
from ._models import DbConnection
from ._utils import get_database_type, Sku, ConnectionType
from azure.cli.command_modules.appservice.static_sites import show_staticsite


# TODO remove or use "use_connection_string"
# TODO add MSI arguments
def create_dbconnection(cmd, resource_group_name, name, db_resource_id, environment=None, use_connection_string=None,
                        connection_string=None, username=None, password=None):
    app = show_staticsite(cmd, name, resource_group_name)
    sku = Sku.FREE if app.sku.name.lower() == "free" else Sku.STANDARD
    connection_type = ConnectionType.CONNECTION_STRING  # TODO make this conditional on MSI args
    db_type = get_database_type(db_resource_id)
    region = db_type.get_location(cmd, db_resource_id)

    if not connection_string:
        connection_string = db_type.get_connection_string(cmd, sku, connection_type, db_resource_id, username, password)

    connection = DbConnection
    connection["properties"]["resourceId"] = db_resource_id
    connection["properties"]["connectionIdentity"] = None  # TODO take this from MSI args
    connection["properties"]["connectionString"] = connection_string
    connection["properties"]["region"] = region

    return DbConnectionClient.create_or_update(cmd, resource_group_name, name, environment, db_connection=connection)


def show_dbconnection(cmd, resource_group_name, name, environment=None, detailed=None):
    return DbConnectionClient.list(cmd, resource_group_name, name, environment, detailed=detailed)


def delete_dbconnection(cmd, resource_group_name, name, environment):
    return DbConnectionClient.delete(cmd, resource_group_name, name, environment)
