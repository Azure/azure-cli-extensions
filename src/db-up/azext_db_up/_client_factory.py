# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from os import getenv
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType

# CLIENT FACTORIES

RM_URI_OVERRIDE = 'AZURE_CLI_RDBMS_RM_URI'
SUB_ID_OVERRIDE = 'AZURE_CLI_RDBMS_SUB_ID'
CLIENT_ID = 'AZURE_CLIENT_ID'
TENANT_ID = 'AZURE_TENANT_ID'
CLIENT_SECRET = 'AZURE_CLIENT_SECRET'


def get_mysql_management_client(cli_ctx, **_):
    from azext_db_up.vendored_sdks.azure_mgmt_rdbms.mysql import MySQLManagementClient

    # Allow overriding resource manager URI using environment variable
    # for testing purposes. Subscription id is also determined by environment
    # variable.
    rm_uri_override = getenv(RM_URI_OVERRIDE)
    if rm_uri_override:
        client_id = getenv(CLIENT_ID)
        if client_id:
            from azure.common.credentials import ServicePrincipalCredentials
            credentials = ServicePrincipalCredentials(
                client_id=client_id,
                secret=getenv(CLIENT_SECRET),
                tenant=getenv(TENANT_ID))
        else:
            from msrest.authentication import Authentication    # pylint: disable=import-error
            credentials = Authentication()

        return MySQLManagementClient(
            subscription_id=getenv(SUB_ID_OVERRIDE),
            base_url=rm_uri_override,
            credentials=credentials)
    # Normal production scenario.
    return get_mgmt_service_client(cli_ctx, MySQLManagementClient)


def get_postgresql_management_client(cli_ctx, **_):
    from azext_db_up.vendored_sdks.azure_mgmt_rdbms.postgresql import PostgreSQLManagementClient

    # Allow overriding resource manager URI using environment variable
    # for testing purposes. Subscription id is also determined by environment
    # variable.
    rm_uri_override = getenv(RM_URI_OVERRIDE)
    if rm_uri_override:
        client_id = getenv(CLIENT_ID)
        if client_id:
            from azure.common.credentials import ServicePrincipalCredentials
            credentials = ServicePrincipalCredentials(
                client_id=client_id,
                secret=getenv(CLIENT_SECRET),
                tenant=getenv(TENANT_ID))
        else:
            from msrest.authentication import Authentication    # pylint: disable=import-error
            credentials = Authentication()

        return PostgreSQLManagementClient(
            subscription_id=getenv(SUB_ID_OVERRIDE),
            base_url=rm_uri_override,
            credentials=credentials)
    # Normal production scenario.
    return get_mgmt_service_client(cli_ctx, PostgreSQLManagementClient)


def get_sql_management_client(cli_ctx):
    from azext_db_up.vendored_sdks.azure_mgmt_sql.sql import SqlManagementClient

    # Normal production scenario.
    return get_mgmt_service_client(cli_ctx, SqlManagementClient)


def cf_mysql_servers(cli_ctx, _):
    return get_mysql_management_client(cli_ctx).servers


def cf_postgres_servers(cli_ctx, _):
    return get_postgresql_management_client(cli_ctx).servers


def cf_sql_servers(cli_ctx, _):
    return get_sql_management_client(cli_ctx).servers


def cf_mysql_firewall_rules(cli_ctx, _):
    return get_mysql_management_client(cli_ctx).firewall_rules


def cf_postgres_firewall_rules(cli_ctx, _):
    return get_postgresql_management_client(cli_ctx).firewall_rules


def cf_sql_firewall_rules(cli_ctx, _):
    return get_sql_management_client(cli_ctx).firewall_rules


def cf_mysql_config(cli_ctx, _):
    return get_mysql_management_client(cli_ctx).configurations


def cf_postgres_config(cli_ctx, _):
    return get_postgresql_management_client(cli_ctx).configurations


def cf_mysql_db(cli_ctx, _):
    return get_mysql_management_client(cli_ctx).databases


def cf_postgres_db(cli_ctx, _):
    return get_postgresql_management_client(cli_ctx).databases


def cf_sql_db(cli_ctx, _):
    return get_sql_management_client(cli_ctx).databases


def resource_client_factory(cli_ctx, **_):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
