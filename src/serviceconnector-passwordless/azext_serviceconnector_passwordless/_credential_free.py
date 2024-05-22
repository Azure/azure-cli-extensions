# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=no-member, too-many-lines, anomalous-backslash-in-string, redefined-outer-name, no-else-raise, attribute-defined-outside-init

import struct
import sys
import re
from knack.log import get_logger
from msrestazure.tools import parse_resource_id
from azure.cli.core import telemetry
from azure.cli.core.azclierror import (
    AzureConnectionError,
    ValidationError,
    CLIInternalError,
    ResourceNotFoundError
)
from azure.cli.core.extension.operations import _install_deps_for_psycopg2, _run_pip
from azure.cli.core._profile import Profile
from azure.cli.command_modules.serviceconnector._utils import (
    generate_random_string,
    is_packaged_installed,
    get_object_id_of_current_user
)
from azure.cli.command_modules.serviceconnector._resource_config import (
    RESOURCE,
    AUTH_TYPE
)
from azure.cli.command_modules.serviceconnector._validators import (
    get_source_resource_name,
    get_target_resource_name,
)
from ._utils import run_cli_cmd, get_local_ip, confirm_all_ip_allow, confirm_admin_set
logger = get_logger(__name__)

AUTHTYPES = {
    AUTH_TYPE.SystemIdentity: 'systemAssignedIdentity',
    AUTH_TYPE.UserIdentity: 'userAssignedIdentity',
    AUTH_TYPE.ServicePrincipalSecret: 'servicePrincipalSecret',
    AUTH_TYPE.UserAccount: 'userAccount',
}


# pylint: disable=line-too-long, consider-using-f-string, too-many-statements
# For db(mysqlFlex/psql/psqlFlex/sql) linker with auth type=systemAssignedIdentity, enable Microsoft Entra auth and create db user on data plane
# For other linker, ignore the steps
def get_enable_mi_for_db_linker_func(yes=False):
    def enable_mi_for_db_linker(cmd, source_id, target_id, auth_info, client_type, connection_name):
        # return if connection is not for db mi
        if auth_info['auth_type'] not in [AUTHTYPES[AUTH_TYPE.SystemIdentity],
                                          AUTHTYPES[AUTH_TYPE.UserIdentity],
                                          AUTHTYPES[AUTH_TYPE.UserAccount],
                                          AUTHTYPES[AUTH_TYPE.ServicePrincipalSecret]
                                          ]:
            return None

        source_type = get_source_resource_name(cmd)
        target_type = get_target_resource_name(cmd)
        source_handler = getSourceHandler(source_id, source_type)
        if source_handler is None:
            return None
        target_handler = getTargetHandler(
            cmd, target_id, target_type, auth_info, client_type, connection_name, skip_prompt=yes)
        if target_handler is None:
            return None
        target_handler.check_db_existence()

        user_object_id = auth_info.get(
            'principal_id') if auth_info['auth_type'] == AUTHTYPES[AUTH_TYPE.UserAccount] else auth_info.get("user_object_id")
        if user_object_id is None:
            try:
                user_object_id = get_object_id_of_current_user()
            except CLIInternalError as e:
                telemetry.set_exception(e, "No-User-Oid")
                if auth_info['auth_type'] == AUTHTYPES[AUTH_TYPE.UserAccount]:
                    raise e
                error_msg = "Unable to get current login user object id. "
                if auth_info['auth_type'] == AUTHTYPES[AUTH_TYPE.UserIdentity]:
                    error_msg += "You can provide it via --user-identity user-object-id=xx"
                if auth_info['auth_type'] == AUTHTYPES[AUTH_TYPE.SystemIdentity]:
                    error_msg += "You can provide it via --system-identity user-object-id=xx"
                logger.warning(error_msg)

        target_handler.user_object_id = user_object_id
        if auth_info['auth_type'] == AUTHTYPES[AUTH_TYPE.SystemIdentity]:
            # enable source mi
            source_object_id = source_handler.get_identity_pid()
            target_handler.identity_object_id = source_object_id
            try:
                if target_type in [RESOURCE.Sql]:
                    target_handler.identity_name = source_handler.get_identity_name()
                elif target_type in [RESOURCE.Postgres, RESOURCE.MysqlFlexible]:
                    identity_info = run_cli_cmd(
                        'az ad sp show --id {}'.format(source_object_id), 15, 10)
                    target_handler.identity_client_id = identity_info.get(
                        'appId')
                    target_handler.identity_name = identity_info.get(
                        'displayName')
            except CLIInternalError as e:
                if 'AADSTS530003' in e.error_msg:
                    logger.warning(
                        'Please ask your IT department for help to join this device to Microsoft Entra ID.')
                raise e
        elif auth_info['auth_type'] == AUTHTYPES[AUTH_TYPE.UserIdentity]:
            mi_client_id = auth_info.get('client_id')
            mi_sub_id = auth_info.get('subscription_id')
            umi_info = run_cli_cmd(
                f'az identity list --subscription {mi_sub_id} --query "[?clientId==\'{mi_client_id}\']"')
            if umi_info is None or len(umi_info) == 0:
                e = ResourceNotFoundError(
                    "No identity found for client id {}".format(mi_client_id))
                telemetry.set_exception(e, "No-Umi")
                raise e
            source_object_id = umi_info[0].get('principalId')
            target_handler.identity_object_id = source_object_id
            target_handler.identity_client_id = mi_client_id
            target_handler.identity_name = umi_info[0].get('name')
        elif auth_info['auth_type'] == AUTHTYPES[AUTH_TYPE.ServicePrincipalSecret]:
            sp_client_id = auth_info.get('client_id')
            sp_object_id = auth_info.get('principal_id')
            try:
                sp_info = run_cli_cmd(
                    'az ad sp show --id {}'.format(sp_client_id))
                if sp_info is None:
                    e = ResourceNotFoundError(
                        "Not found the service principal with client id {}".format(sp_client_id))
                    telemetry.set_exception(e, "No-SP")
                    raise e
                target_handler.identity_object_id = sp_object_id
                target_handler.identity_client_id = sp_client_id
                target_handler.identity_name = sp_info.get('displayName')
            except CLIInternalError as e:
                if 'AADSTS530003' in e.error_msg:
                    logger.warning(
                        'Please ask your IT department for help to join this device to Microsoft Entra ID.')
                raise e

        # enable target Microsoft Entra authentication and set login user as db Microsoft Entra admin
        target_handler.enable_target_aad_auth()
        target_handler.set_user_admin(
            user_object_id, mysql_identity_id=auth_info.get('mysql-identity-id'))

        # create an Microsoft Entra user in db
        target_handler.create_aad_user()
        return target_handler.get_auth_config(user_object_id)

    return enable_mi_for_db_linker


# pylint: disable=unused-argument, too-many-instance-attributes
def getTargetHandler(cmd, target_id, target_type, auth_info, client_type, connection_name, skip_prompt):
    if target_type in {RESOURCE.Sql}:
        return SqlHandler(cmd, target_id, target_type, auth_info, connection_name, skip_prompt)
    if target_type in {RESOURCE.Postgres}:
        return PostgresSingleHandler(cmd, target_id, target_type, auth_info, connection_name, skip_prompt)
    if target_type in {RESOURCE.PostgresFlexible}:
        return PostgresFlexHandler(cmd, target_id, target_type, auth_info, connection_name, skip_prompt)
    if target_type in {RESOURCE.MysqlFlexible}:
        return MysqlFlexibleHandler(cmd, target_id, target_type, auth_info, connection_name, skip_prompt)
    return None


class TargetHandler:

    def __init__(self, cmd, target_id, target_type, auth_info, connection_name, skip_prompt):
        self.cmd = cmd
        self.target_id = target_id
        self.target_type = target_type
        self.tenant_id = Profile(
            cli_ctx=cmd.cli_ctx).get_subscription().get("tenantId")
        target_segments = parse_resource_id(target_id)
        self.subscription = target_segments.get('subscription')
        self.resource_group = target_segments.get('resource_group')
        self.auth_type = auth_info['auth_type']
        self.auth_info = auth_info
        self.login_username = run_cli_cmd(
            'az account show').get("user").get("name")
        self.login_usertype = run_cli_cmd(
            'az account show').get("user").get("type")  # servicePrincipal, user
        if (self.login_usertype not in ['servicePrincipal', 'user']):
            e = CLIInternalError(
                f'{self.login_usertype} is not supported. Please login as user or servicePrincipal')
            telemetry.set_exception(e, "Unsupported-UserType-" + self.login_usertype)
            raise e
        self.aad_username = "aad_" + connection_name
        self.connection_name = connection_name
        self.skip_prompt = skip_prompt

    def enable_target_aad_auth(self):
        return

    def set_user_admin(self, user_object_id, **kwargs):
        return

    def set_target_firewall(self, is_add, ip_name, start_ip=None, end_ip=None):
        return

    def create_aad_user(self):
        return

    def check_db_existence(self):
        return

    def get_auth_flag(self):
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
            return '--user-account'
        if self.auth_type == AUTHTYPES[AUTH_TYPE.SystemIdentity]:
            return '--system-identity'
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserIdentity]:
            return '--user-identity'
        if self.auth_type == AUTHTYPES[AUTH_TYPE.ServicePrincipalSecret]:
            return '--service-principal'
        return None

    def get_auth_config(self, user_object_id):
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
            return {
                'auth_type': self.auth_type,
                'username': self.aad_username,
                'principal_id': user_object_id
            }
        if self.auth_type == AUTHTYPES[AUTH_TYPE.SystemIdentity]:
            return {
                'auth_type': self.auth_type,
                'username': self.aad_username,
            }
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserIdentity]:
            return {
                'auth_type': self.auth_type,
                'username': self.aad_username,
                'client_id': self.identity_client_id,
                'subscription_id': self.auth_info['subscription_id'],
            }
        if self.auth_type == AUTHTYPES[AUTH_TYPE.ServicePrincipalSecret]:
            return {
                'auth_type': self.auth_type,
                'username': self.aad_username,
                'principal_id': self.identity_object_id,
                'client_id': self.identity_client_id,
                'secret': self.auth_info['secret'],
            }
        return None


class MysqlFlexibleHandler(TargetHandler):

    def __init__(self, cmd, target_id, target_type, auth_info, connection_name, skip_prompt):
        super().__init__(cmd, target_id, target_type,
                         auth_info, connection_name, skip_prompt)
        self.endpoint = cmd.cli_ctx.cloud.suffixes.mysql_server_endpoint
        target_segments = parse_resource_id(target_id)
        self.server = target_segments.get('name')
        self.dbname = target_segments.get('child_name_1')
        self.admin_username = self.login_username

    def check_db_existence(self):
        try:
            db_info = run_cli_cmd(
                'az mysql flexible-server db show --ids {}'.format(self.target_id))
            if db_info is None:
                e = ResourceNotFoundError(
                    "No database found with name {}".format(self.dbname))
                telemetry.set_exception(e, "No-Db")
                raise e
        except CLIInternalError as e:
            telemetry.set_exception(e, "No-Db")
            raise e

    def set_user_admin(self, user_object_id, **kwargs):
        mysql_identity_id = kwargs['mysql_identity_id']
        admins = run_cli_cmd(
            'az mysql flexible-server ad-admin list -g {} -s {} --subscription {}'.format(
                self.resource_group, self.server, self.subscription)
        )
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
        if admin_info:
            self.admin_username = admin_info.get('login')
            return

        logger.warning('Set current user as DB Server Microsoft Entra Administrators.')
        # set user as Microsoft Entra admin
        if mysql_identity_id is None:
            e = ValidationError(
                "Provide '{} mysql-identity-id=<user-assigned managed identity ID>' to update Microsoft Entra authentication.".format(
                    self.get_auth_flag()))
            telemetry.set_exception(e, "Missing-Mysql-Umi")
            raise e
        mysql_umi = run_cli_cmd(
            'az mysql flexible-server identity list -g {} -s {} --subscription {}'.format(self.resource_group, self.server, self.subscription))
        if (not mysql_umi) or (not mysql_umi.get("userAssignedIdentities")) or mysql_identity_id not in mysql_umi.get("userAssignedIdentities"):
            run_cli_cmd('az mysql flexible-server identity assign -g {} -s {} --subscription {} --identity {}'.format(
                self.resource_group, self.server, self.subscription, mysql_identity_id))
        run_cli_cmd('az mysql flexible-server ad-admin create -g {} -s {} --subscription {} -u {} -i {} --identity {}'.format(
            self.resource_group, self.server, self.subscription, self.login_username, user_object_id, mysql_identity_id))
        self.admin_username = self.login_username

    def create_aad_user(self):
        query_list = self.get_create_query()
        connection_kwargs = self.get_connection_string()
        ip_name = generate_random_string(prefix='svc_').lower()
        try:
            logger.warning("Connecting to database...")
            self.create_aad_user_in_mysql(connection_kwargs, query_list)
        except AzureConnectionError as e:
            logger.warning(e)
            # allow local access
            ip_address = get_local_ip()
            if not ip_address:
                self.set_target_firewall(
                    True, ip_name, '0.0.0.0', '255.255.255.255')
            else:
                self.set_target_firewall(
                    True, ip_name, ip_address, ip_address)
            try:
                self.create_aad_user_in_mysql(connection_kwargs, query_list)
            except AzureConnectionError as e:
                logger.warning(e)
                if not ip_address:
                    telemetry.set_exception(e, "Connect-Db-Fail")
                    raise e
                if not self.skip_prompt:
                    confirm_all_ip_allow()
                # allow public access
                self.set_target_firewall(
                    True, ip_name, '0.0.0.0', '255.255.255.255')
                # create again
                try:
                    self.create_aad_user_in_mysql(connection_kwargs, query_list)
                except AzureConnectionError as e:
                    telemetry.set_exception(e, "Connect-Db-Fail")
                    raise e
            finally:
                self.set_target_firewall(False, ip_name)

    def set_target_firewall(self, is_add, ip_name, start_ip=None, end_ip=None):
        if is_add:
            target = run_cli_cmd(
                'az mysql flexible-server show --ids {}'.format(self.target_id))
            if target.get('network').get('publicNetworkAccess') == "Disabled":
                ex = AzureConnectionError(
                    "The target resource doesn't allow public access. Please enable it manually and try again.")
                telemetry.set_exception(ex, "Public-Access-Disabled")
                raise ex
            logger.warning("Add firewall rule %s %s - %s...%s", ip_name, start_ip, end_ip,
                           ('(it will be removed after connection is created)' if self.auth_type != AUTHTYPES[
                               AUTH_TYPE.UserAccount] else '(Please delete it manually if it has security risk.)'))
            run_cli_cmd(
                'az mysql flexible-server firewall-rule create --resource-group {0} --name {1} --rule-name {2} '
                '--subscription {3} --start-ip-address {4} --end-ip-address {5}'.format(
                    self.resource_group, self.server, ip_name, self.subscription, start_ip, end_ip)
            )
        else:
            if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
                return
            logger.warning(
                "Remove database server firewall rule %s to recover...", ip_name)
            try:
                run_cli_cmd(
                    'az mysql flexible-server firewall-rule delete --resource-group {0} --name {1} --rule-name {2} '
                    '--subscription {3} --yes'.format(
                        self.resource_group, self.server, ip_name, self.subscription)
                )
            except CLIInternalError as e:
                logger.warning(
                    "Can't remove firewall rule %s. Please manually delete it to avoid security issue. %s", ip_name, str(e))

    def create_aad_user_in_mysql(self, connection_kwargs, query_list):
        if not is_packaged_installed('pymysql'):
            _run_pip(["install", "pymysql"])
        # pylint: disable=import-error
        try:
            import pymysql
            from pymysql.constants import CLIENT
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Dependency pymysql can't be installed, please install it manually with `" + sys.executable + " -m pip install pymysql`.") from e

        connection_kwargs['client_flag'] = CLIENT.MULTI_STATEMENTS
        try:
            connection = pymysql.connect(**connection_kwargs)
            logger.warning(
                "Adding new Microsoft Entra user %s to database...", self.aad_username)
            cursor = connection.cursor()
            for q in query_list:
                if q:
                    try:
                        logger.debug(q)
                        cursor.execute(q)
                    except Exception as e:  # pylint: disable=broad-except
                        logger.warning(
                            "Query %s, error: %s", q, str(e))
        except pymysql.Error as e:
            raise AzureConnectionError(
                "Fail to connect mysql. " + str(e)) from e
        if cursor is not None:
            try:
                cursor.close()
            except Exception as e:  # pylint: disable=broad-except
                ex = CLIInternalError(
                    "Connection close failed." + str(e))
                telemetry.set_exception(ex, "Connect-Db-Close-Fail")
                raise ex from e

    def get_connection_string(self):
        password = run_cli_cmd(
            'az account get-access-token --resource-type oss-rdbms').get('accessToken')

        return {
            'host': self.server + self.endpoint,
            'database': self.dbname,
            'user': self.admin_username,
            'password': password,
            'ssl': {"fake_flag_to_enable_tls": True},
            'autocommit': True
        }

    def get_create_query(self):
        client_id = self.identity_client_id
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
            client_id = self.user_object_id
        return [
            "SET aad_auth_validate_oids_in_tenant = OFF;",
            "DROP USER IF EXISTS '{}'@'%';".format(self.aad_username),
            "CREATE AADUSER '{}' IDENTIFIED BY '{}';".format(
                self.aad_username, client_id),
            "GRANT ALL PRIVILEGES ON `{}`.* TO '{}'@'%';".format(
                self.dbname, self.aad_username),
            "FLUSH privileges;"
        ]


class SqlHandler(TargetHandler):

    def __init__(self, cmd, target_id, target_type, auth_info, connection_name, skip_prompt):
        super().__init__(cmd, target_id, target_type,
                         auth_info, connection_name, skip_prompt)
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
                admin_info = run_cli_cmd('az sql server ad-admin create -g {} --server-name {} --display-name "{}" --object-id {} --subscription {}'.format(
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
                'az sql server firewall-rule create -g {0} -s {1} -n {2} '
                '--subscription {3} --start-ip-address {4} --end-ip-address {5}'.format(
                    self.resource_group, self.server, ip_name, self.subscription, start_ip, end_ip)
            )
        else:
            if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
                return
            logger.warning(
                "Remove database server firewall rule %s to recover...", ip_name)
            try:
                run_cli_cmd(
                    'az sql server firewall-rule delete -g {0} -s {1} -n {2} --subscription {3}'.format(
                        self.resource_group, self.server, ip_name, self.subscription)
                )
            except CLIInternalError as e:
                logger.warning(
                    "Can't remove firewall rule %s. Please manually delete it to avoid security issue. %s", ip_name, str(e))

    def create_aad_user_in_sql(self, connection_args, query_list):

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
                            logger.debug(execution_query)
                            cursor.execute(execution_query)
                        except pyodbc.ProgrammingError as e:
                            logger.warning(e)
                        conn.commit()
        except pyodbc.Error as e:
            search_ip = re.search(
                "Client with IP address '(.*?)' is not allowed to access the server", str(e))
            if search_ip is not None:
                self.ip = search_ip.group(1)
            raise AzureConnectionError("Fail to connect sql." + str(e)) from e

    def get_connection_string(self):
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
        role_q = "CREATE USER \"{}\" FROM EXTERNAL PROVIDER;".format(
            self.aad_username)
        grant_q = "GRANT CONTROL ON DATABASE::\"{}\" TO \"{}\";".format(
            self.dbname, self.aad_username)

        return [role_q, grant_q]


class PostgresFlexHandler(TargetHandler):

    def __init__(self, cmd, target_id, target_type, auth_info, connection_name, skip_prompt):
        super().__init__(cmd, target_id, target_type,
                         auth_info, connection_name, skip_prompt)
        self.endpoint = cmd.cli_ctx.cloud.suffixes.postgresql_server_endpoint
        target_segments = parse_resource_id(target_id)
        self.db_server = target_segments.get('name')
        self.host = self.db_server + self.endpoint
        self.dbname = target_segments.get('child_name_1')
        self.ip = ""
        self.admin_username = self.login_username

    def check_db_existence(self):
        try:
            # `az postgres flexible-server db show -d postgres` will throw exception
            if self.dbname == "postgres":
                server_info = run_cli_cmd(
                    'az postgres flexible-server show -n {} -g {} --subscription {}'.format(
                        self.db_server, self.resource_group, self.subscription))
                if server_info is None:
                    e = ResourceNotFoundError(
                        "No server found for '{}'".format(self.db_server))
                    telemetry.set_exception(e, "No-Server")
                    raise e
                else:
                    return
            db_info = run_cli_cmd(
                'az postgres flexible-server db show --server-name {} --database-name {} -g {} --subscription {}'.format(
                    self.db_server, self.dbname, self.resource_group, self.subscription))
            if db_info is None:
                e = ResourceNotFoundError(
                    "No database '{}' found for server '{}'".format(self.dbname, self.db_server))
                telemetry.set_exception(e, "No-Db")
                raise e
        except CLIInternalError as e:
            telemetry.set_exception(e, "No-Db")
            raise e

    def enable_target_aad_auth(self):
        target = run_cli_cmd(
            'az postgres flexible-server show -g {} -n {} --subscription {}'.format(
                self.resource_group, self.db_server, self.subscription))
        if target.get('authConfig').get('activeDirectoryAuth') == "Enabled":
            return
        run_cli_cmd('az postgres flexible-server update --ids {} --active-directory-auth Enabled'.format(
            self.target_id))

    def set_user_admin(self, user_object_id, **kwargs):
        admins = run_cli_cmd('az postgres flexible-server ad-admin list -g {} -s {} --subscription {}'.format(
            self.resource_group, self.db_server, self.subscription))

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
        admin_info = next((ad for ad in admins if ad.get('objectId', "") == user_object_id), None)
        if not admin_info:
            logger.warning('Set current user as DB Server Microsoft Entra Administrators.')
            admin_info = run_cli_cmd('az postgres flexible-server ad-admin create -u {} -i {} -g {} -s {} --subscription {} -t {}'.format(
                self.login_username, user_object_id, self.resource_group, self.db_server, self.subscription, self.login_usertype))
        self.admin_username = admin_info.get('principalName', self.login_username)

    def create_aad_user(self):
        query_list = self.get_create_query()
        connection_string = self.get_connection_string()
        ip_name = generate_random_string(prefix='svc_').lower()

        try:
            logger.warning("Connecting to database...")
            self.create_aad_user_in_pg(connection_string, query_list)
        except AzureConnectionError as e:
            logger.warning(e)
            if 'password authentication failed' in str(e):
                raise ValidationError('Please confirm current user as Microsoft Entra admin and try again.') from e
            # allow local access
            ip_address = self.ip or get_local_ip()
            if not ip_address:
                self.set_target_firewall(
                    True, ip_name, '0.0.0.0', '255.255.255.255')
            else:
                self.set_target_firewall(
                    True, ip_name, ip_address, ip_address)
            try:
                # create again
                self.create_aad_user_in_pg(connection_string, query_list)
            except AzureConnectionError as e:
                logger.warning(e)
                if not ip_address:
                    telemetry.set_exception(e, "Connect-Db-Fail")
                    raise e
                if not self.skip_prompt:
                    confirm_all_ip_allow()
                self.set_target_firewall(
                    True, ip_name, '0.0.0.0', '255.255.255.255')
                # create again
                try:
                    self.create_aad_user_in_pg(connection_string, query_list)
                except AzureConnectionError as e:
                    telemetry.set_exception(e, "Connect-Db-Fail")
                    raise e
            finally:
                self.set_target_firewall(False, ip_name)

    def set_target_firewall(self, is_add, ip_name, start_ip=None, end_ip=None):
        if is_add:
            target = run_cli_cmd(
                'az postgres flexible-server show --ids {}'.format(self.target_id))
            if target.get('network').get('publicNetworkAccess') == "Disabled":
                ex = AzureConnectionError(
                    "The target resource doesn't allow public access. Please enable it manually and try again.")
                telemetry.set_exception(ex, "Public-Access-Disabled")
                raise ex
            logger.warning("Add firewall rule %s %s - %s...%s", ip_name, start_ip, end_ip,
                           ('(it will be removed after connection is created)' if self.auth_type != AUTHTYPES[
                               AUTH_TYPE.UserAccount] else '(Please delete it manually if it has security risk.)'))
            run_cli_cmd(
                'az postgres flexible-server firewall-rule create --resource-group {0} --name {1} --rule-name {2} '
                '--subscription {3} --start-ip-address {4} --end-ip-address {5}'.format(
                    self.resource_group, self.db_server, ip_name, self.subscription, start_ip, end_ip)
            )
        else:
            if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
                return
            logger.warning(
                "Remove database server firewall rule %s to recover...", ip_name)
            try:
                run_cli_cmd(
                    'az postgres flexible-server firewall-rule delete --resource-group {0} --name {1} --rule-name {2} '
                    '--subscription {3} --yes'.format(
                        self.resource_group, self.db_server, ip_name, self.subscription)
                )
            except CLIInternalError as e:
                logger.warning(
                    "Can't remove firewall rule %s. Please manually delete it to avoid security issue. %s", ip_name, str(e))

    def create_aad_user_in_pg(self, conn_string, query_list):
        if not is_packaged_installed('psycopg2'):
            _install_deps_for_psycopg2()
            _run_pip(["install", "psycopg2"])
        # pylint: disable=import-error
        try:
            import psycopg2
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Dependency psycopg2 can't be installed, please install it manually with `" + sys.executable + " -m pip install psycopg2-binary`.") from e

        # pylint: disable=protected-access
        try:
            conn = psycopg2.connect(conn_string)
        except (psycopg2.Error, psycopg2.OperationalError) as e:
            # logger.warning(e)
            search_ip = re.search(
                'no pg_hba.conf entry for host "(.*)", user ', str(e))
            if search_ip is not None:
                self.ip = search_ip.group(1)
            raise AzureConnectionError(
                "Fail to connect to postgresql. " + str(e)) from e

        conn.autocommit = True
        cursor = conn.cursor()
        logger.warning("Adding new Microsoft Entra user %s to database...",
                       self.aad_username)
        for execution_query in query_list:
            if execution_query:
                try:
                    logger.debug(execution_query)
                    cursor.execute(execution_query)
                except psycopg2.Error as e:  # role "aad_user" already exists
                    logger.warning(e)

        # Clean up
        conn.commit()
        cursor.close()
        conn.close()

    def get_connection_string(self):
        password = run_cli_cmd(
            'az account get-access-token --resource-type oss-rdbms').get('accessToken')

        # extension functions require the extension to be available, which is the case for postgres (default) database.
        conn_string = "host={} user={} dbname=postgres password={} sslmode=require".format(
            self.host, self.admin_username, password)
        return conn_string

    def get_create_query(self):
        object_type = 'service'
        object_id = self.identity_object_id
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
            object_id = self.user_object_id
            object_type = 'user'
        return [
            # 'drop role IF EXISTS "{0}";'.format(self.aad_username),
            "select * from pgaadauth_create_principal_with_oid('{0}', '{1}', '{2}', false, false);".format(
                self.aad_username, object_id, object_type),
            'GRANT ALL PRIVILEGES ON DATABASE "{0}" TO "{1}";'.format(
                self.dbname, self.aad_username),
            'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{}";'.format(
                self.aad_username),
            'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{}";'.format(
                self.aad_username)]


class PostgresSingleHandler(PostgresFlexHandler):

    def enable_target_aad_auth(self):
        return

    def check_db_existence(self):
        try:
            db_info = run_cli_cmd(
                'az postgres db show --ids {} -n {}'.format(self.target_id, self.dbname))
            if db_info is None:
                e = ResourceNotFoundError(
                    "No database found with name {}".format(self.dbname))
                telemetry.set_exception(e, "No-Db")
                raise e
        except CLIInternalError as e:
            telemetry.set_exception(e, "No-Db")
            raise e

    def set_user_admin(self, user_object_id, **kwargs):
        sub = self.subscription
        rg = self.resource_group
        server = self.db_server

        # pylint: disable=not-an-iterable
        admins = run_cli_cmd(
            'az postgres server ad-admin list --ids {}'.format(self.target_id))

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
            logger.warning('Setting current user as database server Microsoft Entra admin:'
                           ' user=%s object id=%s', self.login_username, user_object_id)
            admin_info = run_cli_cmd('az postgres server ad-admin create -g {} --server-name {} --display-name {} --object-id {}'
                                     ' --subscription {}'.format(rg, server, self.login_username, user_object_id, sub))
        self.admin_username = admin_info.get('login', self.login_username)

    def set_target_firewall(self, is_add, ip_name, start_ip=None, end_ip=None):
        sub = self.subscription
        rg = self.resource_group
        server = self.db_server
        target_id = self.target_id
        if is_add:
            target = run_cli_cmd(
                'az postgres server show --ids {}'.format(target_id))
            if target.get('publicNetworkAccess') == "Disabled":
                ex = AzureConnectionError(
                    "The target resource doesn't allow public access. Please enable it manually and try again.")
                telemetry.set_exception(ex, "Public-Access-Disabled")
                raise ex
            logger.warning("Add firewall rule %s %s - %s...%s", ip_name, start_ip, end_ip,
                           ('(it will be removed after connection is created)' if self.auth_type != AUTHTYPES[
                               AUTH_TYPE.UserAccount] else '(Please delete it manually if it has security risk.)'))
            run_cli_cmd(
                'az postgres server firewall-rule create -g {0} -s {1} -n {2} --subscription {3}'
                ' --start-ip-address {4} --end-ip-address {5}'.format(
                    rg, server, ip_name, sub, start_ip, end_ip)
            )
        else:
            if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
                return
            logger.warning(
                "Remove database server firewall rule %s to recover...", ip_name)
            try:
                run_cli_cmd(
                    'az postgres server firewall-rule delete -g {0} -s {1} -n {2} -y'.format(rg, server, ip_name))
            except CLIInternalError as e:
                logger.warning(
                    "Can't remove firewall rule %s. Please manually delete it to avoid security issue. %s", ip_name, str(e))

    def get_connection_string(self):
        password = run_cli_cmd(
            'az account get-access-token --resource-type oss-rdbms').get('accessToken')

        # extension functions require the extension to be available, which is the case for postgres (default) database.
        conn_string = "host={} user={} dbname={} password={} sslmode=require".format(
            self.host, self.admin_username + '@' + self.db_server, self.dbname, password)
        return conn_string

    def get_create_query(self):
        client_id = self.identity_client_id
        if self.auth_type == AUTHTYPES[AUTH_TYPE.UserAccount]:
            client_id = self.user_object_id
        return [
            'SET aad_validate_oids_in_tenant = off;',
            # 'drop role IF EXISTS "{0}";'.format(self.aad_username),
            "CREATE ROLE \"{0}\" WITH LOGIN PASSWORD '{1}' IN ROLE azure_ad_user;".format(
                self.aad_username, client_id),
            'GRANT ALL PRIVILEGES ON DATABASE "{0}" TO "{1}";'.format(
                self.dbname, self.aad_username),
            'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{}";'.format(
                self.aad_username),
            'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "{}";'.format(
                self.aad_username)
        ]


def getSourceHandler(source_id, source_type):
    if source_type in {RESOURCE.WebApp, RESOURCE.FunctionApp}:
        return WebappHandler(source_id, source_type)
    if source_type in {RESOURCE.ContainerApp}:
        return ContainerappHandler(source_id, source_type)
    if source_type in {RESOURCE.SpringCloud, RESOURCE.SpringCloudDeprecated}:
        return SpringHandler(source_id, source_type)
    if source_type in {RESOURCE.Local}:
        return LocalHandler(source_id, source_type)
    return None


# pylint: disable=too-few-public-methods
class SourceHandler:

    def __init__(self, source_id, source_type: RESOURCE):
        self.source_id = source_id
        self.source_type = source_type.value

    def get_identity_pid(self):
        return

    def get_identity_name(self):
        return


def output_is_none(output):
    return not output.stdout


class LocalHandler(SourceHandler):
    def get_identity_pid(self):
        pass


class SpringHandler(SourceHandler):
    def get_identity_name(self):
        segments = parse_resource_id(self.source_id)
        spring = segments.get('name')
        app = segments.get('child_name_1')
        return '{}/apps/{}'.format(spring, app)

    def get_identity_pid(self):
        segments = parse_resource_id(self.source_id)
        sub = segments.get('subscription')
        spring = segments.get('name')
        app = segments.get('child_name_1')
        rg = segments.get('resource_group')
        logger.warning(
            'Checking if Spring app enables System Identity...')
        identity = run_cli_cmd('az {} app identity show -g {} -s {} -n {} --subscription {}'.format(
            self.source_type, rg, spring, app, sub))
        if (identity is None or identity.get('type') != "SystemAssigned"):
            # assign system identity for spring-cloud
            logger.warning('Enabling Spring app System Identity...')
            run_cli_cmd(
                'az {} app identity assign -g {} -s {} -n {} --subscription {}'.format(
                    self.source_type, rg, spring, app, sub))

            identity = run_cli_cmd('az {} app identity show -g {} -s {} -n {} --subscription {}'.format(
                self.source_type, rg, spring, app, sub), 15, 5, output_is_none)

        if identity is None:
            ex = CLIInternalError(
                "Unable to get system identity of Spring. Please try it later.")
            telemetry.set_exception(ex, "No-Smi")
            raise ex
        return identity.get('principalId')


class WebappHandler(SourceHandler):
    def __init__(self, source_id, source_type: RESOURCE):
        super().__init__(source_id, source_type)
        segments = parse_resource_id(self.source_id)
        self.app_name = segments.get('name')
        self.slot_name = segments.get('child_name_1', None)

    def get_identity_name(self):
        if self.slot_name is not None:
            return self.app_name + '/slots/' + self.slot_name
        return self.app_name

    def get_identity_pid(self):
        logger.warning('Checking if WebApp enables System Identity...')
        identity = run_cli_cmd(
            'az webapp identity show --ids {}'.format(self.source_id)) if self.slot_name is None else run_cli_cmd(
            'az webapp identity show --ids {} --slot {}'.format(self.source_id, self.slot_name))
        if (identity is None or "SystemAssigned" not in identity.get('type')):
            # assign system identity for spring-cloud
            logger.warning('Enabling WebApp System Identity...')
            if self.slot_name is None:
                run_cli_cmd(
                    'az webapp identity assign --ids "{}"'.format(self.source_id))

                identity = run_cli_cmd(
                    'az webapp identity show --ids "{}"'.format(self.source_id), 15, 5, output_is_none)
            else:
                run_cli_cmd(
                    'az webapp identity assign --ids "{}" --slot "{}"'.format(self.source_id, self.slot_name))
                identity = run_cli_cmd(
                    'az webapp identity show --ids "{}" --slot "{}"'.format(self.source_id, self.slot_name), 15, 5, output_is_none)

        if identity is None:
            ex = CLIInternalError(
                "Unable to get system identity of Web App. Please try it later.")
            telemetry.set_exception(ex, "No-Smi")
            raise ex
        return identity.get('principalId')


class ContainerappHandler(SourceHandler):
    def get_identity_name(self):
        segments = parse_resource_id(self.source_id)
        app_name = segments.get('name')
        return app_name

    def get_identity_pid(self):
        logger.warning('Checking if Container App enables System Identity...')
        identity = run_cli_cmd(
            'az containerapp identity show --ids {}'.format(self.source_id))
        if (identity is None or "SystemAssigned" not in identity.get('type')):
            # assign system identity for spring-cloud
            logger.warning('Enabling Container App System Identity...')
            run_cli_cmd(
                'az containerapp identity assign --ids {} --system-assigned'.format(self.source_id))
            identity = run_cli_cmd(
                'az containerapp identity show --ids {}'.format(self.source_id), 15, 5, output_is_none)

        if identity is None:
            ex = CLIInternalError(
                "Unable to get system identity of Container App. Please try it later.")
            telemetry.set_exception(ex, "No-Smi")
            raise ex
        return identity.get('principalId')
