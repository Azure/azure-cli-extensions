# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,too-many-statements

import os.path
import platform

from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import (
    file_type, get_resource_name_completion_list, name_type, tags_type)

from ._completers import (
    get_vm_size_completion_list, get_k8s_versions_completion_list, get_k8s_upgrades_completion_list)
from ._validators import (
    validate_create_parameters, validate_k8s_version, validate_linux_host_name,
    validate_ssh_key, validate_max_pods, validate_nodes_count)


def load_arguments(self, _):

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
        c.argument('dns_name_prefix', options_list=['--dns-name-prefix', '-p'])
        c.argument('generate_ssh_keys', action='store_true', validator=validate_create_parameters)
        c.argument('node_vm_size', options_list=['--node-vm-size', '-s'], completer=get_vm_size_completion_list)
        c.argument('ssh_key_value', required=False, type=file_type, default=os.path.join('~', '.ssh', 'id_rsa.pub'),
                   completer=FilesCompleter(), validator=validate_ssh_key)
        c.argument('aad_client_app_id')
        c.argument('aad_server_app_id')
        c.argument('aad_server_app_secret')
        c.argument('aad_tenant_id')
        c.argument('dns_service_ip')
        c.argument('docker_bridge_address')
        c.argument('enable_addons', options_list=['--enable-addons', '-a'])
        c.argument('disable_rbac', action='store_true')
        c.argument('enable_rbac', action='store_true', options_list=['--enable-rbac', '-r'],
                   deprecate_info=c.deprecate(redirect="--disable-rbac", hide="2.0.45"))
        c.argument('max_pods', type=int, options_list=['--max-pods', '-m'], validator=validate_max_pods)
        c.argument('network_plugin')
        c.argument('no_ssh_key', options_list=['--no-ssh-key', '-x'])
        c.argument('pod_cidr')
        c.argument('service_cidr')
        c.argument('vnet_subnet_id')
        c.argument('workspace_resource_id')
        c.argument('skip_subnet_role_assignment', action='store_true')
        c.argument('enable_cluster_autoscaler', action='store_true')
        c.argument('min_count', type=int, validator=validate_nodes_count)
        c.argument('max_count', type=int, validator=validate_nodes_count)

    with self.argument_context('aks update') as c:
        c.argument('enable_cluster_autoscaler', options_list=["--enable-cluster-autoscaler", "-e"], action='store_true')
        c.argument('disable_cluster_autoscaler', options_list=["--disable-cluster-autoscaler", "-d"], action='store_true')
        c.argument('update_cluster_autoscaler', options_list=["--update-cluster-autoscaler", "-u"], action='store_true')
        c.argument('min_count', type=int, validator=validate_nodes_count)
        c.argument('max_count', type=int, validator=validate_nodes_count)

    with self.argument_context('aks upgrade') as c:
        c.argument('kubernetes_version', completer=get_k8s_upgrades_completion_list)


def _get_default_install_location(exe_name):
    system = platform.system()
    if system == 'Windows':
        home_dir = os.environ.get('USERPROFILE')
        if not home_dir:
            return None
        install_location = os.path.join(home_dir, r'.azure-{0}\{0}.exe'.format(exe_name))
    elif system == 'Linux' or system == 'Darwin':
        install_location = '/usr/local/bin/{}'.format(exe_name)
    else:
        install_location = None
    return install_location
