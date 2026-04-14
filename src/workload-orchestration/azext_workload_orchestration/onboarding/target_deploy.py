# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Target deploy command - chains review → publish → install in one step.

Replaces 3 manual commands:
  1. az workload-orchestration target review
  2. az workload-orchestration target publish
  3. az workload-orchestration target install

Usage:
    az workload-orchestration target deploy \\
        -g my-rg -n my-target \\
        --solution-template-version-id <ARM_ID>
"""

import json
import logging

from azure.cli.core.azclierror import CLIInternalError, ValidationError
from azure.cli.core.util import send_raw_request

logger = logging.getLogger(__name__)

TOTAL_STEPS = 3
API_VERSION = "2025-08-01"
ARM_RESOURCE = "https://management.azure.com"


def target_deploy(
    cmd,
    resource_group,
    target_name,
    solution_template_version_id,
    solution_instance_name=None,
    skip_review=False,
    skip_install=False,
    config_file=None,
    config_hierarchy_id=None,
    config_template_rg=None,
    config_template_name=None,
    config_template_version=None,
):
    """Deploy a solution to a target: review → publish → install.

    Chains the 3 LRO operations, passing the solution-version-id
    from review output into publish and install automatically.
    """
    sub_id = cmd.cli_ctx.data.get('subscription_id')
    if not sub_id:
        from azure.cli.core._profile import Profile
        sub_id = Profile(cli_ctx=cmd.cli_ctx).get_subscription_id()

    base_url = (
        f"https://management.azure.com/subscriptions/{sub_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Edge/targets/{target_name}"
    )

    results = {}

    # Optional Step 0: Set configuration before review
    if config_file:
        _handle_config_set(
            cmd, config_file, config_hierarchy_id, config_template_rg,
            config_template_name, config_template_version,
            resource_group, target_name, sub_id,
        )

    # Step 1: Review
    if skip_review:
        _print_step(1, "Review", "Skipped (--skip-review)")
        results["review"] = "Skipped"
        # Without review, user must know the solution-version-id already
        # We'll use the solution-template-version-id for publish directly
        solution_version_id = solution_template_version_id
    else:
        _print_step(1, "Review")
        review_result = _do_review(
            cmd, base_url, solution_template_version_id, solution_instance_name,
        )
        results["review"] = review_result
        solution_version_id = _extract_solution_version_id(review_result)
        _print_step(1, "Review", f"[OK] → version: {_short_id(solution_version_id)}")

    # Step 2: Publish
    _print_step(2, "Publish")
    publish_result = _do_publish(cmd, base_url, solution_version_id)
    results["publish"] = publish_result
    _print_step(2, "Publish", "[OK]")

    # Step 3: Install
    if skip_install:
        _print_step(3, "Install", "Skipped (--skip-install)")
        results["install"] = "Skipped"
    else:
        _print_step(3, "Install")
        install_result = _do_install(cmd, base_url, solution_version_id)
        results["install"] = install_result
        _print_step(3, "Install", "[OK]")

    print(f"\n[OK] Deployment complete for target '{target_name}'")
    return {
        "targetName": target_name,
        "solutionVersionId": solution_version_id,
        "steps": results,
    }


# ---------------------------------------------------------------------------
# Step implementations
# ---------------------------------------------------------------------------

def _do_review(cmd, base_url, solution_template_version_id, solution_instance_name):
    """POST .../reviewSolutionVersion — validates config and creates a solution version."""
    url = f"{base_url}/reviewSolutionVersion?api-version={API_VERSION}"
    body = {
        "solutionTemplateVersionId": solution_template_version_id,
    }
    if solution_instance_name:
        body["solutionInstanceName"] = solution_instance_name

    resp = send_raw_request(
        cmd.cli_ctx, "POST", url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
        resource=ARM_RESOURCE,
    )
    return _parse_response(resp, "review", cmd=cmd)


def _do_publish(cmd, base_url, solution_version_id):
    """POST .../publishSolutionVersion — publishes the reviewed solution."""
    url = f"{base_url}/publishSolutionVersion?api-version={API_VERSION}"
    body = {"solutionVersionId": solution_version_id}

    resp = send_raw_request(
        cmd.cli_ctx, "POST", url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
        resource=ARM_RESOURCE,
    )
    return _parse_response(resp, "publish", cmd=cmd)


def _do_install(cmd, base_url, solution_version_id):
    """POST .../installSolution — installs the published solution on target."""
    url = f"{base_url}/installSolution?api-version={API_VERSION}"
    body = {"solutionVersionId": solution_version_id}

    resp = send_raw_request(
        cmd.cli_ctx, "POST", url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
        resource=ARM_RESOURCE,
    )
    return _parse_response(resp, "install", cmd=cmd)


def _handle_config_set(
    cmd, config_file, hierarchy_id, template_rg,
    template_name, template_version,
    resource_group, target_name, sub_id,
):
    """Optional: set configuration values from file before review."""
    from azext_workload_orchestration.onboarding.utils import invoke_cli_command

    if not hierarchy_id:
        hierarchy_id = (
            f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Edge/targets/{target_name}"
        )

    if not template_rg or not template_name or not template_version:
        raise ValidationError(
            "When using --config-file, you must also provide "
            "--config-template-rg, --config-template-name, and --config-template-version."
        )

    print(f"[0/{TOTAL_STEPS}] Setting configuration from '{config_file}'...")
    invoke_cli_command(cmd, [
        "workload-orchestration", "configuration", "set",
        "--hierarchy-id", hierarchy_id,
        "--template-rg", template_rg,
        "--template-name", template_name,
        "--version", template_version,
        "--file", config_file,
    ], expect_json=False)
    print(f"[0/{TOTAL_STEPS}] Configuration set [OK]")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_response(resp, step_name, cmd=None):
    """Parse a REST response, handling 200/202 LRO patterns."""
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
    raise CLIInternalError(f"{step_name} failed: {error_body}")


def _poll_lro(resp, step_name, cmd=None):
    """Poll an LRO until terminal state."""
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
            logger.debug("LRO poll attempt %d failed for %s", i, step_name)
            continue

        try:
            body = poll_resp.json()
        except Exception:
            continue

        status = body.get("status", "").lower()
        if status in ("succeeded", "completed"):
            return body
        if status in ("failed", "canceled", "cancelled"):
            raise CLIInternalError(
                f"{step_name} LRO failed: {json.dumps(body, indent=2)}"
            )

    raise CLIInternalError(f"{step_name} LRO timed out after {max_polls * retry_after}s")


def _extract_solution_version_id(review_result):
    """Extract solution-version-id from review response."""
    if not review_result or not isinstance(review_result, dict):
        raise CLIInternalError("Review returned no result — cannot determine solution version ID.")

    # The review response may have the ID at different paths
    sv_id = (
        review_result.get("solutionVersionId")
        or review_result.get("properties", {}).get("solutionVersionId")
        or review_result.get("id")
    )
    if not sv_id:
        logger.warning("Could not extract solutionVersionId from review result: %s",
                        json.dumps(review_result, indent=2)[:500])
        raise CLIInternalError(
            "Review succeeded but no solutionVersionId found in response. "
            "Pass --skip-review and provide the solution-version-id directly via "
            "--solution-template-version-id if you already have a reviewed version."
        )
    return sv_id


def _short_id(arm_id):
    """Return just the resource name from an ARM ID for display."""
    if not arm_id:
        return ""
    parts = arm_id.strip("/").split("/")
    return parts[-1] if parts else arm_id


def _print_step(step_num, name, status=""):
    """Print formatted step output."""
    prefix = f"[{step_num}/{TOTAL_STEPS}]"
    if status:
        print(f"{prefix} {name}... {status}")
    else:
        print(f"{prefix} {name}...")
