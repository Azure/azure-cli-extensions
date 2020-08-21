# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# from docutils.nodes import version
from knack.util import CLIError

from azext_k8s_extension.vendored_sdks.models import ExtensionInstance
from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceForCreate
from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceUpdate
from azext_k8s_extension.vendored_sdks.models import ErrorResponseException
from azext_k8s_extension.vendored_sdks.models import ScopeCluster
from azext_k8s_extension.vendored_sdks.models import ScopeNamespace
from azext_k8s_extension.vendored_sdks.models import Scope


def show_k8s_extension(client, resource_group_name, cluster_name, name, cluster_type):
    """Get an existing K8s Extension.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    try:
        extension = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        return extension
    except ErrorResponseException as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = "{0} Verify that the --cluster-type is correct and the resource exists.".format(ex.message)
            # If Configuration not found
            elif ex.message.__contains__("Operation returned an invalid status code 'Not Found'"):
                message = "(ExtensionNotFound) The Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration/" \
                          "extensions/{3} could not be found!".format(cluster_rp, cluster_type, cluster_name, name)
            else:
                message = ex.message
            raise CLIError(message)


def create_k8s_extension(cmd, client, resource_group_name, cluster_name, name, cluster_type,
                         extension_type, scope, auto_upgrade_minor_version=True, release_train='Stable',
                         version=None, target_namespace=None, release_namespace=None, configuration_settings=None,
                         configuration_protected_settings=None, location=None, tags=None):
    """Create a new Extension Instance.

    """
    # Determine ClusterRP
    cluster_rp = __get_cluster_type(cluster_type)

    # Validate scope and namespace
    __validate_scope_and_namespace(scope, release_namespace, target_namespace)

    # Validate version, release_train
    __validate_version_and_release_train(version, release_train, auto_upgrade_minor_version)

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

    # Get Configuration Settings
    # ##for config_key in configuration_settings:

    # Create Extension Instance object
    extension_instance = ExtensionInstanceForCreate(extension_type=extension_type,
                                                    auto_upgrade_minor_version=auto_upgrade_minor_version,
                                                    release_train=release_train,
                                                    version=version,
                                                    scope=ext_scope,
                                                    configuration_settings=configuration_settings,
                                                    configuration_protected_settings=configuration_protected_settings)

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


def __validate_scope_and_namespace(scope, release_namespace, target_namespace):
    if scope == 'cluster':
        if target_namespace is not None:
            message = "When Scope is 'cluster', target_namespace must not be given."
            raise CLIError(message)
    else:
        if release_namespace is not None:
            message = "When Scope is 'namespace', release_namespace must not be given."
            raise CLIError(message)


def __validate_version_and_release_train(version, release_train, auto_upgrade_minor_version):
    if version is not None:
        if release_train is not None:
            message = "Both release_train and version cannot be given. To pin to specific version, give only version."
            raise CLIError(message)
        if auto_upgrade_minor_version is True:
            message = "To pin to specific version, auto_upgrade_minor_version must be set to 'false'."
            raise CLIError(message)
