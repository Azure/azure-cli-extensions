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
from azure.cli.command_modules.appservice.custom import update_app_settings
from azure.cli.core.commands.client_factory import get_subscription_id

def get_auth_settings_v2(cmd, resource_group_name, name, slot=None):
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
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()

def update_auth_settings_v2(cmd, resource_group_name, name, set_string=None, enabled=None, # pylint: disable=unused-argument
                            runtime_version=None, config_file_path=None, unauthenticated_client_action=None, # pylint: disable=unused-argument
                            redirect_provider=None, enable_token_store=None, require_https=None,  # pylint: disable=unused-argument
                            proxy_convention=None, proxy_custom_host_header=None, proxy_custom_proto_header=None, slot=None):  # pylint: disable=unused-argument
    existing_auth = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
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

def prep_auth_settings_for_v2(cmd, resource_group_name, name, slot=None): # pylint: disable=unused-argument
    site_auth_settings = get_auth_settings(cmd, resource_group_name, name, slot)
    settings = []
    if site_auth_settings.client_secret is not None:
        settings.append('MICROSOFT_PROVIDER_AUTHENTICATION_SECRET=' + site_auth_settings.client_secret)
        site_auth_settings.client_secret_setting_name = 'MICROSOFT_PROVIDER_AUTHENTICATION_SECRET'
    if site_auth_settings.facebook_app_secret is not None:
        settings.append('FACEBOOK_PROVIDER_AUTHENTICATION_SECRET=' + site_auth_settings.facebook_app_secret)
        site_auth_settings.facebook_app_secret_setting_name = 'FACEBOOK_PROVIDER_AUTHENTICATION_SECRET'
    if site_auth_settings.git_hub_client_secret is not None:
        settings.append('GITHUB_PROVIDER_AUTHENTICATION_SECRET=' + site_auth_settings.git_hub_client_secret)
        site_auth_settings.git_hub_client_secret_setting_name = 'GITHUB_PROVIDER_AUTHENTICATION_SECRET'
    if site_auth_settings.google_client_secret is not None:
        settings.append('GOOGLE_PROVIDER_AUTHENTICATION_SECRET=' + site_auth_settings.google_client_secret)
        site_auth_settings.google_client_secret_setting_name = 'GOOGLE_PROVIDER_AUTHENTICATION_SECRET'
    if site_auth_settings.microsoft_account_client_secret is not None:
        settings.append('MSA_PROVIDER_AUTHENTICATION_SECRET=' + site_auth_settings.microsoft_account_client_secret)
        site_auth_settings.microsoft_account_client_secret_setting_name = 'MSA_PROVIDER_AUTHENTICATION_SECRET'
    if site_auth_settings.twitter_consumer_secret is not None:
        settings.append('TWITTER_PROVIDER_AUTHENTICATION_SECRET=' + site_auth_settings.twitter_consumer_secret)
        site_auth_settings.twitter_consumer_secret_setting_name = 'TWITTER_PROVIDER_AUTHENTICATION_SECRET'
    if len(settings) > 0:
        update_app_settings(cmd, resource_group_name, name, settings, slot)
        remove_all_auth_settings_secrets(cmd, resource_group_name, name, slot)
        update_auth_settings(cmd, resource_group_name, name, site_auth_settings.enabled, None,
                            site_auth_settings.client_id, site_auth_settings.token_store_enabled, site_auth_settings.runtime_version,
                            site_auth_settings.token_refresh_extension_hours,
                            site_auth_settings.allowed_external_redirect_urls, None,
                            site_auth_settings.client_secret_certificate_thumbprint,
                            site_auth_settings.allowed_audiences, site_auth_settings.issuer, site_auth_settings.facebook_app_id,
                            None, site_auth_settings.facebook_o_auth_scopes,
                            site_auth_settings.twitter_consumer_key, None,
                            site_auth_settings.google_client_id, None, 
                            site_auth_settings.google_o_auth_scopes, site_auth_settings.microsoft_account_client_id,
                            None,
                            site_auth_settings.microsoft_account_o_auth_scopes, slot,
                            site_auth_settings.git_hub_client_id, None, site_auth_settings.git_hub_o_auth_scopes,
                            site_auth_settings.client_secret_setting_name, site_auth_settings.facebook_app_secret_setting_name,
                            site_auth_settings.google_client_secret_setting_name, site_auth_settings.microsoft_account_client_secret_setting_name,
                            site_auth_settings.twitter_consumer_secret_setting_name, site_auth_settings.git_hub_client_secret_setting_name)

def upgrade_to_auth_settings_v2(cmd, resource_group_name, name, slot=None):  # pylint: disable=unused-argument
    if is_auth_v2_app(cmd, resource_group_name, name, slot):
        raise CLIError('Usage Error: Cannot use command az webapp auth upgrade when the app is using auth v2.')
    prep_auth_settings_for_v2(cmd, resource_group_name, name, slot)
    site_auth_settings_v2 = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    final_json = {
        "properties": site_auth_settings_v2
    }    
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()

def get_config_version(cmd, resource_group_name, name, slot=None):  # pylint: disable=unused-argument
    isV2 = is_auth_v2_app(cmd, resource_group_name, name, slot)
    config_version = "v1"
    if isV2:
        config_version = "v2"
    return {
        "configVersion": config_version
    }    

def revert_to_auth_settings(cmd, resource_group_name, name, slot=None):  # pylint: disable=unused-argument
    if not is_auth_v2_app(cmd, resource_group_name, name, slot):
        raise CLIError('Usage Error: Cannot use command az webapp auth revert when the app is using auth v1.')

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
                         site_auth_settings.microsoft_account_o_auth_scopes, slot,
                         site_auth_settings.git_hub_client_id, site_auth_settings.git_hub_client_secret, site_auth_settings.git_hub_o_auth_scopes,
                         site_auth_settings.client_secret_setting_name, site_auth_settings.facebook_app_secret_setting_name,
                         site_auth_settings.google_client_secret_setting_name, site_auth_settings.microsoft_account_client_secret_setting_name,
                         site_auth_settings.twitter_consumer_secret_setting_name, site_auth_settings.git_hub_client_secret_setting_name)

def remove_all_auth_settings_secrets(cmd, resource_group_name, name, slot=None): # pylint: disable=unused-argument
    auth_settings = get_auth_settings(cmd, resource_group_name, name, slot)
    auth_settings.client_secret = ""
    auth_settings.facebook_app_secret = ""
    auth_settings.git_hub_client_secret = ""
    auth_settings.google_client_secret = ""
    auth_settings.microsoft_account_client_secret = ""
    auth_settings.twitter_consumer_secret_setting_name = ""
    return _generic_site_operation(cmd.cli_ctx, resource_group_name, name, 'update_auth_settings', slot, auth_settings)

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
                        git_hub_client_id=None, git_hub_client_secret=None, git_hub_o_auth_scopes=None, # pylint: disable=unused-argument
                        client_secret_setting_name=None, facebook_app_secret_setting_name=None, # pylint: disable=unused-argument
                        google_client_secret_setting_name=None, microsoft_account_client_secret_setting_name=None, # pylint: disable=unused-argument
                        twitter_consume_secret_setting_name=None, git_hub_client_secret_setting_name=None):  # pylint: disable=unused-argument
    if is_auth_v2_app(cmd, resource_group_name, name, slot):
        raise CLIError('Usage Error: Cannot use command az webapp auth-classic update when the app is using auth v2. If you wish to revert the app to v1, run az webapp auth revert')
        
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

def get_aad_settings(cmd, resource_group_name, name, slot=None):
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        return {}
    if "azureActiveDirectory" not in auth_settings["identityProviders"].keys():
        return {}
    return auth_settings["identityProviders"]["azureActiveDirectory"]

def update_aad_settings(cmd, resource_group_name, name, slot=None,  # pylint: disable=unused-argument
                        client_id=None, client_secret_setting_name=None,  # pylint: disable=unused-argument
                        issuer=None, allowed_token_audiences=None):    # pylint: disable=unused-argument
    existing_auth = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in existing_auth.keys():
            existing_auth["identityProviders"] = {}
    if "azureActiveDirectory" not in existing_auth["identityProviders"].keys():
        existing_auth["identityProviders"]["azureActiveDirectory"] = {}
    if client_id is not None or client_secret_setting_name is not None or issuer is not None:
        if "registration" not in existing_auth["identityProviders"]["azureActiveDirectory"].keys():
            existing_auth["identityProviders"]["azureActiveDirectory"]["registration"] = {}
    if allowed_token_audiences is not None:
        if "validation" not in existing_auth["identityProviders"]["azureActiveDirectory"].keys():
            existing_auth["identityProviders"]["azureActiveDirectory"]["validation"] = {}
    
    if client_id is not None:
        existing_auth["identityProviders"]["azureActiveDirectory"]["registration"]["clientId"] = client_id
    if client_secret_setting_name is not None:
        existing_auth["identityProviders"]["azureActiveDirectory"]["registration"]["clientSecretSettingName"] = client_secret_setting_name
    if issuer is not None:
        existing_auth["identityProviders"]["azureActiveDirectory"]["registration"]["openIdIssuer"] = issuer
    if allowed_token_audiences is not None:
        existing_auth["identityProviders"]["azureActiveDirectory"]["validation"]["allowedAudiences"] = allowed_token_audiences.split(",")
    final_json = {
        "properties": existing_auth
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["azureActiveDirectory"]

def get_facebook_settings(cmd, resource_group_name, name, slot=None):
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        return {}
    if "facebook" not in auth_settings["identityProviders"].keys():
        return {}
    return auth_settings["identityProviders"]["facebook"]

def update_facebook_settings(cmd, resource_group_name, name, slot=None,  # pylint: disable=unused-argument
                        app_id=None, app_secret_setting_name=None,  # pylint: disable=unused-argument
                        graph_api_version=None, scopes=None):    # pylint: disable=unused-argument
    existing_auth = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in existing_auth.keys():
            existing_auth["identityProviders"] = {}
    if "facebook" not in existing_auth["identityProviders"].keys():
        existing_auth["identityProviders"]["facebook"] = {}
    if app_id is not None or app_secret_setting_name is not None:
        if "registration" not in existing_auth["identityProviders"]["facebook"].keys():
            existing_auth["identityProviders"]["facebook"]["registration"] = {}
    if scopes is not None:
        if "login" not in existing_auth["identityProviders"]["facebook"].keys():
            existing_auth["identityProviders"]["facebook"]["login"] = {}
    
    if app_id is not None:
        existing_auth["identityProviders"]["facebook"]["registration"]["appId"] = app_id
    if app_secret_setting_name is not None:
        existing_auth["identityProviders"]["facebook"]["registration"]["appSecretSettingName"] = app_secret_setting_name
    if graph_api_version is not None:
        existing_auth["identityProviders"]["facebook"]["graphApiVersion"] = graph_api_version
    if scopes is not None:
        existing_auth["identityProviders"]["facebook"]["login"]["scopes"] = scopes.split(",")
    final_json = {
        "properties": existing_auth
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["facebook"]

def get_github_settings(cmd, resource_group_name, name, slot=None):
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        return {}
    if "gitHub" not in auth_settings["identityProviders"].keys():
        return {}
    return auth_settings["identityProviders"]["gitHub"]

def update_github_settings(cmd, resource_group_name, name, slot=None,  # pylint: disable=unused-argument
                        client_id=None, client_secret_setting_name=None,  # pylint: disable=unused-argument
                        scopes=None):    # pylint: disable=unused-argument
    existing_auth = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in existing_auth.keys():
            existing_auth["identityProviders"] = {}
    if "gitHub" not in existing_auth["identityProviders"].keys():
        existing_auth["identityProviders"]["gitHub"] = {}
    if client_id is not None or client_secret_setting_name is not None:
        if "registration" not in existing_auth["identityProviders"]["gitHub"].keys():
            existing_auth["identityProviders"]["gitHub"]["registration"] = {}
    if scopes is not None:
        if "login" not in existing_auth["identityProviders"]["gitHub"].keys():
            existing_auth["identityProviders"]["gitHub"]["login"] = {}
    
    if client_id is not None:
        existing_auth["identityProviders"]["gitHub"]["registration"]["clientId"] = client_id
    if client_secret_setting_name is not None:
        existing_auth["identityProviders"]["gitHub"]["registration"]["clientSecretSettingName"] = client_secret_setting_name
    if scopes is not None:
        existing_auth["identityProviders"]["gitHub"]["login"]["scopes"] = scopes.split(",")
    final_json = {
        "properties": existing_auth
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["gitHub"]

def get_google_settings(cmd, resource_group_name, name, slot=None):
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        return {}
    if "google" not in auth_settings["identityProviders"].keys():
        return {}
    return auth_settings["identityProviders"]["google"]

def update_google_settings(cmd, resource_group_name, name, slot=None,  # pylint: disable=unused-argument
                        client_id=None, client_secret_setting_name=None,  # pylint: disable=unused-argument
                        scopes=None, allowed_token_audiences=None):    # pylint: disable=unused-argument
    existing_auth = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in existing_auth.keys():
            existing_auth["identityProviders"] = {}
    if "google" not in existing_auth["identityProviders"].keys():
        existing_auth["identityProviders"]["google"] = {}
    if client_id is not None or client_secret_setting_name is not None:
        if "registration" not in existing_auth["identityProviders"]["google"].keys():
            existing_auth["identityProviders"]["google"]["registration"] = {}
    if scopes is not None:
        if "login" not in existing_auth["identityProviders"]["google"].keys():
            existing_auth["identityProviders"]["google"]["login"] = {}
    if allowed_token_audiences is not None:
        if "validation" not in existing_auth["identityProviders"]["google"].keys():
            existing_auth["identityProviders"]["google"]["validation"] = {}
        
    if client_id is not None:
        existing_auth["identityProviders"]["google"]["registration"]["clientId"] = client_id
    if client_secret_setting_name is not None:
        existing_auth["identityProviders"]["google"]["registration"]["clientSecretSettingName"] = client_secret_setting_name
    if scopes is not None:
        existing_auth["identityProviders"]["google"]["login"]["scopes"] = scopes.split(",")
    if allowed_token_audiences is not None:
        existing_auth["identityProviders"]["google"]["validation"]["allowedAudiences"] = allowed_token_audiences.split(",")
    final_json = {
        "properties": existing_auth
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["google"]

def get_twitter_settings(cmd, resource_group_name, name, slot=None):
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        return {}
    if "twitter" not in auth_settings["identityProviders"].keys():
        return {}
    return auth_settings["identityProviders"]["twitter"]

def update_twitter_settings(cmd, resource_group_name, name, slot=None,  # pylint: disable=unused-argument
                        consumer_key=None, consumer_secret_setting_name=None):  # pylint: disable=unused-argument
    existing_auth = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in existing_auth.keys():
            existing_auth["identityProviders"] = {}
    if "twitter" not in existing_auth["identityProviders"].keys():
        existing_auth["identityProviders"]["twitter"] = {}
    if consumer_key is not None or consumer_secret_setting_name is not None:
        if "registration" not in existing_auth["identityProviders"]["twitter"].keys():
            existing_auth["identityProviders"]["twitter"]["registration"] = {}
    
    if consumer_key is not None:
        existing_auth["identityProviders"]["twitter"]["registration"]["consumerKey"] = client_id
    if consumer_secret_setting_name is not None:
        existing_auth["identityProviders"]["twitter"]["registration"]["consumerSecretSettingName"] = client_secret_setting_name
    final_json = {
        "properties": existing_auth
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["twitter"]

def get_apple_settings(cmd, resource_group_name, name, slot=None):
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        return {}
    if "apple" not in auth_settings["identityProviders"].keys():
        return {}
    return auth_settings["identityProviders"]["apple"]

def update_apple_settings(cmd, resource_group_name, name, slot=None,  # pylint: disable=unused-argument
                        client_id=None, client_secret_setting_name=None,  # pylint: disable=unused-argument
                        scopes=None):    # pylint: disable=unused-argument
    existing_auth = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in existing_auth.keys():
            existing_auth["identityProviders"] = {}
    if "apple" not in existing_auth["identityProviders"].keys():
        existing_auth["identityProviders"]["apple"] = {}
    if client_id is not None or client_secret_setting_name is not None:
        if "registration" not in existing_auth["identityProviders"]["apple"].keys():
            existing_auth["identityProviders"]["apple"]["registration"] = {}
    if scopes is not None:
        if "login" not in existing_auth["identityProviders"]["apple"].keys():
            existing_auth["identityProviders"]["apple"]["login"] = {}
    
    if client_id is not None:
        existing_auth["identityProviders"]["apple"]["registration"]["clientId"] = client_id
    if client_secret_setting_name is not None:
        existing_auth["identityProviders"]["apple"]["registration"]["clientSecretSettingName"] = client_secret_setting_name
    if scopes is not None:
        existing_auth["identityProviders"]["apple"]["login"]["scopes"] = scopes.split(",")
    final_json = {
        "properties": existing_auth
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["apple"]

def get_oidc_provider_settings(cmd, resource_group_name, name, provider_name, slot=None): # pylint: disable=unused-argument
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    if "customOpenIdConnectProviders" not in auth_settings["identityProviders"].keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    if provider_name not in auth_settings["identityProviders"]["customOpenIdConnectProviders"].keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    return auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]

def add_oidc_provider_settings(cmd, resource_group_name, name, provider_name, slot=None, # pylint: disable=unused-argument
                                client_id=None, client_secret_setting_name=None,  # pylint: disable=unused-argument
                                openid_configuration=None, scopes=None):    # pylint: disable=unused-argument
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        auth_settings["identityProviders"] = {}
    if "customOpenIdConnectProviders" not in auth_settings["identityProviders"].keys():
        auth_settings["identityProviders"]["customOpenIdConnectProviders"] = {}
    if provider_name in auth_settings["identityProviders"]["customOpenIdConnectProviders"].keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has already been configured: ' + provider_name + '. Please use az webapp auth oidc update to update the provider.')
    auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name] = {
        "registration": {
            "clientId": client_id,
            "clientCredential": {
                "clientSecretSettingName": client_secret_setting_name
            },
            "openIdConnectConfiguration": {
                "wellKnownOpenIdConfiguration": openid_configuration
            }
        }
    }
    if scopes is not None:
        auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["login"] = {}
        auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["login"]["scopes"] = scopes.split(',')
    
    final_json = {
        "properties": auth_settings
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["customOpenIdConnectProviders"][provider_name]

def update_oidc_provider_settings(cmd, resource_group_name, name, provider_name, slot=None, # pylint: disable=unused-argument
                                client_id=None, client_secret_setting_name=None,  # pylint: disable=unused-argument
                                openid_configuration=None, scopes=None):    # pylint: disable=unused-argument
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    if "customOpenIdConnectProviders" not in auth_settings["identityProviders"].keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    if provider_name not in auth_settings["identityProviders"]["customOpenIdConnectProviders"].keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)

    if client_id is not None or client_secret_setting_name is not None or openid_configuration is not None:
        if "registration" not in auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name].keys():
            auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"] = {}
    
    if client_secret_setting_name is not None:
        if "clientCredential" not in auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"].keys():
            auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"]["clientCredential"] = {}
    
    if openid_configuration is not None:
        if "openIdConnectConfiguration" not in auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"].keys():
            auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"]["openIdConnectConfiguration"] = {}
    
    if scopes is not None:
        if "login" not in auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name].keys():
            auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["login"] = {}
    
    if client_id is not None:
        auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"]["clientId"] = client_id
    if client_secret_setting_name is not None:
        auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"]["clientCredential"]["clientSecretSettingName"] = client_secret_setting_name
    if openid_configuration is not None:
        auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["registration"]["openIdConnectConfiguration"]["wellKnownOpenIdConfiguration"] = openid_configuration
    if scopes is not None:
        auth_settings["identityProviders"]["customOpenIdConnectProviders"][provider_name]["login"]["scopes"] = scopes.split(",")
    final_json = {
        "properties": auth_settings
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return r.json()["properties"]["identityProviders"]["customOpenIdConnectProviders"][provider_name]

def remove_oidc_provider_settings(cmd, resource_group_name, name, provider_name, slot=None): # pylint: disable=unused-argument
    auth_settings = get_auth_settings_v2(cmd, resource_group_name, name, slot)["properties"]
    if "identityProviders" not in auth_settings.keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    if "customOpenIdConnectProviders" not in auth_settings["identityProviders"].keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    if provider_name not in auth_settings["identityProviders"]["customOpenIdConnectProviders"].keys():
        raise CLIError('Usage Error: The following custom OpenID Connect provider has not been configured: ' + provider_name)
    auth_settings["identityProviders"]["customOpenIdConnectProviders"].pop(provider_name, None)
    final_json = {
        "properties": auth_settings
    }
    sub_id = get_subscription_id(cmd.cli_ctx)
    r = send_raw_request(cmd.cli_ctx, "PUT", "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/config/authSettingsV2?api-version=2020-12-01".format(sub_id, resource_group_name, name), None, None, json.dumps(final_json))
    return {}


