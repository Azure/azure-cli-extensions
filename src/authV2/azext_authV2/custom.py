# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from datetime import datetime
import time
import uuid
import os

from azure.cli.core.util import sdk_no_wait
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_data_service_client
from azure.mgmt.compute.models import ResourceIdentityType
from msrestazure.tools import parse_resource_id
from msrestazure.azure_exceptions import CloudError

from knack.log import get_logger

from knack.util import CLIError
import json
from azure.cli.core.util import send_raw_request
from azure.cli.core.profiles import get_sdk, supported_api_version, ResourceType
from azure.cli.command_modules.appservice._appservice_utils import _generic_site_operation

def get_auth_settings_v2(cmd, resource_group_name, name, slot=None):
    from azure.cli.core.commands.client_factory import get_subscription_id
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "GET", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2/list?api-version=2020-12-01".format(sub_id, resource_group_name, name))
    return r.json()

def set_auth_settings_v2(cmd, resource_group_name, name, body=None, slot=None):  # pylint: disable=unused-argument
    if body is None:
        json_object = None
    else:
        json_object = json.loads(body)
    final_json = {
        "properties": json_object
    }
    from azure.cli.core.commands.client_factory import get_subscription_id
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json() 

def update_auth_settings_v2(cmd, resource_group_name, name, set_string=None, enabled=None, # pylint: disable=unused-argument
                            runtime_version=None, config_file_path=None, unauthenticated_client_action=None, # pylint: disable=unused-argument
                            redirect_provider=None, enable_token_store=None, require_https=None,  # pylint: disable=unused-argument
                            proxy_convention=None, proxy_custom_host_header=None, proxy_custom_proto_header=None, slot=None):  # pylint: disable=unused-argument
    from azure.cli.core.commands.client_factory import get_subscription_id
    sub_id = get_subscription_id(cmd.cli_ctx)
    getr = send_raw_request(cmd.cli_ctx, "GET", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2/list?api-version=2020-12-01".format(sub_id, resource_group_name, name))
    existing_auth = getr.json()["properties"]
    if set_string is not None:
        split1 = set_string.split("=")
        fieldName = split1[0]
        fieldValue = split1[1]
        split2 = fieldName.split(".")
        split2length = len(split2)
        currentObj = existing_auth
        for field in split2:
            if split2[split2length-1] == field:
                currentObj[field] = fieldValue
            else:
                if field not in currentObj.keys():
                    currentObj[field] = {}
                currentObj = currentObj[field]
    if enabled is not None:
        if "platform" not in existing_auth.keys():
            existing_auth["platform"] = {}
        existing_auth["platform"]["enabled"] = enabled
    
    if runtime_version is not None:
        if "platform" not in existing_auth.keys():
            existing_auth["platform"] = {}
        existing_auth["platform"]["runtimeVersion"] = runtime_version
    
    if config_file_path is not None:
        if "platform" not in existing_auth.keys():
            existing_auth["platform"] = {}
        existing_auth["platform"]["configFilePath"] = config_file_path
    
    if unauthenticated_client_action is not None:
        if "globalValidation" not in existing_auth.keys():
            existing_auth["globalValidation"] = {}
        existing_auth["globalValidation"]["unauthenticatedClientAction"] = unauthenticated_client_action

    if redirect_provider is not None:
        if "globalValidation" not in existing_auth.keys():
            existing_auth["globalValidation"] = {}
        existing_auth["globalValidation"]["redirectToProvider"] = redirect_provider
    
    if enable_token_store is not None:
        if "login" not in existing_auth.keys():
            existing_auth["login"] = {}
        if "tokenStore" not in existing_auth["login"].keys():
            existing_auth["login"]["tokenStore"] = {}
        existing_auth["login"]["tokenStore"]["enabled"] = enable_token_store
    
    if require_https is not None:
        if "httpSettings" not in existing_auth.keys():
            existing_auth["httpSettings"] = {}
        existing_auth["httpSettings"]["requireHttps"] = require_https
        
    if proxy_convention is not None:
        if "httpSettings" not in existing_auth.keys():
            existing_auth["httpSettings"] = {}
        if "forwardProxy" not in existing_auth["httpSettings"].keys():
            existing_auth["httpSettings"]["forwardProxy"] = {}
        existing_auth["httpSettings"]["forwardProxy"]["convention"] = proxy_convention

    if proxy_custom_host_header is not None:
        if "httpSettings" not in existing_auth.keys():
            existing_auth["httpSettings"] = {}
        if "forwardProxy" not in existing_auth["httpSettings"].keys():
            existing_auth["httpSettings"]["forwardProxy"] = {}
        existing_auth["httpSettings"]["forwardProxy"]["customHostHeaderName"] = proxy_custom_host_header
    
    if proxy_custom_proto_header is not None:
        if "httpSettings" not in existing_auth.keys():
            existing_auth["httpSettings"] = {}
        if "forwardProxy" not in existing_auth["httpSettings"].keys():
            existing_auth["httpSettings"]["forwardProxy"] = {}
        existing_auth["httpSettings"]["forwardProxy"]["customProtoHeaderName"] = proxy_custom_proto_header
                
    json_object = existing_auth
    final_json = {
        "properties": json_object
    }    
    
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()

def is_auth_v2_app(cmd, resource_group_name, name, slot=None):
    from azure.cli.core.commands.client_factory import get_subscription_id
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "POST", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettings/list?api-version=2020-12-01".format(sub_id, resource_group_name, name))
    return r.json()["properties"]["configVersion"] == "v2"    

def get_auth_settings(cmd, resource_group_name, name, slot=None):
    return _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'get_auth_settings', slot)

def is_auth_runtime_version_valid(runtime_version=None):
    if runtime_version is None:
        return True
    if runtime_version.startswith("~") and len(runtime_version) > 1:
        try:
            int(runtime_version[1:])
        except ValueError:
            return False
        return True
    split_versions = runtime_version.split('.')
    if len(split_versions) != 3:
        return False
    for version in split_versions:
        try:
            int(version)
        except ValueError:
            return False
    return True

def revert_to_auth_settings(cmd, resource_group_name, name, slot=None):  # pylint: disable=unused-argument
    site_auth_settings = get_auth_settings(cmd, resource_group_name, name, slot)

    set_auth_settings_v2(cmd, resource_group_name, name, None, slot)

    update_auth_settings(cmd, resource_group_name, name, site_auth_settings.enabled, None,
                         site_auth_settings.client_id, site_auth_settings.token_store_enabled, site_auth_settings.runtime_version,
                         site_auth_settings.token_refresh_extension_hours,
                         site_auth_settings.allowed_external_redirect_urls, site_auth_settings.client_secret,
                         site_auth_settings.client_secret_certificate_thumbprint,
                         site_auth_settings.allowed_audiences, site_auth_settings.issuer, site_auth_settings.facebook_app_id,
                         site_auth_settings.facebook_app_secret, site_auth_settings.facebook_o_auth_scopes,
                         site_auth_settings.twitter_consumer_key, site_auth_settings.twitter_consumer_secret,
                         site_auth_settings.google_client_id, site_auth_settings.google_client_secret, 
                         site_auth_settings.google_o_auth_scopes, site_auth_settings.microsoft_account_client_id,
                         site_auth_settings.microsoft_account_client_secret,
                         site_auth_settings.microsoft_account_o_auth_scopes, slot)

def update_auth_settings(cmd, resource_group_name, name, enabled=None, action=None,  # pylint: disable=unused-argument
                        client_id=None, token_store_enabled=None, runtime_version=None,  # pylint: disable=unused-argument
                        token_refresh_extension_hours=None,  # pylint: disable=unused-argument
                        allowed_external_redirect_urls=None, client_secret=None,  # pylint: disable=unused-argument
                        client_secret_certificate_thumbprint=None,  # pylint: disable=unused-argument
                        allowed_audiences=None, issuer=None, facebook_app_id=None,  # pylint: disable=unused-argument
                        facebook_app_secret=None, facebook_oauth_scopes=None,  # pylint: disable=unused-argument
                        twitter_consumer_key=None, twitter_consumer_secret=None,  # pylint: disable=unused-argument
                        google_client_id=None, google_client_secret=None,  # pylint: disable=unused-argument
                        google_oauth_scopes=None, microsoft_account_client_id=None,  # pylint: disable=unused-argument
                        microsoft_account_client_secret=None,  # pylint: disable=unused-argument
                        microsoft_account_oauth_scopes=None, slot=None, # pylint: disable=unused-argument
                        github_client_id=None, github_client_secret=None, # pylint: disable=unused-argument
                        client_secret_setting_name=None, facebook_app_secret_setting_name=None, # pylint: disable=unused-argument
                        google_client_secret_setting_name=None, microsoft_account_client_secret_setting_name=None, # pylint: disable=unused-argument
                        twitter_consume_secret_setting_name=None, github_client_secret_setting_name=None):  # pylint: disable=unused-argument
    if is_auth_v2_app(cmd, resource_group_name, name, slot):
        raise CLIError('Usage Error: Cannot use command az webapp authlegacy update when the app is using auth v2. If you wish to revert the app to v1, run az webapp auth revert')
        
    auth_settings = get_auth_settings(cmd, resource_group_name, name, slot)
    from azure.cli.core.profiles import ResourceType
    UnauthenticatedClientAction = cmd.get_models('UnauthenticatedClientAction', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    if action == 'AllowAnonymous':
        auth_settings.unauthenticated_client_action = UnauthenticatedClientAction.allow_anonymous
    elif action:
        auth_settings.unauthenticated_client_action = UnauthenticatedClientAction.redirect_to_login_page
        auth_settings.default_provider = AUTH_TYPES[action]
    # validate runtime version
    if not is_auth_runtime_version_valid(runtime_version):
        raise CLIError('Usage Error: --runtime-version set to invalid value')

    import inspect
    frame = inspect.currentframe()
    bool_flags = ['enabled', 'token_store_enabled']
    # note: getargvalues is used already in azure.cli.core.commands.
    # and no simple functional replacement for this deprecating method for 3.5
    args, _, _, values = inspect.getargvalues(frame)  # pylint: disable=deprecated-method

    for arg in args[2:]:
        if values.get(arg, None):
            setattr(auth_settings, arg, values[arg] if arg not in bool_flags else values[arg] == 'true')

    return _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'update_auth_settings', slot, auth_settings)