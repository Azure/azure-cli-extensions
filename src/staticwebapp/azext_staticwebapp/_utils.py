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


class ConnectionType(Enum):
    CONNECTION_STRING = auto()
    MANAGED_IDENTITY_USER_ASSIGNED = auto()
    MANAGED_IDENTITY_SYTEM_ASSIGNED= auto()


class Sku(Enum):
    FREE = auto()
    STANDARD = auto()


class AbstractDbHandler:
    DB_TYPE_NAME = ""  # used for emitting user-friendly error messages
    API_VERSION = ""  # the API version for performing GET on RID

    @classmethod
    def _requires_username(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        raise NotImplementedError()

    @classmethod
    def _requires_password(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        raise NotImplementedError()

    @classmethod
    def _is_supported(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        raise NotImplementedError()

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id: str,
                              username=None, password=None, **kwargs) -> str:
        raise NotImplementedError()

    @classmethod
    def _validate(cls, sku: 'Sku', connection_type: 'ConnectionType', username=None, password=None):
        if not cls._is_supported(sku, connection_type):
            raise ValidationError(f"Authentication type '{connection_type}' is not supported for "
                                  f"sku '{sku}' and database type '{cls.DB_TYPE_NAME}'")

        missing_username = not username and cls._requires_username(sku, connection_type)
        missing_password = not password and cls._requires_password(sku, connection_type)
        if missing_password and missing_username:
            raise RequiredArgumentMissingError("Missing database username and password")
        if missing_password:
            raise RequiredArgumentMissingError("Missing database password")
        if missing_username:
            raise RequiredArgumentMissingError("Missing database username")

    @classmethod
    def get_location(cls, cmd, resource_id: str) -> str:
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        request_url = f"{management_hostname.strip('/')}{resource_id}?api-version={cls.API_VERSION}"

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()["location"]

    @classmethod
    def get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id: str,
                              username=None, password=None, **kwargs) -> str:
        cls._validate(sku, connection_type, username, password)
        return cls._get_connection_string(cmd, sku, connection_type, resource_id, username, password, **kwargs)


class CosmosDbHandler(AbstractDbHandler):
    DB_TYPE_NAME = "CosmosDB"
    API_VERSION = "2021-10-15"

    @classmethod
    def _requires_username(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return False

    @classmethod
    def _requires_password(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return False

    @classmethod
    def _is_supported(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return not (sku == sku.FREE and connection_type != ConnectionType.CONNECTION_STRING)

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id: str,
                               username=None, password=None) -> str:
        parsed_rid = parse_resource_id(resource_id)
        resource_group = parsed_rid["resource_group"]
        name = parsed_rid["name"]
        client = cf_db_accounts(cmd.cli_ctx, None)

        if connection_type == ConnectionType.CONNECTION_STRING:
            return client.list_connection_strings(resource_group, name).connection_strings[0].connection_string
        else:
            return client.get(resource_group, name).document_endpoint


class AzureSqlHandler(AbstractDbHandler):
    DB_TYPE_NAME = "Azure SQL"
    API_VERSION = "2021-11-01"

    @classmethod
    def _requires_username(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return sku == Sku.FREE or connection_type == connection_type.CONNECTION_STRING

    @classmethod
    def _requires_password(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return sku == Sku.FREE or connection_type == connection_type.CONNECTION_STRING

    @classmethod
    def _is_supported(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return not (sku == sku.FREE and connection_type != ConnectionType.CONNECTION_STRING)

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id: str,
                              username=None, password=None) -> str:
        parsed_rid = parse_resource_id(resource_id)
        name = parsed_rid["name"]

        if connection_type == ConnectionType.CONNECTION_STRING:
            return (f"Server=tcp:{name}.database.windows.net,1433;Database={parsed_rid['child_name_1']};"
                    f"User ID={username};Password={password};Encrypt=true;Connection Timeout=30;")
        else:
            return (f"Server=tcp:{name}.database.windows.net,1433;Database={parsed_rid['child_name_1']};"
                    f"Encrypt=true;Connection Timeout=30;")


class MySqlFlexHandler(AbstractDbHandler):
    DB_TYPE_NAME = "MySQL Flex"
    API_VERSION = "2021-05-01"

    @classmethod
    def _requires_username(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return True

    @classmethod
    def _requires_password(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return True

    @classmethod
    def _is_supported(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return connection_type == ConnectionType.CONNECTION_STRING

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id: str,
                              username=None, password=None) -> str:
        parsed_rid = parse_resource_id(resource_id)
        server = parsed_rid["name"]
        db = parsed_rid["child_name_1"]
        # only connection string auth supported
        return (f'Server="{server}.mysql.database.azure.com";UserID = "{username}";'
                f'Password="{password}";Database="{db}";SslMode=MySqlSslMode.Required;'
                'SslCa="{path_to_CA_cert}"')

    @classmethod
    def get_location(cls, cmd, resource_id: str) -> str:
        from msrestazure.tools import resource_id as rid

        parsed_rid = parse_resource_id(resource_id)
        unneeded_props = ["child_name_1", "child_type_1", "children", "last_child_num", "child_parent_1"]
        for k in unneeded_props:
            if k in parsed_rid:
                del parsed_rid[k]
        return super(MySqlFlexHandler, cls).get_location(cmd, rid(**parsed_rid))


class PgSqlSingleHandler(AbstractDbHandler):
    DB_TYPE_NAME = "PostgreSQL Single"
    API_VERSION = "2017-12-01"

    @classmethod
    def _requires_username(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return True

    @classmethod
    def _requires_password(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return connection_type == connection_type.CONNECTION_STRING

    @classmethod
    def _is_supported(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        raise NotImplementedError()

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id: str,
                              username=None, password=None) -> str:
        raise NotImplementedError()  # TODO connection string / MSI auth


class PgSqlFlexHandler(AbstractDbHandler):
    DB_TYPE_NAME = "PostgreSQL Flex"
    API_VERSION = "2021-06-01"

    @classmethod
    def _requires_username(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return True

    @classmethod
    def _requires_password(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return True

    @classmethod
    def _is_supported(cls, sku: 'Sku', connection_type: 'ConnectionType') -> bool:
        return connection_type == ConnectionType.CONNECTION_STRING

    @classmethod
    def get_location(cls, cmd, resource_id: str) -> str:
        from msrestazure.tools import resource_id as rid

        parsed_rid = parse_resource_id(resource_id)
        unneeded_props = ["child_name_1", "child_type_1", "children", "last_child_num", "child_parent_1"]
        for k in unneeded_props:
            if k in parsed_rid:
                del parsed_rid[k]
        return super(PgSqlFlexHandler, cls).get_location(cmd, rid(**parsed_rid))

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id: str,
                              username=None, password=None) -> str:
        parsed_rid = parse_resource_id(resource_id)
        server = parsed_rid["name"]
        db = parsed_rid["child_name_1"]
        return (f"Server={server}.postgres.database.azure.com;Database={db};Port=5432;"
                f"User Id={username};Password={password};Ssl Mode=Require;")


RESOURCE_ID_TO_DB_HANDLER = {
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DocumentDB/databaseAccounts\/.*$": CosmosDbHandler,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.Sql\/servers\/.*\/databases\/.*$": AzureSqlHandler,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DBforMySQL\/flexibleServers\/.*\/databases\/.*$": MySqlFlexHandler,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DBforPostgreSQL\/servers\/.*$": PgSqlSingleHandler,
    r"^\/subscriptions\/.*\/resourceGroups\/.*\/providers\/Microsoft.DBforPostgreSQL\/flexibleServers\/.*\/databases\/.*$": PgSqlFlexHandler,
}


def get_database_type(resource_id: str) -> 'AbstractDbHandler':
    for pattern, db_type in RESOURCE_ID_TO_DB_HANDLER.items():
        if re.fullmatch(pattern, resource_id, flags=re.IGNORECASE):
            return db_type
    raise InvalidArgumentValueError("Database resource ID is invalid or of an unsupported DB")
