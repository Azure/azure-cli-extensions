# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from ._clients import DbConnectionClient
from ._models import DbConnection
from ._utils import get_database_type, get_location, get_connection_string


# TODO remove or use "use_connection_string"
# TODO add MSI arguments
# TODO add database username/password arguments
def create_dbconnection(cmd, resource_group_name, name, db_resource_id, environment=None, use_connection_string=None,
                        connection_string=None, username=None, password=None):
    db_type = get_database_type(db_resource_id)
    region = get_location(cmd, db_resource_id, db_type)

    if not connection_string:
        connection_string = get_connection_string(cmd, db_resource_id, db_type, username, password)
    # TODO add MSI logic
    # print(connection_string)

    connection = DbConnection
    connection["properties"]["resourceId"] = db_resource_id
    connection["properties"]["connectionIdentity"] = None  # TODO ?
    connection["properties"]["connectionString"] = connection_string
    connection["properties"]["region"] = region

    return DbConnectionClient.create_or_update(cmd, resource_group_name, name, environment, db_connection=connection)


def show_dbconnection(cmd, resource_group_name, name, environment=None, detailed=None):
    return DbConnectionClient.list(cmd, resource_group_name, name, environment, detailed=detailed)


def delete_dbconnection(cmd, resource_group_name, name, environment):
    return DbConnectionClient.delete(cmd, resource_group_name, name, environment)
