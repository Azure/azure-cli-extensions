# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Target deploy command - chains review -> publish -> install in one step.

Replaces 3 manual commands:
  1. az workload-orchestration target review
  2. az workload-orchestration target publish
  3. az workload-orchestration target install

Optionally prepends config-set (step 0) when --config is provided.

Usage:
    # Friendly name (template lives in target's RG)
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --solution-template-name tmpl --solution-template-version 1.0.0

    # Friendly name with explicit template RG
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --solution-template-name tmpl --solution-template-version 1.0.0 \\
        --solution-template-rg shared-rg

    # With config
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --solution-template-name tmpl --solution-template-version 1.0.0 \\
        --config values.yaml \\
        --config-template-rg rg --config-template-name tmpl --config-template-version 1.0.0
"""

import json
import logging

from azure.cli.core.azclierror import CLIInternalError, ValidationError
from azure.cli.core.util import send_raw_request

import sys

logger = logging.getLogger(__name__)


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


API_VERSION = "2025-08-01"
ARM_RESOURCE = "https://management.azure.com"


def target_deploy(
    cmd,
    resource_group,
    target_name,
    solution_template_name=None,
    solution_template_version=None,
    solution_template_rg=None,
    config=None,
    config_hierarchy_id=None,
    config_template_rg=None,
    config_template_name=None,
    config_template_version=None,
):
    """Deploy a solution to a target: config-set → review → publish → install.

    Standalone deploy function (used internally).
    """
    sub_id = _get_subscription_id(cmd)

    # --- Resolve solution-template-version-id ---
    solution_template_version_id = _resolve_template_version_id(
        solution_template_name, solution_template_version,
        solution_template_rg, resource_group, sub_id,
    )

    base_url = (
        f"{ARM_RESOURCE}/subscriptions/{sub_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Edge/targets/{target_name}"
    )

    # Figure out which steps to run
    do_config = config is not None

    total = sum([do_config, True, True, True])  # config(opt) + review + publish + install
    current = [0]  # mutable counter

    def _log(step_name, status=""):
        if status:
            connector = "└──" if current[0] == total else "├──"
            _eprint(f"{connector} {step_name} {status}")
        else:
            current[0] += 1
            connector = "└──" if current[0] == total else "├──"
            _eprint(f"{connector} {step_name}...")

    results = {}
    sv_id = None

    # --- Step 0: Config set ---
    if do_config:
        _log("Config Set")
        _handle_config_set(
            cmd, config, config_hierarchy_id, config_template_rg,
            config_template_name, config_template_version,
            resource_group, target_name, sub_id,
        )
        _log("Config Set", "✓")
        results["configSet"] = "Succeeded"

    # --- Step 1: Review ---
    _log("Review")
    review_result = _do_review(cmd, base_url, solution_template_version_id)
    results["review"] = review_result
    sv_id = _extract_solution_version_id(review_result)
    _log("Review", f"✓ solutionVersionId: {_short_id(sv_id)}")

    # --- Step 2: Publish ---
    _log("Publish")
    publish_result = _do_publish(cmd, base_url, sv_id)
    results["publish"] = publish_result
    _log("Publish", "✓")

    # --- Step 3: Install ---
    _log("Install")
    install_result = _do_install(cmd, base_url, sv_id)
    results["install"] = install_result
    _log("Install", "✓")

    _eprint(f"\n✅ Deployment complete for target '{target_name}'")
    _eprint(f"   Solution Version: {_short_id(sv_id)}")

    # Return the install LRO result (same format as `az wo target install`)
    return results.get("install", {
        "status": "Succeeded",
        "resourceId": f"{base_url}",
    })


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
        f"{ARM_RESOURCE}/subscriptions/{sub_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Edge/targets/{target_name}"
    )

    do_config = config is not None
    total = sum([do_config, True, True, True])  # config + review + publish + install(AAZ)
    current = [0]

    def _log(step_name, status=""):
        if status:
            connector = "└──" if current[0] == total else "├──"
            _eprint(f"{connector} {step_name} {status}")
        else:
            current[0] += 1
            connector = "└──" if current[0] == total else "├──"
            _eprint(f"{connector} {step_name}...")

    # --- Step 0: Config set ---
    if do_config:
        _log("Config Set")
        # Auto-derive config template args from solution template args
        ct_rg = solution_template_rg or resource_group
        ct_name = solution_template_name
        ct_version = solution_template_version

        _handle_config_set(
            cmd, config, None, ct_rg,
            ct_name, ct_version,
            resource_group, target_name, sub_id,
        )
        _log("Config Set", "✓")

    # --- Step 1: Review ---
    _log("Review")
    review_result = _do_review(cmd, base_url, solution_template_version_id)
    sv_id = _extract_solution_version_id(review_result)
    _log("Review", f"✓ solutionVersionId: {_short_id(sv_id)}")

    # --- Step 2: Publish ---
    _log("Publish")
    _do_publish(cmd, base_url, sv_id)
    _log("Publish", "✓")

    # Step 3 (Install) is handled by AAZ LRO — tick printed in post_operations

    return sv_id


# ---------------------------------------------------------------------------
# Resolution helpers
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
# Step implementations
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
        resource=ARM_RESOURCE,
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
        resource=ARM_RESOURCE,
    )
    return _parse_response(resp, "Publish", cmd=cmd)


def _do_install(cmd, base_url, solution_version_id):
    """POST .../installSolution"""
    url = f"{base_url}/installSolution?api-version={API_VERSION}"
    body = {"solutionVersionId": solution_version_id}

    resp = send_raw_request(
        cmd.cli_ctx, "POST", url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
        resource=ARM_RESOURCE,
    )

    return _parse_response(resp, "Install", cmd=cmd)


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

    # Read config file content
    config_content = _read_config_file(config_file)

    # Step 1: Resolve configuration ID from hierarchy's config reference
    config_ref_url = (
        f"{ARM_RESOURCE}{hierarchy_id}"
        f"/providers/Microsoft.Edge/configurationreferences/default"
        f"?api-version={API_VERSION}"
    )
    ref_resp = send_raw_request(
        cmd.cli_ctx, "GET", config_ref_url,
        headers=["Accept=application/json"],
        resource=ARM_RESOURCE,
    )
    if ref_resp.status_code != 200:
        raise CLIInternalError(
            f"Failed to get configuration reference for {hierarchy_id} "
            f"(HTTP {ref_resp.status_code}). Ensure hierarchy has a configuration reference."
        )
    configuration_id = ref_resp.json().get("properties", {}).get("configurationResourceId")
    if not configuration_id:
        raise CLIInternalError(
            f"Configuration reference for {hierarchy_id} has no configurationResourceId."
        )

    # Step 2: Resolve solution template unique identifier (used as dynamic config name)
    st_url = (
        f"{ARM_RESOURCE}/subscriptions/{sub_id}"
        f"/resourceGroups/{template_rg}"
        f"/providers/Microsoft.Edge/solutionTemplates/{template_name}"
        f"?api-version={API_VERSION}"
    )
    st_resp = send_raw_request(
        cmd.cli_ctx, "GET", st_url,
        headers=["Accept=application/json"],
        resource=ARM_RESOURCE,
    )
    if st_resp.status_code != 200:
        raise CLIInternalError(
            f"Solution template '{template_name}' not found in RG '{template_rg}' "
            f"(HTTP {st_resp.status_code})."
        )
    st_body = st_resp.json()
    dynamic_config_name = (
        st_body.get("properties", {}).get("uniqueIdentifier")
        or template_name
    )

    # Step 3: GET dynamic config version (check if it exists)
    version_url = (
        f"{ARM_RESOURCE}{configuration_id}"
        f"/dynamicConfigurations/{dynamic_config_name}"
        f"/versions/{template_version}"
        f"?api-version={API_VERSION}"
    )
    version_resp = send_raw_request(
        cmd.cli_ctx, "GET", version_url,
        headers=["Accept=application/json"],
        resource=ARM_RESOURCE,
    )

    if version_resp.status_code == 200:
        # Update existing dynamic config version
        existing = version_resp.json()
        existing["properties"]["values"] = config_content
        send_raw_request(
            cmd.cli_ctx, "PUT", version_url,
            body=json.dumps(existing),
            headers=["Content-Type=application/json", "Accept=application/json"],
            resource=ARM_RESOURCE,
        )
    elif version_resp.status_code == 404:
        # Create new: first ensure parent dynamic config exists
        dc_url = (
            f"{ARM_RESOURCE}{configuration_id}"
            f"/dynamicConfigurations/{dynamic_config_name}"
            f"?api-version={API_VERSION}"
        )
        dc_body = {"properties": {"currentVersion": template_version}}
        dc_resp = send_raw_request(
            cmd.cli_ctx, "PUT", dc_url,
            body=json.dumps(dc_body),
            headers=["Content-Type=application/json", "Accept=application/json"],
            resource=ARM_RESOURCE,
        )
        if dc_resp.status_code not in (200, 201):
            raise CLIInternalError(
                f"Failed to create dynamic configuration (HTTP {dc_resp.status_code}): "
                f"{dc_resp.text}"
            )

        # Then create the version with config values
        ver_body = {"properties": {"values": config_content}}
        ver_resp = send_raw_request(
            cmd.cli_ctx, "PUT", version_url,
            body=json.dumps(ver_body),
            headers=["Content-Type=application/json", "Accept=application/json"],
            resource=ARM_RESOURCE,
        )
        if ver_resp.status_code not in (200, 201):
            raise CLIInternalError(
                f"Failed to create dynamic configuration version (HTTP {ver_resp.status_code}): "
                f"{ver_resp.text}"
            )
    else:
        raise CLIInternalError(
            f"Failed to check dynamic configuration version (HTTP {version_resp.status_code}): "
            f"{version_resp.text}"
        )


def _read_config_file(file_path):
    """Read and return contents of a YAML/JSON config file."""
    import os
    if not os.path.isfile(file_path):
        raise ValidationError(f"Config file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# LRO and response helpers
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

    # Error
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
            poll_resp = send_raw_request(cmd.cli_ctx, "GET", location, resource=ARM_RESOURCE)
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


def _short_id(arm_id):
    """Return the last segment of an ARM ID for display."""
    if not arm_id:
        return ""
    parts = arm_id.strip("/").split("/")
    return parts[-1] if parts else arm_id
