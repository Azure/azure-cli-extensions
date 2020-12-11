# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,too-many-locals,too-many-statements
import os
from knack.util import CLIError
from knack.log import get_logger
import psycopg2
import pymysql

logger = get_logger(__name__)
DEFAULT_MYSQL_DB_NAME = 'flexibleserverdb'
DEFAULT_PG_DB_NAME = 'postgres'


def connect_to_flexible_server_mysql(cmd, server_name, administrator_login, administrator_login_password=None,
                                     database_name=None, querytext=None, interactive_mode=None):
    mysql_server_endpoint = cmd.cli_ctx.cloud.suffixes.mysql_server_endpoint
    return connect_to_server_helper("mysql", mysql_server_endpoint, DEFAULT_MYSQL_DB_NAME, server_name,
                                    administrator_login, administrator_login_password, database_name,
                                    querytext, interactive_mode)


def connect_to_flexible_server_postgres(cmd, server_name, administrator_login, administrator_login_password=None,
                                        database_name=None, querytext=None, interactive_mode=None):
    postgresql_server_endpoint = cmd.cli_ctx.cloud.suffixes.postgresql_server_endpoint
    return connect_to_server_helper("postgres", postgresql_server_endpoint, DEFAULT_PG_DB_NAME, server_name,
                                    administrator_login, administrator_login_password, database_name,
                                    querytext, interactive_mode)


def connect_to_server_helper(server_type, endpoint, default_db_name, server_name, administrator_login,
                             administrator_login_password, database_name, query_command, interactive):
    host = '{}{}'.format(server_name, endpoint)
    cursor = None
    json_data = None

    # setup or validate passed in params:
    if database_name is None:
        logger.warning("Connecting to %s database by default.",
                       default_db_name)
        database_name = default_db_name

    if administrator_login_password is None and interactive is None:
        raise CLIError("Please provide password (--admin-password / -p) or run in --interactive mode.")

    # run in either interactive or simple connection mode
    if interactive is not None:
        if query_command is not None:
            logger.warning("Ignoring query command passed in. Cannot run a query and interactive mode simultaneously. "
                           "Please try running either a simple query using -q or run your query in interactive "
                           "mode using --interactive.")

        # if interactive mode indicated, use pgcli to connect
        try:
            if server_type == "postgres":
                cmd = "pgcli -h {0} -u {1} -W {2}".format(host, administrator_login, database_name)
            else:
                cmd = "mycli -h {0} -u {1} {2} --ssl-verify-server-cert".format(host, administrator_login,
                                                                                database_name)
            os.system(cmd)
        except Exception as e:
            raise CLIError("Unable to open interactive mode to {0}. Error: {1}".format(server_name, e))
    else:
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
                # set ssl param to allow for connection
                connection_kwargs['ssl'] = {"fake_flag_to_enable_tls": True}
                connection = pymysql.connect(**connection_kwargs)
            logger.warning('Successfully connected to %s.', server_name)
        except Exception as e:
            logger.warning("Failed connection to %s. Check error and validate firewall and public access "
                           "or virtual network settings.", server_name)
            raise CLIError("Unable to connect to flexible server: {}".format(e))

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
