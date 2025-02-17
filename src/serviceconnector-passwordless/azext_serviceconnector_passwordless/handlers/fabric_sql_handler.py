import struct
import requests
from .target_handler import AUTHTYPES, run_cli_cmd
from .sql_handler import ResourceNotFoundError, SqlHandler
from azure.cli.core import telemetry
from knack.log import get_logger
from azure.cli.core.azclierror import CLIInternalError
from azure.cli.command_modules.serviceconnector._resource_config import AUTH_TYPE

logger = get_logger(__name__)

class FabricSqlHandler(SqlHandler):
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

    def check_db_existence(self):
        fabric_token = self.get_fabric_access_token()
        headers = {"Authorization": "Bearer {}".format(fabric_token)}
        response = requests.get(self.target_id, headers=headers)

        if response:
            response_json = response.json()
            if response_json["id"]:
                return
        
        e = ResourceNotFoundError("No database found with name {}".format(self.dbname))
        telemetry.set_exception(e, "No-Db")
        raise e
        
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

    def get_fabric_access_token(self):
        return run_cli_cmd('az account get-access-token --output json --resource https://api.fabric.microsoft.com/').get('accessToken')

    def set_user_admin(self, user_object_id, **kwargs):
        return
    
    def get_connection_string(self, dbname=""):
        token_bytes = self.get_fabric_access_token().encode('utf-16-le')

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