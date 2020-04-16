# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError

from azext_k8sconfiguration.vendored_sdks.models.source_control_configuration_py3 import SourceControlConfiguration
from azext_k8sconfiguration.vendored_sdks.models.helm_operator_properties import HelmOperatorProperties

def show_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type='connectedClusters',
                          configuration_type='sourceControlConfiguration', api_version='2019-11-01-preview'):
    # Determine ClusterRP
    if cluster_type.lower() == 'connectedclusters':
        cluster_rp = 'Microsoft.Kubernetes'
    elif cluster_type.lower() == 'managedclusters':
        cluster_rp = 'Microsoft.ContainerService'
    else:
        raise CLIError("Invalid cluster-type.  Supported values are 'connectedClusters' and 'managedClusters'.")

    # Validate ConfigurationType
    if configuration_type.lower() != 'sourcecontrolconfiguration':
        raise CLIError('Invalid configuration_type.  Valid value is "sourceControlConfiguration"')

    source_control_configuration_name = name

    # Ensure apiVersion value
    if api_version is None:
        api_version = client.api_version

    return client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, source_control_configuration_name,
                      api_version)

def create_k8sconfiguration(client, resource_group_name, cluster_name, name, repository_url,
                            operator_instance_name=None, operator_namespace='default', cluster_type='connectedClusters',
                            configuration_type='sourceControlConfiguration', operator_params='', cluster_scoped=None,
                            operator_type='flux', enable_helm_operator=None, helm_operator_version='0.2.0',
                            helm_operator_params='', api_version='2019-11-01-preview'):
    # Determine ClusterRP
    if cluster_type.lower() == 'connectedclusters':
        cluster_rp = 'Microsoft.Kubernetes'
    elif cluster_type.lower() == 'managedclusters':
        cluster_rp = 'Microsoft.ContainerService'
    else:
        raise CLIError("Invalid cluster-type.  Supported values are 'connectedClusters' and 'managedClusters'.")

    # Validate configurationType
    if configuration_type.lower() != 'sourcecontrolconfiguration':
        raise CLIError('Invalid configuration_type.  Valid value is "sourceControlConfiguration"')

    source_control_configuration_name = name.strip()

    # Ensure apiVersion value
    if api_version is None:
        api_version = client.api_version

    # Determine operatorScope
    operator_scope = ''
    if cluster_scoped is None:
        operator_scope = 'namespace'

    # Determine operatorInstanceName
    if operator_instance_name is None:
        operator_instance_name = source_control_configuration_name

    # Create helmOperatorProperties object
    helm_operator_properties = HelmOperatorProperties()

    if enable_helm_operator:
        helm_operator_properties.chart_version = helm_operator_version.strip()
        helm_operator_properties.chart_values = helm_operator_params.strip()
    else:
        helm_operator_properties = None

    # Create sourceControlConfiguration object
    source_control_configuration = SourceControlConfiguration(repository_url=repository_url,
                                                              operator_namespace=operator_namespace,
                                                              operator_instance_name=operator_instance_name,
                                                              operator_type=operator_type,
                                                              operator_params=operator_params,
                                                              operator_scope=operator_scope,
                                                              enable_helm_operator=enable_helm_operator,
                                                              helm_operator_properties=helm_operator_properties)

    # Try to create the resource
    return client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
                                   source_control_configuration_name, api_version, source_control_configuration)

def update_k8sconfiguration(client, resource_group_name, cluster_name, name,
                            configuration_type='sourceControlConfiguration', cluster_type='connectedClusters',
                            repository_url=None, operator_params=None, enable_helm_operator=None,
                            helm_operator_version=None, helm_operator_params=None, api_version='2019-11-01-preview'):
    # Determine ClusterRP
    if cluster_type.lower() == 'connectedclusters':
        cluster_rp = 'Microsoft.Kubernetes'
    elif cluster_type.lower() == 'managedclusters':
        cluster_rp = 'Microsoft.ContainerService'
    else:
        raise CLIError("Invalid cluster-type.  Supported values are 'connectedClusters' and 'managedClusters'.")

    # Validate configurationType
    if configuration_type.lower() != 'sourcecontrolconfiguration':
        raise CLIError('Invalid configuration_type.  Valid value is "sourceControlConfiguration"')

    source_control_configuration_name = name.strip()

    # Ensure apiVersion value
    if api_version is None:
        api_version = client.api_version

    config = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name,
                        source_control_configuration_name, api_version).as_dict()

    updateYes = False

    # Set input values, if they are supplied
    if repository_url is not None:
        config['repository_url'] = repository_url
        updateYes = True

    if operator_params is not None:
        config['operator_params'] = operator_params
        updateYes = True

    if enable_helm_operator is not None:
        config['enable_helm_operator'] = enable_helm_operator
        updateYes = True

    if helm_operator_version is not None:
        config['helm_operator_version'] = helm_operator_version
        updateYes = True

    if helm_operator_params is not None:
        config['helm_operator_params'] = helm_operator_params
        updateYes = True

    if updateYes is False:
        raise CLIError('Invalid update.  No values to update!')

    return client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
                                   source_control_configuration_name, api_version, config)

def list_k8sconfiguration(client, resource_group_name, cluster_name, cluster_type='connectedClusters',
                          api_version='2019-11-01-preview'):
    if cluster_type.lower() == 'connectedclusters':
        cluster_rp = 'Microsoft.Kubernetes'
    elif cluster_type.lower() == 'managedclusters':
        cluster_rp = 'Microsoft.ContainerService'
    else:
        raise CLIError("Invalid cluster-type.  Supported values are 'connectedClusters' and 'managedClusters'.")

    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name, api_version)

def delete_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type='connectedClusters',
                            configuration_type='sourceControlConfiguration', api_version='2019-11-01-preview'):
    if cluster_type.lower() == 'connectedclusters':
        cluster_rp = 'Microsoft.Kubernetes'
    elif cluster_type.lower() == 'managedclusters':
        cluster_rp = 'Microsoft.ContainerService'
    else:
        raise CLIError("Invalid cluster-type.  Supported values are 'connectedClusters' and 'managedClusters'.")

    if configuration_type.lower() != 'sourcecontrolconfiguration':
        raise CLIError('Invalid configuration_type.  Valid value is "sourceControlConfiguration"')

    source_control_configuration_name = name

    custom_headers = {"x-ms-force": "true"}

    return client.delete(resource_group_name, cluster_rp, cluster_type, cluster_name, source_control_configuration_name,
                         api_version, custom_headers)
