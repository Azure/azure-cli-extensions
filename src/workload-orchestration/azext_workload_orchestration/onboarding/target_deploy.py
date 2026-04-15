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
    # Friendly name
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --solution-template-name tmpl --solution-template-version 1.0.0

    # ARM ID
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --solution-template-version-id <ARM_ID>

    # With config
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --solution-template-version-id <ARM_ID> \\
        --config values.yaml \\
        --config-template-rg rg --config-template-name tmpl --config-template-version 1.0.0
"""

import json
import logging

from azure.cli.core.azclierror import CLIInternalError, ValidationError
from azure.cli.core.util import send_raw_request

logger = logging.getLogger(__name__)

API_VERSION = "2025-08-01"
ARM_RESOURCE = "https://management.azure.com"


def target_deploy(
    cmd,
    resource_group,
    target_name,
    solution_template_version_id=None,
    solution_template_name=None,
    solution_template_version=None,
    solution_instance_name=None,
    solution_dependencies=None,
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
        solution_template_version_id, solution_template_name,
        solution_template_version, None,
        resource_group, sub_id,
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
            print(f"[{current[0]}/{total}] {step_name}... {status}")
        else:
            current[0] += 1
            print(f"[{current[0]}/{total}] {step_name}...")

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
        _log("Config Set", "[OK]")
        results["configSet"] = "Succeeded"

    # --- Step 1: Review ---
    _log("Review")
    review_result = _do_review(
        cmd, base_url, solution_template_version_id,
        solution_instance_name, solution_dependencies,
    )
    results["review"] = review_result
    sv_id = _extract_solution_version_id(review_result)
    _log("Review", f"[OK] -> solutionVersionId: {_short_id(sv_id)}")

    # --- Step 2: Publish ---
    _log("Publish")
    publish_result = _do_publish(cmd, base_url, sv_id)
    results["publish"] = publish_result
    _log("Publish", "[OK]")

    # --- Step 3: Install ---
    _log("Install")
    install_result = _do_install(cmd, base_url, sv_id)
    results["install"] = install_result
    _log("Install", "[OK]")

    print(f"\n{'=' * 50}")
    print(f"Deployment complete for target '{target_name}'")
    print(f"Solution Version ID: {sv_id}")
    print(f"{'=' * 50}")

    # Return the install LRO result (same format as `az wo target install`)
    return results.get("install", {
        "status": "Succeeded",
        "resourceId": f"{base_url}",
    })


def target_deploy_pre_install(
    cmd,
    resource_group,
    target_name,
    solution_template_version_id=None,
    solution_template_name=None,
    solution_template_version=None,
    solution_instance_name=None,
    solution_dependencies=None,
    config=None,
):
    """Run config-set → review → publish and return the solution-version-id.

    Called by the enhanced `target install` command before the AAZ install step.
    Does NOT run install — that's handled by the AAZ LRO.

    When using friendly name, the target's resource_group is used for the ST.
    Config-template args are auto-derived from solution template args.
    """
    sub_id = _get_subscription_id(cmd)

    solution_template_version_id = _resolve_template_version_id(
        solution_template_version_id, solution_template_name,
        solution_template_version, None,
        resource_group, sub_id,
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
            print(f"[{current[0]}/{total}] {step_name}... {status}")
        else:
            current[0] += 1
            print(f"[{current[0]}/{total}] {step_name}...")

    # --- Step 0: Config set ---
    if do_config:
        _log("Config Set")
        # Auto-derive config template args from solution template args
        ct_rg = solution_template_rg or resource_group
        ct_name = solution_template_name
        ct_version = solution_template_version

        # If using ARM ID, extract name/version/rg from it
        if not ct_name and solution_template_version_id:
            parts = solution_template_version_id.strip("/").split("/")
            # .../resourceGroups/{rg}/providers/Microsoft.Edge/solutionTemplates/{name}/versions/{ver}
            for i, part in enumerate(parts):
                if part.lower() == "resourcegroups" and i + 1 < len(parts):
                    ct_rg = parts[i + 1]
                elif part.lower() == "solutiontemplates" and i + 1 < len(parts):
                    ct_name = parts[i + 1]
                elif part.lower() == "versions" and i + 1 < len(parts):
                    ct_version = parts[i + 1]

        _handle_config_set(
            cmd, config, None, ct_rg,
            ct_name, ct_version,
            resource_group, target_name, sub_id,
        )
        _log("Config Set", "[OK]")

    # --- Step 1: Review ---
    _log("Review")
    review_result = _do_review(
        cmd, base_url, solution_template_version_id,
        solution_instance_name, solution_dependencies,
    )
    sv_id = _extract_solution_version_id(review_result)
    _log("Review", f"[OK] -> solutionVersionId: {_short_id(sv_id)}")

    # --- Step 2: Publish ---
    _log("Publish")
    _do_publish(cmd, base_url, sv_id)
    _log("Publish", "[OK]")

    # Step 3 (Install) is handled by AAZ LRO
    _log("Install")

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
    arm_id, template_name, template_version, _unused,
    default_rg, sub_id,
):
    """Resolve solution-template-version-id from friendly name or ARM ID.

    Mutual exclusivity:
      - Provide --solution-template-version-id (full ARM ID)
      - OR --solution-template-name + --solution-template-version (friendly)

    When using friendly name, the target's resource group is used.
    """
    if arm_id and template_name:
        raise ValidationError(
            "Provide either --solution-template-version-id OR "
            "(--solution-template-name + --solution-template-version), not both."
        )

    if arm_id:
        return arm_id

    if template_name:
        if not template_version:
            raise ValidationError(
                "--solution-template-version is required when using --solution-template-name."
            )
        return (
            f"/subscriptions/{sub_id}/resourceGroups/{default_rg}"
            f"/providers/Microsoft.Edge/solutionTemplates/{template_name}"
            f"/versions/{template_version}"
        )

    raise ValidationError(
        "Provide either --solution-template-version-id or "
        "(--solution-template-name + --solution-template-version)."
    )


# ---------------------------------------------------------------------------
# Step implementations
# ---------------------------------------------------------------------------

def _do_review(cmd, base_url, solution_template_version_id,
               solution_instance_name=None, solution_dependencies=None):
    """POST .../reviewSolutionVersion"""
    url = f"{base_url}/reviewSolutionVersion?api-version={API_VERSION}"
    body = {
        "solutionTemplateVersionId": solution_template_version_id,
    }
    if solution_instance_name:
        body["solutionInstanceName"] = solution_instance_name
    if solution_dependencies:
        body["solutionDependencies"] = (
            json.loads(solution_dependencies)
            if isinstance(solution_dependencies, str)
            else solution_dependencies
        )

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

    Delegates to: az workload-orchestration configuration set
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

    from azext_workload_orchestration.onboarding.utils import invoke_cli_command
    invoke_cli_command(cmd, [
        "workload-orchestration", "configuration", "set",
        "--hierarchy-id", hierarchy_id,
        "--template-rg", template_rg,
        "--template-name", template_name,
        "--version", template_version,
        "--file", config_file,
        "--solution",
    ], expect_json=False)


# ---------------------------------------------------------------------------
# LRO and response helpers
# ---------------------------------------------------------------------------

def _parse_response(resp, step_name, cmd=None):
    """Parse REST response, handling 200/201/202 LRO patterns."""
    status = resp.status_code
    if status in (200, 201):
        try:
            return resp.json()
        except Exception:
            return {"status": "Succeeded"}
    if status == 202:
        return _poll_lro(resp, step_name, cmd=cmd)

    # Error
    try:
        error_body = resp.text
    except Exception:
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
        except Exception:
            logger.debug("LRO poll attempt %d failed for %s", i + 1, step_name)
            continue

        try:
            body = poll_resp.json()
        except Exception:
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
        logger.warning("Could not extract solutionVersionId. Keys at top: %s, inner keys: %s, full (truncated): %s",
                        list(review_result.keys()),
                        list(inner.keys()) if isinstance(inner, dict) else "N/A",
                        json.dumps(review_result, indent=2)[:800])
        raise CLIInternalError(
            "Review succeeded but no solutionVersionId found in response. "
            "Use --resume-from publish --solution-version-id <id> to continue manually."
        )
    return sv_id


def _short_id(arm_id):
    """Return the last segment of an ARM ID for display."""
    if not arm_id:
        return ""
    parts = arm_id.strip("/").split("/")
    return parts[-1] if parts else arm_id
