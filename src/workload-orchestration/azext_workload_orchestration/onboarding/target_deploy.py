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

    # Resume from publish (already reviewed)
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --resume-from publish --solution-version-id <SV_ARM_ID>
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
    solution_template_rg=None,
    solution_instance_name=None,
    solution_dependencies=None,
    solution_version_id=None,
    resume_from=None,
    skip_review=False,
    skip_install=False,
    config=None,
    config_hierarchy_id=None,
    config_template_rg=None,
    config_template_name=None,
    config_template_version=None,
    no_wait=False,
):
    """Deploy a solution to a target: review -> publish -> install.

    Chains up to 4 steps (config-set + review + publish + install),
    passing the solution-version-id from review into publish and install.
    """
    sub_id = _get_subscription_id(cmd)

    # --- Validate resume-from (before template resolution) ---
    if resume_from:
        resume_from = resume_from.lower()
        if resume_from not in ("publish", "install"):
            raise ValidationError("--resume-from must be 'publish' or 'install'.")
        if not solution_version_id:
            raise ValidationError(
                "--solution-version-id is required when using --resume-from."
            )

    # --- Resolve solution-template-version-id (not needed for resume) ---
    if not resume_from:
        solution_template_version_id = _resolve_template_version_id(
            solution_template_version_id, solution_template_name,
            solution_template_version, solution_template_rg,
            resource_group, sub_id,
        )
    elif not solution_template_version_id:
        # resume_from is set, template version not required
        solution_template_version_id = None

    base_url = (
        f"{ARM_RESOURCE}/subscriptions/{sub_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Edge/targets/{target_name}"
    )

    # Figure out which steps to run
    do_config = config is not None
    do_review = (resume_from is None) and (not skip_review)
    do_publish = resume_from in (None, "publish") or skip_review
    do_install = (not skip_install) and (resume_from != "install" or resume_from == "install")

    # If resume_from == "install", skip review and publish
    if resume_from == "install":
        do_review = False
        do_publish = False
    elif resume_from == "publish":
        do_review = False

    total = sum([do_config, do_review, do_publish, do_install])
    step = [0]  # mutable counter

    def _step(name, status=""):
        step[0] += 1
        prefix = f"[{step[0]}/{total}]"
        if status:
            print(f"{prefix} {name}... {status}")
        else:
            print(f"{prefix} {name}...")

    results = {}
    sv_id = solution_version_id  # may be set by review or passed via --solution-version-id

    # --- Step 0: Config set ---
    if do_config:
        _step("Config Set")
        _handle_config_set(
            cmd, config, config_hierarchy_id, config_template_rg,
            config_template_name, config_template_version,
            resource_group, target_name, sub_id,
        )
        _step("Config Set", "[OK]")
        step[0] -= 1  # _step incremented twice; fix
        results["configSet"] = "Succeeded"

    # --- Step 1: Review ---
    if do_review:
        _step("Review")
        review_result = _do_review(
            cmd, base_url, solution_template_version_id,
            solution_instance_name, solution_dependencies,
        )
        results["review"] = review_result
        sv_id = _extract_solution_version_id(review_result)
        _step("Review", f"[OK] -> solutionVersionId: {_short_id(sv_id)}")
        step[0] -= 1
    elif not resume_from:
        print(f"[~] Review skipped (--skip-review)")
        results["review"] = "Skipped"
        sv_id = solution_template_version_id
    else:
        print(f"[~] Review skipped (--resume-from {resume_from})")
        results["review"] = "Skipped"

    if not sv_id:
        raise CLIInternalError("No solution-version-id available. Cannot proceed with publish.")

    # --- Step 2: Publish ---
    if do_publish:
        _step("Publish")
        publish_result = _do_publish(cmd, base_url, sv_id)
        results["publish"] = publish_result
        _step("Publish", "[OK]")
        step[0] -= 1
    else:
        print(f"[~] Publish skipped (--resume-from install)")
        results["publish"] = "Skipped"

    # --- Step 3: Install ---
    if do_install:
        _step("Install")
        install_result = _do_install(cmd, base_url, sv_id, no_wait=no_wait)
        results["install"] = install_result
        if no_wait:
            _step("Install", "[Accepted] (--no-wait)")
        else:
            _step("Install", "[OK]")
        step[0] -= 1
    else:
        print(f"[~] Install skipped (--skip-install)")
        results["install"] = "Skipped"

    print(f"\n{'=' * 50}")
    print(f"Deployment complete for target '{target_name}'")
    print(f"Solution Version ID: {sv_id}")
    print(f"{'=' * 50}")

    return {
        "targetName": target_name,
        "resourceGroup": resource_group,
        "solutionVersionId": sv_id,
        "solutionTemplateVersionId": solution_template_version_id,
        "steps": results,
    }


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
    arm_id, template_name, template_version, template_rg,
    default_rg, sub_id,
):
    """Resolve solution-template-version-id from friendly name or ARM ID.

    Mutual exclusivity:
      - Provide --solution-template-version-id (full ARM ID)
      - OR --solution-template-name + --solution-template-version (friendly)
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
        rg = template_rg or default_rg
        return (
            f"/subscriptions/{sub_id}/resourceGroups/{rg}"
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


def _do_install(cmd, base_url, solution_version_id, no_wait=False):
    """POST .../installSolution"""
    url = f"{base_url}/installSolution?api-version={API_VERSION}"
    body = {"solutionVersionId": solution_version_id}

    resp = send_raw_request(
        cmd.cli_ctx, "POST", url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
        resource=ARM_RESOURCE,
    )

    if no_wait:
        # Return 202 without polling
        if resp.status_code == 202:
            return {"status": "Accepted", "message": "Install triggered (no-wait)"}
        try:
            return resp.json()
        except Exception:
            return {"status": "Accepted"}

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
