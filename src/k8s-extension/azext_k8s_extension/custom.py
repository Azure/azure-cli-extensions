# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument,too-many-locals

from .utils import (
    get_cluster_rp_api_version,
    is_dogfood_cluster,
    read_config_settings_file,
)
from knack.log import get_logger

from azure.cli.core.azclierror import (
    ResourceNotFoundError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from azure.core.exceptions import HttpResponseError
from .vendored_sdks.models import Identity, Scope
from ._validators import validate_cc_registration

from .partner_extensions.ContainerInsights import ContainerInsights
from .partner_extensions.AzureMonitorMetrics import AzureMonitorMetrics
from .partner_extensions.AzureDefender import AzureDefender
from .partner_extensions.OpenServiceMesh import OpenServiceMesh
from .partner_extensions.AzureMLKubernetes import AzureMLKubernetes
from .partner_extensions.DataProtectionKubernetes import DataProtectionKubernetes
from .partner_extensions.Dapr import Dapr
from .partner_extensions.EntraWorkloadIAM import EntraWorkloadIAM
from .partner_extensions.DefaultExtension import (
    DefaultExtension,
    user_confirmation_factory,
)
from . import consts

from ._client_factory import cf_resources

logger = get_logger(__name__)


# A factory method to return the correct extension class based off of the extension name
def ExtensionFactory(extension_name):
    extension_map = {
        "microsoft.azuremonitor.containers": ContainerInsights,
        "microsoft.azuremonitor.containers.metrics": AzureMonitorMetrics,
        "microsoft.azuredefender.kubernetes": AzureDefender,
        "microsoft.openservicemesh": OpenServiceMesh,
        "microsoft.azureml.kubernetes": AzureMLKubernetes,
        "microsoft.dapr": Dapr,
        "microsoft.dataprotection.kubernetes": DataProtectionKubernetes,
        "microsoft.entraworkloadiam": EntraWorkloadIAM,
    }

    # Return the extension if we find it in the map, else return the default
    return extension_map.get(extension_name, DefaultExtension)()


def show_k8s_extension(client, resource_group_name, cluster_name, name, cluster_type, cluster_resource_provider=None):
    """Get an existing K8s Extension."""
    # Determine ClusterRP
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)

    try:
        extension = client.get(
            resource_group_name, cluster_rp, cluster_type, cluster_name, name
        )
        return extension
    except HttpResponseError as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = "{0} Verify that the cluster-type is correct and the resource exists.".format(
                    ex.message
                )
            # If Configuration not found
            elif ex.message.__contains__(
                "Operation returned an invalid status code 'Not Found'"
            ):
                message = (
                    "(ExtensionNotFound) The Resource {0}/{1}/{2}/Microsoft.KubernetesConfiguration/"
                    "extensions/{3} could not be found!".format(
                        cluster_rp, cluster_type, cluster_name, name
                    )
                )
            else:
                message = ex.message
            raise ResourceNotFoundError(message) from ex
        raise ex


def create_k8s_extension(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    name,
    cluster_type,
    extension_type,
    cluster_resource_provider=None,
    scope=None,
    auto_upgrade_minor_version=None,
    release_train=None,
    version=None,
    target_namespace=None,
    release_namespace=None,
    configuration_settings=None,
    configuration_protected_settings=None,
    configuration_settings_file=None,
    configuration_protected_settings_file=None,
    no_wait=False,
    plan_name=None,
    plan_publisher=None,
    plan_product=None
):
    """Create a new Extension Instance."""

    extension_type_lower = extension_type.lower()
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)

    # Configuration Settings & Configuration Protected Settings
    if configuration_settings is not None and configuration_settings_file is not None:
        raise MutuallyExclusiveArgumentError(
            "Error! Both configuration-settings and configuration-settings-file cannot be provided."
        )

    if (
        configuration_protected_settings is not None
        and configuration_protected_settings_file is not None
    ):
        raise MutuallyExclusiveArgumentError(
            "Error! Both configuration-protected-settings and configuration-protected-settings-file "
            "cannot be provided."
        )

    config_settings = {}
    config_protected_settings = {}
    # Get Configuration Settings from file
    if configuration_settings_file is not None:
        config_settings = read_config_settings_file(configuration_settings_file)

    if configuration_settings is not None:
        for dicts in configuration_settings:
            for key, value in dicts.items():
                config_settings[key] = value

    # Get Configuration Protected Settings from file
    if configuration_protected_settings_file is not None:
        config_protected_settings = read_config_settings_file(
            configuration_protected_settings_file
        )

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
        cmd,
        client,
        resource_group_name,
        cluster_name,
        name,
        cluster_type,
        cluster_rp,
        extension_type_lower,
        scope,
        auto_upgrade_minor_version,
        release_train,
        version,
        target_namespace,
        release_namespace,
        config_settings,
        config_protected_settings,
        configuration_settings_file,
        configuration_protected_settings_file,
        plan_name,
        plan_publisher,
        plan_product
    )

    # Common validations
    __validate_version_and_auto_upgrade(
        extension_instance.version, extension_instance.auto_upgrade_minor_version
    )
    __validate_scope_after_customization(extension_instance.scope)

    # Check that registration has been done on Microsoft.KubernetesConfiguration for the subscription
    validate_cc_registration(cmd)

    # Create identity, if required
    # We don't create the identity if we are in DF
    if create_identity and not is_dogfood_cluster(cmd):
        identity_object, location = __create_identity(
            cmd, resource_group_name, cluster_name, cluster_type, cluster_rp
        )
        if identity_object is not None and location is not None:
            extension_instance.identity, extension_instance.location = (
                identity_object,
                location,
            )

    # Try to create the resource
    return sdk_no_wait(
        no_wait,
        client.begin_create,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        extension_instance,
    )


def list_k8s_extension(client, resource_group_name, cluster_name, cluster_type, cluster_resource_provider=None):
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


def update_k8s_extension(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    name,
    cluster_type,
    cluster_resource_provider=None,
    auto_upgrade_minor_version=None,
    release_train=None,
    version=None,
    configuration_settings=None,
    configuration_protected_settings=None,
    configuration_settings_file=None,
    configuration_protected_settings_file=None,
    no_wait=False,
    yes=False,
):
    """Patch an existing Extension Instance."""

    if (
        configuration_settings
        or configuration_protected_settings
        or configuration_settings_file
        or configuration_protected_settings_file
    ):
        msg = (
            "Updating properties in --configuration-settings or --configuration-protected-settings may lead to undesirable state"
            " if the cluster extension type does not support it. Please refer to the documentation of the"
            " cluster extension service to check if updates to these properties is supported."
            " Do you wish to proceed?"
        )
        user_confirmation_factory(cmd, yes, msg)

    # Determine ClusterRP
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)

    # We need to determine the ExtensionType to call ExtensionFactory and create Extension class
    extension = show_k8s_extension(
        client, resource_group_name, cluster_name, name, cluster_type, cluster_rp
    )
    extension_type_lower = extension.extension_type.lower()

    config_settings = {}
    config_protected_settings = {}
    # Get Configuration Settings from file
    if configuration_settings_file is not None:
        config_settings = read_config_settings_file(configuration_settings_file)

    if configuration_settings is not None:
        for dicts in configuration_settings:
            for key, value in dicts.items():
                config_settings[key] = value

    # Get Configuration Protected Settings from file
    if configuration_protected_settings_file is not None:
        config_protected_settings = read_config_settings_file(
            configuration_protected_settings_file
        )

    if configuration_protected_settings is not None:
        for dicts in configuration_protected_settings:
            for key, value in dicts.items():
                config_protected_settings[key] = value

    # Get the extension class based on the extension type
    extension_class = ExtensionFactory(extension_type_lower)

    upd_extension = extension_class.Update(
        cmd,
        resource_group_name,
        cluster_name,
        auto_upgrade_minor_version,
        release_train,
        version,
        config_settings,
        config_protected_settings,
        extension,
        yes,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        upd_extension,
    )


def delete_k8s_extension(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    name,
    cluster_type,
    cluster_resource_provider=None,
    no_wait=False,
    yes=False,
    force=False,
):
    """Delete an existing Kubernetes Extension."""
    # Determine ClusterRP
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_resource_provider)
    extension = None
    try:
        extension = client.get(
            resource_group_name, cluster_rp, cluster_type, cluster_name, name
        )
    except HttpResponseError:
        logger.warning(
            "No extension with name '%s' found on cluster '%s', so nothing to delete",
            name,
            cluster_name,
        )
        return None
    extension_class = ExtensionFactory(extension.extension_type.lower())

    # If there is any custom delete logic, this will call the logic
    extension_class.Delete(
        cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp, yes
    )

    return sdk_no_wait(
        no_wait,
        client.begin_delete,
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        force_delete=force,
    )


# list by location
def list_extension_types_by_location(
        client,
        location,
        plan_publisher=None,
        plan_product=None,
        plan_name=None,
        release_train=None,
        cluster_type=None):

    """ List available Cluster Extension Types in a region."""

    return client.location_list(
        location,
        plan_publisher,
        plan_product,
        plan_name,
        release_train,
        cluster_type)


# get by location
def show_extension_type_by_location(client, location, extension_type):

    """Get properties for a Cluster Extension Type in a region."""
    return client.location_get(
        location,
        extension_type
    )


# list version by location
def list_extension_type_versions_by_location(
        client,
        location,
        extension_type,
        release_train=None,
        cluster_type=None,
        major_version=None,
        show_latest=False):

    """ List available versions for a Cluster Extension Type versions in a region. """

    versions_list = client.list_versions(
        location,
        extension_type,
        release_train,
        cluster_type,
        major_version,
        show_latest)
    return versions_list


# get version by location
def show_extension_type_version_by_location(
        client,
        location,
        extension_type,
        version):

    """ Get properties associated with a Cluster Extension Type version in a region."""
    version = client.get_version(
        location,
        extension_type,
        version)
    return version


# list by cluster
def list_extension_types_by_cluster(
        client,
        resource_group_name,
        cluster_name,
        cluster_type,
        plan_publisher=None,
        plan_name=None,
        plan_product=None,
        release_train=None):

    """ List available Cluster Extension Types for an existing cluster."""
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)

    return client.list(
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        plan_publisher,
        plan_product,
        plan_name,
        release_train)


# get by cluster
def show_extension_type_by_cluster(
        client,
        resource_group_name,
        cluster_name,
        cluster_type,
        extension_type):

    """ Get properties for a Cluster Extension Type for an existing cluster"""
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)

    return client.get(
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        extension_type)


# list version by cluster
def list_extension_type_versions_by_cluster(
        client,
        resource_group_name,
        cluster_type,
        cluster_name,
        extension_type,
        release_train=None,
        major_version=None,
        show_latest=False):

    """ List available versions for a Cluster Extension Type for a given cluster."""
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)

    return client.cluster_list_versions(
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        extension_type,
        release_train,
        major_version,
        show_latest)


# get version by cluster
def show_extension_type_version_by_cluster(
        client,
        resource_group_name,
        cluster_type,
        cluster_name,
        extension_type,
        version):

    """ Get properties associated with a Cluster Extension Type version for an existing cluster"""

    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)

    return client.cluster_get_version(
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        extension_type,
        version)


def __create_identity(cmd, resource_group_name, cluster_name, cluster_type, cluster_rp):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    # We do not create any identities for managedClusters
    if cluster_type.lower() == consts.MANAGED_CLUSTER_TYPE:
        return None, None

    cluster_rp, parent_api_version = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_rp)

    cluster_resource_id = (
        "/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}".format(
            subscription_id, resource_group_name, cluster_rp, cluster_type, cluster_name
        )
    )

    try:
        resource = resources.get_by_id(cluster_resource_id, parent_api_version)
        location = str(resource.location.lower())
    except HttpResponseError as ex:
        raise ex
    identity_type = "SystemAssigned"

    return Identity(type=identity_type), location


def __validate_scope_and_namespace(scope, release_namespace, target_namespace):
    if scope == "cluster":
        if target_namespace is not None:
            message = "When --scope is 'cluster', --target-namespace must not be given."
            raise MutuallyExclusiveArgumentError(message)
    else:
        if release_namespace is not None:
            message = (
                "When --scope is 'namespace', --release-namespace must not be given."
            )
            raise MutuallyExclusiveArgumentError(message)


def __validate_scope_after_customization(scope_obj: Scope):
    if (
        scope_obj is not None
        and scope_obj.namespace is not None
        and scope_obj.namespace.target_namespace is None
    ):
        message = "When --scope is 'namespace', --target-namespace must be given."
        raise RequiredArgumentMissingError(message)


def __validate_version_and_auto_upgrade(version, auto_upgrade_minor_version):
    if version is not None:
        if auto_upgrade_minor_version:
            message = "To pin to specific version, auto-upgrade-minor-version must be set to 'false'."
            raise MutuallyExclusiveArgumentError(message)

        auto_upgrade_minor_version = False
