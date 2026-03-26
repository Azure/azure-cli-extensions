# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import shutil
import time
import re
import os
import contextlib

from typing import Tuple, Union
from urllib.parse import urlparse
from . import consts
from azure.cli.core import telemetry
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError, ValidationError

from kubernetes.client import CoreV1Api, V1NodeList
from kubernetes.client.rest import ApiException

from knack.log import get_logger
from knack.commands import CLICommand

logger = get_logger(__name__)

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

        if pod.spec is not None:
            if pod.spec.init_containers is not None:
                for init_container in pod.spec.init_containers:
                    init_container_logs_status = collect_container_logs(api_instance, containers_folder_name, namespace, pod_name, init_container)
                    if not init_container_logs_status:
                        logger.error(f"Failed to collect logs from init container '{init_container.name}' in pod '{pod_name}'")
            if pod.spec.containers is not None:
                for container in pod.spec.containers:
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
                        name=pod_name, container=container_name, namespace=namespace
                    )

    container_logs_file_name = os.path.join(containers_folder_name, f"{container_name}_logs.txt")

    try:
        with open(container_logs_file_name, "w") as logs_file:
            logs_file.write(str(container_log))
    except Exception as e:
        logger.error(f"Failed to save logs for container '{container_name}' in pod '{pod_name}': {e}")
        return False

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
