# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from enum import Enum, auto
import re
from functools import lru_cache

from msrestazure.tools import parse_resource_id
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError, ValidationError
from azure.cli.core.util import send_raw_request
from azure.cli.command_modules.cosmosdb._client_factory import cf_db_accounts


logger = get_logger(__name__)


class ConnectionType(Enum):
    CONNECTION_STRING = "connection string"
    MANAGED_IDENTITY_USER_ASSIGNED = "user assigned identity"
    MANAGED_IDENTITY_SYSTEM_ASSIGNED = "system assigned identity"


class Sku(Enum):
    FREE = "Free"
    STANDARD = "Standard"


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
    def _requires_database_name(cls) -> bool:
        raise NotImplementedError()

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id, database_name,
                               username=None, password=None, **kwargs):
        raise NotImplementedError()

    # saves some time by prevent reparsing of RIDs
    @classmethod
    @lru_cache(maxsize=100)
    def _parse_resource_id(cls, resource_id: str) -> dict:
        return parse_resource_id(resource_id)

    @classmethod
    def _get_supported_connection_types(cls, sku: 'Sku'):
        connection_types = [ConnectionType.CONNECTION_STRING, ConnectionType.MANAGED_IDENTITY_SYSTEM_ASSIGNED,
                            ConnectionType.MANAGED_IDENTITY_USER_ASSIGNED]
        return [c.value for c in connection_types if cls._is_supported(sku, c)]

    @classmethod
    def _validate(cls, sku: 'Sku', connection_type: 'ConnectionType', database_name, username, password):
        if not cls._is_supported(sku, connection_type):
            raise ValidationError(f"Authentication type '{connection_type.value}' is not supported for "
                                  f"sku '{sku.value}' and database type '{cls.DB_TYPE_NAME}'. Please use one of the "
                                  f"following connection types: {cls._get_supported_connection_types(sku)}")

        missing_username = not username and cls._requires_username(sku, connection_type)
        missing_password = not password and cls._requires_password(sku, connection_type)
        if missing_password and missing_username:
            raise RequiredArgumentMissingError("Please provide the missing database username and password")
        if missing_password:
            raise RequiredArgumentMissingError("Please provide the missing database password")
        if missing_username:
            raise RequiredArgumentMissingError("Please provide the missing database username")

        unnecessary_username = username and not cls._requires_username(sku, connection_type)
        unnecessary_password = password and not cls._requires_password(sku, connection_type)
        if unnecessary_username and unnecessary_password:
            logger.warning("Username and password not required. Ignoring the provided username and password.")
        elif unnecessary_username:
            logger.warning("Username not required. Ignoring the provided username.")
        elif unnecessary_password:
            logger.warning("Password not required. Ignoring the provided password.")

        requires_db_name = cls._requires_database_name()
        if not database_name and requires_db_name:
            raise RequiredArgumentMissingError("Database name (--db-name/-b) required for database type "
                                               f"'{cls.DB_TYPE_NAME}'.")
        if database_name and not requires_db_name:
            logger.warning("Database name not required. Ignoring the provided database name.")

    @classmethod
    def _get_location(cls, cmd, resource_id: str) -> str:
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        request_url = f"{management_hostname.strip('/')}{resource_id}?api-version={cls.API_VERSION}"

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()["location"]

    @classmethod
    def get_location(cls, cmd, resource_id: str) -> str:
        return cls._get_location(cmd, resource_id)

    # Needed when doing a GET on the DB doesn't give the location
    @classmethod
    def _get_location_from_server(cls, cmd, resource_id: str) -> str:
        from msrestazure.tools import resource_id as rid

        parsed_rid = cls._parse_resource_id(resource_id)
        unneeded_props = {"child_name_1", "child_type_1", "children", "last_child_num", "child_parent_1"}
        server_rid_parts = {}
        for k in parsed_rid:
            if k not in unneeded_props:
                server_rid_parts[k] = parsed_rid[k]

        return cls._get_location(cmd, rid(**server_rid_parts))

    @classmethod
    def get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id, database_name,
                              username=None, password=None, **kwargs) -> str:
        cls._validate(sku, connection_type, database_name, username, password)
        return cls._get_connection_string(cmd, sku, connection_type, resource_id, database_name,
                                          username, password, **kwargs)


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
    def _requires_database_name(cls) -> bool:
        return False

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id, database_name,
                               username=None, password=None, **kwargs) -> str:
        parsed_rid = cls._parse_resource_id(resource_id)
        resource_group = parsed_rid["resource_group"]
        name = parsed_rid["name"]
        client = cf_db_accounts(cmd.cli_ctx, None)

        if connection_type == ConnectionType.CONNECTION_STRING:
            return client.list_connection_strings(resource_group, name).connection_strings[0].connection_string
        else:
            return f"AccountEndpoint={client.get(resource_group, name).document_endpoint};"


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
    def _requires_database_name(cls) -> bool:
        return True

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id, database_name,
                               username=None, password=None, **kwargs) -> str:
        parsed_rid = cls._parse_resource_id(resource_id)
        name = parsed_rid["name"]

        if connection_type == ConnectionType.CONNECTION_STRING:
            return (f"Server=tcp:{name}.database.windows.net,1433;Database={database_name};"
                    f"User ID={username};Password={password};")
        else:
            return f"Server=tcp:{name}.database.windows.net,1433;Database={database_name};"


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
    def _requires_database_name(cls) -> bool:
        return True

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id, database_name,
                               username=None, password=None, **kwargs) -> str:
        parsed_rid = cls._parse_resource_id(resource_id)
        server = parsed_rid["name"]
        # only connection string auth supported
        return (f'Server={server}.mysql.database.azure.com;UserID = {username};'
                f'Password={password}";Database={database_name};')

    @classmethod
    def get_location(cls, cmd, resource_id: str) -> str:
        return cls._get_location_from_server(cmd, resource_id)


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
        return not (sku == sku.FREE and connection_type != ConnectionType.CONNECTION_STRING)

    @classmethod
    def _requires_database_name(cls) -> bool:
        return True

    @classmethod
    def get_location(cls, cmd, resource_id: str) -> str:
        return cls._get_location_from_server(cmd, resource_id)

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id, database_name,
                               username=None, password=None, **kwargs) -> str:
        parsed_rid = cls._parse_resource_id(resource_id)
        server = parsed_rid["name"]
        if connection_type == ConnectionType.CONNECTION_STRING:
            return (f"Server={server}.postgres.database.azure.com;Database={database_name};Port=5432;"
                    f"User Id={username}@{server};Password={password};")
        else:
            return (f"Server={server}.postgres.database.azure.com;Database={database_name};Port=5432;"
                    f"User Id={username}@{server};")


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
    def _requires_database_name(cls) -> bool:
        return True

    @classmethod
    def get_location(cls, cmd, resource_id: str) -> str:
        return cls._get_location_from_server(cmd, resource_id)

    @classmethod
    def _get_connection_string(cls, cmd, sku: 'Sku', connection_type: 'ConnectionType', resource_id, database_name,
                               username=None, password=None, **kwargs) -> str:
        parsed_rid = cls._parse_resource_id(resource_id)
        server = parsed_rid["name"]
        return (f"Server={server}.postgres.database.azure.com;Database={database_name};Port=5432;"
                f"User Id={username};Password={password};")


# pylint: disable=line-too-long
RESOURCE_ID_TO_DB_HANDLER = {
    r"^/subscriptions/.+/resourceGroups/.+/providers/Microsoft\.DocumentDB/databaseAccounts/[^/]+$": CosmosDbHandler,
    r"^/subscriptions/.+/resourceGroups/.+/providers/Microsoft\.Sql/servers/[^/]+$": AzureSqlHandler,
    r"^/subscriptions/.+/resourceGroups/.+/providers/Microsoft\.DBforMySQL/flexibleServers/[^/]+$": MySqlFlexHandler,
    r"^/subscriptions/.+/resourceGroups/.+/providers/Microsoft\.DBforPostgreSQL/servers/[^/]+$": PgSqlSingleHandler,
    r"^/subscriptions/.+/resourceGroups/.+/providers/Microsoft\.DBforPostgreSQL/flexibleServers/[^/]+$": PgSqlFlexHandler,
}


def get_database_type(resource_id: str) -> 'AbstractDbHandler':
    for pattern, db_type in RESOURCE_ID_TO_DB_HANDLER.items():
        if re.fullmatch(pattern, resource_id, flags=re.IGNORECASE):
            return db_type
    raise InvalidArgumentValueError("Database resource ID is invalid or of an unsupported DB")
