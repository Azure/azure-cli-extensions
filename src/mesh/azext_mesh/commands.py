# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from __future__ import print_function
from collections import OrderedDict

from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands import CliCommandType

from azure.cli.command_modules.resource._validators import process_deployment_create_namespace
from ._client_factory import (cf_mesh_deployments,
                              cf_mesh_application, cf_mesh_service,
                              cf_mesh_replica, cf_mesh_code_package, cf_mesh_network,
                              cf_mesh_volume)
from ._exception_handler import resource_exception_handler


def transform_log_output(result):
    """Print log. """
    return result


def transform_application(result):
    """Transform an application to table output. """
    return OrderedDict([('Name', result['name']),
                        ('ResourceGroup', result['resourceGroup']),
                        ('ProvisioningState', result['provisioningState']),
                        ('Location', result['location'])])


def transform_application_list(result):
    """Transform an application list to table output. """
    return [transform_application(application) for application in result]


def transform_network(result):
    """Transform a network to table output. """
    ingressConfig = result.get('ingressConfig')
    if ingressConfig is not None:
        return OrderedDict([('Name', result['name']),
                            ('Description', result['description']),
                            ('ProvisioningState', result['provisioningState']),
                            ('PublicIP', ingressConfig['publicIpAddress']),
                            ('AddressPrefix', result['addressPrefix'])])
    return OrderedDict([('Name', result['name']),
                        ('Description', result['description']),
                        ('ProvisioningState', result['provisioningState']),
                        ('AddressPrefix', result['addressPrefix'])])


def transform_network_list(result):
    """Transform a network list to table output. """
    return [transform_network(network) for network in result]


def format_cpu_memory(container_group):
    """Format CPU and memory. """
    containers = container_group.get('containers')
    if containers is not None and containers:
        total_cpu = 0
        total_memory = 0
        for container in containers:
            resources = container.get('resources')
            if resources is not None:
                resources_requests = resources.get('requests')
                if resources_requests is not None:
                    total_cpu += resources_requests.get('cpu', 0)
                    total_memory += resources_requests.get('memoryInGb', 0)
            return '{0} core/{1} gb'.format(total_cpu, total_memory)
    return None


def format_ip_address(container_group):
    """Format IP address. """
    ip_address = container_group.get('ipAddress')
    if ip_address is not None:
        ports = ','.join(str(p['port']) for p in ip_address['ports'])
        return '{0}:{1}'.format(ip_address.get('ip'), ports)
    return None


def transform_volume(result):
    """Transform a volume to table output. """
    return OrderedDict([('Name', result['name']),
                        ('ResourceGroup', result['resourceGroup']),
                        ('Location', result['location']),
                        ('ProvisioningState', result.get('provisioningState')),
                        ('Provider', result.get('provider'))])


def transform_volume_list(result):
    """Transform a volume list to table output. """
    return [transform_volume(volume) for volume in result]


def load_command_table(self, _):
    cmd_util = CliCommandType(
        operations_tmpl='azext_mesh.custom#{}',
        exception_handler=resource_exception_handler
    )

    mesh_service_util = CliCommandType(
        operations_tmpl='azext_mesh.servicefabricmesh.mgmt.servicefabricmesh.operations.service_operations#ServiceOperations.{}',
        exception_handler=resource_exception_handler
    )

    mesh_replica_util = CliCommandType(
        operations_tmpl='azext_mesh.servicefabricmesh.mgmt.servicefabricmesh.operations.replica_operations#ReplicaOperations.{}',
        exception_handler=resource_exception_handler
    )

    mesh_cp_util = CliCommandType(
        operations_tmpl='azext_mesh.servicefabricmesh.mgmt.servicefabricmesh.operations.code_package_operations#CodePackageOperations.{}',
        exception_handler=resource_exception_handler
    )

    mesh_network_util = CliCommandType(
        operations_tmpl='azext_mesh.servicefabricmesh.mgmt.servicefabricmesh.operations.network_operations#NetworkOperations.{}',
        exception_handler=resource_exception_handler
    )

    resource_deployment_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.resource.resources.operations.deployments_operations#DeploymentsOperations.{}',
        client_factory=cf_mesh_deployments,
        resource_type=ResourceType.MGMT_RESOURCE_RESOURCES,
        exception_handler=resource_exception_handler
    )

    with self.command_group('mesh deployment', resource_deployment_sdk) as g:
        g.custom_command('create', 'deploy_arm_template', supports_no_wait=True, validator=process_deployment_create_namespace)

    with self.command_group('mesh app', cmd_util) as g:
        g.custom_command('list', 'list_application', client_factory=cf_mesh_application, table_transformer=transform_application_list, exception_handler=resource_exception_handler)
        g.custom_command('show', 'show_application', client_factory=cf_mesh_application, table_transformer=transform_application, exception_handler=resource_exception_handler)
        g.custom_command('delete', 'delete_application', client_factory=cf_mesh_application, confirmation=True)

    with self.command_group('mesh service', mesh_service_util, client_factory=cf_mesh_service) as g:
        g.command('list', 'list_by_application_name')
        g.command('show', 'get')

    with self.command_group('mesh service-replica', mesh_replica_util, client_factory=cf_mesh_replica) as g:
        g.command('list', 'list_by_service_name')
        g.command('show', 'get')

    with self.command_group('mesh code-package-log', mesh_cp_util, client_factory=cf_mesh_code_package) as g:
        g.command('get', 'get_container_log', transform=transform_log_output)

    with self.command_group('mesh network', mesh_network_util, client_factory=cf_mesh_network) as g:
        g.command('show', 'get', table_transformer=transform_network)
        g.command('delete', 'delete', confirmation=True)

    with self.command_group('mesh network', cmd_util) as g:
        g.custom_command('list', 'list_networks', client_factory=cf_mesh_network, table_transformer=transform_network_list)

    with self.command_group('mesh volume', cmd_util) as g:
        g.custom_command('create', 'create_volume', client_factory=cf_mesh_volume, table_transformer=transform_volume_list)
        g.custom_command('list', 'list_volumes', client_factory=cf_mesh_volume, table_transformer=transform_volume_list)
        g.custom_command('show', 'show_volume', client_factory=cf_mesh_volume, exception_handler=resource_exception_handler, table_transformer=transform_volume)
        g.custom_command('delete', 'delete_volume', client_factory=cf_mesh_volume, confirmation=True)
