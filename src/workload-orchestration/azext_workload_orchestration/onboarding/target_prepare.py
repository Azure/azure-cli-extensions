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
import subprocess
import logging

from azure.cli.core.azclierror import (
    CLIInternalError,
    ValidationError,
)

from azext_workload_orchestration.onboarding.consts import (
    DEFAULT_CERT_MANAGER_VERSION,
    CERT_MANAGER_MANIFEST_URL,
    CERT_MANAGER_NAMESPACE,
    CERT_MANAGER_WEBHOOK_DEPLOYMENT,
    CERT_MANAGER_MIN_PODS,
    CERT_MANAGER_WAIT_TIMEOUT,
    TRUST_MANAGER_DEPLOYMENT,
    TRUST_MANAGER_HELM_REPO,
    TRUST_MANAGER_HELM_REPO_NAME,
    TRUST_MANAGER_HELM_CHART,
    DEFAULT_EXTENSION_TYPE,
    DEFAULT_EXTENSION_NAME,
    DEFAULT_RELEASE_TRAIN,
    DEFAULT_EXTENSION_NAMESPACE,
    DEFAULT_EXTENSION_SCOPE,
)
from azext_workload_orchestration.onboarding.utils import (
    invoke_cli_command,
    print_step,
    print_success,
    print_detail,
)

from azure.cli.core.util import send_raw_request

logger = logging.getLogger(__name__)

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
    skip_cert_manager=False,
    skip_trust_manager=False,
    kube_config=None,
    kube_context=None,
    no_wait=False,
):
    """Prepare an Arc-connected K8s cluster for Workload Orchestration.

    Installs cert-manager, trust-manager, WO extension, and creates a custom
    location. Skips components that are already installed (idempotent).
    """
    extension_name = extension_name or DEFAULT_EXTENSION_NAME
    custom_location_name = custom_location_name or f"{cluster_name}-cl"
    release_train = release_train or DEFAULT_RELEASE_TRAIN
    cert_manager_version = cert_manager_version or DEFAULT_CERT_MANAGER_VERSION

    print(f"\nPreparing cluster '{cluster_name}' for Workload Orchestration...\n")

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

    # Step 1: cert-manager
    try:
        if skip_cert_manager:
            print_step(1, TOTAL_STEPS, "cert-manager", "Skipped (--skip-cert-manager)")
            step_results["cert-manager"] = "Skipped"
        else:
            _ensure_cert_manager(cert_manager_version, kube_config, kube_context)
            step_results["cert-manager"] = "Succeeded"
    except Exception as exc:
        step_results["cert-manager"] = f"FAILED: {exc}"
        logger.error("Step 1/4 failed (cert-manager): %s", exc)
        _print_diagnostic_summary(step_results, cluster_name, resource_group)
        raise CLIInternalError(
            f"cert-manager installation failed: {exc}",
            recommendation=(
                "Check cluster connectivity and kubectl access. "
                "Verify the cluster has internet access to github.com. "
                "Try manually: kubectl apply -f https://github.com/cert-manager/"
                f"cert-manager/releases/download/{cert_manager_version}/cert-manager.yaml"
            )
        )

    # Step 2: trust-manager
    try:
        if skip_trust_manager:
            print_step(2, TOTAL_STEPS, "trust-manager", "Skipped (--skip-trust-manager)")
            step_results["trust-manager"] = "Skipped"
        else:
            _ensure_trust_manager(kube_config, kube_context)
            step_results["trust-manager"] = "Succeeded"
    except CLIInternalError:
        raise  # Already has good error message (e.g., helm not installed)
    except Exception as exc:
        step_results["trust-manager"] = f"FAILED: {exc}"
        logger.error("Step 2/4 failed (trust-manager): %s", exc)
        _print_diagnostic_summary(step_results, cluster_name, resource_group)
        raise CLIInternalError(
            f"trust-manager installation failed: {exc}",
            recommendation=(
                "Ensure helm is installed and the cluster can reach charts.jetstack.io. "
                "Try manually: helm upgrade trust-manager jetstack/trust-manager "
                "--install --namespace cert-manager --wait"
            )
        )

    # Step 3: WO extension
    try:
        extension_id = _ensure_wo_extension(
            cmd, cluster_name, resource_group, extension_name,
            extension_version, release_train, no_wait,
            kube_config, kube_context
        )
        step_results["wo-extension"] = "Succeeded"
    except Exception as exc:
        step_results["wo-extension"] = f"FAILED: {exc}"
        logger.error("Step 3/4 failed (WO extension): %s", exc)
        _print_diagnostic_summary(step_results, cluster_name, resource_group)
        raise CLIInternalError(
            f"WO extension installation failed: {exc}",
            recommendation=(
                "Common causes:\n"
                "  - Wrong release train for this region (try --release-train preview or dev)\n"
                "  - Insufficient cluster resources (need 2+ CPU cores, 4Gi+ memory)\n"
                "  - Storage class not available (check: kubectl get sc)\n"
                "Try manually: az k8s-extension create -g {rg} --cluster-name {cluster} "
                "--cluster-type connectedClusters --name {ext} "
                "--extension-type Microsoft.workloadorchestration --scope cluster "
                f"--release-train {release_train}"
            ).format(rg=resource_group, cluster=cluster_name, ext=extension_name)
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
            f"Custom location creation failed: {exc}",
            recommendation=(
                "Ensure custom-locations feature is enabled:\n"
                f"  az connectedk8s enable-features -n {cluster_name} "
                f"-g {resource_group} --features cluster-connect custom-locations\n"
                "Also verify the extension is in 'Succeeded' state:\n"
                f"  az k8s-extension show -g {resource_group} "
                f"--cluster-name {cluster_name} --cluster-type connectedClusters "
                f"--name {extension_name}"
            )
        )

    # Output extended-location.json
    extended_location = {"name": cl_id, "type": "CustomLocation"}
    _write_extended_location_file(extended_location)

    # Print diagnostic summary (all steps succeeded)
    _print_diagnostic_summary(step_results, cluster_name, resource_group)

    print_success(f"Cluster '{cluster_name}' is ready for Workload Orchestration")
    print_detail("Custom Location ID", cl_id)
    print()

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
            f"in resource group '{resource_group}'.",
            recommendation=(
                f"Run: az connectedk8s connect -g {resource_group} "
                f"-n {cluster_name} -l <location>"
            )
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
# Step 1: cert-manager
# ---------------------------------------------------------------------------

def _ensure_cert_manager(version, kube_config, kube_context):
    """Check if cert-manager is installed; install if missing."""
    try:
        from kubernetes import client, config as k8s_config
        from kubernetes.client.rest import ApiException
    except ImportError:
        raise CLIInternalError(
            "kubernetes Python package is required.",
            recommendation="Run: pip install kubernetes"
        )

    # Load kubeconfig
    try:
        k8s_config.load_kube_config(
            config_file=kube_config,
            context=kube_context
        )
    except Exception as exc:
        raise CLIInternalError(
            f"Failed to load kubeconfig: {exc}",
            recommendation=(
                "Ensure kubectl is configured. "
                "Use --kube-config and --kube-context if needed."
            )
        )

    v1 = client.CoreV1Api()

    # Check if cert-manager namespace exists with running pods
    try:
        v1.read_namespace(CERT_MANAGER_NAMESPACE)
        pods = v1.list_namespaced_pod(CERT_MANAGER_NAMESPACE)
        running = [
            p for p in pods.items
            if p.status and p.status.phase == "Running"
        ]
        if len(running) >= CERT_MANAGER_MIN_PODS:
            print_step(
                1, TOTAL_STEPS, "cert-manager",
                f"Already installed [OK] ({len(running)} pods running)"
            )
            return
        logger.info(
            "cert-manager namespace exists but only %d/%d pods running. Reinstalling.",
            len(running), CERT_MANAGER_MIN_PODS
        )
    except ApiException as exc:
        if exc.status != 404:
            raise CLIInternalError(f"Failed to check cert-manager: {exc}")
        # 404 = namespace doesn't exist, proceed with install

    # Install cert-manager
    print_step(1, TOTAL_STEPS, f"cert-manager... Installing {version}")
    _run_kubectl([
        "apply", "-f",
        CERT_MANAGER_MANIFEST_URL.format(version=version),
        "--wait"
    ], kube_config, kube_context)

    # Wait for webhook to be ready
    _run_kubectl([
        "wait", "--for=condition=Available",
        f"deployment/{CERT_MANAGER_WEBHOOK_DEPLOYMENT}",
        "-n", CERT_MANAGER_NAMESPACE,
        f"--timeout={CERT_MANAGER_WAIT_TIMEOUT}"
    ], kube_config, kube_context)

    print_step(1, TOTAL_STEPS, "cert-manager", f"Installed {version} [OK]")


# ---------------------------------------------------------------------------
# Step 2: trust-manager
# ---------------------------------------------------------------------------

def _ensure_trust_manager(kube_config, kube_context):
    """Check if trust-manager is installed; install via helm if missing."""
    try:
        from kubernetes import client, config as k8s_config
        from kubernetes.client.rest import ApiException
    except ImportError:
        raise CLIInternalError(
            "kubernetes Python package is required.",
            recommendation="Run: pip install kubernetes"
        )

    # Load kubeconfig (may already be loaded from cert-manager step)
    try:
        k8s_config.load_kube_config(
            config_file=kube_config,
            context=kube_context
        )
    except Exception:
        pass  # Already loaded, or will fail below

    apps_v1 = client.AppsV1Api()

    # Check if trust-manager deployment exists
    try:
        apps_v1.read_namespaced_deployment(
            TRUST_MANAGER_DEPLOYMENT, CERT_MANAGER_NAMESPACE
        )
        print_step(2, TOTAL_STEPS, "trust-manager", "Already installed [OK]")
        return
    except ApiException as exc:
        if exc.status != 404:
            raise CLIInternalError(f"Failed to check trust-manager: {exc}")
        # 404 = not found, proceed with install

    # Check if helm is available
    if not _is_helm_available():
        raise CLIInternalError(
            "helm is required to install trust-manager.",
            recommendation=(
                "Install helm from https://helm.sh/docs/intro/install/ "
                "and try again."
            )
        )

    # Install trust-manager via helm
    print_step(2, TOTAL_STEPS, "trust-manager... Installing via helm")

    _run_command([
        "helm", "repo", "add",
        TRUST_MANAGER_HELM_REPO_NAME,
        TRUST_MANAGER_HELM_REPO,
        "--force-update"
    ])

    _run_command([
        "helm", "upgrade", TRUST_MANAGER_DEPLOYMENT,
        TRUST_MANAGER_HELM_CHART,
        "--install",
        "--namespace", CERT_MANAGER_NAMESPACE,
        "--wait"
    ])

    print_step(2, TOTAL_STEPS, "trust-manager", "Installed [OK]")


# ---------------------------------------------------------------------------
# Step 3: WO extension
# ---------------------------------------------------------------------------

def _ensure_wo_extension(
    cmd, cluster_name, resource_group, extension_name,
    extension_version, release_train, no_wait,
    kube_config=None, kube_context=None
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
                f"Already installed [OK] (version {ext_ver})"
            )
            return ext_id

        # Extension exists but is in failed/creating state - delete and reinstall
        logger.info(
            "WO extension exists but in '%s' state. Deleting and reinstalling...",
            prov_state
        )
        print_step(
            3, TOTAL_STEPS,
            f"WO extension... Found in '{prov_state}' state, reinstalling"
        )
        try:
            invoke_cli_command(cmd, [
                "k8s-extension", "delete",
                "-g", resource_group,
                "--cluster-name", cluster_name,
                "--cluster-type", "connectedClusters",
                "--name", ext.get("name", extension_name),
                "--yes",
            ], expect_json=False)
            import time as _time
            _time.sleep(10)  # Wait for delete to propagate
        except CLIInternalError:
            pass  # Best effort delete

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

    # Auto-detect storage class and pass as config setting
    storage_class = _detect_storage_class(kube_config, kube_context)
    if storage_class:
        create_args.extend([
            "--configuration-settings",
            f"redis.persistentVolume.storageClass={storage_class}",
        ])

    result = invoke_cli_command(cmd, create_args)
    ext_id = result.get("id", "") if isinstance(result, dict) else ""

    if no_wait:
        print_step(3, TOTAL_STEPS, "WO extension", "Creating (--no-wait) [OK]")
    else:
        print_step(3, TOTAL_STEPS, "WO extension", "Installed [OK]")

    return ext_id


# ---------------------------------------------------------------------------
# Step 4: Custom location
# ---------------------------------------------------------------------------

def _ensure_custom_location(
    cmd, cluster_name, resource_group, location,
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
                    f"Already exists [OK] ('{custom_location_name}')"
                )
                return cl_id
    except Exception:
        pass  # Not found or error, proceed to create

    if not extension_id:
        raise CLIInternalError(
            "Cannot create custom location: WO extension ID is not available.",
            recommendation=(
                "Ensure the WO extension was installed successfully. "
                "Re-run without --no-wait."
            )
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
            f"Failed to create custom location: {exc}",
            recommendation=(
                "This can happen if the 'custom-locations' feature is not enabled. "
                f"Run: az connectedk8s enable-features -n {cluster_name} "
                f"-g {resource_group} --features cluster-connect custom-locations"
            )
        )

    print_step(4, TOTAL_STEPS, "Custom location", "Created [OK]")
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

    print("\n" + "=" * 60)
    print("  Diagnostic Summary")
    print(f"  Cluster: {cluster_name}")
    print(f"  Resource Group: {resource_group}")
    print(f"  Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print("=" * 60)

    for step_name, result in step_results.items():
        if "FAILED" in result:
            icon = "[FAIL]"
        elif result == "Skipped":
            icon = "○"
        else:
            icon = "[OK]"
        print(f"  {icon} {step_name}: {result}")

    has_failure = any("FAILED" in v for v in step_results.values())
    if has_failure:
        print("\n  [WARN] One or more steps failed. See error details above.")
        print("  Re-run the command to retry - completed steps will be skipped.")
    print("=" * 60 + "\n")


def _write_extended_location_file(extended_location):
    """Write extended-location.json to the current working directory."""
    filepath = os.path.join(os.getcwd(), "extended-location.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(extended_location, f, indent=2)
    print(f"\n  File written: {filepath}")


def _run_kubectl(args, kube_config=None, kube_context=None):
    """Run a kubectl command with optional kubeconfig/context."""
    cmd_args = ["kubectl"]
    if kube_config:
        cmd_args.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_args.extend(["--context", kube_context])
    cmd_args.extend(args)

    logger.debug("Running: %s", " ".join(cmd_args))
    result = subprocess.run(  # pylint: disable=subprocess-run-check
        cmd_args,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise CLIInternalError(
            f"kubectl command failed: {' '.join(args)}\n{error_msg}",
            recommendation="Ensure kubectl is installed and cluster is reachable."
        )
    return result.stdout


def _run_command(cmd_args):
    """Run an arbitrary command (e.g., helm)."""
    logger.debug("Running: %s", " ".join(cmd_args))
    result = subprocess.run(  # pylint: disable=subprocess-run-check
        cmd_args,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise CLIInternalError(
            f"Command failed: {' '.join(cmd_args)}\n{error_msg}"
        )
    return result.stdout


def _is_helm_available():
    """Check if helm is available in PATH."""
    try:
        result = subprocess.run(  # pylint: disable=subprocess-run-check
            ["helm", "version", "--short"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _get_sub_id(cmd):
    """Get subscription ID from CLI context."""
    try:
        from azure.cli.core._profile import Profile
        profile = Profile(cli_ctx=cmd.cli_ctx)
        sub = profile.get_subscription()
        return sub.get("id", "")
    except Exception:
        return ""
