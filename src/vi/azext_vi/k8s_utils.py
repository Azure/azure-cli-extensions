# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Kubernetes utilities for Azure CLI VI extension.

This module provides utilities for troubleshooting Kubernetes extensions,
collecting diagnostic information, and managing Kubernetes client configurations.
"""

import contextlib
import functools
import json
import logging
import os
import platform
import re
import shutil
import stat
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, TypeVar, Union

import oras.client
from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import (
    ClientRequestError,
    CLIInternalError,
    FileOperationError,
    ManualInterrupt,
    RequiredArgumentMissingError,
    ValidationError,
)
from knack.commands import CLICommand
from knack.log import get_logger
from kubernetes import client as kube_client
from kubernetes import config
from kubernetes.client import CoreV1Api, V1Container, V1Pod
from kubernetes.client.rest import ApiException

from . import consts

logger = get_logger(__name__)

# Type variable for generic retry decorator
T = TypeVar("T")


# =============================================================================
# Constants
# =============================================================================

# Retry configuration constants
RETRY_DEFAULT_MAX_RETRIES: int = 3
RETRY_DEFAULT_DELAY: float = 5.0
RETRY_DEFAULT_BACKOFF_MULTIPLIER: float = 2.0
RETRY_MAX_DELAY: float = 60.0

# Diagnostic configuration constants
DIAGNOSTIC_EXCLUDED_CONTAINERS: frozenset = frozenset({
    "mdm", "mdsd", "msi-adapter", "otel-collector"
})
DIAGNOSTIC_METADATA_FILENAME: str = "metadata.json"
DIAGNOSTIC_LOGS_SUFFIX: str = "_logs.txt"
DIAGNOSTIC_CONFIGURATION_FOLDER: str = "configuration"
DIAGNOSTIC_PODS_FOLDER: str = "pods"
DIAGNOSTIC_CONTAINERS_FOLDER: str = "containers"
DIAGNOSTIC_FOLDER_NAME_PATTERN: re.Pattern = re.compile(r'[^a-zA-Z0-9_-]')


class OSType(Enum):
    """Supported operating system types."""
    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass(frozen=True)
class DiagnosticResult:
    """Result of a diagnostic operation.

    Attributes:
        success: Whether the operation completed successfully.
        path: The path where diagnostic data was saved, if applicable.
        message: Optional message providing additional context.
    """
    success: bool
    path: str = ""
    message: str = ""


@dataclass(frozen=True)
class PodMetadata:
    """Metadata extracted from a Kubernetes pod.

    Attributes:
        name: The pod name.
        namespace: The namespace containing the pod.
        labels: Pod labels as a dictionary.
        annotations: Pod annotations as a dictionary.
        status: Current pod phase/status.
    """
    name: str
    namespace: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    status: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "namespace": self.namespace,
            "labels": self.labels or {},
            "annotations": self.annotations or {},
            "status": self.status,
        }


@dataclass
class CollectionContext:
    """Context for diagnostic collection operations.

    Attributes:
        api_instance: Kubernetes CoreV1Api client.
        base_path: Base directory for storing diagnostics.
        namespace: Target namespace for collection.
    """
    api_instance: CoreV1Api
    base_path: str
    namespace: str


# =============================================================================
# Custom Exceptions
# =============================================================================

class K8sUtilsError(Exception):
    """Base exception for k8s_utils module."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details


class KubeConfigError(K8sUtilsError):
    """Exception raised for kubeconfig-related errors."""


class KubeConnectionError(K8sUtilsError):
    """Exception raised when unable to connect to Kubernetes cluster."""


class DiagnosticCollectionError(K8sUtilsError):
    """Exception raised during diagnostic collection operations."""


class ClientInstallationError(K8sUtilsError):
    """Exception raised when client installation fails."""


# =============================================================================
# Decorators
# =============================================================================

def retry_with_backoff(
    max_retries: int = RETRY_DEFAULT_MAX_RETRIES,
    initial_delay: float = RETRY_DEFAULT_DELAY,
    backoff_multiplier: float = RETRY_DEFAULT_BACKOFF_MULTIPLIER,
    max_delay: float = RETRY_MAX_DELAY,
    exceptions: Tuple[type, ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay between retries in seconds.
        backoff_multiplier: Multiplier for exponential backoff.
        max_delay: Maximum delay between retries.
        exceptions: Tuple of exception types to catch and retry.
        on_retry: Optional callback invoked on each retry with (exception, attempt).

    Returns:
        Decorated function with retry logic.

    Example:
        @retry_with_backoff(max_retries=3, exceptions=(ApiException,))
        def fetch_pods():
            return api.list_namespaced_pod(namespace)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break

                    if on_retry:
                        on_retry(e, attempt + 1)
                    else:
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s. Retrying in %.1fs...",
                            attempt + 1, max_retries + 1, func.__name__, str(e), delay
                        )

                    time.sleep(delay)
                    delay = min(delay * backoff_multiplier, max_delay)

            # Re-raise the last exception after all retries exhausted
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected error in retry logic for {func.__name__}")

        return wrapper
    return decorator


def log_step(step_description: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to log the start of a step with timestamp.

    Args:
        step_description: Description of the step being executed.

    Returns:
        Decorated function that logs step execution.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            print(step_description)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# Context Managers
# =============================================================================

@contextlib.contextmanager
def temporary_logging_level(
    logger_instance: logging.Logger,
    level: int
) -> Iterator[None]:
    """Temporarily set a logger's level and restore it afterward.

    Args:
        logger_instance: The logger to modify.
        level: The temporary logging level to set.

    Yields:
        None
    """
    original_level = logger_instance.level
    try:
        logger_instance.setLevel(level)
        yield
    finally:
        logger_instance.setLevel(original_level)


@contextlib.contextmanager
def suppress_logging() -> Iterator[None]:
    """Temporarily suppress all logging output.

    Yields:
        None
    """
    try:
        logging.disable(logging.CRITICAL)
        yield
    finally:
        logging.disable(logging.NOTSET)


# =============================================================================
# Utility Functions
# =============================================================================

def get_utctimestring() -> str:
    """Get the current UTC time as a formatted string.

    Returns:
        UTC timestamp in ISO 8601 format (YYYY-MM-DDTHH-MM-SSZ).
    """
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())


def get_local_timestamp() -> str:
    """Get the current local time as a formatted string.

    Returns:
        Local timestamp in format YYYY-MM-DD-HH.MM.SS.
    """
    return time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())


def sanitize_folder_name(name: str) -> str:
    """Sanitize a string for use as a folder name.

    Removes any characters that are not alphanumeric, underscore, or hyphen.

    Args:
        name: The input string to sanitize.

    Returns:
        Sanitized string safe for use as a folder name.

    Example:
        >>> sanitize_folder_name("my-pod@namespace#1")
        'my-podnamespace1'
    """
    return DIAGNOSTIC_FOLDER_NAME_PATTERN.sub('', name)


def create_unique_folder_name(base_name: str) -> str:
    """Create a unique folder name using the base name and current timestamp.

    Args:
        base_name: The base name for the folder (will be sanitized).

    Returns:
        A string in the format: sanitized_base_name-YYYY-MM-DD-HH.MM.SS

    Example:
        >>> create_unique_folder_name("name1@#$")
        'name1-2025-08-05-15.59.26'
    """
    sanitized_base_name = sanitize_folder_name(base_name)
    timestamp = get_local_timestamp()
    return f"{sanitized_base_name}-{timestamp}"


def parse_namespace_list(namespace_list: str) -> List[str]:
    """Parse a comma-separated namespace list into individual namespaces.

    Args:
        namespace_list: Comma-separated string of namespace names.

    Returns:
        List of trimmed, non-empty namespace names.

    Raises:
        RequiredArgumentMissingError: If no valid namespaces are provided.
    """
    namespaces = [ns.strip() for ns in namespace_list.split(',') if ns.strip()]

    if not namespaces:
        raise RequiredArgumentMissingError(
            "No valid namespaces provided. Please provide at least one namespace."
        )

    return namespaces


def get_operating_system() -> OSType:
    """Get the current operating system type.

    Returns:
        OSType enum value for the current system.

    Raises:
        ClientRequestError: If the operating system is not supported.
    """
    os_name = platform.system().lower()

    try:
        return OSType(os_name)
    except ValueError:
        raise ClientRequestError(
            f"The {os_name} platform is not currently supported."
        )


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: The directory path to ensure exists.

    Returns:
        The Path object for the directory.

    Raises:
        FileOperationError: If the directory cannot be created.
    """
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise FileOperationError(f"Failed to create directory {path}: {e}")


# =============================================================================
# JSON Utilities
# =============================================================================

def save_as_json(destination: Union[str, Path], data: Any) -> DiagnosticResult:
    """Save data to a JSON file with proper error handling.

    Args:
        destination: Path to the output file.
        data: Data to serialize as JSON.

    Returns:
        DiagnosticResult indicating success or failure.
    """
    try:
        with open(destination, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return DiagnosticResult(success=True, path=str(destination))
    except (OSError, TypeError, ValueError) as e:
        error_msg = f"Failed to save data to {destination}: {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)


# =============================================================================
# Kubernetes Configuration
# =============================================================================

@log_step("Setting KubeConfig")
def set_kube_config(kube_config: Optional[str]) -> Optional[str]:
    """Set and normalize the kubeconfig path.

    Handles trimming of quotes that may be present on Windows systems.

    Args:
        kube_config: Path to the kubeconfig file, or None for default.

    Returns:
        Normalized kubeconfig path, or None if not specified.
    """
    if not kube_config:
        return None

    # Trim surrounding quotes (required for Windows compatibility)
    return kube_config.strip("'\"")


def load_kube_config(
    kube_config: Optional[str],
    kube_context: Optional[str],
    skip_ssl_verification: bool
) -> None:
    """Load Kubernetes configuration from file.

    Args:
        kube_config: Path to the kubeconfig file.
        kube_context: Kubernetes context to use.
        skip_ssl_verification: Whether to skip SSL certificate verification.

    Raises:
        FileOperationError: If the kubeconfig cannot be loaded.
    """
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)

        if skip_ssl_verification:
            _configure_ssl_verification(verify=False)

    except config.config_exception.ConfigException as e:
        logger.warning(consts.KUBECONFIG_LOAD_FAILED_WARNING)
        raise FileOperationError(
            f"Problem loading the kubeconfig file: {e}"
        )


def _configure_ssl_verification(verify: bool) -> None:
    """Configure SSL verification for Kubernetes client.

    Args:
        verify: Whether to verify SSL certificates.
    """
    from kubernetes.client import Configuration

    default_config = Configuration.get_default_copy()
    default_config.verify_ssl = verify
    Configuration.set_default(default_config)


@log_step("Checking Connectivity to Cluster")
def check_kube_connection() -> str:
    """Verify connectivity to the Kubernetes cluster.

    Returns:
        The Kubernetes server git version.

    Raises:
        CLIInternalError: If connectivity cannot be verified.
    """
    api_instance = kube_client.VersionApi()

    try:
        api_response = api_instance.get_code()
        return api_response.git_version
    except ApiException as e:
        logger.warning(consts.KUBEAPI_CONNECTIVITY_FAILED_WARNING)
        kubernetes_exception_handler(
            e,
            summary="Unable to verify connectivity to the Kubernetes cluster",
        )

    raise CLIInternalError(
        "Unable to verify connectivity to the Kubernetes cluster. "
        "No version information could be retrieved."
    )


def check_namespace_exists(api_instance: CoreV1Api, namespace: str) -> bool:
    """Check if a namespace exists in the cluster.

    Args:
        api_instance: Kubernetes CoreV1Api client.
        namespace: Name of the namespace to check.

    Returns:
        True if the namespace exists, False otherwise.

    Raises:
        ApiException: For errors other than 404 Not Found.
    """
    try:
        api_instance.read_namespace(name=namespace)
        return True
    except ApiException as e:
        if e.status == 404:
            return False
        raise


# =============================================================================
# Kubernetes Exception Handling
# =============================================================================

def kubernetes_exception_handler(
    ex: Exception,
    summary: str,
    error_message: str = "Error occurred while connecting to the kubernetes cluster: ",
    message_for_unauthorized_request: str = (
        "The user does not have required privileges on the kubernetes cluster "
        "to deploy Azure Arc enabled Kubernetes agents. Please ensure you have "
        "cluster admin privileges on the cluster to onboard."
    ),
    message_for_not_found: str = "The requested kubernetes resource was not found.",
    raise_error: bool = True,
) -> None:
    """Handle Kubernetes API exceptions with appropriate logging and error messages.

    Args:
        ex: The exception that was raised.
        summary: Summary description of the error.
        error_message: Base error message prefix.
        message_for_unauthorized_request: Message for 403 errors.
        message_for_not_found: Message for 404 errors.
        raise_error: Whether to raise a ValidationError.

    Raises:
        ValidationError: If raise_error is True.
    """
    # Log summary at debug level for context
    logger.debug("Kubernetes exception summary: %s", summary)

    if isinstance(ex, ApiException):
        status_code = ex.status

        if status_code == 403:
            logger.error(message_for_unauthorized_request)
        elif status_code == 404:
            logger.error(message_for_not_found)
        else:
            logger.debug("Kubernetes Exception: ", exc_info=True)

        if raise_error:
            raise ValidationError(f"{error_message}\nError Response: {ex.body}")
    else:
        if raise_error:
            raise ValidationError(f"{error_message}\nError: {ex}")
        logger.debug("Kubernetes Exception", exc_info=True)


# =============================================================================
# Client Installation
# =============================================================================

def get_mcr_path(active_directory_endpoint: str) -> str:
    """Determine the MCR (Microsoft Container Registry) path based on the cloud endpoint.

    Args:
        active_directory_endpoint: The Active Directory endpoint URL.

    Returns:
        The appropriate MCR URL for the current cloud environment.
    """
    # For US Government and China clouds, use public MCR
    if active_directory_endpoint.endswith((".us", ".cn")):
        return "mcr.microsoft.com"

    active_directory_array = active_directory_endpoint.split(".")

    # Default MCR postfix
    mcr_postfix = "com"

    # Special cases for USSec (exclude part of suffix)
    if len(active_directory_array) == 4 and active_directory_array[2] == "microsoft":
        mcr_postfix = active_directory_array[3]
    # Special case for USNat
    elif len(active_directory_array) == 5:
        mcr_postfix = ".".join(active_directory_array[2:5])

    return f"mcr.microsoft.{mcr_postfix}"


def _get_helm_paths(operating_system: OSType) -> Tuple[str, str, str, str]:
    """Get platform-specific paths for Helm installation.

    Args:
        operating_system: The target operating system.

    Returns:
        Tuple of (download_location_string, download_file_name,
                  install_location_string, artifact_tag).
    """
    os_name = operating_system.value

    if operating_system == OSType.WINDOWS:
        separator = "\\"
        file_extension = ".zip"
        binary_name = "helm.exe"
    else:
        separator = "/"
        file_extension = ".tar.gz"
        binary_name = "helm"

    machine_type = platform.machine().lower()
    if machine_type in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        arch = "amd64"
    download_location = f".azure{separator}helm{separator}{consts.HELM_VERSION}"
    download_file = f"helm-{consts.HELM_VERSION}-{os_name}-{arch}{file_extension}"
    install_location = f"{download_location}{separator}{os_name}-{arch}{separator}{binary_name}"
    artifact_tag = f"helm-{consts.HELM_VERSION}-{os_name}-{arch}"

    return download_location, download_file, install_location, artifact_tag


@log_step("Install Helm client if it does not exist")
def install_helm_client(cmd: CLICommand) -> str:
    """Install the Helm client if not already present.

    Args:
        cmd: The CLI command context.

    Returns:
        Path to the Helm executable.

    Raises:
        ClientRequestError: If installation fails.
    """
    # Check for user-specified path first
    helm_client_path = os.getenv("HELM_CLIENT_PATH")
    if helm_client_path:
        return helm_client_path

    # Get system information
    operating_system = get_operating_system()
    machine_type = platform.machine()
    print(f"Detected system information: OS - {operating_system.value}, Architecture - {machine_type}")

    # Get platform-specific paths
    download_location_string, download_file_name, install_location_string, artifact_tag = \
        _get_helm_paths(operating_system)

    home_dir = Path.home()
    download_location = home_dir / download_location_string
    install_location = home_dir / install_location_string

    # Return existing installation if present
    if install_location.is_file():
        return str(install_location)

    # Create download directory
    ensure_directory_exists(download_location)

    # Download Helm client
    logger.warning("Downloading helm client for first time. This can take few minutes...")
    mcr_url = get_mcr_path(cmd.cli_ctx.cloud.endpoints.active_directory)

    _download_helm_from_mcr(mcr_url, artifact_tag, download_location)

    # Extract and configure the archive
    _extract_helm_archive(download_location, download_file_name, install_location)

    return str(install_location)


def _download_helm_retry_callback(exception: Exception, attempt: int) -> None:
    """Callback for helm download retry logging."""
    if "Connection reset by peer" in str(exception):
        logger.warning(
            "Connection reset by peer error encountered while downloading helm client. "
            "This is likely a transient network issue. Retrying..."
        )
    else:
        logger.warning("Download attempt %d failed: %s. Retrying...", attempt, exception)


@retry_with_backoff(
    max_retries=RETRY_DEFAULT_MAX_RETRIES,
    initial_delay=RETRY_DEFAULT_DELAY,
    exceptions=(OSError,),
    on_retry=_download_helm_retry_callback,
)
def _download_helm_from_mcr(mcr_url: str, artifact_tag: str, download_location: Path) -> None:
    """Download Helm from Microsoft Container Registry with retry logic.

    Args:
        mcr_url: The MCR URL to download from.
        artifact_tag: The artifact tag to pull.
        download_location: Directory to save the download.

    Raises:
        CLIInternalError: If download fails after all retries.
    """
    try:
        client = oras.client.OrasClient(hostname=mcr_url)
        client.pull(
            target=f"{mcr_url}/{consts.HELM_MCR_URL}:{artifact_tag}",
            outdir=str(download_location),
        )
    except (OSError) as e:
        raise CLIInternalError(
            f"Failed to download helm client: {e}",
            recommendation="Please check your internet connection.",
        )


def _extract_helm_archive(
    download_location: Path,
    download_file_name: str,
    install_location: Path
) -> None:
    """Extract the Helm archive and set executable permissions.

    Args:
        download_location: Directory containing the archive.
        download_file_name: Name of the archive file.
        install_location: Path where the binary should be installed.

    Raises:
        ClientRequestError: If extraction fails.
    """
    archive_path = download_location / download_file_name

    try:
        shutil.unpack_archive(str(archive_path), str(download_location))
        os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)
    except (shutil.ReadError, OSError) as e:
        recommendation = (
            f"Please ensure that you delete the directory '{download_location}' "
            "before trying again."
        )
        raise ClientRequestError(
            f"Failed to extract helm executable: {e}",
            recommendation=recommendation
        )


@log_step("Install Kubectl client if it does not exist")
def install_kubectl_client() -> str:
    """Install the kubectl client if not already present.

    Returns:
        Path to the kubectl executable.

    Raises:
        CLIInternalError: If installation fails.
    """
    # Check for user-specified path first
    kubectl_client_path = os.getenv("KUBECTL_CLIENT_PATH")
    if kubectl_client_path:
        return kubectl_client_path

    try:
        home_dir = Path.home()
        kubectl_dir = home_dir / ".azure" / "kubectl-client"

        ensure_directory_exists(kubectl_dir)

        # Determine binary name based on OS
        operating_system = get_operating_system()
        kubectl_binary = "kubectl.exe" if operating_system == OSType.WINDOWS else "kubectl"
        kubectl_path = kubectl_dir / kubectl_binary

        # Return existing installation if present
        if kubectl_path.is_file():
            return str(kubectl_path)

        # Download kubectl using Azure CLI
        logger.warning("Downloading kubectl client for first time. This can take few minutes...")

        with suppress_logging():
            get_default_cli().invoke(
                ["aks", "install-cli", "--install-location", str(kubectl_path)]
            )

        logger.warning("")  # Add newline after download
        return str(kubectl_path)

    except (OSError, FileNotFoundError) as e:
        raise CLIInternalError(f"Unable to install kubectl. Error: {e}")


# =============================================================================
# Diagnostic Folder Management
# =============================================================================

@log_step("Creating folder for extension Diagnostic Checks Logs")
def create_folder_diagnosticlogs(
    folder_name: str,
    base_folder_name: str
) -> DiagnosticResult:
    """Create the diagnostic logs folder structure.

    Args:
        folder_name: Name of the folder to create (usually includes timestamp).
        base_folder_name: Base folder name under .azure directory.

    Returns:
        DiagnosticResult with the path and success status.
    """
    try:
        home_dir = Path.home()
        base_path = home_dir / ".azure" / base_folder_name

        # Create base directory if it doesn't exist
        base_path.mkdir(parents=True, exist_ok=True)

        # Create timestamped folder
        full_path = base_path / folder_name

        # Remove existing folder to prevent overwriting
        if full_path.exists():
            shutil.rmtree(full_path, ignore_errors=True)

        full_path.mkdir()

        return DiagnosticResult(success=True, path=str(full_path))

    except PermissionError as e:
        logger.exception(
            "An exception occurred while creating the diagnostic logs folder: %s", e
        )
        return DiagnosticResult(success=False, message=str(e))
    except OSError as e:
        if "[Errno 28]" in str(e):  # No space left on device
            return DiagnosticResult(
                success=False,
                message="Insufficient storage space available."
            )
        logger.exception(
            "An exception occurred while creating the diagnostic logs folder: %s", e
        )
        return DiagnosticResult(success=False, message=str(e))


def create_folder_diagnostics_namespace(
    base_folder: str,
    namespace: str
) -> DiagnosticResult:
    """Create a folder for namespace-specific diagnostics.

    Args:
        base_folder: Base folder for all diagnostics.
        namespace: Namespace name.

    Returns:
        DiagnosticResult with the folder path and success status.
    """
    print(f"Creating folder for namespace '{namespace}'")

    namespace_folder = Path(base_folder) / namespace

    try:
        namespace_folder.mkdir(parents=True, exist_ok=True)
        return DiagnosticResult(success=True, path=str(namespace_folder))
    except OSError as e:
        error_msg = f"Failed to create diagnostics folder for namespace '{namespace}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)


# =============================================================================
# Pod Metadata Collection
# =============================================================================

def extract_pod_metadata(pod: V1Pod) -> Optional[PodMetadata]:
    """Extract metadata from a Kubernetes pod object.

    Args:
        pod: The Kubernetes pod object.

    Returns:
        PodMetadata dataclass if successful, None if metadata is missing.
    """
    if pod.metadata is None or pod.status is None:
        return None

    return PodMetadata(
        name=pod.metadata.name or "",
        namespace=pod.metadata.namespace or "",
        labels=pod.metadata.labels or {},
        annotations=pod.metadata.annotations or {},
        status=pod.status.phase or "",
    )


def save_pod_metadata(pod_folder: Union[str, Path], pod_metadata: PodMetadata) -> DiagnosticResult:
    """Save pod metadata to a JSON file.

    Args:
        pod_folder: Folder to save the metadata file.
        pod_metadata: The pod metadata to save.

    Returns:
        DiagnosticResult indicating success or failure.
    """
    metadata_file = Path(pod_folder) / DIAGNOSTIC_METADATA_FILENAME
    return save_as_json(metadata_file, pod_metadata.to_dict())


# =============================================================================
# Diagnostic Collection Functions
# =============================================================================

def collect_container_logs(
    api_instance: CoreV1Api,
    containers_folder: Union[str, Path],
    namespace: str,
    pod_name: str,
    container: V1Container
) -> DiagnosticResult:
    """Collect logs from a specific container.

    Args:
        api_instance: Kubernetes CoreV1Api client.
        containers_folder: Folder to save container logs.
        namespace: Pod namespace.
        pod_name: Name of the pod.
        container: Container specification.

    Returns:
        DiagnosticResult indicating success or failure.
    """
    container_name = container.name
    print(f"Collecting logs from container '{container_name}' in pod '{pod_name}'")

    try:
        container_log = api_instance.read_namespaced_pod_log(
            name=pod_name,
            container=container_name,
            namespace=namespace
        )
    except ApiException as e:
        error_msg = f"Failed to read logs for container '{container_name}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)

    log_file = Path(containers_folder) / f"{container_name}{DIAGNOSTIC_LOGS_SUFFIX}"

    try:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(str(container_log))
        return DiagnosticResult(success=True, path=str(log_file))
    except OSError as e:
        error_msg = f"Failed to save logs for container '{container_name}' in pod '{pod_name}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)


def collect_pod_information(
    pods_folder: Union[str, Path],
    namespace: str,
    pod: V1Pod
) -> DiagnosticResult:
    """Collect information from a pod and save to disk.

    Args:
        pods_folder: Base folder for pod diagnostics.
        namespace: Pod namespace.
        pod: The pod object.

    Returns:
        DiagnosticResult indicating success or failure.
    """
    pod_metadata = extract_pod_metadata(pod)

    if pod_metadata is None:
        error_msg = f"Failed to collect metadata for pod in namespace '{namespace}'"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)

    pod_name = pod_metadata.name
    print(f"Collecting information for pod '{pod_name}' in namespace '{namespace}'")

    pod_folder = Path(pods_folder) / pod_name

    try:
        pod_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        error_msg = f"Failed to create folder for pod '{pod_name}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)

    return save_pod_metadata(pod_folder, pod_metadata)


def _should_skip_container(container: V1Container) -> bool:
    """Check if a container should be skipped during log collection.

    Args:
        container: The container to check.

    Returns:
        True if the container should be skipped.
    """
    return container.name in DIAGNOSTIC_EXCLUDED_CONTAINERS


def _collect_containers_logs(
    api_instance: CoreV1Api,
    containers_folder: Path,
    namespace: str,
    pod_name: str,
    containers: Optional[List[V1Container]],
    container_type: str = "container"
) -> DiagnosticResult:
    """Collect logs from a list of containers.

    Args:
        api_instance: Kubernetes CoreV1Api client.
        containers_folder: Folder to save container logs.
        namespace: Pod namespace.
        pod_name: Pod name.
        containers: List of containers to collect logs from.
        container_type: Type of containers (for logging purposes).

    Returns:
        DiagnosticResult indicating overall success.
    """
    if not containers:
        return DiagnosticResult(success=True)

    for container in containers:
        if _should_skip_container(container):
            continue

        result = collect_container_logs(
            api_instance, containers_folder, namespace, pod_name, container
        )

        if not result.success:
            logger.error(
                "Failed to collect logs from %s '%s' in pod '%s': %s",
                container_type, container.name, pod_name, result.message
            )
            # Continue collecting other containers even if one fails

    return DiagnosticResult(success=True)


def walk_through_pods(
    api_instance: CoreV1Api,
    folder_namespace: Union[str, Path],
    namespace: str
) -> DiagnosticResult:
    """Walk through all pods in a namespace and collect diagnostics.

    Args:
        api_instance: Kubernetes CoreV1Api client.
        folder_namespace: Folder for namespace diagnostics.
        namespace: Target namespace.

    Returns:
        DiagnosticResult indicating overall success.
    """
    print(f"Collecting information from pods in namespace '{namespace}'")

    try:
        pods = api_instance.list_namespaced_pod(namespace)
    except ApiException as e:
        error_msg = f"Failed to list pods in namespace '{namespace}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)

    pods_folder = Path(folder_namespace) / DIAGNOSTIC_PODS_FOLDER

    try:
        pods_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        error_msg = f"Failed to create pods folder for namespace '{namespace}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)

    all_success = True

    for pod in pods.items:
        pod_name = pod.metadata.name if pod.metadata else "unknown"

        # Collect pod information
        pod_result = collect_pod_information(pods_folder, namespace, pod)
        if not pod_result.success:
            logger.error("Failed to collect information for pod '%s'", pod_name)
            all_success = False
            continue

        # Create containers folder
        containers_folder = pods_folder / pod_name / DIAGNOSTIC_CONTAINERS_FOLDER
        try:
            containers_folder.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error("Failed to create containers folder for pod '%s': %s", pod_name, e)
            all_success = False
            continue

        # Collect init container logs
        if pod.spec and pod.spec.init_containers:
            _collect_containers_logs(
                api_instance, containers_folder, namespace, pod_name,
                pod.spec.init_containers, "init container"
            )

        # Collect container logs
        if pod.spec and pod.spec.containers:
            result = _collect_containers_logs(
                api_instance, containers_folder, namespace, pod_name,
                pod.spec.containers, "container"
            )
            if not result.success:
                all_success = False

    return DiagnosticResult(success=all_success)


def collect_namespace_configmaps(
    api_instance: CoreV1Api,
    namespace_folder: Union[str, Path],
    namespace: str
) -> DiagnosticResult:
    """Collect all ConfigMaps from a namespace.

    Args:
        api_instance: Kubernetes CoreV1Api client.
        namespace_folder: Folder for namespace diagnostics.
        namespace: Target namespace.

    Returns:
        DiagnosticResult indicating overall success.
    """
    print(f"Collecting configurations for namespace '{namespace}'")

    config_folder = Path(namespace_folder) / DIAGNOSTIC_CONFIGURATION_FOLDER

    try:
        config_folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        error_msg = f"Failed to create configuration folder for namespace '{namespace}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)

    try:
        config_maps = api_instance.list_namespaced_config_map(namespace)
    except ApiException as e:
        error_msg = f"Failed to list ConfigMaps in namespace '{namespace}': {e}"
        logger.error(error_msg)
        return DiagnosticResult(success=False, message=error_msg)

    for cm in config_maps.items:
        cm_name = cm.metadata.name if cm.metadata else "unknown"
        cm_data = cm.data or {}
        cm_file = config_folder / f"{cm_name}.json"

        result = save_as_json(cm_file, cm_data)
        if not result.success:
            logger.error("Failed to save ConfigMap '%s': %s", cm_name, result.message)
            return DiagnosticResult(success=False, message=result.message)

    return DiagnosticResult(success=True, path=str(config_folder))


def collect_namespace(
    api_instance: CoreV1Api,
    base_path: str,
    namespace: str
) -> DiagnosticResult:
    """Collect all diagnostics for a single namespace.

    Args:
        api_instance: Kubernetes CoreV1Api client.
        base_path: Base path for diagnostics.
        namespace: Target namespace.

    Returns:
        DiagnosticResult indicating overall success.
    """
    print(f"Collecting diagnostics information for namespace '{namespace}'...")

    # Check if namespace exists
    if not check_namespace_exists(api_instance, namespace):
        logger.warning("Namespace '%s' does not exist. Skipping...", namespace)
        return DiagnosticResult(success=True, message=f"Namespace '{namespace}' does not exist")

    # Create namespace folder
    folder_result = create_folder_diagnostics_namespace(base_path, namespace)
    if not folder_result.success:
        logger.error("Failed to create diagnostics folder for namespace '%s'.", namespace)
        return folder_result

    namespace_folder = folder_result.path
    all_success = True

    # Collect ConfigMaps
    configmaps_result = collect_namespace_configmaps(api_instance, namespace_folder, namespace)
    if not configmaps_result.success:
        all_success = False

    # Collect pod information and logs
    pods_result = walk_through_pods(api_instance, namespace_folder, namespace)
    if not pods_result.success:
        all_success = False

    return DiagnosticResult(
        success=all_success,
        path=namespace_folder,
        message="" if all_success else "Some diagnostic collections failed"
    )


# =============================================================================
# Main Entry Point
# =============================================================================

def troubleshoot_k8s_extension(
    cmd: CLICommand,
    name: str,
    namespace_list: str,
    kube_config: Optional[str] = None,
    kube_context: Optional[str] = None,
    skip_ssl_verification: bool = False,
) -> None:
    """Troubleshoot an existing Kubernetes Extension by collecting diagnostics.

    This function orchestrates the collection of diagnostic information from
    specified Kubernetes namespaces, including pod logs, ConfigMaps, and
    metadata.

    Args:
        cmd: The CLI command context.
        name: Name of the extension being troubleshot.
        namespace_list: Comma-separated list of namespaces to collect from.
        kube_config: Optional path to kubeconfig file.
        kube_context: Optional Kubernetes context to use.
        skip_ssl_verification: Whether to skip SSL verification.

    Raises:
        ManualInterrupt: If the user interrupts the operation.
        RequiredArgumentMissingError: If no valid namespaces are provided.
        FileOperationError: If kubeconfig cannot be loaded.
    """
    try:
        print(
            "Collecting diagnostics information from the namespaces provided. "
            "This operation may take a while to complete ..."
        )

        # Parse and validate namespaces
        namespaces = parse_namespace_list(namespace_list)

        # Configure Kubernetes client
        kube_config = set_kube_config(kube_config)

        # Suppress verbose Kubernetes client logging
        with temporary_logging_level(kube_client.rest.logger, logging.WARNING):
            load_kube_config(kube_config, kube_context, skip_ssl_verification)

        # Install required clients
        install_helm_client(cmd)
        install_kubectl_client()

        # Verify cluster connectivity
        check_kube_connection()

        # Create diagnostic logs folder
        diagnostic_folder_name = create_unique_folder_name(name)
        folder_result = create_folder_diagnosticlogs(
            diagnostic_folder_name, consts.ARC_EXT_DIAGNOSTIC_LOGS
        )

        if not folder_result.success:
            logger.warning(
                "The diagnoser was unable to save logs to your machine. "
                "Please check whether sufficient storage is available and "
                "run the troubleshoot command again."
            )
            return

        filepath_with_timestamp = folder_result.path

        # Collect diagnostics from each namespace
        api_instance = kube_client.CoreV1Api()
        all_collections_successful = True

        for namespace in namespaces:
            result = collect_namespace(api_instance, filepath_with_timestamp, namespace)
            if not result.success:
                all_collections_successful = False

        # Report results
        if all_collections_successful:
            print(
                f"\nThe diagnoser logs have been saved at this path: '{filepath_with_timestamp}'.\n"
                "These logs can be attached while filing a support ticket for further assistance.\n"
            )
        else:
            logger.warning(
                "The diagnoser was unable to save some logs to your machine. "
                "Please check whether sufficient storage is available and "
                "run the troubleshoot command again."
            )

    except KeyboardInterrupt:
        raise ManualInterrupt("Process terminated externally.")


# =============================================================================
# Legacy Compatibility (Deprecated)
# =============================================================================

def convert_to_pod_dict(pod: V1Pod) -> Optional[Dict[str, Any]]:
    """Convert a pod to a dictionary representation.

    .. deprecated::
        Use :func:`extract_pod_metadata` instead, which returns a proper
        dataclass with type safety.

    Args:
        pod: The Kubernetes pod object.

    Returns:
        Dictionary with pod metadata, or None if metadata is missing.
    """
    metadata = extract_pod_metadata(pod)
    return metadata.to_dict() if metadata else None
