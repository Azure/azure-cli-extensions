# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Context initialization for onboarding simplification.

Finds or creates a WO context, sets it as current, and ensures the required
capabilities and hierarchy levels are present.

Usage (called by target create --init-context):
    context_id = handle_init_context(cli_ctx, ctx_name, rg, location,
                                     hierarchy_level, capabilities)
"""

# pylint: disable=broad-exception-caught

import json
import logging

from azure.cli.core.azclierror import CLIInternalError

from azext_workload_orchestration.onboarding.consts import (
    ARM_ENDPOINT,
    CONTEXT_API_VERSION,
)
from azext_workload_orchestration.onboarding.utils import (
    CmdProxy,
    invoke_cli_command,
    invoke_silent,
    parse_arm_id,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def handle_init_context(cli_ctx, ctx_name, resource_group, location,
                        hierarchy_level, capabilities):
    """Find or create a WO context and return its ARM resource ID.

    Strategy (in order):
      1. Check if a context is already set in CLI config → use it
      2. List contexts in the target's resource group → use first match
      3. Create a new context with the given name
      4. If create fails (e.g. name conflict), search subscription-wide

    After resolving the context, ensures the required hierarchy level and
    capabilities are present (adds them if missing).

    Returns:
        str: The ARM resource ID of the context.

    Raises:
        CLIInternalError: If no context can be found or created.
    """
    import configparser

    cmd = CmdProxy(cli_ctx)

    # ------------------------------------------------------------------
    # 1. Check CLI config for an already-set context
    # ------------------------------------------------------------------
    try:
        existing_ctx_id = cli_ctx.config.get('workload_orchestration', 'context_id')
        if existing_ctx_id:
            logger.info("Context already set in config: %s", existing_ctx_id)
            _ensure_capabilities(cli_ctx, existing_ctx_id, hierarchy_level, capabilities)
            print("[init-context] Using existing context [OK]")
            return existing_ctx_id
    except (configparser.NoSectionError, configparser.NoOptionError):
        pass

    # ------------------------------------------------------------------
    # 2. List contexts in this resource group
    # ------------------------------------------------------------------
    try:
        existing = invoke_cli_command(cmd, [
            "workload-orchestration", "context", "list", "-g", resource_group
        ])
        if existing and isinstance(existing, list) and len(existing) > 0:
            ctx_id = existing[0].get("id", "")
            if ctx_id:
                parts = parse_arm_id(ctx_id)
                found_name = parts.get("contexts", ctx_name)
                found_rg = parts.get("resourcegroups", resource_group)
                _set_current(found_name, found_rg)
                _ensure_capabilities(cli_ctx, ctx_id, hierarchy_level, capabilities)
                print(f"[init-context] Using existing context '{found_name}' [OK]")
                return ctx_id
    except Exception:
        pass  # No contexts found — proceed to create

    # ------------------------------------------------------------------
    # 3. Create a new context
    # ------------------------------------------------------------------
    print(f"[init-context] Creating context '{ctx_name}'...")

    create_args = _build_create_args(ctx_name, resource_group, location,
                                     hierarchy_level, capabilities)
    exit_code = invoke_silent(create_args)

    if exit_code == 0:
        _set_current(ctx_name, resource_group)

        # Read back the context ID from config (set by 'context use')
        try:
            ctx_id = cli_ctx.config.get('workload_orchestration', 'context_id')
            if ctx_id:
                print(f"[init-context] Context '{ctx_name}' created [OK]")
                return ctx_id
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass

        # Fallback: construct the ID manually
        sub_id = cli_ctx.data.get('subscription_id', '')
        ctx_id = (f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
                  f"/providers/Microsoft.Edge/contexts/{ctx_name}")
        print(f"[init-context] Context '{ctx_name}' created [OK]")
        return ctx_id

    # ------------------------------------------------------------------
    # 4. Create failed — search subscription-wide
    # ------------------------------------------------------------------
    logger.warning("Context create returned exit %d. Searching subscription...", exit_code)
    ctx_id = _search_subscription(cli_ctx)
    if ctx_id:
        parts = parse_arm_id(ctx_id)
        found_name = parts.get("contexts", "unknown")
        found_rg = parts.get("resourcegroups", resource_group)
        _set_current(found_name, found_rg)
        _ensure_capabilities(cli_ctx, ctx_id, hierarchy_level, capabilities)
        print(f"[init-context] Using existing context '{found_name}' in RG '{found_rg}' [OK]")
        return ctx_id

    raise CLIInternalError(
        "Could not create or find an existing context. "
        "Please provide --context-id explicitly."
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_create_args(ctx_name, resource_group, location,
                       hierarchy_level, capabilities):
    """Build the arg list for 'az workload-orchestration context create'."""
    # Capabilities: [0].name=X [0].description=X [1].name=Y ...
    cap_args = []
    for i, cap in enumerate(capabilities or []):
        cap_args.extend([f"[{i}].name={cap}", f"[{i}].description={cap}"])

    hier_args = [f"[0].name={hierarchy_level}", f"[0].description={hierarchy_level}"]

    args = [
        "workload-orchestration", "context", "create",
        "-g", resource_group, "-l", location, "--name", ctx_name,
        "--hierarchies",
    ] + hier_args

    if cap_args:
        args.append("--capabilities")
        args.extend(cap_args)

    args.extend(["-o", "none"])
    return args


def _set_current(ctx_name, ctx_rg):
    """Set a context as the CLI default (silently)."""
    invoke_silent([
        "workload-orchestration", "context", "use",
        "--name", ctx_name, "-g", ctx_rg, "-o", "none",
    ])


def _search_subscription(cli_ctx):
    """Search the entire subscription for any existing context. Returns ID or None."""
    from azure.cli.core.util import send_raw_request

    sub_id = cli_ctx.data.get('subscription_id', '')
    try:
        resp = send_raw_request(
            cli_ctx,
            method="GET",
            url=(f"{ARM_ENDPOINT}/subscriptions/{sub_id}"
                 f"/providers/Microsoft.Edge/contexts"
                 f"?api-version={CONTEXT_API_VERSION}"),
            resource=ARM_ENDPOINT,
        )
        if resp.status_code == 200:
            contexts = resp.json().get("value", [])
            if contexts:
                return contexts[0].get("id")
    except Exception as exc:
        logger.warning("Subscription-wide context search failed: %s", exc)
    return None


def _ensure_capabilities(cli_ctx, ctx_id, hierarchy_level, capabilities):
    """Add missing capabilities/hierarchies to an existing context via PUT."""
    if not capabilities:
        return

    cmd = CmdProxy(cli_ctx)
    parts = parse_arm_id(ctx_id)
    ctx_rg = parts.get("resourcegroups")
    ctx_name = parts.get("contexts")
    sub_id = parts.get("subscriptions")

    if not ctx_rg or not ctx_name:
        return

    # Get current context state
    try:
        ctx_data = invoke_cli_command(cmd, [
            "workload-orchestration", "context", "show",
            "-g", ctx_rg, "--name", ctx_name,
        ])
    except Exception:
        return

    if not ctx_data or not isinstance(ctx_data, dict):
        return

    props = ctx_data.get("properties", {})
    existing_caps = {c.get("name", "") for c in (props.get("capabilities") or [])}
    existing_hiers = {h.get("name", "") for h in (props.get("hierarchies") or [])}

    missing_caps = [c for c in capabilities if c not in existing_caps]
    missing_hier = hierarchy_level not in existing_hiers

    if not missing_caps and not missing_hier:
        return  # Nothing to add

    # Merge existing + new
    all_caps = list(props.get("capabilities") or [])
    for cap in missing_caps:
        all_caps.append({"name": cap, "description": cap})

    all_hiers = list(props.get("hierarchies") or [])
    if missing_hier:
        all_hiers.append({"name": hierarchy_level, "description": hierarchy_level})

    print(f"[init-context] Adding capabilities {missing_caps} to context...")

    # PUT updated context
    from azure.cli.core.util import send_raw_request

    if not sub_id:
        sub_id = cli_ctx.data.get('subscription_id', '')

    location = ctx_data.get("location", "")
    body = {
        "location": location,
        "properties": {
            "capabilities": [{"name": c.get("name", ""), "description": c.get("description", "")}
                             for c in all_caps],
            "hierarchies": [{"name": h.get("name", ""), "description": h.get("description", "")}
                            for h in all_hiers],
        }
    }

    try:
        resp = send_raw_request(
            cli_ctx,
            method="PUT",
            url=(f"{ARM_ENDPOINT}/subscriptions/{sub_id}"
                 f"/resourceGroups/{ctx_rg}/providers/Microsoft.Edge"
                 f"/contexts/{ctx_name}?api-version={CONTEXT_API_VERSION}"),
            body=json.dumps(body),
            resource=ARM_ENDPOINT,
        )
        if resp.status_code in (200, 201):
            print("[init-context] Capabilities updated [OK]")
        else:
            logger.warning("Context update returned %d: %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.warning("Failed to update context capabilities: %s", exc)
