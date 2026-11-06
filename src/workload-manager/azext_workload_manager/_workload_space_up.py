# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.util import sdk_no_wait
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id

logger = get_logger(__name__)

_API_VERSION = '2026-11-01-preview'


def workload_space_up(cmd, resource_group_name, space_name, location, tags=None, deployment_name=None,
                      managed_cluster_resource_id=None, workload_execution_subnet_id=None,
                      runtime_link_subnet_id=None, no_wait=False):
    if not re.fullmatch(r'(?![.-])[A-Za-z0-9_.-]{1,64}', space_name):
        raise InvalidArgumentValueError(
            '--space-name must contain 1-64 letters, numbers, underscores, periods or hyphens, '
            'and cannot start with a period or hyphen.'
        )
    deployment_name = deployment_name or space_name
    if not re.fullmatch(r'[A-Za-z0-9_.()-]{1,64}', deployment_name):
        raise InvalidArgumentValueError(
            '--deployment-name must contain 1-64 letters, numbers, underscores, periods, hyphens or parentheses.'
        )

    references = (managed_cluster_resource_id, workload_execution_subnet_id, runtime_link_subnet_id)
    if any(value is not None for value in references):
        if not all(references):
            raise RequiredArgumentMissingError(
                'Specify --managed-cluster-resource-id, --workload-execution-subnet-id and '
                '--runtime-link-subnet-id together, or omit all three for managed runtimes.'
            )
        subscription_id = get_subscription_id(cmd.cli_ctx)
        _validate_reference(
            managed_cluster_resource_id, 'Microsoft.ContainerService/managedClusters',
            subscription_id, '--managed-cluster-resource-id'
        )
        for value, option in (
                (workload_execution_subnet_id, '--workload-execution-subnet-id'),
                (runtime_link_subnet_id, '--runtime-link-subnet-id')):
            _validate_reference(value, 'Microsoft.Network/virtualNetworks/subnets', subscription_id, option)
        if workload_execution_subnet_id.lower() == runtime_link_subnet_id.lower():
            raise InvalidArgumentValueError('The execution and runtime-link subnets must be distinct.')
        if (workload_execution_subnet_id.rsplit('/', 2)[0].lower() !=
                runtime_link_subnet_id.rsplit('/', 2)[0].lower()):
            raise InvalidArgumentValueError('The execution and runtime-link subnets must be in the same VNet.')

    template = _build_workload_space_template(*references)
    parameters = {
        'workloadSpaceName': {'value': space_name},
        'location': {'value': location},
        'tags': {'value': tags or {}},
    }

    # Newer CLI versions use a separate deployments SDK; retain support for the minimum CLI version.
    resource_type = getattr(ResourceType, 'MGMT_RESOURCE_DEPLOYMENTS', ResourceType.MGMT_RESOURCE_RESOURCES)
    deployment_model, properties_model = get_sdk(
        cmd.cli_ctx, resource_type, 'Deployment', 'DeploymentProperties', mod='models'
    )
    deployment = deployment_model(properties=properties_model.from_dict({
        'mode': 'Incremental', 'template': template, 'parameters': parameters,
    }))
    client = get_mgmt_service_client(cmd.cli_ctx, resource_type)
    logger.warning(
        "Submitting ARM deployment '%s'. Track it with: az deployment group show --resource-group %s --name %s",
        deployment_name, resource_group_name, deployment_name
    )
    return sdk_no_wait(
        no_wait, client.deployments.begin_create_or_update,
        resource_group_name=resource_group_name,
        deployment_name=deployment_name,
        parameters=deployment,
    )


def _validate_reference(value, expected_type, subscription_id, option):
    if not is_valid_resource_id(value):
        raise InvalidArgumentValueError(f'{option} must be a full {expected_type} resource ID.')
    parsed = parse_resource_id(value)
    resource_type = '/'.join([
        parsed.get('namespace', ''), parsed.get('type', ''),
        *(parsed[f'child_type_{index}'] for index in range(1, parsed.get('last_child_num', 0) + 1)),
    ])
    if resource_type.lower() != expected_type.lower() or not parsed.get('resource_group'):
        raise InvalidArgumentValueError(f'{option} must be a full {expected_type} resource ID.')
    if parsed.get('subscription', '').lower() != subscription_id.lower():
        raise InvalidArgumentValueError(f'{option} must be in the selected subscription.')


def _child_resource_id(resource_type, name):
    return (
        f"[resourceId('Microsoft.Compute/workloadSpaces/{resource_type}', "
        f"parameters('workloadSpaceName'), '{name}')]"
    )


def _build_workload_space_template(managed_cluster_resource_id=None, workload_execution_subnet_id=None,
                                   runtime_link_subnet_id=None):
    aks_properties = {'provisioningMode': 'Managed', 'managedProfile': {'offering': 'Standard'}}
    aci_properties = {'provisioningMode': 'Managed', 'managedProfile': {'provider': 'ACI'}}
    link_properties = {
        'orchestratorBindingResourceId': _child_resource_id('runtimeBindings', 'aks'),
        'executionBindingResourceId': _child_resource_id('runtimeBindings', 'aci'),
    }
    if managed_cluster_resource_id:
        aks_properties = {'provisioningMode': 'Referenced', 'resourceId': managed_cluster_resource_id}
        aci_properties['networkProfile'] = {'subnetResourceId': workload_execution_subnet_id}
        link_properties['subnetResourceId'] = runtime_link_subnet_id

    resources = [{
        'type': 'Microsoft.Compute/workloadSpaces',
        'apiVersion': _API_VERSION,
        'name': "[parameters('workloadSpaceName')]",
        'location': "[parameters('location')]",
        'tags': "[parameters('tags')]",
        'properties': {},
    }]
    space_id = "[resourceId('Microsoft.Compute/workloadSpaces', parameters('workloadSpaceName'))]"
    predecessor_id = space_id
    # All mutations share a workload-space operation gate, even for otherwise independent children.
    for resource_type, name, kind, properties in (
            ('runtimeBindings', 'aks', 'Kubernetes', aks_properties),
            ('runtimeBindings', 'aci', 'ServerlessContainers', aci_properties),
            ('runtimeLinks', 'link', None, link_properties),
            ('capabilities', 'agent-sandbox', 'AgentSandbox', {'versionPolicy': 'ServiceManaged'}),
            ('capabilities', 'pod-snapshot-restore', 'PodSnapshotRestore', {'versionPolicy': 'ServiceManaged'})):
        resource = {
            'type': f'Microsoft.Compute/workloadSpaces/{resource_type}',
            'apiVersion': _API_VERSION,
            'name': f"[format('{{0}}/{name}', parameters('workloadSpaceName'))]",
            'dependsOn': [predecessor_id],
            'properties': properties,
        }
        if kind:
            resource['kind'] = kind
        resources.append(resource)
        predecessor_id = _child_resource_id(resource_type, name)

    return {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#',
        'contentVersion': '1.0.0.0',
        'parameters': {
            'workloadSpaceName': {'type': 'string', 'minLength': 1, 'maxLength': 64},
            'location': {'type': 'string'},
            'tags': {'type': 'object', 'defaultValue': {}},
        },
        'resources': resources,
        'outputs': {'workloadSpaceId': {'type': 'string', 'value': space_id}},
    }
