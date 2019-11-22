# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.commands.client_factory import get_subscription_id
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import _resource_client_factory
from azext_connectedk8s._client_factory import _auth_client_factory
from azext_connectedk8s._multi_api_adaptor import MultiAPIAdaptor
import datetime
from msrest.serialization import TZ_UTC
from dateutil.relativedelta import relativedelta
import uuid
from azure.graphrbac.models import (PasswordCredential, ApplicationCreateParameters, ServicePrincipalCreateParameters)
from knack.log import get_logger
import os
import json
from azure.mgmt.subscription import SubscriptionClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.cli.core._profile import Profile
from azure.cli.core.api import get_config_dir
import platform
import yaml, copy, base64, atexit, tempfile
from kubernetes.client import ApiClient, Configuration


logger = get_logger(__name__)

def create_connectedk8s(cmd, client, resource_group_name, cluster_name, onboarding_spn_id=None, onboarding_spn_secret=None, location=None, kube_config=None, kube_context=None, tags=None):
    #print(kube_config)
    subscription_id = get_subscription_id(cmd.cli_ctx)
    print(subscription_id)
    """if(subscription_id is not None):
        try:
            sub_client = get_client_from_cli_profile(SubscriptionClient)
        except CLIError:
            logger.info("Not logged in, running az login")
            _run_az_cli_login()
            sub_client = get_client_from_cli_profile(SubscriptionClient)
        #print(sub_client.subscriptions.list())
        sub_list = []
        for sub in sub_client.subscriptions.list():
            sub_list.append(sub.subscription_id)
        print(sub_list)
        if(subscription_id not in sub_list):
            raise CLIError("Provided subscription name does not exist")"""

    #if(resource_group_name is None):
    #    raise CLIError("Provide resource group name")
    #print(get_subscription_id(cmd.cli_ctx))
    #print(subscription_name)
    rg_client = _resource_client_factory(cmd.cli_ctx)
    rg_name_list = []
    for item in rg_client.resource_groups.list():
        rg_name_list.append(item.name)
        if(item.name==resource_group_name and location!=item.location):
            raise CLIError("The resource group already exists in the location {}".format(item.location))
    print(rg_name_list)
    if(resource_group_name not in rg_name_list):
        print("Creating resource group")
        if(location is None):
            raise CLIError("Provide the location to create the resource group")
        #profile = Profile(cli_ctx=cmd.cli_ctx)
        #print(json.dumps(profile.get_sp_auth_info(subscription_name), indent=2))
        # = profile.get_raw_token(cmd, subscription=subscription_name, resource=resource_group_name)
        #accToken = profile.get_access_token(cmd, subscription=subscription_name, resource=resource_group_name)
        #print(accToken)
        resource_group_params = {'location': location}
        rg_client.resource_groups.create_or_update(resource_group_name, resource_group_params)

    print("start")
    #print(get_subscription_id(cmd.cli_ctx))
    graph_client = _graph_client_factory(cmd.cli_ctx)
    onboarding_tenant_id = graph_client.config.tenant_id
    if(onboarding_spn_id is not None and onboarding_spn_secret is None):
        raise CLIError("Provide the onboarding spn password")
    #client1 = _graph_client_factory(cmd.cli_ctx)
    spn_list = list_spn(graph_client)
    spn_appid_list=[]
    for i in spn_list:
        spn_appid_list.append(i.app_id)
    if(onboarding_spn_id is not None and onboarding_spn_id not in spn_appid_list):
        raise CLIError("Provided service principal does not exist")
    if(onboarding_spn_id is None):
        file_name_connectedk8s = 'azureArcServicePrincipal.json'
        principal_obj = load_acs_service_principal(subscription_id, file_name=file_name_connectedk8s)
        #print(principal_obj)
        var = None
        if principal_obj:
            if(principal_obj.get('service_principal') not in spn_appid_list):
                erase_acs_service_principal(file_name=file_name_connectedk8s)
                var = "temp"
        if (principal_obj and var is None):
            onboarding_spn_id = principal_obj.get('service_principal')
            #print(onboarding_spn_id)
            onboarding_spn_secret = principal_obj.get('client_secret')
        else:
            graph_client = _graph_client_factory(cmd.cli_ctx)
            role_client = _auth_client_factory(cmd.cli_ctx).role_assignments
            print(role_client.config.subscription_id)
            scopes = ['/subscriptions/' + role_client.config.subscription_id]
            years = 1
            import time
            app_start_date = datetime.datetime.now(TZ_UTC)
            app_end_date = app_start_date + relativedelta(years=years)
            app_display_name = ('azure-cli-' + app_start_date.strftime('%Y-%m-%d-%H-%M-%S'))
            name = 'http://' + app_display_name
            password = str(uuid.uuid4())
            aad_application = create_application(cmd,
                                            display_name=app_display_name,
                                            homepage='https://' + app_display_name,
                                            identifier_uris=[name],
                                            available_to_other_tenants=False,
                                            password=password,
                                            key_value=None,
                                            start_date=app_start_date,
                                            end_date=app_end_date,
                                            credential_description='rbac')
            _RETRY_TIMES = 36
            app_id = aad_application.app_id
            aad_sp = None
            for l in range(0, _RETRY_TIMES):
                try:
                    aad_sp = _create_service_principal(cmd.cli_ctx, app_id, resolve_app=False)
                    break
                except Exception as ex:  # pylint: disable=broad-except
                    if l < _RETRY_TIMES and (
                            ' does not reference ' in str(ex) or ' does not exist ' in str(ex)):
                        time.sleep(5)
                        logger.warning('Retrying service principal creation: %s/%s', l + 1, _RETRY_TIMES)
                    else:
                        logger.warning(
                            "Creating service principal failed for appid '%s'. Trace followed:\n%s",
                            name, ex.response.headers if hasattr(ex,
                                                                'response') else ex)  # pylint: disable=no-member
                        raise
            #correct
            store_acs_service_principal(subscription_id, password, app_id, file_name=file_name_connectedk8s)
            role = 'Kubernetes Cluster - Azure Arc Onborading Role'
            sp_oid = aad_sp.object_id
            for scope in scopes:
                logger.warning('Creating a role assignment under the scope of "%s"', scope)
                for l in range(0, _RETRY_TIMES):
                    try:
                        _create_role_assignment(cmd.cli_ctx, role, sp_oid, None, scope, resolve_assignee=False)
                        break
                    except Exception as ex:
                        if l < _RETRY_TIMES and ' does not exist in the directory ' in str(ex):
                            time.sleep(5)
                            logger.warning('  Retrying role assignment creation: %s/%s', l + 1,
                                        _RETRY_TIMES)
                            continue
                        elif _error_caused_by_role_assignment_exists(ex):
                            logger.warning('  Role assignment already exits.\n')
                            break
                        else:
                            # dump out history for diagnoses
                            logger.warning('  Role assignment creation failed.\n')
                            if getattr(ex, 'response', None) is not None:
                                logger.warning('  role assignment response headers: %s\n',
                                            ex.response.headers)  # pylint: disable=no-member
                        raise
            onboarding_spn_id = app_id
            onboarding_spn_secret = password
            print("spn_id: "+app_id)
            print("spn_secret: "+password)
            print("name: "+name)
            print("app_display_name: "+app_display_name)
            print("tenant_id: "+graph_client.config.tenant_id)
            print()
    #load_kube_config(config_file=kube_config, context=kube_context)
    return client.create(resource_group_name, cluster_name, onboarding_tenant_id, onboarding_spn_id, onboarding_spn_secret, location, kube_config, kube_context)

def erase_acs_service_principal(file_name='acsServicePrincipal.json'):
    config_path = os.path.join(get_config_dir(), file_name)
    open(config_path, 'w').close()

def load_acs_service_principal(subscription_id, file_name='acsServicePrincipal.json'):
    config_path = os.path.join(get_config_dir(), file_name)
    #print(config_path + "load")
    config = load_service_principals(config_path)
    #print(config)
    if not config:
        return None
    return config.get(subscription_id)

def load_service_principals(config_path):
    if not os.path.exists(config_path):
        return None
    fd = os.open(config_path, os.O_RDONLY)
    try:
        with os.fdopen(fd) as f:
            return json.loads(f.read())
    except:  # pylint: disable=bare-except
        return None

def store_acs_service_principal(subscription_id, client_secret, service_principal,
                                file_name='acsServicePrincipal.json'):
    obj = {}
    if client_secret:
        obj['client_secret'] = client_secret
    if service_principal:
        obj['service_principal'] = service_principal

    config_path = os.path.join(get_config_dir(), file_name)
    full_config = load_service_principals(config_path=config_path)
    if not full_config:
        full_config = {}
    full_config[subscription_id] = obj

    with os.fdopen(os.open(config_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600),
                   'w+') as spFile:
        json.dump(full_config, spFile)

def list_spn(client):
    show_mine = True
    if show_mine:
        return list_owned_objects(client.signed_in_user, 'servicePrincipal')

def list_owned_objects(client, object_type=None):
    result = client.list_owned_objects()
    #print(result)
    if object_type:
        result = [r for r in result if r.object_type and r.object_type.lower() == object_type.lower()]
        #print(result)
    return result

def get_connectedk8s(cmd, client, resource_group_name, cluster_name):
    return client.get(resource_group_name, cluster_name)

def list_connectedk8s(cmd, client, resource_group_name=None):
    if(resource_group_name is None):
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)
    
def delete_connectedk8s(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None):
    return client.delete(resource_group_name, cluster_name, kube_config, kube_context)

def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

def create_application(cmd, display_name, homepage=None, identifier_uris=None,  # pylint: disable=too-many-locals
                       available_to_other_tenants=False, password=None, reply_urls=None,
                       key_value=None, key_type=None, key_usage=None, start_date=None, end_date=None,
                       oauth2_allow_implicit_flow=None, required_resource_accesses=None, native_app=None,
                       credential_description=None, app_roles=None):
    graph_client = _graph_client_factory(cmd.cli_ctx)
    password_creds = [PasswordCredential(start_date=start_date, end_date=end_date, key_id=str(uuid.uuid4()), value=password, custom_key_identifier=None)]
    app_create_param = ApplicationCreateParameters(available_to_other_tenants=False,
                                                   display_name=display_name,
                                                   identifier_uris=identifier_uris,
                                                   homepage='https://' + display_name,
                                                   reply_urls=None,
                                                   key_credentials=None,
                                                   password_credentials=password_creds,
                                                   oauth2_allow_implicit_flow=None,
                                                   required_resource_access=None,
                                                   app_roles=None)
    try:
        result = graph_client.applications.create(app_create_param)
    except GraphErrorException as ex:
        if 'insufficient privileges' in str(ex).lower():
            link = 'https://docs.microsoft.com/azure/azure-resource-manager/resource-group-create-service-principal-portal'  # pylint: disable=line-too-long
            raise CLIError("Directory permission is needed for the current user to register the application. "
                           "For how to configure, please refer '{}'. Original error: {}".format(link, ex))
        raise
    return result

def _create_service_principal(cli_ctx, identifier, resolve_app=True):
    client = _graph_client_factory(cli_ctx)
    app_id = identifier
    if resolve_app:
        if _is_guid(identifier):
            result = list(client.applications.list(filter="appId eq '{}'".format(identifier)))
        else:
            result = list(client.applications.list(
                filter="identifierUris/any(s:s eq '{}')".format(identifier)))

        try:
            if not result:  # assume we get an object id
                result = [client.applications.get(identifier)]
            app_id = result[0].app_id
        except GraphErrorException:
            pass  # fallback to appid (maybe from an external tenant?)

    return client.service_principals.create(ServicePrincipalCreateParameters(app_id=app_id, account_enabled=True))

def _error_caused_by_role_assignment_exists(ex):
    return getattr(ex, 'status_code', None) == 409 and 'role assignment already exists' in ex.message

def _create_role_assignment(cli_ctx, role, assignee, resource_group_name=None, scope=None,
                            resolve_assignee=True, assignee_principal_type=None):
    print("now")
    factory = _auth_client_factory(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions
    role = '34e09817-6cbe-4d01-b1a2-e0eac5743d41'
    role_id = '/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/{}'.format(definitions_client.config.subscription_id, role)
    object_id = assignee
    worker = MultiAPIAdaptor(cli_ctx)
    return worker.create_role_assignment(assignments_client, uuid.uuid4(), role_id, object_id, scope,
                                         assignee_principal_type)

