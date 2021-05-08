# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument,too-many-locals

import json
from knack.log import get_logger

from msrestazure.azure_exceptions import CloudError

from azure.cli.core.azclierror import ResourceNotFoundError, MutuallyExclusiveArgumentError, \
    InvalidArgumentValueError, CommandNotFoundError, RequiredArgumentMissingError
from azure.cli.core.commands.client_factory import get_subscription_id
from .vendored_sdks.models import ConfigurationIdentity
from .vendored_sdks.models import ErrorResponseException
from .vendored_sdks.models import Scope

from .partner_extensions.ContainerInsights import ContainerInsights
from .partner_extensions.AzureDefender import AzureDefender
from .partner_extensions.Cassandra import Cassandra
from .partner_extensions.AzureMLKubernetes import AzureMLKubernetes
from .partner_extensions.DefaultExtension import DefaultExtension
from . import consts

from ._client_factory import cf_resources

logger = get_logger(__name__)


# A factory method to return the correct extension class based off of the extension name
def ExtensionFactory(extension_name):
    extension_map = {
        'microsoft.azuremonitor.containers': ContainerInsights,
        'microsoft.azuredefender.kubernetes': AzureDefender,
        'microsoft.azureml.kubernetes': AzureMLKubernetes,
        'cassandradatacentersoperator': Cassandra,
    }

    # Return the extension if we find it in the map, else return the default
    return extension_map.get(extension_name, DefaultExtension)()


def show_k8s_extension(client, resource_group_name, cluster_name, name, cluster_type):
    """Get an existing K8s Extension.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_rp(cluster_type)

    try:
        extension = client.get(resource_group_name,
                               cluster_rp, cluster_type, cluster_name, name)
        return extension
    except ErrorResponseException as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = "{0} Verify that the cluster-type is correct and the resource exists.".format(
                    ex.message)
            # If Configuration not found
            elif ex.message.__contains__("Operation returned an invalid status code 'Not Found'"):
                message = "(ExtensionNotFound) The Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration/" \
                          "extensions/{3} could not be found!".format(
                              cluster_rp, cluster_type, cluster_name, name)
            else:
                message = ex.message
            raise ResourceNotFoundError(message)


def create_k8s_extension(cmd, client, resource_group_name, cluster_name, name, cluster_type,
                         extension_type, scope=None, auto_upgrade_minor_version=None, release_train=None,
                         version=None, target_namespace=None, release_namespace=None, configuration_settings=None,
                         configuration_protected_settings=None, configuration_settings_file=None,
                         configuration_protected_settings_file=None, tags=None):
    """Create a new Extension Instance.

    """
    extension_type_lower = extension_type.lower()

    # Determine ClusterRP
    cluster_rp = __get_cluster_rp(cluster_type)

    # Configuration Settings & Configuration Protected Settings
    if configuration_settings is not None and configuration_settings_file is not None:
        raise MutuallyExclusiveArgumentError(
            'Error! Both configuration-settings and configuration-settings-file cannot be provided.'
        )

    if configuration_protected_settings is not None and configuration_protected_settings_file is not None:
        raise MutuallyExclusiveArgumentError(
            'Error! Both configuration-protected-settings and configuration-protected-settings-file '
            'cannot be provided.'
        )

    config_settings = {}
    config_protected_settings = {}
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

    # Identity is not created by default.  Extension type must specify if identity is required.
    create_identity = False
    extension_instance = None

    # Scope & Namespace validation - common to all extension-types
    __validate_scope_and_namespace(scope, release_namespace, target_namespace)

    # Give Partners a chance to their extensionType specific validations and to set value over-rides.

    # Get the extension class based on the extension name
    extension_class = ExtensionFactory(extension_type_lower)
    extension_instance, name, create_identity = extension_class.Create(
        cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type_lower, scope,
        auto_upgrade_minor_version, release_train, version, target_namespace, release_namespace, config_settings,
        config_protected_settings, configuration_settings_file, configuration_protected_settings_file)

    # Common validations
    __validate_version_and_auto_upgrade(extension_instance.version, extension_instance.auto_upgrade_minor_version)
    __validate_scope_after_customization(extension_instance.scope)

    # Create identity, if required
    if create_identity:
        extension_instance.identity, extension_instance.location = \
            __create_identity(cmd, resource_group_name, cluster_name, cluster_type, cluster_rp)

    # Try to create the resource
    return client.create(resource_group_name, cluster_rp, cluster_type, cluster_name, name, extension_instance)


def list_k8s_extension(client, resource_group_name, cluster_name, cluster_type):
    cluster_rp = __get_cluster_rp(cluster_type)
    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


def update_k8s_extension(client, resource_group_name, cluster_type, cluster_name, name,
                         auto_upgrade_minor_version='', release_train='', version='', tags=None):

    """Patch an existing Extension Instance.

    """

    # TODO: Remove this after we eventually get PATCH implemented for update and uncomment
    raise CommandNotFoundError(
        f"\"{consts.EXTENSION_NAME} update\" currently is not available. "
        f"Use \"{consts.EXTENSION_NAME} create\" to update a previously created extension instance."
    )

    # # Ensure some values are provided for update
    # if auto_upgrade_minor_version is None and release_train is None and version is None:
    #     message = "Error! No values provided for update. Provide new value(s) for one or more of these properties:" \
    #               " auto-upgrade-minor-version, release-train or version."
    #     raise RequiredArgumentMissingError(message)

    # # Determine ClusterRP
    # cluster_rp = __get_cluster_rp(cluster_type)

    # # Get the existing extensionInstance
    # extension = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)

    # extension_type_lower = extension.extension_type.lower()

    # # Get the extension class based on the extension name
    # extension_class = ExtensionFactory(extension_type_lower)
    # upd_extension = extension_class.Update(extension, auto_upgrade_minor_version, release_train, version)

    # __validate_version_and_auto_upgrade(version, auto_upgrade_minor_version)

    # upd_extension = ExtensionInstanceUpdate(auto_upgrade_minor_version=auto_upgrade_minor_version,
    #                                         release_train=release_train, version=version)

    # return client.update(resource_group_name, cluster_rp, cluster_type, cluster_name, name, upd_extension)


def delete_k8s_extension(client, resource_group_name, cluster_name, name, cluster_type):
    """Delete an existing Kubernetes Extension.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_rp(cluster_type)
    return client.delete(resource_group_name, cluster_rp, cluster_type, cluster_name, name)


def __create_identity(cmd, resource_group_name, cluster_name, cluster_type, cluster_rp):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(subscription_id,
                                                                                               resource_group_name,
                                                                                               cluster_rp,
                                                                                               cluster_type,
                                                                                               cluster_name)

    if cluster_rp == 'Microsoft.Kubernetes':
        parent_api_version = '2020-01-01-preview'
    elif cluster_rp == 'Microsoft.ResourceConnector':
        parent_api_version = '2020-09-15-privatepreview'
    elif cluster_rp == 'Microsoft.ContainerService':
        parent_api_version = '2017-07-01'
    else:
        raise InvalidArgumentValueError(
            "Error! Cluster type '{}' is not supported for extension identity".format(cluster_type)
        )

    try:
        resource = resources.get_by_id(cluster_resource_id, parent_api_version)
        location = str(resource.location.lower())
    except CloudError as ex:
        raise ex
    identity_type = "SystemAssigned"

    return ConfigurationIdentity(type=identity_type), location


def __get_cluster_rp(cluster_type):
    rp = ""
    if cluster_type.lower() == 'connectedclusters':
        rp = 'Microsoft.Kubernetes'
    elif cluster_type.lower() == 'appliances':
        rp = 'Microsoft.ResourceConnector'
    elif cluster_type.lower() == '':
        rp = 'Microsoft.ContainerService'
    else:
        raise InvalidArgumentValueError("Error! Cluster type '{}' is not supported".format(cluster_type))
    return rp


def __validate_scope_and_namespace(scope, release_namespace, target_namespace):
    if scope == 'cluster':
        if target_namespace is not None:
            message = "When --scope is 'cluster', --target-namespace must not be given."
            raise MutuallyExclusiveArgumentError(message)
    else:
        if release_namespace is not None:
            message = "When --scope is 'namespace', --release-namespace must not be given."
            raise MutuallyExclusiveArgumentError(message)


def __validate_scope_after_customization(scope_obj: Scope):
    if scope_obj is not None and scope_obj.namespace is not None and scope_obj.namespace.target_namespace is None:
        message = "When --scope is 'namespace', --target-namespace must be given."
        raise RequiredArgumentMissingError(message)


def __validate_version_and_auto_upgrade(version, auto_upgrade_minor_version):
    if version is not None:
        if auto_upgrade_minor_version:
            message = "To pin to specific version, auto-upgrade-minor-version must be set to 'false'."
            raise MutuallyExclusiveArgumentError(message)

        auto_upgrade_minor_version = False


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
