import struct
import sys
import re
from ..handlers.target_handler import (
    AUTHTYPES,
    TargetHandler
)
from azure.mgmt.core.tools import parse_resource_id
from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import (
    AzureConnectionError,
    ValidationError,
    CLIInternalError,
    ResourceNotFoundError
)
from azure.cli.core.extension.operations import _run_pip
from azure.cli.command_modules.serviceconnector._utils import (
    generate_random_string,
    is_packaged_installed
)
from azure.cli.command_modules.serviceconnector._resource_config import AUTH_TYPE
from .._utils import run_cli_cmd, confirm_admin_set
logger = get_logger(__name__)

class SqlHandler(TargetHandler):
    def __init__(self, cmd, target_id, target_type, auth_info, connection_name, skip_prompt, new_user):
        super().__init__(cmd, target_id, target_type,
                         auth_info, connection_name, skip_prompt, new_user)
        self.endpoint = cmd.cli_ctx.cloud.suffixes.sql_server_hostname
        target_segments = parse_resource_id(target_id)
        self.server = target_segments.get('name')
        self.dbname = target_segments.get('child_name_1')
        self.ip = ""

    def check_db_existence(self):
        try:
            db_info = run_cli_cmd(
                'az sql db show --ids "{}"'.format(self.target_id))
            if db_info is None:
                e = ResourceNotFoundError(
                    "No database found with name {}".format(self.dbname))
                telemetry.set_exception(e, "No-Db")
                raise e
        except CLIInternalError as e:
            telemetry.set_exception(e, "No-Db")
            raise e

    def set_user_admin(self, user_object_id, **kwargs):
        # pylint: disable=not-an-iterable
        admins = run_cli_cmd(
            'az sql server ad-admin list --ids "{}"'.format(self.target_id))
        if not user_object_id:
            if not admins:
                e = ValidationError(
                    'No Microsoft Entra admin found. Please set current user as Microsoft Entra admin and try again.')
                telemetry.set_exception(e, "Missing-Aad-Admin")
                raise e
            else:
                logger.warning(
                    'Unable to check if current user is Microsoft Entra admin. Please confirm current user as Microsoft Entra admin manually.')
                return
        admin_info = next((ad for ad in admins if ad.get('sid') == user_object_id), None)
        if not admin_info:
            set_admin = True
            if not self.skip_prompt:
                set_admin = confirm_admin_set()
            if set_admin:
                logger.warning('Setting current user as database server Microsoft Entra admin:'
                               ' user=%s object id=%s', self.login_username, user_object_id)
                admin_info = run_cli_cmd('az sql server ad-admin create -g "{}" --server-name "{}" --display-name "{}" --object-id "{}" --subscription "{}"'.format(
                    self.resource_group, self.server, self.login_username, user_object_id, self.subscription))
        self.admin_username = admin_info.get('login', self.login_username) if admin_info else self.login_username

    def create_aad_user(self):
        query_list = self.get_create_query()
        connection_args = self.get_connection_string()
        ip_name = generate_random_string(prefix='svc_').lower()
        try:
            logger.warning("Connecting to database...")
            self.create_aad_user_in_sql(connection_args, query_list)
        except AzureConnectionError as e:
            from azure.cli.core.util import in_cloud_console
            if in_cloud_console():
                self.set_target_firewall(
                    True, ip_name, '0.0.0.0', '0.0.0.0')
            else:
                if not self.ip:
                    error_code = ''
                    error_res = re.search(
                        r'\((\d{5})\)', str(e))
                    if error_res:
                        error_code = error_res.group(1)
                    telemetry.set_exception(e, "Connect-Db-Fail-" + error_code)
                    raise e
                logger.warning(e)
                # allow local access
                ip_address = self.ip
                self.set_target_firewall(True, ip_name, ip_address, ip_address)
            try:
                # create again
                self.create_aad_user_in_sql(connection_args, query_list)
            except AzureConnectionError as e:
                logger.warning(e)
                ex = AzureConnectionError(
                    "Please confirm local environment can connect to database and try again.")
                error_code = ''
                error_res = re.search(
                    r'\((\d{5})\)', str(e))
                if error_res:
                    error_code = error_res.group(1)
                telemetry.set_exception(e, "Connect-Db-Fail-" + error_code)
                raise ex from e
            finally:
                self.set_target_firewall(False, ip_name)

    def set_target_firewall(self, is_add, ip_name, start_ip=None, end_ip=None):
        if is_add:
            target = run_cli_cmd(
                'az sql server show --ids "{}"'.format(self.target_id))
            # logger.warning("Update database server firewall rule to connect...")
            if target.get('publicNetworkAccess') == "Disabled":
                ex = AzureConnectionError(
                    "The target resource doesn't allow public access. Please enable it manually and try again.")
                telemetry.set_exception(ex, "Public-Access-Disabled")
                raise ex
            logger.warning("Add firewall rule %s %s - %s...%s", ip_name, start_ip, end_ip,
                           ('(it will be removed after connection is created)' if self.auth_type != AUTHTYPES[
                               AUTH_TYPE.UserAccount] else '(Please delete it manually if it has security risk.)'))
            run_cli_cmd(
                'az sql server firewall-rule create -g "{0}" -s "{1}" -n "{2}" '
                '--subscription "{3}" --start-ip-address {4} --end-ip-address {5}'.format(
                    self.resource_group, self.server, ip_name, self.subscription, start_ip, end_ip)
            )
        else:
            if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
                return
            logger.warning(
                "Remove database server firewall rule %s to recover...", ip_name)
            try:
                run_cli_cmd(
                    'az sql server firewall-rule delete -g "{0}" -s "{1}" -n "{2}" --subscription "{3}"'.format(
                        self.resource_group, self.server, ip_name, self.subscription)
                )
            except CLIInternalError as e:
                logger.warning(
                    "Can't remove firewall rule %s. Please manually delete it to avoid security issue. %s", ip_name, str(e))

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
            'az account get-access-token --output json --resource https://database.windows.net/').get('accessToken').encode('utf-16-le')

        token_struct = struct.pack(
            f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        # This connection option is defined by microsoft in msodbcsql.h
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        conn_string = 'DRIVER={{{driver}}};server=' + \
            self.server + self.endpoint + ';database=' + self.dbname + ';'
        logger.debug(conn_string)
        return {'connection_string': conn_string, 'attrs_before': {SQL_COPT_SS_ACCESS_TOKEN: token_struct}}

    def get_create_query(self):
        if self.auth_type in [AUTHTYPES[AUTH_TYPE.SystemIdentity], AUTHTYPES[AUTH_TYPE.UserIdentity], AUTHTYPES[AUTH_TYPE.ServicePrincipalSecret]]:
            self.aad_username = self.identity_name
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
            self.aad_username = self.login_username
        delete_q = "DROP USER IF EXISTS \"{}\";".format(
            self.aad_username)
        role_q = "CREATE USER \"{}\" FROM EXTERNAL PROVIDER;".format(
            self.aad_username)
        grant_q = "GRANT CONTROL ON DATABASE::\"{}\" TO \"{}\";".format(
            self.dbname, self.aad_username)

        return [delete_q, role_q, grant_q]
        