# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ResourceNotFoundError, CommandNotFoundError, \
    RequiredArgumentMissingError
from knack.log import get_logger
from azext_k8s_configuration._utils import _get_cluster_type, \
    _fix_compliance_state, _get_data_from_key_or_file, _to_base64
from azext_k8s_configuration._validators import _validate_known_hosts, _validate_url_with_params, \
    _validate_configuration_name, _validate_cc_registration, _validate_private_key

from azext_k8s_configuration.vendored_sdks.models import SourceControlConfiguration
from azext_k8s_configuration.vendored_sdks.models import HelmOperatorProperties
from azext_k8s_configuration.vendored_sdks.models import ErrorResponseException

logger = get_logger(__name__)


def show_k8s_configuration(client, resource_group_name, cluster_name, name, cluster_type):
    """Get an existing Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = _get_cluster_type(cluster_type)

    try:
        config = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        return _fix_compliance_state(config)
    except ErrorResponseException as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = ex.message
                recommendation = 'Verify that the --cluster-type is correct and the Resource ' \
                                 '{0}/{1}/{2} exists'.format(cluster_rp, cluster_type, cluster_name)
            # If Configuration not found
            elif ex.message.__contains__("Operation returned an invalid status code 'Not Found'"):
                message = '(ConfigurationNotFound) The Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration/' \
                          'sourcecontrolConfigurations/{3} could not be found!'.format(cluster_rp, cluster_type,
                                                                                       cluster_name, name)
                recommendation = 'Verify that the Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration' \
                                 '/sourcecontrolConfigurations/{3} exists'.format(cluster_rp, cluster_type,
                                                                                  cluster_name, name)
            else:
                message = ex.message
                recommendation = ''
            raise ResourceNotFoundError(message, recommendation) from ex


# pylint: disable=too-many-locals
def create_k8s_configuration(cmd, client, resource_group_name, cluster_name, name, repository_url, scope, cluster_type,
                             operator_instance_name=None, operator_namespace='default',
                             helm_operator_chart_version='1.2.0', operator_type='flux', operator_params='',
                             ssh_private_key='', ssh_private_key_file='', https_user='', https_key='',
                             ssh_known_hosts='', ssh_known_hosts_file='', enable_helm_operator=None,
                             helm_operator_params=''):
    """Create a new Kubernetes Source Control Configuration.

    """
    # Validate configuration name
    _validate_configuration_name(name)

    # Determine ClusterRP
    cluster_rp = _get_cluster_type(cluster_type)

    # Determine operatorInstanceName
    if operator_instance_name is None:
        operator_instance_name = name

    # Create helmOperatorProperties object
    helm_operator_properties = None
    if enable_helm_operator:
        helm_operator_properties = HelmOperatorProperties()
        helm_operator_properties.chart_version = helm_operator_chart_version.strip()
        helm_operator_properties.chart_values = helm_operator_params.strip()

    protected_settings = _get_protected_settings(ssh_private_key,
                                                 ssh_private_key_file,
                                                 https_user,
                                                 https_key)
    knownhost_data = _get_data_from_key_or_file(ssh_known_hosts, ssh_known_hosts_file)
    if knownhost_data:
        _validate_known_hosts(knownhost_data)

    # Flag which parameters have been set and validate these settings against the set repository url
    ssh_private_key_set = ssh_private_key != '' or ssh_private_key_file != ''
    known_hosts_contents_set = knownhost_data != ''
    https_auth_set = https_user != '' and https_key != ''
    _validate_url_with_params(repository_url,
                              ssh_private_key_set=ssh_private_key_set,
                              known_hosts_contents_set=known_hosts_contents_set,
                              https_auth_set=https_auth_set)

    # Validate that the subscription is registered to Microsoft.KubernetesConfiguration
    _validate_cc_registration(cmd)

    # Create sourceControlConfiguration object
    source_control_configuration = SourceControlConfiguration(repository_url=repository_url,
                                                              operator_namespace=operator_namespace,
                                                              operator_instance_name=operator_instance_name,
                                                              operator_type=operator_type,
                                                              operator_params=operator_params,
                                                              configuration_protected_settings=protected_settings,
                                                              operator_scope=scope,
                                                              ssh_known_hosts_contents=knownhost_data,
                                                              enable_helm_operator=enable_helm_operator,
                                                              helm_operator_properties=helm_operator_properties)

    # Try to create the resource
    config = client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
                                     name, source_control_configuration)

    return _fix_compliance_state(config)


def update_k8s_configuration(client, resource_group_name, cluster_name, name, cluster_type,
                             repository_url=None, operator_params=None, ssh_known_hosts='',
                             ssh_known_hosts_file='', enable_helm_operator=None, helm_operator_chart_version=None,
                             helm_operator_params=None):
    """Update an existing Kubernetes Source Control Configuration.

    """

    # TODO: Remove this after we eventually get PATCH implemented for update and uncomment
    raise CommandNotFoundError(
        "\"k8s-configuration update\" currently is not available. "
        "Use \"k8s-configuration create\" to update a previously created configuration."
    )

    # # Determine ClusterRP
    # cluster_rp = __get_cluster_type(cluster_type)

    # source_control_configuration_name = name.strip()

    # config = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name,
    #                     source_control_configuration_name)
    # update_yes = False

    # # Set input values, if they are supplied
    # if repository_url is not None:
    #     config.repository_url = repository_url
    #     update_yes = True

    # if operator_params is not None:
    #     config.operator_params = operator_params
    #     update_yes = True

    # knownhost_data = get_data_from_key_or_file(ssh_known_hosts, ssh_known_hosts_file)
    # if knownhost_data:
    #     validate_known_hosts(knownhost_data)
    #     config.ssh_known_hosts_contents = knownhost_data
    #     update_yes = True

    # if enable_helm_operator is not None:
    #     config.enable_helm_operator = enable_helm_operator
    #     update_yes = True

    # # Get the helm operator properties from the config and set them
    # if config.helm_operator_properties is None:
    #     config.helm_operator_properties = HelmOperatorProperties()
    # if helm_operator_chart_version is not None:
    #     config.helm_operator_properties.chart_version = helm_operator_chart_version.strip()
    #     update_yes = True
    # if helm_operator_params is not None:
    #     config.helm_operator_properties.chart_values = helm_operator_params.strip()
    #     update_yes = True

    # if update_yes is False:
    #     raise RequiredArgumentMissingError(
    #         'Invalid update. No values to update!',
    #         'Verify that at least one changed parameter is provided in the update command')

    # # Flag which parameters have been set and validate these settings against the set repository url
    # known_hosts_contents_set = config.ssh_known_hosts_contents != ""
    # validate_url_with_params(config.repository_url,
    #                          ssh_private_key_set=False,
    #                          known_hosts_contents_set=known_hosts_contents_set,
    #                          https_auth_set=False)

    # config = client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
    #                                  source_control_configuration_name, config)

    # return __fix_compliance_state(config)


def list_k8s_configuration(client, resource_group_name, cluster_name, cluster_type):
    cluster_rp = _get_cluster_type(cluster_type)
    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


def delete_k8s_configuration(client, resource_group_name, cluster_name, name, cluster_type):
    """Delete an existing Kubernetes Source Control Configuration.

    """
    # Determine ClusterRP
    cluster_rp = _get_cluster_type(cluster_type)

    source_control_configuration_name = name

    return client.delete(resource_group_name, cluster_rp, cluster_type, cluster_name, source_control_configuration_name)


def _get_protected_settings(ssh_private_key, ssh_private_key_file, https_user, https_key):
    protected_settings = {}
    ssh_private_key_data = _get_data_from_key_or_file(ssh_private_key, ssh_private_key_file)

    # Add gitops private key data to protected settings if exists
    # Dry-run all key types to determine if the private key is in a valid format
    if ssh_private_key_data != '':
        _validate_private_key(ssh_private_key_data)
        protected_settings["sshPrivateKey"] = ssh_private_key_data

    # Check if both httpsUser and httpsKey exist, then add to protected settings
    if https_user != '' and https_key != '':
        protected_settings['httpsUser'] = _to_base64(https_user)
        protected_settings['httpsKey'] = _to_base64(https_key)
    elif https_user != '':
        raise RequiredArgumentMissingError(
            'Error! --https-user used without --https-key',
            'Try providing both --https-user and --https-key together')
    elif https_key != '':
        raise RequiredArgumentMissingError(
            'Error! --http-key used without --http-user',
            'Try providing both --https-user and --https-key together')

    return protected_settings
