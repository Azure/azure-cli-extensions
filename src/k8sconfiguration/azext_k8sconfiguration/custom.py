# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError

from azext_k8sconfiguration.vendored_sdks.models.source_control_configuration_py3 import SourceControlConfiguration
from azext_k8sconfiguration.vendored_sdks.models.helm_operator_properties import HelmOperatorProperties


def show_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type='connectedClusters'):
    """Get an existing Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    source_control_configuration_name = name

    return client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, source_control_configuration_name)


def create_k8sconfiguration(client, resource_group_name, cluster_name, name, repository_url,
                            operator_instance_name=None, operator_namespace='default', cluster_type='connectedClusters',
                            operator_params='', cluster_scoped=None, operator_type='flux', enable_helm_operator=None,
                            helm_operator_version='0.2.0', helm_operator_params=''):
    """Create a new Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    # Determine operatorScope
    operator_scope = ''
    if cluster_scoped is None:
        operator_scope = 'namespace'

    # Determine operatorInstanceName
    if operator_instance_name is None:
        operator_instance_name = name

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
                                   name, source_control_configuration)


def update_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type='connectedClusters',
                            repository_url=None, operator_params=None, enable_helm_operator=None,
                            helm_operator_version=None, helm_operator_params=None):
    """Create a new Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    source_control_configuration_name = name.strip()

    config = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name,
                        source_control_configuration_name).as_dict()

    update_yes = False

    # Set input values, if they are supplied
    if repository_url is not None:
        config['repository_url'] = repository_url
        update_yes = True

    if operator_params is not None:
        config['operator_params'] = operator_params
        update_yes = True

    if enable_helm_operator is not None:
        config['enable_helm_operator'] = enable_helm_operator
        update_yes = True

    if helm_operator_version is not None:
        config['helm_operator_version'] = helm_operator_version
        update_yes = True

    if helm_operator_params is not None:
        config['helm_operator_params'] = helm_operator_params
        update_yes = True

    if update_yes is False:
        raise CLIError('Invalid update.  No values to update!')

    return client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
                                   source_control_configuration_name, config)


def list_k8sconfiguration(client, resource_group_name, cluster_name, cluster_type='connectedClusters'):
    cluster_rp = __get_cluster_type(cluster_type)
    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


def delete_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type='connectedClusters'):
    """Delete an existing Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    source_control_configuration_name = name

    custom_headers = {"x-ms-force": "true"}

    return client.delete(resource_group_name, cluster_rp, cluster_type, cluster_name, source_control_configuration_name,
                         custom_headers)


def __get_cluster_type(cluster_type):
    if cluster_type.lower() == 'connectedclusters':
        return 'Microsoft.Kubernetes'
    # Since cluster_type is an enum of only two values, if not connectedClusters, it will be managedClusters.
    return 'Microsoft.ContainerService'
