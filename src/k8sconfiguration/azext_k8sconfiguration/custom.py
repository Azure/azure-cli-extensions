# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from urllib.parse import urlparse
from knack.util import CLIError
from knack.log import get_logger
from paramiko.hostkeys import HostKeyEntry
from Crypto.PublicKey import RSA

from azext_k8sconfiguration.vendored_sdks.models import SourceControlConfiguration
from azext_k8sconfiguration.vendored_sdks.models import HelmOperatorProperties
from azext_k8sconfiguration.vendored_sdks.models import ErrorResponseException

logger = get_logger(__name__)


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


# pylint: disable=too-many-locals
def create_k8sconfiguration(client, resource_group_name, cluster_name, name, repository_url, scope, cluster_type,
                            operator_instance_name=None, operator_namespace='default', helm_operator_version='1.2.0',
                            operator_type='flux', operator_params='', ssh_private_key='', ssh_private_key_file='',
                            https_user='', https_key='', ssh_known_hosts='', ssh_known_hosts_file='',
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

    protected_settings = __get_protected_settings(ssh_private_key, ssh_private_key_file, https_user, https_key)
    knownhost_data = __get_data_from_key_or_file(ssh_known_hosts, ssh_known_hosts_file)
    if knownhost_data != '':
        __validate_known_hosts(knownhost_data)

    # Flag which parameters have been set and validate these settings against the set repository url
    ssh_private_key_set = ssh_private_key != '' or ssh_private_key_file != ''
    ssh_known_hosts_set = knownhost_data != ''
    https_auth_set = https_user != '' and https_key != ''
    __validate_url_with_params(repository_url, ssh_private_key_set, ssh_known_hosts_set, https_auth_set)

    # Create sourceControlConfiguration object
    source_control_configuration = SourceControlConfiguration(repository_url=repository_url,
                                                              operator_namespace=operator_namespace,
                                                              operator_instance_name=operator_instance_name,
                                                              operator_type=operator_type,
                                                              operator_params=operator_params,
                                                              configuration_protected_settings=protected_settings,
                                                              operator_scope=scope,
                                                              ssh_known_hosts=knownhost_data,
                                                              enable_helm_operator=enable_helm_operator,
                                                              helm_operator_properties=helm_operator_properties)

    # Try to create the resource
    config = client.create_or_update(resource_group_name, cluster_rp, cluster_type, cluster_name,
                                     name, source_control_configuration)

    return __fix_compliance_state(config)


def update_k8sconfiguration(client, resource_group_name, cluster_name, name, cluster_type,
                            repository_url=None, operator_params=None, ssh_known_hosts='',
                            ssh_known_hosts_file='', enable_helm_operator=None, helm_operator_version=None,
                            helm_operator_params=None):
    """Update an existing Kubernetes Source Control Configuration.

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

    knownhost_data = __get_data_from_key_or_file(ssh_known_hosts, ssh_known_hosts_file)
    if knownhost_data != '':
        __validate_known_hosts(knownhost_data)
        config['ssh_known_hosts'] = knownhost_data
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

    # Flag which paramesters have been set and validate these settings against the set repository url
    ssh_known_hosts_set = 'ssh_known_hosts' in config
    __validate_url_with_params(config['repository_url'], False, ssh_known_hosts_set, False)

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


def __get_protected_settings(ssh_private_key, ssh_private_key_file, https_user, https_key):
    protected_settings = {}
    ssh_private_key_data = __get_data_from_key_or_file(ssh_private_key, ssh_private_key_file)

    # Add gitops private key data to protected settings if exists
    if ssh_private_key_data != '':
        try:
            RSA.importKey(__from_base64(ssh_private_key_data))
        except Exception as ex:
            raise CLIError("Error! ssh private key provided in wrong format, ensure your private key is valid") from ex
        protected_settings["sshPrivateKey"] = ssh_private_key_data

    # Check if both httpsUser and httpsKey exist, then add to protected settings
    if https_user != '' and https_key != '':
        protected_settings['httpsUser'] = __to_base64(https_user)
        protected_settings['httpsKey'] = __to_base64(https_key)
    elif https_user != '':
        raise CLIError('Error! --https-user must be proivded with --https-key')
    elif https_key != '':
        raise CLIError('Error! --http-key must be provided with --http-user')

    return protected_settings


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


def __validate_url_with_params(repository_url, ssh_private_key_set, known_hosts_contents_set, https_auth_set):
    scheme = urlparse(repository_url).scheme

    if scheme in ('http', 'https'):
        if ssh_private_key_set:
            raise CLIError('Error! An ssh private key cannot be used with an http(s) url')
        if known_hosts_contents_set:
            raise CLIError('Error! ssh known_hosts cannot be used with an http(s) url')
        if not https_auth_set and scheme == 'https':
            logger.warning('Warning! https url is being used without https auth params, ensure the repository '
                           'url provided is not a private repo')
    else:
        if https_auth_set:
            raise CLIError('Error! https auth (--https-user and --https-key) cannot be used with a non-http(s) url')


def __validate_known_hosts(knownhost_data):
    knownhost_str = __from_base64(knownhost_data).decode('utf-8')
    lines = knownhost_str.split('\n')
    for line in lines:
        line = line.strip(' ')
        line_len = len(line)
        if (line_len == 0) or (line[0] == "#"):
            continue
        try:
            host_key = HostKeyEntry.from_line(line)
            if not host_key:
                raise Exception('not enough fields found in known_hosts line')
        except Exception as ex:
            raise CLIError('Error! ssh known_hosts provided in wrong format, ensure your '
                           'known_hosts provided is valid') from ex


def __get_data_from_key_or_file(key, filepath):
    if key != '' and filepath != '':
        raise CLIError("Error! Both textual key and key filepath cannot be provided")
    data = ''
    if filepath != '':
        data = __read_key_file(filepath)
    elif key != '':
        data = key
    return data


def __read_key_file(path):
    try:
        with open(path, "r") as myfile:  # user passed in filename
            data_list = myfile.readlines()  # keeps newline characters intact
            data_list_len = len(data_list)
            if (data_list_len) <= 0:
                raise Exception("File provided does not contain any data")
            raw_data = ''.join(data_list)
        return __to_base64(raw_data)
    except Exception as ex:
        raise CLIError("Error! Unable to read key file specified with: {0} ".format(ex)) from ex


def __from_base64(base64_str):
    return base64.b64decode(base64_str)


def __to_base64(raw_data):
    bytes_data = raw_data.encode('utf-8')
    return base64.b64encode(bytes_data).decode('utf-8')
