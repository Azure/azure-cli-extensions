# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import binascii
import datetime
import errno
import io
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
import zipfile
from distutils.version import StrictVersion
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
from azure.cli.core.azclierror import ManualInterrupt, InvalidArgumentValueError, UnclassifiedUserFault, CLIInternalError, FileOperationError, ClientRequestError, DeploymentError, ValidationError, ArgumentUsageError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.keys import is_valid_ssh_rsa_public_key
from azure.cli.core.util import get_file_json, in_cloud_console, shell_safe_json_parse, truncate_text, sdk_no_wait
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core._profile import Profile
from azure.graphrbac.models import (ApplicationCreateParameters,
                                    PasswordCredential,
                                    KeyCredential,
                                    ServicePrincipalCreateParameters,
                                    GetObjectsParameters)
from .vendored_sdks.azure_mgmt_preview_aks.v2021_08_01.models import (ContainerServiceLinuxProfile,
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
                                                                      ManagedServiceIdentityUserAssignedIdentitiesValue,
                                                                      ManagedClusterAutoUpgradeProfile,
                                                                      KubeletConfig,
                                                                      LinuxOSConfig,
                                                                      ManagedClusterHTTPProxyConfig,
                                                                      SysctlConfig,
                                                                      ManagedClusterPodIdentityProfile,
                                                                      ManagedClusterPodIdentity,
                                                                      ManagedClusterPodIdentityException,
                                                                      UserAssignedIdentity)
from ._client_factory import cf_resource_groups
from ._client_factory import get_auth_management_client
from ._client_factory import get_graph_rbac_management_client
from ._client_factory import get_msi_client
from ._client_factory import cf_resources
from ._client_factory import get_resource_by_name
from ._client_factory import cf_container_registry_service
from ._client_factory import cf_storage
from ._client_factory import cf_agent_pools
from ._resourcegroup import get_rg_location

from ._roleassignments import add_role_assignment, create_role_assignment, build_role_scope, resolve_role_id, \
    resolve_object_id

from ._helpers import (_populate_api_server_access_profile, _set_vm_set_type,
                       _set_outbound_type, _parse_comma_separated_list,
                       _trim_fqdn_name_containing_hcp)
from ._loadbalancer import (set_load_balancer_sku, is_load_balancer_profile_provided,
                            update_load_balancer_profile, create_load_balancer_profile)
from ._natgateway import (create_nat_gateway_profile, update_nat_gateway_profile, is_nat_gateway_profile_provided)
from ._consts import CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME
from ._consts import CONST_MONITORING_ADDON_NAME
from ._consts import CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID
from ._consts import CONST_MONITORING_USING_AAD_MSI_AUTH
from ._consts import CONST_VIRTUAL_NODE_ADDON_NAME
from ._consts import CONST_VIRTUAL_NODE_SUBNET_NAME
from ._consts import CONST_AZURE_POLICY_ADDON_NAME
from ._consts import CONST_KUBE_DASHBOARD_ADDON_NAME
from ._consts import CONST_INGRESS_APPGW_ADDON_NAME
from ._consts import CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID, CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME
from ._consts import CONST_INGRESS_APPGW_SUBNET_CIDR, CONST_INGRESS_APPGW_SUBNET_ID
from ._consts import CONST_INGRESS_APPGW_WATCH_NAMESPACE
from ._consts import CONST_SCALE_SET_PRIORITY_REGULAR, CONST_SCALE_SET_PRIORITY_SPOT, CONST_SPOT_EVICTION_POLICY_DELETE
from ._consts import CONST_SCALE_DOWN_MODE_DELETE
from ._consts import CONST_CONFCOM_ADDON_NAME, CONST_ACC_SGX_QUOTE_HELPER_ENABLED
from ._consts import CONST_OPEN_SERVICE_MESH_ADDON_NAME
from ._consts import CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME, CONST_SECRET_ROTATION_ENABLED
from ._consts import CONST_MANAGED_IDENTITY_OPERATOR_ROLE, CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID
from ._consts import CONST_PRIVATE_DNS_ZONE_SYSTEM, CONST_PRIVATE_DNS_ZONE_NONE
from ._consts import ADDONS, ADDONS_DESCRIPTIONS
from .maintenanceconfiguration import aks_maintenanceconfiguration_update_internal
from .addonconfiguration import update_addons, enable_addons, ensure_default_log_analytics_workspace_for_monitoring, \
    sanitize_loganalytics_ws_resource_id, ensure_container_insights_for_monitoring, add_monitoring_role_assignment, \
    add_ingress_appgw_addon_role_assignment, add_virtual_node_role_assignment

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
            # added in python 2.7.13 and 3.6
            return ssl.SSLContext(ssl.PROTOCOL_TLS)
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
        hook.add(message='Creating service principal',
                 value=0.1 * x, total_val=1.0)
        try:
            create_service_principal(
                cli_ctx, service_principal, rbac_client=rbac_client)
            break
        # TODO figure out what exception AAD throws here sometimes.
        except Exception as ex:  # pylint: disable=broad-except
            logger.info(ex)
            time.sleep(2 + 2 * x)
    else:
        return False
    hook.add(message='Finished service principal creation',
             value=1.0, total_val=1.0)
    logger.info('Finished service principal creation')
    return service_principal


def _delete_role_assignments(cli_ctx, role, service_principal, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for AAD role to delete', value=0, total_val=1.0)
    logger.info('Waiting for AAD role to delete')
    for x in range(0, 10):
        hook.add(message='Waiting for AAD role to delete',
                 value=0.1 * x, total_val=1.0)
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
    resource_group_part = re.sub(
        '[^A-Za-z0-9-]', '', resource_group_name)[0:16]
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
        raise CLIError(
            'specify either --password or --key-value, but not both.')

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
            result = list(rbac_client.applications.list(
                filter="appId eq '{}'".format(identifier)))
        except ValueError:
            result = list(rbac_client.applications.list(
                filter="identifierUris/any(s:s eq '{}')".format(identifier)))

        if not result:  # assume we get an object id
            result = [rbac_client.applications.get(identifier)]
        app_id = result[0].app_id
    else:
        app_id = identifier

    return rbac_client.service_principals.create(ServicePrincipalCreateParameters(app_id=app_id, account_enabled=True))


def delete_role_assignments(cli_ctx, ids=None, assignee=None, role=None, resource_group_name=None,
                            scope=None, include_inherited=False, yes=None):
    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions
    ids = ids or []
    if ids:
        if assignee or role or resource_group_name or scope or include_inherited:
            raise CLIError(
                'When assignment ids are used, other parameter values are not required')
        for i in ids:
            assignments_client.delete_by_id(i)
        return
    if not any([ids, assignee, role, resource_group_name, scope, assignee, yes]):
        from knack.prompting import prompt_y_n
        msg = 'This will delete all role assignments under the subscription. Are you sure?'
        if not prompt_y_n(msg, default="n"):
            return

    scope = build_role_scope(resource_group_name, scope,
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
        hook.add(message='Waiting for AAD role to delete',
                 value=0.1 * x, total_val=1.0)
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
        assignee_object_id = resolve_object_id(cli_ctx, assignee)

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
            role_id = resolve_role_id(role, scope, definitions_client)
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


def subnet_role_assignment_exists(cli_ctx, scope):
    network_contributor_role_id = "4d97b98b-1d4f-4787-a291-c67834d212e7"

    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments

    for i in assignments_client.list_for_scope(scope=scope, filter='atScope()'):
        if i.scope == scope and i.role_definition_id.endswith(network_contributor_role_id):
            return True
    return False


_re_user_assigned_identity_resource_id = re.compile(
    r'/subscriptions/(.*?)/resourcegroups/(.*?)/providers/microsoft.managedidentity/userassignedidentities/(.*)',
    flags=re.IGNORECASE)


def _get_user_assigned_identity(cli_ctx, resource_id):
    resource_id = resource_id.lower()
    match = _re_user_assigned_identity_resource_id.search(resource_id)
    if match:
        subscription_id = match.group(1)
        resource_group_name = match.group(2)
        identity_name = match.group(3)
        msi_client = get_msi_client(cli_ctx, subscription_id)
        try:
            identity = msi_client.user_assigned_identities.get(resource_group_name=resource_group_name,
                                                               resource_name=identity_name)
        except CloudError as ex:
            if 'was not found' in ex.message:
                raise CLIError("Identity {} not found.".format(resource_id))
            raise CLIError(ex.message)
        return identity
    raise CLIError(
        "Cannot parse identity name from provided resource id {}.".format(resource_id))


def _get_user_assigned_identity_client_id(cli_ctx, resource_id):
    return _get_user_assigned_identity(cli_ctx, resource_id).client_id


def _get_user_assigned_identity_object_id(cli_ctx, resource_id):
    return _get_user_assigned_identity(cli_ctx, resource_id).principal_id


def _update_dict(dict1, dict2):
    cp = dict1.copy()
    cp.update(dict2)
    return cp


def aks_browse(cmd,     # pylint: disable=too-many-statements,too-many-branches
               client,
               resource_group_name,
               name,
               disable_browser=False,
               listen_address='127.0.0.1',
               listen_port='8001'):
    # verify the kube-dashboard addon was not disabled
    instance = client.get(resource_group_name, name)
    addon_profiles = instance.addon_profiles or {}
    # addon name is case insensitive
    addon_profile = next((addon_profiles[k] for k in addon_profiles
                          if k.lower() == CONST_KUBE_DASHBOARD_ADDON_NAME.lower()),
                         ManagedClusterAddonProfile(enabled=False))

    # open portal view if addon is not enabled or k8s version >= 1.19.0
    if StrictVersion(instance.kubernetes_version) >= StrictVersion('1.19.0') or (not addon_profile.enabled):
        subscription_id = get_subscription_id(cmd.cli_ctx)
        dashboardURL = (
            # Azure Portal URL (https://portal.azure.com for public cloud)
            cmd.cli_ctx.cloud.endpoints.portal +
            ('/#resource/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.ContainerService'
             '/managedClusters/{2}/workloads').format(subscription_id, resource_group_name, name)
        )

        if in_cloud_console():
            logger.warning(
                'To view the Kubernetes resources view, please open %s in a new tab', dashboardURL)
        else:
            logger.warning('Kubernetes resources view on %s', dashboardURL)

        if not disable_browser:
            webbrowser.open_new_tab(dashboardURL)
        return

    # otherwise open the kube-dashboard addon
    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')

    _, browse_path = tempfile.mkstemp()

    aks_get_credentials(cmd, client, resource_group_name,
                        name, admin=False, path=browse_path)
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
        response = requests.post(
            'http://localhost:8888/openport/{0}'.format(listen_port))
        result = json.loads(response.text)
        dashboardURL = '{0}api/v1/namespaces/kube-system/services/{1}:kubernetes-dashboard:/proxy/'.format(
            result['url'], protocol)
        term_id = os.environ.get('ACC_TERM_ID')
        if term_id:
            response = requests.post('http://localhost:8888/openLink/{0}'.format(term_id),
                                     json={"url": dashboardURL})
        logger.warning(
            'To view the console, please open %s in a new tab', dashboardURL)
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
                    logger.warning(
                        '"--address" is only supported in kubectl v1.13 and later.')
                    logger.warning(
                        'The "--listen-address" argument will be ignored.')
                subprocess.call(["kubectl", "--kubeconfig",
                                browse_path, "proxy", "--port", listen_port])
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


def aks_maintenanceconfiguration_list(
    cmd,
    client,
    resource_group_name,
    cluster_name
):
    return client.list_by_managed_cluster(resource_group_name, cluster_name)


def aks_maintenanceconfiguration_show(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    config_name
):
    logger.warning('resource_group_name: %s, cluster_name: %s, config_name: %s ',
                   resource_group_name, cluster_name, config_name)
    return client.get(resource_group_name, cluster_name, config_name)


def aks_maintenanceconfiguration_delete(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    config_name
):
    logger.warning('resource_group_name: %s, cluster_name: %s, config_name: %s ',
                   resource_group_name, cluster_name, config_name)
    return client.delete(resource_group_name, cluster_name, config_name)


def aks_maintenanceconfiguration_add(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    config_name,
    config_file,
    weekday,
    start_hour
):
    configs = client.list_by_managed_cluster(resource_group_name, cluster_name)
    for config in configs:
        if config.name == config_name:
            raise CLIError("Maintenance configuration '{}' already exists, please try a different name, "
                           "use 'aks maintenanceconfiguration list' to get current list of maitenance configurations".format(config_name))
    return aks_maintenanceconfiguration_update_internal(cmd, client, resource_group_name, cluster_name, config_name, config_file, weekday, start_hour)


def aks_maintenanceconfiguration_update(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    config_name,
    config_file,
    weekday,
    start_hour
):
    configs = client.list_by_managed_cluster(resource_group_name, cluster_name)
    found = False
    for config in configs:
        if config.name == config_name:
            found = True
            break
    if not found:
        raise CLIError("Maintenance configuration '{}' doesn't exist."
                       "use 'aks maintenanceconfiguration list' to get current list of maitenance configurations".format(config_name))

    return aks_maintenanceconfiguration_update_internal(cmd, client, resource_group_name, cluster_name, config_name, config_file, weekday, start_hour)


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
               enable_ahub=False,
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
               os_sku=None,
               enable_fips_image=False,
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
               nat_gateway_managed_outbound_ip_count=None,
               nat_gateway_idle_timeout=None,
               outbound_type=None,
               enable_addons=None,
               workspace_resource_id=None,
               enable_msi_auth_for_monitoring=False,
               min_count=None,
               max_count=None,
               vnet_subnet_id=None,
               pod_subnet_id=None,
               ppg=None,
               max_pods=0,
               aad_client_app_id=None,
               aad_server_app_id=None,
               aad_server_app_secret=None,
               aad_tenant_id=None,
               tags=None,
               node_zones=None,
               enable_node_public_ip=False,
               node_public_ip_prefix_id=None,
               generate_ssh_keys=False,  # pylint: disable=unused-argument
               enable_pod_security_policy=False,
               node_resource_group=None,
               uptime_sla=False,
               attach_acr=None,
               enable_private_cluster=False,
               private_dns_zone=None,
               enable_managed_identity=True,
               fqdn_subdomain=None,
               disable_public_fqdn=False,
               api_server_authorized_ip_ranges=None,
               aks_custom_headers=None,
               appgw_name=None,
               appgw_subnet_prefix=None,
               appgw_subnet_cidr=None,
               appgw_id=None,
               appgw_subnet_id=None,
               appgw_watch_namespace=None,
               enable_aad=False,
               enable_azure_rbac=False,
               aad_admin_group_object_ids=None,
               aci_subnet_name=None,
               enable_sgxquotehelper=False,
               kubelet_config=None,
               linux_os_config=None,
               http_proxy_config=None,
               assign_identity=None,
               auto_upgrade_channel=None,
               enable_pod_identity=False,
               enable_pod_identity_with_kubenet=False,
               enable_encryption_at_host=False,
               enable_ultra_ssd=False,
               enable_secret_rotation=False,
               disable_local_accounts=False,
               no_wait=False,
               assign_kubelet_identity=None,
               workload_runtime=None,
               gpu_instance_profile=None,
               yes=False):
    if not no_ssh_key:
        try:
            if not ssh_key_value or not is_valid_ssh_rsa_public_key(ssh_key_value):
                raise ValueError()
        except (TypeError, ValueError):
            shortened_key = truncate_text(ssh_key_value)
            raise CLIError(
                'Provided ssh key ({}) is invalid or non-existent'.format(shortened_key))

    subscription_id = get_subscription_id(cmd.cli_ctx)

    if dns_name_prefix and fqdn_subdomain:
        raise CLIError(
            '--dns-name-prefix and --fqdn-subdomain cannot be used at same time')
    if not dns_name_prefix and not fqdn_subdomain:
        dns_name_prefix = _get_default_dns_prefix(
            name, resource_group_name, subscription_id)

    rg_location = get_rg_location(cmd.cli_ctx, resource_group_name)
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
    load_balancer_sku = set_load_balancer_sku(
        load_balancer_sku, kubernetes_version)

    if api_server_authorized_ip_ranges and load_balancer_sku == "basic":
        raise CLIError(
            '--api-server-authorized-ip-ranges can only be used with standard load balancer')

    agent_pool_profile = ManagedClusterAgentPoolProfile(
        # Must be 12 chars or less before ACS RP adds to it
        name=_trim_nodepoolname(nodepool_name),
        tags=nodepool_tags,
        node_labels=nodepool_labels,
        count=int(node_count),
        vm_size=node_vm_size,
        os_type="Linux",
        os_sku=os_sku,
        mode="System",
        vnet_subnet_id=vnet_subnet_id,
        pod_subnet_id=pod_subnet_id,
        proximity_placement_group_id=ppg,
        availability_zones=node_zones,
        enable_node_public_ip=enable_node_public_ip,
        enable_fips=enable_fips_image,
        node_public_ip_prefix_id=node_public_ip_prefix_id,
        enable_encryption_at_host=enable_encryption_at_host,
        enable_ultra_ssd=enable_ultra_ssd,
        max_pods=int(max_pods) if max_pods else None,
        type=vm_set_type,
        workload_runtime=workload_runtime,
        gpu_instance_profile=gpu_instance_profile
    )

    if node_osdisk_size:
        agent_pool_profile.os_disk_size_gb = int(node_osdisk_size)

    if node_osdisk_type:
        agent_pool_profile.os_disk_type = node_osdisk_type

    _check_cluster_autoscaler_flag(
        enable_cluster_autoscaler, min_count, max_count, node_count, agent_pool_profile)

    if kubelet_config:
        agent_pool_profile.kubelet_config = _get_kubelet_config(kubelet_config)

    if linux_os_config:
        agent_pool_profile.linux_os_config = _get_linux_os_config(
            linux_os_config)

    linux_profile = None
    # LinuxProfile is just used for SSH access to VMs, so omit it if --no-ssh-key was specified.
    if not no_ssh_key:
        ssh_config = ContainerServiceSshConfiguration(
            public_keys=[ContainerServiceSshPublicKey(key_data=ssh_key_value)])
        linux_profile = ContainerServiceLinuxProfile(
            admin_username=admin_username, ssh=ssh_config)

    windows_profile = None

    if windows_admin_username:
        if windows_admin_password is None:
            try:
                windows_admin_password = prompt_pass(
                    msg='windows-admin-password: ', confirm=True)
            except NoTTYException:
                raise CLIError(
                    'Please specify both username and password in non-interactive mode.')

        windows_license_type = None
        if enable_ahub:
            windows_license_type = 'Windows_Server'

        windows_profile = ManagedClusterWindowsProfile(
            admin_username=windows_admin_username,
            admin_password=windows_admin_password,
            license_type=windows_license_type)

    service_principal_profile = None
    principal_obj = None
    # If customer explicitly provides a service principal, disable managed identity.
    if service_principal and client_secret:
        enable_managed_identity = False
    if not enable_managed_identity:
        principal_obj = _ensure_aks_service_principal(cmd.cli_ctx,
                                                      service_principal=service_principal, client_secret=client_secret,
                                                      subscription_id=subscription_id, dns_name_prefix=dns_name_prefix,
                                                      fqdn_subdomain=fqdn_subdomain, location=location, name=name)
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

    need_post_creation_vnet_permission_granting = False
    if (vnet_subnet_id and not skip_subnet_role_assignment and
            not subnet_role_assignment_exists(cmd.cli_ctx, vnet_subnet_id)):
        # if service_principal_profile is None, then this cluster is an MSI cluster,
        # and the service principal does not exist. Two cases:
        # 1. For system assigned identity, we just tell user to grant the
        # permission after the cluster is created to keep consistent with portal experience.
        # 2. For user assigned identity, we can grant needed permission to
        # user provided user assigned identity before creating managed cluster.
        if service_principal_profile is None and not assign_identity:
            msg = ('It is highly recommended to use USER assigned identity '
                   '(option --assign-identity) when you want to bring your own'
                   'subnet, which will have no latency for the role assignment to '
                   'take effect. When using SYSTEM assigned identity, '
                   'azure-cli will grant Network Contributor role to the '
                   'system assigned identity after the cluster is created, and '
                   'the role assignment will take some time to take effect, see '
                   'https://docs.microsoft.com/en-us/azure/aks/use-managed-identity, '
                   'proceed to create cluster with system assigned identity?')
            from knack.prompting import prompt_y_n
            if not yes and not prompt_y_n(msg, default="n"):
                return None
            need_post_creation_vnet_permission_granting = True
        else:
            scope = vnet_subnet_id
            identity_client_id = ""
            if assign_identity:
                identity_client_id = _get_user_assigned_identity_client_id(
                    cmd.cli_ctx, assign_identity)
            else:
                identity_client_id = service_principal_profile.client_id
            if not add_role_assignment(cmd.cli_ctx, 'Network Contributor',
                                       identity_client_id, scope=scope):
                logger.warning('Could not create a role assignment for subnet. '
                               'Are you an Owner on this subscription?')

    load_balancer_profile = create_load_balancer_profile(
        load_balancer_managed_outbound_ip_count,
        load_balancer_outbound_ips,
        load_balancer_outbound_ip_prefixes,
        load_balancer_outbound_ports,
        load_balancer_idle_timeout)

    nat_gateway_profile = create_nat_gateway_profile(
        nat_gateway_managed_outbound_ip_count,
        nat_gateway_idle_timeout)

    outbound_type = _set_outbound_type(
        outbound_type, vnet_subnet_id, load_balancer_sku, load_balancer_profile)

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
            raise CLIError(
                'Please use kubenet as the network plugin type when pod_cidr is specified')
        network_profile = ContainerServiceNetworkProfile(
            network_plugin=network_plugin,
            pod_cidr=pod_cidr,
            service_cidr=service_cidr,
            dns_service_ip=dns_service_ip,
            docker_bridge_cidr=docker_bridge_address,
            network_policy=network_policy,
            load_balancer_sku=load_balancer_sku.lower(),
            load_balancer_profile=load_balancer_profile,
            nat_gateway_profile=nat_gateway_profile,
            outbound_type=outbound_type
        )
    else:
        if load_balancer_sku.lower() == "standard" or load_balancer_profile or nat_gateway_profile:
            network_profile = ContainerServiceNetworkProfile(
                network_plugin="kubenet",
                load_balancer_sku=load_balancer_sku.lower(),
                load_balancer_profile=load_balancer_profile,
                nat_gateway_profile=nat_gateway_profile,
                outbound_type=outbound_type,
            )
        if load_balancer_sku.lower() == "basic":
            network_profile = ContainerServiceNetworkProfile(
                load_balancer_sku=load_balancer_sku.lower(),
            )

    addon_profiles = _handle_addons_args(
        cmd=cmd,
        addons_str=enable_addons,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        addon_profiles={},
        workspace_resource_id=workspace_resource_id,
        enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring,
        appgw_name=appgw_name,
        appgw_subnet_prefix=appgw_subnet_prefix,
        appgw_subnet_cidr=appgw_subnet_cidr,
        appgw_id=appgw_id,
        appgw_subnet_id=appgw_subnet_id,
        appgw_watch_namespace=appgw_watch_namespace,
        enable_sgxquotehelper=enable_sgxquotehelper,
        aci_subnet_name=aci_subnet_name,
        vnet_subnet_id=vnet_subnet_id,
        enable_secret_rotation=enable_secret_rotation,
    )
    monitoring = False
    if CONST_MONITORING_ADDON_NAME in addon_profiles:
        monitoring = True
        if enable_msi_auth_for_monitoring and not enable_managed_identity:
            raise ArgumentUsageError("--enable-msi-auth-for-monitoring can not be used on clusters with service principal auth.")
        ensure_container_insights_for_monitoring(cmd,
                                                 addon_profiles[CONST_MONITORING_ADDON_NAME], subscription_id,
                                                 resource_group_name, name, location,
                                                 aad_route=enable_msi_auth_for_monitoring, create_dcr=True,
                                                 create_dcra=False)

    # addon is in the list and is enabled
    ingress_appgw_addon_enabled = CONST_INGRESS_APPGW_ADDON_NAME in addon_profiles and \
        addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].enabled

    os_type = 'Linux'
    enable_virtual_node = False
    if CONST_VIRTUAL_NODE_ADDON_NAME + os_type in addon_profiles:
        enable_virtual_node = True

    aad_profile = None
    if enable_aad:
        if any([aad_client_app_id, aad_server_app_id, aad_server_app_secret]):
            raise CLIError('"--enable-aad" cannot be used together with '
                           '"--aad-client-app-id/--aad-server-app-id/--aad-server-app-secret"')
        if disable_rbac and enable_azure_rbac:
            raise CLIError(
                '"--enable-azure-rbac" can not be used together with "--disable-rbac"')
        aad_profile = ManagedClusterAADProfile(
            managed=True,
            enable_azure_rbac=enable_azure_rbac,
            # ids -> i_ds due to track 2 naming issue
            admin_group_object_i_ds=_parse_comma_separated_list(
                aad_admin_group_object_ids),
            tenant_id=aad_tenant_id
        )
    else:
        if aad_admin_group_object_ids is not None:
            raise CLIError(
                '"--admin-aad-object-id" can only be used together with "--enable-aad"')

        if enable_azure_rbac is True:
            raise CLIError(
                '"--enable-azure-rbac" can only be used together with "--enable-aad"')

        if any([aad_client_app_id, aad_server_app_id, aad_server_app_secret]):
            aad_profile = ManagedClusterAADProfile(
                client_app_id=aad_client_app_id,
                server_app_id=aad_server_app_id,
                server_app_secret=aad_server_app_secret,
                tenant_id=aad_tenant_id
            )

    # Check that both --disable-rbac and --enable-rbac weren't provided
    if all([disable_rbac, enable_rbac]):
        raise CLIError(
            'specify either "--disable-rbac" or "--enable-rbac", not both.')

    api_server_access_profile = None
    if api_server_authorized_ip_ranges:
        api_server_access_profile = _populate_api_server_access_profile(
            api_server_authorized_ip_ranges)

    identity = None
    if not enable_managed_identity and assign_identity:
        raise CLIError(
            '--assign-identity can only be specified when --enable-managed-identity is specified')
    if enable_managed_identity and not assign_identity:
        identity = ManagedClusterIdentity(
            type="SystemAssigned"
        )
    elif enable_managed_identity and assign_identity:
        user_assigned_identity = {
            assign_identity: ManagedServiceIdentityUserAssignedIdentitiesValue()
        }
        identity = ManagedClusterIdentity(
            type="UserAssigned",
            user_assigned_identities=user_assigned_identity
        )

    identity_profile = None
    if assign_kubelet_identity:
        if not assign_identity:
            raise CLIError('--assign-kubelet-identity can only be specified when --assign-identity is specified')
        kubelet_identity = _get_user_assigned_identity(cmd.cli_ctx, assign_kubelet_identity)
        identity_profile = {
            'kubeletidentity': UserAssignedIdentity(
                resource_id=assign_kubelet_identity,
                client_id=kubelet_identity.client_id,
                object_id=kubelet_identity.principal_id
            )
        }
        cluster_identity_object_id = _get_user_assigned_identity_object_id(cmd.cli_ctx, assign_identity)
        # ensure the cluster identity has "Managed Identity Operator" role at the scope of kubelet identity
        _ensure_cluster_identity_permission_on_kubelet_identity(cmd.cli_ctx, cluster_identity_object_id, assign_kubelet_identity)

    pod_identity_profile = None
    if enable_pod_identity:
        if not enable_managed_identity:
            raise CLIError(
                '--enable-pod-identity can only be specified when --enable-managed-identity is specified')
        pod_identity_profile = ManagedClusterPodIdentityProfile(enabled=True)
        _ensure_pod_identity_kubenet_consent(
            network_profile, pod_identity_profile, enable_pod_identity_with_kubenet)

    enable_rbac = True
    if disable_rbac:
        enable_rbac = False

    auto_upgrade_profile = None
    if auto_upgrade_channel is not None:
        auto_upgrade_profile = ManagedClusterAutoUpgradeProfile(
            upgrade_channel=auto_upgrade_channel)

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
        api_server_access_profile=api_server_access_profile,
        auto_upgrade_profile=auto_upgrade_profile,
        pod_identity_profile=pod_identity_profile,
        identity_profile=identity_profile,
        disable_local_accounts=bool(disable_local_accounts))

    if node_resource_group:
        mc.node_resource_group = node_resource_group

    use_custom_private_dns_zone = False
    if not enable_private_cluster and disable_public_fqdn:
        raise ArgumentUsageError("--disable_public_fqdn should only be used with --enable-private-cluster")
    if enable_private_cluster:
        if load_balancer_sku.lower() != "standard":
            raise ArgumentUsageError(
                "Please use standard load balancer for private cluster")
        mc.api_server_access_profile = ManagedClusterAPIServerAccessProfile(
            enable_private_cluster=True
        )
        if disable_public_fqdn:
            mc.api_server_access_profile.enable_private_cluster_public_fqdn = False

    if private_dns_zone:
        if not enable_private_cluster:
            raise ArgumentUsageError(
                "Invalid private dns zone for public cluster. It should always be empty for public cluster")
        mc.api_server_access_profile.private_dns_zone = private_dns_zone
        from msrestazure.tools import is_valid_resource_id
        if private_dns_zone.lower() != CONST_PRIVATE_DNS_ZONE_SYSTEM and private_dns_zone.lower() != CONST_PRIVATE_DNS_ZONE_NONE:
            if is_valid_resource_id(private_dns_zone):
                use_custom_private_dns_zone = True
            else:
                raise ResourceNotFoundError(private_dns_zone + " is not a valid Azure resource ID.")

    if fqdn_subdomain:
        if not use_custom_private_dns_zone:
            raise ArgumentUsageError(
                "--fqdn-subdomain should only be used for private cluster with custom private dns zone")
        mc.fqdn_subdomain = fqdn_subdomain

    if http_proxy_config:
        mc.http_proxy_config = _get_http_proxy_config(http_proxy_config)

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
            if monitoring and enable_msi_auth_for_monitoring:
                # Creating a DCR Association (for the monitoring addon) requires waiting for cluster creation to finish
                no_wait = False

            created_cluster = _put_managed_cluster_ensuring_permission(
                cmd,
                client,
                subscription_id,
                resource_group_name,
                name,
                mc,
                monitoring,
                ingress_appgw_addon_enabled,
                enable_virtual_node,
                need_post_creation_vnet_permission_granting,
                vnet_subnet_id,
                enable_managed_identity,
                attach_acr,
                headers,
                no_wait)

            if monitoring and enable_msi_auth_for_monitoring:
                # Create the DCR Association here
                ensure_container_insights_for_monitoring(cmd,
                                                         addon_profiles[CONST_MONITORING_ADDON_NAME], subscription_id,
                                                         resource_group_name, name, location,
                                                         aad_route=enable_msi_auth_for_monitoring, create_dcr=False,
                                                         create_dcra=True)

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
               nat_gateway_managed_outbound_ip_count=None,
               nat_gateway_idle_timeout=None,
               api_server_authorized_ip_ranges=None,
               enable_pod_security_policy=False,
               disable_pod_security_policy=False,
               attach_acr=None,
               detach_acr=None,
               uptime_sla=False,
               no_uptime_sla=False,
               enable_aad=False,
               aad_tenant_id=None,
               aad_admin_group_object_ids=None,
               enable_ahub=False,
               disable_ahub=False,
               aks_custom_headers=None,
               auto_upgrade_channel=None,
               enable_managed_identity=False,
               assign_identity=None,
               enable_pod_identity=False,
               enable_pod_identity_with_kubenet=False,
               disable_pod_identity=False,
               enable_secret_rotation=False,
               disable_secret_rotation=False,
               disable_local_accounts=False,
               enable_local_accounts=False,
               enable_public_fqdn=False,
               disable_public_fqdn=False,
               yes=False,
               tags=None,
               windows_admin_password=None,
               enable_azure_rbac=False,
               disable_azure_rbac=False):
    update_autoscaler = enable_cluster_autoscaler or disable_cluster_autoscaler or update_cluster_autoscaler
    update_acr = attach_acr is not None or detach_acr is not None
    update_pod_security = enable_pod_security_policy or disable_pod_security_policy
    update_lb_profile = is_load_balancer_profile_provided(load_balancer_managed_outbound_ip_count,
                                                          load_balancer_outbound_ips,
                                                          load_balancer_outbound_ip_prefixes,
                                                          load_balancer_outbound_ports,
                                                          load_balancer_idle_timeout)
    update_natgw_profile = is_nat_gateway_profile_provided(nat_gateway_managed_outbound_ip_count, nat_gateway_idle_timeout)
    update_aad_profile = not (
        aad_tenant_id is None and aad_admin_group_object_ids is None and not enable_azure_rbac and not disable_azure_rbac)
    # pylint: disable=too-many-boolean-expressions
    if not update_autoscaler and \
       cluster_autoscaler_profile is None and \
       not update_acr and \
       not update_lb_profile \
       and api_server_authorized_ip_ranges is None and \
       not update_pod_security and \
       not update_lb_profile and \
       not update_natgw_profile and \
       not uptime_sla and \
       not no_uptime_sla and \
       not enable_aad and \
       not update_aad_profile and  \
       not enable_ahub and  \
       not disable_ahub and \
       not auto_upgrade_channel and \
       not enable_managed_identity and \
       not assign_identity and \
       not enable_pod_identity and \
       not disable_pod_identity and \
       not enable_secret_rotation and \
       not disable_secret_rotation and \
       not tags and \
       not windows_admin_password and \
       not enable_local_accounts and \
       not disable_local_accounts and \
       not enable_public_fqdn and \
       not disable_public_fqdn:
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
                       '"--no-uptime-sla" or '
                       '"--load-balancer-managed-outbound-ip-count" or '
                       '"--load-balancer-outbound-ips" or '
                       '"--load-balancer-outbound-ip-prefixes" or '
                       '"--nat-gateway-managed-outbound-ip-count" or '
                       '"--nat-gateway-idle-timeout" or '
                       '"--enable-aad" or '
                       '"--aad-tenant-id" or '
                       '"--aad-admin-group-object-ids" or '
                       '"--enable-ahub" or '
                       '"--disable-ahub" or '
                       '"--enable-managed-identity" or '
                       '"--enable-pod-identity" or '
                       '"--disable-pod-identity" or '
                       '"--auto-upgrade-channel" or '
                       '"--enable-secret-rotation" or '
                       '"--disable-secret-rotation" or '
                       '"--tags" or '
                       '"--windows-admin-password" or '
                       '"--enable-azure-rbac" or '
                       '"--disable-azure-rbac" or '
                       '"--enable-local-accounts" or '
                       '"--disable-local-accounts" or '
                       '"--enable-public-fqdn" or '
                       '"--disable-public-fqdn"')
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
            raise CLIError(
                'value of min-count should be less than or equal to value of max-count.')

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
            logger.warning(
                'Cluster autoscaler is already disabled for this managed cluster.')
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

    if disable_local_accounts and enable_local_accounts:
        raise CLIError('Cannot specify --disable-local-accounts and --enable-local-accounts '
                       'at the same time.')

    if disable_local_accounts:
        instance.disable_local_accounts = True

    if enable_local_accounts:
        instance.disable_local_accounts = False

    if update_lb_profile:
        instance.network_profile.load_balancer_profile = update_load_balancer_profile(
            load_balancer_managed_outbound_ip_count,
            load_balancer_outbound_ips,
            load_balancer_outbound_ip_prefixes,
            load_balancer_outbound_ports,
            load_balancer_idle_timeout,
            instance.network_profile.load_balancer_profile)

    if update_natgw_profile:
        instance.network_profile.nat_gateway_profile = update_nat_gateway_profile(
            nat_gateway_managed_outbound_ip_count,
            nat_gateway_idle_timeout,
            instance.network_profile.nat_gateway_profile)

    if attach_acr and detach_acr:
        raise CLIError(
            'Cannot specify "--attach-acr" and "--detach-acr" at the same time.')

    if uptime_sla and no_uptime_sla:
        raise CLIError(
            'Cannot specify "--uptime-sla" and "--no-uptime-sla" at the same time.')

    if uptime_sla:
        instance.sku = ManagedClusterSKU(
            name="Basic",
            tier="Paid"
        )

    if no_uptime_sla:
        instance.sku = ManagedClusterSKU(
            name="Basic",
            tier="Free"
        )

    subscription_id = get_subscription_id(cmd.cli_ctx)
    client_id = ""
    if _is_msi_cluster(instance):
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
            _populate_api_server_access_profile(
                api_server_authorized_ip_ranges, instance)

    if enable_aad:
        if instance.aad_profile is not None and instance.aad_profile.managed:
            raise CLIError(
                'Cannot specify "--enable-aad" if managed AAD is already enabled')
        instance.aad_profile = ManagedClusterAADProfile(
            managed=True
        )
    if update_aad_profile:
        if instance.aad_profile is None or not instance.aad_profile.managed:
            raise CLIError('Cannot specify "--aad-tenant-id/--aad-admin-group-object-ids/--enable-azure-rbac/--disable-azure-rbac"'
                           ' if managed AAD is not enabled')
        if aad_tenant_id is not None:
            instance.aad_profile.tenant_id = aad_tenant_id
        if aad_admin_group_object_ids is not None:
            # ids -> i_ds due to track 2 naming issue
            instance.aad_profile.admin_group_object_i_ds = _parse_comma_separated_list(
                aad_admin_group_object_ids)
        if enable_azure_rbac and disable_azure_rbac:
            raise CLIError(
                'Cannot specify "--enable-azure-rbac" and "--disable-azure-rbac" at the same time')
        if enable_azure_rbac:
            instance.aad_profile.enable_azure_rbac = True
        if disable_azure_rbac:
            instance.aad_profile.enable_azure_rbac = False

    if enable_ahub and disable_ahub:
        raise CLIError(
            'Cannot specify "--enable-ahub" and "--disable-ahub" at the same time')

    if enable_ahub:
        instance.windows_profile.license_type = 'Windows_Server'
    if disable_ahub:
        instance.windows_profile.license_type = 'None'

    if enable_public_fqdn and disable_public_fqdn:
        raise MutuallyExclusiveArgumentError(
            'Cannot specify "--enable-public-fqdn" and "--disable-public-fqdn" at the same time')
    is_private_cluster = instance.api_server_access_profile is not None and instance.api_server_access_profile.enable_private_cluster
    if enable_public_fqdn:
        if not is_private_cluster:
            raise ArgumentUsageError('--enable-public-fqdn can only be used for private cluster')
        instance.api_server_access_profile.enable_private_cluster_public_fqdn = True
    if disable_public_fqdn:
        if not is_private_cluster:
            raise ArgumentUsageError('--disable-public-fqdn can only be used for private cluster')
        if instance.api_server_access_profile.private_dns_zone.lower() == CONST_PRIVATE_DNS_ZONE_NONE:
            raise ArgumentUsageError('--disable-public-fqdn cannot be applied for none mode private dns zone cluster')
        instance.api_server_access_profile.enable_private_cluster_public_fqdn = False

    if auto_upgrade_channel is not None:
        if instance.auto_upgrade_profile is None:
            instance.auto_upgrade_profile = ManagedClusterAutoUpgradeProfile()
        instance.auto_upgrade_profile.upgrade_channel = auto_upgrade_channel

    if not enable_managed_identity and assign_identity:
        raise CLIError(
            '--assign-identity can only be specified when --enable-managed-identity is specified')

    current_identity_type = "spn"
    if instance.identity is not None:
        current_identity_type = instance.identity.type.casefold()

    goal_identity_type = current_identity_type
    if enable_managed_identity:
        if not assign_identity:
            goal_identity_type = "systemassigned"
        else:
            goal_identity_type = "userassigned"

    if current_identity_type != goal_identity_type:
        from knack.prompting import prompt_y_n
        msg = ""
        if current_identity_type == "spn":
            msg = ('Your cluster is using service principal, and you are going to update the cluster to use {} managed identity.\n'
                   'After updating, your cluster\'s control plane and addon pods will switch to use managed identity, but kubelet '
                   'will KEEP USING SERVICE PRINCIPAL until you upgrade your agentpool.\n '
                   'Are you sure you want to perform this operation?').format(goal_identity_type)
        else:
            msg = ('Your cluster is already using {} managed identity, and you are going to update the cluster to use {} managed identity. \n'
                   'Are you sure you want to perform this operation?').format(current_identity_type, goal_identity_type)
        if not yes and not prompt_y_n(msg, default="n"):
            return None
        if goal_identity_type == "systemassigned":
            instance.identity = ManagedClusterIdentity(
                type="SystemAssigned"
            )
        elif goal_identity_type == "userassigned":
            user_assigned_identity = {
                assign_identity: ManagedServiceIdentityUserAssignedIdentitiesValue()
            }
            instance.identity = ManagedClusterIdentity(
                type="UserAssigned",
                user_assigned_identities=user_assigned_identity
            )

    if enable_pod_identity:
        if not _is_pod_identity_addon_enabled(instance):
            # we only rebuild the pod identity profile if it's disabled before
            _update_addon_pod_identity(
                instance, enable=True,
                allow_kubenet_consent=enable_pod_identity_with_kubenet,
            )

    if disable_pod_identity:
        _update_addon_pod_identity(instance, enable=False)

    azure_keyvault_secrets_provider_addon_profile = None
    monitoring_addon_enabled = False
    ingress_appgw_addon_enabled = False
    virtual_node_addon_enabled = False

    if instance.addon_profiles is not None:
        azure_keyvault_secrets_provider_addon_profile = instance.addon_profiles.get(CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME, None)
        azure_keyvault_secrets_provider_enabled = CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME in instance.addon_profiles and \
            instance.addon_profiles[CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME].enabled
        monitoring_addon_enabled = CONST_MONITORING_ADDON_NAME in instance.addon_profiles and \
            instance.addon_profiles[CONST_MONITORING_ADDON_NAME].enabled
        ingress_appgw_addon_enabled = CONST_INGRESS_APPGW_ADDON_NAME in instance.addon_profiles and \
            instance.addon_profiles[CONST_INGRESS_APPGW_ADDON_NAME].enabled
        virtual_node_addon_enabled = CONST_VIRTUAL_NODE_ADDON_NAME + 'Linux' in instance.addon_profiles and \
            instance.addon_profiles[CONST_VIRTUAL_NODE_ADDON_NAME + 'Linux'].enabled

    if enable_secret_rotation:
        if not azure_keyvault_secrets_provider_enabled:
            raise CLIError(
                '--enable-secret-rotation can only be specified when azure-keyvault-secrets-provider is enabled')
        azure_keyvault_secrets_provider_addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "true"

    if disable_secret_rotation:
        if not azure_keyvault_secrets_provider_enabled:
            raise CLIError(
                '--disable-secret-rotation can only be specified when azure-keyvault-secrets-provider is enabled')
        azure_keyvault_secrets_provider_addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "false"

    if tags:
        instance.tags = tags

    if windows_admin_password:
        instance.windows_profile.admin_password = windows_admin_password

    headers = get_aks_custom_headers(aks_custom_headers)

    return _put_managed_cluster_ensuring_permission(cmd,
                                                    client,
                                                    subscription_id,
                                                    resource_group_name,
                                                    name,
                                                    instance,
                                                    monitoring_addon_enabled,
                                                    ingress_appgw_addon_enabled,
                                                    virtual_node_addon_enabled,
                                                    False,
                                                    instance.agent_pool_profiles[0].vnet_subnet_id,
                                                    _is_msi_cluster(instance),
                                                    attach_acr,
                                                    headers,
                                                    no_wait)


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
                        path=os.path.join(os.path.expanduser(
                            '~'), '.kube', 'config'),
                        overwrite_existing=False,
                        context_name=None,
                        public_fqdn=False):
    credentialResults = None
    serverType = None
    if public_fqdn:
        serverType = 'public'
    if admin:
        credentialResults = client.list_cluster_admin_credentials(
            resource_group_name, name, serverType)
    else:
        if user.lower() == 'clusteruser':
            credentialResults = client.list_cluster_user_credentials(
                resource_group_name, name, serverType)
        elif user.lower() == 'clustermonitoringuser':
            credentialResults = client.list_cluster_monitoring_user_credentials(
                resource_group_name, name, serverType)
        else:
            raise CLIError("The user is invalid.")
    if not credentialResults:
        raise CLIError("No Kubernetes credentials found.")

    try:
        kubeconfig = credentialResults.kubeconfigs[0].value.decode(
            encoding='UTF-8')
        _print_or_merge_credentials(
            path, kubeconfig, overwrite_existing, context_name)
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
        storage_account_id = get_storage_account_from_diag_settings(
            cmd.cli_ctx, resource_group_name, name)
        if storage_account_id is None:
            raise CLIError(
                "A storage account must be specified, since there isn't one in the diagnostic settings.")

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
        storage_client = cf_storage(
            cmd.cli_ctx, parsed_storage_account['subscription'])
        storage_account_keys = storage_client.storage_accounts.list_keys(parsed_storage_account['resource_group'],
                                                                         storage_account_name)
        kwargs = {
            'account_name': storage_account_name,
            'account_key': storage_account_keys.keys[0].value
        }
        cloud_storage_client = cloud_storage_account_service_factory(
            cmd.cli_ctx, kwargs)

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
    aks_get_credentials(cmd, client, resource_group_name,
                        name, admin=True, path=temp_kubeconfig_path)

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
    aks_get_credentials(cmd, client, resource_group_name,
                        name, admin=True, path=temp_kubeconfig_path)

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
                raise CLIError(
                    "Cannot scale cluster autoscaler enabled node pool.")

            agent_profile.count = int(node_count)  # pylint: disable=no-member
            # null out the SP and AAD profile because otherwise validation complains
            instance.service_principal_profile = None
            instance.aad_profile = None
            return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, instance)
    raise CLIError('The nodepool "{}" was not found.'.format(nodepool_name))


def aks_upgrade(cmd,    # pylint: disable=unused-argument, too-many-return-statements
                client,
                resource_group_name,
                name,
                kubernetes_version='',
                control_plane_only=False,
                no_wait=False,
                node_image_only=False,
                aks_custom_headers=None,
                yes=False):
    from knack.prompting import prompt_y_n
    msg = 'Kubernetes may be unavailable during cluster upgrades.\n Are you sure you want to perform this operation?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None

    instance = client.get(resource_group_name, name)

    vmas_cluster = False
    for agent_profile in instance.agent_pool_profiles:
        if agent_profile.type.lower() == "availabilityset":
            vmas_cluster = True
            break

    if kubernetes_version != '' and node_image_only:
        raise CLIError('Conflicting flags. Upgrading the Kubernetes version will also upgrade node image version. '
                       'If you only want to upgrade the node version please use the "--node-image-only" option only.')

    if node_image_only:
        msg = "This node image upgrade operation will run across every node pool in the cluster " \
              "and might take a while. Do you wish to continue?"
        if not yes and not prompt_y_n(msg, default="n"):
            return None

        # This only provide convenience for customer at client side so they can run az aks upgrade to upgrade all
        # nodepools of a cluster. The SDK only support upgrade single nodepool at a time.
        for agent_pool_profile in instance.agent_pool_profiles:
            if vmas_cluster:
                raise CLIError('This cluster is not using VirtualMachineScaleSets. Node image upgrade only operation '
                               'can only be applied on VirtualMachineScaleSets cluster.')
            agent_pool_client = cf_agent_pools(cmd.cli_ctx)
            _upgrade_single_nodepool_image_version(
                True, agent_pool_client, resource_group_name, name, agent_pool_profile.name)
        mc = client.get(resource_group_name, name)
        return _remove_nulls([mc])[0]

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

    headers = get_aks_custom_headers(aks_custom_headers)

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, instance, headers=headers)


def _upgrade_single_nodepool_image_version(no_wait, client, resource_group_name, cluster_name, nodepool_name):
    return sdk_no_wait(no_wait, client.begin_upgrade_node_image_version, resource_group_name, cluster_name, nodepool_name)


def _handle_addons_args(cmd,  # pylint: disable=too-many-statements
                        addons_str,
                        subscription_id,
                        resource_group_name,
                        addon_profiles=None,
                        workspace_resource_id=None,
                        enable_msi_auth_for_monitoring=False,
                        appgw_name=None,
                        appgw_subnet_prefix=None,
                        appgw_subnet_cidr=None,
                        appgw_id=None,
                        appgw_subnet_id=None,
                        appgw_watch_namespace=None,
                        enable_sgxquotehelper=False,
                        aci_subnet_name=None,
                        vnet_subnet_id=None,
                        enable_secret_rotation=False):
    if not addon_profiles:
        addon_profiles = {}
    addons = addons_str.split(',') if addons_str else []
    if 'http_application_routing' in addons:
        addon_profiles[CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME] = ManagedClusterAddonProfile(
            enabled=True)
        addons.remove('http_application_routing')
    if 'kube-dashboard' in addons:
        addon_profiles[CONST_KUBE_DASHBOARD_ADDON_NAME] = ManagedClusterAddonProfile(
            enabled=True)
        addons.remove('kube-dashboard')
    # TODO: can we help the user find a workspace resource ID?
    if 'monitoring' in addons:
        if not workspace_resource_id:
            # use default workspace if exists else create default workspace
            workspace_resource_id = ensure_default_log_analytics_workspace_for_monitoring(
                cmd, subscription_id, resource_group_name)
        workspace_resource_id = sanitize_loganalytics_ws_resource_id(workspace_resource_id)
        addon_profiles[CONST_MONITORING_ADDON_NAME] = ManagedClusterAddonProfile(enabled=True,
                                                                                 config={CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID: workspace_resource_id,
                                                                                         CONST_MONITORING_USING_AAD_MSI_AUTH: enable_msi_auth_for_monitoring})
        addons.remove('monitoring')
    elif workspace_resource_id:
        raise CLIError(
            '"--workspace-resource-id" requires "--enable-addons monitoring".')
    if 'azure-policy' in addons:
        addon_profiles[CONST_AZURE_POLICY_ADDON_NAME] = ManagedClusterAddonProfile(
            enabled=True)
        addons.remove('azure-policy')
    if 'gitops' in addons:
        addon_profiles['gitops'] = ManagedClusterAddonProfile(enabled=True)
        addons.remove('gitops')
    if 'ingress-appgw' in addons:
        addon_profile = ManagedClusterAddonProfile(enabled=True, config={})
        if appgw_name is not None:
            addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME] = appgw_name
        if appgw_subnet_prefix is not None:
            addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_prefix
        if appgw_subnet_cidr is not None:
            addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_cidr
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
        addon_profiles[CONST_OPEN_SERVICE_MESH_ADDON_NAME] = addon_profile
        addons.remove('open-service-mesh')
    if 'azure-keyvault-secrets-provider' in addons:
        addon_profile = ManagedClusterAddonProfile(
            enabled=True, config={CONST_SECRET_ROTATION_ENABLED: "false"})
        if enable_secret_rotation:
            addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "true"
        addon_profiles[CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME] = addon_profile
        addons.remove('azure-keyvault-secrets-provider')
    if 'confcom' in addons:
        addon_profile = ManagedClusterAddonProfile(
            enabled=True, config={CONST_ACC_SGX_QUOTE_HELPER_ENABLED: "false"})
        if enable_sgxquotehelper:
            addon_profile.config[CONST_ACC_SGX_QUOTE_HELPER_ENABLED] = "true"
        addon_profiles[CONST_CONFCOM_ADDON_NAME] = addon_profile
        addons.remove('confcom')
    if 'virtual-node' in addons:
        if not aci_subnet_name or not vnet_subnet_id:
            raise CLIError(
                '"--enable-addons virtual-node" requires "--aci-subnet-name" and "--vnet-subnet-id".')
        # TODO: how about aciConnectorwindows, what is its addon name?
        os_type = 'Linux'
        addon_profiles[CONST_VIRTUAL_NODE_ADDON_NAME + os_type] = ManagedClusterAddonProfile(
            enabled=True,
            config={CONST_VIRTUAL_NODE_SUBNET_NAME: aci_subnet_name}
        )
        addons.remove('virtual-node')

    # error out if any (unrecognized) addons remain
    if addons:
        raise CLIError('"{}" {} not recognized by the --enable-addons argument.'.format(
            ",".join(addons), "are" if len(addons) > 1 else "is"))
    return addon_profiles


def _ensure_aks_service_principal(cli_ctx,
                                  service_principal=None,
                                  client_secret=None,
                                  subscription_id=None,
                                  dns_name_prefix=None,
                                  fqdn_subdomain=None,
                                  location=None,
                                  name=None):
    file_name_aks = 'aksServicePrincipal.json'
    # TODO: This really needs to be unit tested.
    rbac_client = get_graph_rbac_management_client(cli_ctx)
    if not service_principal:
        # --service-principal not specified, try to load it from local disk
        principal_obj = load_acs_service_principal(
            subscription_id, file_name=file_name_aks)
        if principal_obj:
            service_principal = principal_obj.get('service_principal')
            client_secret = principal_obj.get('client_secret')
        else:
            # Nothing to load, make one.
            if not client_secret:
                client_secret = _create_client_secret()
            salt = binascii.b2a_hex(os.urandom(3)).decode('utf-8')
            if dns_name_prefix:
                url = 'http://{}.{}.{}.cloudapp.azure.com'.format(
                    salt, dns_name_prefix, location)
            else:
                url = 'http://{}.{}.{}.cloudapp.azure.com'.format(
                    salt, fqdn_subdomain, location)

            service_principal = _build_service_principal(
                rbac_client, cli_ctx, name, url, client_secret)
            if not service_principal:
                raise CLIError('Could not create a service principal with the right permissions. '
                               'Are you an Owner on this project?')
            logger.info('Created a service principal: %s', service_principal)
            # We don't need to add role assignment for this created SPN
    else:
        # --service-principal specfied, validate --client-secret was too
        if not client_secret:
            raise CLIError(
                '--client-secret is required if --service-principal is specified')
    store_acs_service_principal(
        subscription_id, client_secret, service_principal, file_name=file_name_aks)
    return load_acs_service_principal(subscription_id, file_name=file_name_aks)


def _check_cluster_autoscaler_flag(enable_cluster_autoscaler,
                                   min_count,
                                   max_count,
                                   node_count,
                                   agent_pool_profile):
    if enable_cluster_autoscaler:
        if min_count is None or max_count is None:
            raise CLIError(
                'Please specify both min-count and max-count when --enable-cluster-autoscaler enabled')
        if int(min_count) > int(max_count):
            raise CLIError(
                'value of min-count should be less than or equal to value of max-count')
        if int(node_count) < int(min_count) or int(node_count) > int(max_count):
            raise CLIError(
                'node-count is not in the range of min-count and max-count')
        agent_pool_profile.min_count = int(min_count)
        agent_pool_profile.max_count = int(max_count)
        agent_pool_profile.enable_auto_scaling = True
    else:
        if min_count is not None or max_count is not None:
            raise CLIError(
                'min-count and max-count are required for --enable-cluster-autoscaler, please use the flag')


def _create_client_secret():
    # Add a special character to satsify AAD SP secret requirements
    special_char = '$'
    client_secret = binascii.b2a_hex(
        os.urandom(10)).decode('utf-8') + special_char
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
            acr_client = cf_container_registry_service(
                cli_ctx, subscription_id=parsed_registry['subscription'])
            registry = acr_client.registries.get(
                parsed_registry['resource_group'], parsed_registry['name'])
        except CloudError as ex:
            raise CLIError(ex.message)
        _ensure_aks_acr_role_assignment(
            cli_ctx, client_id, registry.id, detach)
        return

    # Check if the ACR exists by name accross all resource groups.
    registry_name = acr_name_or_id
    registry_resource = 'Microsoft.ContainerRegistry/registries'
    try:
        registry = get_resource_by_name(
            cli_ctx, registry_name, registry_resource)
    except CloudError as ex:
        if 'was not found' in ex.message:
            raise CLIError(
                "ACR {} not found. Have you provided the right ACR name?".format(registry_name))
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

    if not add_role_assignment(cli_ctx,
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
                      node_public_ip_prefix_id=None,
                      node_vm_size=None,
                      node_osdisk_type=None,
                      node_osdisk_size=0,
                      node_count=3,
                      vnet_subnet_id=None,
                      pod_subnet_id=None,
                      ppg=None,
                      max_pods=0,
                      os_type="Linux",
                      os_sku=None,
                      enable_fips_image=False,
                      min_count=None,
                      max_count=None,
                      enable_cluster_autoscaler=False,
                      scale_down_mode=CONST_SCALE_DOWN_MODE_DELETE,
                      node_taints=None,
                      priority=CONST_SCALE_SET_PRIORITY_REGULAR,
                      eviction_policy=CONST_SPOT_EVICTION_POLICY_DELETE,
                      spot_max_price=float('nan'),
                      labels=None,
                      max_surge=None,
                      mode="User",
                      aks_custom_headers=None,
                      kubelet_config=None,
                      linux_os_config=None,
                      enable_encryption_at_host=False,
                      enable_ultra_ssd=False,
                      workload_runtime=None,
                      gpu_instance_profile=None,
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
                raise CLIError(
                    'Taint does not match allowed values. Expect value such as "special=true:NoSchedule".')

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
        os_sku=os_sku,
        enable_fips=enable_fips_image,
        storage_profile=ContainerServiceStorageProfileTypes.managed_disks,
        vnet_subnet_id=vnet_subnet_id,
        pod_subnet_id=pod_subnet_id,
        proximity_placement_group_id=ppg,
        agent_pool_type="VirtualMachineScaleSets",
        max_pods=int(max_pods) if max_pods else None,
        orchestrator_version=kubernetes_version,
        availability_zones=node_zones,
        enable_node_public_ip=enable_node_public_ip,
        node_public_ip_prefix_id=node_public_ip_prefix_id,
        node_taints=taints_array,
        scale_set_priority=priority,
        scale_down_mode=scale_down_mode,
        upgrade_settings=upgradeSettings,
        enable_encryption_at_host=enable_encryption_at_host,
        enable_ultra_ssd=enable_ultra_ssd,
        mode=mode,
        workload_runtime=workload_runtime,
        gpu_instance_profile=gpu_instance_profile
    )

    if priority == CONST_SCALE_SET_PRIORITY_SPOT:
        agent_pool.scale_set_eviction_policy = eviction_policy
        if isnan(spot_max_price):
            spot_max_price = -1
        agent_pool.spot_max_price = spot_max_price

    _check_cluster_autoscaler_flag(
        enable_cluster_autoscaler, min_count, max_count, node_count, agent_pool)

    if node_osdisk_size:
        agent_pool.os_disk_size_gb = int(node_osdisk_size)

    if node_osdisk_type:
        agent_pool.os_disk_type = node_osdisk_type

    if kubelet_config:
        agent_pool.kubelet_config = _get_kubelet_config(kubelet_config)

    if linux_os_config:
        agent_pool.linux_os_config = _get_linux_os_config(linux_os_config)

    headers = get_aks_custom_headers(aks_custom_headers)
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, nodepool_name, agent_pool, headers=headers)


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
        raise CLIError(
            "The new node count is the same as the current node count.")
    instance.count = new_node_count  # pylint: disable=no-member
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


def aks_agentpool_upgrade(cmd,  # pylint: disable=unused-argument
                          client,
                          resource_group_name,
                          cluster_name,
                          nodepool_name,
                          kubernetes_version='',
                          no_wait=False,
                          node_image_only=False,
                          max_surge=None,
                          aks_custom_headers=None):
    if kubernetes_version != '' and node_image_only:
        raise CLIError('Conflicting flags. Upgrading the Kubernetes version will also upgrade node image version.'
                       'If you only want to upgrade the node version please use the "--node-image-only" option only.')

    if node_image_only:
        return _upgrade_single_nodepool_image_version(no_wait,
                                                      client,
                                                      resource_group_name,
                                                      cluster_name,
                                                      nodepool_name)

    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    instance.orchestrator_version = kubernetes_version

    if not instance.upgrade_settings:
        instance.upgrade_settings = AgentPoolUpgradeSettings()

    if max_surge:
        instance.upgrade_settings.max_surge = max_surge

    headers = get_aks_custom_headers(aks_custom_headers)

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, nodepool_name, instance, headers=headers)


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
                         scale_down_mode=None,
                         min_count=None, max_count=None,
                         max_surge=None,
                         mode=None,
                         no_wait=False):

    update_autoscaler = enable_cluster_autoscaler + \
        disable_cluster_autoscaler + update_cluster_autoscaler

    if (update_autoscaler != 1 and not tags and not scale_down_mode and not mode and not max_surge):
        raise CLIError('Please specify one or more of "--enable-cluster-autoscaler" or '
                       '"--disable-cluster-autoscaler" or '
                       '"--update-cluster-autoscaler" or '
                       '"--tags" or "--mode" or "--max-surge" or "--scale-down-mode"')

    instance = client.get(resource_group_name, cluster_name, nodepool_name)

    if min_count is None or max_count is None:
        if enable_cluster_autoscaler or update_cluster_autoscaler:
            raise CLIError('Please specify both min-count and max-count when --enable-cluster-autoscaler or '
                           '--update-cluster-autoscaler set.')
    if min_count is not None and max_count is not None:
        if int(min_count) > int(max_count):
            raise CLIError(
                'value of min-count should be less than or equal to value of max-count.')

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
            logger.warning(
                'Autoscaler is already disabled for this node pool.')
            return None
        instance.enable_auto_scaling = False
        instance.min_count = None
        instance.max_count = None

    instance.tags = tags

    if scale_down_mode is not None:
        instance.scale_down_mode = scale_down_mode

    if mode is not None:
        instance.mode = mode

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


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

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, cluster_name, nodepool_name)


def aks_addon_list_available():
    available_addons = []
    for k, v in ADDONS.items():
        available_addons.append({
            "name": k,
            "description": ADDONS_DESCRIPTIONS[v]
        })
    return available_addons


def aks_addon_list(cmd, client, resource_group_name, name):  # pylint: disable=unused-argument
    addon_profiles = client.get(resource_group_name, name).addon_profiles

    current_addons = []

    for name, addon in ADDONS.items():
        if not addon_profiles or addon not in addon_profiles:
            current_addons.append({
                "name": name,
                "api_key": addon,
                "enabled": False
            })
        else:
            current_addons.append({
                "name": name,
                "api_key": addon,
                "enabled": addon_profiles[addon].enabled
            })

    return current_addons


def aks_addon_show(cmd, client, resource_group_name, name, addon):  # pylint: disable=unused-argument
    addon_profiles = client.get(resource_group_name, name).addon_profiles
    addon_key = ADDONS[addon]

    if not addon_profiles or addon_key not in addon_profiles or not addon_profiles[addon_key].enabled:
        raise CLIError(f'Addon "{addon}" is not enabled in this cluster.')

    return {
        "name": addon,
        "api_key": addon_key,
        "config": addon_profiles[addon_key].config,
        "identity": addon_profiles[addon_key].identity
    }


def aks_addon_enable(cmd, client, resource_group_name, name, addon, workspace_resource_id=None,
                     subnet_name=None, appgw_name=None, appgw_subnet_prefix=None, appgw_subnet_cidr=None, appgw_id=None,
                     appgw_subnet_id=None,
                     appgw_watch_namespace=None, enable_sgxquotehelper=False, enable_secret_rotation=False,
                     no_wait=False, enable_msi_auth_for_monitoring=False):
    return enable_addons(cmd, client, resource_group_name, name, addon, workspace_resource_id=workspace_resource_id,
                         subnet_name=subnet_name, appgw_name=appgw_name, appgw_subnet_prefix=appgw_subnet_prefix,
                         appgw_subnet_cidr=appgw_subnet_cidr, appgw_id=appgw_id, appgw_subnet_id=appgw_subnet_id,
                         appgw_watch_namespace=appgw_watch_namespace, enable_sgxquotehelper=enable_sgxquotehelper,
                         enable_secret_rotation=enable_secret_rotation, no_wait=no_wait,
                         enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring)


def aks_addon_disable(cmd, client, resource_group_name, name, addon, no_wait=False):
    return aks_disable_addons(cmd, client, resource_group_name, name, addon, no_wait)


def aks_addon_update(cmd, client, resource_group_name, name, addon, workspace_resource_id=None,
                     subnet_name=None, appgw_name=None, appgw_subnet_prefix=None, appgw_subnet_cidr=None, appgw_id=None,
                     appgw_subnet_id=None,
                     appgw_watch_namespace=None, enable_sgxquotehelper=False, enable_secret_rotation=False,
                     no_wait=False, enable_msi_auth_for_monitoring=False):
    addon_profiles = client.get(resource_group_name, name).addon_profiles
    addon_key = ADDONS[addon]

    if not addon_profiles or addon_key not in addon_profiles or not addon_profiles[addon_key].enabled:
        raise CLIError(f'Addon "{addon}" is not enabled in this cluster.')

    return enable_addons(cmd, client, resource_group_name, name, addon, check_enabled=False,
                         workspace_resource_id=workspace_resource_id,
                         subnet_name=subnet_name, appgw_name=appgw_name, appgw_subnet_prefix=appgw_subnet_prefix,
                         appgw_subnet_cidr=appgw_subnet_cidr, appgw_id=appgw_id, appgw_subnet_id=appgw_subnet_id,
                         appgw_watch_namespace=appgw_watch_namespace, enable_sgxquotehelper=enable_sgxquotehelper,
                         enable_secret_rotation=enable_secret_rotation, no_wait=no_wait,
                         enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring)


def aks_disable_addons(cmd, client, resource_group_name, name, addons, no_wait=False):
    instance = client.get(resource_group_name, name)
    subscription_id = get_subscription_id(cmd.cli_ctx)

    try:
        if addons == "monitoring" and CONST_MONITORING_ADDON_NAME in instance.addon_profiles and \
                instance.addon_profiles[CONST_MONITORING_ADDON_NAME].enabled and \
                CONST_MONITORING_USING_AAD_MSI_AUTH in instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config and \
                str(instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config[CONST_MONITORING_USING_AAD_MSI_AUTH]).lower() == 'true':
            # remove the DCR association because otherwise the DCR can't be deleted
            ensure_container_insights_for_monitoring(
                cmd,
                instance.addon_profiles[CONST_MONITORING_ADDON_NAME],
                subscription_id,
                resource_group_name,
                name,
                instance.location,
                remove_monitoring=True,
                aad_route=True,
                create_dcr=False,
                create_dcra=True
            )
    except TypeError:
        pass

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
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, instance)


def aks_enable_addons(cmd, client, resource_group_name, name, addons, workspace_resource_id=None,
                      subnet_name=None, appgw_name=None, appgw_subnet_prefix=None, appgw_subnet_cidr=None, appgw_id=None, appgw_subnet_id=None,
                      appgw_watch_namespace=None, enable_sgxquotehelper=False, enable_secret_rotation=False, no_wait=False, enable_msi_auth_for_monitoring=False):

    instance = client.get(resource_group_name, name)
    msi_auth = True if instance.service_principal_profile.client_id == "msi" else False  # this is overwritten by _update_addons(), so the value needs to be recorded here

    subscription_id = get_subscription_id(cmd.cli_ctx)
    instance = _update_addons(cmd, instance, subscription_id, resource_group_name, name, addons, enable=True,
                              workspace_resource_id=workspace_resource_id, enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring, subnet_name=subnet_name,
                              appgw_name=appgw_name, appgw_subnet_prefix=appgw_subnet_prefix, appgw_subnet_cidr=appgw_subnet_cidr, appgw_id=appgw_id, appgw_subnet_id=appgw_subnet_id, appgw_watch_namespace=appgw_watch_namespace,
                              enable_sgxquotehelper=enable_sgxquotehelper, enable_secret_rotation=enable_secret_rotation, no_wait=no_wait)

    if CONST_MONITORING_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[CONST_MONITORING_ADDON_NAME].enabled:
        if CONST_MONITORING_USING_AAD_MSI_AUTH in instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config and \
                str(instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config[CONST_MONITORING_USING_AAD_MSI_AUTH]).lower() == 'true':
            if not msi_auth:
                raise ArgumentUsageError("--enable-msi-auth-for-monitoring can not be used on clusters with service principal auth.")
            else:
                # create a Data Collection Rule (DCR) and associate it with the cluster
                ensure_container_insights_for_monitoring(cmd, instance.addon_profiles[CONST_MONITORING_ADDON_NAME], subscription_id, resource_group_name, name, instance.location, aad_route=True, create_dcr=True, create_dcra=True)
        else:
            # monitoring addon will use legacy path
            ensure_container_insights_for_monitoring(cmd, instance.addon_profiles[CONST_MONITORING_ADDON_NAME], subscription_id, resource_group_name, name, instance.location, aad_route=False)

    monitoring = CONST_MONITORING_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[
        CONST_MONITORING_ADDON_NAME].enabled
    ingress_appgw_addon_enabled = CONST_INGRESS_APPGW_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[
        CONST_INGRESS_APPGW_ADDON_NAME].enabled

    os_type = 'Linux'
    enable_virtual_node = False
    if CONST_VIRTUAL_NODE_ADDON_NAME + os_type in instance.addon_profiles:
        enable_virtual_node = True

    need_post_creation_role_assignment = monitoring or ingress_appgw_addon_enabled or enable_virtual_node
    if need_post_creation_role_assignment:
        # adding a wait here since we rely on the result for role assignment
        result = LongRunningOperation(cmd.cli_ctx)(
            client.begin_create_or_update(resource_group_name, name, instance))
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
            add_monitoring_role_assignment(result, cluster_resource_id, cmd)
        if ingress_appgw_addon_enabled:
            add_ingress_appgw_addon_role_assignment(result, cmd)
        if enable_virtual_node:
            # All agent pool will reside in the same vnet, we will grant vnet level Contributor role
            # in later function, so using a random agent pool here is OK
            random_agent_pool = result.agent_pool_profiles[0]
            if random_agent_pool.vnet_subnet_id != "":
                add_virtual_node_role_assignment(
                    cmd, result, random_agent_pool.vnet_subnet_id)
            # Else, the cluster is not using custom VNet, the permission is already granted in AKS RP,
            # we don't need to handle it in client side in this case.

    else:
        result = sdk_no_wait(no_wait, client.begin_create_or_update,
                             resource_group_name, name, instance)
    return result


def aks_rotate_certs(cmd, client, resource_group_name, name, no_wait=True):     # pylint: disable=unused-argument
    return sdk_no_wait(no_wait, client.begin_rotate_cluster_certificates, resource_group_name, name)


def _update_addons(cmd,  # pylint: disable=too-many-branches,too-many-statements
                   instance,
                   subscription_id,
                   resource_group_name,
                   name,
                   addons,
                   enable,
                   workspace_resource_id=None,
                   enable_msi_auth_for_monitoring=False,
                   subnet_name=None,
                   appgw_name=None,
                   appgw_subnet_prefix=None,
                   appgw_subnet_cidr=None,
                   appgw_id=None,
                   appgw_subnet_id=None,
                   appgw_watch_namespace=None,
                   enable_sgxquotehelper=False,
                   enable_secret_rotation=False,
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
        if addon == CONST_VIRTUAL_NODE_ADDON_NAME:
            # only linux is supported for now, in the future this will be a user flag
            addon += os_type

        # honor addon names defined in Azure CLI
        for key in list(addon_profiles):
            if key.lower() == addon.lower() and key != addon:
                addon_profiles[addon] = addon_profiles.pop(key)

        if enable:
            # add new addons or update existing ones and enable them
            addon_profile = addon_profiles.get(
                addon, ManagedClusterAddonProfile(enabled=False))
            # special config handling for certain addons
            if addon == CONST_MONITORING_ADDON_NAME:
                logAnalyticsConstName = CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID
                if addon_profile.enabled:
                    raise CLIError('The monitoring addon is already enabled for this managed cluster.\n'
                                   'To change monitoring configuration, run "az aks disable-addons -a monitoring"'
                                   'before enabling it again.')
                if not workspace_resource_id:
                    workspace_resource_id = ensure_default_log_analytics_workspace_for_monitoring(
                        cmd,
                        subscription_id,
                        resource_group_name)
                workspace_resource_id = sanitize_loganalytics_ws_resource_id(workspace_resource_id)

                addon_profile.config = {logAnalyticsConstName: workspace_resource_id}
                addon_profile.config[CONST_MONITORING_USING_AAD_MSI_AUTH] = enable_msi_auth_for_monitoring
            elif addon == (CONST_VIRTUAL_NODE_ADDON_NAME + os_type):
                if addon_profile.enabled:
                    raise CLIError('The virtual-node addon is already enabled for this managed cluster.\n'
                                   'To change virtual-node configuration, run '
                                   '"az aks disable-addons -a virtual-node -g {resource_group_name}" '
                                   'before enabling it again.')
                if not subnet_name:
                    raise CLIError(
                        'The aci-connector addon requires setting a subnet name.')
                addon_profile.config = {
                    CONST_VIRTUAL_NODE_SUBNET_NAME: subnet_name}
            elif addon == CONST_INGRESS_APPGW_ADDON_NAME:
                if addon_profile.enabled:
                    raise CLIError('The ingress-appgw addon is already enabled for this managed cluster.\n'
                                   'To change ingress-appgw configuration, run '
                                   f'"az aks disable-addons -a ingress-appgw -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={})
                if appgw_name is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME] = appgw_name
                if appgw_subnet_prefix is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_prefix
                if appgw_subnet_cidr is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_CIDR] = appgw_subnet_cidr
                if appgw_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID] = appgw_id
                if appgw_subnet_id is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_SUBNET_ID] = appgw_subnet_id
                if appgw_watch_namespace is not None:
                    addon_profile.config[CONST_INGRESS_APPGW_WATCH_NAMESPACE] = appgw_watch_namespace
            elif addon == CONST_OPEN_SERVICE_MESH_ADDON_NAME:
                if addon_profile.enabled:
                    raise CLIError('The open-service-mesh addon is already enabled for this managed cluster.\n'
                                   'To change open-service-mesh configuration, run '
                                   f'"az aks disable-addons -a open-service-mesh -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={})
            elif addon == CONST_CONFCOM_ADDON_NAME:
                if addon_profile.enabled:
                    raise CLIError('The confcom addon is already enabled for this managed cluster.\n'
                                   'To change confcom configuration, run '
                                   f'"az aks disable-addons -a confcom -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={CONST_ACC_SGX_QUOTE_HELPER_ENABLED: "false"})
                if enable_sgxquotehelper:
                    addon_profile.config[CONST_ACC_SGX_QUOTE_HELPER_ENABLED] = "true"
            elif addon == CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME:
                if addon_profile.enabled:
                    raise CLIError('The azure-keyvault-secrets-provider addon is already enabled for this managed cluster.\n'
                                   'To change azure-keyvault-secrets-provider configuration, run '
                                   f'"az aks disable-addons -a azure-keyvault-secrets-provider -n {name} -g {resource_group_name}" '
                                   'before enabling it again.')
                addon_profile = ManagedClusterAddonProfile(
                    enabled=True, config={CONST_SECRET_ROTATION_ENABLED: "false"})
                if enable_secret_rotation:
                    addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "true"
                addon_profiles[CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME] = addon_profile
            addon_profiles[addon] = addon_profile
        else:
            if addon not in addon_profiles:
                if addon == CONST_KUBE_DASHBOARD_ADDON_NAME:
                    addon_profiles[addon] = ManagedClusterAddonProfile(
                        enabled=False)
                else:
                    raise CLIError(
                        "The addon {} is not installed.".format(addon))
            addon_profiles[addon].config = None
        addon_profiles[addon].enabled = enable

    instance.addon_profiles = addon_profiles

    # null out the SP and AAD profile because otherwise validation complains
    instance.service_principal_profile = None
    instance.aad_profile = None

    return instance


def aks_get_versions(cmd, client, location):    # pylint: disable=unused-argument
    return client.list_orchestrators(location, resource_type='managedClusters')


def aks_get_os_options(cmd, client, location):    # pylint: disable=unused-argument
    return client.get_os_options(location, resource_type='managedClusters')


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
        merge_kubernetes_configurations(
            path, temp_path, overwrite_existing, context_name)
    except yaml.YAMLError as ex:
        logger.warning(
            'Failed to merge credentials to kube config file: %s', ex)
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
        raise CLIError(
            'failed to load additional configuration from {}'.format(addition_file))

    if existing is None:
        existing = addition
    else:
        _handle_merge(existing, addition, 'clusters', replace)
        _handle_merge(existing, addition, 'users', replace)
        _handle_merge(existing, addition, 'contexts', replace)
        existing['current-context'] = addition['current-context']

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != 'Windows':
        existing_file_perms = "{:o}".format(
            stat.S_IMODE(os.lstat(existing_file).st_mode))
        if not existing_file_perms.endswith('600'):
            logger.warning('%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                           existing_file, existing_file_perms)

    with open(existing_file, 'w+') as stream:
        yaml.safe_dump(existing, stream, default_flow_style=False)

    current_context = addition.get('current-context', 'UNKNOWN')
    msg = 'Merged "{}" as current context in {}'.format(
        current_context, existing_file)
    print(msg)


def cloud_storage_account_service_factory(cli_ctx, kwargs):
    from azure.cli.core.profiles import ResourceType, get_sdk
    t_cloud_storage_account = get_sdk(
        cli_ctx, ResourceType.DATA_STORAGE, 'common#CloudStorageAccount')
    account_name = kwargs.pop('account_name', None)
    account_key = kwargs.pop('account_key', None)
    sas_token = kwargs.pop('sas_token', None)
    kwargs.pop('connection_string', None)
    return t_cloud_storage_account(account_name, account_key, sas_token)


def get_storage_account_from_diag_settings(cli_ctx, resource_group_name, name):
    from azure.mgmt.monitor import MonitorManagementClient
    diag_settings_client = get_mgmt_service_client(
        cli_ctx, MonitorManagementClient).diagnostic_settings
    subscription_id = get_subscription_id(cli_ctx)
    aks_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.ContainerService' \
        '/managedClusters/{2}'.format(subscription_id,
                                      resource_group_name, name)
    diag_settings = diag_settings_client.list(aks_resource_id)
    if diag_settings.value:
        return diag_settings.value[0].storage_account_id

    print("No diag settings specified")
    return None


def display_diagnostics_report(temp_kubeconfig_path):   # pylint: disable=too-many-statements
    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')

    nodes = subprocess.check_output(
        ["kubectl", "--kubeconfig", temp_kubeconfig_path,
            "get", "node", "--no-headers"],
        universal_newlines=True)
    logger.debug(nodes)
    node_lines = nodes.splitlines()
    ready_nodes = {}
    for node_line in node_lines:
        columns = node_line.split()
        logger.debug(node_line)
        if columns[1] != "Ready":
            logger.warning(
                "Node %s is not Ready. Current state is: %s.", columns[0], columns[1])
        else:
            ready_nodes[columns[0]] = False

    logger.debug('There are %s ready nodes in the cluster',
                 str(len(ready_nodes)))

    if not ready_nodes:
        logger.warning(
            'No nodes are ready in the current cluster. Diagnostics info might not be available.')

    network_config_array = []
    network_status_array = []
    apds_created = False

    max_retry = 10
    for retry in range(0, max_retry):
        if not apds_created:
            apd = subprocess.check_output(
                ["kubectl", "--kubeconfig", temp_kubeconfig_path, "get",
                    "apd", "-n", "aks-periscope", "--no-headers"],
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
                    logger.debug('Dns status for node %s is %s',
                                 node_name, network_config)
                    network_status = subprocess.check_output(
                        ["kubectl", "--kubeconfig", temp_kubeconfig_path,
                         "get", "apd", apdName, "-n",
                         "aks-periscope", "-o=jsonpath={.spec.networkoutbound}"],
                        universal_newlines=True)
                    logger.debug('Network status for node %s is %s',
                                 node_name, network_status)

                    if not network_config or not network_status:
                        print("The diagnostics information for node {} is not ready yet. "
                              "Will try again in 10 seconds.".format(node_name))
                        time.sleep(10)
                        break

                    network_config_array += json.loads(
                        '[' + network_config + ']')
                    network_status_object = json.loads(network_status)
                    network_status_array += format_diag_status(
                        network_status_object)
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


def _put_managed_cluster_ensuring_permission(
    cmd,     # pylint: disable=too-many-locals,too-many-statements,too-many-branches
    client,
    subscription_id,
    resource_group_name,
    name,
    managed_cluster,
    monitoring_addon_enabled,
    ingress_appgw_addon_enabled,
    virtual_node_addon_enabled,
    need_grant_vnet_permission_to_cluster_identity,
    vnet_subnet_id,
    enable_managed_identity,
    attach_acr,
    headers,
    no_wait
):
    # some addons require post cluster creation role assigment
    need_post_creation_role_assignment = (monitoring_addon_enabled or
                                          ingress_appgw_addon_enabled or
                                          (enable_managed_identity and attach_acr) or
                                          virtual_node_addon_enabled or
                                          need_grant_vnet_permission_to_cluster_identity)
    if need_post_creation_role_assignment:
        # adding a wait here since we rely on the result for role assignment
        cluster = LongRunningOperation(cmd.cli_ctx)(client.begin_create_or_update(
            resource_group_name=resource_group_name,
            resource_name=name,
            parameters=managed_cluster,
            headers=headers))
        cloud_name = cmd.cli_ctx.cloud.name
        # add cluster spn/msi Monitoring Metrics Publisher role assignment to publish metrics to MDM
        # mdm metrics is supported only in azure public cloud, so add the role assignment only in this cloud
        if monitoring_addon_enabled and cloud_name.lower() == 'azurecloud':
            from msrestazure.tools import resource_id
            cluster_resource_id = resource_id(
                subscription=subscription_id,
                resource_group=resource_group_name,
                namespace='Microsoft.ContainerService', type='managedClusters',
                name=name
            )
            add_monitoring_role_assignment(cluster, cluster_resource_id, cmd)
        if ingress_appgw_addon_enabled:
            add_ingress_appgw_addon_role_assignment(cluster, cmd)
        if virtual_node_addon_enabled:
            add_virtual_node_role_assignment(cmd, cluster, vnet_subnet_id)
        if need_grant_vnet_permission_to_cluster_identity:
            if not create_role_assignment(cmd.cli_ctx, 'Network Contributor',
                                          cluster.identity.principal_id, scope=vnet_subnet_id,
                                          resolve_assignee=False):
                logger.warning('Could not create a role assignment for subnet. '
                               'Are you an Owner on this subscription?')

        if enable_managed_identity and attach_acr:
            # Attach ACR to cluster enabled managed identity
            if cluster.identity_profile is None or \
               cluster.identity_profile["kubeletidentity"] is None:
                logger.warning('Your cluster is successfully created, but we failed to attach '
                               'acr to it, you can manually grant permission to the identity '
                               'named <ClUSTER_NAME>-agentpool in MC_ resource group to give '
                               'it permission to pull from ACR.')
            else:
                kubelet_identity_client_id = cluster.identity_profile["kubeletidentity"].client_id
                _ensure_aks_acr(cmd.cli_ctx,
                                client_id=kubelet_identity_client_id,
                                acr_name_or_id=attach_acr,
                                subscription_id=subscription_id)
    else:
        cluster = sdk_no_wait(no_wait, client.begin_create_or_update,
                              resource_group_name=resource_group_name,
                              resource_name=name,
                              parameters=managed_cluster,
                              headers=headers)

    return cluster


def _is_msi_cluster(managed_cluster):
    return (managed_cluster and managed_cluster.identity and
            (managed_cluster.identity.type.casefold() == "systemassigned" or managed_cluster.identity.type.casefold() == "userassigned"))


def _get_kubelet_config(file_path):
    if not os.path.isfile(file_path):
        raise CLIError("{} is not valid file, or not accessable.".format(file_path))
    kubelet_config = get_file_json(file_path)
    if not isinstance(kubelet_config, dict):
        raise CLIError(
            "Error reading kubelet configuration at {}. Please see https://aka.ms/CustomNodeConfig for correct format.".format(file_path))
    config_object = KubeletConfig()
    config_object.cpu_manager_policy = kubelet_config.get(
        "cpuManagerPolicy", None)
    config_object.cpu_cfs_quota = kubelet_config.get("cpuCfsQuota", None)
    config_object.cpu_cfs_quota_period = kubelet_config.get(
        "cpuCfsQuotaPeriod", None)
    config_object.image_gc_high_threshold = kubelet_config.get(
        "imageGcHighThreshold", None)
    config_object.image_gc_low_threshold = kubelet_config.get(
        "imageGcLowThreshold", None)
    config_object.topology_manager_policy = kubelet_config.get(
        "topologyManagerPolicy", None)
    config_object.allowed_unsafe_sysctls = kubelet_config.get(
        "allowedUnsafeSysctls", None)
    config_object.fail_swap_on = kubelet_config.get("failSwapOn", None)
    config_object.container_log_max_files = kubelet_config.get(
        "containerLogMaxFiles", None)
    config_object.container_log_max_size_mb = kubelet_config.get(
        "containerLogMaxSizeMB", None)
    config_object.pod_max_pids = kubelet_config.get(
        "podMaxPids", None)

    return config_object


def _get_linux_os_config(file_path):
    if not os.path.isfile(file_path):
        raise CLIError("{} is not valid file, or not accessable.".format(file_path))
    os_config = get_file_json(file_path)
    if not isinstance(os_config, dict):
        raise CLIError(
            "Error reading Linux OS configuration at {}. Please see https://aka.ms/CustomNodeConfig for correct format.".format(file_path))
    config_object = LinuxOSConfig()
    config_object.transparent_huge_page_enabled = os_config.get(
        "transparentHugePageEnabled", None)
    config_object.transparent_huge_page_defrag = os_config.get(
        "transparentHugePageDefrag", None)
    config_object.swap_file_size_mb = os_config.get("swapFileSizeMB", None)
    # sysctl settings
    sysctls = os_config.get("sysctls", None)
    if not isinstance(sysctls, dict):
        raise CLIError(
            "Error reading Sysctl settings at {}. Please see https://aka.ms/CustomNodeConfig for correct format.".format(file_path))
    config_object.sysctls = SysctlConfig()
    config_object.sysctls.net_core_somaxconn = sysctls.get(
        "netCoreSomaxconn", None)
    config_object.sysctls.net_core_netdev_max_backlog = sysctls.get(
        "netCoreNetdevMaxBacklog", None)
    config_object.sysctls.net_core_rmem_max = sysctls.get(
        "netCoreRmemMax", None)
    config_object.sysctls.net_core_wmem_max = sysctls.get(
        "netCoreWmemMax", None)
    config_object.sysctls.net_core_optmem_max = sysctls.get(
        "netCoreOptmemMax", None)
    config_object.sysctls.net_ipv4_tcp_max_syn_backlog = sysctls.get(
        "netIpv4TcpMaxSynBacklog", None)
    config_object.sysctls.net_ipv4_tcp_max_tw_buckets = sysctls.get(
        "netIpv4TcpMaxTwBuckets", None)
    config_object.sysctls.net_ipv4_tcp_fin_timeout = sysctls.get(
        "netIpv4TcpFinTimeout", None)
    config_object.sysctls.net_ipv4_tcp_keepalive_time = sysctls.get(
        "netIpv4TcpKeepaliveTime", None)
    config_object.sysctls.net_ipv4_tcp_keepalive_probes = sysctls.get(
        "netIpv4TcpKeepaliveProbes", None)
    config_object.sysctls.net_ipv4_tcpkeepalive_intvl = sysctls.get(
        "netIpv4TcpkeepaliveIntvl", None)
    config_object.sysctls.net_ipv4_tcp_rmem = sysctls.get(
        "netIpv4TcpRmem", None)
    config_object.sysctls.net_ipv4_tcp_wmem = sysctls.get(
        "netIpv4TcpWmem", None)
    config_object.sysctls.net_ipv4_tcp_tw_reuse = sysctls.get(
        "netIpv4TcpTwReuse", None)
    config_object.sysctls.net_ipv4_ip_local_port_range = sysctls.get(
        "netIpv4IpLocalPortRange", None)
    config_object.sysctls.net_ipv4_neigh_default_gc_thresh1 = sysctls.get(
        "netIpv4NeighDefaultGcThresh1", None)
    config_object.sysctls.net_ipv4_neigh_default_gc_thresh2 = sysctls.get(
        "netIpv4NeighDefaultGcThresh2", None)
    config_object.sysctls.net_ipv4_neigh_default_gc_thresh3 = sysctls.get(
        "netIpv4NeighDefaultGcThresh3", None)
    config_object.sysctls.net_netfilter_nf_conntrack_max = sysctls.get(
        "netNetfilterNfConntrackMax", None)
    config_object.sysctls.net_netfilter_nf_conntrack_buckets = sysctls.get(
        "netNetfilterNfConntrackBuckets", None)
    config_object.sysctls.fs_inotify_max_user_watches = sysctls.get(
        "fsInotifyMaxUserWatches", None)
    config_object.sysctls.fs_file_max = sysctls.get("fsFileMax", None)
    config_object.sysctls.fs_aio_max_nr = sysctls.get("fsAioMaxNr", None)
    config_object.sysctls.fs_nr_open = sysctls.get("fsNrOpen", None)
    config_object.sysctls.kernel_threads_max = sysctls.get(
        "kernelThreadsMax", None)
    config_object.sysctls.vm_max_map_count = sysctls.get("vmMaxMapCount", None)
    config_object.sysctls.vm_swappiness = sysctls.get("vmSwappiness", None)
    config_object.sysctls.vm_vfs_cache_pressure = sysctls.get(
        "vmVfsCachePressure", None)

    return config_object


def _get_http_proxy_config(file_path):
    if not os.path.isfile(file_path):
        raise CLIError("{} is not valid file, or not accessable.".format(file_path))
    hp_config = get_file_json(file_path)
    if not isinstance(hp_config, dict):
        raise CLIError(
            "Error reading Http Proxy Config at {}. Please see https://aka.ms/HttpProxyConfig for correct format.".format(file_path))
    config_object = ManagedClusterHTTPProxyConfig()
    config_object.http_proxy = hp_config.get("httpProxy", None)
    config_object.https_proxy = hp_config.get("httpsProxy", None)
    config_object.no_proxy = hp_config.get("noProxy", None)
    config_object.trusted_ca = hp_config.get("trustedCa", None)

    return config_object


def _is_pod_identity_addon_enabled(instance):
    if not instance:
        return False
    if not instance.pod_identity_profile:
        return False
    return bool(instance.pod_identity_profile.enabled)


def _ensure_pod_identity_addon_is_enabled(instance):
    if not _is_pod_identity_addon_enabled(instance):
        raise CLIError('The pod identity addon is not enabled for this managed cluster yet.\n'
                       'To enable, run "az aks update --enable-pod-identity')


def _ensure_pod_identity_kubenet_consent(network_profile, pod_identity_profile, customer_consent):
    if not network_profile or not network_profile.network_plugin:
        # invalid data
        return
    if network_profile.network_plugin.lower() != 'kubenet':
        # not kubenet, no need to check
        return

    if customer_consent is None:
        # no set this time, read from previous value
        customer_consent = bool(
            pod_identity_profile.allow_network_plugin_kubenet)

    if not customer_consent:
        raise CLIError(
            '--enable-pod-identity-with-kubenet is required for enabling pod identity addon when using Kubenet network plugin')
    pod_identity_profile.allow_network_plugin_kubenet = True


def _update_addon_pod_identity(instance, enable, pod_identities=None, pod_identity_exceptions=None, allow_kubenet_consent=None):
    if not enable:
        # when disable, remove previous saved value
        instance.pod_identity_profile = ManagedClusterPodIdentityProfile(
            enabled=False)
        return

    if not instance.pod_identity_profile:
        # not set before
        instance.pod_identity_profile = ManagedClusterPodIdentityProfile(
            enabled=enable,
            user_assigned_identities=pod_identities,
            user_assigned_identity_exceptions=pod_identity_exceptions,
        )

    _ensure_pod_identity_kubenet_consent(
        instance.network_profile, instance.pod_identity_profile, allow_kubenet_consent)

    instance.pod_identity_profile.enabled = enable
    instance.pod_identity_profile.user_assigned_identities = pod_identities or []
    instance.pod_identity_profile.user_assigned_identity_exceptions = pod_identity_exceptions or []


def _ensure_managed_identity_operator_permission(cli_ctx, instance, scope):
    cluster_identity_object_id = None
    if instance.identity.type.lower() == 'userassigned':
        for identity in instance.identity.user_assigned_identities.values():
            cluster_identity_object_id = identity.principal_id
            break
    elif instance.identity.type.lower() == 'systemassigned':
        cluster_identity_object_id = instance.identity.principal_id
    else:
        raise CLIError('unsupported identity type: {}'.format(
            instance.identity.type))
    if cluster_identity_object_id is None:
        raise CLIError('unable to resolve cluster identity')

    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments
    cluster_identity_object_id = cluster_identity_object_id.lower()
    scope = scope.lower()

    # list all assignments of the target identity (scope) that assigned to the cluster identity
    filter_query = "atScope() and assignedTo('{}')".format(cluster_identity_object_id)
    for i in assignments_client.list_for_scope(scope=scope, filter=filter_query):
        if not i.role_definition_id.lower().endswith(CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID):
            continue

        # sanity checks to make sure we see the correct assignments
        if i.principal_id.lower() != cluster_identity_object_id:
            # assignedTo() should return the assignment to cluster identity
            continue
        if not scope.startswith(i.scope.lower()):
            # atScope() should return the assignments in subscription / resource group / resource level
            continue

        # already assigned
        logger.debug('Managed Identity Opereator role has been assigned to {}'.format(i.scope))
        return

    if not add_role_assignment(cli_ctx, CONST_MANAGED_IDENTITY_OPERATOR_ROLE, cluster_identity_object_id,
                               is_service_principal=False, scope=scope):
        raise CLIError(
            'Could not grant Managed Identity Operator permission for cluster')

    # need more time to propogate this assignment...
    print()
    print('Wait 30 seconds for identity role assignment propagation.')
    time.sleep(30)


def aks_pod_identity_add(cmd, client, resource_group_name, cluster_name,
                         identity_name, identity_namespace, identity_resource_id,
                         binding_selector=None,
                         no_wait=False):  # pylint: disable=unused-argument
    instance = client.get(resource_group_name, cluster_name)
    _ensure_pod_identity_addon_is_enabled(instance)

    user_assigned_identity = _get_user_assigned_identity(
        cmd.cli_ctx, identity_resource_id)
    _ensure_managed_identity_operator_permission(
        cmd.cli_ctx, instance, user_assigned_identity.id)

    pod_identities = []
    if instance.pod_identity_profile.user_assigned_identities:
        pod_identities = instance.pod_identity_profile.user_assigned_identities
    pod_identity = ManagedClusterPodIdentity(
        name=identity_name,
        namespace=identity_namespace,
        identity=UserAssignedIdentity(
            resource_id=user_assigned_identity.id,
            client_id=user_assigned_identity.client_id,
            object_id=user_assigned_identity.principal_id,
        )
    )
    if binding_selector is not None:
        pod_identity.binding_selector = binding_selector
    pod_identities.append(pod_identity)

    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=pod_identities,
        pod_identity_exceptions=instance.pod_identity_profile.user_assigned_identity_exceptions,
    )

    # send the managed cluster represeentation to update the pod identity addon
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, instance)


def aks_pod_identity_delete(cmd, client, resource_group_name, cluster_name,
                            identity_name, identity_namespace,
                            no_wait=False):  # pylint: disable=unused-argument
    instance = client.get(resource_group_name, cluster_name)
    _ensure_pod_identity_addon_is_enabled(instance)

    pod_identities = []
    if instance.pod_identity_profile.user_assigned_identities:
        for pod_identity in instance.pod_identity_profile.user_assigned_identities:
            if pod_identity.name == identity_name and pod_identity.namespace == identity_namespace:
                # to remove
                continue
            pod_identities.append(pod_identity)

    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=pod_identities,
        pod_identity_exceptions=instance.pod_identity_profile.user_assigned_identity_exceptions,
    )

    # send the managed cluster represeentation to update the pod identity addon
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, instance)


def aks_pod_identity_list(cmd, client, resource_group_name, cluster_name):  # pylint: disable=unused-argument
    instance = client.get(resource_group_name, cluster_name)
    return _remove_nulls([instance])[0]


def aks_pod_identity_exception_add(cmd, client, resource_group_name, cluster_name,
                                   exc_name, exc_namespace, pod_labels, no_wait=False):  # pylint: disable=unused-argument
    instance = client.get(resource_group_name, cluster_name)
    _ensure_pod_identity_addon_is_enabled(instance)

    pod_identity_exceptions = []
    if instance.pod_identity_profile.user_assigned_identity_exceptions:
        pod_identity_exceptions = instance.pod_identity_profile.user_assigned_identity_exceptions
    exc = ManagedClusterPodIdentityException(
        name=exc_name, namespace=exc_namespace, pod_labels=pod_labels)
    pod_identity_exceptions.append(exc)

    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=instance.pod_identity_profile.user_assigned_identities,
        pod_identity_exceptions=pod_identity_exceptions,
    )

    # send the managed cluster represeentation to update the pod identity addon
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, instance)


def aks_pod_identity_exception_delete(cmd, client, resource_group_name, cluster_name,
                                      exc_name, exc_namespace, no_wait=False):  # pylint: disable=unused-argument
    instance = client.get(resource_group_name, cluster_name)
    _ensure_pod_identity_addon_is_enabled(instance)

    pod_identity_exceptions = []
    if instance.pod_identity_profile.user_assigned_identity_exceptions:
        for exc in instance.pod_identity_profile.user_assigned_identity_exceptions:
            if exc.name == exc_name and exc.namespace == exc_namespace:
                # to remove
                continue
            pod_identity_exceptions.append(exc)

    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=instance.pod_identity_profile.user_assigned_identities,
        pod_identity_exceptions=pod_identity_exceptions,
    )

    # send the managed cluster represeentation to update the pod identity addon
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, instance)


def aks_pod_identity_exception_update(cmd, client, resource_group_name, cluster_name,
                                      exc_name, exc_namespace, pod_labels, no_wait=False):  # pylint: disable=unused-argument
    instance = client.get(resource_group_name, cluster_name)
    _ensure_pod_identity_addon_is_enabled(instance)

    found_target = False
    updated_exc = ManagedClusterPodIdentityException(
        name=exc_name, namespace=exc_namespace, pod_labels=pod_labels)
    pod_identity_exceptions = []
    if instance.pod_identity_profile.user_assigned_identity_exceptions:
        for exc in instance.pod_identity_profile.user_assigned_identity_exceptions:
            if exc.name == exc_name and exc.namespace == exc_namespace:
                found_target = True
                pod_identity_exceptions.append(updated_exc)
            else:
                pod_identity_exceptions.append(exc)

    if not found_target:
        raise CLIError(
            'pod identity exception {}/{} not found'.format(exc_namespace, exc_name))

    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=instance.pod_identity_profile.user_assigned_identities,
        pod_identity_exceptions=pod_identity_exceptions,
    )

    # send the managed cluster represeentation to update the pod identity addon
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, instance)


def aks_pod_identity_exception_list(cmd, client, resource_group_name, cluster_name):
    instance = client.get(resource_group_name, cluster_name)
    return _remove_nulls([instance])[0]


def _ensure_cluster_identity_permission_on_kubelet_identity(cli_ctx, cluster_identity_object_id, scope):
    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments

    for i in assignments_client.list_for_scope(scope=scope, filter='atScope()'):
        if i.scope.lower() != scope.lower():
            continue
        if not i.role_definition_id.lower().endswith(CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID):
            continue
        if i.principal_id.lower() != cluster_identity_object_id.lower():
            continue
        # already assigned
        return

    if not add_role_assignment(cli_ctx, CONST_MANAGED_IDENTITY_OPERATOR_ROLE, cluster_identity_object_id,
                               is_service_principal=False, scope=scope):
        raise CLIError('Could not grant Managed Identity Operator permission to cluster identity at scope {}'.format(scope))


def aks_egress_endpoints_list(cmd, client, resource_group_name, name):   # pylint: disable=unused-argument
    return client.list_outbound_network_dependencies_endpoints(resource_group_name, name)
