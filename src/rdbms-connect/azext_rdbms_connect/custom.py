# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,too-many-locals
from knack.util import CLIError
from knack.log import get_logger
import mysql.connector as mysql_connector
import psycopg2

logger = get_logger(__name__)
DEFAULT_MYSQL_DB_NAME = 'flexibleserverdb'
DEFAULT_PG_DB_NAME = 'postgres'


def connect_to_flexible_server_mysql(cmd, server_name, administrator_login, administrator_login_password,
                                     database_name=None, mysql_query=None):
    mysql_server_endpoint = cmd.cli_ctx.cloud.suffixes.mysql_server_endpoint
    return connect_to_server_helper("mysql", mysql_server_endpoint, DEFAULT_MYSQL_DB_NAME, server_name,
                                    administrator_login, administrator_login_password, database_name, mysql_query)


def connect_to_flexible_server_postgres(cmd, server_name, administrator_login, administrator_login_password,
                                          database_name=None, postgres_query=None):
    postgresql_server_endpoint = cmd.cli_ctx.cloud.suffixes.postgresql_server_endpoint
    return connect_to_server_helper("postgres", postgresql_server_endpoint, DEFAULT_PG_DB_NAME, server_name,
                                    administrator_login, administrator_login_password, database_name, postgres_query)


def connect_to_server_helper(server_type, endpoint, default_db_name, server_name, administrator_login,
                             administrator_login_password, database_name, query_command):
    host = '{}{}'.format(server_name, endpoint)
    cursor = None
    json_data = None
    if database_name is None:
        logger.warning("Connecting to %s database by default.",
                       default_db_name)
        database_name = default_db_name

    # connect to server
    try:
        connection_kwargs = {
            'host': host,
            'database': database_name,
            'user': administrator_login,
            'password': administrator_login_password
        }

        # depending on server type, use the right connection library to test the connetion
        if server_type == "postgres":
            connection = psycopg2.connect(**connection_kwargs)
            connection.set_session(autocommit=True)
        else:
            connection = mysql_connector.connect(**connection_kwargs)

        logger.warning('Successfully connected to %s.', server_name)
    except Exception as e:
        logger.warning('Failed connection to %s. Check error and validate firewall and public access \
                       or virtual network settings.', server_name)
        raise CLIError("Unable to connect to flexible server: {}".format(e))

    # execute query if passed in
    if query_command is not None:
        try:
            cursor = connection.cursor()
            cursor.execute(query_command)
            logger.warning("Ran Database Query: '%s'", query_command)
            logger.warning("Retrieving first 30 rows of query output.")
            result = cursor.fetchmany(30)  # limit to 30 rows of output for now
            row_headers = [x[0] for x in cursor.description]  # this will extract row headers
            # format the result for a clean display
            json_data = []
            for rv in result:
                json_data.append(dict(zip(row_headers, rv)))
        except Exception as e:
            raise CLIError("Unable to execute query '{0}': {1}".format(query_command, e))
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                    logger.warning("Closed the connection to %s", server_name)
                except Exception:  # pylint: disable=broad-except
                    logger.warning('Unable to close connection cursor.')
    return json_data
