import struct
import sys
import re

from azure.cli.command_modules.serviceconnector._utils import is_packaged_installed
from .target_handler import AUTHTYPES, TargetHandler, run_cli_cmd
from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import (
    AzureConnectionError,
    CLIInternalError
)
from azure.cli.core.extension.operations import _run_pip
from azure.cli.command_modules.serviceconnector._resource_config import AUTH_TYPE
logger = get_logger(__name__)

class FabricSqlHandler(TargetHandler):
    def __init__(self, cmd, target_id, target_type, auth_info, connection_name, connstr_props, skip_prompt, new_user):
        super().__init__(cmd, target_id, target_type,
                         auth_info, connection_name, skip_prompt, new_user)

        self.target_id = target_id

        if not connstr_props:
            raise CLIInternalError("Missing additional connection string properties for Fabric SQL target.")

        Server = connstr_props.get('Server') or connstr_props.get('Data Source')
        Database = connstr_props.get('Database') or connstr_props.get('Initial Catalog')
        if not Server or not Database:
            raise CLIInternalError("Missing 'Server' or 'Database' in additonal connection string properties keys."
                                   "Use --connection-string-props 'Server=xxx' 'Database=xxx' to provide the values.")

        # Construct the ODBC connection string
        self.ODBCConnectionString = self.construct_odbc_connection_string(Server, Database)
        logger.warning("ODBC connection string: %s", self.ODBCConnectionString)

    def construct_odbc_connection_string(self, server, database):
        # Map fields to ODBC fields
        odbc_dict = {
            'Driver': '{driver}',
            'Server': server,
            'Database': database,
        }

        odbc_connection_string = ';'.join([f'{key}={value}' for key, value in odbc_dict.items()])
        return odbc_connection_string

    def create_aad_user(self):
        query_list = self.get_create_query()
        connection_args = self.get_connection_string()

        logger.warning("Connecting to database...")
        self.create_aad_user_in_sql(connection_args, query_list)

    def create_aad_user_in_sql(self, connection_args, query_list):
        if not self.new_user:
            query_list = query_list[1:]
        if not is_packaged_installed('pyodbc'):
            _run_pip(["install", "pyodbc"])

        # pylint: disable=import-error, c-extension-no-member
        try:
            import pyodbc
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Dependency pyodbc can't be installed, please install it manually with `" + sys.executable + " -m pip install pyodbc`.") from e
        drivers = [x for x in pyodbc.drivers() if x in [
            'ODBC Driver 17 for SQL Server', 'ODBC Driver 18 for SQL Server']]
        if not drivers:
            ex = CLIInternalError(
                "Please manually install odbc 17/18 for SQL server, reference: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server/")
            telemetry.set_exception(ex, "No-ODBC-Driver")
            raise ex
        try:
            with pyodbc.connect(connection_args.get("connection_string").format(driver=drivers[0]), attrs_before=connection_args.get("attrs_before")) as conn:
                with conn.cursor() as cursor:
                    logger.warning(
                        "Adding new Microsoft Entra user %s to database...", self.aad_username)
                    for execution_query in query_list:
                        try:
                            logger.warning("Running query: %s", execution_query)
                            cursor.execute(execution_query)
                        except pyodbc.ProgrammingError as e:
                            logger.warning("Query execution failed: %s", str(e))
                        conn.commit()
        except pyodbc.Error as e:
            search_ip = re.search(
                "Client with IP address '(.*?)' is not allowed to access the server", str(e))
            if search_ip is not None:
                self.ip = search_ip.group(1)
            raise AzureConnectionError("Fail to connect sql." + str(e)) from e

    def get_connection_string(self, dbname=""):
        token_bytes = run_cli_cmd(
            'az account get-access-token --output json --resource https://api.fabric.microsoft.com/').get('accessToken').encode('utf-16-le')

        token_struct = struct.pack(
            f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        # This connection option is defined by microsoft in msodbcsql.h
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        conn_string = self.ODBCConnectionString
        return {'connection_string': conn_string, 'attrs_before': {SQL_COPT_SS_ACCESS_TOKEN: token_struct}}

    def get_create_query(self):
        if self.auth_type in [AUTHTYPES[AUTH_TYPE.SystemIdentity], AUTHTYPES[AUTH_TYPE.UserIdentity]]:
            self.aad_username = self.identity_name
        else:
            raise CLIInternalError("Unsupported auth type: " + self.auth_type)

        delete_q = "DROP USER IF EXISTS \"{}\";".format(self.aad_username)
        role_q = "CREATE USER \"{}\" FROM EXTERNAL PROVIDER;".format(self.aad_username)
        grant_q1 = "ALTER ROLE db_datareader ADD MEMBER \"{}\"".format(self.aad_username)
        grant_q2 = "ALTER ROLE db_datawriter ADD MEMBER \"{}\"".format(self.aad_username)
        grant_q3 = "ALTER ROLE db_ddladmin ADD MEMBER \"{}\"".format(self.aad_username)

        return [delete_q, role_q, grant_q1, grant_q2, grant_q3]