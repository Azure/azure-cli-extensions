# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,too-many-locals,too-many-statements,too-many-nested-blocks
import os
from knack.util import CLIError
from knack.log import get_logger
import psycopg2
import pymysql
from pymysql.constants import CLIENT
from azure.cli.core.azclierror import RequiredArgumentMissingError, AzureConnectionError, ArgumentUsageError
from azure.cli.core.extension import EXTENSIONS_DIR


logger = get_logger(__name__)
DEFAULT_MYSQL_DB_NAME = ''  # no default database required
DEFAULT_PG_DB_NAME = 'postgres'


# pylint: disable=raise-missing-from
def connect_to_flexible_server_mysql(cmd, server_name, administrator_login, administrator_login_password=None,
                                     database_name=None, interactive_mode=None, querytext=None):
    if querytext:
        raise ArgumentUsageError("Use az mysql flexible-server execute command for query execution")
    mysql_server_endpoint = cmd.cli_ctx.cloud.suffixes.mysql_server_endpoint
    return connect_to_server_helper(server_type="mysql",
                                    endpoint=mysql_server_endpoint,
                                    default_db_name=DEFAULT_MYSQL_DB_NAME,
                                    server_name=server_name,
                                    administrator_login=administrator_login,
                                    administrator_login_password=administrator_login_password,
                                    database_name=database_name,
                                    interactive=interactive_mode)


def connect_to_flexible_server_postgres(cmd, server_name, administrator_login, administrator_login_password=None,
                                        database_name=None, interactive_mode=None, querytext=None):
    if querytext:
        raise ArgumentUsageError("Use az postgres flexible-server execute command for query execution")
    postgresql_server_endpoint = cmd.cli_ctx.cloud.suffixes.postgresql_server_endpoint
    return connect_to_server_helper(server_type="postgres",
                                    endpoint=postgresql_server_endpoint,
                                    default_db_name=DEFAULT_PG_DB_NAME,
                                    server_name=server_name,
                                    administrator_login=administrator_login,
                                    administrator_login_password=administrator_login_password,
                                    database_name=database_name,
                                    interactive=interactive_mode)


def execute_flexible_server_mysql(cmd, server_name, administrator_login, administrator_login_password,
                                  database_name=None, querytext=None, file_path=None):
    mysql_server_endpoint = cmd.cli_ctx.cloud.suffixes.mysql_server_endpoint
    return connect_to_server_helper(server_type="mysql",
                                    endpoint=mysql_server_endpoint,
                                    default_db_name=DEFAULT_MYSQL_DB_NAME,
                                    server_name=server_name,
                                    administrator_login=administrator_login,
                                    administrator_login_password=administrator_login_password,
                                    database_name=database_name,
                                    query_command=querytext,
                                    file_path=file_path)


def execute_flexible_server_postgres(cmd, server_name, administrator_login, administrator_login_password,
                                     database_name=None, querytext=None, file_path=None):
    postgresql_server_endpoint = cmd.cli_ctx.cloud.suffixes.postgresql_server_endpoint
    return connect_to_server_helper(server_type="postgres",
                                    endpoint=postgresql_server_endpoint,
                                    default_db_name=DEFAULT_PG_DB_NAME,
                                    server_name=server_name,
                                    administrator_login=administrator_login,
                                    administrator_login_password=administrator_login_password,
                                    database_name=database_name,
                                    query_command=querytext,
                                    file_path=file_path)


def connect_to_server_helper(server_type, endpoint, default_db_name, server_name, administrator_login,
                             administrator_login_password, database_name, query_command=None,
                             interactive=None, file_path=None):
    host = f'{server_name}{endpoint}'
    json_data = None

    # setup or validate passed in params:
    if database_name is None:
        database_name = default_db_name
        if database_name:  # in mysql scenario default db will be empty string
            logger.warning("Connecting to %s database by default.",
                           database_name)

    if administrator_login_password is None and interactive is None:
        raise RequiredArgumentMissingError("Please provide password (--admin-password / -p) or "
                                           "run in --interactive mode.")

    # run in either interactive or simple connection mode
    if interactive is not None:
        if query_command is not None:
            logger.warning("Ignoring query command passed in. Cannot run a query and interactive mode simultaneously. "
                           "Please try running either a simple query using -q or run your query in interactive "
                           "mode using --interactive.")

        _connect_interactive(server_type=server_type,
                             host=host,
                             server_name=server_name,
                             database_name=database_name,
                             login_username=administrator_login)

    elif file_path is None:
        json_data = _connect_execute_query(server_type=server_type,
                                           host=host,
                                           server_name=server_name,
                                           database_name=database_name,
                                           login_username=administrator_login,
                                           login_pw=administrator_login_password,
                                           query=query_command)

    if file_path is not None:
        _connect_execute_file(server_type=server_type,
                              host=host,
                              server_name=server_name,
                              database_name=database_name,
                              login_username=administrator_login,
                              login_pw=administrator_login_password,
                              file_path=file_path)

    return json_data


def set_environment_paths(extension_directory):
    extension_python_path = os.path.join(extension_directory, 'rdbms-connect')
    extension_path = os.path.join(extension_python_path, 'bin')  # path to exe

    # if path names are None then return empty string to allow concatenation
    path_var = os.environ.get('PATH', '')
    python_path_var = os.environ.get('PYTHONPATH', '')

    if path_var:
        os.environ["PATH"] += os.pathsep + extension_path
    else:
        os.environ['PATH'] = path_var

    if python_path_var:
        os.environ['PYTHONPATH'] += os.pathsep + extension_python_path
    else:
        os.environ['PYTHONPATH'] = extension_python_path


def _connect_interactive(server_type, host, server_name, database_name, login_username):
    # if interactive mode indicated, use pgcli to connect
    try:
        # setup environment path variable for pgcli and mycli
        set_environment_paths(EXTENSIONS_DIR)

        if server_type == "postgres":
            cmd = f"pgcli -h {host} -u {login_username} -W {database_name}"
        else:
            cmd = f"mycli -h {host} -u {login_username} {database_name} --ssl-verify-server-cert"
        os.system(cmd)
    except Exception as e:
        raise AzureConnectionError(f"Unable to open interactive mode to {server_name}. Error: {e}")


def _connect_execute_query(server_type, host, server_name, database_name, login_username, login_pw, query=None):
    json_data = None

    # connect to server
    try:
        connection_kwargs = {
            'host': host,
            'database': database_name,
            'user': login_username,
            'password': login_pw
        }

        # depending on server type, use the right connection library to test the connetion
        if server_type == "postgres":
            connection = psycopg2.connect(**connection_kwargs)
            connection.set_session(autocommit=True)
        else:
            # set ssl param to allow for connection
            connection_kwargs['ssl'] = {"fake_flag_to_enable_tls": True}
            connection_kwargs['autocommit'] = True
            connection = pymysql.connect(**connection_kwargs)
        logger.warning('Successfully connected to %s.', server_name)
    except Exception as e:
        logger.warning("Failed connection to %s. Check error and validate firewall and public access "
                       "or virtual network settings.", server_name)
        raise AzureConnectionError(f"Unable to connect to flexible server: {e}")

    if query is not None:
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            logger.warning("Ran Database Query: '%s'", query)
            logger.warning("Retrieving first 30 rows of query output, if applicable.")

            # only print out if rows were returned
            if cursor.description:
                result = cursor.fetchmany(30)  # limit to 30 rows of output for now
                row_headers = [x[0] for x in cursor.description]  # this will extract row headers
                # format the result for a clean display
                json_data = []
                for rv in result:
                    json_data.append(dict(zip(row_headers, rv)))
        except Exception as e:
            raise CLIError(f"Unable to execute query '{query}': {e}")
        finally:
            try:
                cursor.close()
                logger.warning("Closed the connection to %s", server_name)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning('Unable to close connection cursor.')
                raise CLIError(str(e))

    return json_data


def _connect_execute_file(server_type, host, server_name, database_name, login_username, login_pw, file_path):

    # connect to server
    try:
        connection_kwargs = {
            'host': host,
            'database': database_name,
            'user': login_username,
            'password': login_pw
        }

        # depending on server type, use the right connection library to test the connetion
        if server_type == "postgres":
            connection = psycopg2.connect(**connection_kwargs)
            connection.set_session(autocommit=True)
        else:
            # set ssl param to allow for connection
            connection_kwargs['ssl'] = {"fake_flag_to_enable_tls": True}
            connection_kwargs['client_flag'] = CLIENT.MULTI_STATEMENTS
            connection_kwargs['autocommit'] = True
            connection = pymysql.connect(**connection_kwargs)

    except Exception as e:
        logger.warning("Failed connection to %s. Check error and validate firewall and public access "
                       "or virtual network settings.", server_name)
        raise AzureConnectionError(f"Unable to connect to flexible server: {e}")

    # Execute the file
    fail_flag = False
    try:
        logger.warning("Running sql file '%s'...", file_path)
        cursor = connection.cursor()

        with open(file_path, "r", encoding="utf-8-sig") as sql_file:
            cursor.execute(sql_file.read())

        if server_type == 'postgres':
            logger.warning('Successfully executed the file.')
    except Exception as e:
        fail_flag = True
        logger.warning("Unable to execute the sql file %s", file_path)
        raise CLIError(e)
    finally:
        if cursor is not None:
            try:
                cursor.close()
                if not fail_flag and server_type == 'mysql':
                    logger.warning('Successfully executed the file.')
                logger.warning("Closed the connection to %s", server_name)
            except Exception as e:  # pylint: disable=broad-except
                if server_type == 'postgres':
                    raise CLIError("Unable to close connection cursor. " + str(e))
                raise CLIError(str(e))
