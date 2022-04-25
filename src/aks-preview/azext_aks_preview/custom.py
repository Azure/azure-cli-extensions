# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
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
import webbrowser
from math import isnan

import colorama  # pylint: disable=import-error
import yaml  # pylint: disable=import-error
from azure.cli.core.api import get_config_dir
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    InvalidArgumentValueError,
)
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import (
    get_mgmt_service_client,
    get_subscription_id,
)
from azure.cli.core.util import (
    get_file_json,
    in_cloud_console,
    read_file_content,
    sdk_no_wait,
    shell_safe_json_parse,
)
from azure.graphrbac.models import (
    ApplicationCreateParameters,
    KeyCredential,
    PasswordCredential,
    ServicePrincipalCreateParameters,
)
from dateutil.parser import parse  # pylint: disable=import-error
from dateutil.relativedelta import relativedelta  # pylint: disable=import-error
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_pass
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError
from six.moves.urllib.error import URLError  # pylint: disable=import-error
from six.moves.urllib.request import urlopen  # pylint: disable=import-error
from tabulate import tabulate  # pylint: disable=import-error

from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW

from ._client_factory import (
    cf_agent_pools,
    cf_container_registry_service,
    cf_nodepool_snapshots_client,
    cf_mc_snapshots_client,
    cf_storage,
    get_auth_management_client,
    get_graph_rbac_management_client,
    get_msi_client,
    get_resource_by_name,
)
from ._consts import (
    ADDONS,
    ADDONS_DESCRIPTIONS,
    CONST_ACC_SGX_QUOTE_HELPER_ENABLED,
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
    CONST_AZURE_POLICY_ADDON_NAME,
    CONST_CONFCOM_ADDON_NAME,
    CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    CONST_INGRESS_APPGW_ADDON_NAME,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME,
    CONST_INGRESS_APPGW_SUBNET_CIDR,
    CONST_INGRESS_APPGW_SUBNET_ID,
    CONST_INGRESS_APPGW_WATCH_NAMESPACE,
    CONST_KUBE_DASHBOARD_ADDON_NAME,
    CONST_MANAGED_IDENTITY_OPERATOR_ROLE,
    CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID,
    CONST_MONITORING_ADDON_NAME,
    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID,
    CONST_MONITORING_USING_AAD_MSI_AUTH,
    CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    CONST_ROTATION_POLL_INTERVAL,
    CONST_SCALE_DOWN_MODE_DELETE,
    CONST_SCALE_SET_PRIORITY_REGULAR,
    CONST_SCALE_SET_PRIORITY_SPOT,
    CONST_SECRET_ROTATION_ENABLED,
    CONST_SPOT_EVICTION_POLICY_DELETE,
    CONST_VIRTUAL_NODE_ADDON_NAME,
    CONST_VIRTUAL_NODE_SUBNET_NAME,
)
from ._helpers import (
    _trim_fqdn_name_containing_hcp,
)
from ._podidentity import (
    _ensure_managed_identity_operator_permission,
    _ensure_pod_identity_addon_is_enabled,
    _fill_defaults_for_pod_identity_profile,
    _update_addon_pod_identity,
)
from ._resourcegroup import get_rg_location
from ._roleassignments import (
    add_role_assignment,
    build_role_scope,
    create_role_assignment,
    resolve_object_id,
    resolve_role_id,
)
from .addonconfiguration import (
    add_ingress_appgw_addon_role_assignment,
    add_monitoring_role_assignment,
    add_virtual_node_role_assignment,
    enable_addons,
    ensure_container_insights_for_monitoring,
    ensure_default_log_analytics_workspace_for_monitoring,
    sanitize_loganalytics_ws_resource_id,
)
from .maintenanceconfiguration import (
    aks_maintenanceconfiguration_update_internal,
)
from .vendored_sdks.azure_mgmt_preview_aks.v2022_03_02_preview.models import (
    AgentPool,
    AgentPoolUpgradeSettings,
    ContainerServiceStorageProfileTypes,
    CreationData,
    KubeletConfig,
    LinuxOSConfig,
    ManagedClusterAddonProfile,
    ManagedClusterHTTPProxyConfig,
    ManagedClusterPodIdentity,
    ManagedClusterPodIdentityException,
    PowerState,
    Snapshot,
    ManagedClusterSnapshot,
    SysctlConfig,
    UserAssignedIdentity,
)

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


_re_snapshot_resource_id = re.compile(
    r'/subscriptions/(.*?)/resourcegroups/(.*?)/providers/microsoft.containerservice/snapshots/(.*)',
    flags=re.IGNORECASE)


_re_mc_snapshot_resource_id = re.compile(
    r'/subscriptions/(.*?)/resourcegroups/(.*?)/providers/microsoft.containerservice/managedclustersnapshots/(.*)',
    flags=re.IGNORECASE)


def _get_snapshot(cli_ctx, snapshot_id):
    snapshot_id = snapshot_id.lower()
    match = _re_snapshot_resource_id.search(snapshot_id)
    if match:
        subscription_id = match.group(1)
        resource_group_name = match.group(2)
        snapshot_name = match.group(3)
        snapshot_client = cf_nodepool_snapshots_client(
            cli_ctx, subscription_id=subscription_id)
        try:
            snapshot = snapshot_client.get(resource_group_name, snapshot_name)
        except CloudError as ex:
            if 'was not found' in ex.message:
                raise InvalidArgumentValueError(
                    "Snapshot {} not found.".format(snapshot_id))
            raise CLIError(ex.message)
        return snapshot
    raise InvalidArgumentValueError(
        "Cannot parse snapshot name from provided resource id {}.".format(snapshot_id))


def _get_cluster_snapshot(cli_ctx, snapshot_id):
    snapshot_id = snapshot_id.lower()
    match = _re_mc_snapshot_resource_id.search(snapshot_id)
    if match:
        subscription_id = match.group(1)
        resource_group_name = match.group(2)
        snapshot_name = match.group(3)
        snapshot_client = cf_mc_snapshots_client(
            cli_ctx, subscription_id=subscription_id)
        try:
            snapshot = snapshot_client.get(resource_group_name, snapshot_name)
        except CloudError as ex:
            if 'was not found' in ex.message:
                raise InvalidArgumentValueError(
                    "Managed cluster snapshot {} not found.".format(snapshot_id))
            raise CLIError(ex.message)
        return snapshot
    raise InvalidArgumentValueError(
        "Cannot parse snapshot name from provided resource id {}.".format(snapshot_id))


def aks_browse(
    cmd,
    client,
    resource_group_name,
    name,
    disable_browser=False,
    listen_address="127.0.0.1",
    listen_port="8001",
):
    from azure.cli.command_modules.acs.custom import _aks_browse

    return _aks_browse(
        cmd,
        client,
        resource_group_name,
        name,
        disable_browser,
        listen_address,
        listen_port,
        CUSTOM_MGMT_AKS_PREVIEW,
    )


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


# pylint: disable=unused-argument,too-many-locals
def aks_create(cmd,
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
               node_vm_size=None,
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
               pod_cidrs=None,
               service_cidrs=None,
               ip_families=None,
               dns_service_ip=None,
               docker_bridge_address=None,
               load_balancer_sku=None,
               load_balancer_managed_outbound_ip_count=None,
               load_balancer_managed_outbound_ipv6_count=None,
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
               # NOTE: for workload identity flags, we need to know if it's set to True/False or not set (None)
               enable_workload_identity=None,
               enable_encryption_at_host=False,
               enable_ultra_ssd=False,
               edge_zone=None,
               enable_secret_rotation=False,
               rotation_poll_interval=None,
               disable_local_accounts=False,
               no_wait=False,
               assign_kubelet_identity=None,
               workload_runtime=None,
               gpu_instance_profile=None,
               enable_windows_gmsa=False,
               gmsa_dns_server=None,
               gmsa_root_domain_name=None,
               snapshot_id=None,
               cluster_snapshot_id=None,
               enable_oidc_issuer=False,
               host_group_id=None,
               crg_id=None,
               message_of_the_day=None,
               enable_azure_keyvault_kms=False,
               azure_keyvault_kms_key_id=None,
               yes=False,
               enable_namespace_resources=False): # Check what this name should be.
    # DO NOT MOVE: get all the original parameters and save them as a dictionary
    raw_parameters = locals()

    from azure.cli.command_modules.acs._consts import DecoratorEarlyExitException
    from azure.cli.command_modules.acs.decorator import AKSParamDict
    from .decorator import AKSPreviewCreateDecorator

    # decorator pattern
    aks_create_decorator = AKSPreviewCreateDecorator(
        cmd=cmd,
        client=client,
        raw_parameters=AKSParamDict(raw_parameters),
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
    )
    try:
        # construct mc profile
        mc = aks_create_decorator.construct_mc_preview_profile()
    except DecoratorEarlyExitException:
        # exit gracefully
        return None
    # send request to create a real managed cluster
    return aks_create_decorator.create_mc_preview(mc)


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
               load_balancer_managed_outbound_ipv6_count=None,
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
               # NOTE: for workload identity flags, we need to know if it's set to True/False or not set (None)
               enable_workload_identity=None,
               disable_workload_identity=None,
               enable_secret_rotation=False,
               disable_secret_rotation=False,
               rotation_poll_interval=None,
               disable_local_accounts=False,
               enable_local_accounts=False,
               enable_public_fqdn=False,
               disable_public_fqdn=False,
               yes=False,
               tags=None,
               nodepool_labels=None,
               windows_admin_password=None,
               enable_azure_rbac=False,
               disable_azure_rbac=False,
               enable_windows_gmsa=False,
               gmsa_dns_server=None,
               gmsa_root_domain_name=None,
               enable_oidc_issuer=False,
               http_proxy_config=None,
               enable_azure_keyvault_kms=False,
               azure_keyvault_kms_key_id=None,
               enable_namespace_resources=False):
    # DO NOT MOVE: get all the original parameters and save them as a dictionary
    raw_parameters = locals()

    from azure.cli.command_modules.acs._consts import DecoratorEarlyExitException
    from azure.cli.command_modules.acs.decorator import AKSParamDict
    from .decorator import AKSPreviewUpdateDecorator

    # decorator pattern
    aks_update_decorator = AKSPreviewUpdateDecorator(
        cmd=cmd,
        client=client,
        raw_parameters=AKSParamDict(raw_parameters),
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
    )
    try:
        # update mc profile
        mc = aks_update_decorator.update_mc_preview_profile()
    except DecoratorEarlyExitException:
        # exit gracefully
        return None
    # send request to update the real managed cluster
    return aks_update_decorator.update_mc_preview(mc)


# pylint: disable=unused-argument
def aks_show(cmd, client, resource_group_name, name):
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
                        namespace_name=None,
                        admin=False,
                        user='clusterUser',
                        path=os.path.join(os.path.expanduser(
                            '~'), '.kube', 'config'),
                        overwrite_existing=False,
                        context_name=None,
                        public_fqdn=False,
                        credential_format=None):
    credentialResults = None
    serverType = None
    if public_fqdn:
        serverType = 'public'
    if credential_format:
        credential_format = credential_format.lower()
        if admin:
            raise InvalidArgumentValueError("--format can only be specified when requesting clusterUser credential.")
    if admin:
        if namespace_name is not None:
            raise InvalidArgumentValueError("--namespace is not valid for admin credentials") # Do we want this?
        credentialResults = client.list_cluster_admin_credentials(
            resource_group_name, name, serverType)
    else:
        if user.lower() == 'clusteruser':
            credentialResults = client.list_cluster_user_credentials(
                resource_group_name, name, serverType, credential_format, namespace_name)
        elif user.lower() == 'clustermonitoringuser':
            credentialResults = client.list_cluster_monitoring_user_credentials(
                resource_group_name, name, serverType, namespace_name=namespace_name)
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

    from msrestazure.tools import (is_valid_resource_id, parse_resource_id,
                                   resource_id)
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

    # Form containerName from fqdn, as it was previously jsut the location of code is changed.
    # https://docs.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata#container-names
    maxContainerNameLength = 63
    fqdn = mc.fqdn if mc.fqdn is not None else mc.private_fqdn
    normalized_container_name = fqdn.replace('.', '-')
    len_of_container_name = normalized_container_name.index("-hcp-")
    if len_of_container_name == -1:
        len_of_container_name = maxContainerNameLength
    container_name = normalized_container_name[:len_of_container_name]

    sas_token = sas_token.strip('?')
    deployment_yaml = _read_periscope_yaml()
    deployment_yaml = deployment_yaml.replace(
        "# <accountName, string>", storage_account_name)
    deployment_yaml = deployment_yaml.replace("# <saskey, base64 encoded>",
                                              (base64.b64encode(bytes("?" + sas_token, 'ascii'))).decode('ascii'))
    deployment_yaml = deployment_yaml.replace(
        "# <containerName, string>", container_name)

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

    token_in_storage_account_url = readonly_sas_token if readonly_sas_token is not None else sas_token
    log_storage_account_url = f"https://{storage_account_name}.blob.core.windows.net/" \
                              f"{_trim_fqdn_name_containing_hcp(container_name)}?{token_in_storage_account_url}"

    print(f'{colorama.Fore.GREEN}Your logs are being uploaded to storage account {format_bright(storage_account_name)}')

    print()
    print(f'You can download Azure Storage Explorer here '
          f'{format_hyperlink("https://azure.microsoft.com/en-us/features/storage-explorer/")}'
          f' to check the logs by adding the storage account using the following URL:')
    print(f'{format_hyperlink(log_storage_account_url)}')

    print()
    if not prompt_y_n('Do you want to see analysis results now?', default="n"):
        print(f"You can run 'az aks kanalyze -g {resource_group_name} -n {name}' "
              f"anytime to check the analysis results.")
    else:
        display_diagnostics_report(temp_kubeconfig_path)


def _read_periscope_yaml():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    periscope_yaml_file = os.path.join(
        curr_dir, "deploymentyaml", "aks-periscope.yaml")
    yaml_file = open(periscope_yaml_file, "r")
    data_loaded = yaml_file.read()

    return data_loaded


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
    _fill_defaults_for_pod_identity_profile(instance.pod_identity_profile)

    if len(instance.agent_pool_profiles) > 1 and nodepool_name == "":
        raise CLIError('There are more than one node pool in the cluster. '
                       'Please specify nodepool name or use az aks nodepool command to scale node pool')

    for agent_profile in instance.agent_pool_profiles:
        if agent_profile.name == nodepool_name or (nodepool_name == "" and len(instance.agent_pool_profiles) == 1):
            if agent_profile.enable_auto_scaling:
                raise CLIError(
                    "Cannot scale cluster autoscaler enabled node pool.")

            agent_profile.count = int(node_count)  # pylint: disable=no-member
            # null out the SP profile because otherwise validation complains
            instance.service_principal_profile = None
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
    _fill_defaults_for_pod_identity_profile(instance.pod_identity_profile)

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
                True, agent_pool_client, resource_group_name, name, agent_pool_profile.name, None)
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
            agent_profile.creation_data = None

    # null out the SP profile because otherwise validation complains
    instance.service_principal_profile = None

    headers = get_aks_custom_headers(aks_custom_headers)

    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, name, instance, headers=headers)


def _upgrade_single_nodepool_image_version(no_wait, client, resource_group_name, cluster_name, nodepool_name, snapshot_id=None):
    headers = {}
    if snapshot_id:
        headers["AKSSnapshotId"] = snapshot_id

    return sdk_no_wait(no_wait, client.begin_upgrade_node_image_version, resource_group_name, cluster_name, nodepool_name, headers=headers)


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
                        enable_secret_rotation=False,
                        rotation_poll_interval=None,):
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
        workspace_resource_id = sanitize_loganalytics_ws_resource_id(
            workspace_resource_id)
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
        addon_profile = ManagedClusterAddonProfile(enabled=True, config={
                                                   CONST_SECRET_ROTATION_ENABLED: "false", CONST_ROTATION_POLL_INTERVAL: "2m"})
        if enable_secret_rotation:
            addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "true"
        if rotation_poll_interval is not None:
            addon_profile.config[CONST_ROTATION_POLL_INTERVAL] = rotation_poll_interval
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
                      os_type=None,
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
                      snapshot_id=None,
                      host_group_id=None,
                      crg_id=None,
                      message_of_the_day=None,
                      no_wait=False):
    instances = client.list(resource_group_name, cluster_name)
    for agentpool_profile in instances:
        if agentpool_profile.name == nodepool_name:
            raise CLIError("Node pool {} already exists, please try a different name, "
                           "use 'aks nodepool list' to get current list of node pool".format(nodepool_name))

    upgradeSettings = AgentPoolUpgradeSettings()
    taints_array = []

    creationData = None
    if snapshot_id:
        snapshot = _get_snapshot(cmd.cli_ctx, snapshot_id)
        if not kubernetes_version:
            kubernetes_version = snapshot.kubernetes_version
        if not os_type:
            os_type = snapshot.os_type
        if not os_sku:
            os_sku = snapshot.os_sku
        if not node_vm_size:
            node_vm_size = snapshot.vm_size

        creationData = CreationData(
            source_resource_id=snapshot_id
        )

    if not os_type:
        os_type = "Linux"

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
        gpu_instance_profile=gpu_instance_profile,
        creation_data=creationData,
        host_group_id=host_group_id,
        capacity_reservation_group_id=crg_id
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

    if message_of_the_day:
        agent_pool.message_of_the_day = _get_message_of_the_day(
            message_of_the_day)

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
                          aks_custom_headers=None,
                          snapshot_id=None):

    if kubernetes_version != '' and node_image_only:
        raise CLIError('Conflicting flags. Upgrading the Kubernetes version will also upgrade node image version.'
                       'If you only want to upgrade the node version please use the "--node-image-only" option only.')

    if node_image_only:
        return _upgrade_single_nodepool_image_version(no_wait,
                                                      client,
                                                      resource_group_name,
                                                      cluster_name,
                                                      nodepool_name,
                                                      snapshot_id)

    creationData = None
    if snapshot_id:
        snapshot = _get_snapshot(cmd.cli_ctx, snapshot_id)
        if not kubernetes_version and not node_image_only:
            kubernetes_version = snapshot.kubernetes_version

        creationData = CreationData(
            source_resource_id=snapshot_id
        )

    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    instance.orchestrator_version = kubernetes_version
    instance.creation_data = creationData

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
                         labels=None,
                         node_taints=None,
                         no_wait=False):

    update_autoscaler = enable_cluster_autoscaler + \
        disable_cluster_autoscaler + update_cluster_autoscaler

    if (update_autoscaler != 1 and not tags and not scale_down_mode and not mode and not max_surge and labels is None and node_taints is None):
        raise CLIError('Please specify one or more of "--enable-cluster-autoscaler" or '
                       '"--disable-cluster-autoscaler" or '
                       '"--update-cluster-autoscaler" or '
                       '"--tags" or "--mode" or "--max-surge" or "--scale-down-mode" or "--labels" or "--node-taints')

    instance = client.get(resource_group_name, cluster_name, nodepool_name)

    if node_taints is not None:
        taints_array = []
        if node_taints != '':
            for taint in node_taints.split(','):
                try:
                    taint = taint.strip()
                    taints_array.append(taint)
                except ValueError:
                    raise InvalidArgumentValueError(
                        'Taint does not match allowed values. Expect value such as "special=true:NoSchedule".')
        instance.node_taints = taints_array

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

    if labels is not None:
        instance.node_labels = labels
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


def aks_agentpool_stop(cmd,   # pylint: disable=unused-argument
                       client,
                       resource_group_name,
                       cluster_name,
                       nodepool_name,
                       aks_custom_headers=None,
                       no_wait=False):
    agentpool_exists = False
    instances = client.list(resource_group_name, cluster_name)
    for agentpool_profile in instances:
        if agentpool_profile.name.lower() == nodepool_name.lower():
            agentpool_exists = True
            break

    if not agentpool_exists:
        raise InvalidArgumentValueError(
            "Node pool {} doesnt exist, use 'aks nodepool list' to get current node pool list".format(nodepool_name))

    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    power_state = PowerState(code="Stopped")
    instance.power_state = power_state
    headers = get_aks_custom_headers(aks_custom_headers)
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, nodepool_name, instance, headers=headers)


def aks_agentpool_start(cmd,   # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        cluster_name,
                        nodepool_name,
                        aks_custom_headers=None,
                        no_wait=False):
    agentpool_exists = False
    instances = client.list(resource_group_name, cluster_name)
    for agentpool_profile in instances:
        if agentpool_profile.name.lower() == nodepool_name.lower():
            agentpool_exists = True
            break
    if not agentpool_exists:
        raise InvalidArgumentValueError(
            "Node pool {} doesnt exist, use 'aks nodepool list' to get current node pool list".format(nodepool_name))
    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    power_state = PowerState(code="Running")
    instance.power_state = power_state
    headers = get_aks_custom_headers(aks_custom_headers)
    return sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, cluster_name, nodepool_name, instance, headers=headers)


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
                     appgw_watch_namespace=None, enable_sgxquotehelper=False, enable_secret_rotation=False, rotation_poll_interval=None,
                     no_wait=False, enable_msi_auth_for_monitoring=False):
    return enable_addons(cmd, client, resource_group_name, name, addon, workspace_resource_id=workspace_resource_id,
                         subnet_name=subnet_name, appgw_name=appgw_name, appgw_subnet_prefix=appgw_subnet_prefix,
                         appgw_subnet_cidr=appgw_subnet_cidr, appgw_id=appgw_id, appgw_subnet_id=appgw_subnet_id,
                         appgw_watch_namespace=appgw_watch_namespace, enable_sgxquotehelper=enable_sgxquotehelper,
                         enable_secret_rotation=enable_secret_rotation, rotation_poll_interval=rotation_poll_interval, no_wait=no_wait,
                         enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring)


def aks_addon_disable(cmd, client, resource_group_name, name, addon, no_wait=False):
    return aks_disable_addons(cmd, client, resource_group_name, name, addon, no_wait)


def aks_addon_update(cmd, client, resource_group_name, name, addon, workspace_resource_id=None,
                     subnet_name=None, appgw_name=None, appgw_subnet_prefix=None, appgw_subnet_cidr=None, appgw_id=None,
                     appgw_subnet_id=None,
                     appgw_watch_namespace=None, enable_sgxquotehelper=False, enable_secret_rotation=False, rotation_poll_interval=None,
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
                         enable_secret_rotation=enable_secret_rotation, rotation_poll_interval=rotation_poll_interval, no_wait=no_wait,
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
                      appgw_watch_namespace=None, enable_sgxquotehelper=False, enable_secret_rotation=False, rotation_poll_interval=None, no_wait=False, enable_msi_auth_for_monitoring=False):

    instance = client.get(resource_group_name, name)
    # this is overwritten by _update_addons(), so the value needs to be recorded here
    msi_auth = True if instance.service_principal_profile.client_id == "msi" else False

    subscription_id = get_subscription_id(cmd.cli_ctx)
    instance = _update_addons(cmd, instance, subscription_id, resource_group_name, name, addons, enable=True,
                              workspace_resource_id=workspace_resource_id, enable_msi_auth_for_monitoring=enable_msi_auth_for_monitoring, subnet_name=subnet_name,
                              appgw_name=appgw_name, appgw_subnet_prefix=appgw_subnet_prefix, appgw_subnet_cidr=appgw_subnet_cidr, appgw_id=appgw_id, appgw_subnet_id=appgw_subnet_id, appgw_watch_namespace=appgw_watch_namespace,
                              enable_sgxquotehelper=enable_sgxquotehelper, enable_secret_rotation=enable_secret_rotation, rotation_poll_interval=rotation_poll_interval, no_wait=no_wait)

    if CONST_MONITORING_ADDON_NAME in instance.addon_profiles and instance.addon_profiles[CONST_MONITORING_ADDON_NAME].enabled:
        if CONST_MONITORING_USING_AAD_MSI_AUTH in instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config and \
                str(instance.addon_profiles[CONST_MONITORING_ADDON_NAME].config[CONST_MONITORING_USING_AAD_MSI_AUTH]).lower() == 'true':
            if not msi_auth:
                raise ArgumentUsageError(
                    "--enable-msi-auth-for-monitoring can not be used on clusters with service principal auth.")
            else:
                # create a Data Collection Rule (DCR) and associate it with the cluster
                ensure_container_insights_for_monitoring(
                    cmd, instance.addon_profiles[CONST_MONITORING_ADDON_NAME], subscription_id, resource_group_name, name, instance.location, aad_route=True, create_dcr=True, create_dcra=True)
        else:
            # monitoring addon will use legacy path
            ensure_container_insights_for_monitoring(
                cmd, instance.addon_profiles[CONST_MONITORING_ADDON_NAME], subscription_id, resource_group_name, name, instance.location, aad_route=False)

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
                   disable_secret_rotation=False,
                   rotation_poll_interval=None,
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
                workspace_resource_id = sanitize_loganalytics_ws_resource_id(
                    workspace_resource_id)

                addon_profile.config = {
                    logAnalyticsConstName: workspace_resource_id}
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
                    enabled=True, config={CONST_SECRET_ROTATION_ENABLED: "false", CONST_ROTATION_POLL_INTERVAL: "2m"})
                if enable_secret_rotation:
                    addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "true"
                if disable_secret_rotation:
                    addon_profile.config[CONST_SECRET_ROTATION_ENABLED] = "false"
                if rotation_poll_interval is not None:
                    addon_profile.config[CONST_ROTATION_POLL_INTERVAL] = rotation_poll_interval
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

    # null out the SP profile because otherwise validation complains
    instance.service_principal_profile = None

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
    for _, diag_setting in enumerate(diag_settings):
        if diag_setting:
            return diag_setting.storage_account_id

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


def _get_message_of_the_day(file_path):
    if not os.path.isfile(file_path):
        raise CLIError(
            "{} is not valid file, or not accessable.".format(file_path))
    content = read_file_content(file_path)
    if not content:
        raise ArgumentUsageError(
            "message of the day should point to a non-empty file if specified.")
    content = base64.b64encode(bytes(content, 'ascii')).decode('ascii')
    return content


def _get_kubelet_config(file_path):
    if not os.path.isfile(file_path):
        raise CLIError(
            "{} is not valid file, or not accessable.".format(file_path))
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
        raise CLIError(
            "{} is not valid file, or not accessable.".format(file_path))
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
        raise CLIError(
            "{} is not valid file, or not accessable.".format(file_path))
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

    from azext_aks_preview.decorator import AKSPreviewModels

    # store all the models used by pod identity
    pod_identity_models = AKSPreviewModels(
        cmd, CUSTOM_MGMT_AKS_PREVIEW).pod_identity_models
    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=pod_identities,
        pod_identity_exceptions=instance.pod_identity_profile.user_assigned_identity_exceptions,
        models=pod_identity_models
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

    from azext_aks_preview.decorator import AKSPreviewModels

    # store all the models used by pod identity
    pod_identity_models = AKSPreviewModels(
        cmd, CUSTOM_MGMT_AKS_PREVIEW).pod_identity_models
    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=pod_identities,
        pod_identity_exceptions=instance.pod_identity_profile.user_assigned_identity_exceptions,
        models=pod_identity_models
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

    from azext_aks_preview.decorator import AKSPreviewModels

    # store all the models used by pod identity
    pod_identity_models = AKSPreviewModels(
        cmd, CUSTOM_MGMT_AKS_PREVIEW).pod_identity_models
    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=instance.pod_identity_profile.user_assigned_identities,
        pod_identity_exceptions=pod_identity_exceptions,
        models=pod_identity_models
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

    from azext_aks_preview.decorator import AKSPreviewModels

    # store all the models used by pod identity
    pod_identity_models = AKSPreviewModels(
        cmd, CUSTOM_MGMT_AKS_PREVIEW).pod_identity_models
    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=instance.pod_identity_profile.user_assigned_identities,
        pod_identity_exceptions=pod_identity_exceptions,
        models=pod_identity_models
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

    from azext_aks_preview.decorator import AKSPreviewModels

    # store all the models used by pod identity
    pod_identity_models = AKSPreviewModels(
        cmd, CUSTOM_MGMT_AKS_PREVIEW).pod_identity_models
    _update_addon_pod_identity(
        instance, enable=True,
        pod_identities=instance.pod_identity_profile.user_assigned_identities,
        pod_identity_exceptions=pod_identity_exceptions,
        models=pod_identity_models
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
        raise CLIError(
            'Could not grant Managed Identity Operator permission to cluster identity at scope {}'.format(scope))


def aks_egress_endpoints_list(cmd, client, resource_group_name, name):   # pylint: disable=unused-argument
    return client.list_outbound_network_dependencies_endpoints(resource_group_name, name)


def aks_snapshot_create(cmd,    # pylint: disable=too-many-locals,too-many-statements,too-many-branches
                        client,
                        resource_group_name,
                        name,
                        cluster_id,
                        location=None,
                        tags=None,
                        aks_custom_headers=None,
                        no_wait=False):

    rg_location = get_rg_location(cmd.cli_ctx, resource_group_name)
    if location is None:
        location = rg_location

    creationData = CreationData(
        source_resource_id=cluster_id
    )

    snapshot = ManagedClusterSnapshot(
        name=name,
        tags=tags,
        location=location,
        creation_data=creationData,
        snapshot_type="ManagedCluster",
    )

    headers = get_aks_custom_headers(aks_custom_headers)
    return client.create_or_update(resource_group_name, name, snapshot, headers=headers)


def aks_snapshot_show(cmd, client, resource_group_name, name):   # pylint: disable=unused-argument
    snapshot = client.get(resource_group_name, name)
    return snapshot


def aks_snapshot_delete(cmd,    # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        name,
                        no_wait=False,
                        yes=False):

    from knack.prompting import prompt_y_n
    msg = 'This will delete the cluster snapshot "{}" in resource group "{}", Are you sure?'.format(
        name, resource_group_name)
    if not yes and not prompt_y_n(msg, default="n"):
        return None

    return client.delete(resource_group_name, name)


def aks_snapshot_list(cmd, client, resource_group_name=None):  # pylint: disable=unused-argument
    if resource_group_name is None or resource_group_name == '':
        return client.list()

    return client.list_by_resource_group(resource_group_name)


def aks_nodepool_snapshot_create(cmd,    # pylint: disable=too-many-locals,too-many-statements,too-many-branches
                                 client,
                                 resource_group_name,
                                 snapshot_name,
                                 nodepool_id,
                                 location=None,
                                 tags=None,
                                 aks_custom_headers=None,
                                 no_wait=False):

    rg_location = get_rg_location(cmd.cli_ctx, resource_group_name)
    if location is None:
        location = rg_location

    creationData = CreationData(
        source_resource_id=nodepool_id
    )

    snapshot = Snapshot(
        name=snapshot_name,
        tags=tags,
        location=location,
        creation_data=creationData
    )

    headers = get_aks_custom_headers(aks_custom_headers)
    return client.create_or_update(resource_group_name, snapshot_name, snapshot, headers=headers)


def aks_nodepool_snapshot_show(cmd, client, resource_group_name, snapshot_name):   # pylint: disable=unused-argument
    snapshot = client.get(resource_group_name, snapshot_name)
    return snapshot


def aks_nodepool_snapshot_delete(cmd,    # pylint: disable=unused-argument
                                 client,
                                 resource_group_name,
                                 snapshot_name,
                                 no_wait=False,
                                 yes=False):

    from knack.prompting import prompt_y_n
    msg = 'This will delete the nodepool snapshot "{}" in resource group "{}", Are you sure?'.format(
        snapshot_name, resource_group_name)
    if not yes and not prompt_y_n(msg, default="n"):
        return None

    return client.delete(resource_group_name, snapshot_name)


def aks_nodepool_snapshot_list(cmd, client, resource_group_name=None):  # pylint: disable=unused-argument
    if resource_group_name is None or resource_group_name == '':
        return client.list()

    return client.list_by_resource_group(resource_group_name)
