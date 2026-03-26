# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument,too-many-locals

import contextlib
import logging
import os
import platform
import shutil
import stat
import time

from .utils import (
    get_cluster_rp_api_version,
    is_dogfood_cluster,
    read_config_settings_file,
)
from knack.log import get_logger

from azure.cli.core import get_default_cli, telemetry

from azure.cli.core.azclierror import (
    ClientRequestError,
    CLIInternalError,
    FileOperationError,
    ResourceNotFoundError,
    ManualInterrupt,
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
from .partner_extensions.DefaultExtension import (
    DefaultExtension,
    user_confirmation_factory,
)
from . import consts
from . import utils

from ._client_factory import cf_resources

from kubernetes import client as kube_client
from kubernetes import config
from kubernetes.config.kube_config import KubeConfigMerger
from kubernetes.client.rest import ApiException
from kubernetes.client import CoreV1Api, V1NodeList

from typing import Optional, Union

import oras.client

from knack.commands import CLICommand

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


def troubleshoot_extension(
    cmd: CLICommand,
    name: str,
    namespace_list: str,
    kube_config: Optional[str] = None,
    kube_context: Optional[str] = None,
    skip_ssl_verification: bool = False,
) -> None:

    """Troubleshoot an existing Kubernetes Extension."""

    try:
        print("Collecting diagnostics information from the namespaces provided. This operation may take a while to complete ...\n")

        namespaces = [ns.strip() for ns in namespace_list.split(',') if ns.strip()]

        # Check if namespaces list is empty and throw an exception
        if not namespaces:
            raise RequiredArgumentMissingError(
                "No valid namespaces provided. Please provide at least one namespace."
            )

        # Setting the intial values as True
        storage_space_available = True

        # Setting kube_config
        kube_config = set_kube_config(kube_config)
        kube_client.rest.logger.setLevel(logging.WARNING)

        # Loading the kubeconfig file in kubernetes client configuration
        load_kube_config(kube_config, kube_context, skip_ssl_verification)

        # Install helm client
        helm_client_location = install_helm_client(cmd)

        # Install kubectl client
        kubectl_client_location = install_kubectl_client()

        # Checking the connection to kubernetes cluster.
        check_kube_connection()

        # Creating timestamp folder to store all the diagnoser logs
        diagnostic_logs_folder_name = utils.create_unique_folder_name(name)

        # Generate the diagnostic folder in a given location
        filepath_with_timestamp, diagnostic_folder_status = (
            utils.create_folder_diagnosticlogs(
                diagnostic_logs_folder_name, consts.ARC_EXT_DIAGNOSTIC_LOGS
            )
        )

        if diagnostic_folder_status is not True:
            storage_space_available = False

        api_instance = kube_client.CoreV1Api()

        for namespace in namespaces:
            collect_namespace_status = collect_namespace(api_instance,filepath_with_timestamp, namespace)
            if collect_namespace_status is not True:
                storage_space_available = False

        if storage_space_available:
            print(
                f"The diagnoser logs have been saved at this path: '{filepath_with_timestamp}'.\n"
                "These logs can be attached while filing a "
                "support ticket for further assistance.\n"
            )
        else:
            logger.warning(
                "The diagnoser was unable to save logs to your machine. Please check whether sufficient storage is "
                "available and run the troubleshoot command again."
            )

    # Handling the user manual interrupt
    except KeyboardInterrupt:
        raise ManualInterrupt("Process terminated externally.")

def collect_namespace(api_instance: CoreV1Api, base_path: str, namespace: str) -> bool:
    print(f"Step: {utils.get_utctimestring()}: Collecting diagnostics information for namespace '{namespace}'...")

    collection_success = True

    if not utils.check_namespace_exists(api_instance, namespace):
        logger.warning(f"Namespace '{namespace}' does not exist. Skipping...")
        return collection_success

    folder_namespace, folder_namespace_status = (
        utils.create_folder_diagnostics_namespace(base_path, namespace)
    )

    if folder_namespace_status is not True:
        logger.error(f"Failed to create diagnostics folder for namespace '{namespace}'.")
        collection_success = False

    logs_status = (
        utils.collect_namespace_configmaps(api_instance, folder_namespace, namespace)
    )

    if logs_status is not True:
        collection_success = False

    pods_status = (
        utils.walk_through_pods(api_instance, folder_namespace, namespace)
    )

    if pods_status is not True:
        collection_success = False

    return collection_success

def set_kube_config(kube_config: Union[str, None]) -> Union[str, None]:
    print(f"Step: {utils.get_utctimestring()}: Setting KubeConfig")
    if kube_config:
        # Trim kubeconfig. This is required for windows os.
        if kube_config.startswith(("'", '"')):
            kube_config = kube_config[1:]
        if kube_config.endswith(("'", '"')):
            kube_config = kube_config[:-1]
        return kube_config
    return None

def load_kube_config(
    kube_config: Union[str, None], kube_context: Union[str, None], skip_ssl_verification: bool
) -> None:
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
        if skip_ssl_verification:
            from kubernetes.client import Configuration

            default_config = Configuration.get_default_copy()
            default_config.verify_ssl = False
            Configuration.set_default(default_config)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.LOAD_KUBECONFIG_FAULT_TYPE,
            summary="Problem loading the kubeconfig file",
        )
        logger.warning(consts.KUBECONFIG_LOAD_FAILED_WARNING)
        raise FileOperationError("Problem loading the kubeconfig file. " + str(e))

def install_helm_client(cmd: CLICommand) -> str:
    print(
        f"Step: {utils.get_utctimestring()}: Install Helm client if it does not exist"
    )
    # Return helm client path set by user
    helm_client_path = os.getenv("HELM_CLIENT_PATH")
    if helm_client_path:
        return helm_client_path

    # Fetch system related info
    operating_system = platform.system().lower()
    machine_type = platform.machine()

    # Send machine telemetry
    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.MachineType": machine_type}
    )
    # Set helm binary download & install locations
    if operating_system == "windows":
        download_location_string = f".azure\\helm\\{consts.HELM_VERSION}"
        download_file_name = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip"
        install_location_string = (
            f".azure\\helm\\{consts.HELM_VERSION}\\{operating_system}-amd64\\helm.exe"
        )
        artifactTag = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64"
    elif operating_system == "linux" or operating_system == "darwin":
        download_location_string = f".azure/helm/{consts.HELM_VERSION}"
        download_file_name = (
            f"helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz"
        )
        install_location_string = (
            f".azure/helm/{consts.HELM_VERSION}/{operating_system}-amd64/helm"
        )
        artifactTag = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64"
    else:
        telemetry.set_exception(
            exception="Unsupported OS for installing helm client",
            fault_type=consts.Helm_Unsupported_OS_Fault_Type,
            summary=f"{operating_system} is not supported for installing helm client",
        )
        raise ClientRequestError(
            f"The {operating_system} platform is not currently supported for installing helm client."
        )

    download_location = os.path.expanduser(os.path.join("~", download_location_string))
    download_dir = os.path.dirname(download_location)
    install_location = os.path.expanduser(os.path.join("~", install_location_string))

    # Download compressed Helm binary if not already present
    if not os.path.isfile(install_location):
        # Creating the helm folder if it doesnt exist
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                telemetry.set_exception(
                    exception=e,
                    fault_type=consts.Create_Directory_Fault_Type,
                    summary="Unable to create helm directory",
                )
                raise ClientRequestError("Failed to create helm directory." + str(e))

        # Downloading compressed helm client executable
        logger.warning(
            "Downloading helm client for first time. This can take few minutes..."
        )

        mcr_url = utils.get_mcr_path(cmd.cli_ctx.cloud.endpoints.active_directory)

        client = oras.client.OrasClient(hostname=mcr_url)
        retry_count = 3
        retry_delay = 5
        for i in range(retry_count):
            try:
                client.pull(
                    target=f"{mcr_url}/{consts.HELM_MCR_URL}:{artifactTag}",
                    outdir=download_location,
                )
                break
            except Exception as e:
                if i == retry_count - 1:
                    if "Connection reset by peer" in str(e):
                        telemetry.set_user_fault()
                    telemetry.set_exception(
                        exception=e,
                        fault_type=consts.Download_Helm_Fault_Type,
                        summary="Unable to download helm client.",
                    )
                    raise CLIInternalError(
                        f"Failed to download helm client: {e}",
                        recommendation="Please check your internet connection.",
                    )
                time.sleep(retry_delay)

        # Extract the archive.
        try:
            extract_dir = download_location
            download_location = os.path.expanduser(
                os.path.join(download_location, download_file_name)
            )
            shutil.unpack_archive(download_location, extract_dir)
            os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.EXTRACT_HELMEXE_FAULT_TYPE,
                summary="Unable to extract helm executable",
            )
            reco_str = f"Please ensure that you delete the directory '{extract_dir}' before trying again."
            raise ClientRequestError(
                "Failed to extract helm executable." + str(e), recommendation=reco_str
            )

    return install_location

def install_kubectl_client() -> str:
    print(
        f"Step: {utils.get_utctimestring()}: Install Kubectl client if it does not exist"
    )
    # Return kubectl client path set by user
    kubectl_client_path = os.getenv("KUBECTL_CLIENT_PATH")
    if kubectl_client_path:
        return kubectl_client_path

    try:
        # Fetching the current directory where the cli installs the kubectl executable
        home_dir = os.path.expanduser("~")
        kubectl_filepath = os.path.join(home_dir, ".azure", "kubectl-client")

        with contextlib.suppress(FileExistsError):
            os.makedirs(kubectl_filepath)

        # Setting path depending on the OS being used
        operating_system = platform.system().lower()
        kubectl = "kubectl.exe" if operating_system == "windows" else "kubectl"
        kubectl_path = os.path.join(kubectl_filepath, kubectl)

        if os.path.isfile(kubectl_path):
            return kubectl_path

        # Downloading kubectl executable if its not present in the machine
        logger.warning(
            "Downloading kubectl client for first time. This can take few minutes..."
        )
        logging.disable(logging.CRITICAL)
        get_default_cli().invoke(
            ["aks", "install-cli", "--install-location", kubectl_path]
        )
        logging.disable(logging.NOTSET)
        logger.warning("\n")
        # Return the path of the kubectl executable
        return kubectl_path

    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.DOWNLOAD_AND_INSTALL_KUBECTL_FAULT_TYPE,
            summary="Failed to download and install kubectl",
        )
        raise CLIInternalError(f"Unable to install kubectl. Error: {e}")

def check_kube_connection() -> str:
    print(f"Step: {utils.get_utctimestring()}: Checking Connectivity to Cluster")
    api_instance = kube_client.VersionApi()
    try:
        api_response = api_instance.get_code()
        git_version: str = api_response.git_version
        return git_version
    except Exception as e:  # pylint: disable=broad-except
        logger.warning(consts.KUBEAPI_CONNECTIVITY_FAILED_WARNING)
        utils.kubernetes_exception_handler(
            e,
            consts.KUBERNETES_CONNECTIVITY_FAULT_TYPE,
            "Unable to verify connectivity to the Kubernetes cluster",
        )

    raise CLIInternalError(
        "Unable to verify connectivity to the Kubernetes cluster. No version information could be retrieved.")

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
