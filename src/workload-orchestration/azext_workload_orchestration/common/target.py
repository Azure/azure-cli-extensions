# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Target prepare, deploy, and service-group link for Workload Orchestration."""

# pylint: disable=broad-exception-caught
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
# pylint: disable=import-outside-toplevel

import json
import os
import logging

from azure.cli.core.azclierror import (
    CLIInternalError,
    HTTPError,
    ValidationError,
)
from azure.cli.core.util import send_raw_request

from azext_workload_orchestration.common.consts import (
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
    SG_MEMBER_API_VERSION,
    TARGET_API_VERSION,
    get_arm_endpoint,
)
from azext_workload_orchestration.common.utils import (
    _eprint,
    invoke_cli_command,
)

logger = logging.getLogger(__name__)


# ===========================================================================
# target_prepare
# ===========================================================================


def target_prepare(
    cmd,
    cluster_name,
    resource_group,
    location,
    extension_name=None,
    custom_location_name=None,
    custom_location_resource_group=None,
    custom_location_location=None,
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
    custom_location_resource_group = custom_location_resource_group or resource_group
    custom_location_location = custom_location_location or location
    release_train = release_train or DEFAULT_RELEASE_TRAIN
    cert_manager_version = cert_manager_version or DEFAULT_CERT_MANAGER_VERSION

    _eprint(f"\nPreparing cluster '{cluster_name}' for Workload Orchestration...\n")

    step_results = {}

    try:
        connected_cluster_id = _preflight_checks(cmd, cluster_name, resource_group)
        step_results["preflight"] = "Passed"
    except Exception as exc:
        step_results["preflight"] = f"FAILED: {exc}"
        _print_failure_hint(step_results)
        raise

    # Step 1+2: cert-manager + trust-manager (single AIO Arc extension)
    try:
        _ensure_cert_trust_manager_via_aio_extension(
            cmd, cluster_name, resource_group,
            cert_manager_version, no_wait,
        )
        step_results["cert-manager"] = "Succeeded"
        step_results["trust-manager"] = "Succeeded (bundled)"
    except Exception as exc:
        step_results["cert-manager"] = f"FAILED: {exc}"
        logger.debug(
            "Steps 1-2/4 failed (AIO cert/trust-manager): %s", exc
        )
        _print_failure_hint(step_results)
        raise CLIInternalError("cert-manager/trust-manager installation failed. See error above.")

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
        logger.debug("Step 3/4 failed (WO extension): %s", exc)
        _print_failure_hint(step_results)
        raise CLIInternalError("WO extension installation failed. See error above.")

    # Step 4: Custom location
    try:
        cl_id = _ensure_custom_location(
            cmd, cluster_name, custom_location_resource_group, custom_location_location,
            custom_location_name, extension_id, connected_cluster_id
        )
        step_results["custom-location"] = "Succeeded"
    except ValidationError:
        raise
    except Exception as exc:
        step_results["custom-location"] = f"FAILED: {exc}"
        logger.debug("Step 4/4 failed (Custom location): %s", exc)
        _print_failure_hint(step_results)
        raise CLIInternalError("Custom location creation failed. See error above.")

    extended_location = {"name": cl_id, "type": "CustomLocation"}

    _eprint()

    return {
        "clusterName": cluster_name,
        "customLocationId": cl_id,
        "extensionId": extension_id,
        "extendedLocation": extended_location,
        "connectedClusterId": connected_cluster_id,
    }


# ---------------------------------------------------------------------------
# target_prepare — Pre-flight checks
# ---------------------------------------------------------------------------

def _preflight_checks(cmd, cluster_name, resource_group):
    """Verify cluster is Arc-connected and custom-locations feature enabled."""
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
# target_prepare — Step 1+2: cert-manager + trust-manager via AIO Platform extension
# ---------------------------------------------------------------------------

def _ensure_cert_trust_manager_via_aio_extension(
    cmd, cluster_name, resource_group, version, no_wait
):
    """Install cert-manager + trust-manager as an Arc k8s-extension.

    Uses microsoft.iotoperations.platform which bundles cert-manager and
    trust-manager. Idempotent: skips if an extension of that type already
    exists on the cluster.
    """
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
            _eprint(
                f"  ├── Workload Orchestration Extension Dependency: {AIO_PLATFORM_EXTENSION_NAME} "
                f"Already installed ✓ ({ext_ver})"
            )
            return
        logger.info(
            "Existing AIO platform extension in state '%s'; reinstalling.",
            prov_state,
        )

    version_msg = f" version {version}" if version else ""
    _eprint(
        f"  ├── Installing Workload Orchestration Extension Dependency: "
        f"{AIO_PLATFORM_EXTENSION_NAME}{version_msg}..."
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
    _eprint(
        f"  Workload Orchestration Extension Dependency: "
        f"{AIO_PLATFORM_EXTENSION_NAME} Installed{suffix} ✓"
    )


# ---------------------------------------------------------------------------
# target_prepare — Step 3: WO extension
# ---------------------------------------------------------------------------

def _ensure_wo_extension(
    cmd, cluster_name, resource_group, extension_name,
    extension_version, release_train, no_wait,
    kube_config=None, kube_context=None,
):
    """Check if WO extension is installed; install if missing."""
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
            _eprint(
                f"  ├── Workload Orchestration Extension: {extension_name} "
                f"Already installed ✓ ({ext_ver})"
            )
            return ext_id

    version_msg = f" version {extension_version}" if extension_version else ""
    _eprint(
        f"  ├── Installing Workload Orchestration Extension: {extension_name}{version_msg}..."
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
        _eprint(f"  ├── Workload Orchestration Extension: {extension_name} Creating (--no-wait) ✓")
    else:
        _eprint(f"  ├── Workload Orchestration Extension: {extension_name} Installed ✓")

    return ext_id


# ---------------------------------------------------------------------------
# target_prepare — Step 4: Custom location
# ---------------------------------------------------------------------------

def _ensure_custom_location(
    cmd, cluster_name, resource_group, location,  # pylint: disable=unused-argument
    custom_location_name, extension_id, connected_cluster_id
):
    """Check if custom location exists; create if missing."""
    # Check existing - use REST directly to avoid CLI error output on 404
    sub_id = _get_subscription_id(cmd)
    cl_arm_url = (
        f"{get_arm_endpoint(cmd)}/subscriptions"
        f"/{sub_id}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.ExtendedLocation"
        f"/customLocations/{custom_location_name}"
    )
    try:
        response = send_raw_request(
            cmd.cli_ctx,
            method="GET",
            url=f"{cl_arm_url}?api-version=2021-08-15",
        )
        if response.status_code == 200 and response.text:
            cl_info = response.json()
            cl_id = cl_info.get("id", "")
            if cl_id:
                # Validate that the existing CL is bound to our cluster
                existing_host = (
                    cl_info.get("properties", {}).get("hostResourceId", "")
                )
                if existing_host.lower() != connected_cluster_id.lower():
                    raise ValidationError(
                        f"Requested Custom Location '{custom_location_name}' is already "
                        f"associated with Cluster '{existing_host}'. "
                        f"Please choose a different name."
                    )
                _eprint(
                    f"  └── Custom Location: '{custom_location_name}' Already exists ✓"
                )
                return cl_id
    except ValidationError:
        raise
    except Exception:
        pass  # Not found or error, proceed to create

    if not extension_id:
        raise CLIInternalError(
            "Cannot create custom location: WO extension ID is not available."
        )

    _eprint(f"  └── Creating Custom Location: '{custom_location_name}'...")

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

    _eprint(f"  └── Custom Location: '{custom_location_name}' Created ✓")
    return cl_id


# ---------------------------------------------------------------------------
# target_prepare — Helpers
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


def _print_failure_hint(step_results):
    """Print a concise one-line failure summary to stderr.

    The raw error from the underlying az subcommand has already been
    printed (it goes to stderr from `invoke_cli_command`), and azcli
    will print our raised CLIInternalError on exit. This hint just
    points to the failed step + tells the user retry is safe.
    """
    failed = [k for k, v in step_results.items() if "FAILED" in v]
    if not failed:
        return
    name = failed[-1]
    _eprint(f"\n✗ {name} failed — see error above.")
    _eprint("  Re-run the command to retry; completed steps will be skipped.\n")


def _write_extended_location_file(extended_location):
    """Write extended-location.json to the current working directory."""
    filepath = os.path.join(os.getcwd(), "extended-location.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(extended_location, f, indent=2)
    _eprint(f"\n  File written: {filepath}")


# ===========================================================================
# target_deploy
# ===========================================================================

API_VERSION = "2025-08-01"


def target_deploy_pre_install(
    cmd,
    resource_group,
    target_name,
    solution_template_name=None,
    solution_template_version=None,
    solution_template_rg=None,
    config=None,
):
    """Run config-set → review → publish and return the solution-version-id.

    Called by the enhanced `target install` command before the AAZ install step.
    Does NOT run install — that's handled by the AAZ LRO.

    When using friendly name, solution_template_rg defaults to resource_group.
    Config-template args are auto-derived from solution template args.
    """
    sub_id = _get_subscription_id(cmd)

    solution_template_version_id = _resolve_template_version_id(
        solution_template_name, solution_template_version,
        solution_template_rg, resource_group, sub_id,
    )

    base_url = (
        f"{get_arm_endpoint(cmd)}/subscriptions/{sub_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Edge/targets/{target_name}"
    )

    do_config = config is not None

    # --- Step 0: Config set ---
    if do_config:
        # Auto-derive config template args from solution template args
        ct_rg = solution_template_rg or resource_group
        ct_name = solution_template_name
        ct_version = solution_template_version

        _handle_config_set(
            cmd, config, None, ct_rg,
            ct_name, ct_version,
            resource_group, target_name, sub_id,
        )

    # --- Step 1: Review ---
    review_result = _do_review(cmd, base_url, solution_template_version_id)
    sv_id = _extract_solution_version_id(review_result)

    # --- Step 2: Publish ---
    _do_publish(cmd, base_url, sv_id)

    # Step 3 (Install) is handled by AAZ LRO — tick printed in post_operations

    return sv_id

# ---------------------------------------------------------------------------
# target_deploy — Resolution helpers
# ---------------------------------------------------------------------------


def _get_subscription_id(cmd):
    """Get subscription ID from CLI context."""
    sub_id = cmd.cli_ctx.data.get('subscription_id')
    if not sub_id:
        from azure.cli.core._profile import Profile
        sub_id = Profile(cli_ctx=cmd.cli_ctx).get_subscription_id()
    return sub_id


def _resolve_template_version_id(
    template_name, template_version, template_rg,
    default_rg, sub_id,
):
    """Resolve solution-template-version-id from the friendly-name args.

    When template_rg is not provided, defaults to default_rg (target's RG).
    """
    if not template_name:
        raise ValidationError(
            "--solution-template-name is required for full deploy."
        )
    if not template_version:
        raise ValidationError(
            "--solution-template-version is required when using --solution-template-name."
        )
    rg = template_rg or default_rg
    return (
        f"/subscriptions/{sub_id}/resourceGroups/{rg}"
        f"/providers/Microsoft.Edge/solutionTemplates/{template_name}"
        f"/versions/{template_version}"
    )

# ---------------------------------------------------------------------------
# target_deploy — Step implementations
# ---------------------------------------------------------------------------


def _do_review(cmd, base_url, solution_template_version_id):
    """POST .../reviewSolutionVersion"""
    url = f"{base_url}/reviewSolutionVersion?api-version={API_VERSION}"
    body = {
        "solutionTemplateVersionId": solution_template_version_id,
    }

    resp = send_raw_request(
        cmd.cli_ctx, "POST", url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
    )
    return _parse_response(resp, "Review", cmd=cmd)


def _do_publish(cmd, base_url, solution_version_id):
    """POST .../publishSolutionVersion"""
    url = f"{base_url}/publishSolutionVersion?api-version={API_VERSION}"
    body = {"solutionVersionId": solution_version_id}

    resp = send_raw_request(
        cmd.cli_ctx, "POST", url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
    )
    return _parse_response(resp, "Publish", cmd=cmd)


def _handle_config_set(
    cmd, config_file, hierarchy_id, template_rg,
    template_name, template_version,
    resource_group, target_name, sub_id,
):
    """Set configuration values from file before review.

    Calls the configuration-set REST APIs directly (no subprocess).
    Flow: resolve config ID → resolve template unique ID → GET/PUT dynamic config version.
    """
    if not hierarchy_id:
        hierarchy_id = (
            f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Edge/targets/{target_name}"
        )

    if not template_rg or not template_name or not template_version:
        raise ValidationError(
            "When using --config, you must also provide "
            "--config-template-rg, --config-template-name, and --config-template-version."
        )

    config_content = _read_config_file(config_file)

    # Step 1: Resolve configuration ID from hierarchy's config reference
    config_ref_url = (
        f"{get_arm_endpoint(cmd)}{hierarchy_id}"
        f"/providers/Microsoft.Edge/configurationreferences/default"
        f"?api-version={API_VERSION}"
    )
    try:
        ref_resp = send_raw_request(
            cmd.cli_ctx, "GET", config_ref_url,
            headers=["Accept=application/json"],
        )
    except HTTPError as e:
        raise CLIInternalError(
            f"Failed to get configuration reference for {hierarchy_id}. "
            f"Ensure hierarchy has a configuration reference. Error: {e}"
        ) from e
    configuration_id = ref_resp.json().get("properties", {}).get("configurationResourceId")
    if not configuration_id:
        raise CLIInternalError(
            f"Configuration reference for {hierarchy_id} has no configurationResourceId."
        )

    # Step 2: Resolve solution template unique identifier (used as dynamic config name)
    st_url = (
        f"{get_arm_endpoint(cmd)}/subscriptions/{sub_id}"
        f"/resourceGroups/{template_rg}"
        f"/providers/Microsoft.Edge/solutionTemplates/{template_name}"
        f"?api-version={API_VERSION}"
    )
    try:
        st_resp = send_raw_request(
            cmd.cli_ctx, "GET", st_url,
            headers=["Accept=application/json"],
        )
    except HTTPError as e:
        raise CLIInternalError(
            f"Solution template '{template_name}' not found in RG '{template_rg}'. "
            f"Error: {e}"
        ) from e
    st_body = st_resp.json()
    dynamic_config_name = (
        st_body.get("properties", {}).get("uniqueIdentifier")
        or template_name
    )

    # Step 3: GET dynamic config version (check if it exists)
    version_url = (
        f"{get_arm_endpoint(cmd)}{configuration_id}"
        f"/dynamicConfigurations/{dynamic_config_name}"
        f"/versions/{template_version}"
        f"?api-version={API_VERSION}"
    )
    version_exists = False
    try:
        version_resp = send_raw_request(
            cmd.cli_ctx, "GET", version_url,
            headers=["Accept=application/json"],
        )
        version_exists = True
    except HTTPError:
        # 404 is expected when dynamic config version doesn't exist yet
        pass

    if version_exists:
        # Update existing dynamic config version
        existing = version_resp.json()
        existing["properties"]["values"] = config_content
        send_raw_request(
            cmd.cli_ctx, "PUT", version_url,
            body=json.dumps(existing),
            headers=["Content-Type=application/json", "Accept=application/json"],
        )
    else:
        # Create new: first ensure parent dynamic config exists
        dc_url = (
            f"{get_arm_endpoint(cmd)}{configuration_id}"
            f"/dynamicConfigurations/{dynamic_config_name}"
            f"?api-version={API_VERSION}"
        )
        dc_body = {"properties": {"currentVersion": template_version}}
        send_raw_request(
            cmd.cli_ctx, "PUT", dc_url,
            body=json.dumps(dc_body),
            headers=["Content-Type=application/json", "Accept=application/json"],
        )

        # Then create the version with config values
        ver_body = {"properties": {"values": config_content}}
        send_raw_request(
            cmd.cli_ctx, "PUT", version_url,
            body=json.dumps(ver_body),
            headers=["Content-Type=application/json", "Accept=application/json"],
        )


def _read_config_file(file_path):
    """Read and return contents of a YAML/JSON config file."""
    if not os.path.isfile(file_path):
        raise ValidationError(f"Config file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# ---------------------------------------------------------------------------
# target_deploy — LRO and response helpers
# ---------------------------------------------------------------------------


def _parse_response(resp, step_name, cmd=None):
    """Parse REST response, handling 200/201/202 LRO patterns."""
    status = resp.status_code
    if status in (200, 201):
        try:
            return resp.json()
        except (ValueError, AttributeError):
            return {"status": "Succeeded"}
    if status == 202:
        return _poll_lro(resp, step_name, cmd=cmd)

    try:
        error_body = resp.text
    except (ValueError, AttributeError):
        error_body = f"HTTP {status}"
    raise CLIInternalError(f"{step_name} failed (HTTP {status}): {error_body}")


def _poll_lro(resp, step_name, cmd=None):
    """Poll an LRO via Location or Azure-AsyncOperation header."""
    import time

    location = resp.headers.get("Location") or resp.headers.get("Azure-AsyncOperation")
    if not location:
        logger.warning("No LRO polling URL in %s response headers", step_name)
        return {"status": "Accepted"}

    retry_after = int(resp.headers.get("Retry-After", "10"))
    max_polls = 60  # ~10 min max

    for i in range(max_polls):
        time.sleep(retry_after)
        try:
            poll_resp = send_raw_request(cmd.cli_ctx, "GET", location)
        except (CLIInternalError, ValueError, ConnectionError):
            logger.debug("LRO poll attempt %d failed for %s", i + 1, step_name)
            continue

        try:
            body = poll_resp.json()
        except (ValueError, AttributeError):
            continue

        poll_status = body.get("status", "").lower()
        if poll_status in ("succeeded", "completed"):
            return body
        if poll_status in ("failed", "canceled", "cancelled"):
            raise CLIInternalError(
                f"{step_name} LRO failed: {json.dumps(body, indent=2)}"
            )

    raise CLIInternalError(f"{step_name} LRO timed out after {max_polls * retry_after}s")


def _extract_solution_version_id(review_result):
    """Extract solution-version-id from review response."""
    if not review_result or not isinstance(review_result, dict):
        raise CLIInternalError("Review returned no result - cannot determine solution version ID.")

    # The LRO response structure:
    # {id, name, status, properties: {id: <SV ARM ID>, properties: {...}, ...}}
    # The solution version ARM ID is at properties.id (NOT properties.properties.id)
    props = review_result.get("properties", {})

    sv_id = (
        props.get("id")                                      # properties.id (most common)
        or review_result.get("solutionVersionId")             # top-level fallback
        or props.get("solutionVersionId")                     # properties.solutionVersionId
        or (props.get("properties", {}) or {}).get("id")      # properties.properties.id
    )
    if not sv_id:
        logger.warning(
            "Could not extract solutionVersionId. Keys: %s, full (truncated): %s",
            list(review_result.keys()),
            json.dumps(review_result, indent=2)[:800]
        )
        raise CLIInternalError(
            "Review succeeded but no solutionVersionId found in response."
        )
    return sv_id


# ===========================================================================
# target_sg_link
# ===========================================================================

def link_target_to_service_group(cmd, target_id, service_group_name):
    """Link a target to a service group and refresh hierarchy.

    Two REST calls:
    1. PUT {targetId}/providers/Microsoft.Relationships/serviceGroupMember/{sgName}
    2. PUT {targetId} (update target to refresh hierarchy — MANDATORY)
    """
    sg_member_url = (
        f"{get_arm_endpoint(cmd)}{target_id}"
        f"/providers/Microsoft.Relationships/serviceGroupMember/{service_group_name}"
    )

    # Step 1: Create ServiceGroupMember relationship
    try:
        invoke_cli_command(cmd, [
            "rest",
            "--method", "put",
            "--url", f"{sg_member_url}?api-version={SG_MEMBER_API_VERSION}",
            "--body", json.dumps({
                "properties": {
                    "targetId": f"/providers/Microsoft.Management/serviceGroups/{service_group_name}"
                }
            }),
            "--header", "Content-Type=application/json",
        ], expect_json=False)
        logger.info("ServiceGroupMember created: %s -> %s", target_id, service_group_name)
    except Exception as exc:
        raise CLIInternalError(
            f"Failed to link target to service group '{service_group_name}': {exc}"
        )

    # Step 2: Update target to refresh hierarchy (MANDATORY)
    try:
        # GET current target
        target_data = invoke_cli_command(cmd, [
            "rest",
            "--method", "get",
            "--url", f"{get_arm_endpoint(cmd)}{target_id}?api-version={TARGET_API_VERSION}",
        ])

        # PUT target (update to refresh hierarchy)
        if target_data and isinstance(target_data, dict):
            # Strip read-only fields, preserve writable top-level fields
            body = {
                "location": target_data.get("location", ""),
                "properties": target_data.get("properties", {}),
            }
            if "extendedLocation" in target_data:
                body["extendedLocation"] = target_data["extendedLocation"]
            if "tags" in target_data:
                body["tags"] = target_data["tags"]

            invoke_cli_command(cmd, [
                "rest",
                "--method", "put",
                "--url", f"{get_arm_endpoint(cmd)}{target_id}?api-version={TARGET_API_VERSION}",
                "--body", json.dumps(body),
                "--header", "Content-Type=application/json",
            ], expect_json=False)
            logger.info("Target hierarchy refreshed after SG link")

    except Exception as exc:
        logger.warning(
            "Target hierarchy refresh after SG link may have failed: %s. "
            "Target may appear unlinked until next update.", exc
        )
