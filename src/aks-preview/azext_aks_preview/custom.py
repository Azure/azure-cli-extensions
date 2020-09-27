# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import binascii
import datetime
import errno
import json
import os
import os.path
import platform
import re
import ssl
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import base64
import webbrowser
from math import isnan
from six.moves.urllib.request import urlopen  # pylint: disable=import-error
from six.moves.urllib.error import URLError  # pylint: disable=import-error
import requests
from knack.log import get_logger
from knack.util import CLIError
from knack.prompting import prompt_pass, NoTTYException

import yaml  # pylint: disable=import-error
from dateutil.relativedelta import relativedelta  # pylint: disable=import-error
from dateutil.parser import parse  # pylint: disable=import-error
from msrestazure.azure_exceptions import CloudError

import colorama  # pylint: disable=import-error
from tabulate import tabulate  # pylint: disable=import-error
from azure.cli.core.api import get_config_dir
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.keys import is_valid_ssh_rsa_public_key
from azure.cli.core.util import in_cloud_console, shell_safe_json_parse, truncate_text, sdk_no_wait
from azure.cli.core.commands import LongRunningOperation
from azure.graphrbac.models import (ApplicationCreateParameters,
                                    PasswordCredential,
                                    KeyCredential,
                                    ServicePrincipalCreateParameters,
                                    GetObjectsParameters)
from .vendored_sdks.azure_mgmt_preview_aks.v2020_09_01.models import (ContainerServiceLinuxProfile,
                                                                      ManagedClusterWindowsProfile,
                                                                      ContainerServiceNetworkProfile,
                                                                      ManagedClusterServicePrincipalProfile,
                                                                      ContainerServiceSshConfiguration,
                                                                      ContainerServiceSshPublicKey,
                                                                      ManagedCluster,
                                                                      ManagedClusterAADProfile,
                                                                      ManagedClusterAddonProfile,
                                                                      ManagedClusterAgentPoolProfile,
                                                                      AgentPool,
                                                                      AgentPoolUpgradeSettings,
                                                                      ContainerServiceStorageProfileTypes,
                                                                      ManagedClusterIdentity,
                                                                      ManagedClusterAPIServerAccessProfile,
                                                                      ManagedClusterSKU,
                                                                      ManagedClusterIdentityUserAssignedIdentitiesValue)
from ._client_factory import cf_resource_groups
from ._client_factory import get_auth_management_client
from ._client_factory import get_graph_rbac_management_client
from ._client_factory import get_msi_client
from ._client_factory import cf_resources
from ._client_factory import get_resource_by_name
from ._client_factory import cf_container_registry_service
from ._client_factory import cf_storage
from ._client_factory import cf_agent_pools


from ._helpers import (_populate_api_server_access_profile, _set_vm_set_type,
                       _set_outbound_type, _parse_comma_separated_list,
                       _trim_fqdn_name_containing_hcp)
from ._loadbalancer import (set_load_balancer_sku, is_load_balancer_profile_provided,
                            update_load_balancer_profile, create_load_balancer_profile)
from ._consts import CONST_KUBE_DASHBOARD_ADDON_NAME
from ._consts import CONST_INGRESS_APPGW_ADDON_NAME
from ._consts import CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID, CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME
from ._consts import CONST_INGRESS_APPGW_SUBNET_PREFIX, CONST_INGRESS_APPGW_SUBNET_ID
from ._consts import CONST_INGRESS_APPGW_WATCH_NAMESPACE
from ._consts import CONST_SCALE_SET_PRIORITY_REGULAR, CONST_SCALE_SET_PRIORITY_SPOT, CONST_SPOT_EVICTION_POLICY_DELETE
from ._consts import CONST_CONFCOM_ADDON_NAME, CONST_ACC_SGX_QUOTE_HELPER_ENABLED
from ._consts import CONST_OPEN_SERVICE_MESH_ADDON_NAME, CONST_OPEN_SERVICE_MESH_NAME_KEY
from ._consts import ADDONS
logger = get_logger(__name__)


def which(binary):
    path_var = os.getenv('PATH')
    if platform.system() == 'Windows':
        binary = binary + '.exe'
        parts = path_var.split(';')
    else:
        parts = path_var.split(':')

    for part in parts:
        bin_path = os.path.join(part, binary)
        if os.path.exists(bin_path) and os.path.isfile(bin_path) and os.access(bin_path, os.X_OK):
            return bin_path

    return None


def wait_then_open(url):
    """
    Waits for a bit then opens a URL.  Useful for waiting for a proxy to come up, and then open the URL.
    """
    for _ in range(1, 10):
        try:
            urlopen(url, context=_ssl_context())
        except URLError:
            time.sleep(1)
        break
    webbrowser.open_new_tab(url)


def wait_then_open_async(url):
    """
    Spawns a thread that waits for a bit then opens a URL.
    """
    t = threading.Thread(target=wait_then_open, args=({url}))
    t.daemon = True
    t.start()


def _ssl_context():
    if sys.version_info < (3, 4) or (in_cloud_console() and platform.system() == 'Windows'):
        try:
            return ssl.SSLContext(ssl.PROTOCOL_TLS)  # added in python 2.7.13 and 3.6
        except AttributeError:
            return ssl.SSLContext(ssl.PROTOCOL_TLSv1)

    return ssl.create_default_context()


def _build_service_principal(rbac_client, cli_ctx, name, url, client_secret):
    # use get_progress_controller
    hook = cli_ctx.get_progress_controller(True)
    hook.add(messsage='Creating service principal', value=0, total_val=1.0)
    logger.info('Creating service principal')
    # always create application with 5 years expiration
    start_date = datetime.datetime.utcnow()
    end_date = start_date + relativedelta(years=5)
    result = create_application(rbac_client.applications, name, url, [url], password=client_secret,
                                start_date=start_date, end_date=end_date)
    service_principal = result.app_id  # pylint: disable=no-member
    for x in range(0, 10):
        hook.add(message='Creating service principal', value=0.1 * x, total_val=1.0)
        try:
            create_service_principal(cli_ctx, service_principal, rbac_client=rbac_client)
            break
        # TODO figure out what exception AAD throws here sometimes.
        except Exception as ex:  # pylint: disable=broad-except
            logger.info(ex)
            time.sleep(2 + 2 * x)
    else:
        return False
    hook.add(message='Finished service principal creation', value=1.0, total_val=1.0)
    logger.info('Finished service principal creation')
    return service_principal


def _add_role_assignment(cli_ctx, role, service_principal_msi_id, is_service_principal=True, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for AAD role to propagate', value=0, total_val=1.0)
    logger.info('Waiting for AAD role to propagate')
    for x in range(0, 10):
        hook.add(message='Waiting for AAD role to propagate', value=0.1 * x, total_val=1.0)
        try:
            # TODO: break this out into a shared utility library
            create_role_assignment(cli_ctx, role, service_principal_msi_id, is_service_principal, scope=scope)
            break
        except CloudError as ex:
            if ex.message == 'The role assignment already exists.':
                break
            logger.info(ex.message)
        except:  # pylint: disable=bare-except
            pass
        time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message='AAD role propagation done', value=1.0, total_val=1.0)
    logger.info('AAD role propagation done')
    return True


def _delete_role_assignments(cli_ctx, role, service_principal, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for AAD role to delete', value=0, total_val=1.0)
    logger.info('Waiting for AAD role to delete')
    for x in range(0, 10):
        hook.add(message='Waiting for AAD role to delete', value=0.1 * x, total_val=1.0)
        try:
            delete_role_assignments(cli_ctx,
                                    role=role,
                                    assignee=service_principal,
                                    scope=scope)
            break
        except CLIError as ex:
            raise ex
        except CloudError as ex:
            logger.info(ex)
        time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message='AAD role deletion done', value=1.0, total_val=1.0)
    logger.info('AAD role deletion done')
    return True


def _get_default_dns_prefix(name, resource_group_name, subscription_id):
    # Use subscription id to provide uniqueness and prevent DNS name clashes
    name_part = re.sub('[^A-Za-z0-9-]', '', name)[0:10]
    if not name_part[0].isalpha():
        name_part = (str('a') + name_part)[0:10]
    resource_group_part = re.sub('[^A-Za-z0-9-]', '', resource_group_name)[0:16]
    return '{}-{}-{}'.format(name_part, resource_group_part, subscription_id[0:6])


# pylint: disable=too-many-locals
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


def load_acs_service_principal(subscription_id, file_name='acsServicePrincipal.json'):
    config_path = os.path.join(get_config_dir(), file_name)
    config = load_service_principals(config_path)
    if not config:
        return None
    return config.get(subscription_id)


def load_service_principals(config_path):
    if not os.path.exists(config_path):
        return None
    fd = os.open(config_path, os.O_RDONLY)
    try:
        with os.fdopen(fd) as f:
            return shell_safe_json_parse(f.read())
    except:  # pylint: disable=bare-except
        return None


def _invoke_deployment(cmd, resource_group_name, deployment_name, template, parameters, validate, no_wait,
                       subscription_id=None):
    from azure.cli.core.profiles import ResourceType
    DeploymentProperties = cmd.get_models('DeploymentProperties', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    properties = DeploymentProperties(template=template, parameters=parameters, mode='incremental')
    smc = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                  subscription_id=subscription_id).deployments
    if validate:
        logger.info('==== BEGIN TEMPLATE ====')
        logger.info(json.dumps(template, indent=2))
        logger.info('==== END TEMPLATE ====')

    if cmd.supported_api_version(min_api='2019-10-01', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES):
        Deployment = cmd.get_models('Deployment', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
        deployment = Deployment(properties=properties)

        if validate:
            validation_poller = smc.validate(resource_group_name, deployment_name, deployment)
            return LongRunningOperation(cmd.cli_ctx)(validation_poller)
        return sdk_no_wait(no_wait, smc.create_or_update, resource_group_name, deployment_name, deployment)

    if validate:
        return smc.validate(resource_group_name, deployment_name, properties)
    return sdk_no_wait(no_wait, smc.create_or_update, resource_group_name, deployment_name, properties)


def create_application(client, display_name, homepage, identifier_uris,
                       available_to_other_tenants=False, password=None, reply_urls=None,
                       key_value=None, key_type=None, key_usage=None, start_date=None,
                       end_date=None):
    from azure.graphrbac.models import GraphErrorException
    password_creds, key_creds = _build_application_creds(password=password, key_value=key_value, key_type=key_type,
                                                         key_usage=key_usage, start_date=start_date, end_date=end_date)

    app_create_param = ApplicationCreateParameters(available_to_other_tenants=available_to_other_tenants,
                                                   display_name=display_name,
                                                   identifier_uris=identifier_uris,
                                                   homepage=homepage,
                                                   reply_urls=reply_urls,
                                                   key_credentials=key_creds,
                                                   password_credentials=password_creds)
    try:
        return client.create(app_create_param)
    except GraphErrorException as ex:
        if 'insufficient privileges' in str(ex).lower():
            link = 'https://docs.microsoft.com/azure/azure-resource-manager/resource-group-create-service-principal-portal'  # pylint: disable=line-too-long
            raise CLIError("Directory permission is needed for the current user to register the application. "
                           "For how to configure, please refer '{}'. Original error: {}".format(link, ex))
        raise


def _build_application_creds(password=None, key_value=None, key_type=None,
                             key_usage=None, start_date=None, end_date=None):
    if password and key_value:
        raise CLIError('specify either --password or --key-value, but not both.')

    if not start_date:
        start_date = datetime.datetime.utcnow()
    elif isinstance(start_date, str):
        start_date = parse(start_date)

    if not end_date:
        end_date = start_date + relativedelta(years=1)
    elif isinstance(end_date, str):
        end_date = parse(end_date)

    key_type = key_type or 'AsymmetricX509Cert'
    key_usage = key_usage or 'Verify'

    password_creds = None
    key_creds = None
    if password:
        password_creds = [PasswordCredential(start_date=start_date, end_date=end_date,
                                             key_id=str(uuid.uuid4()), value=password)]
    elif key_value:
        key_creds = [KeyCredential(start_date=start_date, end_date=end_date, value=key_value,
                                   key_id=str(uuid.uuid4()), usage=key_usage, type=key_type)]

    return (password_creds, key_creds)


def create_service_principal(cli_ctx, identifier, resolve_app=True, rbac_client=None):
    if rbac_client is None:
        rbac_client = get_graph_rbac_management_client(cli_ctx)

    if resolve_app:
        try:
            uuid.UUID(identifier)
            result = list(rbac_client.applications.list(filter="appId eq '{}'".format(identifier)))
        except ValueError:
            result = list(rbac_client.applications.list(
                filter="identifierUris/any(s:s eq '{}')".format(identifier)))

        if not result:  # assume we get an object id
            result = [rbac_client.applications.get(identifier)]
        app_id = result[0].app_id
    else:
        app_id = identifier

    return rbac_client.service_principals.create(ServicePrincipalCreateParameters(app_id=app_id, account_enabled=True))


def create_role_assignment(cli_ctx, role, assignee, is_service_principal, resource_group_name=None, scope=None):
    return _create_role_assignment(cli_ctx,
                                   role, assignee, resource_group_name,
                                   scope, resolve_assignee=is_service_principal)


def _create_role_assignment(cli_ctx, role, assignee,
                            resource_group_name=None, scope=None, resolve_assignee=True):
    from azure.cli.core.profiles import ResourceType, get_sdk
    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions

    scope = _build_role_scope(resource_group_name, scope, assignments_client.config.subscription_id)

    role_id = _resolve_role_id(role, scope, definitions_client)

    # If the cluster has service principal resolve the service principal client id to get the object id,
    # if not use MSI object id.
    object_id = _resolve_object_id(cli_ctx, assignee) if resolve_assignee else assignee
    RoleAssignmentCreateParameters = get_sdk(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                             'RoleAssignmentCreateParameters', mod='models',
                                             operation_group='role_assignments')
    parameters = RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=object_id)
    assignment_name = uuid.uuid4()
    custom_headers = None
    return assignments_client.create(scope, assignment_name, parameters, custom_headers=custom_headers)


def delete_role_assignments(cli_ctx, ids=None, assignee=None, role=None, resource_group_name=None,
                            scope=None, include_inherited=False, yes=None):
    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions
    ids = ids or []
    if ids:
        if assignee or role or resource_group_name or scope or include_inherited:
            raise CLIError('When assignment ids are used, other parameter values are not required')
        for i in ids:
            assignments_client.delete_by_id(i)
        return
    if not any([ids, assignee, role, resource_group_name, scope, assignee, yes]):
        from knack.prompting import prompt_y_n
        msg = 'This will delete all role assignments under the subscription. Are you sure?'
        if not prompt_y_n(msg, default="n"):
            return

    scope = _build_role_scope(resource_group_name, scope,
                              assignments_client.config.subscription_id)
    assignments = _search_role_assignments(cli_ctx, assignments_client, definitions_client,
                                           scope, assignee, role, include_inherited,
                                           include_groups=False)

    if assignments:
        for a in assignments:
            assignments_client.delete_by_id(a.id)


def _delete_role_assignments(cli_ctx, role, service_principal, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for AAD role to delete', value=0, total_val=1.0)
    logger.info('Waiting for AAD role to delete')
    for x in range(0, 10):
        hook.add(message='Waiting for AAD role to delete', value=0.1 * x, total_val=1.0)
        try:
            delete_role_assignments(cli_ctx,
                                    role=role,
                                    assignee=service_principal,
                                    scope=scope)
            break
        except CLIError as ex:
            raise ex
        except CloudError as ex:
            logger.info(ex)
        time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message='AAD role deletion done', value=1.0, total_val=1.0)
    logger.info('AAD role deletion done')
    return True


def _search_role_assignments(cli_ctx, assignments_client, definitions_client,
                             scope, assignee, role, include_inherited, include_groups):
    assignee_object_id = None
    if assignee:
        assignee_object_id = _resolve_object_id(cli_ctx, assignee)

    # always use "scope" if provided, so we can get assignments beyond subscription e.g. management groups
    if scope:
        assignments = list(assignments_client.list_for_scope(
            scope=scope, filter='atScope()'))
    elif assignee_object_id:
        if include_groups:
            f = "assignedTo('{}')".format(assignee_object_id)
        else:
            f = "principalId eq '{}'".format(assignee_object_id)
        assignments = list(assignments_client.list(filter=f))
    else:
        assignments = list(assignments_client.list())

    if assignments:
        assignments = [a for a in assignments if (
            not scope or
            include_inherited and re.match(_get_role_property(a, 'scope'), scope, re.I) or
            _get_role_property(a, 'scope').lower() == scope.lower()
        )]

        if role:
            role_id = _resolve_role_id(role, scope, definitions_client)
            assignments = [i for i in assignments if _get_role_property(
                i, 'role_definition_id') == role_id]

        if assignee_object_id:
            assignments = [i for i in assignments if _get_role_property(
                i, 'principal_id') == assignee_object_id]

    return assignments


def _get_role_property(obj, property_name):
    if isinstance(obj, dict):
        return obj[property_name]
    return getattr(obj, property_name)


def _build_role_scope(resource_group_name, scope, subscription_id):
    subscription_scope = '/subscriptions/' + subscription_id
    if scope:
        if resource_group_name:
            err = 'Resource group "{}" is redundant because scope is supplied'
            raise CLIError(err.format(resource_group_name))
    elif resource_group_name:
        scope = subscription_scope + '/resourceGroups/' + resource_group_name
    else:
        scope = subscription_scope
    return scope


def _resolve_role_id(role, scope, definitions_client):
    role_id = None
    try:
        uuid.UUID(role)
        role_id = role
    except ValueError:
        pass
    if not role_id:  # retrieve role id
        role_defs = list(definitions_client.list(scope, "roleName eq '{}'".format(role)))
        if not role_defs:
            raise CLIError("Role '{}' doesn't exist.".format(role))
        if len(role_defs) > 1:
            ids = [r.id for r in role_defs]
            err = "More than one role matches the given name '{}'. Please pick a value from '{}'"
            raise CLIError(err.format(role, ids))
        role_id = role_defs[0].id
    return role_id


def _resolve_object_id(cli_ctx, assignee):
    client = get_graph_rbac_management_client(cli_ctx)
    result = None
    if assignee.find('@') >= 0:  # looks like a user principal name
        result = list(client.users.list(filter="userPrincipalName eq '{}'".format(assignee)))
    if not result:
        result = list(client.service_principals.list(
            filter="servicePrincipalNames/any(c:c eq '{}')".format(assignee)))
    if not result:  # assume an object id, let us verify it
        result = _get_object_stubs(client, [assignee])

    # 2+ matches should never happen, so we only check 'no match' here
    if not result:
        raise CLIError("No matches in graph database for '{}'".format(assignee))

    return result[0].object_id


def _get_object_stubs(graph_client, assignees):
    params = GetObjectsParameters(include_directory_object_references=True,
                                  object_ids=assignees)
    return list(graph_client.objects.get_objects_by_object_ids(params))


def subnet_role_assignment_exists(cli_ctx, scope):
    network_contributor_role_id = "4d97b98b-1d4f-4787-a291-c67834d212e7"

    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments

    for i in assignments_client.list_for_scope(scope=scope, filter='atScope()'):
        if i.scope == scope and i.role_definition_id.endswith(network_contributor_role_id):
            return True
    return False


def _get_user_assigned_identity_client_id(cli_ctx, resource_id):
    msi_client = get_msi_client(cli_ctx)
    pattern = '/subscriptions/.*?/resourcegroups/(.*?)/providers/microsoft.managedidentity/userassignedidentities/(.*)'
    resource_id = resource_id.lower()
    match = re.search(pattern, resource_id)
    if match:
        resource_group_name = match.group(1)
        identity_name = match.group(2)
        try:
            identity = msi_client.user_assigned_identities.get(resource_group_name=resource_group_name,
                                                               resource_name=identity_name)
        except CloudError as ex:
            if 'was not found' in ex.message:
                raise CLIError("Identity {} not found.".format(resource_id))
            raise CLIError(ex.message)
        return identity.client_id
    raise CLIError("Cannot parse identity name from provided resource id {}.".format(resource_id))


def _update_dict(dict1, dict2):
    cp = dict1.copy()
    cp.update(dict2)
    return cp


def aks_browse(cmd,     # pylint: disable=too-many-statements
               client,
               resource_group_name,
               name,
               disable_browser=False,
               listen_address='127.0.0.1',
               listen_port='8001'):
    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')

    # verify the kube-dashboard addon was not disabled
    instance = client.get(resource_group_name, name)
    addon_profiles = instance.addon_profiles or {}
    # addon name is case insensitive
    addon_profile = next((addon_profiles[k] for k in addon_profiles
                          if k.lower() == CONST_KUBE_DASHBOARD_ADDON_NAME.lower()),
                         ManagedClusterAddonProfile(enabled=True))
    if not addon_profile.enabled:
        raise CLIError('The kube-dashboard addon was disabled for this managed cluster.\n'
                       'To use "az aks browse" first enable the add-on\n'
                       'by running "az aks enable-addons --addons kube-dashboard".')

    _, browse_path = tempfile.mkstemp()

    aks_get_credentials(cmd, client, resource_group_name, name, admin=False, path=browse_path)
    # find the dashboard pod's name
    try:
        dashboard_pod = subprocess.check_output(
            ["kubectl", "get", "pods", "--kubeconfig", browse_path, "--namespace", "kube-system",
             "--output", "name", "--selector", "k8s-app=kubernetes-dashboard"],
            universal_newlines=True)
    except subprocess.CalledProcessError as err:
        raise CLIError('Could not find dashboard pod: {}'.format(err))
    if dashboard_pod:
        # remove any "pods/" or "pod/" prefix from the name
        dashboard_pod = str(dashboard_pod).split('/')[-1].strip()
    else:
        raise CLIError("Couldn't find the Kubernetes dashboard pod.")

    # find the port
    try:
        dashboard_port = subprocess.check_output(
            ["kubectl", "get", "pods", "--kubeconfig", browse_path, "--namespace", "kube-system",
             "--selector", "k8s-app=kubernetes-dashboard",
             "--output", "jsonpath='{.items[0].spec.containers[0].ports[0].containerPort}'"]
        )
        # output format: b"'{port}'"
        dashboard_port = int((dashboard_port.decode('utf-8').replace("'", "")))
    except subprocess.CalledProcessError as err:
        raise CLIError('Could not find dashboard port: {}'.format(err))

    # use https if dashboard container is using https
    if dashboard_port == 8443:
        protocol = 'https'
    else:
        protocol = 'http'

    proxy_url = 'http://{0}:{1}/'.format(listen_address, listen_port)
    dashboardURL = '{0}/api/v1/namespaces/kube-system/services/{1}:kubernetes-dashboard:/proxy/'.format(proxy_url,
                                                                                                        protocol)
    # launch kubectl port-forward locally to access the remote dashboard
    if in_cloud_console():
        # TODO: better error handling here.
        response = requests.post('http://localhost:8888/openport/{0}'.format(listen_port))
        result = json.loads(response.text)
        dashboardURL = '{0}api/v1/namespaces/kube-system/services/{1}:kubernetes-dashboard:/proxy/'.format(
            result['url'], protocol)
        term_id = os.environ.get('ACC_TERM_ID')
        if term_id:
            response = requests.post('http://localhost:8888/openLink/{0}'.format(term_id),
                                     json={"url": dashboardURL})
        logger.warning('To view the console, please open %s in a new tab', dashboardURL)
    else:
        logger.warning('Proxy running on %s', proxy_url)

    logger.warning('Press CTRL+C to close the tunnel...')
    if not disable_browser:
        wait_then_open_async(dashboardURL)
    try:
        try:
            subprocess.check_output(["kubectl", "--kubeconfig", browse_path, "proxy", "--address",
                                     listen_address, "--port", listen_port], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            if err.output.find(b'unknown flag: --address'):
                if listen_address != '127.0.0.1':
                    logger.warning('"--address" is only supported in kubectl v1.13 and later.')
                    logger.warning('The "--listen-address" argument will be ignored.')
                subprocess.call(["kubectl", "--kubeconfig", browse_path, "proxy", "--port", listen_port])
    except KeyboardInterrupt:
        # Let command processing finish gracefully after the user presses [Ctrl+C]
        pass
    finally:
        if in_cloud_console():
            requests.post('http://localhost:8888/closeport/8001')


def _trim_nodepoolname(nodepool_name):
    if not nodepool_name:
        return "nodepool1"
    return nodepool_name[:12]


def _add_monitoring_role_assignment(result, cluster_resource_id, cmd):
    service_principal_msi_id = None
    # Check if service principal exists, if it does, assign permissions to service principal
    # Else, provide permissions to MSI
    if (
            hasattr(result, 'service_principal_profile') and
            hasattr(result.service_principal_profile, 'client_id') and
            result.service_principal_profile.client_id != 'msi'
    ):
        logger.info('valid service principal exists, using it')
        service_principal_msi_id = result.service_principal_profile.client_id
        is_service_principal = True
    elif (
            (hasattr(result, 'addon_profiles')) and
            ('omsagent' in result.addon_profiles) and
            (hasattr(result.addon_profiles['omsagent'], 'identity')) and
            (hasattr(result.addon_profiles['omsagent'].identity, 'object_id'))
    ):
        logger.info('omsagent MSI exists, using it')
        service_principal_msi_id = result.addon_profiles['omsagent'].identity.object_id
        is_service_principal = False

    if service_principal_msi_id is not None:
        if not _add_role_assignment(cmd.cli_ctx, 'Monitoring Metrics Publisher',
                                    service_principal_msi_id, is_service_principal, scope=cluster_resource_id):
            logger.warning('Could not create a role assignment for Monitoring addon. '
                           'Are you an Owner on this subscription?')
    else:
        logger.warning('Could not find service principal or user assigned MSI for role'
                       'assignment')


def _add_ingress_appgw_addon_role_assignment(result, cmd):
    service_principal_msi_id = None
    # Check if service principal exists, if it does, assign permissions to service principal
    # Else, provide permissions to MSI
    if (
            hasattr(result, 'service_principal_profile') and
            hasattr(result.service_principal_profile, 'client_id') and
            result.service_principal_profile.client_id != 'msi'
    ):
        service_principal_msi_id = result.service_principal_profile.client_id
        is_service_principal = True
    elif (
            (hasattr(result, 'addon_profiles')) and
            (CONST_INGRESS_APPGW_ADDON_NAME in result.addon_profiles) and
            (hasattr(result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME], 'identity')) and
            (hasattr(result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].identity, 'object_id'))
    ):
        service_principal_msi_id = result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].identity.object_id
        is_service_principal = False

    if service_principal_msi_id is not None:
        config = result.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].config
        from msrestazure.tools import parse_resource_id, resource_id
        if CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID in config:
            appgw_id = config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID]
            parsed_appgw_id = parse_resource_id(appgw_id)
            appgw_group_id = resource_id(subscription=parsed_appgw_id["subscription"],
                                         resource_group=parsed_appgw_id["resource_group"])
            if not _add_role_assignment(cmd.cli_ctx, 'Contributor',
                                        service_principal_msi_id, is_service_principal, scope=appgw_group_id):
                logger.warning('Could not create a role assignment for application gateway: %s '
                               'specified in %s addon. '
                               'Are you an Owner on this subscription?', appgw_id, CONST_INGRESS_APPGW_ADDON_NAME)
        if CONST_INGRESS_APPGW_SUBNET_ID in config:
            subnet_id = config[CONST_INGRESS_APPGW_SUBNET_ID]
            if not _add_role_assignment(cmd.cli_ctx, 'Network Contributor',
                                        service_principal_msi_id, is_service_principal, scope=subnet_id):
                logger.warning('Could not create a role assignment for subnet: %s '
                               'specified in %s addon. '
                               'Are you an Owner on this subscription?', subnet_id, CONST_INGRESS_APPGW_ADDON_NAME)
        if CONST_INGRESS_APPGW_SUBNET_PREFIX in config:
            if result.agent_pool_profiles[0].vnet_subnet_id is not None:
                parsed_subnet_vnet_id = parse_resource_id(result.agent_pool_profiles[0].vnet_subnet_id)
                vnet_id = resource_id(subscription=parsed_subnet_vnet_id["subscription"],
                                      resource_group=parsed_subnet_vnet_id["resource_group"],
                                      namespace="Microsoft.Network",
                                      type="virtualNetworks",
                                      name=parsed_subnet_vnet_id["name"])
                if not _add_role_assignment(cmd.cli_ctx, 'Contributor',
                                            service_principal_msi_id, is_service_principal, scope=vnet_id):
                    logger.warning('Could not create a role assignment for virtual network: %s '
                                   'specified in %s addon. '
                                   'Are you an Owner on this subscription?', vnet_id, CONST_INGRESS_APPGW_ADDON_NAME)


def aks_create(cmd,     # pylint: disable=too-many-locals,too-many-statements,too-many-branches
               client,
               resource_group_name,
               name,
               ssh_key_value,
               dns_name_prefix=None,
               location=None,
               admin_username="azureuser",
               windows_admin_username=None,
               windows_admin_password=None,
               kubernetes_version='',
               node_vm_size="Standard_DS2_v2",
               node_osdisk_type=None,
               node_osdisk_size=0,
               node_osdisk_diskencryptionset_id=None,
               node_count=3,
               nodepool_name="nodepool1",
               nodepool_tags=None,
               nodepool_labels=None,
               service_principal=None, client_secret=None,
               no_ssh_key=False,
               disable_rbac=None,
               enable_rbac=None,
               enable_vmss=None,
               vm_set_type=None,
               skip_subnet_role_assignment=False,
               enable_cluster_autoscaler=False,
               cluster_autoscaler_profile=None,
               network_plugin=None,
               network_policy=None,
               pod_cidr=None,
               service_cidr=None,
               dns_service_ip=None,
               docker_bridge_address=None,
               load_balancer_sku=None,
               load_balancer_managed_outbound_ip_count=None,
               load_balancer_outbound_ips=None,
               load_balancer_outbound_ip_prefixes=None,
               load_balancer_outbound_ports=None,
               load_balancer_idle_timeout=None,
               outbound_type=None,
               enable_addons=None,
               workspace_resource_id=None,
               min_count=None,
               max_count=None,
               vnet_subnet_id=None,
               ppg=None,
               max_pods=0,
               aad_client_app_id=None,
               aad_server_app_id=None,
               aad_server_app_secret=None,
               aad_tenant_id=None,
               tags=None,
               node_zones=None,
               enable_node_public_ip=False,
               generate_ssh_keys=False,  # pylint: disable=unused-argument
               enable_pod_security_policy=False,
               node_resource_group=None,
               uptime_sla=False,
               attach_acr=None,
               enable_private_cluster=False,
               enable_managed_identity=False,
               api_server_authorized_ip_ranges=None,
               aks_custom_headers=None,
               appgw_name=None,
               appgw_subnet_prefix=None,
               appgw_id=None,
               appgw_subnet_id=None,
               appgw_watch_namespace=None,
               enable_aad=False,
               enable_azure_rbac=False,
               aad_admin_group_object_ids=None,
               disable_sgxquotehelper=False,
               assign_identity=None,
               osm_mesh_name=None,
               no_wait=False):
    if not no_ssh_key:
        try:
            if not ssh_key_value or not is_valid_ssh_rsa_public_key(ssh_key_value):
                raise ValueError()
        except (TypeError, ValueError):
            shortened_key = truncate_text(ssh_key_value)
            raise CLIError('Provided ssh key ({}) is invalid or non-existent'.format(shortened_key))

    subscription_id = get_subscription_id(cmd.cli_ctx)
    if not dns_name_prefix:
        dns_name_prefix = _get_default_dns_prefix(name, resource_group_name, subscription_id)

    rg_location = _get_rg_location(cmd.cli_ctx, resource_group_name)
    if location is None:
        location = rg_location

    # Flag to be removed, kept for back-compatibility only. Remove the below section
    # when we deprecate the enable-vmss flag
    if enable_vmss:
        if vm_set_type and vm_set_type.lower() != "VirtualMachineScaleSets".lower():
            raise CLIError('enable-vmss and provided vm_set_type ({}) are conflicting with each other'.
                           format(vm_set_type))
        vm_set_type = "VirtualMachineScaleSets"

    vm_set_type = _set_vm_set_type(vm_set_type, kubernetes_version)
    load_balancer_sku = set_load_balancer_sku(load_balancer_sku, kubernetes_version)

    if api_server_authorized_ip_ranges and load_balancer_sku == "basic":
        raise CLIError('--api-server-authorized-ip-ranges can only be used with standard load balancer')

    agent_pool_profile = ManagedClusterAgentPoolProfile(
        name=_trim_nodepoolname(nodepool_name),  # Must be 12 chars or less before ACS RP adds to it
        tags=nodepool_tags,
        node_labels=nodepool_labels,
        count=int(node_count),
        vm_size=node_vm_size,
        os_type="Linux",
        mode="System",
        vnet_subnet_id=vnet_subnet_id,
        proximity_placement_group_id=ppg,
        availability_zones=node_zones,
        enable_node_public_ip=enable_node_public_ip,
        max_pods=int(max_pods) if max_pods else None,
        type=vm_set_type
    )

    if node_osdisk_size:
        agent_pool_profile.os_disk_size_gb = int(node_osdisk_size)

    if node_osdisk_type:
        agent_pool_profile.os_disk_type = node_osdisk_type

    _check_cluster_autoscaler_flag(enable_cluster_autoscaler, min_count, max_count, node_count, agent_pool_profile)

    linux_profile = None
    # LinuxProfile is just used for SSH access to VMs, so omit it if --no-ssh-key was specified.
    if not no_ssh_key:
        ssh_config = ContainerServiceSshConfiguration(
            public_keys=[ContainerServiceSshPublicKey(key_data=ssh_key_value)])
        linux_profile = ContainerServiceLinuxProfile(admin_username=admin_username, ssh=ssh_config)

    windows_profile = None

    if windows_admin_username:
        if windows_admin_password is None:
            try:
                windows_admin_password = prompt_pass(msg='windows-admin-password: ', confirm=True)
            except NoTTYException:
                raise CLIError('Please specify both username and password in non-interactive mode.')

        windows_profile = ManagedClusterWindowsProfile(
            admin_username=windows_admin_username,
            admin_password=windows_admin_password)

    principal_obj = _ensure_aks_service_principal(cmd.cli_ctx,
                                                  service_principal=service_principal, client_secret=client_secret,
                                                  subscription_id=subscription_id, dns_name_prefix=dns_name_prefix,
                                                  location=location, name=name)
    service_principal_profile = ManagedClusterServicePrincipalProfile(
        client_id=principal_obj.get("service_principal"),
        secret=principal_obj.get("client_secret"))

    if attach_acr:
        if enable_managed_identity:
            if no_wait:
                raise CLIError('When --attach-acr and --enable-managed-identity are both specified, '
                               '--no-wait is not allowed, please wait until the whole operation succeeds.')
        else:
            _ensure_aks_acr(cmd.cli_ctx,
                            client_id=service_principal_profile.client_id,
                            acr_name_or_id=attach_acr,
                            subscription_id=subscription_id)

    if (vnet_subnet_id and not skip_subnet_role_assignment and
            not subnet_role_assignment_exists(cmd.cli_ctx, vnet_subnet_id)):
        scope = vnet_subnet_id
        identity_client_id = service_principal_profile.client_id
        if enable_managed_identity and assign_identity:
            identity_client_id = _get_user_assigned_identity_client_id(cmd.cli_ctx, assign_identity)
        if not _add_role_assignment(
                cmd.cli_ctx,
                'Network Contributor',
                identity_client_id,
                scope=scope):
            logger.warning('Could not create a role assignment for subnet. '
                           'Are you an Owner on this subscription?')

    load_balancer_profile = create_load_balancer_profile(
        load_balancer_managed_outbound_ip_count,
        load_balancer_outbound_ips,
        load_balancer_outbound_ip_prefixes,
        load_balancer_outbound_ports,
        load_balancer_idle_timeout)

    outbound_type = _set_outbound_type(outbound_type, network_plugin, load_balancer_sku, load_balancer_profile)

    network_profile = None
    if any([network_plugin,
            pod_cidr,
            service_cidr,
            dns_service_ip,
            docker_bridge_address,
            network_policy]):
        if not network_plugin:
            raise CLIError('Please explicitly specify the network plugin type')
        if pod_cidr and network_plugin == "azure":
            raise CLIError('Please use kubenet as the network plugin type when pod_cidr is specified')
        network_profile = ContainerServiceNetworkProfile(
            network_plugin=network_plugin,
            pod_cidr=pod_cidr,
            service_cidr=service_cidr,
            dns_service_ip=dns_service_ip,
            docker_bridge_cidr=docker_bridge_address,
            network_policy=network_policy,
            load_balancer_sku=load_balancer_sku.lower(),
            load_balancer_profile=load_balancer_profile,
            outbound_type=outbound_type
        )
    else:
        if load_balancer_sku.lower() == "standard" or load_balancer_profile:
            network_profile = ContainerServiceNetworkProfile(
                network_plugin="kubenet",
                load_balancer_sku=load_balancer_sku.lower(),
                load_balancer_profile=load_balancer_profile,
                outbound_type=outbound_type,
            )
        if load_balancer_sku.lower() == "basic":
            network_profile = ContainerServiceNetworkProfile(
                load_balancer_sku=load_balancer_sku.lower(),
            )

    addon_profiles = _handle_addons_args(
        cmd,
        enable_addons,
        subscription_id,
        resource_group_name,
        {},
        workspace_resource_id,
        appgw_name,
        appgw_subnet_prefix,
        appgw_id,
        appgw_subnet_id,
        appgw_watch_namespace,
        disable_sgxquotehelper,
        osm_mesh_name
    )
    monitoring = False
    if 'omsagent' in addon_profiles:
        monitoring = True
        _ensure_container_insights_for_monitoring(cmd, addon_profiles['omsagent'])

    # addon is in the list and is enabled
    ingress_appgw_addon_enabled = CONST_INGRESS_APPGW_ADDON_NAME in addon_profiles and \
        addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].enabled

    aad_profile = None
    if enable_aad:
        if any([aad_client_app_id, aad_server_app_id, aad_server_app_secret]):
            raise CLIError('"--enable-aad" cannot be used together with '
                           '"--aad-client-app-id/--aad-server-app-id/--aad-server-app-secret"')

        aad_profile = ManagedClusterAADProfile(
            managed=True,
            enable_azure_rbac=enable_azure_rbac,
            admin_group_object_ids=_parse_comma_separated_list(aad_admin_group_object_ids),
            tenant_id=aad_tenant_id
        )
    else:
        if aad_admin_group_object_ids is not None:
            raise CLIError('"--admin-aad-object-id" can only be used together with "--enable-aad"')

        if enable_azure_rbac is True:
            raise CLIError('"--enable-azure-rbac" can only be used together with "--enable-aad"')

        if any([aad_client_app_id, aad_server_app_id, aad_server_app_secret]):
            aad_profile = ManagedClusterAADProfile(
                client_app_id=aad_client_app_id,
                server_app_id=aad_server_app_id,
                server_app_secret=aad_server_app_secret,
                tenant_id=aad_tenant_id
            )

    # Check that both --disable-rbac and --enable-rbac weren't provided
    if all([disable_rbac, enable_rbac]):
        raise CLIError('specify either "--disable-rbac" or "--enable-rbac", not both.')

    api_server_access_profile = None
    if api_server_authorized_ip_ranges:
        api_server_access_profile = _populate_api_server_access_profile(api_server_authorized_ip_ranges)

    identity = None
    if not enable_managed_identity and assign_identity:
        raise CLIError('--assign-identity can only be specified when --enable-managed-identity is specified')
    if enable_managed_identity and not assign_identity:
        identity = ManagedClusterIdentity(
            type="SystemAssigned"
        )
    elif enable_managed_identity and assign_identity:
        user_assigned_identity = {
            assign_identity: ManagedClusterIdentityUserAssignedIdentitiesValue()
        }
        identity = ManagedClusterIdentity(
            type="UserAssigned",
            user_assigned_identities=user_assigned_identity
        )

    enable_rbac = True
    if disable_rbac:
        enable_rbac = False

    mc = ManagedCluster(
        location=location, tags=tags,
        dns_prefix=dns_name_prefix,
        kubernetes_version=kubernetes_version,
        enable_rbac=enable_rbac,
        agent_pool_profiles=[agent_pool_profile],
        linux_profile=linux_profile,
        windows_profile=windows_profile,
        service_principal_profile=service_principal_profile,
        network_profile=network_profile,
        addon_profiles=addon_profiles,
        aad_profile=aad_profile,
        auto_scaler_profile=cluster_autoscaler_profile,
        enable_pod_security_policy=bool(enable_pod_security_policy),
        identity=identity,
        disk_encryption_set_id=node_osdisk_diskencryptionset_id,
        api_server_access_profile=api_server_access_profile)

    if node_resource_group:
        mc.node_resource_group = node_resource_group

    if enable_private_cluster:
        if load_balancer_sku.lower() != "standard":
            raise CLIError("Please use standard load balancer for private cluster")
        mc.api_server_access_profile = ManagedClusterAPIServerAccessProfile(
            enable_private_cluster=True
        )

    if uptime_sla:
        mc.sku = ManagedClusterSKU(
            name="Basic",
            tier="Paid"
        )

    headers = get_aks_custom_headers(aks_custom_headers)

    # Due to SPN replication latency, we do a few retries here
    max_retry = 30
    retry_exception = Exception(None)
    for _ in range(0, max_retry):
        try:
            logger.info('AKS cluster is creating, please wait...')

            # some addons require post cluster creation role assigment
            need_post_creation_role_assignment = monitoring or ingress_appgw_addon_enabled
            if need_post_creation_role_assignment:
                # adding a wait here since we rely on the result for role assignment
                created_cluster = LongRunningOperation(cmd.cli_ctx)(client.create_or_update(
                    resource_group_name=resource_group_name,
                    resource_name=name,
                    parameters=mc,
                    custom_headers=headers))
                cloud_name = cmd.cli_ctx.cloud.name
                # add cluster spn/msi Monitoring Metrics Publisher role assignment to publish metrics to MDM
                # mdm metrics is supported only in azure public cloud, so add the role assignment only in this cloud
                if monitoring and cloud_name.lower() == 'azurecloud':
                    from msrestazure.tools import resource_id
                    cluster_resource_id = resource_id(
                        subscription=subscription_id,
                        resource_group=resource_group_name,
                        namespace='Microsoft.ContainerService', type='managedClusters',
                        name=name
                    )
                    _add_monitoring_role_assignment(created_cluster, cluster_resource_id, cmd)
                if ingress_appgw_addon_enabled:
                    _add_ingress_appgw_addon_role_assignment(created_cluster, cmd)

            else:
                created_cluster = sdk_no_wait(no_wait, client.create_or_update,
                                              resource_group_name=resource_group_name,
                                              resource_name=name,
                                              parameters=mc,
                                              custom_headers=headers).result()

            if enable_managed_identity and attach_acr:
                # Attach ACR to cluster enabled managed identity
                if created_cluster.identity_profile is None or \
                   created_cluster.identity_profile["kubeletidentity"] is None:
                    logger.warning('Your cluster is successfully created, but we failed to attach '
                                   'acr to it, you can manually grant permission to the identity '
                                   'named <ClUSTER_NAME>-agentpool in MC_ resource group to give '
                                   'it permission to pull from ACR.')
                else:
                    kubelet_identity_client_id = created_cluster.identity_profile["kubeletidentity"].client_id
                    _ensure_aks_acr(cmd.cli_ctx,
                                    client_id=kubelet_identity_client_id,
                                    acr_name_or_id=attach_acr,
                                    subscription_id=subscription_id)

            return created_cluster
        except CloudError as ex:
            retry_exception = ex
            if 'not found in Active Directory tenant' in ex.message:
                time.sleep(3)
            else:
                raise ex
    raise retry_exception


def aks_update(cmd,     # pylint: disable=too-many-statements,too-many-branches,too-many-locals
               client,
               resource_group_name,
               name,
               enable_cluster_autoscaler=False,
               disable_cluster_autoscaler=False,
               update_cluster_autoscaler=False,
               cluster_autoscaler_profile=None,
               min_count=None, max_count=None, no_wait=False,
               load_balancer_managed_outbound_ip_count=None,
               load_balancer_outbound_ips=None,
               load_balancer_outbound_ip_prefixes=None,
               load_balancer_outbound_ports=None,
               load_balancer_idle_timeout=None,
               api_server_authorized_ip_ranges=None,
               enable_pod_security_policy=False,
               disable_pod_security_policy=False,
               attach_acr=None,
               detach_acr=None,
               uptime_sla=False,
               enable_aad=False,
               aad_tenant_id=None,
               aad_admin_group_object_ids=None,
               aks_custom_headers=None):
    update_autoscaler = enable_cluster_autoscaler or disable_cluster_autoscaler or update_cluster_autoscaler
    update_acr = attach_acr is not None or detach_acr is not None
    update_pod_security = enable_pod_security_policy or disable_pod_security_policy
    update_lb_profile = is_load_balancer_profile_provided(load_balancer_managed_outbound_ip_count,
                                                          load_balancer_outbound_ips,
                                                          load_balancer_outbound_ip_prefixes,
                                                          load_balancer_outbound_ports,
                                                          load_balancer_idle_timeout)
    update_aad_profile = not (aad_tenant_id is None and aad_admin_group_object_ids is None)
    # pylint: disable=too-many-boolean-expressions
    if not update_autoscaler and \
       cluster_autoscaler_profile is None and \
       not update_acr and \
       not update_lb_profile \
       and api_server_authorized_ip_ranges is None and \
       not update_pod_security and \
       not update_lb_profile and \
       not uptime_sla and \
       not enable_aad and \
       not update_aad_profile:
        raise CLIError('Please specify "--enable-cluster-autoscaler" or '
                       '"--disable-cluster-autoscaler" or '
                       '"--update-cluster-autoscaler" or '
                       '"--cluster-autoscaler-profile" or '
                       '"--enable-pod-security-policy" or '
                       '"--disable-pod-security-policy" or '
                       '"--api-server-authorized-ip-ranges" or '
                       '"--attach-acr" or '
                       '"--detach-acr" or '
                       '"--uptime-sla" or '
                       '"--load-balancer-managed-outbound-ip-count" or '
                       '"--load-balancer-outbound-ips" or '
                       '"--load-balancer-outbound-ip-prefixes" or '
                       '"--enable-aad" or '
                       '"--aad-tenant-id" or '
                       '"--aad-admin-group-object-ids"')

    instance = client.get(resource_group_name, name)

    if update_autoscaler and len(instance.agent_pool_profiles) > 1:
        raise CLIError('There is more than one node pool in the cluster. Please use "az aks nodepool" command '
                       'to update per node pool auto scaler settings')

    if min_count is None or max_count is None:
        if enable_cluster_autoscaler or update_cluster_autoscaler:
            raise CLIError('Please specify both min-count and max-count when --enable-cluster-autoscaler or '
                           '--update-cluster-autoscaler set.')

    if min_count is not None and max_count is not None:
        if int(min_count) > int(max_count):
            raise CLIError('value of min-count should be less than or equal to value of max-count.')

    if enable_cluster_autoscaler:
        if instance.agent_pool_profiles[0].enable_auto_scaling:
            logger.warning('Cluster autoscaler is already enabled for this managed cluster.\n'
                           'Please run "az aks update --update-cluster-autoscaler" '
                           'if you want to update min-count or max-count.')
            return None
        instance.agent_pool_profiles[0].min_count = int(min_count)
        instance.agent_pool_profiles[0].max_count = int(max_count)
        instance.agent_pool_profiles[0].enable_auto_scaling = True

    if update_cluster_autoscaler:
        if not instance.agent_pool_profiles[0].enable_auto_scaling:
            raise CLIError('Cluster autoscaler is not enabled for this managed cluster.\n'
                           'Run "az aks update --enable-cluster-autoscaler" '
                           'to enable cluster with min-count and max-count.')
        instance.agent_pool_profiles[0].min_count = int(min_count)
        instance.agent_pool_profiles[0].max_count = int(max_count)

    if disable_cluster_autoscaler:
        if not instance.agent_pool_profiles[0].enable_auto_scaling:
            logger.warning('Cluster autoscaler is already disabled for this managed cluster.')
            return None
        instance.agent_pool_profiles[0].enable_auto_scaling = False
        instance.agent_pool_profiles[0].min_count = None
        instance.agent_pool_profiles[0].max_count = None

    # if intention is to clear profile
    if cluster_autoscaler_profile == {}:
        instance.auto_scaler_profile = {}
    # else profile is provided, update instance profile if it exists
    elif cluster_autoscaler_profile:
        instance.auto_scaler_profile = _update_dict(instance.auto_scaler_profile.__dict__,
                                                    dict((key.replace("-", "_"), value)
                                                         for (key, value) in cluster_autoscaler_profile.items())) \
            if instance.auto_scaler_profile else cluster_autoscaler_profile

    if enable_pod_security_policy and disable_pod_security_policy:
        raise CLIError('Cannot specify --enable-pod-security-policy and --disable-pod-security-policy '
                       'at the same time.')

    if enable_pod_security_policy:
        instance.enable_pod_security_policy = True

    if disable_pod_security_policy:
        instance.enable_pod_security_policy = False

    if update_lb_profile:
        instance.network_profile.load_balancer_profile = update_load_balancer_profile(
            load_balancer_managed_outbound_ip_count,
            load_balancer_outbound_ips,
            load_balancer_outbound_ip_prefixes,
            load_balancer_outbound_ports,
            load_balancer_idle_timeout,
            instance.network_profile.load_balancer_profile)

    if attach_acr and detach_acr:
        raise CLIError('Cannot specify "--attach-acr" and "--detach-acr" at the same time.')

    if uptime_sla:
        instance.sku = ManagedClusterSKU(
            name="Basic",
            tier="Paid"
        )

    subscription_id = get_subscription_id(cmd.cli_ctx)
    client_id = ""
    if instance.identity is not None and instance.identity.type == "SystemAssigned":
        if instance.identity_profile is None or instance.identity_profile["kubeletidentity"] is None:
            raise CLIError('Unexpected error getting kubelet\'s identity for the cluster. '
                           'Please do not set --attach-acr or --detach-acr. '
                           'You can manually grant or revoke permission to the identity named '
                           '<ClUSTER_NAME>-agentpool in MC_ resource group to access ACR.')
        client_id = instance.identity_profile["kubeletidentity"].client_id
    else:
        client_id = instance.service_principal_profile.client_id
    if not client_id:
        raise CLIError('Cannot get the AKS cluster\'s service principal.')

    if attach_acr:
        _ensure_aks_acr(cmd.cli_ctx,
                        client_id=client_id,
                        acr_name_or_id=attach_acr,
                        subscription_id=subscription_id)

    if detach_acr:
        _ensure_aks_acr(cmd.cli_ctx,
                        client_id=client_id,
                        acr_name_or_id=detach_acr,
                        subscription_id=subscription_id,
                        detach=True)

    # empty string is valid as it disables ip whitelisting
    if api_server_authorized_ip_ranges is not None:
        instance.api_server_access_profile = \
            _populate_api_server_access_profile(api_server_authorized_ip_ranges, instance)

    if enable_aad:
        if instance.aad_profile is not None and instance.aad_profile.managed:
            raise CLIError('Cannot specify "--enable-aad" if managed AAD is already enabled')
        instance.aad_profile = ManagedClusterAADProfile(
            managed=True
        )
    if update_aad_profile:
        if instance.aad_profile is None or not instance.aad_profile.managed:
            raise CLIError('Cannot specify "--aad-tenant-id/--aad-admin-group-object-ids"'
                           ' if managed AAD is not enabled')
        if aad_tenant_id is not None:
            instance.aad_profile.tenant_id = aad_tenant_id
        if aad_admin_group_object_ids is not None:
            instance.aad_profile.admin_group_object_ids = _parse_comma_separated_list(aad_admin_group_object_ids)

    headers = get_aks_custom_headers(aks_custom_headers)
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, name, instance, custom_headers=headers)


def aks_show(cmd, client, resource_group_name, name):   # pylint: disable=unused-argument
    mc = client.get(resource_group_name, name)
    return _remove_nulls([mc])[0]


def _remove_nulls(managed_clusters):
    """
    Remove some often-empty fields from a list of ManagedClusters, so the JSON representation
    doesn't contain distracting null fields.

    This works around a quirk of the SDK for python behavior. These fields are not sent
    by the server, but get recreated by the CLI's own "to_dict" serialization.
    """
    attrs = ['tags']
    ap_attrs = ['os_disk_size_gb', 'vnet_subnet_id']
    sp_attrs = ['secret']
    for managed_cluster in managed_clusters:
        for attr in attrs:
            if getattr(managed_cluster, attr, None) is None:
                delattr(managed_cluster, attr)
        if managed_cluster.agent_pool_profiles is not None:
            for ap_profile in managed_cluster.agent_pool_profiles:
                for attr in ap_attrs:
                    if getattr(ap_profile, attr, None) is None:
                        delattr(ap_profile, attr)
        for attr in sp_attrs:
            if getattr(managed_cluster.service_principal_profile, attr, None) is None:
                delattr(managed_cluster.service_principal_profile, attr)
    return managed_clusters


def aks_get_credentials(cmd,    # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        name,
                        admin=False,
                        user='clusterUser',
                        path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                        overwrite_existing=False,
                        context_name=None):
    credentialResults = None
    if admin:
        credentialResults = client.list_cluster_admin_credentials(resource_group_name, name)
    else:
        if user.lower() == 'clusteruser':
            credentialResults = client.list_cluster_user_credentials(resource_group_name, name)
        elif user.lower() == 'clustermonitoringuser':
            credentialResults = client.list_cluster_monitoring_user_credentials(resource_group_name, name)
        else:
            raise CLIError("The user is invalid.")
    if not credentialResults:
        raise CLIError("No Kubernetes credentials found.")

    try:
        kubeconfig = credentialResults.kubeconfigs[0].value.decode(encoding='UTF-8')
        _print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name)
    except (IndexError, ValueError):
        raise CLIError("Fail to find kubeconfig file.")


# pylint: disable=line-too-long
def aks_kollect(cmd,    # pylint: disable=too-many-statements,too-many-locals
                client,
                resource_group_name,
                name,
                storage_account=None,
                sas_token=None,
                container_logs=None,
                kube_objects=None,
                node_logs=None):
    colorama.init()

    mc = client.get(resource_group_name, name)

    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')

    storage_account_id = None
    if storage_account is None:
        print("No storage account specified. Try getting storage account from diagnostic settings")
        storage_account_id = get_storage_account_from_diag_settings(cmd.cli_ctx, resource_group_name, name)
        if storage_account_id is None:
            raise CLIError("A storage account must be specified, since there isn't one in the diagnostic settings.")

    from msrestazure.tools import is_valid_resource_id, parse_resource_id, resource_id
    if storage_account_id is None:
        if not is_valid_resource_id(storage_account):
            storage_account_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=resource_group_name,
                namespace='Microsoft.Storage', type='storageAccounts',
                name=storage_account
            )
        else:
            storage_account_id = storage_account

    if is_valid_resource_id(storage_account_id):
        try:
            parsed_storage_account = parse_resource_id(storage_account_id)
        except CloudError as ex:
            raise CLIError(ex.message)
    else:
        raise CLIError("Invalid storage account id %s" % storage_account_id)

    storage_account_name = parsed_storage_account['name']

    readonly_sas_token = None
    if sas_token is None:
        storage_client = cf_storage(cmd.cli_ctx, parsed_storage_account['subscription'])
        storage_account_keys = storage_client.storage_accounts.list_keys(parsed_storage_account['resource_group'],
                                                                         storage_account_name)
        kwargs = {
            'account_name': storage_account_name,
            'account_key': storage_account_keys.keys[0].value
        }
        cloud_storage_client = cloud_storage_account_service_factory(cmd.cli_ctx, kwargs)

        sas_token = cloud_storage_client.generate_shared_access_signature(
            'b',
            'sco',
            'rwdlacup',
            datetime.datetime.utcnow() + datetime.timedelta(days=1))

        readonly_sas_token = cloud_storage_client.generate_shared_access_signature(
            'b',
            'sco',
            'rl',
            datetime.datetime.utcnow() + datetime.timedelta(days=1))

        readonly_sas_token = readonly_sas_token.strip('?')

    from knack.prompting import prompt_y_n

    print()
    print('This will deploy a daemon set to your cluster to collect logs and diagnostic information and '
          f'save them to the storage account '
          f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}{storage_account_name}{colorama.Style.RESET_ALL} as '
          f'outlined in {format_hyperlink("http://aka.ms/AKSPeriscope")}.')
    print()
    print('If you share access to that storage account to Azure support, you consent to the terms outlined'
          f' in {format_hyperlink("http://aka.ms/DiagConsent")}.')
    print()
    if not prompt_y_n('Do you confirm?', default="n"):
        return

    print()
    print("Getting credentials for cluster %s " % name)
    _, temp_kubeconfig_path = tempfile.mkstemp()
    aks_get_credentials(cmd, client, resource_group_name, name, admin=True, path=temp_kubeconfig_path)

    print()
    print("Starts collecting diag info for cluster %s " % name)

    sas_token = sas_token.strip('?')
    deployment_yaml = urlopen(
        "https://raw.githubusercontent.com/Azure/aks-periscope/latest/deployment/aks-periscope.yaml").read().decode()
    deployment_yaml = deployment_yaml.replace("# <accountName, base64 encoded>",
                                              (base64.b64encode(bytes(storage_account_name, 'ascii'))).decode('ascii'))
    deployment_yaml = deployment_yaml.replace("# <saskey, base64 encoded>",
                                              (base64.b64encode(bytes("?" + sas_token, 'ascii'))).decode('ascii'))

    yaml_lines = deployment_yaml.splitlines()
    for index, line in enumerate(yaml_lines):
        if "DIAGNOSTIC_CONTAINERLOGS_LIST" in line and container_logs is not None:
            yaml_lines[index] = line + ' ' + container_logs
        if "DIAGNOSTIC_KUBEOBJECTS_LIST" in line and kube_objects is not None:
            yaml_lines[index] = line + ' ' + kube_objects
        if "DIAGNOSTIC_NODELOGS_LIST" in line and node_logs is not None:
            yaml_lines[index] = line + ' ' + node_logs
    deployment_yaml = '\n'.join(yaml_lines)

    fd, temp_yaml_path = tempfile.mkstemp()
    temp_yaml_file = os.fdopen(fd, 'w+t')
    try:
        temp_yaml_file.write(deployment_yaml)
        temp_yaml_file.flush()
        temp_yaml_file.close()
        try:
            print()
            print("Cleaning up aks-periscope resources if existing")

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "serviceaccount,configmap,daemonset,secret",
                             "--all", "-n", "aks-periscope", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "ClusterRoleBinding",
                             "aks-periscope-role-binding", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "ClusterRoleBinding",
                             "aks-periscope-role-binding-view", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "ClusterRole",
                             "aks-periscope-role", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "--all",
                             "apd", "-n", "aks-periscope", "--ignore-not-found"],
                            stderr=subprocess.DEVNULL)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "CustomResourceDefinition",
                             "diagnostics.aks-periscope.azure.github.com", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            print()
            print("Deploying aks-periscope")
            subprocess.check_output(["kubectl", "--kubeconfig", temp_kubeconfig_path, "apply", "-f",
                                     temp_yaml_path, "-n", "aks-periscope"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            raise CLIError(err.output)
    finally:
        os.remove(temp_yaml_path)

    print()
    fqdn = mc.fqdn if mc.fqdn is not None else mc.private_fqdn
    normalized_fqdn = fqdn.replace('.', '-')
    token_in_storage_account_url = readonly_sas_token if readonly_sas_token is not None else sas_token
    log_storage_account_url = f"https://{storage_account_name}.blob.core.windows.net/" \
                              f"{_trim_fqdn_name_containing_hcp(normalized_fqdn)}?{token_in_storage_account_url}"

    print(f'{colorama.Fore.GREEN}Your logs are being uploaded to storage account {format_bright(storage_account_name)}')

    print()
    print(f'You can download Azure Stroage Explorer here '
          f'{format_hyperlink("https://azure.microsoft.com/en-us/features/storage-explorer/")}'
          f' to check the logs by adding the storage account using the following URL:')
    print(f'{format_hyperlink(log_storage_account_url)}')

    print()
    if not prompt_y_n('Do you want to see analysis results now?', default="n"):
        print(f"You can run 'az aks kanalyze -g {resource_group_name} -n {name}' "
              f"anytime to check the analysis results.")
    else:
        display_diagnostics_report(temp_kubeconfig_path)


def aks_kanalyze(cmd, client, resource_group_name, name):
    colorama.init()

    client.get(resource_group_name, name)

    _, temp_kubeconfig_path = tempfile.mkstemp()
    aks_get_credentials(cmd, client, resource_group_name, name, admin=True, path=temp_kubeconfig_path)

    display_diagnostics_report(temp_kubeconfig_path)


def aks_scale(cmd,  # pylint: disable=unused-argument
              client,
              resource_group_name,
              name,
              node_count,
              nodepool_name="",
              no_wait=False):
    instance = client.get(resource_group_name, name)

    if len(instance.agent_pool_profiles) > 1 and nodepool_name == "":
        raise CLIError('There are more than one node pool in the cluster. '
                       'Please specify nodepool name or use az aks nodepool command to scale node pool')

    for agent_profile in instance.agent_pool_profiles:
        if agent_profile.name == nodepool_name or (nodepool_name == "" and len(instance.agent_pool_profiles) == 1):
            if agent_profile.enable_auto_scaling:
                raise CLIError("Cannot scale cluster autoscaler enabled node pool.")

            agent_profile.count = int(node_count)  # pylint: disable=no-member
            # null out the SP and AAD profile because otherwise validation complains
            instance.service_principal_profile = None
            instance.aad_profile = None
            return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, name, instance)
    raise CLIError('The nodepool "{}" was not found.'.format(nodepool_name))


def aks_upgrade(cmd,    # pylint: disable=unused-argument, too-many-return-statements
                client,
                resource_group_name,
                name,
                kubernetes_version='',
                control_plane_only=False,
                no_wait=False,
                node_image_only=False,
                yes=False):
    from knack.prompting import prompt_y_n
    msg = 'Kubernetes may be unavailable during cluster upgrades.\n Are you sure you want to perform this operation?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None

    instance = client.get(resource_group_name, name)

    if kubernetes_version != '' and node_image_only:
        raise CLIError('Conflicting flags. Upgrading the Kubernetes version will also upgrade node image version. If you only want to upgrade the node version please use the "--node-image-only" option only.')

    vmas_cluster = False
    for agent_profile in instance.agent_pool_profiles:
        if agent_profile.type.lower() == "availabilityset":
            vmas_cluster = True
            break

    if node_image_only:
        msg = "This node image upgrade operation will run across every node pool in the cluster and might take a while, do you wish to continue?"
        if not yes and not prompt_y_n(msg, default="n"):
            return None
        agent_pool_client = cf_agent_pools(cmd.cli_ctx)
        for agent_pool_profile in instance.agent_pool_profiles:
            if vmas_cluster:
                raise CLIError('This cluster is not using VirtualMachineScaleSets. Node image upgrade only operation can only be applied on VirtualMachineScaleSets cluster.')
            _upgrade_single_agent_pool_node_image(agent_pool_client, resource_group_name, name, agent_pool_profile, no_wait)
        return None

    if instance.kubernetes_version == kubernetes_version:
        if instance.provisioning_state == "Succeeded":
            logger.warning("The cluster is already on version %s and is not in a failed state. No operations "
                           "will occur when upgrading to the same version if the cluster is not in a failed state.",
                           instance.kubernetes_version)
        elif instance.provisioning_state == "Failed":
            logger.warning("Cluster currently in failed state. Proceeding with upgrade to existing version %s to "
                           "attempt resolution of failed cluster state.", instance.kubernetes_version)

    upgrade_all = False
    instance.kubernetes_version = kubernetes_version

    # for legacy clusters, we always upgrade node pools with CCP.
    if instance.max_agent_pools < 8 or vmas_cluster:
        if control_plane_only:
            msg = ("Legacy clusters do not support control plane only upgrade. All node pools will be "
                   "upgraded to {} as well. Continue?").format(instance.kubernetes_version)
            if not yes and not prompt_y_n(msg, default="n"):
                return None
        upgrade_all = True
    else:
        if not control_plane_only:
            msg = ("Since control-plane-only argument is not specified, this will upgrade the control plane "
                   "AND all nodepools to version {}. Continue?").format(instance.kubernetes_version)
            if not yes and not prompt_y_n(msg, default="n"):
                return None
            upgrade_all = True
        else:
            msg = ("Since control-plane-only argument is specified, this will upgrade only the control plane to {}. "
                   "Node pool will not change. Continue?").format(instance.kubernetes_version)
            if not yes and not prompt_y_n(msg, default="n"):
                return None

    if upgrade_all:
        for agent_profile in instance.agent_pool_profiles:
            agent_profile.orchestrator_version = kubernetes_version

    # null out the SP and AAD profile because otherwise validation complains
    instance.service_principal_profile = None
    instance.aad_profile = None

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, name, instance)


def _upgrade_single_agent_pool_node_image(client, resource_group_name, cluster_name, agent_pool_profile, no_wait):
    instance = client.get(resource_group_name, cluster_name, agent_pool_profile.name)
    instance.node_image_version = 'latest'
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, agent_pool_profile.name, instance)


def _handle_addons_args(cmd,  # pylint: disable=too-many-statements
                        addons_str,
                        subscription_id,
                        resource_group_name,
                        addon_profiles=None,
                        workspace_resource_id=None,
                        appgw_name=None,
                        appgw_subnet_prefix=None,
                        appgw_id=None,
                        appgw_subnet_id=None,
                        appgw_watch_namespace=None,
                        disable_sgxquotehelper=False,
                        osm_mesh_name=None):
    if not addon_profiles:
        addon_profiles = {}
    addons = addons_str.split(',') if addons_str else []
    if 'http_application_routing' in addons:
        addon_profiles['httpApplicationRouting'] = ManagedClusterAddonProfile(enabled=True)
        addons.remove('http_application_routing')
    if 'kube-dashboard' in addons:
        addon_profiles[CONST_KUBE_DASHBOARD_ADDON_NAME] = ManagedClusterAddonProfile(enabled=True)
        addons.remove('kube-dashboard')
    # TODO: can we help the user find a workspace resource ID?
    if 'monitoring' in addons:
        if not workspace_resource_id:
            # use default workspace if exists else create default workspace
            workspace_resource_id = _ensure_default_log_analytics_workspace_for_monitoring(
                cmd, subscription_id, resource_group_name)

        workspace_resource_id = workspace_resource_id.strip()
        if not workspace_resource_id.startswith('/'):
            workspace_resource_id = '/' + workspace_resource_id
        if workspace_resource_id.endswith('/'):
            workspace_resource_id = workspace_resource_id.rstrip('/')
        addon_profiles['omsagent'] = ManagedClusterAddonProfile(
            enabled=True, config={'logAnalyticsWorkspaceResourceID': workspace_resource_id})
        addons.remove('monitoring')
    # error out if '--enable-addons=monitoring' isn't set but workspace_resource_id is
    elif workspace_resource_id:
        raise CLIError('"--workspace-resource-id" requires "--enable-addons monitoring".')
    if 'azure-policy' in addons:
        addon_profiles['azurepolicy'] = ManagedClusterAddonProfile(enabled=True)
        addons.remove('azure-policy')
    if 'ingress-appgw' in addons:
        addon_profile = ManagedClusterAddonProfile(enabled=True, config={})
        if appgw_name is not None:
            addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME] = appgw_name
        if appgw_subnet_prefix is not None:
            addon_profile.config[CONST_INGRESS_APPGW_SUBNET_PREFIX] = appgw_subnet_prefix
        if appgw_id is not None:
            addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID] = appgw_id
        if appgw_subnet_id is not None:
            addon_profile.config[CONST_INGRESS_APPGW_SUBNET_ID] = appgw_subnet_id
        if appgw_watch_namespace is not None:
            addon_profile.config[CONST_INGRESS_APPGW_WATCH_NAMESPACE] = appgw_watch_namespace
        addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME] = addon_profile
        addons.remove('ingress-appgw')
    if 'open-service-mesh' in addons:
        addon_profile = ManagedClusterAddonProfile(enabled=True, config={})
        if osm_mesh_name is not None:
            addon_profile.config[CONST_OPEN_SERVICE_MESH_NAME_KEY] = osm_mesh_name
        addon_profiles[CONST_OPEN_SERVICE_MESH_ADDON_NAME] = addon_profile
        addons.remove('open-service-mesh')
    if 'confcom' in addons:
        addon_profile = ManagedClusterAddonProfile(enabled=True, config={CONST_ACC_SGX_QUOTE_HELPER_ENABLED: "true"})
        if disable_sgxquotehelper:
            addon_profile.config[CONST_ACC_SGX_QUOTE_HELPER_ENABLED] = "false"
        addon_profiles[CONST_CONFCOM_ADDON_NAME] = addon_profile
        addons.remove('confcom')

    # error out if any (unrecognized) addons remain
    if addons:
        raise CLIError('"{}" {} not recognized by the --enable-addons argument.'.format(
            ",".join(addons), "are" if len(addons) > 1 else "is"))
    return addon_profiles


def _ensure_default_log_analytics_workspace_for_monitoring(cmd, subscription_id, resource_group_name):
    # mapping for azure public cloud
    # log analytics workspaces cannot be created in WCUS region due to capacity limits
    # so mapped to EUS per discussion with log analytics team
    AzureCloudLocationToOmsRegionCodeMap = {
        "australiasoutheast": "ASE",
        "australiaeast": "EAU",
        "australiacentral": "CAU",
        "canadacentral": "CCA",
        "centralindia": "CIN",
        "centralus": "CUS",
        "eastasia": "EA",
        "eastus": "EUS",
        "eastus2": "EUS2",
        "eastus2euap": "EAP",
        "francecentral": "PAR",
        "japaneast": "EJP",
        "koreacentral": "SE",
        "northeurope": "NEU",
        "southcentralus": "SCUS",
        "southeastasia": "SEA",
        "uksouth": "SUK",
        "usgovvirginia": "USGV",
        "westcentralus": "EUS",
        "westeurope": "WEU",
        "westus": "WUS",
        "westus2": "WUS2"
    }
    AzureCloudRegionToOmsRegionMap = {
        "australiacentral": "australiacentral",
        "australiacentral2": "australiacentral",
        "australiaeast": "australiaeast",
        "australiasoutheast": "australiasoutheast",
        "brazilsouth": "southcentralus",
        "canadacentral": "canadacentral",
        "canadaeast": "canadacentral",
        "centralus": "centralus",
        "centralindia": "centralindia",
        "eastasia": "eastasia",
        "eastus": "eastus",
        "eastus2": "eastus2",
        "francecentral": "francecentral",
        "francesouth": "francecentral",
        "japaneast": "japaneast",
        "japanwest": "japaneast",
        "koreacentral": "koreacentral",
        "koreasouth": "koreacentral",
        "northcentralus": "eastus",
        "northeurope": "northeurope",
        "southafricanorth": "westeurope",
        "southafricawest": "westeurope",
        "southcentralus": "southcentralus",
        "southeastasia": "southeastasia",
        "southindia": "centralindia",
        "uksouth": "uksouth",
        "ukwest": "uksouth",
        "westcentralus": "eastus",
        "westeurope": "westeurope",
        "westindia": "centralindia",
        "westus": "westus",
        "westus2": "westus2"
    }

    # mapping for azure china cloud
    # log analytics only support China East2 region
    AzureChinaLocationToOmsRegionCodeMap = {
        "chinaeast": "EAST2",
        "chinaeast2": "EAST2",
        "chinanorth": "EAST2",
        "chinanorth2": "EAST2"
    }
    AzureChinaRegionToOmsRegionMap = {
        "chinaeast": "chinaeast2",
        "chinaeast2": "chinaeast2",
        "chinanorth": "chinaeast2",
        "chinanorth2": "chinaeast2"
    }

    # mapping for azure us governmner cloud
    AzureFairfaxLocationToOmsRegionCodeMap = {
        "usgovvirginia": "USGV"
    }
    AzureFairfaxRegionToOmsRegionMap = {
        "usgovvirginia": "usgovvirginia"
    }

    rg_location = _get_rg_location(cmd.cli_ctx, resource_group_name)
    cloud_name = cmd.cli_ctx.cloud.name

    if cloud_name.lower() == 'azurecloud':
        workspace_region = AzureCloudRegionToOmsRegionMap.get(rg_location, "eastus")
        workspace_region_code = AzureCloudLocationToOmsRegionCodeMap.get(workspace_region, "EUS")
    elif cloud_name.lower() == 'azurechinacloud':
        workspace_region = AzureChinaRegionToOmsRegionMap.get(rg_location, "chinaeast2")
        workspace_region_code = AzureChinaLocationToOmsRegionCodeMap.get(workspace_region, "EAST2")
    elif cloud_name.lower() == 'azureusgovernment':
        workspace_region = AzureFairfaxRegionToOmsRegionMap.get(rg_location, "usgovvirginia")
        workspace_region_code = AzureFairfaxLocationToOmsRegionCodeMap.get(workspace_region, "USGV")
    else:
        logger.error("AKS Monitoring addon not supported in cloud : %s", cloud_name)

    default_workspace_resource_group = 'DefaultResourceGroup-' + workspace_region_code
    default_workspace_name = 'DefaultWorkspace-{0}-{1}'.format(subscription_id, workspace_region_code)

    default_workspace_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.OperationalInsights' \
        '/workspaces/{2}'.format(subscription_id, default_workspace_resource_group, default_workspace_name)
    resource_groups = cf_resource_groups(cmd.cli_ctx, subscription_id)
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    # check if default RG exists
    if resource_groups.check_existence(default_workspace_resource_group):
        try:
            resource = resources.get_by_id(default_workspace_resource_id, '2015-11-01-preview')
            return resource.id
        except CloudError as ex:
            if ex.status_code != 404:
                raise ex
    else:
        resource_groups.create_or_update(default_workspace_resource_group, {'location': workspace_region})

    default_workspace_params = {
        'location': workspace_region,
        'properties': {
            'sku': {
                'name': 'standalone'
            }
        }
    }
    async_poller = resources.create_or_update_by_id(default_workspace_resource_id, '2015-11-01-preview',
                                                    default_workspace_params)

    ws_resource_id = ''
    while True:
        result = async_poller.result(15)
        if async_poller.done():
            ws_resource_id = result.id
            break

    return ws_resource_id


def _ensure_container_insights_for_monitoring(cmd, addon):
    if not addon.enabled:
        return None

    # workaround for this addon key which has been seen lowercased in the wild
    if 'loganalyticsworkspaceresourceid' in addon.config:
        addon.config['logAnalyticsWorkspaceResourceID'] = addon.config.pop('loganalyticsworkspaceresourceid')

    workspace_resource_id = addon.config['logAnalyticsWorkspaceResourceID'].strip()
    if not workspace_resource_id.startswith('/'):
        workspace_resource_id = '/' + workspace_resource_id

    if workspace_resource_id.endswith('/'):
        workspace_resource_id = workspace_resource_id.rstrip('/')

    # extract subscription ID and resource group from workspace_resource_id URL
    try:
        subscription_id = workspace_resource_id.split('/')[2]
        resource_group = workspace_resource_id.split('/')[4]
    except IndexError:
        raise CLIError('Could not locate resource group in workspace-resource-id URL.')

    # region of workspace can be different from region of RG so find the location of the workspace_resource_id
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    try:
        resource = resources.get_by_id(workspace_resource_id, '2015-11-01-preview')
        location = resource.location
    except CloudError as ex:
        raise ex

    unix_time_in_millis = int(
        (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)

    solution_deployment_name = 'ContainerInsights-{}'.format(unix_time_in_millis)

    # pylint: disable=line-too-long
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "workspaceResourceId": {
                "type": "string",
                "metadata": {
                    "description": "Azure Monitor Log Analytics Resource ID"
                }
            },
            "workspaceRegion": {
                "type": "string",
                "metadata": {
                    "description": "Azure Monitor Log Analytics workspace region"
                }
            },
            "solutionDeploymentName": {
                "type": "string",
                "metadata": {
                    "description": "Name of the solution deployment"
                }
            }
        },
        "resources": [
            {
                "type": "Microsoft.Resources/deployments",
                "name": "[parameters('solutionDeploymentName')]",
                "apiVersion": "2017-05-10",
                "subscriptionId": "[split(parameters('workspaceResourceId'),'/')[2]]",
                "resourceGroup": "[split(parameters('workspaceResourceId'),'/')[4]]",
                "properties": {
                    "mode": "Incremental",
                    "template": {
                        "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                        "contentVersion": "1.0.0.0",
                        "parameters": {},
                        "variables": {},
                        "resources": [
                            {
                                "apiVersion": "2015-11-01-preview",
                                "type": "Microsoft.OperationsManagement/solutions",
                                "location": "[parameters('workspaceRegion')]",
                                "name": "[Concat('ContainerInsights', '(', split(parameters('workspaceResourceId'),'/')[8], ')')]",
                                "properties": {
                                    "workspaceResourceId": "[parameters('workspaceResourceId')]"
                                },
                                "plan": {
                                    "name": "[Concat('ContainerInsights', '(', split(parameters('workspaceResourceId'),'/')[8], ')')]",
                                    "product": "[Concat('OMSGallery/', 'ContainerInsights')]",
                                    "promotionCode": "",
                                    "publisher": "Microsoft"
                                }
                            }
                        ]
                    },
                    "parameters": {}
                }
            }
        ]
    }

    params = {
        "workspaceResourceId": {
            "value": workspace_resource_id
        },
        "workspaceRegion": {
            "value": location
        },
        "solutionDeploymentName": {
            "value": solution_deployment_name
        }
    }

    deployment_name = 'aks-monitoring-{}'.format(unix_time_in_millis)
    # publish the Container Insights solution to the Log Analytics workspace
    return _invoke_deployment(cmd, resource_group, deployment_name, template, params,
                              validate=False, no_wait=False, subscription_id=subscription_id)


def _ensure_aks_service_principal(cli_ctx,
                                  service_principal=None,
                                  client_secret=None,
                                  subscription_id=None,
                                  dns_name_prefix=None,
                                  location=None,
                                  name=None):
    file_name_aks = 'aksServicePrincipal.json'
    # TODO: This really needs to be unit tested.
    rbac_client = get_graph_rbac_management_client(cli_ctx)
    if not service_principal:
        # --service-principal not specified, try to load it from local disk
        principal_obj = load_acs_service_principal(subscription_id, file_name=file_name_aks)
        if principal_obj:
            service_principal = principal_obj.get('service_principal')
            client_secret = principal_obj.get('client_secret')
        else:
            # Nothing to load, make one.
            if not client_secret:
                client_secret = _create_client_secret()
            salt = binascii.b2a_hex(os.urandom(3)).decode('utf-8')
            url = 'http://{}.{}.{}.cloudapp.azure.com'.format(salt, dns_name_prefix, location)

            service_principal = _build_service_principal(rbac_client, cli_ctx, name, url, client_secret)
            if not service_principal:
                raise CLIError('Could not create a service principal with the right permissions. '
                               'Are you an Owner on this project?')
            logger.info('Created a service principal: %s', service_principal)
            # We don't need to add role assignment for this created SPN
    else:
        # --service-principal specfied, validate --client-secret was too
        if not client_secret:
            raise CLIError('--client-secret is required if --service-principal is specified')
    store_acs_service_principal(subscription_id, client_secret, service_principal, file_name=file_name_aks)
    return load_acs_service_principal(subscription_id, file_name=file_name_aks)


def _get_rg_location(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    # Just do the get, we don't need the result, it will error out if the group doesn't exist.
    rg = groups.get(resource_group_name)
    return rg.location


def _check_cluster_autoscaler_flag(enable_cluster_autoscaler,
                                   min_count,
                                   max_count,
                                   node_count,
                                   agent_pool_profile):
    if enable_cluster_autoscaler:
        if min_count is None or max_count is None:
            raise CLIError('Please specify both min-count and max-count when --enable-cluster-autoscaler enabled')
        if int(min_count) > int(max_count):
            raise CLIError('value of min-count should be less than or equal to value of max-count')
        if int(node_count) < int(min_count) or int(node_count) > int(max_count):
            raise CLIError('node-count is not in the range of min-count and max-count')
        agent_pool_profile.min_count = int(min_count)
        agent_pool_profile.max_count = int(max_count)
        agent_pool_profile.enable_auto_scaling = True
    else:
        if min_count is not None or max_count is not None:
            raise CLIError('min-count and max-count are required for --enable-cluster-autoscaler, please use the flag')


def _create_client_secret():
    # Add a special character to satsify AAD SP secret requirements
    special_char = '$'
    client_secret = binascii.b2a_hex(os.urandom(10)).decode('utf-8') + special_char
    return client_secret


def _ensure_aks_acr(cli_ctx,
                    client_id,
                    acr_name_or_id,
                    subscription_id,    # pylint: disable=unused-argument
                    detach=False):
    from msrestazure.tools import is_valid_resource_id, parse_resource_id
    # Check if the ACR exists by resource ID.
    if is_valid_resource_id(acr_name_or_id):
        try:
            parsed_registry = parse_resource_id(acr_name_or_id)
            acr_client = cf_container_registry_service(cli_ctx, subscription_id=parsed_registry['subscription'])
            registry = acr_client.registries.get(parsed_registry['resource_group'], parsed_registry['name'])
        except CloudError as ex:
            raise CLIError(ex.message)
        _ensure_aks_acr_role_assignment(cli_ctx, client_id, registry.id, detach)
        return

    # Check if the ACR exists by name accross all resource groups.
    registry_name = acr_name_or_id
    registry_resource = 'Microsoft.ContainerRegistry/registries'
    try:
        registry = get_resource_by_name(cli_ctx, registry_name, registry_resource)
    except CloudError as ex:
        if 'was not found' in ex.message:
            raise CLIError("ACR {} not found. Have you provided the right ACR name?".format(registry_name))
        raise CLIError(ex.message)
    _ensure_aks_acr_role_assignment(cli_ctx, client_id, registry.id, detach)
    return


def _ensure_aks_acr_role_assignment(cli_ctx,
                                    client_id,
                                    registry_id,
                                    detach=False):
    if detach:
        if not _delete_role_assignments(cli_ctx,
                                        'acrpull',
                                        client_id,
                                        scope=registry_id):
            raise CLIError('Could not delete role assignments for ACR. '
                           'Are you an Owner on this subscription?')
        return

    if not _add_role_assignment(cli_ctx,
                                'acrpull',
                                client_id,
                                scope=registry_id):
        raise CLIError('Could not create a role assignment for ACR. '
                       'Are you an Owner on this subscription?')
    return


def aks_agentpool_show(cmd,     # pylint: disable=unused-argument
                       client,
                       resource_group_name,
                       cluster_name,
                       nodepool_name):
    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    return instance


def aks_agentpool_list(cmd,     # pylint: disable=unused-argument
                       client,
                       resource_group_name,
                       cluster_name):
    return client.list(resource_group_name, cluster_name)


def aks_agentpool_add(cmd,      # pylint: disable=unused-argument,too-many-locals
                      client,
                      resource_group_name,
                      cluster_name,
                      nodepool_name,
                      tags=None,
                      kubernetes_version=None,
                      node_zones=None,
                      enable_node_public_ip=False,
                      node_vm_size=None,
                      node_osdisk_type=None,
                      node_osdisk_size=0,
                      node_count=3,
                      vnet_subnet_id=None,
                      ppg=None,
                      max_pods=0,
                      os_type="Linux",
                      min_count=None,
                      max_count=None,
                      enable_cluster_autoscaler=False,
                      node_taints=None,
                      priority=CONST_SCALE_SET_PRIORITY_REGULAR,
                      eviction_policy=CONST_SPOT_EVICTION_POLICY_DELETE,
                      spot_max_price=float('nan'),
                      labels=None,
                      max_surge=None,
                      mode="User",
                      aks_custom_headers=None,
                      no_wait=False):
    instances = client.list(resource_group_name, cluster_name)
    for agentpool_profile in instances:
        if agentpool_profile.name == nodepool_name:
            raise CLIError("Node pool {} already exists, please try a different name, "
                           "use 'aks nodepool list' to get current list of node pool".format(nodepool_name))

    upgradeSettings = AgentPoolUpgradeSettings()
    taints_array = []

    if node_taints is not None:
        for taint in node_taints.split(','):
            try:
                taint = taint.strip()
                taints_array.append(taint)
            except ValueError:
                raise CLIError('Taint does not match allowed values. Expect value such as "special=true:NoSchedule".')

    if node_vm_size is None:
        if os_type == "Windows":
            node_vm_size = "Standard_D2s_v3"
        else:
            node_vm_size = "Standard_DS2_v2"

    if max_surge:
        upgradeSettings.max_surge = max_surge

    agent_pool = AgentPool(
        name=nodepool_name,
        tags=tags,
        node_labels=labels,
        count=int(node_count),
        vm_size=node_vm_size,
        os_type=os_type,
        storage_profile=ContainerServiceStorageProfileTypes.managed_disks,
        vnet_subnet_id=vnet_subnet_id,
        proximity_placement_group_id=ppg,
        agent_pool_type="VirtualMachineScaleSets",
        max_pods=int(max_pods) if max_pods else None,
        orchestrator_version=kubernetes_version,
        availability_zones=node_zones,
        enable_node_public_ip=enable_node_public_ip,
        node_taints=taints_array,
        scale_set_priority=priority,
        upgrade_settings=upgradeSettings,
        mode=mode
    )

    if priority == CONST_SCALE_SET_PRIORITY_SPOT:
        agent_pool.scale_set_eviction_policy = eviction_policy
        if isnan(spot_max_price):
            spot_max_price = -1
        agent_pool.spot_max_price = spot_max_price

    _check_cluster_autoscaler_flag(enable_cluster_autoscaler, min_count, max_count, node_count, agent_pool)

    if node_osdisk_size:
        agent_pool.os_disk_size_gb = int(node_osdisk_size)

    if node_osdisk_type:
        agent_pool.os_disk_type = node_osdisk_type

    headers = get_aks_custom_headers(aks_custom_headers)
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, nodepool_name, agent_pool, custom_headers=headers)


def aks_agentpool_scale(cmd,    # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        cluster_name,
                        nodepool_name,
                        node_count=3,
                        no_wait=False):
    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    new_node_count = int(node_count)
    if instance.enable_auto_scaling:
        raise CLIError("Cannot scale cluster autoscaler enabled node pool.")
    if new_node_count == instance.count:
        raise CLIError("The new node count is the same as the current node count.")
    instance.count = new_node_count  # pylint: disable=no-member
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


def aks_agentpool_upgrade(cmd,  # pylint: disable=unused-argument
                          client,
                          resource_group_name,
                          cluster_name,
                          nodepool_name,
                          kubernetes_version='',
                          no_wait=False,
                          node_image_only=False,
                          max_surge=None,):

    from knack.prompting import prompt_y_n
    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    if kubernetes_version != '' and node_image_only:
        raise CLIError('Conflicting flags. Upgrading the Kubernetes version will also upgrade node image version. If you only want to upgrade the node version please use the "--node-image-only" option only.')

    instance.orchestrator_version = kubernetes_version
    if node_image_only:
        msg = "This node image upgrade operation will run across every node in this node pool and might take a while, " \
              "do you wish to continue? "
        if not prompt_y_n(msg, default="n"):
            return None
        instance.node_image_version = 'latest'

    if not instance.upgrade_settings:
        instance.upgrade_settings = AgentPoolUpgradeSettings()

    if max_surge:
        instance.upgrade_settings.max_surge = max_surge

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


def aks_agentpool_get_upgrade_profile(cmd,   # pylint: disable=unused-argument
                                      client,
                                      resource_group_name,
                                      cluster_name,
                                      nodepool_name):
    return client.get_upgrade_profile(resource_group_name, cluster_name, nodepool_name)


def aks_agentpool_update(cmd,   # pylint: disable=unused-argument
                         client,
                         resource_group_name,
                         cluster_name,
                         nodepool_name,
                         tags=None,
                         enable_cluster_autoscaler=False,
                         disable_cluster_autoscaler=False,
                         update_cluster_autoscaler=False,
                         min_count=None, max_count=None,
                         max_surge=None,
                         mode=None,
                         no_wait=False):

    update_autoscaler = enable_cluster_autoscaler + disable_cluster_autoscaler + update_cluster_autoscaler

    if (update_autoscaler != 1 and not tags and not mode and not max_surge):
        raise CLIError('Please specify one or more of "--enable-cluster-autoscaler" or '
                       '"--disable-cluster-autoscaler" or '
                       '"--update-cluster-autoscaler" or '
                       '"--tags" or "--mode" or "--max-surge"')

    instance = client.get(resource_group_name, cluster_name, nodepool_name)

    if min_count is None or max_count is None:
        if enable_cluster_autoscaler or update_cluster_autoscaler:
            raise CLIError('Please specify both min-count and max-count when --enable-cluster-autoscaler or '
                           '--update-cluster-autoscaler set.')
    if min_count is not None and max_count is not None:
        if int(min_count) > int(max_count):
            raise CLIError('value of min-count should be less than or equal to value of max-count.')

    if enable_cluster_autoscaler:
        if instance.enable_auto_scaling:
            logger.warning('Autoscaler is already enabled for this node pool.\n'
                           'Please run "az aks nodepool update --update-cluster-autoscaler" '
                           'if you want to update min-count or max-count.')
            return None
        instance.min_count = int(min_count)
        instance.max_count = int(max_count)
        instance.enable_auto_scaling = True

    if update_cluster_autoscaler:
        if not instance.enable_auto_scaling:
            raise CLIError('Autoscaler is not enabled for this node pool.\n'
                           'Run "az aks nodepool update --enable-cluster-autoscaler" '
                           'to enable cluster with min-count and max-count.')
        instance.min_count = int(min_count)
        instance.max_count = int(max_count)

    if not instance.upgrade_settings:
        instance.upgrade_settings = AgentPoolUpgradeSettings()

    if max_surge:
        instance.upgrade_settings.max_surge = max_surge

    if disable_cluster_autoscaler:
        if not instance.enable_auto_scaling:
            logger.warning('Autoscaler is already disabled for this node pool.')
            return None
        instance.enable_auto_scaling = False
        instance.min_count = None
        instance.max_count = None

    instance.tags = tags
    if mode is not None:
        instance.mode = mode

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


def aks_agentpool_delete(cmd,   # pylint: disable=unused-argument
                         client,
                         resource_group_name,
                         cluster_name,
                         nodepool_name,
                         no_wait=False):
    agentpool_exists = False
    instances = client.list(resource_group_name, cluster_name)
    for agentpool_profile in instances:
        if agentpool_profile.name.lower() == nodepool_name.lower():
            agentpool_exists = True
            break

    if not agentpool_exists:
        raise CLIError("Node pool {} doesnt exist, "
                       "use 'aks nodepool list' to get current node pool list".format(nodepool_name))

    return sdk_no_wait(no_wait, client.delete, resource_group_name, cluster_name, nodepool_name)


def aks_disable_addons(cmd, client, resource_group_name, name, addons, no_wait=False):
    instance = client.get(resource_group_name, name)
    subscription_id = get_subscription_id(cmd.cli_ctx)

    instance = _update_addons(
        cmd,
        instance,
        subscription_id,
        resource_group_name,
        name,
        addons,
        enable=False,
        no_wait=no_wait
    )

    # send the managed cluster representation to update the addon profiles
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, name, instance)


def aks_enable_addons(cmd, client, resource_group_name, name, addons, workspace_resource_id=None,
                      subnet_name=None, appgw_name=None, appgw_subnet_prefix=None, appgw_id=None, appgw_subnet_id=None,
                      appgw_watch_namespace=None, disable_sgxquotehelper=False, no_wait=False, osm_mesh_name=None):
    instance = client.get(resource_group_name, name)
    subscription_id = get_subscription_id(cmd.cli_ctx)
    instance = _update_addons(cmd, instance, subscription_id, resource_group_name, name, addons, enable=True,
                              workspace_resource_id=workspace_resource_id, subnet_name=subnet_name,
                              appgw_name=appgw_name, appgw_subnet_prefix=appgw_subnet_prefix, appgw_id=appgw_id, appgw_subnet_id=appgw_subnet_id, appgw_watch_namespace=appgw_watch_namespace,
                              disable_sgxquotehelper=disable_sgxquotehelper, osm_mesh_name=osm_mesh_name, no_wait=no_wait)

    if 'omsagent' in instance.addon_profiles and instance.addon_profiles['omsagent'].enabled:
        _ensure_container_insights_for_monitoring(cmd, instance.addon_profiles['omsagent'])

    monitoring = 'omsagent' in instance.addon_profiles and instance.addon_profiles['omsagent'].enabled
    ingress_appgw_addon_enabled = CONST_INGRESS_APPGW_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].enabled
    need_post_creation_role_assignment = monitoring or ingress_appgw_addon_enabled

    if need_post_creation_role_assignment:
        # adding a wait here since we rely on the result for role assignment
        result = LongRunningOperation(cmd.cli_ctx)(client.create_or_update(resource_group_name, name, instance))
        cloud_name = cmd.cli_ctx.cloud.name
        # mdm metrics supported only in Azure Public cloud so add the role assignment only in this cloud
        if monitoring and cloud_name.lower() == 'azurecloud':
            from msrestazure.tools import resource_id
            cluster_resource_id = resource_id(
                subscription=subscription_id,
                resource_group=resource_group_name,
                namespace='Microsoft.ContainerService', type='managedClusters',
                name=name
            )
            _add_monitoring_role_assignment(result, cluster_resource_id, cmd)
        if ingress_appgw_addon_enabled:
            _add_ingress_appgw_addon_role_assignment(result, cmd)

    else:
        result = sdk_no_wait(no_wait, client.create_or_update,
                             resource_group_name, name, instance)
    return result


def aks_rotate_certs(cmd, client, resource_group_name, name, no_wait=True):     # pylint: disable=unused-argument
    return sdk_no_wait(no_wait, client.rotate_cluster_certificates, resource_group_name, name)


def _update_addons(cmd,  # pylint: disable=too-many-branches,too-many-statements
                   instance,
                   subscription_id,
                   resource_group_name,
                   name,
                   addons,
                   enable,
                   workspace_resource_id=None,
                   subnet_name=None,
                   appgw_name=None,
                   appgw_subnet_prefix=None,
                   appgw_id=None,
                   appgw_subnet_id=None,
                   appgw_watch_namespace=None,
                   disable_sgxquotehelper=False,
                   osm_mesh_name=None,
                   no_wait=False):  # pylint: disable=unused-argument

    # parse the comma-separated addons argument
    addon_args = addons.split(',')

    addon_profiles = instance.addon_profiles or {}

    os_type = 'Linux'

    # for each addons argument
    for addon_arg in addon_args:
        if addon_arg not in ADDONS:
            raise CLIError("Invalid addon name: {}.".format(addon_arg))
        addon = ADDONS[addon_arg]
        if addon == 'aciConnector':
            # only linux is supported for now, in the future this will be a user flag
            addon += os_type
        # addon name is case insensitive
        addon = next((x for x in addon_profiles.keys() if x.lower() == addon.lower()), addon)
        if enable:
            # add new addons or update existing ones and enable them
            addon_profile = addon_profiles.get(addon, ManagedClusterAddonProfile(enabled=False))
            # special config handling for certain addons
            if addon == 'omsagent':
                if addon_profile.enabled:
                    raise CLIError('The monitoring addon is already enabled for this managed cluster.\n'
                                   'To change monitoring configuration, run "az aks disable-addons -a monitoring"'
                                   'before enabling it again.')
                if not workspace_resource_id:
                    workspace_resource_id = _ensure_default_log_analytics_workspace_for_monitoring(
                        cmd,
                        subscription_id,
                        resource_group_name)
                workspace_resource_id = workspace_resource_id.strip()
                if not workspace_resource_id.startswith('/'):
                    workspace_resource_id = '/' + workspace_resource_id
                if workspace_resource_id.endswith('/'):
                    workspace_resource_id = workspace_resource_id.rstrip('/')
                addon_profile.config = {'logAnalyticsWorkspaceResourceID': workspace_resource_id}
            elif addon.lower() == ('aciConnector' + os_type).lower():
                if addon_profile.enabled:
                    raise CLIError('The virtual-node addon is already enabled for this managed cluster.\n'
                                   'To change virtual-node configuration, run '
                                   '"az aks disable-addons -a virtual-node -g {resource_group_name}" '
                                   'before enabling it again.')
                if not subnet_name:
                    raise CLIError('The aci-connector addon requires setting a subnet name.')
                addon_profile.config = {'SubnetName': subnet_name}
            elif addon.lower() == CONST_INGRESS_APPGW_ADDON_NAME.lower():
                if addon_profile.enabled:
                    raise CLIError('The ingress-appgw addon is already enabled for this managed cluster.\n'
                                   'To change ingress-appgw configuration, run '
                                   f'"az aks disable-addons -a ingress-appgw -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(enabled=True, config={})
                if appgw_name is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME] = appgw_name
                if appgw_subnet_prefix is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_PREFIX] = appgw_subnet_prefix
                if appgw_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID] = appgw_id
                if appgw_subnet_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_ID] = appgw_subnet_id
                if appgw_watch_namespace is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_WATCH_NAMESPACE] = appgw_watch_namespace
            elif addon.lower() == CONST_OPEN_SERVICE_MESH_ADDON_NAME.lower():
                if addon_profile.enabled:
                    raise CLIError('The open-service-mesh addon is already enabled for this managed cluster.\n'
                                   'To change open-service-mesh configuration, run '
                                   f'"az aks disable-addons -a open-service-mesh -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(enabled=True, config={})
                if osm_mesh_name is not None:
                    addon_profile.config[CONST_OPEN_SERVICE_MESH_NAME_KEY] = osm_mesh_name
            elif addon.lower() == CONST_CONFCOM_ADDON_NAME.lower():
                if addon_profile.enabled:
                    raise CLIError('The confcom addon is already enabled for this managed cluster.\n'
                                   'To change confcom configuration, run '
                                   f'"az aks disable-addons -a confcom -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(enabled=True, config={CONST_ACC_SGX_QUOTE_HELPER_ENABLED: "true"})
                if disable_sgxquotehelper:
                    addon_profile.config[CONST_ACC_SGX_QUOTE_HELPER_ENABLED] = "false"
            addon_profiles[addon] = addon_profile
        else:
            if addon not in addon_profiles:
                if addon == CONST_KUBE_DASHBOARD_ADDON_NAME:
                    addon_profiles[addon] = ManagedClusterAddonProfile(enabled=False)
                else:
                    raise CLIError("The addon {} is not installed.".format(addon))
            addon_profiles[addon].config = None
        addon_profiles[addon].enabled = enable

    instance.addon_profiles = addon_profiles

    # null out the SP and AAD profile because otherwise validation complains
    instance.service_principal_profile = None
    instance.aad_profile = None

    return instance


def aks_get_versions(cmd, client, location):    # pylint: disable=unused-argument
    return client.list_orchestrators(location, resource_type='managedClusters')


def _print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name):
    """Merge an unencrypted kubeconfig into the file at the specified path, or print it to
    stdout if the path is "-".
    """
    # Special case for printing to stdout
    if path == "-":
        print(kubeconfig)
        return

    # ensure that at least an empty ~/.kube/config exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise
    if not os.path.exists(path):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt'):
            pass

    # merge the new kubeconfig into the existing one
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, 'w+t')
    try:
        additional_file.write(kubeconfig)
        additional_file.flush()
        merge_kubernetes_configurations(path, temp_path, overwrite_existing, context_name)
    except yaml.YAMLError as ex:
        logger.warning('Failed to merge credentials to kube config file: %s', ex)
    finally:
        additional_file.close()
        os.remove(temp_path)


def _handle_merge(existing, addition, key, replace):
    if not addition[key]:
        return
    if existing[key] is None:
        existing[key] = addition[key]
        return

    for i in addition[key]:
        for j in existing[key]:
            if i['name'] == j['name']:
                if replace or i == j:
                    existing[key].remove(j)
                else:
                    from knack.prompting import prompt_y_n
                    msg = 'A different object named {} already exists in your kubeconfig file.\nOverwrite?'
                    overwrite = False
                    try:
                        overwrite = prompt_y_n(msg.format(i['name']))
                    except NoTTYException:
                        pass
                    if overwrite:
                        existing[key].remove(j)
                    else:
                        msg = 'A different object named {} already exists in {} in your kubeconfig file.'
                        raise CLIError(msg.format(i['name'], key))
        existing[key].append(i)


def load_kubernetes_configuration(filename):
    try:
        with open(filename) as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            raise CLIError('{} does not exist'.format(filename))
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        raise CLIError('Error parsing {} ({})'.format(filename, str(ex)))


def merge_kubernetes_configurations(existing_file, addition_file, replace, context_name=None):
    existing = load_kubernetes_configuration(existing_file)
    addition = load_kubernetes_configuration(addition_file)

    if context_name is not None:
        addition['contexts'][0]['name'] = context_name
        addition['contexts'][0]['context']['cluster'] = context_name
        addition['clusters'][0]['name'] = context_name
        addition['current-context'] = context_name

    # rename the admin context so it doesn't overwrite the user context
    for ctx in addition.get('contexts', []):
        try:
            if ctx['context']['user'].startswith('clusterAdmin'):
                admin_name = ctx['name'] + '-admin'
                addition['current-context'] = ctx['name'] = admin_name
                break
        except (KeyError, TypeError):
            continue

    if addition is None:
        raise CLIError('failed to load additional configuration from {}'.format(addition_file))

    if existing is None:
        existing = addition
    else:
        _handle_merge(existing, addition, 'clusters', replace)
        _handle_merge(existing, addition, 'users', replace)
        _handle_merge(existing, addition, 'contexts', replace)
        existing['current-context'] = addition['current-context']

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != 'Windows':
        existing_file_perms = "{:o}".format(stat.S_IMODE(os.lstat(existing_file).st_mode))
        if not existing_file_perms.endswith('600'):
            logger.warning('%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                           existing_file, existing_file_perms)

    with open(existing_file, 'w+') as stream:
        yaml.safe_dump(existing, stream, default_flow_style=False)

    current_context = addition.get('current-context', 'UNKNOWN')
    msg = 'Merged "{}" as current context in {}'.format(current_context, existing_file)
    print(msg)


def cloud_storage_account_service_factory(cli_ctx, kwargs):
    from azure.cli.core.profiles import ResourceType, get_sdk
    t_cloud_storage_account = get_sdk(cli_ctx, ResourceType.DATA_STORAGE, 'common#CloudStorageAccount')
    account_name = kwargs.pop('account_name', None)
    account_key = kwargs.pop('account_key', None)
    sas_token = kwargs.pop('sas_token', None)
    kwargs.pop('connection_string', None)
    return t_cloud_storage_account(account_name, account_key, sas_token)


def get_storage_account_from_diag_settings(cli_ctx, resource_group_name, name):
    from azure.mgmt.monitor import MonitorManagementClient
    diag_settings_client = get_mgmt_service_client(cli_ctx, MonitorManagementClient).diagnostic_settings
    subscription_id = get_subscription_id(cli_ctx)
    aks_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.ContainerService' \
        '/managedClusters/{2}'.format(subscription_id, resource_group_name, name)
    diag_settings = diag_settings_client.list(aks_resource_id)
    if diag_settings.value:
        return diag_settings.value[0].storage_account_id

    print("No diag settings specified")
    return None


def display_diagnostics_report(temp_kubeconfig_path):   # pylint: disable=too-many-statements
    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')

    nodes = subprocess.check_output(
        ["kubectl", "--kubeconfig", temp_kubeconfig_path, "get", "node", "--no-headers"],
        universal_newlines=True)
    logger.debug(nodes)
    node_lines = nodes.splitlines()
    ready_nodes = {}
    for node_line in node_lines:
        columns = node_line.split()
        logger.debug(node_line)
        if columns[1] != "Ready":
            logger.warning("Node %s is not Ready. Current state is: %s.", columns[0], columns[1])
        else:
            ready_nodes[columns[0]] = False

    logger.debug('There are %s ready nodes in the cluster', str(len(ready_nodes)))

    if not ready_nodes:
        logger.warning('No nodes are ready in the current cluster. Diagnostics info might not be available.')

    network_config_array = []
    network_status_array = []
    apds_created = False

    max_retry = 10
    for retry in range(0, max_retry):
        if not apds_created:
            apd = subprocess.check_output(
                ["kubectl", "--kubeconfig", temp_kubeconfig_path, "get", "apd", "-n", "aks-periscope", "--no-headers"],
                universal_newlines=True
            )
            apd_lines = apd.splitlines()
            if apd_lines and 'No resources found' in apd_lines[0]:
                apd_lines.pop(0)

            print("Got {} diagnostic results for {} ready nodes{}\r".format(len(apd_lines),
                                                                            len(ready_nodes),
                                                                            '.' * retry), end='')
            if len(apd_lines) < len(ready_nodes):
                time.sleep(3)
            else:
                apds_created = True
                print()
        else:
            for node_name in ready_nodes:
                if ready_nodes[node_name]:
                    continue
                apdName = "aks-periscope-diagnostic-" + node_name
                try:
                    network_config = subprocess.check_output(
                        ["kubectl", "--kubeconfig", temp_kubeconfig_path,
                         "get", "apd", apdName, "-n",
                         "aks-periscope", "-o=jsonpath={.spec.networkconfig}"],
                        universal_newlines=True)
                    logger.debug('Dns status for node %s is %s', node_name, network_config)
                    network_status = subprocess.check_output(
                        ["kubectl", "--kubeconfig", temp_kubeconfig_path,
                         "get", "apd", apdName, "-n",
                         "aks-periscope", "-o=jsonpath={.spec.networkoutbound}"],
                        universal_newlines=True)
                    logger.debug('Network status for node %s is %s', node_name, network_status)

                    if not network_config or not network_status:
                        print("The diagnostics information for node {} is not ready yet. "
                              "Will try again in 10 seconds.".format(node_name))
                        time.sleep(10)
                        break

                    network_config_array += json.loads('[' + network_config + ']')
                    network_status_object = json.loads(network_status)
                    network_status_array += format_diag_status(network_status_object)
                    ready_nodes[node_name] = True
                except subprocess.CalledProcessError as err:
                    raise CLIError(err.output)

    print()
    if network_config_array:
        print("Below are the network configuration for each node: ")
        print()
        print(tabulate(network_config_array, headers="keys", tablefmt='simple'))
        print()
    else:
        logger.warning("Could not get network config. "
                       "Please run 'az aks kanalyze' command later to get the analysis results.")

    if network_status_array:
        print("Below are the network connectivity results for each node:")
        print()
        print(tabulate(network_status_array, headers="keys", tablefmt='simple'))
    else:
        logger.warning("Could not get networking status. "
                       "Please run 'az aks kanalyze' command later to get the analysis results.")


def format_diag_status(diag_status):
    for diag in diag_status:
        if diag["Status"]:
            if "Error:" in diag["Status"]:
                diag["Status"] = f'{colorama.Fore.RED}{diag["Status"]}{colorama.Style.RESET_ALL}'
            else:
                diag["Status"] = f'{colorama.Fore.GREEN}{diag["Status"]}{colorama.Style.RESET_ALL}'

    return diag_status


def format_bright(msg):
    return f'\033[1m{colorama.Style.BRIGHT}{msg}{colorama.Style.RESET_ALL}'


def format_hyperlink(the_link):
    return f'\033[1m{colorama.Style.BRIGHT}{colorama.Fore.BLUE}{the_link}{colorama.Style.RESET_ALL}'


def get_aks_custom_headers(aks_custom_headers=None):
    headers = {}
    if aks_custom_headers is not None:
        if aks_custom_headers != "":
            for pair in aks_custom_headers.split(','):
                parts = pair.split('=')
                if len(parts) != 2:
                    raise CLIError('custom headers format is incorrect')
                headers[parts[0]] = parts[1]
    return headers
