# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from __future__ import print_function
from collections import OrderedDict

from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands import CliCommandType

from azure.cli.command_modules.resource._validators import _validate_deployment_name
from knack.util import CLIError
from ._client_factory import (cf_mesh_deployments,
                              cf_mesh_volume, cf_mesh_secret_value)
from ._exception_handler import resource_exception_handler

#
# Table Output formatting for various top level and proxy resources
#


# Application Resource table output formatting
def transform_application(result):
    return OrderedDict([('Name', result['name']),
                        ('ResourceGroup', result.get('resourceGroup')),
                        ('Location', result.get('location')),
                        ('ProvisioningState', result.get('provisioningState'))])


def transform_application_list(result):
    return [transform_application(application) for application in result]


# Service Resource table output formatting
def transform_service(result):
    return OrderedDict([('Name', result['name']),
                        ('ProvisioningState', result.get('provisioningState')),
                        ('Status', result.get('status')),
                        ('HealthState', result.get('healthState')),
                        ('ReplicaCount', result.get('replicaCount'))])


def transform_service_list(result):
    return [transform_service(service) for service in result]


# Service Replica table output formatting
def transform_service_replica(result):
    return OrderedDict([('Name', result['replicaName'])])


def transform_service_replica_list(result):
    return [transform_service_replica(replica) for replica in result]


# Volume Resource table output formatting
def transform_volume(result):
    return OrderedDict([('Name', result['name']),
                        ('ResourceGroup', result.get('resourceGroup')),
                        ('Location', result.get('location')),
                        ('ProvisioningState', result.get('provisioningState')),
                        ('Provider', result.get('provider'))])


def transform_volume_list(result):
    return [transform_volume(volume) for volume in result]


# Network Resource table output formatting
def transform_network(result):
    address_prefix = None
    if result.get('properties', {}).get('kind') == 'Local':
        address_prefix = result.get('properties', {}).get('networkAddressPrefix')
    return OrderedDict([('Name', result['name']),
                        ('ResourceGroup', result.get('resourceGroup')),
                        ('Location', result.get('location')),
                        ('Kind', result.get('properties', {}).get('kind')),
                        ('AddressPrefix', address_prefix),
                        ('ProvisioningState', result.get('properties', {}).get('provisioningState')),
                        ('status', result.get('properties', {}).get('status'))])


def transform_network_list(result):
    return [transform_network(network) for network in result]


# Secret Resource table output formatting
def transform_secret(result):
    return OrderedDict([('Name', result['name']),
                        ('ResourceGroup', result.get('resourceGroup')),
                        ('Location', result.get('location')),
                        ('ProvisioningState', result.get('properties', {}).get('provisioningState')),
                        ('Kind', result.get('properties', {}).get('kind'))])


def transform_secret_list(result):
    return [transform_secret(secret) for secret in result]


# Secret valuetable output formatting
def transform_secretvalue(result):
    return OrderedDict([('Version', result['name']),
                        ('ResourceGroup', result.get('resourceGroup')),
                        ('Location', result.get('location')),
                        ('ProvisioningState', result.get('provisioningState'))])


def transform_secretvalue_list(result):
    return [transform_secretvalue(secret) for secret in result]


#
# Custom formatting for additional types
#

# print log
def transform_log_output(result):
    return result.content


# CPU and memory
def format_cpu_memory(container_group):
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


# IP Address and port
def format_ip_address(container_group):
    ip_address = container_group.get('ipAddress')
    if ip_address is not None:
        ports = ','.join(str(p['port']) for p in ip_address['ports'])
        return '{0}:{1}'.format(ip_address.get('ip'), ports)
    return None


def transform_gateway(result):
    """Transform a gateway list to table output. """
    return OrderedDict([('Name', result.get('name')),
                        ('ResourceGroup', result.get('resourceGroup')),
                        ('Location', result.get('location')),
                        ('ProvisioningState', result.get('provisioningState')),
                        ('Status', result.get('status')),
                        ('PublicIP', result.get('ipAddress'))])


def transform_gateway_list(result):
    """Transform a gateway list to table output. """
    return [transform_gateway(gateway) for gateway in result]


def process_deployment_create_namespace(namespace):
    if bool(namespace.template_uri) == bool(namespace.template_file) == bool(namespace.input_yaml_files):
        raise CLIError('incorrect usage: --template-file FILE | --template-uri URI | --input-yaml-files PATH')
    _validate_deployment_name(namespace)


def load_command_table(self, _):  # pylint: disable=too-many-statements
    cmd_util = CliCommandType(
        operations_tmpl='azext_mesh.custom#{}',
        exception_handler=resource_exception_handler
    )

    mesh_secret_value_util = CliCommandType(
        operations_tmpl='azext_mesh.servicefabricmesh.mgmt.servicefabricmesh.operations.secret_value_operations#SecretValueOperations.{}',
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

    with self.command_group('mesh generate', resource_deployment_sdk) as g:
        g.custom_command('armtemplate', 'generate_arm_template')

    with self.command_group('mesh app'):
        from .aaz.latest.mesh.app import Show, List
        self.command_table['mesh app show'] = Show(loader=self, table_transformer=transform_application)
        self.command_table['mesh app list'] = List(loader=self, table_transformer=transform_application_list)

    with self.command_group('mesh service'):
        from .aaz.latest.mesh.service import Show, List
        self.command_table['mesh service show'] = Show(loader=self, table_transformer=transform_service)
        self.command_table['mesh service list'] = List(loader=self, table_transformer=transform_service_list)

    with self.command_group('mesh service-replica'):
        from .aaz.latest.mesh.service_replica import Show, List
        self.command_table['mesh service-replica show'] = Show(loader=self, table_transformer=transform_service_replica)
        self.command_table['mesh service-replica list'] = List(loader=self, table_transformer=transform_service_replica_list)

    with self.command_group('mesh code-package-log'):
        from .aaz.latest.mesh.code_package_log import Get
        self.command_table['mesh code-package-log get'] = Get(loader=self, transform=transform_log_output)

    with self.command_group('mesh network'):
        from .aaz.latest.mesh.network import Show, List
        self.command_table['mesh network show'] = Show(loader=self, table_transformer=transform_network)
        self.command_table['mesh network list'] = List(loader=self, table_transformer=transform_network_list)

    with self.command_group('mesh volume', cmd_util) as g:
        g.custom_command('create', 'create_volume', client_factory=cf_mesh_volume, table_transformer=transform_volume_list)

    with self.command_group('mesh volume'):
        from .aaz.latest.mesh.volume import Show, List
        self.command_table['mesh volume show'] = Show(loader=self, table_transformer=transform_volume)
        self.command_table['mesh volume list'] = List(loader=self, table_transformer=transform_volume_list)

    with self.command_group('mesh secret'):
        from .aaz.latest.mesh.secret import List
        self.command_table['mesh secret list'] = List(loader=self, table_transformer=transform_secret_list)

    with self.command_group('mesh secretvalue', mesh_secret_value_util, client_factory=cf_mesh_secret_value) as g:
        g.show_command('show', 'get')

    with self.command_group('mesh secretvalue', cmd_util, client_factory=cf_mesh_secret_value) as g:
        g.custom_show_command('show', 'secret_show')

    with self.command_group('mesh secretvalue'):
        from .aaz.latest.mesh.secretvalue import List
        self.command_table['mesh secretvalue list'] = List(loader=self, table_transformer=transform_secretvalue_list)

    with self.command_group('mesh gateway'):
        from .aaz.latest.mesh.gateway import Show, List
        self.command_table['mesh gateway show'] = Show(loader=self, table_transformer=transform_gateway)
        self.command_table['mesh gateway list'] = List(loader=self, table_transformer=transform_gateway_list)
