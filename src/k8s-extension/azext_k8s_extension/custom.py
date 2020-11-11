# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from knack.util import CLIError
from knack.log import get_logger

from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceForCreate
from azext_k8s_extension.vendored_sdks.models import ConfigurationIdentity
from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceUpdate
from azext_k8s_extension.vendored_sdks.models import ErrorResponseException
from azext_k8s_extension.vendored_sdks.models import ScopeCluster
from azext_k8s_extension.vendored_sdks.models import ScopeNamespace
from azext_k8s_extension.vendored_sdks.models import Scope
from .containerinsights import _get_container_insights_settings
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.azure_exceptions import CloudError
from ._client_factory import cf_resources

logger = get_logger(__name__)


def show_k8s_extension(client, resource_group_name, cluster_name, name, cluster_type):
    """Get an existing K8s Extension.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    try:
        extension = client.get(resource_group_name,
                               cluster_rp, cluster_type, cluster_name, name)
        return extension
    except ErrorResponseException as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = "{0} Verify that the --cluster-type is correct and the resource exists.".format(
                    ex.message)
            # If Configuration not found
            elif ex.message.__contains__("Operation returned an invalid status code 'Not Found'"):
                message = "(ExtensionNotFound) The Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration/" \
                          "extensions/{3} could not be found!".format(
                              cluster_rp, cluster_type, cluster_name, name)
            else:
                message = ex.message
            raise CLIError(message)


def create_k8s_extension(cmd, client, resource_group_name, cluster_name, name, cluster_type,
                         extension_type, scope='cluster', auto_upgrade_minor_version=None, release_train=None,
                         version=None, target_namespace=None, release_namespace=None, configuration_settings=None,
                         configuration_protected_settings=None, configuration_settings_file=None,
                         configuration_protected_settings_file=None, location=None, tags=None):
    """Create a new Extension Instance.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    # Validate scope and namespace
    __validate_scope_and_namespace(scope, release_namespace, target_namespace, name)

    # Validate version, release_train
    __validate_version_and_release_train(
        version, release_train, auto_upgrade_minor_version)

    # Configuration Settings & Configuration Protected Settings
    if configuration_settings is not None and configuration_settings_file is not None:
        raise CLIError('Error! Both configuration_settings and configuration_settings_file cannot be provided.')

    if configuration_protected_settings is not None and configuration_protected_settings_file is not None:
        raise CLIError('Error! Both configuration_protected_settings and configuration_protected_settings_file '
                       'cannot be provided.')

    config_settings = {}
    config_protected_settings = {}
    create_identity = False
    # Get Configuration Settings from file
    if configuration_settings_file is not None:
        config_settings = __get_config_settings_from_file(configuration_settings_file)

    if configuration_settings is not None:
        for dicts in configuration_settings:
            for key, value in dicts.items():
                config_settings[key] = value

    # Get Configuration Protected Settings from file
    if configuration_protected_settings_file is not None:
        config_protected_settings = __get_config_settings_from_file(configuration_protected_settings_file)

    if configuration_protected_settings is not None:
        for dicts in configuration_protected_settings:
            for key, value in dicts.items():
                config_protected_settings[key] = value

    # ExtensionType specific conditions
    extension_type_lower = extension_type.lower()

    if extension_type_lower in 'azuremonitor-containers' 'microsoft.azuredefender.kubernetes':
        create_identity = True
        # hardcoding  name, release_namespace and scope since ci only supports one instance and cluster scope
        # and platform doesnt have support yet extension specific constraints like this
        logger.warning('Ignoring name, release_namespace and scope parameters since {0} '
                       'only supports cluster scope and single instance of this extension'.format(extension_type_lower))

        scope = 'cluster'
        if not config_settings:
            config_settings = {}

        if not config_protected_settings:
            config_protected_settings = {}

        if extension_type.lower() == "azuremonitor-containers":
            name = 'azuremonitor-containers'
            release_namespace = 'azuremonitor-containers'
            is_ci_extension_type = True
        else:
            name = extension_type_lower
            release_namespace = "azuredefender"
            is_ci_extension_type = False

        _get_container_insights_settings(cmd, resource_group_name, cluster_name, config_settings,
                                         config_protected_settings, is_ci_extension_type)

    # Determine namespace name
    if scope == 'cluster':
        if release_namespace is None:
            release_namespace = name
        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)
    else:
        if target_namespace is None:
            target_namespace = name
        scope_namespace = ScopeNamespace(target_namespace=target_namespace)
        ext_scope = Scope(namespace=scope_namespace, cluster=None)

    identity_object = None
    cluster_location = ""
    # Create identity
    if create_identity:
        subscription_id = get_subscription_id(cmd.cli_ctx)
        resources = cf_resources(cmd.cli_ctx, subscription_id)
        cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Kubernetes/' \
                              'connectedClusters/{2}'.format(subscription_id, resource_group_name, cluster_name)
        try:
            resource = resources.get_by_id(cluster_resource_id, '2020-01-01-preview')
            cluster_location = str(resource.location.lower())
        except CloudError as ex:
            raise ex
        identity_type = "SystemAssigned"
        identity_object = ConfigurationIdentity(type=identity_type)
    # Create Extension Instance object
    extension_instance = ExtensionInstanceForCreate(extension_type=extension_type,
                                                    auto_upgrade_minor_version=auto_upgrade_minor_version,
                                                    release_train=release_train,
                                                    version=version,
                                                    scope=ext_scope,
                                                    configuration_settings=config_settings,
                                                    configuration_protected_settings=config_protected_settings,
                                                    identity=identity_object,
                                                    location=cluster_location)

    # Try to create the resource
    return client.create(resource_group_name, cluster_rp, cluster_type, cluster_name, name, extension_instance)


def list_k8s_extension(cmd, client, resource_group_name, cluster_name, cluster_type):
    cluster_rp = __get_cluster_type(cluster_type)
    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


def update_k8s_extension(cmd, client, resource_group_name, cluster_type, cluster_name, name,
                         auto_upgrade_minor_version='', release_train='', version='', tags=None):

    print("In update!")

    # Ensure some values are provided for update
    if auto_upgrade_minor_version is None and release_train is None and version is None:
        message = "No values provided for update. Provide new value(s) for one or more of these properties:" \
                  " auto_upgrade_minor_version, release_train or version."
        CLIError(message)

    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)
    upd_extension = ExtensionInstanceUpdate(auto_upgrade_minor_version=auto_upgrade_minor_version,
                                            release_train=release_train, version=version)

    return client.update(resource_group_name, cluster_rp, cluster_type, cluster_name, name, upd_extension)


def delete_k8s_extension(cmd, client, resource_group_name, cluster_name, name, cluster_type, location=None, tags=None):
    """Delete an existing Kubernetes Extension.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    k8s_extension_instance_name = name

    return client.delete(resource_group_name, cluster_rp, cluster_type, cluster_name, k8s_extension_instance_name)


def __get_cluster_type(cluster_type):
    if cluster_type.lower() == 'connectedclusters':
        return 'Microsoft.Kubernetes'
    # Since cluster_type is an enum of only two values, if not connectedClusters, it will be managedClusters.
    return 'Microsoft.ContainerService'


def __validate_scope_and_namespace(scope, release_namespace, target_namespace, name):
    if scope == 'cluster':
        if target_namespace is not None:
            message = "When Scope is 'cluster', target_namespace must not be given."
            raise CLIError(message)
        if release_namespace is None:
            release_namespace = name
    else:
        if release_namespace is not None:
            message = "When Scope is 'namespace', release_namespace must not be given."
            raise CLIError(message)


def __validate_version_and_release_train(version, release_train, auto_upgrade_minor_version):
    if version is not None:
        if release_train is not None:
            message = "Both release_train and version cannot be given. To pin to specific version, give only version."
            raise CLIError(message)
        if auto_upgrade_minor_version is not False:
            message = "To pin to specific version, auto-upgrade-minor-version must be set to 'false'."
            raise CLIError(message)


def __get_config_settings_from_file(file_path):
    try:
        config_file = open(file_path,)
        settings = json.load(config_file)
    except ValueError:
        raise Exception("File {} is not a valid JSON file".format(file_path))

    files = len(settings)
    if files == 0:
        raise Exception("File {} is empty".format(file_path))

    return settings
