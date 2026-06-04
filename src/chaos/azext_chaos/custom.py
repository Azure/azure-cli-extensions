# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import time

from azure.cli.core.aaz import has_value
from azure.cli.core.util import send_raw_request
from knack.log import get_logger
from knack.util import CLIError

from .aaz.latest.chaos.scenario.config._create import Create as _ScenarioConfigCreate

logger = get_logger(__name__)

# Substring pattern emitted by BE's evaluation-state gate
# (StartScenarioValidationCommand / StartScenarioExecutionCommand).
_EVALUATION_NOT_READY_PATTERN = "not evaluated yet"


_LRO_TERMINAL_STATES = {"Succeeded", "Failed", "Cancelled", "Canceled"}
_LRO_POLL_INTERVAL_SECONDS = 5
_LRO_TIMEOUT_SECONDS = 600  # 10 min default


def _poll_or_return(cmd, response):
    """Dispatch a raw HTTP response: return body for 200, poll for 201/202, raise on error."""
    if response.status_code == 200:
        return response.json() if response.text else None
    if response.status_code in (201, 202):
        return _poll_lro(cmd, response)
    try:
        error_body = response.json()
        message = error_body.get("error", {}).get("message", response.text)
    except Exception:  # pylint: disable=broad-except
        message = response.text or f"HTTP {response.status_code}"
    raise CLIError(f"Request failed ({response.status_code}): {message}")


def _poll_lro(cmd, initial_response):
    """Choose polling strategy based on LRO headers."""
    headers = initial_response.headers
    async_url = headers.get("Azure-AsyncOperation")
    location_url = headers.get("Location")
    try:
        retry_after = int(headers.get("Retry-After", _LRO_POLL_INTERVAL_SECONDS))
    except (ValueError, TypeError):
        retry_after = _LRO_POLL_INTERVAL_SECONDS
    if async_url:
        return _poll_async_operation(cmd, async_url, location_url, retry_after)
    if location_url:
        return _poll_location(cmd, location_url, retry_after)
    return initial_response.json() if initial_response.text else None


def _poll_async_operation(cmd, poll_url, location_url, retry_after):
    """Poll Azure-AsyncOperation URL until terminal status."""
    elapsed = 0
    while elapsed < _LRO_TIMEOUT_SECONDS:
        time.sleep(retry_after)
        elapsed += retry_after
        poll_resp = send_raw_request(cmd.cli_ctx, "GET", poll_url)
        body = poll_resp.json() if poll_resp.text else {}
        status = body.get("status", "")
        try:
            retry_after = int(poll_resp.headers.get("Retry-After", retry_after))
        except (ValueError, TypeError):
            pass  # keep current retry_after
        if status in _LRO_TERMINAL_STATES:
            if status != "Succeeded":
                err = body.get("error", {})
                msg = err.get("message", f"LRO terminated with status: {status}")
                raise CLIError(msg)
            if location_url:
                final = send_raw_request(cmd.cli_ctx, "GET", location_url)
                return final.json() if final.text else body
            return body
    raise CLIError(f"Long-running operation timed out after {_LRO_TIMEOUT_SECONDS}s.")


def _poll_location(cmd, poll_url, retry_after):
    """Poll Location URL until non-202 response."""
    elapsed = 0
    while elapsed < _LRO_TIMEOUT_SECONDS:
        time.sleep(retry_after)
        elapsed += retry_after
        poll_resp = send_raw_request(cmd.cli_ctx, "GET", poll_url)
        if poll_resp.status_code == 200:
            return poll_resp.json() if poll_resp.text else None
        if poll_resp.status_code != 202:
            try:
                error_body = poll_resp.json()
                msg = error_body.get("error", {}).get("message", poll_resp.text)
            except Exception:  # pylint: disable=broad-except
                msg = poll_resp.text or f"HTTP {poll_resp.status_code}"
            raise CLIError(f"LRO poll failed ({poll_resp.status_code}): {msg}")
        try:
            retry_after = int(poll_resp.headers.get("Retry-After", retry_after))
        except (ValueError, TypeError):
            pass  # keep current retry_after
    raise CLIError(f"Long-running operation timed out after {_LRO_TIMEOUT_SECONDS}s.")


def _build_arm_url(cmd, resource_group, workspace, path_suffix):
    """Build a fully qualified ARM URL for a workspace-scoped sub-resource."""
    from azure.cli.core.commands.client_factory import get_subscription_id
    sub = get_subscription_id(cmd.cli_ctx)
    return (
        f"/subscriptions/{sub}/resourceGroups/{resource_group}"
        f"/providers/Microsoft.Chaos/workspaces/{workspace}"
        f"{path_suffix}"
        f"?api-version=2026-05-01-preview"
    )


def _is_evaluation_error(error_text):
    """Check if an error message indicates the workspace evaluation gate."""
    if not error_text:
        return False
    return _EVALUATION_NOT_READY_PATTERN in error_text.lower()


def _make_evaluation_hint(workspace, resource_group, context_suffix=""):
    """Build the friendly hint for evaluation-state errors."""
    hint = (
        f"Workspace has not been evaluated. "
        f"Run `az chaos workspace refresh-recommendations "
        f"--name {workspace} --resource-group {resource_group}` "
        f"(or its alias `az chaos workspace evaluate-scenarios`) "
        f"to (re)trigger evaluation, or "
        f"`az chaos workspace show-evaluation "
        f"--name {workspace} --resource-group {resource_group}` "
        f"to inspect the current evaluation state without triggering a new one."
    )
    if context_suffix:
        hint += f" {context_suffix}"
    return hint


# ── workspace refresh-recommendations────────────────────────────────────

# Inner LROs that complete via the outer refreshRecommendations LRO. After the
# outer call reports terminal, the BE has written results to these singletons.
# A common silent failure is Azure Resource Graph propagation lag: discovery
# 403s but the outer LRO still completes. We surface those inner failures so
# the user gets a non-zero exit, not a misleading green message.
_INNER_LRO_FAILURE_HINT = (
    "This commonly happens immediately after a Reader role assignment is "
    "added to the workspace's managed identity: Azure Resource Graph can "
    "lag 1-3 minutes before honoring the new role. Wait ~60-180s and re-run "
    "'refresh-recommendations'. If it persists, run "
    "'az chaos workspace show-discovery' / 'show-evaluation' for full error "
    "detail and verify the workspace UAMI has Reader on all in-scope scopes."
)


def _check_inner_lro(cmd, resource_group_name, workspace_name, path_suffix,
                     operation_label):
    """Fetch a /latest singleton and raise if its inner status is Failed.

    Returns silently for any other state (Succeeded, in-progress, no result
    yet, or endpoint not reachable). We only flip to non-zero exit when the
    inner result is unambiguously Failed.
    """
    url = _build_arm_url(cmd, resource_group_name, workspace_name, path_suffix)
    try:
        response = send_raw_request(cmd.cli_ctx, "GET", url)
    except Exception:  # pylint: disable=broad-except
        return  # /latest may legitimately 404 on a fresh workspace
    if response.status_code != 200 or not response.text:
        return
    try:
        body = response.json()
    except Exception:  # pylint: disable=broad-except
        return
    props = body.get("properties") or {}
    status = props.get("status", "")
    if status != "Failed":
        return
    # Surface the inner failure
    errors = props.get("errors") or []
    if errors:
        first = errors[0]
        code = first.get("errorCode") or first.get("code") or "Unknown"
        message = first.get("errorMessage") or first.get("message") or ""
        detail = f"{code}: {message}".strip(": ")
    else:
        detail = "no error detail returned by the service"
    raise CLIError(
        f"refresh-recommendations completed but the inner "
        f"{operation_label} operation Failed ({detail}). "
        f"{_INNER_LRO_FAILURE_HINT}"
    )


def workspace_refresh_recommendations(cmd, resource_group_name, workspace_name,
                                      no_wait=False):
    """POST + poll LRO for workspace refresh-recommendations."""
    url = _build_arm_url(
        cmd, resource_group_name, workspace_name, "/refreshRecommendations"
    )
    response = send_raw_request(cmd.cli_ctx, "POST", url)

    if no_wait:
        return response.json() if response.text else None

    # Poll to completion
    _poll_or_return(cmd, response)

    # Even when the outer LRO reports Succeeded, the inner discovery and
    # evaluation LROs may have failed (typically Azure Resource Graph 403
    # during propagation lag after a fresh role assignment). Check both
    # before declaring success.
    _check_inner_lro(
        cmd, resource_group_name, workspace_name,
        "/discoveries/latest", "resource discovery",
    )
    _check_inner_lro(
        cmd, resource_group_name, workspace_name,
        "/evaluations/latest", "scenario evaluation",
    )

    logger.warning(
        "Successfully refreshed recommendations for workspace '%s' "
        "in resource group '%s'. Workspace evaluation has been refreshed; "
        "subsequent 'scenario config validate' / 'scenario run start' calls "
        "(for non-custom scenarios) now have a satisfied evaluation gate.\n"
        "Run 'az chaos scenario list -w %s -g %s' to see updated "
        "recommendation statuses.",
        workspace_name, resource_group_name,
        workspace_name, resource_group_name,
    )
    return None


# ── scenario config validate ─────────────────────────────────────────────

def scenario_config_validate(cmd, resource_group_name, workspace_name,  # pylint: disable=too-many-positional-arguments
                             scenario_name, scenario_configuration_name,
                             no_wait=False):
    """POST validate + poll LRO + auto-GET validations/latest."""
    validate_url = _build_arm_url(
        cmd, resource_group_name, workspace_name,
        f"/scenarios/{scenario_name}"
        f"/configurations/{scenario_configuration_name}/validate"
    )
    response = send_raw_request(cmd.cli_ctx, "POST", validate_url)

    if no_wait:
        logger.warning(
            "Validation submitted. Use 'az chaos scenario config show-validation "
            "--workspace-name %s --resource-group %s --scenario-name %s "
            "--name %s' to retrieve the result once the operation completes.",
            workspace_name, resource_group_name, scenario_name,
            scenario_configuration_name,
        )
        return response.json() if response.text else None

    # Poll LRO to completion
    _poll_or_return(cmd, response)

    # Auto-GET validations/latest
    latest_url = _build_arm_url(
        cmd, resource_group_name, workspace_name,
        f"/scenarios/{scenario_name}"
        f"/configurations/{scenario_configuration_name}"
        f"/validations/latest"
    )
    latest_response = send_raw_request(cmd.cli_ctx, "GET", latest_url)
    result = latest_response.json()

    # Check for non-success status (aligned with scenario_run_start behavior)
    status = (result.get("properties") or {}).get("status", "")
    if status != "Succeeded":
        _check_evaluation_error_in_validation(result, workspace_name,
                                              resource_group_name)

    return result


def _check_evaluation_error_in_validation(result, workspace, resource_group):
    """Check validation result for evaluation-state errors and raise with hint."""
    props = result.get("properties") or {}
    # Check system errors
    for err in (props.get("errors") or []):
        msg = err.get("message", "")
        if _is_evaluation_error(msg):
            raise CLIError(
                _make_evaluation_hint(workspace, resource_group)
            )
    # Check validation errors
    val_errors = (props.get("validationErrors") or {}).get("errors") or []
    for err in val_errors:
        msg = err.get("message", "")
        if _is_evaluation_error(msg):
            raise CLIError(
                _make_evaluation_hint(workspace, resource_group)
            )


# ── scenario run start ───────────────────────────────────────────────────

def scenario_run_start(cmd, resource_group_name, workspace_name,  # pylint: disable=too-many-positional-arguments
                       scenario_name, scenario_configuration_name,
                       skip_validation=False, no_wait=False):
    """Execute a scenario configuration with optional pre-flight validation."""
    from azext_chaos._table_format import validation_show_table_format

    # Pre-flight validation (unless --skip-validation)
    if not skip_validation:
        validate_url = _build_arm_url(
            cmd, resource_group_name, workspace_name,
            f"/scenarios/{scenario_name}"
            f"/configurations/{scenario_configuration_name}/validate"
        )
        val_response = send_raw_request(cmd.cli_ctx, "POST", validate_url)

        # Always poll validation to completion, even with --no-wait
        _poll_or_return(cmd, val_response)

        # GET validations/latest
        latest_url = _build_arm_url(
            cmd, resource_group_name, workspace_name,
            f"/scenarios/{scenario_name}"
            f"/configurations/{scenario_configuration_name}"
            f"/validations/latest"
        )
        latest_response = send_raw_request(cmd.cli_ctx, "GET", latest_url)
        val_result = latest_response.json()

        val_status = (val_result.get("properties") or {}).get("status", "")
        if val_status != "Succeeded":
            # Check for evaluation-state error first
            _check_evaluation_error_in_validation(
                val_result, workspace_name, resource_group_name
            )
            # Render validation errors and exit non-zero
            table = validation_show_table_format(val_result)
            logger.error("Pre-flight validation failed:")
            logger.error("  Status: %s", table.get("Status", "Unknown"))
            if table.get("Errors"):
                logger.error("  Errors: %s", table["Errors"])
            raise CLIError(
                f"Validation failed for configuration "
                f"'{scenario_configuration_name}'. Fix the reported errors "
                f"before running the scenario."
            )

    # Execute
    execute_url = _build_arm_url(
        cmd, resource_group_name, workspace_name,
        f"/scenarios/{scenario_name}"
        f"/configurations/{scenario_configuration_name}/execute"
    )
    exec_response = send_raw_request(cmd.cli_ctx, "POST", execute_url)

    if no_wait:
        # Parse run ID from Location header. Two paths observed in production:
        #   - Resource URL pointing at .../scenarioRuns/{runId} → parse it.
        #   - Operation-status URL → do a single GET on Azure-AsyncOperation
        #     and read the runId from the body.
        location = exec_response.headers.get("Location", "")
        async_op = exec_response.headers.get("Azure-AsyncOperation", "")
        run_id = _extract_run_id_from_location(location)
        if not run_id:
            run_id = _fetch_run_id_from_async_op(cmd, async_op or location)

        if run_id:
            logger.warning(
                "Scenario run started (run ID: %s). "
                "Run 'az chaos scenario run show --workspace-name %s "
                "--resource-group %s --scenario-name %s --run-id %s' "
                "to check status.",
                run_id, workspace_name, resource_group_name,
                scenario_name, run_id,
            )
        else:
            logger.warning(
                "Scenario run started, but the run ID could not be parsed "
                "from the Location/Azure-AsyncOperation header. "
                "Run 'az chaos scenario run list --workspace-name %s "
                "--resource-group %s --scenario-name %s' to recover it "
                "(the most recent entry is yours).",
                workspace_name, resource_group_name, scenario_name,
            )
        # Always return a parseable shape so `-o json` is never empty.
        return {
            "runId": run_id,
            "operationStatusUrl": async_op or location or None,
        }

    # Poll execute LRO to completion
    run_result = _poll_or_return(cmd, exec_response)

    # Extract run ID from the completed ScenarioRun resource
    if isinstance(run_result, dict):
        run_id = run_result.get("name", "")
    else:
        run_id = ""

    if run_id:
        logger.warning(
            "Scenario run started successfully (run ID: %s). "
            "Run 'az chaos scenario run show --workspace-name %s "
            "--resource-group %s --scenario-name %s --run-id %s' "
            "to check status.",
            run_id, workspace_name, resource_group_name,
            scenario_name, run_id,
        )

    return run_result


def _extract_run_id_from_location(location_url):
    """Parse the run ID from a Location header URL.

    Handles two common shapes observed for ScenarioRuns_Execute:

    1. Resource URL:    .../scenarios/{s}/scenarioRuns/{runId}?api-version=...
                        .../scenarios/{s}/runs/{runId}?api-version=...
    2. Operation URL:   .../locations/{region}/operationResults/{opId}?...

    For (1) the run id is the segment after `scenarioRuns` (or legacy `runs`).
    For (2) we cannot derive the run id from the URL alone — return None and
    let the caller surface the operation URL as a fallback.
    """
    if not location_url:
        return None
    try:
        clean_url = location_url.split("?", 1)[0]
        segments = [s for s in clean_url.strip("/").split("/") if s]
        # Prefer the more specific marker; fall back to legacy `runs` segment.
        for marker in ("scenarioRuns", "runs"):
            if marker in segments:
                idx = segments.index(marker)
                if idx + 1 < len(segments):
                    return segments[idx + 1]
        return None
    except (ValueError, AttributeError):
        return None


def _fetch_run_id_from_async_op(cmd, async_op_url):
    """One-shot GET of an Azure-AsyncOperation URL to extract a runId.

    Used as a fallback for --no-wait when the Location header is an
    operation-status URL rather than a resource URL. We do a SINGLE GET (no
    polling loop) — the body may report InProgress, but it commonly already
    contains the resulting runId in either properties.runId / properties.name
    or the operation name itself.
    """
    if not async_op_url:
        return None
    try:
        resp = send_raw_request(cmd.cli_ctx, "GET", async_op_url)
        if resp.status_code != 200 or not resp.text:
            return None
        body = resp.json() or {}
    except Exception:  # pylint: disable=broad-except
        return None
    props = body.get("properties") or {}
    return (
        props.get("runId")
        or props.get("scenarioRunId")
        or props.get("name")
        or body.get("name")
    )


# ── singleton "latest result" GETs ───────────────────────────────────────
# These four endpoints are intentionally NOT in the public swagger by ARM policy:
# `/latest` paths are polling endpoints, not real GETs, and including them in
# the OpenAPI spec confuses customers and SDK generation. They live in the GW
# resource models (preserved for future api-versions by ADO PR #15743714) and
# are served by the BE controllers below. URLs are taken from those controller
# routes (services/BE/src/Chaos.Workspaces.Api/Controllers/):
#   - ScenarioConfigurationsController.cs
#       [HttpGet("{scenarioConfigurationId}/validations/latest")]
#       [HttpGet("{scenarioConfigurationId}/fixResourcePermissions/latest")]
#   - ResourceDiscoveryOperationsController.cs
#       [HttpGet("latest")]  (under /workspaces/{id}/discoveries)
#   - ScenarioEvaluationOperationsController.cs
#       [HttpGet("latest")]  (under /workspaces/{id}/evaluations)
# These custom wrappers are the permanent CLI surface for these reads — they
# will not be replaced by aaz-generated commands in a future api-version.


def workspace_show_discovery(cmd, resource_group_name, workspace_name):
    """GET the latest workspace-scope resource-discovery operation result."""
    url = _build_arm_url(
        cmd, resource_group_name, workspace_name, "/discoveries/latest"
    )
    response = send_raw_request(cmd.cli_ctx, "GET", url)
    return response.json() if response.text else None


def workspace_show_evaluation(cmd, resource_group_name, workspace_name):
    """GET the latest workspace scenario-evaluation operation result."""
    url = _build_arm_url(
        cmd, resource_group_name, workspace_name, "/evaluations/latest"
    )
    response = send_raw_request(cmd.cli_ctx, "GET", url)
    return response.json() if response.text else None


def scenario_config_show_validation(cmd, resource_group_name, workspace_name,
                                    scenario_name, scenario_configuration_name):
    """GET the latest validation result for a scenario configuration."""
    url = _build_arm_url(
        cmd, resource_group_name, workspace_name,
        f"/scenarios/{scenario_name}"
        f"/configurations/{scenario_configuration_name}"
        f"/validations/latest"
    )
    response = send_raw_request(cmd.cli_ctx, "GET", url)
    return response.json() if response.text else None


def scenario_config_show_permission_fix(cmd, resource_group_name, workspace_name,
                                        scenario_name, scenario_configuration_name):
    """GET the latest permission-fix result for a scenario configuration.

    The response body carries `properties.whatIfMode` indicating whether the
    latest fix was a what-if dry run or an actual fix — there is no separate
    "show the last what-if" query; the singleton-latest GET returns whichever
    fix was most recently submitted. To preview without applying, use
    `az chaos scenario config fix-permissions --what-if` (POST side).
    """
    url = _build_arm_url(
        cmd, resource_group_name, workspace_name,
        f"/scenarios/{scenario_name}"
        f"/configurations/{scenario_configuration_name}"
        f"/fixResourcePermissions/latest"
    )
    response = send_raw_request(cmd.cli_ctx, "GET", url)
    return response.json() if response.text else None


# ── scenario config fix-permissions ──────────────────────────────────────
# Overrides the aaz-generated command. The generated version uses
# `final-state-via: location` against the SAS-signed /fixResourcePermissions
# /latest Location header; the AAZ runtime mangles that URL on polling and
# returns a misleading 404 even when the role assignment succeeded server-
# side. Mirroring the validate/refresh-recommendations pattern (POST + own
# _poll_or_return + GET /latest) avoids the AAZ poller entirely.

def scenario_config_fix_permissions(cmd, resource_group_name, workspace_name,  # pylint: disable=too-many-positional-arguments
                                    scenario_name, scenario_configuration_name,
                                    what_if=False, no_wait=False):
    """POST fixResourcePermissions + poll LRO + auto-GET fixResourcePermissions/latest."""
    logger.info(
        "fix-permissions requires that the workspace, scenario, and "
        "configuration all exist. If you receive a 404 NotFound error, "
        "verify: (1) the workspace '%s' exists in resource group '%s'; "
        "(2) the scenario '%s' exists under that workspace; "
        "(3) the configuration '%s' exists under that scenario. "
        "Run 'az chaos scenario config show' to confirm the "
        "configuration exists before calling fix-permissions.",
        workspace_name, resource_group_name, scenario_name,
        scenario_configuration_name,
    )
    fix_url = _build_arm_url(
        cmd, resource_group_name, workspace_name,
        f"/scenarios/{scenario_name}"
        f"/configurations/{scenario_configuration_name}/fixResourcePermissions"
    )
    body = json.dumps({"whatIf": bool(what_if)})
    response = send_raw_request(
        cmd.cli_ctx, "POST", fix_url,
        body=body,
        headers=["Content-Type=application/json"],
    )

    if no_wait:
        logger.warning(
            "Permission fix submitted. Use 'az chaos scenario config "
            "show-permission-fix --workspace-name %s --resource-group %s "
            "--scenario-name %s --name %s' to retrieve the result once the "
            "operation completes.",
            workspace_name, resource_group_name, scenario_name,
            scenario_configuration_name,
        )
        return response.json() if response.text else None

    # Poll LRO to completion via Azure-AsyncOperation header (avoids the
    # AAZ-poller behavior of GET-ing the SAS-signed Location URL).
    _poll_or_return(cmd, response)

    # Auto-GET fixResourcePermissions/latest under our own ARM URL (we
    # control the api-version query param; no SAS-stripping).
    return scenario_config_show_permission_fix(
        cmd, resource_group_name, workspace_name,
        scenario_name, scenario_configuration_name,
    )


# ── scenario run cancel ──────────────────────────────────────────────────

def scenario_run_cancel(cmd, resource_group_name, workspace_name,  # pylint: disable=too-many-positional-arguments
                        scenario_name, run_id, no_wait=False):
    """POST cancel + poll LRO for a scenario run."""
    url = _build_arm_url(
        cmd, resource_group_name, workspace_name,
        f"/scenarios/{scenario_name}/runs/{run_id}/cancel"
    )
    response = send_raw_request(cmd.cli_ctx, "POST", url)

    if no_wait:
        return response.json() if response.text else None

    _poll_or_return(cmd, response)

    logger.warning(
        "Successfully cancelled scenario run '%s' for scenario '%s' "
        "in workspace '%s' (resource group '%s').",
        run_id, scenario_name, workspace_name, resource_group_name,
    )
    return None


# ── AAZCommand subclass overrides ────────────────────────────────────────
# Subclassing keeps the aaz-generated module pristine (no hand-edits under
# azext_chaos/aaz/) while letting us inject pre/post-operation behavior.
# Pattern reference: Azure/azure-cli-extensions:src/connectedmachine
# /azext_connectedmachine/custom.py — subclass + register in commands.py.

class ScenarioConfigCreate(_ScenarioConfigCreate):
    """Override `chaos scenario config create` to auto-derive ``--scenario-id``.

    The ARM resource ID for a scenario is deterministic from the other
    args (subscription, resource group, workspace, scenario name), so
    requiring users to type the full ID is poor UX. When the caller did
    not supply ``--scenario-id`` we synthesize it before the request
    builder reads ``args.scenario_id``.
    """

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.scenario_id):
            args.scenario_id = (
                f"/subscriptions/{self.ctx.subscription_id}"
                f"/resourceGroups/{args.resource_group}"
                f"/providers/Microsoft.Chaos"
                f"/workspaces/{args.workspace_name}"
                f"/scenarios/{args.scenario_name}"
            )
