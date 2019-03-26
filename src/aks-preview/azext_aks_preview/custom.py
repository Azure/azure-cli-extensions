# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
import binascii
import datetime
import json
import os
import os.path
import re
import time
import uuid
from ipaddress import ip_network
from knack.log import get_logger
from knack.util import CLIError
import dateutil.parser  # pylint: disable=import-error
from dateutil.relativedelta import relativedelta  # pylint: disable=import-error
from msrestazure.azure_exceptions import CloudError

from azure.cli.core.api import get_config_dir
from azure.cli.core._profile import Profile
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.keys import is_valid_ssh_rsa_public_key
from azure.cli.core.util import shell_safe_json_parse, truncate_text, sdk_no_wait
from azure.graphrbac.models import (ApplicationCreateParameters,
                                    PasswordCredential,
                                    KeyCredential,
                                    ServicePrincipalCreateParameters,
                                    GetObjectsParameters)
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ContainerServiceLinuxProfile
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ContainerServiceNetworkProfile
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ManagedClusterServicePrincipalProfile
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ContainerServiceSshConfiguration
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ContainerServiceSshPublicKey
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ManagedCluster
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ManagedClusterAADProfile
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ManagedClusterAddonProfile
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ManagedClusterAgentPoolProfile
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import AgentPool
from .vendored_sdks.azure_mgmt_preview_aks.v2019_02_01.models import ContainerServiceStorageProfileTypes
from ._client_factory import cf_resource_groups
from ._client_factory import get_auth_management_client
from ._client_factory import get_graph_rbac_management_client
from ._client_factory import cf_resources

logger = get_logger(__name__)


# pylint:disable=too-many-lines,unused-argument

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


def _add_role_assignment(cli_ctx, role, service_principal, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cli_ctx.get_progress_controller(True)
    hook.add(message='Waiting for AAD role to propagate', value=0, total_val=1.0)
    logger.info('Waiting for AAD role to propagate')
    for x in range(0, 10):
        hook.add(message='Waiting for AAD role to propagate', value=0.1 * x, total_val=1.0)
        try:
            # TODO: break this out into a shared utility library
            create_role_assignment(cli_ctx, role, service_principal, scope=scope)
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


def _get_subscription_id(cli_ctx):
    _, sub_id, _ = Profile(cli_ctx=cli_ctx).get_login_credentials(subscription_id=None)
    return sub_id


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


def _invoke_deployment(cli_ctx, resource_group_name, deployment_name, template, parameters, validate, no_wait,
                       subscription_id=None):
    from azure.mgmt.resource.resources import ResourceManagementClient
    from azure.mgmt.resource.resources.models import DeploymentProperties

    properties = DeploymentProperties(template=template, parameters=parameters, mode='incremental')
    smc = get_mgmt_service_client(cli_ctx, ResourceManagementClient, subscription_id=subscription_id).deployments
    if validate:
        logger.info('==== BEGIN TEMPLATE ====')
        logger.info(json.dumps(template, indent=2))
        logger.info('==== END TEMPLATE ====')
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
            link = 'https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal'  # pylint: disable=line-too-long
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
        start_date = dateutil.parser.parse(start_date)

    if not end_date:
        end_date = start_date + relativedelta(years=1)
    elif isinstance(end_date, str):
        end_date = dateutil.parser.parse(end_date)

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


def create_role_assignment(cli_ctx, role, assignee, resource_group_name=None, scope=None):
    return _create_role_assignment(cli_ctx, role, assignee, resource_group_name, scope)


def _create_role_assignment(cli_ctx, role, assignee, resource_group_name=None, scope=None, resolve_assignee=True):
    from azure.cli.core.profiles import ResourceType, get_sdk
    factory = get_auth_management_client(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions

    scope = _build_role_scope(resource_group_name, scope, assignments_client.config.subscription_id)

    role_id = _resolve_role_id(role, scope, definitions_client)
    object_id = _resolve_object_id(cli_ctx, assignee) if resolve_assignee else assignee
    RoleAssignmentCreateParameters = get_sdk(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                             'RoleAssignmentCreateParameters', mod='models',
                                             operation_group='role_assignments')
    parameters = RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=object_id)
    assignment_name = uuid.uuid4()
    custom_headers = None
    return assignments_client.create(scope, assignment_name, parameters, custom_headers=custom_headers)


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
        elif len(role_defs) > 1:
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


def _trim_nodepoolname(nodepool_name):
    if not nodepool_name:
        return "nodepool1"
    return nodepool_name[:12]


# pylint: disable=too-many-statements
def aks_create(cmd, client, resource_group_name, name, ssh_key_value,  # pylint: disable=too-many-locals
               dns_name_prefix=None,
               location=None,
               admin_username="azureuser",
               kubernetes_version='',
               node_vm_size="Standard_DS2_v2",
               node_osdisk_size=0,
               node_count=3,
               nodepool_name="nodepool1",
               service_principal=None, client_secret=None,
               no_ssh_key=False,
               disable_rbac=None,
               enable_rbac=None,
               enable_vmss=None,
               skip_subnet_role_assignment=False,
               enable_cluster_autoscaler=False,
               network_plugin=None,
               network_policy=None,
               pod_cidr=None,
               service_cidr=None,
               dns_service_ip=None,
               docker_bridge_address=None,
               enable_addons=None,
               workspace_resource_id=None,
               min_count=None,
               max_count=None,
               vnet_subnet_id=None,
               max_pods=0,
               aad_client_app_id=None,
               aad_server_app_id=None,
               aad_server_app_secret=None,
               aad_tenant_id=None,
               tags=None,
               node_zones=None,
               generate_ssh_keys=False,  # pylint: disable=unused-argument
               no_wait=False):
    if not no_ssh_key:
        try:
            if not ssh_key_value or not is_valid_ssh_rsa_public_key(ssh_key_value):
                raise ValueError()
        except (TypeError, ValueError):
            shortened_key = truncate_text(ssh_key_value)
            raise CLIError('Provided ssh key ({}) is invalid or non-existent'.format(shortened_key))

    subscription_id = _get_subscription_id(cmd.cli_ctx)
    if not dns_name_prefix:
        dns_name_prefix = _get_default_dns_prefix(name, resource_group_name, subscription_id)

    rg_location = _get_rg_location(cmd.cli_ctx, resource_group_name)
    if location is None:
        location = rg_location

    agent_pool_profile = ManagedClusterAgentPoolProfile(
        name=_trim_nodepoolname(nodepool_name),  # Must be 12 chars or less before ACS RP adds to it
        count=int(node_count),
        vm_size=node_vm_size,
        os_type="Linux",
        vnet_subnet_id=vnet_subnet_id,
        availability_zones=node_zones,
        max_pods=int(max_pods) if max_pods else None
    )

    if enable_vmss:
        agent_pool_profile.type = "VirtualMachineScaleSets"
    if node_osdisk_size:
        agent_pool_profile.os_disk_size_gb = int(node_osdisk_size)

    _check_cluster_autoscaler_flag(enable_cluster_autoscaler, min_count, max_count, node_count, agent_pool_profile)

    linux_profile = None
    # LinuxProfile is just used for SSH access to VMs, so omit it if --no-ssh-key was specified.
    if not no_ssh_key:
        ssh_config = ContainerServiceSshConfiguration(
            public_keys=[ContainerServiceSshPublicKey(key_data=ssh_key_value)])
        linux_profile = ContainerServiceLinuxProfile(admin_username=admin_username, ssh=ssh_config)

    principal_obj = _ensure_aks_service_principal(cmd.cli_ctx,
                                                  service_principal=service_principal, client_secret=client_secret,
                                                  subscription_id=subscription_id, dns_name_prefix=dns_name_prefix,
                                                  location=location, name=name)
    service_principal_profile = ManagedClusterServicePrincipalProfile(
        client_id=principal_obj.get("service_principal"),
        secret=principal_obj.get("client_secret"))

    if (vnet_subnet_id and not skip_subnet_role_assignment and
            not subnet_role_assignment_exists(cmd.cli_ctx, vnet_subnet_id)):
        scope = vnet_subnet_id
        if not _add_role_assignment(cmd.cli_ctx, 'Network Contributor', service_principal, scope=scope):
            logger.warning('Could not create a role assignment for subnet. '
                           'Are you an Owner on this subscription?')

    network_profile = None
    if any([network_plugin,
            pod_cidr,
            service_cidr,
            dns_service_ip,
            docker_bridge_address,
            network_policy]):
        network_profile = ContainerServiceNetworkProfile(
            network_plugin=network_plugin,
            pod_cidr=pod_cidr,
            service_cidr=service_cidr,
            dns_service_ip=dns_service_ip,
            docker_bridge_cidr=docker_bridge_address,
            network_policy=network_policy
        )

    addon_profiles = _handle_addons_args(
        cmd,
        enable_addons,
        subscription_id,
        resource_group_name,
        {},
        workspace_resource_id
    )
    if 'omsagent' in addon_profiles:
        _ensure_container_insights_for_monitoring(cmd, addon_profiles['omsagent'])
    aad_profile = None
    if any([aad_client_app_id, aad_server_app_id, aad_server_app_secret, aad_tenant_id]):
        aad_profile = ManagedClusterAADProfile(
            client_app_id=aad_client_app_id,
            server_app_id=aad_server_app_id,
            server_app_secret=aad_server_app_secret,
            tenant_id=aad_tenant_id
        )

    # Check that both --disable-rbac and --enable-rbac weren't provided
    if all([disable_rbac, enable_rbac]):
        raise CLIError('specify either "--disable-rbac" or "--enable-rbac", not both.')

    mc = ManagedCluster(
        location=location, tags=tags,
        dns_prefix=dns_name_prefix,
        kubernetes_version=kubernetes_version,
        enable_rbac=False if disable_rbac else True,
        agent_pool_profiles=[agent_pool_profile],
        linux_profile=linux_profile,
        service_principal_profile=service_principal_profile,
        network_profile=network_profile,
        addon_profiles=addon_profiles,
        aad_profile=aad_profile)

    # Due to SPN replication latency, we do a few retries here
    max_retry = 30
    retry_exception = Exception(None)
    for _ in range(0, max_retry):
        try:
            return sdk_no_wait(no_wait, client.create_or_update,
                               resource_group_name=resource_group_name, resource_name=name, parameters=mc)
        except CloudError as ex:
            retry_exception = ex
            if 'not found in Active Directory tenant' in ex.message:
                time.sleep(3)
            else:
                raise ex
    raise retry_exception


def aks_update(cmd, client, resource_group_name, name, enable_cluster_autoscaler=False,
               disable_cluster_autoscaler=False,
               update_cluster_autoscaler=False,
               min_count=None, max_count=None, no_wait=False,
               api_server_authorized_ip_ranges=None):
    update_flags = enable_cluster_autoscaler + disable_cluster_autoscaler + update_cluster_autoscaler
    if update_flags != 1 and api_server_authorized_ip_ranges is None:
        raise CLIError('Please specify "--enable-cluster-autoscaler" or '
                       '"--disable-cluster-autoscaler" or '
                       '"--update-cluster-autoscaler" or '
                       '"--api-server-authorized-ip-ranges"')

    # TODO: change this approach when we support multiple agent pools.
    instance = client.get(resource_group_name, name)
    node_count = instance.agent_pool_profiles[0].count

    if min_count is None or max_count is None:
        if enable_cluster_autoscaler or update_cluster_autoscaler:
            raise CLIError('Please specifying both min-count and max-count when --enable-cluster-autoscaler or '
                           '--update-cluster-autoscaler set.')
    if min_count is not None and max_count is not None:
        if int(min_count) > int(max_count):
            raise CLIError('value of min-count should be less than or equal to value of max-count.')
        if int(node_count) < int(min_count) or int(node_count) > int(max_count):
            raise CLIError("current node count '{}' is not in the range of min-count and max-count.".format(node_count))

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

    if api_server_authorized_ip_ranges is not None:
        instance.api_server_authorized_ip_ranges = []
        if api_server_authorized_ip_ranges != "":
            for ip in api_server_authorized_ip_ranges.split(','):
                try:
                    ip_net = ip_network(ip)
                    instance.api_server_authorized_ip_ranges.append(ip_net.with_prefixlen)
                except ValueError:
                    raise CLIError('IP addresses or CIDRs should be provided for authorized IP ranges.')

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, name, instance)


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
        for ap_profile in managed_cluster.agent_pool_profiles:
            for attr in ap_attrs:
                if getattr(ap_profile, attr, None) is None:
                    delattr(ap_profile, attr)
        for attr in sp_attrs:
            if getattr(managed_cluster.service_principal_profile, attr, None) is None:
                delattr(managed_cluster.service_principal_profile, attr)
    return managed_clusters


ADDONS = {
    'http_application_routing': 'httpApplicationRouting',
    'monitoring': 'omsagent'
}


def aks_scale(cmd, client, resource_group_name, name, node_count, nodepool_name="", no_wait=False):
    instance = client.get(resource_group_name, name)
    # TODO: change this approach when we support multiple agent pools.
    for agent_profile in instance.agent_pool_profiles:
        if agent_profile.name == nodepool_name or (nodepool_name == "" and len(instance.agent_pool_profiles) == 1):
            agent_profile.count = int(node_count)  # pylint: disable=no-member
            # null out the SP and AAD profile because otherwise validation complains
            instance.service_principal_profile = None
            instance.aad_profile = None
            return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, name, instance)
    raise CLIError('The nodepool "{}" was not found.'.format(nodepool_name))


def aks_upgrade(cmd, client, resource_group_name, name, kubernetes_version, no_wait=False, **kwargs):  # pylint: disable=unused-argument
    instance = client.managed_clusters.get(resource_group_name, name)

    if instance.kubernetes_version == kubernetes_version:
        if instance.provisioning_state == "Succeeded":
            logger.warning("The cluster is already on version %s and is not in a failed state. No operations "
                           "will occur when upgrading to the same version if the cluster is not in a failed state.",
                           instance.kubernetes_version)
        elif instance.provisioning_state == "Failed":
            logger.warning("Cluster currently in failed state. Proceeding with upgrade to existing version %s to "
                           "attempt resolution of failed cluster state.", instance.kubernetes_version)

    instance.kubernetes_version = kubernetes_version

    # null out the SP and AAD profile because otherwise validation complains
    instance.service_principal_profile = None
    instance.aad_profile = None

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, name, instance)


def _handle_addons_args(cmd, addons_str, subscription_id, resource_group_name, addon_profiles=None,
                        workspace_resource_id=None):
    if not addon_profiles:
        addon_profiles = {}
    addons = addons_str.split(',') if addons_str else []
    if 'http_application_routing' in addons:
        addon_profiles['httpApplicationRouting'] = ManagedClusterAddonProfile(enabled=True)
        addons.remove('http_application_routing')
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

    # error out if any (unrecognized) addons remain
    if addons:
        raise CLIError('"{}" {} not recognized by the --enable-addons argument.'.format(
            ",".join(addons), "are" if len(addons) > 1 else "is"))
    return addon_profiles


def _ensure_default_log_analytics_workspace_for_monitoring(cmd, subscription_id, resource_group_name):
    # log analytics workspaces cannot be created in WCUS region due to capacity limits
    # so mapped to EUS per discussion with log analytics team
    AzureLocationToOmsRegionCodeMap = {
        "eastus": "EUS",
        "westeurope": "WEU",
        "southeastasia": "SEA",
        "australiasoutheast": "ASE",
        "usgovvirginia": "USGV",
        "westcentralus": "EUS",
        "japaneast": "EJP",
        "uksouth": "SUK",
        "canadacentral": "CCA",
        "centralindia": "CIN",
        "eastus2euap": "EAP"
    }
    AzureRegionToOmsRegionMap = {
        "australiaeast": "australiasoutheast",
        "australiasoutheast": "australiasoutheast",
        "brazilsouth": "eastus",
        "canadacentral": "canadacentral",
        "canadaeast": "canadacentral",
        "centralus": "eastus",
        "eastasia": "southeastasia",
        "eastus": "eastus",
        "eastus2": "eastus",
        "japaneast": "japaneast",
        "japanwest": "japaneast",
        "northcentralus": "eastus",
        "northeurope": "westeurope",
        "southcentralus": "eastus",
        "southeastasia": "southeastasia",
        "uksouth": "uksouth",
        "ukwest": "uksouth",
        "westcentralus": "eastus",
        "westeurope": "westeurope",
        "westus": "eastus",
        "westus2": "eastus",
        "centralindia": "centralindia",
        "southindia": "centralindia",
        "westindia": "centralindia",
        "koreacentral": "southeastasia",
        "koreasouth": "southeastasia",
        "francecentral": "westeurope",
        "francesouth": "westeurope"
    }

    rg_location = _get_rg_location(cmd.cli_ctx, resource_group_name)
    default_region_name = "eastus"
    default_region_code = "EUS"

    workspace_region = AzureRegionToOmsRegionMap[
        rg_location] if AzureRegionToOmsRegionMap[rg_location] else default_region_name
    workspace_region_code = AzureLocationToOmsRegionCodeMap[
        workspace_region] if AzureLocationToOmsRegionCodeMap[workspace_region] else default_region_code

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
    workspace_resource_id = addon.config['logAnalyticsWorkspaceResourceID']

    workspace_resource_id = workspace_resource_id.strip()

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
    return _invoke_deployment(cmd.cli_ctx, resource_group, deployment_name, template, params,
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
            raise CLIError('Please specifying both min-count and max-count when --enable-cluster-autoscaler enabled')
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
    special_chars = '!#$%&*-+_.:;<>=?@][^}{|~)('
    special_char = special_chars[ord(os.urandom(1)) % len(special_chars)]
    client_secret = binascii.b2a_hex(os.urandom(10)).decode('utf-8') + special_char
    return client_secret


def aks_agentpool_show(cmd, client, resource_group_name, cluster_name, nodepool_name):
    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    return instance


def aks_agentpool_list(cmd, client, resource_group_name, cluster_name):
    return client.list(resource_group_name, cluster_name)


def aks_agentpool_add(cmd, client, resource_group_name, cluster_name, nodepool_name,
                      kubernetes_version=None,
                      node_zones=None,
                      node_vm_size="Standard_DS2_v2",
                      node_osdisk_size=0,
                      node_count=3,
                      vnet_subnet_id=None,
                      max_pods=0,
                      os_type="Linux",
                      no_wait=False):
    instances = client.list(resource_group_name, cluster_name)
    for agentpool_profile in instances:
        if agentpool_profile.name == nodepool_name:
            raise CLIError("Node pool {} already exists, please try a different name, "
                           "use 'aks nodepool list' to get current list of node pool".format(nodepool_name))

    agent_pool = AgentPool(
        name=nodepool_name,
        count=int(node_count),
        vm_size=node_vm_size,
        os_type=os_type,
        storage_profile=ContainerServiceStorageProfileTypes.managed_disks,
        vnet_subnet_id=vnet_subnet_id,
        agent_pool_type="VirtualMachineScaleSets",
        max_pods=int(max_pods) if max_pods else None,
        orchestrator_version=kubernetes_version,
        availability_zones=node_zones
    )

    if node_osdisk_size:
        agent_pool.os_disk_size_gb = int(node_osdisk_size)

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, nodepool_name, agent_pool)


def aks_agentpool_scale(cmd, client, resource_group_name, cluster_name,
                        nodepool_name,
                        node_count=3,
                        no_wait=False):
    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    instance.count = int(node_count)  # pylint: disable=no-member
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


def aks_agentpool_upgrade(cmd, client, resource_group_name, cluster_name,
                          kubernetes_version,
                          nodepool_name,
                          no_wait=False):
    instance = client.get(resource_group_name, cluster_name, nodepool_name)
    instance.orchestrator_version = kubernetes_version

    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name, cluster_name, nodepool_name, instance)


def aks_agentpool_delete(cmd, client, resource_group_name, cluster_name,
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
