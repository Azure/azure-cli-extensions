# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,too-many-statements

import os.path
import platform

from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import (
    file_type, get_resource_name_completion_list, name_type, tags_type, zones_type, get_enum_type)
from knack.arguments import CLIArgumentType

from ._completers import (
    get_vm_size_completion_list, get_k8s_versions_completion_list, get_k8s_upgrades_completion_list)
from ._validators import (
    validate_create_parameters, validate_k8s_version, validate_linux_host_name,
    validate_ssh_key, validate_max_pods, validate_nodes_count, validate_ip_ranges,
    validate_nodepool_name, validate_vm_set_type, validate_load_balancer_sku,
    validate_load_balancer_outbound_ips, validate_load_balancer_outbound_ip_prefixes,
    validate_taints, validate_priority, validate_eviction_policy, validate_acr, validate_user,
    validate_load_balancer_outbound_ports, validate_load_balancer_idle_timeout)
from ._consts import CONST_OUTBOUND_TYPE_LOAD_BALANCER, CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING


def load_arguments(self, _):

    acr_arg_type = CLIArgumentType(metavar='ACR_NAME_OR_RESOURCE_ID')

    # AKS command argument configuration
    with self.argument_context('aks') as c:
        c.argument('resource_name', name_type, help='Name of the managed cluster.',
                   completer=get_resource_name_completion_list('Microsoft.ContainerService/ManagedClusters'))
        c.argument('name', name_type, help='Name of the managed cluster.',
                   completer=get_resource_name_completion_list('Microsoft.ContainerService/ManagedClusters'))
        c.argument('kubernetes_version', options_list=['--kubernetes-version', '-k'], validator=validate_k8s_version)
        c.argument('node_count', options_list=['--node-count', '-c'], type=int)
        c.argument('tags', tags_type)

    with self.argument_context('aks create') as c:
        c.argument('name', validator=validate_linux_host_name)
        c.argument('kubernetes_version', completer=get_k8s_versions_completion_list)
        c.argument('admin_username', options_list=['--admin-username', '-u'], default='azureuser')
        c.argument('windows_admin_username', options_list=['--windows-admin-username'])
        c.argument('windows_admin_password', options_list=['--windows-admin-password'])
        c.argument('dns_name_prefix', options_list=['--dns-name-prefix', '-p'])
        c.argument('generate_ssh_keys', action='store_true', validator=validate_create_parameters)
        c.argument('node_vm_size', options_list=['--node-vm-size', '-s'], completer=get_vm_size_completion_list)
        c.argument('nodepool_name', type=str, default='nodepool1',
                   help='Node pool name, upto 12 alphanumeric characters', validator=validate_nodepool_name)
        c.argument('ssh_key_value', required=False, type=file_type, default=os.path.join('~', '.ssh', 'id_rsa.pub'),
                   completer=FilesCompleter(), validator=validate_ssh_key)
        c.argument('aad_client_app_id')
        c.argument('aad_server_app_id')
        c.argument('aad_server_app_secret')
        c.argument('aad_tenant_id')
        c.argument('dns_service_ip')
        c.argument('docker_bridge_address')
        c.argument('load_balancer_sku', type=str, validator=validate_load_balancer_sku)
        c.argument('load_balancer_managed_outbound_ip_count', type=int)
        c.argument('load_balancer_outbound_ips', type=str, validator=validate_load_balancer_outbound_ips)
        c.argument('load_balancer_outbound_ip_prefixes', type=str, validator=validate_load_balancer_outbound_ip_prefixes)
        c.argument('load_balancer_outbound_ports', type=int, validator=validate_load_balancer_outbound_ports)
        c.argument('load_balancer_idle_timeout', type=int, validator=validate_load_balancer_idle_timeout)
        c.argument('outbound_type', arg_type=get_enum_type([CONST_OUTBOUND_TYPE_LOAD_BALANCER,
                                                            CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING]))
        c.argument('enable_addons', options_list=['--enable-addons', '-a'])
        c.argument('disable_rbac', action='store_true')
        c.argument('enable_rbac', action='store_true', options_list=['--enable-rbac', '-r'],
                   deprecate_info=c.deprecate(redirect="--disable-rbac", hide="2.0.45"))
        c.argument('max_pods', type=int, options_list=['--max-pods', '-m'], validator=validate_max_pods)
        c.argument('network_plugin')
        c.argument('network_policy')
        c.argument('no_ssh_key', options_list=['--no-ssh-key', '-x'])
        c.argument('pod_cidr')
        c.argument('service_cidr')
        c.argument('vnet_subnet_id')
        c.argument('workspace_resource_id')
        c.argument('skip_subnet_role_assignment', action='store_true')
        c.argument('enable_cluster_autoscaler', action='store_true')
        c.argument('min_count', type=int, validator=validate_nodes_count)
        c.argument('max_count', type=int, validator=validate_nodes_count)
        c.argument('enable_vmss', action='store_true', help='To be deprecated. Use vm_set_type instead.')
        c.argument('vm_set_type', type=str, validator=validate_vm_set_type)
        c.argument('node_zones', zones_type, options_list=['--node-zones', '--zones', '-z'], help='(--node-zones will be deprecated, use --zones) Space-separated list of availability zones where agent nodes will be placed.')
        c.argument('enable_pod_security_policy', action='store_true')
        c.argument('node_resource_group')
        c.argument('attach_acr', acr_arg_type, validator=validate_acr)
        c.argument('api_server_authorized_ip_ranges', type=str, validator=validate_ip_ranges)
        c.argument('aks_custom_headers')
        c.argument('enable_private_cluster', action='store_true')
        c.argument('enable_managed_identity', action='store_true')

    with self.argument_context('aks update') as c:
        c.argument('enable_cluster_autoscaler', options_list=["--enable-cluster-autoscaler", "-e"], action='store_true')
        c.argument('disable_cluster_autoscaler', options_list=["--disable-cluster-autoscaler", "-d"], action='store_true')
        c.argument('update_cluster_autoscaler', options_list=["--update-cluster-autoscaler", "-u"], action='store_true')
        c.argument('min_count', type=int, validator=validate_nodes_count)
        c.argument('max_count', type=int, validator=validate_nodes_count)
        c.argument('load_balancer_managed_outbound_ip_count', type=int)
        c.argument('load_balancer_outbound_ips', type=str, validator=validate_load_balancer_outbound_ips)
        c.argument('load_balancer_outbound_ip_prefixes', type=str, validator=validate_load_balancer_outbound_ip_prefixes)
        c.argument('load_balancer_outbound_ports', type=int, validator=validate_load_balancer_outbound_ports)
        c.argument('load_balancer_idle_timeout', type=int, validator=validate_load_balancer_idle_timeout)
        c.argument('api_server_authorized_ip_ranges', type=str, validator=validate_ip_ranges)
        c.argument('enable_pod_security_policy', action='store_true')
        c.argument('disable_pod_security_policy', action='store_true')
        c.argument('attach_acr', acr_arg_type, validator=validate_acr)
        c.argument('detach_acr', acr_arg_type, validator=validate_acr)

    with self.argument_context('aks scale') as c:
        c.argument('nodepool_name', type=str,
                   help='Node pool name, upto 12 alphanumeric characters', validator=validate_nodepool_name)

    with self.argument_context('aks upgrade') as c:
        c.argument('kubernetes_version', completer=get_k8s_upgrades_completion_list)

    with self.argument_context('aks nodepool') as c:
        c.argument('cluster_name', type=str, help='The cluster name.')

    for scope in ['aks nodepool add']:
        with self.argument_context(scope) as c:
            c.argument('nodepool_name', type=str, options_list=['--name', '-n'], validator=validate_nodepool_name, help='The node pool name.')
            c.argument('node_zones', zones_type, options_list=['--node-zones', '--zones', '-z'], help='(--node-zones will be deprecated) Space-separated list of availability zones where agent nodes will be placed.')
            c.argument('node_vm_size', options_list=['--node-vm-size', '-s'], completer=get_vm_size_completion_list)
            c.argument('max_pods', type=int, options_list=['--max-pods', '-m'], validator=validate_max_pods)
            c.argument('os_type', type=str)
            c.argument('enable_cluster_autoscaler', options_list=["--enable-cluster-autoscaler", "-e"], action='store_true')
            c.argument('node_taints', type=str, validator=validate_taints)
            c.argument('priority', type=str, validator=validate_priority)
            c.argument('eviction_policy', type=str, validator=validate_eviction_policy)

    for scope in ['aks nodepool show', 'aks nodepool delete', 'aks nodepool scale', 'aks nodepool upgrade', 'aks nodepool update']:
        with self.argument_context(scope) as c:
            c.argument('nodepool_name', type=str, options_list=['--name', '-n'], validator=validate_nodepool_name, help='The node pool name.')

    with self.argument_context('aks nodepool update') as c:
        c.argument('enable_cluster_autoscaler', options_list=["--enable-cluster-autoscaler", "-e"], action='store_true')
        c.argument('disable_cluster_autoscaler', options_list=["--disable-cluster-autoscaler", "-d"], action='store_true')
        c.argument('update_cluster_autoscaler', options_list=["--update-cluster-autoscaler", "-u"], action='store_true')

    with self.argument_context('aks disable-addons') as c:
        c.argument('addons', options_list=['--addons', '-a'])

    with self.argument_context('aks enable-addons') as c:
        c.argument('addons', options_list=['--addons', '-a'])
        c.argument('subnet_name', options_list=['--subnet-name', '-s'])

    with self.argument_context('aks get-credentials') as c:
        c.argument('admin', options_list=['--admin', '-a'], default=False)
        c.argument('user', options_list=['--user', '-u'], default='clusterUser', validator=validate_user)
        c.argument('path', options_list=['--file', '-f'], type=file_type, completer=FilesCompleter(),
                   default=os.path.join(os.path.expanduser('~'), '.kube', 'config'))


def _get_default_install_location(exe_name):
    system = platform.system()
    if system == 'Windows':
        home_dir = os.environ.get('USERPROFILE')
        if not home_dir:
            return None
        install_location = os.path.join(home_dir, r'.azure-{0}\{0}.exe'.format(exe_name))
    elif system in ('Linux', 'Darwin'):
        install_location = '/usr/local/bin/{}'.format(exe_name)
    else:
        install_location = None
    return install_location
