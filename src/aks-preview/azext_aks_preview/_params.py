# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,too-many-statements

import os.path
import platform

from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import (
    file_type, get_resource_name_completion_list, get_three_state_flag, name_type, tags_type, zones_type, get_enum_type)
from knack.arguments import CLIArgumentType

from ._completers import (
    get_vm_size_completion_list, get_k8s_versions_completion_list, get_k8s_upgrades_completion_list, get_ossku_completion_list)
from ._validators import (
    validate_cluster_autoscaler_profile, validate_create_parameters, validate_k8s_version, validate_linux_host_name,
    validate_ssh_key, validate_nodes_count, validate_ip_ranges,
    validate_nodepool_name, validate_vm_set_type, validate_load_balancer_sku,
    validate_load_balancer_outbound_ips, validate_load_balancer_outbound_ip_prefixes,
    validate_taints, validate_priority, validate_eviction_policy, validate_spot_max_price, validate_acr, validate_user,
    validate_load_balancer_outbound_ports, validate_load_balancer_idle_timeout, validate_nodepool_tags,
    validate_nodepool_labels, validate_vnet_subnet_id, validate_pod_subnet_id, validate_max_surge, validate_assign_identity, validate_addons,
    validate_pod_identity_pod_labels, validate_pod_identity_resource_name, validate_pod_identity_resource_namespace, validate_assign_kubelet_identity)
from ._consts import CONST_OUTBOUND_TYPE_LOAD_BALANCER, \
    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING, CONST_SCALE_SET_PRIORITY_REGULAR, CONST_SCALE_SET_PRIORITY_SPOT, \
    CONST_SPOT_EVICTION_POLICY_DELETE, CONST_SPOT_EVICTION_POLICY_DEALLOCATE, \
    CONST_NODEPOOL_MODE_SYSTEM, CONST_NODEPOOL_MODE_USER, \
    CONST_OS_DISK_TYPE_MANAGED, CONST_OS_DISK_TYPE_EPHEMERAL, \
    CONST_RAPID_UPGRADE_CHANNEL, CONST_STABLE_UPGRADE_CHANNEL, CONST_PATCH_UPGRADE_CHANNEL, CONST_NODE_IMAGE_UPGRADE_CHANNEL, CONST_NONE_UPGRADE_CHANNEL


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
        c.argument('enable_ahub', options_list=['--enable-ahub'])
        c.argument('dns_name_prefix', options_list=['--dns-name-prefix', '-p'])
        c.argument('generate_ssh_keys', action='store_true', validator=validate_create_parameters)
        c.argument('node_vm_size', options_list=['--node-vm-size', '-s'], completer=get_vm_size_completion_list)
        c.argument('nodepool_name', type=str, default='nodepool1',
                   help='Node pool name, upto 12 alphanumeric characters', validator=validate_nodepool_name)
        c.argument('nodepool_tags', nargs='*', validator=validate_nodepool_tags, help='space-separated tags: key[=value] [key[=value] ...]. Use "" to clear existing tags.')
        c.argument('nodepool_labels', nargs='*', validator=validate_nodepool_labels, help='space-separated labels: key[=value] [key[=value] ...]. You can not change the node labels through CLI after creation. See https://aka.ms/node-labels for syntax of labels.')
        c.argument('os_sku', type=str, options_list=['--os-sku'], completer=get_ossku_completion_list)
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
        c.argument('enable_addons', options_list=['--enable-addons', '-a'], validator=validate_addons)
        c.argument('disable_rbac', action='store_true')
        c.argument('enable_rbac', action='store_true', options_list=['--enable-rbac', '-r'],
                   deprecate_info=c.deprecate(redirect="--disable-rbac", hide="2.0.45"))
        c.argument('max_pods', type=int, options_list=['--max-pods', '-m'])
        c.argument('network_plugin', arg_type=get_enum_type(['azure', 'kubenet']))
        c.argument('network_policy')
        c.argument('no_ssh_key', options_list=['--no-ssh-key', '-x'])
        c.argument('pod_cidr')
        c.argument('service_cidr')
        c.argument('vnet_subnet_id', type=str, validator=validate_vnet_subnet_id)
        c.argument('pod_subnet_id', type=str, validator=validate_pod_subnet_id)
        c.argument('ppg')
        c.argument('workspace_resource_id')
        c.argument('skip_subnet_role_assignment', action='store_true')
        c.argument('enable_fips_image', action='store_true', is_preview=True)
        c.argument('enable_cluster_autoscaler', action='store_true')
        c.argument('uptime_sla', action='store_true')
        c.argument('cluster_autoscaler_profile', nargs='+', validator=validate_cluster_autoscaler_profile)
        c.argument('min_count', type=int, validator=validate_nodes_count)
        c.argument('max_count', type=int, validator=validate_nodes_count)
        c.argument('enable_vmss', action='store_true', help='To be deprecated. Use vm_set_type instead.')
        c.argument('vm_set_type', type=str, validator=validate_vm_set_type)
        c.argument('node_zones', zones_type, options_list=['--node-zones', '--zones', '-z'], help='(--node-zones will be deprecated, use --zones) Space-separated list of availability zones where agent nodes will be placed.')
        c.argument('enable_node_public_ip', action='store_true')
        c.argument('node_public_ip_prefix_id', type=str)
        c.argument('enable_pod_security_policy', action='store_true')
        c.argument('node_resource_group')
        c.argument('attach_acr', acr_arg_type)
        c.argument('api_server_authorized_ip_ranges', type=str, validator=validate_ip_ranges)
        c.argument('enable_ahub', options_list=['--enable-ahub'])
        c.argument('disable_ahub', options_list=['--disable-ahub'])
        c.argument('aks_custom_headers')
        c.argument('enable_private_cluster', action='store_true')
        c.argument('private_dns_zone')
        c.argument('fqdn_subdomain')
        c.argument('enable_managed_identity', action='store_true')
        c.argument('assign_identity', type=str, validator=validate_assign_identity)
        c.argument('enable_sgxquotehelper', action='store_true')
        c.argument('auto_upgrade_channel', arg_type=get_enum_type([CONST_RAPID_UPGRADE_CHANNEL, CONST_STABLE_UPGRADE_CHANNEL, CONST_PATCH_UPGRADE_CHANNEL, CONST_NODE_IMAGE_UPGRADE_CHANNEL, CONST_NONE_UPGRADE_CHANNEL]))
        c.argument('kubelet_config', type=str)
        c.argument('linux_os_config', type=str)
        c.argument('enable_pod_identity', action='store_true')
        c.argument('appgw_name', options_list=['--appgw-name'], arg_group='Application Gateway')
        c.argument('appgw_subnet_prefix', options_list=['--appgw-subnet-prefix'], arg_group='Application Gateway', deprecate_info=c.deprecate(redirect='--appgw-subnet-cidr', hide=True))
        c.argument('appgw_subnet_cidr', options_list=['--appgw-subnet-cidr'], arg_group='Application Gateway')
        c.argument('appgw_id', options_list=['--appgw-id'], arg_group='Application Gateway')
        c.argument('appgw_subnet_id', options_list=['--appgw-subnet-id'], arg_group='Application Gateway')
        c.argument('appgw_watch_namespace', options_list=['--appgw-watch-namespace'], arg_group='Application Gateway')
        c.argument('aci_subnet_name', type=str)
        c.argument('enable_encryption_at_host', arg_type=get_three_state_flag(), help='Enable EncryptionAtHost.')
        c.argument('enable_secret_rotation', action='store_true')
        c.argument('assign_kubelet_identity', type=str, validator=validate_assign_kubelet_identity)
        c.argument('disable_local_accounts', action='store_true')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('aks update') as c:
        c.argument('enable_cluster_autoscaler', options_list=["--enable-cluster-autoscaler", "-e"], action='store_true')
        c.argument('disable_cluster_autoscaler', options_list=["--disable-cluster-autoscaler", "-d"], action='store_true')
        c.argument('update_cluster_autoscaler', options_list=["--update-cluster-autoscaler", "-u"], action='store_true')
        c.argument('cluster_autoscaler_profile', nargs='+', validator=validate_cluster_autoscaler_profile)
        c.argument('min_count', type=int, validator=validate_nodes_count)
        c.argument('max_count', type=int, validator=validate_nodes_count)
        c.argument('uptime_sla', action='store_true')
        c.argument('no_uptime_sla', action='store_true')
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
        c.argument('aks_custom_headers')
        c.argument('auto_upgrade_channel', arg_type=get_enum_type([CONST_RAPID_UPGRADE_CHANNEL, CONST_STABLE_UPGRADE_CHANNEL, CONST_PATCH_UPGRADE_CHANNEL, CONST_NODE_IMAGE_UPGRADE_CHANNEL, CONST_NONE_UPGRADE_CHANNEL]))
        c.argument('enable_managed_identity', action='store_true')
        c.argument('assign_identity', type=str, validator=validate_assign_identity)
        c.argument('enable_pod_identity', action='store_true')
        c.argument('disable_pod_identity', action='store_true')
        c.argument('enable_secret_rotation', action='store_true')
        c.argument('disable_secret_rotation', action='store_true')
        c.argument('windows_admin_password', options_list=['--windows-admin-password'])
        c.argument('disable_local_accounts', action='store_true')
        c.argument('enable_local_accounts', action='store_true')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('aks scale') as c:
        c.argument('nodepool_name', type=str,
                   help='Node pool name, upto 12 alphanumeric characters', validator=validate_nodepool_name)

    with self.argument_context('aks upgrade') as c:
        c.argument('kubernetes_version', completer=get_k8s_upgrades_completion_list)
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('aks maintenanceconfiguration') as c:
        c.argument('cluster_name', type=str, help='The cluster name.')

    for scope in ['aks maintenanceconfiguration add', 'aks maintenanceconfiguration update']:
        with self.argument_context(scope) as c:
            c.argument('config_name', type=str, options_list=['--name', '-n'], help='The config name.')
            c.argument('config_file', type=str, options_list=['--config-file'], help='The config json file.', required=False)
            c.argument('weekday', type=str, options_list=['--weekday'], help='weekday on which maintenance can happen. e.g. Monday', required=False)
            c.argument('start_hour', type=int, options_list=['--start-hour'], help='maintenance start hour of 1 hour window on the weekday. e.g. 1 means 1:00am - 2:00am', required=False)

    for scope in ['aks maintenanceconfiguration show', 'aks maintenanceconfiguration delete']:
        with self.argument_context(scope) as c:
            c.argument('config_name', type=str, options_list=['--name', '-n'], help='The config name.')

    with self.argument_context('aks nodepool') as c:
        c.argument('cluster_name', type=str, help='The cluster name.')

    with self.argument_context('aks command invoke') as c:
        c.argument('command_string', type=str, options_list=["--command", "-c"], help='the command to run')
        c.argument('command_files', options_list=["--file", "-f"], required=False, action="append", help='attach any files the command may use, or use \'.\' to upload the current folder.')

    with self.argument_context('aks command result') as c:
        c.argument('command_id', type=str, options_list=["--command-id", "-i"], help='the command ID from "aks command invoke"')

    for scope in ['aks nodepool add']:
        with self.argument_context(scope) as c:
            c.argument('nodepool_name', type=str, options_list=['--name', '-n'], validator=validate_nodepool_name, help='The node pool name.')
            c.argument('tags', tags_type)
            c.argument('node_zones', zones_type, options_list=['--node-zones', '--zones', '-z'], help='(--node-zones will be deprecated) Space-separated list of availability zones where agent nodes will be placed.')
            c.argument('enable_node_public_ip', action='store_true')
            c.argument('node_public_ip_prefix_id', type=str)
            c.argument('node_vm_size', options_list=['--node-vm-size', '-s'], completer=get_vm_size_completion_list)
            c.argument('max_pods', type=int, options_list=['--max-pods', '-m'])
            c.argument('os_type', type=str)
            c.argument('os_sku', type=str, options_list=['--os-sku'], completer=get_ossku_completion_list)
            c.argument('enable_fips_image', action='store_true', is_preview=True)
            c.argument('enable_cluster_autoscaler', options_list=["--enable-cluster-autoscaler", "-e"], action='store_true')
            c.argument('node_taints', type=str, validator=validate_taints)
            c.argument('priority', arg_type=get_enum_type([CONST_SCALE_SET_PRIORITY_REGULAR, CONST_SCALE_SET_PRIORITY_SPOT]), validator=validate_priority)
            c.argument('eviction_policy', arg_type=get_enum_type([CONST_SPOT_EVICTION_POLICY_DELETE, CONST_SPOT_EVICTION_POLICY_DEALLOCATE]), validator=validate_eviction_policy)
            c.argument('spot_max_price', type=float, validator=validate_spot_max_price)
            c.argument('labels', nargs='*', validator=validate_nodepool_labels)
            c.argument('mode', arg_type=get_enum_type([CONST_NODEPOOL_MODE_SYSTEM, CONST_NODEPOOL_MODE_USER]))
            c.argument('aks_custom_headers')
            c.argument('ppg')
            c.argument('max_surge', type=str, validator=validate_max_surge)
            c.argument('node_os_disk_type', arg_type=get_enum_type([CONST_OS_DISK_TYPE_MANAGED, CONST_OS_DISK_TYPE_EPHEMERAL]))
            c.argument('vnet_subnet_id', type=str, validator=validate_vnet_subnet_id)
            c.argument('pod_subnet_id', type=str, validator=validate_pod_subnet_id)
            c.argument('kubelet_config', type=str)
            c.argument('linux_os_config', type=str)
            c.argument('enable_encryption_at_host', options_list=['--enable-encryption-at-host'], action='store_true')

    for scope in ['aks nodepool show', 'aks nodepool delete', 'aks nodepool scale', 'aks nodepool upgrade', 'aks nodepool update']:
        with self.argument_context(scope) as c:
            c.argument('nodepool_name', type=str, options_list=['--name', '-n'], validator=validate_nodepool_name, help='The node pool name.')

    with self.argument_context('aks nodepool upgrade') as c:
        c.argument('max_surge', type=str, validator=validate_max_surge)

    with self.argument_context('aks nodepool update') as c:
        c.argument('enable_cluster_autoscaler', options_list=["--enable-cluster-autoscaler", "-e"], action='store_true')
        c.argument('disable_cluster_autoscaler', options_list=["--disable-cluster-autoscaler", "-d"], action='store_true')
        c.argument('update_cluster_autoscaler', options_list=["--update-cluster-autoscaler", "-u"], action='store_true')
        c.argument('tags', tags_type)
        c.argument('mode', arg_type=get_enum_type([CONST_NODEPOOL_MODE_SYSTEM, CONST_NODEPOOL_MODE_USER]))
        c.argument('max_surge', type=str, validator=validate_max_surge)

    with self.argument_context('aks disable-addons') as c:
        c.argument('addons', options_list=['--addons', '-a'], validator=validate_addons)

    with self.argument_context('aks enable-addons') as c:
        c.argument('addons', options_list=['--addons', '-a'], validator=validate_addons)
        c.argument('subnet_name', options_list=['--subnet-name', '-s'])
        c.argument('enable_sgxquotehelper', action='store_true')
        c.argument('osm_mesh_name', options_list=['--osm-mesh-name'])
        c.argument('appgw_name', options_list=['--appgw-name'], arg_group='Application Gateway')
        c.argument('appgw_subnet_prefix', options_list=['--appgw-subnet-prefix'], arg_group='Application Gateway', deprecate_info=c.deprecate(redirect='--appgw-subnet-cidr', hide=True))
        c.argument('appgw_subnet_cidr', options_list=['--appgw-subnet-cidr'], arg_group='Application Gateway')
        c.argument('appgw_id', options_list=['--appgw-id'], arg_group='Application Gateway')
        c.argument('appgw_subnet_id', options_list=['--appgw-subnet-id'], arg_group='Application Gateway')
        c.argument('appgw_watch_namespace', options_list=['--appgw-watch-namespace'], arg_group='Application Gateway')
        c.argument('enable_secret_rotation', action='store_true')

    with self.argument_context('aks get-credentials') as c:
        c.argument('admin', options_list=['--admin', '-a'], default=False)
        c.argument('context_name', options_list=['--context'],
                   help='If specified, overwrite the default context name.')
        c.argument('user', options_list=['--user', '-u'], default='clusterUser', validator=validate_user)
        c.argument('path', options_list=['--file', '-f'], type=file_type, completer=FilesCompleter(),
                   default=os.path.join(os.path.expanduser('~'), '.kube', 'config'))

    with self.argument_context('aks pod-identity') as c:
        c.argument('cluster_name', type=str, help='The cluster name.')

    with self.argument_context('aks pod-identity add') as c:
        c.argument('identity_name', type=str, options_list=['--name', '-n'], default=None, required=False,
                   help='The pod identity name. Generate if not specified.',
                   validator=validate_pod_identity_resource_name('identity_name', required=False))
        c.argument('identity_namespace', type=str, options_list=['--namespace'], help='The pod identity namespace.')
        c.argument('identity_resource_id', type=str, options_list=['--identity-resource-id'], help='Resource id of the identity to use.')
        c.argument('binding_selector', type=str, options_list=['--binding-selector'], help='Optional binding selector to use.')

    with self.argument_context('aks pod-identity delete') as c:
        c.argument('identity_name', type=str, options_list=['--name', '-n'], default=None, required=True,
                   help='The pod identity name.',
                   validator=validate_pod_identity_resource_name('identity_name', required=True))
        c.argument('identity_namespace', type=str, options_list=['--namespace'], help='The pod identity namespace.')

    with self.argument_context('aks pod-identity exception add') as c:
        c.argument('exc_name', type=str, options_list=['--name', '-n'], default=None, required=False,
                   help='The pod identity exception name. Generate if not specified.',
                   validator=validate_pod_identity_resource_name('exc_name', required=False))
        c.argument('exc_namespace', type=str, options_list=['--namespace'], required=True,
                   help='The pod identity exception namespace.',
                   validator=validate_pod_identity_resource_namespace)
        c.argument('pod_labels', nargs='*', required=True,
                   help='space-separated labels: key=value [key=value ...].',
                   validator=validate_pod_identity_pod_labels)

    with self.argument_context('aks pod-identity exception delete') as c:
        c.argument('exc_name', type=str, options_list=['--name', '-n'], required=True,
                   help='The pod identity exception name to remove.',
                   validator=validate_pod_identity_resource_name('exc_name', required=True))
        c.argument('exc_namespace', type=str, options_list=['--namespace'], required=True,
                   help='The pod identity exception namespace to remove.',
                   validator=validate_pod_identity_resource_namespace)

    with self.argument_context('aks pod-identity exception update') as c:
        c.argument('exc_name', type=str, options_list=['--name', '-n'], required=True,
                   help='The pod identity exception name to remove.',
                   validator=validate_pod_identity_resource_name('exc_name', required=True))
        c.argument('exc_namespace', type=str, options_list=['--namespace'], required=True,
                   help='The pod identity exception namespace to remove.',
                   validator=validate_pod_identity_resource_namespace)
        c.argument('pod_labels', nargs='*', required=True,
                   help='pod labels in key=value [key=value ...].',
                   validator=validate_pod_identity_pod_labels)


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
