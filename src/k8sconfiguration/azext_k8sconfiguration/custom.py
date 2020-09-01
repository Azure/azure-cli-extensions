# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError

from azext_k8sconfiguration.vendored_sdks.models import SourceControlConfiguration
from azext_k8sconfiguration.vendored_sdks.models import HelmOperatorProperties
from azext_k8sconfiguration.vendored_sdks.models import ErrorResponseException
import base64


def show_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type):
    """Get an existing Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    try:
        config = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        return __fix_compliance_state(config)
    except ErrorResponseException as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = "{0} Verify that the --cluster-type is correct and the resource exists.".format(ex.message)
            # If Configuration not found
            elif ex.message.__contains__("Operation returned an invalid status code 'Not Found'"):
                message = "(ConfigurationNotFound) The Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration/" \
                          "sourcecontrolConfigurations/{3} could not be found!".format(cluster_rp, cluster_type,
                                                                                       cluster_name, name)
            else:
                message = ex.message
            raise CLIError(message)


def create_k8sconfiguration(client, resource_group_name, cluster_name, name, repository_url, scope, cluster_type,
                            operator_instance_name=None, operator_namespace='default', helm_operator_version='0.3.0',
                            operator_type='flux', operator_params='', gitops_privatekey_filepath='', gitops_privatekey='', 
                            enable_helm_operator=None, helm_operator_params=''):
    """Create a new Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    # Determine operatorInstanceName
    if operator_instance_name is None:
        operator_instance_name = name

    # Create helmOperatorProperties object
    helm_operator_properties = None

    if enable_helm_operator:
        helm_operator_properties = HelmOperatorProperties()
        helm_operator_properties.chart_version = helm_operator_version.strip()
        helm_operator_properties.chart_values = helm_operator_params.strip()

    if gitops_privatekey != '' and gitops_privatekey_filepath != '':
        raise Exception("Cannot provide raw key AND filepath, must choose one")
    elif gitops_privatekey_filepath != '':
        with open (gitops_privatekey_filepath, "r") as myfile: # user passed in filename
            dataList = myfile.readlines() # keeps newline characters intact
            if len(dataList) <= 1:
                raise Exception("Empty file was provided")
            dataRaw = ''.join(dataList)
            dataBytes = dataRaw.encode('utf-8')
            data = base64.b64encode(dataBytes)
            data = data.decode('utf-8')
            configuration_protected_settings = "{\"GitOpsPrivateKey\":\""+ data +"\"}"
    elif gitops_privatekey != '':
        if "\\n" in gitops_privatekey: # user passed raw key
            dataBytes = gitops_privatekey.encode('utf-8')
            data = base64.b64encode(dataBytes)
            data = data.decode('utf-8')
        else: # user passed base64 encoded key
            data = gitops_privatekey
        configuration_protected_settings = "{\"GitOpsPrivateKey\":\""+ data +"\"}"
    else:
        configuration_protected_settings = "{}"

    # Create sourceControlConfiguration object
    source_control_configuration = SourceControlConfiguration(repository_url=repository_url,
                                                              operator_namespace=operator_namespace,
                                                              operator_instance_name=operator_instance_name,
                                                              operator_type=operator_type,
                                                              operator_params=operator_params,
                                                              configuration_protected_settings=configuration_protected_settings,
                                                              operator_scope=scope,
                                                              enable_helm_operator=enable_helm_operator,
                                                              helm_operator_properties=helm_operator_properties)

    # Try to create the resource
    config = client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
                                     name, source_control_configuration)

    return __fix_compliance_state(config)


def update_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type,
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

    config = client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
                                     source_control_configuration_name, config)

    return __fix_compliance_state(config)


def list_k8sconfiguration(client, resource_group_name, cluster_name, cluster_type):
    cluster_rp = __get_cluster_type(cluster_type)
    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


def delete_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type):
    """Delete an existing Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    source_control_configuration_name = name

    return client.delete(resource_group_name, cluster_rp, cluster_type, cluster_name, source_control_configuration_name)


def __get_cluster_type(cluster_type):
    if cluster_type.lower() == 'connectedclusters':
        return 'Microsoft.Kubernetes'
    # Since cluster_type is an enum of only two values, if not connectedClusters, it will be managedClusters.
    return 'Microsoft.ContainerService'


def __fix_compliance_state(config):
    # If we get Compliant/NonCompliant as compliance_sate, change them before returning
    if config.compliance_status.compliance_state.lower() == 'noncompliant':
        config.compliance_status.compliance_state = 'Failed'
    elif config.compliance_status.compliance_state.lower() == 'compliant':
        config.compliance_status.compliance_state = 'Installed'

    return config
