# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Context initialization and capability management for Workload Orchestration.

Consolidated from context_init.py and context_capability.py.

context_init: Finds or creates a WO context, sets it as current, and ensures
the required capabilities and hierarchy levels are present.

context_capability: Pure-Python helpers that GET the current context state,
normalize/dedup user input case-insensitively, compute the delta vs existing
capabilities, skip the ARM call entirely if there is no change (idempotent),
and otherwise issue ONE PATCH with only the capabilities array.

Exports:
    handle_init_context(cli_ctx, ...)
    capability_add(cli_ctx, ...)
    capability_remove(cli_ctx, ...)
    capability_list(cli_ctx, ...)
    capability_show(cli_ctx, ...)
"""

# pylint: disable=broad-exception-caught

import json
import logging
import re
import sys

from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
)
from azure.cli.core.util import send_raw_request

from azext_workload_orchestration.common.consts import (
    ARM_ENDPOINT,
    CONTEXT_API_VERSION,
)
from azext_workload_orchestration.common.utils import (
    CmdProxy,
    invoke_cli_command,
    invoke_silent,
    parse_arm_id,
)

logger = logging.getLogger(__name__)


# ===========================================================================
# context_init — Public entry point
# ===========================================================================

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
        if existing and isinstance(existing, list):
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
# context_init — Private helpers
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
        return

    all_caps = list(props.get("capabilities") or [])
    for cap in missing_caps:
        all_caps.append({"name": cap, "description": cap})

    all_hiers = list(props.get("hierarchies") or [])
    if missing_hier:
        all_hiers.append({"name": hierarchy_level, "description": hierarchy_level})

    print(f"[init-context] Adding capabilities {missing_caps} to context...")

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


# ===========================================================================
# context_capability — Constants
# ===========================================================================

_CAP_NAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-_.]*[a-zA-Z0-9])?$")
_MAX_CAP_NAME_LEN = 61


# ---------------------------------------------------------------------------
# context_capability — Validation
# ---------------------------------------------------------------------------


def _validate_cap_name(name):
    """Validate and return a trimmed capability name."""
    if not name or not isinstance(name, str):
        raise InvalidArgumentValueError(
            "Capability name is required and must be a non-empty string."
        )
    name = name.strip()
    if not name:
        raise InvalidArgumentValueError("Capability name cannot be whitespace.")
    if len(name) > _MAX_CAP_NAME_LEN:
        raise InvalidArgumentValueError(
            f"Capability name '{name[:20]}...' exceeds {_MAX_CAP_NAME_LEN} characters."
        )
    if not _CAP_NAME_RE.match(name):
        raise InvalidArgumentValueError(
            f"Capability name '{name}' has invalid characters. "
            f"Allowed: alphanumerics, hyphens, underscores, and dots."
        )
    return name


# ---------------------------------------------------------------------------
# context_capability — Input normalization
# ---------------------------------------------------------------------------


def _normalize_input(name, description, capabilities):
    """Normalize user input into a deduped list of {name, description} dicts.

    Accepts:
      - name + description (single capability shorthand)
      - capabilities (list of dicts or strings)

    Dedups case-insensitively on name. First occurrence wins.
    """
    items = []
    if name:
        if capabilities:
            raise InvalidArgumentValueError(
                "Specify either --cap-name (with --description) or --capabilities, not both."
            )
        nm = _validate_cap_name(name)
        desc = description if description else nm
        items.append({"name": nm, "description": desc})
    elif capabilities:
        if isinstance(capabilities, str):
            try:
                capabilities = json.loads(capabilities)
            except (ValueError, TypeError) as exc:
                raise InvalidArgumentValueError(
                    "--capabilities must be a JSON array, shorthand list, or @file."
                ) from exc
        if not isinstance(capabilities, list):
            raise InvalidArgumentValueError(
                f"--capabilities must be a list (got {type(capabilities).__name__})."
            )
        for entry in capabilities:
            if isinstance(entry, str):
                nm = _validate_cap_name(entry)
                items.append({"name": nm, "description": nm})
            elif isinstance(entry, dict):
                nm = _validate_cap_name(entry.get("name"))
                desc = entry.get("description") or nm
                items.append({"name": nm, "description": desc})
            else:
                raise InvalidArgumentValueError(
                    "Each capability must be a string or object with 'name'."
                )
    else:
        raise InvalidArgumentValueError(
            "Provide either --cap-name + --description (single) or --capabilities (bulk)."
        )

    seen = set()
    deduped = []
    for item in items:
        key = item["name"].lower()
        if key in seen:
            logger.debug("Skipping duplicate input capability: %s", item["name"])
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _normalize_names_input(name, names):
    """Normalize name/names into a deduped list of validated names."""
    raw = []
    if name and names:
        raise InvalidArgumentValueError("Specify either --cap-name or --names, not both.")
    if name:
        raw.append(name)
    elif names:
        if isinstance(names, str):
            raw.extend([n.strip() for n in names.split(",") if n.strip()])
        elif isinstance(names, list):
            raw.extend(names)
        else:
            raise InvalidArgumentValueError("--names must be a string or list.")
    else:
        raise InvalidArgumentValueError("Provide --cap-name or --names.")

    seen = set()
    deduped = []
    for n in raw:
        nm = _validate_cap_name(n)
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        deduped.append(nm)
    return deduped


# ---------------------------------------------------------------------------
# context_capability — Context fetch and PATCH
# ---------------------------------------------------------------------------


def _fetch_context(cli_ctx, resource_group, context_name, subscription=None):
    """GET the context resource. Returns (context_dict, subscription_id)."""
    cmd = CmdProxy(cli_ctx)
    args = ["workload-orchestration", "context", "show",
            "-g", resource_group, "--name", context_name]
    if subscription:
        args.extend(["--subscription", subscription])
    try:
        ctx = invoke_cli_command(cmd, args)
    except Exception as exc:
        raise ResourceNotFoundError(
            f"Context '{context_name}' not found in resource group '{resource_group}'."
        ) from exc
    if not ctx or not isinstance(ctx, dict):
        raise ResourceNotFoundError(
            f"Context '{context_name}' returned empty or invalid data."
        )
    sub_id = subscription or cli_ctx.data.get("subscription_id", "")
    arm_id = ctx.get("id", "")
    if arm_id and "/subscriptions/" in arm_id:
        try:
            sub_id = arm_id.split("/subscriptions/")[1].split("/")[0]
        except IndexError:
            pass
    return ctx, sub_id


def _sanitize_caps(caps):
    """Ensure capabilities list contains only plain {name, description} dicts."""
    sanitized = []
    for c in caps:
        entry = {
            "name": str(c.get("name", "")),
            "description": str(c.get("description", c.get("name", ""))),
        }
        sanitized.append(entry)
    return sanitized


def _patch_context_capabilities(cli_ctx, sub_id, resource_group,
                                context_name, capabilities_list):
    """PATCH the context with the given capabilities list."""
    body = {
        "properties": {
            "capabilities": [
                {"name": c["name"], "description": c.get("description", c["name"])}
                for c in capabilities_list
            ]
        }
    }
    url = (
        f"{ARM_ENDPOINT}/subscriptions/{sub_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Edge"
        f"/contexts/{context_name}?api-version={CONTEXT_API_VERSION}"
    )
    resp = send_raw_request(
        cli_ctx,
        method="PATCH",
        url=url,
        body=json.dumps(body),
        resource=ARM_ENDPOINT,
    )
    if resp.status_code not in (200, 201, 202):
        raise CLIInternalError(
            f"Context PATCH failed: {resp.status_code} {resp.text}"
        )
    try:
        return resp.json()
    except (ValueError, AttributeError):
        return {"status_code": resp.status_code}


# ---------------------------------------------------------------------------
# context_capability — Helpers
# ---------------------------------------------------------------------------


def _existing_caps(ctx):
    """Extract capabilities list from context dict."""
    return list((ctx.get("properties") or {}).get("capabilities") or [])


def _log(msg):
    """Print status message to stderr (visible to user but not in JSON output)."""
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# context_capability — Public API
# ---------------------------------------------------------------------------


def capability_add(cli_ctx, resource_group, context_name, name=None,
                   description=None, capabilities=None, subscription=None,
                   state=None):  # pylint: disable=unused-argument
    """Add capabilities to a context. Idempotent - skips if already present."""
    requested = _normalize_input(name, description, capabilities)

    ctx, sub_id = _fetch_context(cli_ctx, resource_group, context_name, subscription)
    existing = _sanitize_caps(_existing_caps(ctx))
    existing_lower = {c["name"].lower() for c in existing}

    added = [e for e in requested if e["name"].lower() not in existing_lower]
    skipped = [e for e in requested if e["name"].lower() in existing_lower]

    if not added:
        count = len(existing)
        _log(f"No changes needed \u2014 all {len(skipped)} capability(ies) already exist. "
             f"({count} total)")
        return ctx

    merged = existing + added
    names_str = ", ".join(c["name"] for c in added)
    _log(f"Adding {len(added)}: {names_str}")

    updated = _patch_context_capabilities(
        cli_ctx, sub_id, resource_group, context_name, merged
    )
    _log(f"\u2713 Done ({len(merged)} total capabilities)")
    return updated


def capability_remove(cli_ctx, resource_group, context_name, name=None,
                      names=None, force=False, yes=False, subscription=None):  # noqa: E501
    """Remove capabilities from a context. Idempotent - skips if not present."""
    if force:
        logger.debug("Force mode enabled — skipping in-use checks.")
    target_names = _normalize_names_input(name, names)

    ctx, sub_id = _fetch_context(cli_ctx, resource_group, context_name, subscription)
    existing = _sanitize_caps(_existing_caps(ctx))

    target_lower = {n.lower() for n in target_names}
    to_remove = [c for c in existing if c["name"].lower() in target_lower]
    not_found = [n for n in target_names
                 if n.lower() not in {c["name"].lower() for c in existing}]

    if not_found:
        logger.debug("Capabilities not found on context: %s", not_found)

    if not to_remove:
        _log(f"No changes needed \u2014 none of the {len(target_names)} "
             f"capability(ies) exist on context. ({len(existing)} total)")
        return ctx

    remaining = [c for c in existing if c["name"].lower() not in target_lower]

    if not remaining:
        raise InvalidArgumentValueError(
            "Cannot remove the last capability \u2014 a context must have at least one. "
            "Add a replacement first or delete the context."
        )

    if not yes:
        names_str = ", ".join(c["name"] for c in to_remove)
        try:
            from knack.prompting import prompt_y_n
            if not prompt_y_n(
                f"Remove {len(to_remove)} capability(ies) [{names_str}] "
                f"from '{context_name}'?"
            ):
                _log("Cancelled.")
                return ctx
        except Exception as exc:
            raise InvalidArgumentValueError(
                "Use --yes to confirm removal in non-interactive sessions."
            ) from exc

    names_str = ", ".join(c["name"] for c in to_remove)
    _log(f"Removing {len(to_remove)}: {names_str}")

    updated = _patch_context_capabilities(
        cli_ctx, sub_id, resource_group, context_name, remaining
    )
    _log(f"\u2713 Done ({len(remaining)} total capabilities)")
    return updated


def capability_list(cli_ctx, resource_group, context_name, filter_pattern=None,
                    subscription=None):
    """List capabilities on a context."""
    ctx, _ = _fetch_context(cli_ctx, resource_group, context_name, subscription)
    caps = _sanitize_caps(_existing_caps(ctx))
    if filter_pattern:
        regex = re.compile(
            "^" + re.escape(filter_pattern).replace(r"\*", ".*") + "$",
            re.IGNORECASE,
        )
        caps = [c for c in caps if regex.match(c.get("name", ""))]
    return caps


def capability_show(cli_ctx, resource_group, context_name, name,
                    subscription=None):
    """Show a single capability by name (case-insensitive)."""
    nm = _validate_cap_name(name)
    ctx, _ = _fetch_context(cli_ctx, resource_group, context_name, subscription)
    caps = _sanitize_caps(_existing_caps(ctx))
    for c in caps:
        if c["name"].lower() == nm.lower():
            return c
    raise ResourceNotFoundError(
        f"Capability '{name}' not found on context '{context_name}'."
    )
