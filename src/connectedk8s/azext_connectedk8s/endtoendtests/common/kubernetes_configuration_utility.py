import sys

from azure.mgmt.kubernetesconfiguration import SourceControlConfigurationClient
from azure.mgmt.kubernetesconfiguration.models import SourceControlConfiguration, HelmOperatorProperties


# This function returns the python client to interact with resources under the namespace 'Microsoft.KubernetesConfiguration'
def get_kubernetes_configuration_client(credential, subscription_id):
    return SourceControlConfigurationClient(credential, subscription_id)


# This function returns the python client to interact with the connected cluster resource
def get_source_control_configuration_client(credential, subscription_id):
    try:
        return get_kubernetes_configuration_client(credential, subscription_id).source_control_configurations
    except Exception as e:
        sys.exit("Error occured while creating source control configuration client: " + str(e))


# This function creates a new kubernetes configuration on a given cluster
def create_kubernetes_configuration(kc_client, resource_group_name, repository_url, cluster_rp, cluster_type, cluster_name,
                                    configuration_name, operator_scope, operator_namespace='default', operator_instance_name=None,
                                    operator_type='flux', operator_params='', enable_helm_operator=None, helm_operator_version='0.6.0',
                                    helm_operator_params=''):
    if operator_instance_name is None:
        operator_instance_name = configuration_name

    helm_operator_properties = None
    if enable_helm_operator:
        helm_operator_properties = HelmOperatorProperties()
        helm_operator_properties.chart_version = helm_operator_version.strip()
        helm_operator_properties.chart_values = helm_operator_params.strip()
    source_control_configuration = SourceControlConfiguration(repository_url=repository_url,
                                                              operator_namespace=operator_namespace,
                                                              operator_instance_name=operator_instance_name,
                                                              operator_type=operator_type,
                                                              operator_params=operator_params,
                                                              operator_scope=operator_scope,
                                                              enable_helm_operator=enable_helm_operator,
                                                              helm_operator_properties=helm_operator_properties)
    try:
        return kc_client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name, configuration_name,source_control_configuration)
    except Exception as e:
        sys.exit("Error occured while creating the kubernetes configuration resource: " + str(e))


# This function gets a kubernetes configuration resource
def show_kubernetes_configuration(kc_client, resource_group_name, cluster_rp, cluster_type, cluster_name, configuration_name):
    try:
        return kc_client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, configuration_name)
    except Exception as e:
        sys.exit("Error occured while fetching the kubernetes configuration resource: " + str(e))
