# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client


def get_mariadb_management_client(cli_ctx, **_):
    from azure.mgmt.rdbms.mariadb import MariaDBManagementClient

    return get_mgmt_service_client(cli_ctx, MariaDBManagementClient)


def get_mysql_management_client(cli_ctx, **_):
    from azure.mgmt.rdbms.mysql import MySQLManagementClient

    return get_mgmt_service_client(cli_ctx, MySQLManagementClient)


def get_mysql_flexible_management_client(cli_ctx, **_):
    from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient

    return get_mgmt_service_client(cli_ctx, MySQLManagementClient)


def get_postgresql_management_client(cli_ctx, **_):
    from azure.mgmt.rdbms.postgresql import PostgreSQLManagementClient

    return get_mgmt_service_client(cli_ctx, PostgreSQLManagementClient)


def get_postgresql_flexible_management_client(cli_ctx, **_):
    from azure.mgmt.rdbms.postgresql_flexibleservers import PostgreSQLManagementClient

    return get_mgmt_service_client(cli_ctx, PostgreSQLManagementClient)


def cf_mysql_flexible_location_capabilities(cli_ctx, _):
    return get_mysql_flexible_management_client(cli_ctx).location_based_capabilities


def cf_postgres_flexible_location_capabilities(cli_ctx, _):
    return get_postgresql_flexible_management_client(cli_ctx).location_based_capabilities
