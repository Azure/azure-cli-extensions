# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Utility functions for the workload-orchestration support bundle feature."""

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone

from knack.log import get_logger

from azext_workload_orchestration._support_consts import (
    BUNDLE_PREFIX,
    FOLDER_LOGS,
    FOLDER_RESOURCES,
    FOLDER_CHECKS,
    FOLDER_CLUSTER_INFO,
    STATUS_PASS,
    STATUS_FAIL,
    STATUS_WARN,
    STATUS_SKIP,
    STATUS_ERROR,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Kubernetes client initialization
# ---------------------------------------------------------------------------

def get_kubernetes_client(kube_config=None, kube_context=None):
    """Initialize and return kubernetes API clients.

    Returns a dict with 'core_v1', 'apps_v1', 'custom_objects', 'storage_v1',
    'admissionregistration_v1', 'apis', 'version' clients, plus 'context_info'
    with the active context name, cluster, and kubeconfig path.
    """
    try:
        from kubernetes import client, config
        from kubernetes.config import list_kube_config_contexts
    except ImportError:
        raise CLIError(
            "The 'kubernetes' package is required. "
            "Install it with: pip install kubernetes>=24.2.0"
        )

    config_file = kube_config or os.path.expanduser("~/.kube/config")

    # Read context info before loading
    context_info = {"context": "unknown", "cluster": "unknown", "kubeconfig": config_file}
    try:
        contexts, active = list_kube_config_contexts(config_file=kube_config)
        if active:
            context_info["context"] = active.get("name", "unknown")
            context_info["cluster"] = active.get("context", {}).get("cluster", "unknown")
            context_info["user"] = active.get("context", {}).get("user", "unknown")
        if kube_context:
            context_info["context"] = kube_context
    except Exception:
        pass

    try:
        config.load_kube_config(
            config_file=kube_config,
            context=kube_context,
        )
    except config.ConfigException as ex:
        raise CLIError(
            f"Failed to load kubeconfig: {ex}. "
            "Make sure you have a valid kubeconfig file at "
            f"'{config_file}'. Run 'az aks get-credentials' or "
            "'export KUBECONFIG=/path/to/config'."
        )
    except Exception as ex:
        raise CLIError(
            f"Failed to load kubeconfig: {ex}. "
            "Make sure you have a valid kubeconfig and cluster context. "
            "Run 'az aks get-credentials' or set KUBECONFIG."
        )

    return {
        "core_v1": client.CoreV1Api(),
        "apps_v1": client.AppsV1Api(),
        "custom_objects": client.CustomObjectsApi(),
        "storage_v1": client.StorageV1Api(),
        "admissionregistration_v1": client.AdmissionregistrationV1Api(),
        "apis": client.ApisApi(),
        "version": client.VersionApi(),
        "context_info": context_info,
    }


# ---------------------------------------------------------------------------
# Bundle directory management
# ---------------------------------------------------------------------------

def create_bundle_directory(output_dir=None):
    """Create the bundle directory structure and return its path.

    Returns (bundle_dir, bundle_name) tuple.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    bundle_name = f"{BUNDLE_PREFIX}-{timestamp}"

    if output_dir:
        base = os.path.abspath(output_dir)
        os.makedirs(base, exist_ok=True)
    else:
        base = os.getcwd()

    bundle_dir = os.path.join(base, bundle_name)
    os.makedirs(bundle_dir, exist_ok=True)

    # Create sub-folders
    for folder in (FOLDER_LOGS, FOLDER_RESOURCES, FOLDER_CHECKS, FOLDER_CLUSTER_INFO):
        os.makedirs(os.path.join(bundle_dir, folder), exist_ok=True)

    # Create per-namespace log directories
    # (populated later when we know which namespaces to collect)
    return bundle_dir, bundle_name


def create_namespace_log_dir(bundle_dir, namespace):
    """Create a log subdirectory for a namespace."""
    ns_dir = os.path.join(bundle_dir, FOLDER_LOGS, namespace)
    os.makedirs(ns_dir, exist_ok=True)
    return ns_dir


def create_zip_bundle(bundle_dir, bundle_name, output_dir=None):
    """Zip the bundle directory and remove the raw folder.

    Returns the path to the zip file. If zip creation fails, keeps the raw
    directory so data is not lost.
    """
    if output_dir:
        zip_base = os.path.join(os.path.abspath(output_dir), bundle_name)
    else:
        zip_base = os.path.join(os.path.dirname(bundle_dir), bundle_name)

    try:
        zip_path = shutil.make_archive(zip_base, "zip", os.path.dirname(bundle_dir), bundle_name)
    except (IOError, OSError, PermissionError) as ex:
        logger.warning("Failed to create zip: %s. Raw bundle preserved at: %s", ex, bundle_dir)
        raise CLIError(
            f"Failed to create zip bundle: {ex}. "
            f"Raw bundle data preserved at: {bundle_dir}"
        )

    # Only clean up raw directory after successful zip
    shutil.rmtree(bundle_dir, ignore_errors=True)

    return zip_path


# ---------------------------------------------------------------------------
# Safe API call wrapper
# ---------------------------------------------------------------------------

def safe_api_call(func, *args, description="API call", **kwargs):
    """Execute a kubernetes API call with error handling.

    Returns (result, error_string). On success error_string is None.
    On failure result is None and error_string describes the problem.
    """
    try:
        from kubernetes.client.exceptions import ApiException
    except ImportError:
        return None, "kubernetes package not available"

    try:
        result = func(*args, **kwargs)
        return result, None
    except ApiException as ex:
        if ex.status == 403:
            msg = (
                f"Permission denied for {description} (403 Forbidden). "
                "The service account may lack the required RBAC role. "
                "Ensure the user has at least 'view' ClusterRole binding."
            )
            logger.warning(msg)
            return None, msg
        if ex.status == 401:
            msg = (
                f"Authentication failed for {description} (401 Unauthorized). "
                "Cluster credentials may be expired. "
                "Run 'az aks get-credentials' to refresh."
            )
            logger.warning(msg)
            return None, msg
        if ex.status == 404:
            msg = f"Resource not found for {description} (404)"
            logger.debug(msg)
            return None, msg
        msg = f"{description} failed: {ex.status} {ex.reason}"
        logger.warning(msg)
        return None, msg
    except Exception as ex:
        msg = f"{description} failed: {type(ex).__name__}: {ex}"
        logger.warning(msg)
        return None, msg


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

def write_json(filepath, data):
    """Write data as formatted JSON. Returns True on success."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except (IOError, OSError, PermissionError, TypeError) as ex:
        logger.warning("Failed to write %s: %s", filepath, ex)
        return False


def write_text(filepath, text):
    """Write plain text to file. Returns True on success."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text if text else "")
        return True
    except (IOError, OSError, PermissionError) as ex:
        logger.warning("Failed to write %s: %s", filepath, ex)
        return False


def write_check_result(bundle_dir, category, check_name, status, message, details=None):
    """Write a single prerequisite check result to the checks folder.

    Returns a dict representing the check result.
    """
    result = {
        "category": category,
        "check_name": check_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details:
        result["details"] = details

    filepath = os.path.join(bundle_dir, FOLDER_CHECKS, f"{category}--{check_name}.json")
    write_json(filepath, result)
    return result


# ---------------------------------------------------------------------------
# Resource parsing helpers
# ---------------------------------------------------------------------------

def parse_cpu(cpu_str):
    """Parse Kubernetes CPU string to float cores.

    Examples: '3860m' -> 3.86, '4' -> 4.0, '500m' -> 0.5
    """
    if not cpu_str:
        return 0.0
    cpu_str = str(cpu_str).strip()
    if cpu_str.endswith("m"):
        return float(cpu_str[:-1]) / 1000.0
    return float(cpu_str)


def parse_memory_gi(mem_str):
    """Parse Kubernetes memory string to GiB.

    Examples: '27601704Ki' -> ~26.3, '4Gi' -> 4.0, '4096Mi' -> 4.0
    """
    if not mem_str:
        return 0.0
    mem_str = str(mem_str).strip()
    if mem_str.endswith("Ki"):
        return float(mem_str[:-2]) / (1024 * 1024)
    if mem_str.endswith("Mi"):
        return float(mem_str[:-2]) / 1024
    if mem_str.endswith("Gi"):
        return float(mem_str[:-2])
    if mem_str.endswith("Ti"):
        return float(mem_str[:-2]) * 1024
    # Plain bytes
    try:
        return float(mem_str) / (1024 ** 3)
    except ValueError:
        return 0.0


def format_bytes(size_bytes):
    """Format byte count to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 ** 3):.1f} GB"


def check_disk_space(path, estimated_bytes):
    """Check if there is enough disk space. Returns (ok, free_bytes)."""
    total, used, free = shutil.disk_usage(path)
    needed = estimated_bytes * 2  # raw + zip
    return free >= needed, free


# ---------------------------------------------------------------------------
# Detect cluster capabilities
# ---------------------------------------------------------------------------

def detect_cluster_capabilities(clients):
    """Detect which optional components are installed on the cluster.

    Returns a dict of capability booleans.
    """
    apis_client = clients["apis"]
    result, err = safe_api_call(apis_client.get_api_versions, description="get API groups")
    if err:
        logger.warning("Could not detect cluster capabilities: %s", err)
        return {
            "has_gatekeeper": False, "has_kyverno": False,
            "has_cert_manager": False, "has_symphony": False,
            "has_openshift": False, "has_metrics": False,
        }

    group_names = {g.name for g in (result.groups or [])}

    from azext_workload_orchestration._support_consts import (
        API_GROUP_GATEKEEPER_TEMPLATES,
        API_GROUP_KYVERNO,
        API_GROUP_CERT_MANAGER,
        API_GROUP_SYMPHONY,
        API_GROUP_OPENSHIFT_SECURITY,
        API_GROUP_METRICS,
    )

    return {
        "has_gatekeeper": API_GROUP_GATEKEEPER_TEMPLATES in group_names,
        "has_kyverno": API_GROUP_KYVERNO in group_names,
        "has_cert_manager": API_GROUP_CERT_MANAGER in group_names,
        "has_symphony": API_GROUP_SYMPHONY in group_names,
        "has_openshift": API_GROUP_OPENSHIFT_SECURITY in group_names,
        "has_metrics": API_GROUP_METRICS in group_names,
    }


# ---------------------------------------------------------------------------
# CLI error helper
# ---------------------------------------------------------------------------

try:
    from azure.cli.core.azclierror import CLIError
except ImportError:
    # Fallback for testing outside azure-cli
    class CLIError(Exception):
        pass
