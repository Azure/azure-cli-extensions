# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import time
import uuid

from azure.cli.core.aaz import has_value
from azure.cli.core.util import send_raw_request
from knack.log import get_logger
from knack.util import CLIError

from .aaz.latest.chaos.scenario.config._create import Create as _ScenarioConfigCreate
from .aaz.latest.chaos.scenario.config._execute import Execute as _ScenarioConfigExecute
from .aaz.latest.chaos.workspace._refresh_recommendation import RefreshRecommendation as _RefreshRecommendation

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


def _build_arm_url(cli_ctx, resource_group, workspace, path_suffix):
    """Build a fully qualified ARM URL for a workspace-scoped sub-resource."""
    from azure.cli.core.commands.client_factory import get_subscription_id
    sub = get_subscription_id(cli_ctx)
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
        f"Run `az chaos workspace refresh-recommendation "
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
    "'refresh-recommendation'. If it persists, run "
    "'az chaos workspace show-discovery' / 'show-evaluation' for full error "
    "detail and verify the workspace UAMI has Reader on all in-scope scopes."
)


def _check_inner_lro(cli_ctx, resource_group_name, workspace_name, path_suffix,
                     operation_label):
    """Fetch a /latest singleton and raise if its inner status is Failed.

    Returns silently for any other state (Succeeded, in-progress, no result
    yet, or endpoint not reachable). We only flip to non-zero exit when the
    inner result is unambiguously Failed.
    """
    url = _build_arm_url(cli_ctx, resource_group_name, workspace_name, path_suffix)
    try:
        response = send_raw_request(cli_ctx, "GET", url)
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
        f"refresh-recommendation completed but the inner "
        f"{operation_label} operation Failed ({detail}). "
        f"{_INNER_LRO_FAILURE_HINT}"
    )


# ── workspace refresh-recommendation ────────────────────────────────────
# The user-facing command is the AAZ-generated `chaos workspace
# refresh-recommendation`. We override it via the `WorkspaceRefreshRecommendation`
# subclass at the bottom of this file (registered in commands.py
# `_register_aaz_subclass_overrides`). The `post_operations` hook calls
# `_check_inner_lro` for both inner discoveries/latest and evaluations/latest
# to detect the silent-failure case the framework polling alone misses.


# ── scenario config validate ─────────────────────────────────────────────

def scenario_config_validate(cmd, resource_group_name, workspace_name,  # pylint: disable=too-many-positional-arguments
                             scenario_name, scenario_configuration_name,
                             no_wait=False):
    """POST validate + poll LRO + auto-GET validations/latest."""
    validate_url = _build_arm_url(
        cmd.cli_ctx, resource_group_name, workspace_name,
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
        cmd.cli_ctx, resource_group_name, workspace_name,
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
            cmd.cli_ctx, resource_group_name, workspace_name,
            f"/scenarios/{scenario_name}"
            f"/configurations/{scenario_configuration_name}/validate"
        )
        val_response = send_raw_request(cmd.cli_ctx, "POST", validate_url)

        # Always poll validation to completion, even with --no-wait
        _poll_or_return(cmd, val_response)

        # GET validations/latest
        latest_url = _build_arm_url(
            cmd.cli_ctx, resource_group_name, workspace_name,
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
        cmd.cli_ctx, resource_group_name, workspace_name,
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
        cmd.cli_ctx, resource_group_name, workspace_name, "/discoveries/latest"
    )
    response = send_raw_request(cmd.cli_ctx, "GET", url)
    return response.json() if response.text else None


def workspace_show_evaluation(cmd, resource_group_name, workspace_name):
    """GET the latest workspace scenario-evaluation operation result."""
    url = _build_arm_url(
        cmd.cli_ctx, resource_group_name, workspace_name, "/evaluations/latest"
    )
    response = send_raw_request(cmd.cli_ctx, "GET", url)
    return response.json() if response.text else None


def scenario_config_show_validation(cmd, resource_group_name, workspace_name,
                                    scenario_name, scenario_configuration_name):
    """GET the latest validation result for a scenario configuration."""
    url = _build_arm_url(
        cmd.cli_ctx, resource_group_name, workspace_name,
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
        cmd.cli_ctx, resource_group_name, workspace_name,
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
        cmd.cli_ctx, resource_group_name, workspace_name,
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
        cmd.cli_ctx, resource_group_name, workspace_name,
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


# ── az chaos setup (porcelain / composite first-day experience) ──────────
# `az chaos setup` is a COMPOSITE (porcelain) command per the CLI design
# philosophy (.github/skills/chaos-automation-codegen/context/
# cli-design-philosophy.md). Its identity is the WORKFLOW — "stand up a
# ready-to-use Chaos Studio environment" — not any single API operation, and
# it is a CLI-surface-specific affordance (intentionally NOT mirrored to the
# Terraform/PowerShell surfaces). Inspired by `az containerapp up` /
# `az webapp up`: ensure the resource group, create the workspace + identity,
# grant the identity the permissions discovery needs, evaluate scenarios, then
# report the discovered scenarios and the commands to run next.

# Azure built-in "Reader" role. The workspace's managed identity must hold
# Reader on each in-scope resource for resource discovery + scenario evaluation
# to succeed: discovery always runs under the workspace MI
# (services/AP/.../TargetDiscoveryController.cs) and refreshRecommendations
# orchestrates discover-then-evaluate
# (services/GW/.../RefreshWorkspaceRecommendationsOrchestration.cs). GUID
# verified against the Azure RBAC built-in roles reference:
# https://learn.microsoft.com/azure/role-based-access-control/built-in-roles/general#reader
_READER_ROLE_DEFINITION_GUID = "acdd72a7-3385-48ef-bd42-f606fba81ae7"

_RESOURCE_GROUP_API_VERSION = "2021-04-01"
_ROLE_ASSIGNMENT_API_VERSION = "2022-04-01"

# Resource discovery runs under the workspace identity; a freshly-granted Reader
# role can lag in Azure Resource Graph (typically clears in 1-3 min), so the
# evaluate step retries a bounded number of times before reporting a hint.
_EVALUATION_MAX_ATTEMPTS = 3
_EVALUATION_RETRY_INTERVAL_SECONDS = 120


def setup(cmd, resource_group_name, workspace_name, location, scopes,  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
          user_assigned=None, skip_permissions=False,
          skip_evaluation_wait=False, tags=None):
    """Stand up a ready-to-use Chaos Studio environment end to end.

    Composite first-day-experience flow: ensure the resource group exists,
    create the workspace with a managed identity, grant that identity the
    Reader role discovery requires on each scope, evaluate scenarios, and
    report the discovered scenarios plus suggested next commands.

    Assigning Reader is idempotent — an already-present assignment is a no-op
    (ARM reports ``RoleAssignmentExists``). Only when a *new* assignment is
    created this run does the evaluate step wait out Azure Resource Graph
    propagation (retrying a few times); pass ``--skip-evaluation-wait`` to force
    a single attempt (e.g. in CI).
    """
    # 1. Resource group ──────────────────────────────────────────────────
    _ensure_resource_group(cmd, resource_group_name, location)

    # 2. Workspace ───────────────────────────────────────────────────────
    workspace = _create_setup_workspace(
        cmd, resource_group_name, workspace_name, location,
        scopes, user_assigned, tags,
    )

    # 3. Permissions — Reader for the workspace identity on each scope ────
    principal_ids = _resolve_workspace_principal_ids(workspace, user_assigned)
    role_assignments = []
    if skip_permissions:
        logger.warning(
            "Skipping permission setup (--skip-permissions). Evaluation will "
            "still run, but it can only discover resources if the workspace "
            "identity already holds the Reader role on the target scopes.",
        )
    elif not principal_ids:
        logger.warning(
            "Could not resolve the workspace identity principal ID; skipping "
            "Reader role assignment. Grant Reader to the workspace identity on "
            "the target scopes manually, then re-run "
            "'az chaos workspace refresh-recommendation'.",
        )
    else:
        for principal_id in principal_ids:
            for scope in scopes:
                assignment = _assign_reader_role(cmd, scope, principal_id)
                if assignment:
                    role_assignments.append(assignment)

    # 4. Evaluate scenarios ──────────────────────────────────────────────
    # Only wait out Azure Resource Graph propagation when we created a NEW role
    # assignment this run — that is what lags. A pre-existing assignment
    # (roleAssignmentName is None) is a no-op with no propagation delay, so a
    # single evaluation attempt is enough.
    created_new_assignment = any(
        a.get("roleAssignmentName") for a in role_assignments
    )
    wait_for_propagation = created_new_assignment and not skip_evaluation_wait
    evaluated = _evaluate_scenarios_workflow(
        cmd, resource_group_name, workspace_name,
        wait_for_propagation=wait_for_propagation,
    )

    # 5. Report ──────────────────────────────────────────────────────────
    scenarios = _list_workspace_scenarios(
        cmd, resource_group_name, workspace_name,
    )
    next_steps = _build_setup_next_steps(
        resource_group_name, workspace_name, scenarios, evaluated,
    )
    _print_setup_summary(
        resource_group_name, workspace_name, scenarios, next_steps,
    )
    return {
        "workspace": workspace,
        "identityPrincipalIds": principal_ids,
        "roleAssignments": role_assignments,
        "scenarios": scenarios,
        "nextSteps": next_steps,
    }


def _ensure_resource_group(cmd, resource_group_name, location):
    """Create the resource group if it does not already exist."""
    from azure.cli.core.commands.client_factory import get_subscription_id
    sub = get_subscription_id(cmd.cli_ctx)
    rg_url = (
        f"/subscriptions/{sub}/resourcegroups/{resource_group_name}"
        f"?api-version={_RESOURCE_GROUP_API_VERSION}"
    )
    try:
        existing = send_raw_request(cmd.cli_ctx, "GET", rg_url)
        if existing.status_code == 200:
            logger.warning(
                "Using existing resource group '%s'.", resource_group_name,
            )
            return
    except Exception:  # pylint: disable=broad-except
        pass  # GET raises on 404 — fall through to create.
    logger.warning(
        "Creating resource group '%s' in location '%s'.",
        resource_group_name, location,
    )
    send_raw_request(
        cmd.cli_ctx, "PUT", rg_url,
        body=json.dumps({"location": location}),
        headers=["Content-Type=application/json"],
    )


def _create_setup_workspace(cmd, resource_group_name, workspace_name,  # pylint: disable=too-many-arguments,too-many-positional-arguments
                            location, scopes, user_assigned, tags):
    """PUT the workspace, poll the create LRO, and return the final resource.

    When ``user_assigned`` is supplied the workspace uses a UserAssigned
    identity; otherwise it uses a SystemAssigned identity (the workspace's own
    system-assigned identity becomes the workspace identity).
    """
    if user_assigned:
        identity = {
            "type": "UserAssigned",
            "userAssignedIdentities": {uid: {} for uid in user_assigned},
        }
    else:
        identity = {"type": "SystemAssigned"}
    body = {
        "location": location,
        "identity": identity,
        "properties": {"scopes": list(scopes)},
    }
    if tags:
        body["tags"] = tags
    url = _build_arm_url(cmd.cli_ctx, resource_group_name, workspace_name, "")
    logger.warning(
        "Creating workspace '%s' (identity: %s).",
        workspace_name, identity["type"],
    )
    response = send_raw_request(
        cmd.cli_ctx, "PUT", url,
        body=json.dumps(body), headers=["Content-Type=application/json"],
    )
    _poll_or_return(cmd, response)
    # Re-GET for the authoritative identity block: ARM populates the managed
    # identity ``principalId`` asynchronously and it may be absent on the
    # initial create response.
    final = send_raw_request(cmd.cli_ctx, "GET", url)
    return final.json() if final.text else {}


def _resolve_workspace_principal_ids(workspace, user_assigned):
    """Return the identity principal IDs to grant Reader to.

    For a system-assigned identity that is the single ``identity.principalId``.
    For user-assigned identities it is the ``principalId`` of each assigned
    identity (ARM resource-id keys are matched case-insensitively).
    """
    identity = (workspace or {}).get("identity") or {}
    principal_ids = []
    if user_assigned:
        ua_map = identity.get("userAssignedIdentities") or {}
        for uid in user_assigned:
            entry = ua_map.get(uid)
            if entry is None:
                for key, value in ua_map.items():
                    if key.lower() == uid.lower():
                        entry = value
                        break
            if entry and entry.get("principalId"):
                principal_ids.append(entry["principalId"])
    else:
        principal_id = identity.get("principalId")
        if principal_id:
            principal_ids.append(principal_id)
    return principal_ids


def _subscription_from_scope(scope):
    """Extract the subscription GUID from an ARM scope id (best-effort)."""
    segments = [s for s in (scope or "").strip("/").split("/") if s]
    if len(segments) >= 2 and segments[0].lower() == "subscriptions":
        return segments[1]
    return None


def _assign_reader_role(cmd, scope, principal_id):
    """Assign the Reader role to a principal on a scope (idempotent).

    Returns a record of the assignment, or ``None`` when it could not be made.
    An already-existing assignment is treated as success. Other failures
    (e.g. the caller lacks Owner / User Access Administrator) are surfaced as a
    warning rather than aborting the whole setup.
    """
    sub = _subscription_from_scope(scope)
    if not sub:
        logger.warning(
            "Skipping role assignment on '%s': could not parse a subscription "
            "from the scope.", scope,
        )
        return None
    role_definition_id = (
        f"/subscriptions/{sub}/providers/Microsoft.Authorization"
        f"/roleDefinitions/{_READER_ROLE_DEFINITION_GUID}"
    )
    assignment_name = str(uuid.uuid4())
    url = (
        f"{scope}/providers/Microsoft.Authorization/roleAssignments/"
        f"{assignment_name}?api-version={_ROLE_ASSIGNMENT_API_VERSION}"
    )
    body = json.dumps({
        "properties": {
            "roleDefinitionId": role_definition_id,
            "principalId": principal_id,
            # ``ServicePrincipal`` lets ARM skip the directory lookup that can
            # 400 with PrincipalNotFound right after a managed identity is
            # created (Azure AD replication lag).
            "principalType": "ServicePrincipal",
        }
    })
    try:
        send_raw_request(
            cmd.cli_ctx, "PUT", url,
            body=body, headers=["Content-Type=application/json"],
        )
        logger.warning(
            "Granted Reader to identity %s on scope %s.", principal_id, scope,
        )
        return {
            "scope": scope,
            "principalId": principal_id,
            "roleAssignmentName": assignment_name,
        }
    except Exception as ex:  # pylint: disable=broad-except
        text = str(ex)
        if "RoleAssignmentExists" in text or "already exists" in text.lower():
            logger.warning(
                "Reader already assigned to identity %s on scope %s.",
                principal_id, scope,
            )
            return {
                "scope": scope,
                "principalId": principal_id,
                "roleAssignmentName": None,
            }
        logger.warning(
            "Could not assign Reader to identity %s on scope %s: %s. You may "
            "need Owner or User Access Administrator on the scope. Assign "
            "Reader manually, then re-run 'az chaos workspace "
            "refresh-recommendation --name <ws> --resource-group <rg>'.",
            principal_id, scope, text,
        )
        return None


def _evaluate_scenarios_workflow(cmd, resource_group_name, workspace_name,
                                 wait_for_propagation=False):
    """Run the evaluate-scenarios workflow for the workspace.

    This is the porcelain "evaluate scenarios" step. It is intentionally bound
    to the SAME logical workflow exposed by
    ``az chaos workspace evaluate-scenarios`` — NOT to the plumbing
    ``refresh-recommendation`` op. Today that workflow maps 1:1 to
    ``Workspaces_RefreshRecommendations`` (a single ``POST
    /refreshRecommendations`` that orchestrates discover-then-evaluate). When
    the spec splits that op into ``Workspaces_Discover`` +
    ``Workspaces_Evaluate`` (2026-08-01-preview — see the
    ``WorkspaceRefreshRecommendation`` docstring), update THIS helper (and
    ``WorkspaceEvaluateScenarios``) to call both in sequence; ``setup``
    inherits the new behavior automatically because it routes through here.

    Resource discovery runs under the workspace identity, and a freshly-granted
    Reader role can lag in Azure Resource Graph (1-3 min). When
    ``wait_for_propagation`` is set, the whole evaluation is retried up to
    ``_EVALUATION_MAX_ATTEMPTS`` times with
    ``_EVALUATION_RETRY_INTERVAL_SECONDS`` between attempts so the common
    first-run case returns discovered scenarios instead of a propagation-lag
    failure. The rerun hint is only emitted once all attempts are exhausted.

    Returns ``True`` when discovery/evaluation completed cleanly, ``False``
    otherwise (never raises — the resource group, workspace, identity, and role
    assignments are already provisioned by the time we get here).
    """
    max_attempts = _EVALUATION_MAX_ATTEMPTS if wait_for_propagation else 1
    url = _build_arm_url(
        cmd.cli_ctx, resource_group_name, workspace_name,
        "/refreshRecommendations",
    )
    for attempt in range(1, max_attempts + 1):
        if max_attempts > 1:
            logger.warning(
                "Evaluating scenarios for workspace '%s' (attempt %d/%d).",
                workspace_name, attempt, max_attempts,
            )
        else:
            logger.warning(
                "Evaluating scenarios for workspace '%s'.", workspace_name,
            )
        response = send_raw_request(cmd.cli_ctx, "POST", url)
        _poll_or_return(cmd, response)

        failed_label = _setup_inner_lro_failure(
            cmd, resource_group_name, workspace_name,
        )
        if not failed_label:
            return True

        if attempt < max_attempts:
            logger.warning(
                "Scenario evaluation did not complete (%s failed) — commonly "
                "Azure Resource Graph propagation lag right after the Reader "
                "role is granted to the workspace identity. Waiting %d seconds "
                "before retrying...",
                failed_label, _EVALUATION_RETRY_INTERVAL_SECONDS,
            )
            time.sleep(_EVALUATION_RETRY_INTERVAL_SECONDS)
        else:
            logger.warning(
                "Workspace provisioned, but scenario evaluation did not "
                "complete (%s failed)%s. The resource group, workspace, "
                "identity, and role assignments are all in place. Re-run "
                "'az chaos workspace refresh-recommendation --name %s "
                "--resource-group %s' in a couple of minutes, then "
                "'az chaos scenario list --workspace-name %s -g %s'.",
                failed_label,
                f" after {max_attempts} attempts" if max_attempts > 1 else "",
                workspace_name, resource_group_name,
                workspace_name, resource_group_name,
            )
    return False


def _setup_inner_lro_failure(cmd, resource_group_name, workspace_name):
    """Return a label if discovery/evaluation inner LRO is Failed, else None.

    Soft (non-raising) sibling of ``_check_inner_lro`` — setup downgrades inner
    failures to a warning instead of a non-zero exit.
    """
    checks = (
        ("/discoveries/latest", "resource discovery"),
        ("/evaluations/latest", "scenario evaluation"),
    )
    for path_suffix, label in checks:
        url = _build_arm_url(
            cmd.cli_ctx, resource_group_name, workspace_name, path_suffix,
        )
        try:
            resp = send_raw_request(cmd.cli_ctx, "GET", url)
        except Exception:  # pylint: disable=broad-except
            continue  # /latest may legitimately 404 on a fresh workspace
        if resp.status_code != 200 or not resp.text:
            continue
        try:
            props = (resp.json() or {}).get("properties") or {}
        except Exception:  # pylint: disable=broad-except
            continue
        if props.get("status") == "Failed":
            return label
    return None


def _list_workspace_scenarios(cmd, resource_group_name, workspace_name):
    """GET the catalog/discovered scenarios for the workspace."""
    url = _build_arm_url(
        cmd.cli_ctx, resource_group_name, workspace_name, "/scenarios",
    )
    try:
        resp = send_raw_request(cmd.cli_ctx, "GET", url)
    except Exception:  # pylint: disable=broad-except
        return []
    if resp.status_code != 200 or not resp.text:
        return []
    try:
        return (resp.json() or {}).get("value") or []
    except Exception:  # pylint: disable=broad-except
        return []


def _build_setup_next_steps(resource_group_name, workspace_name, scenarios,
                            evaluated):
    """Build the list of suggested next commands after setup completes."""
    steps = []
    if not evaluated:
        steps.append(
            f"az chaos workspace refresh-recommendation "
            f"--name {workspace_name} --resource-group {resource_group_name}"
        )
    steps.append(
        f"az chaos scenario list --workspace-name {workspace_name} "
        f"-g {resource_group_name}"
    )
    example_scenario = (
        scenarios[0].get("name") if scenarios else "<scenario-name>"
    )
    steps.append(
        f"az chaos scenario config create --workspace-name {workspace_name} "
        f"-g {resource_group_name} --scenario-name {example_scenario} "
        f"--name <config-name> --parameters @params.json"
    )
    steps.append(
        f"az chaos scenario run start --workspace-name {workspace_name} "
        f"-g {resource_group_name} --scenario-name {example_scenario} "
        f"--config-name <config-name>"
    )
    return steps


def _print_setup_summary(resource_group_name, workspace_name, scenarios,
                         next_steps):
    """Emit the human-friendly post-setup summary (mirrors `containerapp up`)."""
    logger.warning(
        "\nChaos Studio workspace '%s' is ready in resource group '%s'.",
        workspace_name, resource_group_name,
    )
    if scenarios:
        logger.warning("Discovered %d scenario(s):", len(scenarios))
        for scenario in scenarios:
            name = scenario.get("name", "<unknown>")
            recommendation = (
                ((scenario.get("properties") or {}).get("recommendation")) or {}
            ).get("recommendationStatus", "")
            suffix = f" ({recommendation})" if recommendation else ""
            logger.warning("  - %s%s", name, suffix)
    else:
        logger.warning(
            "No scenarios discovered yet. If evaluation is still in progress "
            "or needs a retry, re-run 'az chaos workspace "
            "refresh-recommendation' and then 'az chaos scenario list'.",
        )
    logger.warning("\nNext steps:")
    for step in next_steps:
        logger.warning("  %s", step)


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


class WorkspaceRefreshRecommendation(_RefreshRecommendation):
    """Override ``chaos workspace refresh-recommendation`` to detect inner-LRO failures.

    Why this exists:
        The GW orchestrates ``POST /refreshRecommendations`` as a composite
        DTFx workflow (discover -> evaluate) and overrides the response
        ``Location`` header to point at ``evaluations/latest``. That
        passthrough returns HTTP 200 with the real status nested at
        ``body["properties"]["status"]``. The aaz framework polling uses
        ``final-state-via: location`` and reads only the root-level status,
        so it silently returns success when discovery or evaluation
        actually failed (e.g. ARG propagation lag after a fresh Reader
        role assignment to the workspace UAMI).

        This ``post_operations`` hook reads the ``properties.status`` on
        ``discoveries/latest`` and ``evaluations/latest`` to detect the
        real outcome and raises a ``CLIError`` with ARG-lag guidance when
        either inner LRO failed.

    Lifecycle:
        Remove this subclass (and the corresponding ``command_table``
        registration in ``commands.py``) when the Microsoft.Chaos spec
        deprecates ``/refreshRecommendations`` in favor of the separate
        ``/discover`` + ``/evaluate`` ARM ops (planned 2026-08-01-preview;
        tracked in ``docs/projects/workspace-operations-decoupling/
        phase-2-public-preview.plan.md``). The replacement ops are
        straightforward LROs the standard aaz poller handles correctly.
    """

    def _handler(self, command_args):
        # Override the parent's poller construction. The AAZ-generated
        # ``WorkspacesRefreshRecommendations.__call__`` passes ``None`` as
        # the LRO success deserializer to ``build_lro_polling``; the
        # framework's ``base_polling._parse_resource`` later tries to call
        # that ``None`` and raises ``TypeError: 'NoneType' object is not
        # callable``. We provide a no-op deserializer so ``.result()`` on
        # the poller returns ``None`` cleanly. The actual diagnostic value
        # is in ``post_operations`` above (which runs during
        # ``_execute_operations``, before ``.result()`` is called).
        super()._handler(command_args)
        return self.build_lro_poller(self._execute_operations, lambda _: None)

    def post_operations(self):
        args = self.ctx.args
        rg = str(args.resource_group)
        ws = str(args.workspace_name)
        _check_inner_lro(
            self.cli_ctx, rg, ws,
            "/discoveries/latest", "resource discovery",
        )
        _check_inner_lro(
            self.cli_ctx, rg, ws,
            "/evaluations/latest", "scenario evaluation",
        )
        logger.warning(
            "Successfully refreshed recommendations for workspace '%s' "
            "in resource group '%s'. Workspace evaluation has been refreshed; "
            "subsequent 'scenario config validate' / 'scenario run start' calls "
            "(for non-custom scenarios) now have a satisfied evaluation gate.\n"
            "Run 'az chaos scenario list --workspace-name %s -g %s' to see "
            "updated recommendation statuses.",
            ws, rg, ws, rg,
        )


class WorkspaceEvaluateScenarios(WorkspaceRefreshRecommendation):
    """Porcelain alias of ``chaos workspace refresh-recommendation``.

    Today this is a thin alias that maps to the same composite LRO. When
    ``/refreshRecommendations`` is deprecated in favor of separate
    ``/discover`` + ``/evaluate`` ARM ops (2026-08-01-preview), this
    command will become a true composite that invokes both in sequence,
    while ``refresh-recommendation`` retires alongside its parent op.

    The user-facing name (``evaluate-scenarios``) is the human-first verb
    for "evaluate every scenario in this workspace against the latest
    discovered resources" -- the same logical workflow this entire LRO
    performs, just named more conversationally.
    """


class ScenarioConfigExecute(_ScenarioConfigExecute):
    """Override ``chaos scenario config execute`` to avoid the AAZ-generated
    ``NoneType`` crash on successful LRO completion.

    The AAZ-generated inner operation passes ``None`` as the LRO success
    deserializer; the framework's ``base_polling._parse_resource`` later
    invokes that ``None`` and raises ``TypeError: 'NoneType' object is
    not callable``. Same fix as ``WorkspaceRefreshRecommendation``: inject
    a no-op deserializer so ``.result()`` on the poller returns ``None``
    cleanly. The user-facing porcelain (``chaos scenario run start`` in
    ``custom.py``) supersedes this command for typical workflows, but
    ``scenario config execute`` remains the plumbing surface for
    automation/agents and must not crash.
    """

    def _handler(self, command_args):
        super()._handler(command_args)
        return self.build_lro_poller(self._execute_operations, lambda _: None)
