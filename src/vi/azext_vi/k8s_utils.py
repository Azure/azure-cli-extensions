# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import logging
import os
import platform
import shutil
import stat
import time
import json
import shutil
import time
import re
import os
import contextlib

from knack.log import get_logger

from azure.cli.core import get_default_cli

from azure.cli.core.azclierror import (
    ClientRequestError,
    CLIInternalError,
    FileOperationError,
    ManualInterrupt,
    RequiredArgumentMissingError,
)

from . import consts

from kubernetes import client as kube_client
from kubernetes import config
from kubernetes.config.kube_config import KubeConfigMerger
from kubernetes.client.rest import ApiException
from kubernetes.client import CoreV1Api, V1NodeList

from typing import Optional, Tuple, Union
import oras.client

from knack.commands import CLICommand

logger = get_logger(__name__)


def troubleshoot_k8s_extension(
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
        diagnostic_logs_folder_name = create_unique_folder_name(name)

        # Generate the diagnostic folder in a given location
        filepath_with_timestamp, diagnostic_folder_status = (
            create_folder_diagnosticlogs(
                diagnostic_logs_folder_name, consts.ARC_EXT_DIAGNOSTIC_LOGS
            )
        )

        if diagnostic_folder_status is not True:
            storage_space_available = False

        api_instance = kube_client.CoreV1Api()

        for namespace in namespaces:
            collect_namespace_status = collect_namespace(api_instance, filepath_with_timestamp, namespace)
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
    print(f"Step: {get_utctimestring()}: Collecting diagnostics information for namespace '{namespace}'...")

    collection_success = True

    if not check_namespace_exists(api_instance, namespace):
        logger.warning(f"Namespace '{namespace}' does not exist. Skipping...")
        return collection_success

    folder_namespace, folder_namespace_status = (
        create_folder_diagnostics_namespace(base_path, namespace)
    )

    if folder_namespace_status is not True:
        logger.error(f"Failed to create diagnostics folder for namespace '{namespace}'.")
        collection_success = False

    logs_status = (
        collect_namespace_configmaps(api_instance, folder_namespace, namespace)
    )

    if logs_status is not True:
        collection_success = False

    pods_status = (
        walk_through_pods(api_instance, folder_namespace, namespace)
    )

    if pods_status is not True:
        collection_success = False

    return collection_success

def set_kube_config(kube_config: Union[str, None]) -> Union[str, None]:
    print(f"Step: {get_utctimestring()}: Setting KubeConfig")
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
        logger.warning(consts.KUBECONFIG_LOAD_FAILED_WARNING)
        raise FileOperationError("Problem loading the kubeconfig file. " + str(e))

def install_helm_client(cmd: CLICommand) -> str:
    print(
        f"Step: {get_utctimestring()}: Install Helm client if it does not exist"
    )
    # Return helm client path set by user
    helm_client_path = os.getenv("HELM_CLIENT_PATH")
    if helm_client_path:
        return helm_client_path

    # Fetch system related info
    operating_system = platform.system().lower()
    machine_type = platform.machine()

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
                raise ClientRequestError("Failed to create helm directory." + str(e))

        # Downloading compressed helm client executable
        logger.warning(
            "Downloading helm client for first time. This can take few minutes..."
        )

        mcr_url = get_mcr_path(cmd.cli_ctx.cloud.endpoints.active_directory)

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
                        print("Connection reset by peer error encountered while downloading helm client. This is likely a transient network issue.")
           
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
            reco_str = f"Please ensure that you delete the directory '{extract_dir}' before trying again."
            raise ClientRequestError(
                "Failed to extract helm executable." + str(e), recommendation=reco_str
            )

    return install_location

def install_kubectl_client() -> str:
    print(
        f"Step: {get_utctimestring()}: Install Kubectl client if it does not exist"
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
        raise CLIInternalError(f"Unable to install kubectl. Error: {e}")

def check_kube_connection() -> str:
    print(f"Step: {get_utctimestring()}: Checking Connectivity to Cluster")
    api_instance = kube_client.VersionApi()
    try:
        api_response = api_instance.get_code()
        git_version: str = api_response.git_version
        return git_version
    except Exception as e:  # pylint: disable=broad-except
        logger.warning(consts.KUBEAPI_CONNECTIVITY_FAILED_WARNING)
        kubernetes_exception_handler(
            e,
            consts.KUBERNETES_CONNECTIVITY_FAULT_TYPE,
            "Unable to verify connectivity to the Kubernetes cluster",
        )

    raise CLIInternalError(
        "Unable to verify connectivity to the Kubernetes cluster. No version information could be retrieved.")

def get_cluster_rp_api_version(cluster_type, cluster_rp=None) -> Tuple[str, str]:
    if cluster_type.lower() == consts.PROVISIONED_CLUSTER_TYPE:
        if cluster_rp is None or cluster_rp.strip() == "":
            raise RequiredArgumentMissingError(
                "Error! Cluster Resource Provider value is required for Cluster Type '{}'".format(cluster_type)
            )
        if cluster_rp.lower() == consts.HYBRIDCONTAINERSERVICE_RP:
            return (
                consts.HYBRIDCONTAINERSERVICE_RP,
                consts.HYBRIDCONTAINERSERVICE_API_VERSION,
            )
        raise InvalidArgumentValueError(
            "Error! Cluster type '{}' and Cluster Resource Provider '{}' combination is not supported".format(cluster_type, cluster_rp)
        )
    if cluster_type.lower() == consts.CONNECTED_CLUSTER_TYPE:
        return consts.CONNECTED_CLUSTER_RP, consts.CONNECTED_CLUSTER_API_VERSION
    if cluster_type.lower() == consts.APPLIANCE_TYPE:
        return consts.APPLIANCE_RP, consts.APPLIANCE_API_VERSION
    if (
        cluster_type.lower() == ""
        or cluster_type.lower() == consts.MANAGED_CLUSTER_TYPE
    ):
        return consts.MANAGED_CLUSTER_RP, consts.MANAGED_CLUSTER_API_VERSION
    raise InvalidArgumentValueError(
        "Error! Cluster type '{}' is not supported".format(cluster_type)
    )

def read_config_settings_file(file_path):
    try:
        with open(file_path, "r") as f:
            settings = json.load(f)
            if len(settings) == 0:
                raise Exception("File {} is empty".format(file_path))
            return settings
    except ValueError as ex:
        raise Exception("File {} is not a valid JSON file".format(file_path)) from ex

def is_dogfood_cluster(cmd):
    return (
        urlparse(cmd.cli_ctx.cloud.endpoints.resource_manager).hostname
        == consts.DF_RM_HOSTNAME
    )

def is_skip_prerequisites_specified(configuration_settings):
    # Determine if provisioning to prerequisites should be skipped by a configuration setting named skipPrerequisites.
    SKIP_PREQUISITES = 'skipPrerequisites'

    has_skip_prerequisites_set = False

    if SKIP_PREQUISITES in configuration_settings:
        skip_prerequisites_configuration_setting = configuration_settings[SKIP_PREQUISITES]
        if (isinstance(skip_prerequisites_configuration_setting, str) and str(skip_prerequisites_configuration_setting).lower() == "true") or (isinstance(skip_prerequisites_configuration_setting, bool) and skip_prerequisites_configuration_setting):
            has_skip_prerequisites_set = True

    return has_skip_prerequisites_set

def get_utctimestring() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())

def validate_node_api_response(api_instance: CoreV1Api) -> Union[V1NodeList, None]:
    try:
        node_api_response = api_instance.list_node()
        return node_api_response
    except Exception:
        logger.debug(
            "Error occurred while listing nodes on this kubernetes cluster:",
            exc_info=True,
        )
        return None

def kubernetes_exception_handler(
    ex: Exception,
    fault_type: str,
    summary: str,
    error_message: str = "Error occurred while connecting to the kubernetes cluster: ",
    message_for_unauthorized_request: str = "The user does not have required privileges on the "
    "kubernetes cluster to deploy Azure Arc enabled Kubernetes agents. Please "
    "ensure you have cluster admin privileges on the cluster to onboard.",
    message_for_not_found: str = "The requested kubernetes resource was not found.",
    raise_error: bool = True,
) -> None:
    telemetry.set_user_fault()
    if isinstance(ex, ApiException):
        status_code = ex.status
        if status_code == 403:
            logger.error(message_for_unauthorized_request)
        elif status_code == 404:
            logger.error(message_for_not_found)
        else:
            logger.debug("Kubernetes Exception: ", exc_info=True)
        if raise_error:
            telemetry.set_exception(
                exception=ex, fault_type=fault_type, summary=summary
            )
            raise ValidationError(error_message + "\nError Response: " + str(ex.body))
    else:
        if raise_error:
            telemetry.set_exception(
                exception=ex, fault_type=fault_type, summary=summary
            )
            raise ValidationError(error_message + "\nError: " + str(ex))

        logger.debug("Kubernetes Exception", exc_info=True)

def create_unique_folder_name(base_name: str) -> str:
    """Create a unique folder name using the base name and current timestamp.

    Args:
        base_name: The base name for the folder (will be sanitized)

    Returns:
        A string in the format: sanitized_base_name-YYYY-MM-DD-HH.MM.SS

    Example:
        create_unique_folder_name("name1@#$") -> "name1-2025-08-05-15.59.26"
    """

    sanitized_base_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)
    timestamp = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
    return f"{sanitized_base_name}-{timestamp}"

def create_folder_diagnostics_namespace(base_folder: str, namespace: str) -> tuple[str, bool]:
    print(
        f"Step: {get_utctimestring()}: Creating folder for namespace '{namespace}'"
    )
    namespace_folder_name = os.path.join(base_folder, namespace)
    try:
        os.makedirs(namespace_folder_name, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create diagnostics folder for namespace '{namespace}': {e}")
        return "", False

    return namespace_folder_name, True

def collect_namespace_configmaps(api_instance, namespace_folder_name: str, namespace: str) -> bool:
    print(
        f"Step: {get_utctimestring()}: Collecting configurations for namespace '{namespace}'"
    )

    namespace_configuration_folder_name = os.path.join(namespace_folder_name, "configuration")
    try:
        os.makedirs(namespace_configuration_folder_name, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create configuration folder for namespace '{namespace}': {e}")
        return False

    config_maps = api_instance.list_namespaced_config_map(namespace)

    for cm in config_maps.items:
        cm_name = cm.metadata.name
        cm_data = cm.data or {}
        cm_file_path = os.path.join(namespace_configuration_folder_name, f"{cm_name}.json")

        try:
            with open(cm_file_path, "w") as f:
                json.dump(cm_data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save ConfigMap '{cm_name}': {e}")
            return False

    return True

def walk_through_pods(api_instance: CoreV1Api, folder_namespace: str, namespace: str) -> bool:
    print(
        f"Step: {get_utctimestring()}: Collecting information from pods in namespace '{namespace}'"
    )

    try:
        pods = api_instance.list_namespaced_pod(namespace)
    except Exception as e:
        logger.error(f"Failed to list pods in namespace '{namespace}': {e}")
        return False

    pods_folder_name = os.path.join(folder_namespace, "pods")
    try:
        os.makedirs(pods_folder_name, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create pods folder for namespace '{namespace}': {e}")
        return False

    for pod in pods.items:
        pod_name = pod.metadata.name
        pod_information_status = collect_pod_information(api_instance, pods_folder_name, namespace, pod)
        if not pod_information_status:
            logger.error(f"Failed to collect information for pod '{pod_name}'")
            return False
        containers_folder_name = os.path.join(pods_folder_name, pod_name, "containers")
        try:
            os.makedirs(containers_folder_name, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create containers folder for pod '{pod_name}': {e}")
            return False
        
        otel_containers = ["mdm", "mdsd", "msi-adapter", "otel-collector"]

        if pod.spec is not None:
            if pod.spec.init_containers is not None:
                for init_container in pod.spec.init_containers:
                    if init_container.name in otel_containers:
                        continue
                    init_container_logs_status = collect_container_logs(api_instance, containers_folder_name, namespace, pod_name, init_container)
                    if not init_container_logs_status:
                        logger.error(f"Failed to collect logs from init container '{init_container.name}' in pod '{pod_name}'")
            if pod.spec.containers is not None:
                for container in pod.spec.containers:
                    if container.name in otel_containers:
                        continue
                    container_logs_status = collect_container_logs(api_instance, containers_folder_name, namespace, pod_name, container)
                    if not container_logs_status:
                        logger.error(f"Failed to collect logs from container '{container.name}' in pod '{pod_name}'")
                        return False

    return True

def collect_container_logs(api_instance: CoreV1Api, containers_folder_name: str, namespace: str, pod_name: str, container) -> bool:
    print(
        f"Step: {get_utctimestring()}: Collecting logs from container '{container.name}' in pod '{pod_name}'"
    )

    container_name = container.name

    container_log = api_instance.read_namespaced_pod_log(
                        name=pod_name, 
                        container=container_name, 
                        namespace=namespace)

    container_logs_file_name = os.path.join(containers_folder_name, f"{container_name}_logs.txt")

    try:
        with open(container_logs_file_name, "w") as logs_file:
            logs_file.write(str(container_log))
    except Exception as e:
        logger.error(f"Failed to save logs for container '{container_name}' in pod '{pod_name}': {e}")
        return True

    return True

def convert_to_pod_dict(pod) -> dict:
    if pod.metadata is None or pod.status is None:
        return None
    pod_metadata = pod.metadata
    pod_status = pod.status.phase
    return {
        "name": pod_metadata.name,
        "namespace": pod_metadata.namespace,
        "labels": pod_metadata.labels,
        "annotations": pod_metadata.annotations,
        "status": pod_status,
    }

def collect_pod_information(api_instance: CoreV1Api, pods_folder_name: str, namespace: str, pod) -> bool:
    pod_metadata = convert_to_pod_dict(pod)
    if pod_metadata is None:
        logger.error(f"Failed to collect metadata for pod in namespace '{namespace}'")
        return False

    pod_name = pod_metadata["name"]
    print(
        f"Step: {get_utctimestring()}: Collecting information for pod '{pod_name}' in namespace '{namespace}'"
    )

    pod_folder_name = os.path.join(pods_folder_name, pod_name)
    try:
        os.makedirs(pod_folder_name, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create folder for pod '{pod_name}': {e}")
        return False

    return save_pod_metadata(pod_folder_name, pod_metadata)

def save_pod_metadata(pod_folder_name: str, pod: dict) -> bool:
    metadata_file = os.path.join(pod_folder_name, "metadata.json")

    return save_as_json(metadata_file, pod)

def save_as_json(destination: str, data) -> bool:
    try:
        with open(destination, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Failed to save data to {destination}: {e}")
        return False

def create_folder_diagnosticlogs(folder_name: str, base_folder_name: str) -> tuple[str, bool]:
    print(
        f"Step: {get_utctimestring()}: Creating folder for extension Diagnostic Checks Logs"
    )
    try:
        # Fetching path to user directory to create the arc diagnostic folder
        home_dir = os.path.expanduser("~")
        filepath = os.path.join(home_dir, ".azure", base_folder_name)
        # Creating Diagnostic folder and its subfolder with the given timestamp and cluster name to store all the logs
        with contextlib.suppress(FileExistsError):
            os.mkdir(filepath)
        filepath_with_timestamp = os.path.join(filepath, folder_name)
        try:
            os.mkdir(filepath_with_timestamp)
        except FileExistsError:
            # Deleting the folder if present with the same timestamp to prevent overriding in the same folder and then
            #  creating it again
            shutil.rmtree(filepath_with_timestamp, ignore_errors=True)
            os.mkdir(filepath_with_timestamp)

        return filepath_with_timestamp, True

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            if filepath_with_timestamp:
                shutil.rmtree(filepath_with_timestamp, ignore_errors=False)
            telemetry.set_exception(
                exception=e,
                fault_type=consts.No_Storage_Space_Available_Fault_Type,
                summary="No space left on device",
            )
            return "", False
        logger.exception(
            "An exception has occurred while creating the diagnostic logs folder in "
            "your local machine."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type,
            summary="Error while trying to create diagnostic logs folder",
        )
        return "", False

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.exception(
            "An exception has occurred while creating the diagnostic logs folder in "
            "your local machine."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type,
            summary="Error while trying to create diagnostic logs folder",
        )
        return "", False

def get_mcr_path(active_directory_endpoint: str) -> str:
    active_directory_array = active_directory_endpoint.split(".")

    # For US Government and China clouds, use public mcr
    if active_directory_endpoint.endswith((".us", ".cn")):
        return "mcr.microsoft.com"

    # Default MCR postfix
    mcr_postfix = "com"
    # special cases for USSec, exclude part of suffix
    if len(active_directory_array) == 4 and active_directory_array[2] == "microsoft":
        mcr_postfix = active_directory_array[3]
    # special case for USNat
    elif len(active_directory_array) == 5:
        mcr_postfix = (
            active_directory_array[2]
            + "."
            + active_directory_array[3]
            + "."
            + active_directory_array[4]
        )

    mcr_url = f"mcr.microsoft.{mcr_postfix}"
    return mcr_url

def check_namespace_exists(api_instance, namespace: str) -> bool:
    print(f"Step: {get_utctimestring()}: Checking if namespace '{namespace}' exists...")
    try:
        api_instance.read_namespace(name=namespace)
        return True
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            raise  # Re-raise other exceptions
