# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Hierarchy create command - creates a hierarchy level in a single command.

Wraps 4-6 operations into one:
  0. Auto-create Context + update hierarchies/capabilities (if needed)
  1. Create Service Group
  2. Create Site (in Service Group)
  3. Create Configuration
  4. Create Configuration Reference (links Config to Site)
  5. Create Site Reference (links Site to Context)

Usage:
    az workload-orchestration hierarchy create \\
        --name my-factory -g my-rg -l eastus --level-label Factory \\
        --parent my-region --capabilities soap shampoo
"""

# pylint: disable=broad-exception-caught
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
# pylint: disable=import-outside-toplevel

import json
import logging
from datetime import datetime, timezone

from azure.cli.core.azclierror import (
    CLIInternalError,
    ValidationError,
)
from azure.cli.core.util import send_raw_request

from azext_workload_orchestration.onboarding.consts import (
    ARM_ENDPOINT,
    SERVICE_GROUP_API_VERSION,
    SITE_API_VERSION,
    CONFIGURATION_API_VERSION,
    CONFIG_REF_API_VERSION,
    EDGE_RP_NAMESPACE,
    MAX_HIERARCHY_NAME_LENGTH,
)
from azext_workload_orchestration.onboarding.utils import (
    invoke_cli_command,
    print_step,
    print_success,
    print_detail,
)

logger = logging.getLogger(__name__)

TOTAL_STEPS_WITH_CONTEXT = 6
TOTAL_STEPS_NO_CONTEXT = 4


def hierarchy_create(
    cmd,
    name,
    resource_group,
    location,
    level_label,
    parent=None,
    capabilities=None,
    description=None,
    context_name=None,
    context_rg=None,
    skip_context=False,
    skip_site_reference=False,
):
    """Create a hierarchy level (ServiceGroup + Site + Config + ConfigRef) in one command.

    Optionally auto-creates a default Context and SiteReference if none exists.
    All PUT operations are idempotent (safe to re-run).
    """
    # -----------------------------------------------------------------------
    # Pre-flight validation
    # -----------------------------------------------------------------------
    if len(name) > MAX_HIERARCHY_NAME_LENGTH:
        raise ValidationError(
            f"Name '{name}' is {len(name)} characters. "
            f"Maximum is {MAX_HIERARCHY_NAME_LENGTH} "
            "(limited by the Configuration resource name constraint)."
        )

    description = description or name
    sub_id = _get_sub_id(cmd)
    tenant_id = _get_tenant_id(cmd)

    total_steps = TOTAL_STEPS_NO_CONTEXT if skip_context else TOTAL_STEPS_WITH_CONTEXT
    step = 0
    step_results = {}

    print(f"\nCreating hierarchy level '{name}' ({level_label})...\n")

    # -----------------------------------------------------------------------
    # Step 0: Auto-create / detect Context (if not skipped)
    # -----------------------------------------------------------------------
    ctx_name = None
    ctx_rg = None

    if not skip_context:
        step += 1
        try:
            ctx_name, ctx_rg = _ensure_context(
                cmd, resource_group, location, context_name, context_rg,
                level_label, capabilities, step, total_steps
            )
            step_results["context"] = "Succeeded"
        except Exception as exc:
            step_results["context"] = f"FAILED: {exc}"
            _print_hierarchy_diagnostic(step_results, name, resource_group)
            raise CLIInternalError(
                f"Context setup failed: {exc}",
                recommendation=(
                    "Try creating context manually:\n"
                    f"  az workload-orchestration context create -g {resource_group} "
                    f"-l {location} --name {resource_group}-context "
                    "--capabilities [] --hierarchies []"
                )
            )

    # -----------------------------------------------------------------------
    # Step 1: Create Service Group
    # -----------------------------------------------------------------------
    step += 1
    try:
        parent_id = (
            f"/providers/Microsoft.Management/serviceGroups/{parent}"
            if parent
            else f"/providers/Microsoft.Management/serviceGroups/{tenant_id}"
        )
        sg_id = f"/providers/Microsoft.Management/serviceGroups/{name}"

        _arm_put_quiet(cmd, f"{ARM_ENDPOINT}{sg_id}", {
            "properties": {
                "displayName": name,
                "parent": {"resourceId": parent_id}
            }
        }, SERVICE_GROUP_API_VERSION)

        print_step(step, total_steps, "Service Group", "[OK] Created")
        step_results["service-group"] = "Succeeded"
    except Exception as exc:
        step_results["service-group"] = f"FAILED: {exc}"
        _print_hierarchy_diagnostic(step_results, name, resource_group)
        raise CLIInternalError(
            f"Service Group creation failed: {exc}",
            recommendation=(
                f"Try manually: az rest --method put "
                f"--url \"{ARM_ENDPOINT}{sg_id}?api-version={SERVICE_GROUP_API_VERSION}\" "
                f"--header Content-Type=application/json "
                f"--body \"{{\\\"properties\\\":{{\\\"displayName\\\":\\\"{name}\\\","
                f"\\\"parent\\\":{{\\\"resourceId\\\":\\\"{parent_id}\\\"}}}}}}\" "
                f"--resource {ARM_ENDPOINT}"
            )
        )

    # -----------------------------------------------------------------------
    # Step 2: Create Site (in Service Group, regional endpoint)
    # Retry with backoff - RBAC on new ServiceGroup scope takes time to propagate
    # -----------------------------------------------------------------------
    step += 1
    site_id = f"{sg_id}/providers/{EDGE_RP_NAMESPACE}/sites/{name}"
    try:
        regional_url = f"https://{location}.management.azure.com{site_id}"

        max_retries = 4
        retry_delay = 10  # seconds
        last_err = None
        for attempt in range(max_retries):
            try:
                _arm_put_quiet(cmd, regional_url, {
                    "properties": {
                        "displayName": name,
                        "description": description,
                        "labels": {"level": level_label}
                    }
                }, SITE_API_VERSION)
                last_err = None
                break
            except Exception as exc:
                last_err = exc
                err_str = str(exc).lower()
                is_auth_error = any(x in err_str for x in [
                    "authorizationfailed", "forbidden", "403",
                    "does not have authorization"
                ])
                if is_auth_error and attempt < max_retries - 1:
                    wait = retry_delay * (attempt + 1)
                    logger.info(
                        "Site creation got 403 (RBAC propagation). "
                        "Retry %d/%d in %ds...", attempt + 1, max_retries - 1, wait
                    )
                    print_step(step, total_steps, "Site",
                               f"Waiting for permissions ({wait}s)...")
                    import time
                    time.sleep(wait)
                else:
                    raise

        if last_err:
            raise last_err

        print_step(step, total_steps, "Site", "[OK] Created")
        step_results["site"] = "Succeeded"
    except Exception as exc:
        step_results["site"] = f"FAILED: {exc}"
        _print_hierarchy_diagnostic(step_results, name, resource_group)
        raise CLIInternalError(
            f"Site creation failed: {exc}",
            recommendation=(
                "Check that the region supports the Sites API. "
                f"Region used: {location}. "
                "Try eastus2euap for canary testing."
            )
        )

    # -----------------------------------------------------------------------
    # Step 3: Create Configuration
    # -----------------------------------------------------------------------
    step += 1
    config_id = (
        f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
        f"/providers/{EDGE_RP_NAMESPACE}/configurations/{name}"
    )
    try:
        regional_config_url = f"https://{location}.management.azure.com{config_id}"

        _arm_put_quiet(cmd, regional_config_url, {
            "location": location
        }, CONFIGURATION_API_VERSION)

        print_step(step, total_steps, "Configuration", "[OK] Created")
        step_results["configuration"] = "Succeeded"
    except Exception as exc:
        step_results["configuration"] = f"FAILED: {exc}"
        _print_hierarchy_diagnostic(step_results, name, resource_group)
        raise CLIInternalError(
            f"Configuration creation failed: {exc}",
            recommendation=(
                f"Configuration name must be ≤{MAX_HIERARCHY_NAME_LENGTH} chars. "
                f"Current name: '{name}' ({len(name)} chars)."
            )
        )

    # -----------------------------------------------------------------------
    # Step 4: Create Configuration Reference (links Config → Site)
    # -----------------------------------------------------------------------
    step += 1
    try:
        config_ref_url = (
            f"{ARM_ENDPOINT}{site_id}"
            f"/providers/{EDGE_RP_NAMESPACE}/configurationreferences/default"
        )

        _arm_put_quiet(cmd, config_ref_url, {
            "properties": {
                "configurationResourceId": config_id
            }
        }, CONFIG_REF_API_VERSION)

        print_step(step, total_steps, "Configuration Reference", "[OK] Linked")
        step_results["config-reference"] = "Succeeded"
    except Exception as exc:
        step_results["config-reference"] = f"FAILED: {exc}"
        _print_hierarchy_diagnostic(step_results, name, resource_group)
        raise CLIInternalError(
            f"Configuration Reference creation failed: {exc}",
            recommendation="This links the Configuration to the Site. Check ARM access."
        )

    # -----------------------------------------------------------------------
    # Step 5: Create Site Reference (links Site → Context)
    # -----------------------------------------------------------------------
    if not skip_context and not skip_site_reference and ctx_name:
        step += 1
        try:
            invoke_cli_command(cmd, [
                "workload-orchestration", "context", "site-reference", "create",
                "-g", ctx_rg or resource_group,
                "--context-name", ctx_name,
                "--name", f"{name}-ref",
                "--site-id", site_id,
            ], expect_json=False)

            print_step(step, total_steps, "Site Reference", "[OK] Linked to context")
            step_results["site-reference"] = "Succeeded"
        except Exception as exc:
            # Site reference may already exist (not critical)
            if "already exists" in str(exc).lower() or "conflict" in str(exc).lower():
                print_step(step, total_steps, "Site Reference", "Already exists [OK]")
                step_results["site-reference"] = "Already exists"
            else:
                step_results["site-reference"] = f"FAILED: {exc}"
                logger.warning("Site reference creation failed (non-critical): %s", exc)
                print_step(step, total_steps, "Site Reference", f"[WARN] Warning: {exc}")

    # -----------------------------------------------------------------------
    # Output
    # -----------------------------------------------------------------------
    _print_hierarchy_diagnostic(step_results, name, resource_group)

    print_success(f"Hierarchy level '{name}' created")
    print_detail("Service Group", sg_id)
    print_detail("Site ID", site_id)
    print_detail("Configuration ID", config_id)
    if ctx_name:
        print_detail("Context", ctx_name)
    print()

    return {
        "name": name,
        "levelLabel": level_label,
        "serviceGroupId": sg_id,
        "siteId": site_id,
        "configurationId": config_id,
        "contextName": ctx_name,
        "contextAutoCreated": ctx_name is not None and not context_name,
    }


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------

def _ensure_context(
    cmd, resource_group, location, context_name, context_rg,
    level_label, capabilities, step, total_steps
):
    """Ensure a WO context exists. Auto-create if needed.

    Returns (context_name, context_rg) tuple.
    """
    # Check if context is already set in CLI config
    try:
        current = invoke_cli_command(cmd, [
            "workload-orchestration", "context", "current",
        ])
        if current and isinstance(current, dict):
            existing_name = current.get("name") or current.get("contextName")
            existing_rg = current.get("resourceGroup")
            if existing_name:
                print_step(step, total_steps, "Context",
                           f"Using existing '{existing_name}' [OK]")

                # Update context with new hierarchy level and capabilities if needed
                _update_context_if_needed(
                    cmd, existing_name, existing_rg or resource_group,
                    level_label, capabilities
                )
                return existing_name, existing_rg or resource_group
    except Exception:
        pass  # No context set, try to find or create one

    # Try to use explicitly provided context
    if context_name:
        ctx_rg = context_rg or resource_group
        print_step(step, total_steps, "Context",
                   f"Using specified '{context_name}' [OK]")
        _update_context_if_needed(cmd, context_name, ctx_rg, level_label, capabilities)

        # Set as current
        try:
            invoke_cli_command(cmd, [
                "workload-orchestration", "context", "use",
                "--name", context_name, "-g", ctx_rg,
            ], expect_json=False)
        except Exception:
            pass
        return context_name, ctx_rg

    # Auto-create default context
    default_ctx_name = f"{resource_group}-context"
    ctx_rg = context_rg or resource_group
    print_step(step, total_steps, "Context",
               f"Creating default '{default_ctx_name}'")

    # Build hierarchies and capabilities for context create
    hierarchies_args = [
        f"[0].name={level_label.lower()}",
        f"[0].description={level_label}",
    ]
    capabilities_args = []
    if capabilities:
        for i, cap in enumerate(capabilities):
            capabilities_args.extend([
                f"[{i}].name={cap}",
                f"[{i}].description={cap}",
            ])

    create_args = [
        "workload-orchestration", "context", "create",
        "-g", ctx_rg,
        "-l", location,
        "--name", default_ctx_name,
        "--hierarchies",
    ] + hierarchies_args

    if capabilities_args:
        create_args.append("--capabilities")
        create_args.extend(capabilities_args)

    invoke_cli_command(cmd, create_args, expect_json=False)

    # Set as current
    try:
        invoke_cli_command(cmd, [
            "workload-orchestration", "context", "use",
            "--name", default_ctx_name, "-g", ctx_rg,
        ], expect_json=False)
    except Exception:
        pass

    print_step(step, total_steps, "Context",
               f"Created '{default_ctx_name}' [OK]")
    return default_ctx_name, ctx_rg


def _update_context_if_needed(cmd, context_name, context_rg, level_label, capabilities):
    """Update existing context with new hierarchy level or capabilities if not already present."""
    try:
        ctx = invoke_cli_command(cmd, [
            "workload-orchestration", "context", "show",
            "-g", context_rg, "--name", context_name,
        ])
        if not ctx or not isinstance(ctx, dict):
            return

        props = ctx.get("properties", {})
        existing_hierarchies = [
            h.get("name", "").lower()
            for h in (props.get("hierarchies") or [])
        ]
        existing_capabilities = [
            c.get("name", "").lower()
            for c in (props.get("capabilities") or [])
        ]

        needs_update = False

        # Check if hierarchy level needs adding
        if level_label.lower() not in existing_hierarchies:
            logger.info("Adding hierarchy level '%s' to context", level_label)
            needs_update = True

        # Check if capabilities need adding
        if capabilities:
            new_caps = [c for c in capabilities if c.lower() not in existing_capabilities]
            if new_caps:
                logger.info("Adding capabilities %s to context", new_caps)
                needs_update = True

        if needs_update:
            # Context update with hierarchies/capabilities is complex,
            # log the need but don't auto-update to avoid breaking existing config
            logger.info(
                "Context '%s' may need hierarchy/capability updates. "
                "Run: az workload-orchestration context update ...",
                context_name
            )
    except Exception as exc:
        logger.debug("Could not check/update context: %s", exc)


# ---------------------------------------------------------------------------
# ARM helper (quiet - no output)
# ---------------------------------------------------------------------------

def _arm_put_quiet(cmd, url, body, api_version):
    """PUT request using send_raw_request with manual token for regional endpoints.

    We manually acquire the token with the correct subscription context and
    pass it as an Authorization header. This bypasses send_raw_request's
    built-in auth which fails on regional URLs (eastus2euap.management.azure.com)
    because it can't match them to a known cloud endpoint.
    """
    from azure.cli.core._profile import Profile

    full_url = f"{url}?api-version={api_version}"
    body_str = json.dumps(body) if isinstance(body, dict) else body
    logger.debug("PUT %s", full_url)

    # Get token manually with correct subscription
    profile = Profile(cli_ctx=cmd.cli_ctx)
    token_info, _, _ = profile.get_raw_token(
        resource="https://management.azure.com",
        subscription=profile.get_subscription_id()
    )
    token_type, token, _ = token_info

    send_raw_request(
        cmd.cli_ctx,
        method="PUT",
        url=full_url,
        body=body_str,
        headers=[
            f"Authorization={token_type} {token}",
            "Content-Type=application/json",
        ],
        skip_authorization_header=True,
    )


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def _print_hierarchy_diagnostic(step_results, name, resource_group):
    """Print diagnostic summary for hierarchy creation."""
    print("\n" + "=" * 60)
    print("  Hierarchy Creation - Diagnostic Summary")
    print(f"  Name: {name}")
    print(f"  Resource Group: {resource_group}")
    print(f"  Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print("=" * 60)

    for step_name, result in step_results.items():
        if "FAILED" in result:
            icon = "[FAIL]"
        elif "Warning" in result:
            icon = "[WARN]"
        else:
            icon = "[OK]"
        print(f"  {icon} {step_name}: {result}")

    has_failure = any("FAILED" in v for v in step_results.values())
    if has_failure:
        print("\n  [WARN] One or more steps failed.")
        print("  Re-run the command to retry - PUTs are idempotent (safe to re-run).")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_sub_id(cmd):
    """Get subscription ID from CLI context."""
    try:
        from azure.cli.core._profile import Profile
        profile = Profile(cli_ctx=cmd.cli_ctx)
        sub = profile.get_subscription()
        return sub.get("id", "")
    except Exception:
        return ""


def _get_tenant_id(cmd):
    """Get tenant ID from CLI context."""
    try:
        from azure.cli.core._profile import Profile
        profile = Profile(cli_ctx=cmd.cli_ctx)
        sub = profile.get_subscription()
        return sub.get("tenantId", "")
    except Exception:
        return ""
