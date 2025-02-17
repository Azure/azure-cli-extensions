from azure.mgmt.core.tools import parse_resource_id
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError
from azure.cli.core._profile import Profile
from azure.cli.command_modules.serviceconnector._resource_config import AUTH_TYPE
from .._utils import run_cli_cmd

AUTHTYPES = {
    AUTH_TYPE.SystemIdentity: 'systemAssignedIdentity',
    AUTH_TYPE.UserIdentity: 'userAssignedIdentity',
    AUTH_TYPE.ServicePrincipalSecret: 'servicePrincipalSecret',
    AUTH_TYPE.UserAccount: 'userAccount',
}


class TargetHandler:
    def __init__(self, cmd, target_id, target_type, auth_info, connection_name, skip_prompt, new_user):
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
        self.new_user = new_user
        self.endpoint = ""
        self.user_object_id = ""
        self.identity_name = ""
        self.identity_client_id = ""
        self.identity_object_id = ""

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
