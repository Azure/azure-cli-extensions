# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Target prepare command - prepares an Arc-connected K8s cluster for WO.

Installs cert-manager, trust-manager, WO extension, and creates a custom
location. Idempotent - skips components that already exist.

Usage:
    az workload-orchestration target prepare \\
        --cluster-name my-cluster -g my-rg -l eastus
"""

# pylint: disable=broad-exception-caught
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
# pylint: disable=import-outside-toplevel

import json
import os
import logging
import sys

from azure.cli.core.azclierror import (
    CLIInternalError,
    ValidationError,
)
from azure.cli.core.util import send_raw_request

from azext_workload_orchestration.onboarding.consts import (
    DEFAULT_CERT_MANAGER_VERSION,
    AIO_PLATFORM_EXTENSION_TYPE,
    AIO_PLATFORM_EXTENSION_NAME,
    AIO_PLATFORM_EXTENSION_NAMESPACE,
    AIO_PLATFORM_EXTENSION_SCOPE,
    DEFAULT_EXTENSION_TYPE,
    DEFAULT_EXTENSION_NAME,
    DEFAULT_RELEASE_TRAIN,
    DEFAULT_EXTENSION_NAMESPACE,
    DEFAULT_EXTENSION_SCOPE,
    DEFAULT_STORAGE_SIZE,
)
from azext_workload_orchestration.onboarding.utils import (
    invoke_cli_command,
    print_step,
    print_success,
    print_detail,
)

logger = logging.getLogger(__name__)


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


TOTAL_STEPS = 4


def target_prepare(
    cmd,
    cluster_name,
    resource_group,
    location,
    extension_name=None,
    custom_location_name=None,
    extension_version=None,
    release_train=None,
    cert_manager_version=None,
    kube_config=None,
    kube_context=None,
    no_wait=False,
):
    """Prepare an Arc-connected K8s cluster for Workload Orchestration.

    Installs cert-manager + trust-manager (via the AIO platform Arc
    extension), the WO extension, and creates a custom location.
    Idempotent: skips components that are already installed.
    """
    extension_name = extension_name or DEFAULT_EXTENSION_NAME
    custom_location_name = custom_location_name or f"{cluster_name}-cl"
    release_train = release_train or DEFAULT_RELEASE_TRAIN
    cert_manager_version = cert_manager_version or DEFAULT_CERT_MANAGER_VERSION

    _eprint(f"\nPreparing cluster '{cluster_name}' for Workload Orchestration...\n")

    # Track step results for diagnostic summary
    step_results = {}

    # Pre-flight: verify cluster is Arc-connected and features enabled
    try:
        connected_cluster_id = _preflight_checks(cmd, cluster_name, resource_group)
        step_results["preflight"] = "Passed"
    except Exception as exc:
        step_results["preflight"] = f"FAILED: {exc}"
        _print_diagnostic_summary(step_results, cluster_name, resource_group)
        raise

    # Step 1+2: cert-manager + trust-manager (single AIO Arc extension)
    try:
        _ensure_cert_trust_manager_via_aio_extension(
            cmd, cluster_name, resource_group,
            cert_manager_version, no_wait,
        )
        step_results["cert-manager"] = "Succeeded"
        step_results["trust-manager"] = "Succeeded (bundled)"
        print_step(
            2, TOTAL_STEPS, "trust-manager",
            "Bundled with cert-manager ✓"
        )
    except Exception as exc:
        step_results["cert-manager"] = f"FAILED: {exc}"
        logger.error(
            "Steps 1-2/4 failed (AIO cert/trust-manager): %s", exc
        )
        _print_diagnostic_summary(step_results, cluster_name, resource_group)
        raise CLIInternalError(
            f"cert-manager/trust-manager installation failed: {exc}"
        )

    # Step 3: WO extension
    try:
        extension_id = _ensure_wo_extension(
            cmd, cluster_name, resource_group, extension_name,
            extension_version, release_train, no_wait,
            kube_config, kube_context,
        )
        step_results["wo-extension"] = "Succeeded"
    except Exception as exc:
        step_results["wo-extension"] = f"FAILED: {exc}"
        logger.error("Step 3/4 failed (WO extension): %s", exc)
        _print_diagnostic_summary(step_results, cluster_name, resource_group)
        raise CLIInternalError(
            f"WO extension installation failed: {exc}"
        )

    # Step 4: Custom location
    try:
        cl_id = _ensure_custom_location(
            cmd, cluster_name, resource_group, location,
            custom_location_name, extension_id, connected_cluster_id
        )
        step_results["custom-location"] = "Succeeded"
    except Exception as exc:
        step_results["custom-location"] = f"FAILED: {exc}"
        logger.error("Step 4/4 failed (Custom location): %s", exc)
        _print_diagnostic_summary(step_results, cluster_name, resource_group)
        raise CLIInternalError(
            f"Custom location creation failed: {exc}"
        )

    # Output extended-location.json
    extended_location = {"name": cl_id, "type": "CustomLocation"}
    _write_extended_location_file(extended_location)

    print_success(f"Cluster '{cluster_name}' is ready for Workload Orchestration")
    print_detail("Custom Location ID", cl_id)
    _eprint()

    return {
        "clusterName": cluster_name,
        "customLocationId": cl_id,
        "extensionId": extension_id,
        "extendedLocation": extended_location,
        "connectedClusterId": connected_cluster_id,
    }


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def _preflight_checks(cmd, cluster_name, resource_group):
    """Verify cluster is Arc-connected and custom-locations feature enabled."""
    # Check cluster is Arc-connected
    try:
        cluster_info = invoke_cli_command(
            cmd,
            ["connectedk8s", "show", "-n", cluster_name, "-g", resource_group]
        )
    except CLIInternalError:
        raise ValidationError(
            f"Cluster '{cluster_name}' is not Arc-connected or not found "
            f"in resource group '{resource_group}'."
        )

    connected_cluster_id = cluster_info.get("id", "")
    if not connected_cluster_id:
        raise CLIInternalError(
            f"Could not get resource ID for cluster '{cluster_name}'."
        )

    # Check custom-locations feature enabled
    features = cluster_info.get("features", {})
    # Different API versions return this differently
    cl_enabled = (
        features.get("customLocationsEnabled", False)
        or cluster_info.get("properties", {}).get(
            "customLocationsEnabled", False
        )
    )
    # If we can't determine, proceed anyway - the custom location
    # create step will fail with a clear error if not enabled
    if cl_enabled is False:
        logger.warning(
            "custom-locations feature may not be enabled. "
            "If custom location creation fails, run: "
            "az connectedk8s enable-features -n %s -g %s "
            "--features cluster-connect custom-locations",
            cluster_name, resource_group
        )

    return connected_cluster_id


# ---------------------------------------------------------------------------
# Step 1+2: cert-manager + trust-manager via AIO Platform extension
# ---------------------------------------------------------------------------

def _ensure_cert_trust_manager_via_aio_extension(
    cmd, cluster_name, resource_group, version, no_wait
):
    """Install cert-manager + trust-manager as an Arc k8s-extension.

    Uses microsoft.iotoperations.platform which bundles cert-manager and
    trust-manager. Idempotent: skips if an extension of that type already
    exists on the cluster.
    """
    # Check existing extensions for a matching AIO platform extension
    try:
        extensions = invoke_cli_command(
            cmd,
            [
                "k8s-extension", "list",
                "-g", resource_group,
                "--cluster-name", cluster_name,
                "--cluster-type", "connectedClusters",
            ]
        )
    except CLIInternalError:
        extensions = []

    existing = None
    for ext in (extensions or []):
        ext_type = (ext.get("extensionType", "") or "").lower()
        if ext_type == AIO_PLATFORM_EXTENSION_TYPE.lower():
            existing = ext
            break

    if existing:
        ext_ver = existing.get("version", "unknown")
        prov_state = (existing.get("provisioningState", "") or "").lower()
        if prov_state == "succeeded":
            print_step(
                1, TOTAL_STEPS, "cert-manager + trust-manager",
                f"Already installed ✓ (AIO platform ext {ext_ver})"
            )
            return
        logger.info(
            "Existing AIO platform extension in state '%s'; reinstalling.",
            prov_state,
        )

    version_msg = f" version {version}" if version else ""
    print_step(
        1, TOTAL_STEPS,
        f"cert-manager + trust-manager... Installing AIO platform ext{version_msg}"
    )

    create_args = [
        "k8s-extension", "create",
        "--resource-group", resource_group,
        "--cluster-name", cluster_name,
        "--name", AIO_PLATFORM_EXTENSION_NAME,
        "--cluster-type", "connectedClusters",
        "--extension-type", AIO_PLATFORM_EXTENSION_TYPE,
        "--scope", AIO_PLATFORM_EXTENSION_SCOPE,
        "--release-namespace", AIO_PLATFORM_EXTENSION_NAMESPACE,
    ]
    if version:
        create_args.extend(["--version", version, "--auto-upgrade", "false"])
    if no_wait:
        create_args.append("--no-wait")

    invoke_cli_command(cmd, create_args)

    suffix = " (--no-wait)" if no_wait else ""
    print_step(
        1, TOTAL_STEPS, "cert-manager + trust-manager",
        f"Installed via AIO platform extension{suffix} ✓"
    )


# ---------------------------------------------------------------------------
# Step 3: WO extension
# ---------------------------------------------------------------------------

def _ensure_wo_extension(
    cmd, cluster_name, resource_group, extension_name,
    extension_version, release_train, no_wait,
    kube_config=None, kube_context=None,
):
    """Check if WO extension is installed; install if missing."""
    # Check existing extensions
    try:
        extensions = invoke_cli_command(
            cmd,
            [
                "k8s-extension", "list",
                "-g", resource_group,
                "--cluster-name", cluster_name,
                "--cluster-type", "connectedClusters",
            ]
        )
    except CLIInternalError:
        extensions = []

    # Find WO extension that is actually working
    wo_extensions = [
        ext for ext in (extensions or [])
        if (ext.get("extensionType", "") or "").lower()
        == DEFAULT_EXTENSION_TYPE.lower()
    ]

    if wo_extensions:
        ext = wo_extensions[0]
        ext_id = ext.get("id", "")
        ext_ver = ext.get("version", "unknown")
        prov_state = ext.get("provisioningState", "").lower()

        if prov_state == "succeeded":
            print_step(
                3, TOTAL_STEPS, "WO extension",
                f"Already installed ✓ (version {ext_ver})"
            )
            return ext_id

    # Install extension
    version_msg = f" version {extension_version}" if extension_version else ""
    print_step(
        3, TOTAL_STEPS,
        f"WO extension... Creating '{extension_name}'{version_msg}"
    )

    create_args = [
        "k8s-extension", "create",
        "-g", resource_group,
        "--cluster-name", cluster_name,
        "--cluster-type", "connectedClusters",
        "--name", extension_name,
        "--extension-type", DEFAULT_EXTENSION_TYPE,
        "--scope", DEFAULT_EXTENSION_SCOPE,
        "--release-train", release_train,
        "--auto-upgrade", "false",
    ]
    if extension_version:
        create_args.extend(["--version", extension_version])
    if no_wait:
        create_args.append("--no-wait")

    # Auto-detect storage class and pass redis PVC config
    storage_class = _detect_storage_class(kube_config, kube_context)
    if storage_class:
        create_args.extend([
            "--configuration-settings",
            f"redis.persistentVolume.storageClass={storage_class}",
            "--configuration-settings",
            f"redis.persistentVolume.size={DEFAULT_STORAGE_SIZE}",
        ])

    result = invoke_cli_command(cmd, create_args)
    ext_id = result.get("id", "") if isinstance(result, dict) else ""

    if no_wait:
        print_step(3, TOTAL_STEPS, "WO extension", "Creating (--no-wait) ✓")
    else:
        print_step(3, TOTAL_STEPS, "WO extension", "Installed ✓")

    return ext_id


# ---------------------------------------------------------------------------
# Step 4: Custom location
# ---------------------------------------------------------------------------

def _ensure_custom_location(
    cmd, cluster_name, resource_group, location,  # pylint: disable=unused-argument
    custom_location_name, extension_id, connected_cluster_id
):
    """Check if custom location exists; create if missing."""
    # Check existing - use REST directly to avoid CLI error output on 404
    sub_id = _get_sub_id(cmd)
    cl_arm_url = (
        f"https://management.azure.com/subscriptions"
        f"/{sub_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.ExtendedLocation"
        f"/customLocations/{custom_location_name}"
    )
    try:
        response = send_raw_request(
            cmd.cli_ctx,
            method="GET",
            url=f"{cl_arm_url}?api-version=2021-08-15",
            resource="https://management.azure.com"
        )
        if response.status_code == 200 and response.text:
            cl_info = response.json()
            cl_id = cl_info.get("id", "")
            if cl_id:
                print_step(
                    4, TOTAL_STEPS, "Custom location",
                    f"Already exists ✓ ('{custom_location_name}')"
                )
                return cl_id
    except Exception:
        pass  # Not found or error, proceed to create

    if not extension_id:
        raise CLIInternalError(
            "Cannot create custom location: WO extension ID is not available."
        )

    print_step(
        4, TOTAL_STEPS,
        f"Custom location... Creating '{custom_location_name}'"
    )

    try:
        result = invoke_cli_command(
            cmd,
            [
                "customlocation", "create",
                "-g", resource_group,
                "-n", custom_location_name,
                "--cluster-extension-ids", extension_id,
                "--host-resource-id", connected_cluster_id,
                "--namespace", DEFAULT_EXTENSION_NAMESPACE,
                "--location", location,
            ]
        )
        cl_id = result.get("id", "") if isinstance(result, dict) else ""
    except CLIInternalError as exc:
        raise CLIInternalError(
            f"Failed to create custom location: {exc}"
        )

    print_step(4, TOTAL_STEPS, "Custom location", "Created ✓")
    return cl_id


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_storage_class(kube_config=None, kube_context=None):
    """Auto-detect the default storage class from the cluster."""
    try:
        from kubernetes import client, config as k8s_config
        k8s_config.load_kube_config(
            config_file=kube_config, context=kube_context
        )
        storage_v1 = client.StorageV1Api()
        scs = storage_v1.list_storage_class()
        # Prefer the default storage class
        for sc in scs.items:
            annotations = sc.metadata.annotations or {}
            if annotations.get("storageclass.kubernetes.io/is-default-class") == "true":
                logger.info("Auto-detected default storage class: %s", sc.metadata.name)
                return sc.metadata.name
        # Fallback: first available storage class
        if scs.items:
            name = scs.items[0].metadata.name
            logger.info("No default storage class found, using first: %s", name)
            return name
    except Exception as exc:
        logger.warning("Could not detect storage class: %s", exc)
    return None


def _print_diagnostic_summary(step_results, cluster_name, resource_group):
    """Print a diagnostic summary showing what succeeded/failed.

    This gives the DRI/support engineer a quick picture of where things
    went wrong when a customer reports an issue.
    """
    from datetime import datetime, timezone

    _eprint("\n" + "=" * 60)
    _eprint("  Diagnostic Summary")
    _eprint(f"  Cluster: {cluster_name}")
    _eprint(f"  Resource Group: {resource_group}")
    _eprint(f"  Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    _eprint("=" * 60)

    for step_name, result in step_results.items():
        if "FAILED" in result:
            icon = "✗"
        elif result == "Skipped":
            icon = "○"
        else:
            icon = "✓"
        _eprint(f"  {icon} {step_name}: {result}")

    has_failure = any("FAILED" in v for v in step_results.values())
    if has_failure:
        _eprint("\n  [WARN] One or more steps failed. See error details above.")
        _eprint("  Re-run the command to retry - completed steps will be skipped.")
    _eprint("=" * 60 + "\n")


def _write_extended_location_file(extended_location):
    """Write extended-location.json to the current working directory."""
    filepath = os.path.join(os.getcwd(), "extended-location.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(extended_location, f, indent=2)
    _eprint(f"\n  File written: {filepath}")


def _get_sub_id(cmd):
    """Get subscription ID from CLI context."""
    try:
        from azure.cli.core._profile import Profile
        profile = Profile(cli_ctx=cmd.cli_ctx)
        sub = profile.get_subscription()
        return sub.get("id", "")
    except Exception:
        return ""
