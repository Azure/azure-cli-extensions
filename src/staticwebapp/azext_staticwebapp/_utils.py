# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from enum import Enum, auto
import re

from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError, ValidationError
from azure.cli.core.util import send_raw_request
from azure.cli.command_modules.cosmosdb._client_factory import cf_db_accounts
from msrestazure.tools import parse_resource_id

class DbType(Enum):
    COSMOS_DB = auto()
    AZURE_SQL = auto()
    MYSQL_SINGLE = auto()
    MYSQL_FLEX = auto()
    PGSQL_SINGLE = auto()
    PGSQL_FLEX = auto()


rid_to_db_type = {
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DocumentDB/databaseAccounts\/.*$": DbType.COSMOS_DB,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers/Microsoft.Sql/servers\/.*\/databases\/.*$": DbType.AZURE_SQL,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DBforMySQL\/servers\/.*$": DbType.MYSQL_SINGLE,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DBforMySQL/flexibleServers\/.*$": DbType.MYSQL_FLEX,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DBforPostgreSQL\/servers\/.*$": DbType.PGSQL_SINGLE,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DBforPostgreSQL\/flexibleServers\/.*$": DbType.PGSQL_FLEX,
}


db_type_to_api_version = {
    DbType.COSMOS_DB: "2021-10-15",
    DbType.AZURE_SQL: "2021-11-01",
    DbType.MYSQL_SINGLE: "2017-12-01",
    DbType.MYSQL_FLEX: "2021-05-01",
    DbType.PGSQL_SINGLE: "2017-12-01",
    DbType.PGSQL_FLEX: "2021-06-01",
}


def get_database_type(resource_id: str) -> 'DbType':
    for pattern, db_type in rid_to_db_type.items():
        if re.fullmatch(pattern, resource_id, flags=re.IGNORECASE):
            return db_type
    raise InvalidArgumentValueError("Database resource ID is invalid or of an unsupported DB")


def get_location(cmd, resource_id: str, db_type: 'DbType') -> str:
    management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
    api_version = db_type_to_api_version[db_type]
    request_url = f"{management_hostname.strip('/')}{resource_id}?api-version={api_version}"

    r = send_raw_request(cmd.cli_ctx, "GET", request_url)
    return r.json()["location"]


# TODO
def get_connection_string(cmd, resource_id: str, db_type: 'DbType', username=None, password=None):
    parsed_rid = parse_resource_id(resource_id)
    resource_group = parsed_rid["resource_group"]
    name = parsed_rid["name"]
    if db_type == DbType.COSMOS_DB:
        client = cf_db_accounts(cmd.cli_ctx, None)
        return client.list_connection_strings(resource_group, name).connection_strings[0].connection_string
    if db_type == DbType.AZURE_SQL:
        if not username or not password:
            raise RequiredArgumentMissingError("Must include database username and password for Azure SQL databases")
        return (f"Server=tcp:{name}.database.windows.net,1433;Database={parsed_rid['child_name_1']};"
                f"User ID={username};Password={password};Encrypt=true;Connection Timeout=30;")
    # TODO verify
    if db_type == DbType.MYSQL_SINGLE:
        pass  # TODO not supported? confirm with Thomas
    # TODO verify
    if db_type == DbType.MYSQL_FLEX:
        return (f'Server="{your_server}.mysql.database.azure.com";UserID = "{your_username}";Password="{your_password}";Database="{your_database}";SslMode=MySqlSslMode.Required;SslCa="{{path_to_CA_cert}}"')
    # TODO verify
    if db_type == DbType.PGSQL_SINGLE:
        return
    # TODO verify
    if db_type == DbType.PGSQL_FLEX:
        return
    raise InvalidArgumentValueError("Database resource ID is invalid or of an unsupported DB")

