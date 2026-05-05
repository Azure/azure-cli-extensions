# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Context capability management for Workload Orchestration.

Pure-Python helpers that GET the current context state,
normalize/dedup user input case-insensitively, compute the delta vs existing
capabilities, skip the ARM call entirely if there is no change (idempotent),
and otherwise issue ONE PATCH with only the capabilities array.

Exports:
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
    get_arm_endpoint,
    CONTEXT_API_VERSION,
)
from azext_workload_orchestration.common.utils import (
    CmdProxy,
    invoke_cli_command,
)

logger = logging.getLogger(__name__)


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
      - name + description (single capability shorthand — legacy, kept for internal use)
      - capabilities (list of dicts or strings)

    If description is missing from an item, defaults to name.
    Dedups case-insensitively on name. First occurrence wins.
    """
    items = []
    if name:
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
            "Provide --capabilities (JSON array of {name, description?})."
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
    """Normalize name/names into a deduped list of validated names.

    Accepts:
      - name: single string (legacy internal use)
      - names: list of strings (from --capabilities string array), or
               comma-separated string (legacy --names format)
    """
    raw = []
    if name and names:
        raise InvalidArgumentValueError("Specify either --cap-name or --capabilities, not both.")
    if name:
        raw.append(name)
    elif names:
        if isinstance(names, list):
            raw.extend([n.strip() for n in names if isinstance(n, str) and n.strip()])
        elif isinstance(names, str):
            raw.extend([n.strip() for n in names.split(",") if n.strip()])
        else:
            raise InvalidArgumentValueError("--capabilities must be a string array.")
    else:
        raise InvalidArgumentValueError("Provide --capabilities (string array of names to remove).")

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
        f"{get_arm_endpoint(cli_ctx)}/subscriptions/{sub_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Edge"
        f"/contexts/{context_name}?api-version={CONTEXT_API_VERSION}"
    )
    resp = send_raw_request(
        cli_ctx,
        method="PATCH",
        url=url,
        body=json.dumps(body),
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
