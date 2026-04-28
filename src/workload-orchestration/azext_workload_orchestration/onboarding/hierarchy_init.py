# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Lightweight hierarchy initialization for target create --init-hierarchy.

Creates a simple site + configuration + config-reference + site-reference
in a resource group scope (no service group). This is the "RG-scoped"
hierarchy used when a user just wants a quick site without the full
hierarchy_create flow (which requires a Service Group parent).

Usage (called by target create --init-hierarchy):
    handle_init_hierarchy(cli_ctx, site_name, resource_group, location,
                          hierarchy_level, context_id)
"""

# pylint: disable=broad-exception-caught

import json
import logging

from azure.cli.core.util import send_raw_request

from azext_workload_orchestration.onboarding.consts import (
    ARM_ENDPOINT,
    SITE_API_VERSION,
    CONFIGURATION_API_VERSION,
    CONFIG_REF_API_VERSION,
)
from azext_workload_orchestration.onboarding.utils import (
    invoke_silent,
    parse_arm_id,
)

logger = logging.getLogger(__name__)


def handle_init_hierarchy(cli_ctx, site_name, resource_group, location,
                          hierarchy_level, context_id=None):
    """Create a minimal RG-scoped hierarchy: Site → Configuration → ConfigRef → SiteRef.

    Steps:
      1. PUT site at regional endpoint
      2. PUT configuration at regional endpoint
      3. PUT configuration-reference (links config → site)
      4. Create site-reference via CLI (links site → context)

    All PUTs are idempotent — safe to re-run.

    Args:
        cli_ctx: Azure CLI context (from self.ctx.cli_ctx)
        site_name: Name for the new site
        resource_group: Target resource group
        location: Azure region (e.g., eastus2euap)
        hierarchy_level: Level label (e.g., "line", "factory")
        context_id: Optional ARM ID of the context to link to
    """
    # Get subscription ID — prefer extracting from context_id, fall back to CLI profile
    if context_id:
        parts = parse_arm_id(context_id)
        sub_id = parts.get("subscriptions", "")
    else:
        sub_id = ""
    if not sub_id:
        from azure.cli.core._profile import Profile
        sub_id = Profile(cli_ctx=cli_ctx).get_subscription_id()
    regional_base = f"https://{location}.management.azure.com"

    site_id = (f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
               f"/providers/Microsoft.Edge/sites/{site_name}")
    config_id = (f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
                 f"/providers/Microsoft.Edge/configurations/{site_name}")

    print(f"[init-hierarchy] Creating site '{site_name}'...")

    # Step 1: Create Site (regional endpoint)
    _put_resource(
        cli_ctx,
        url=f"{regional_base}{site_id}?api-version={SITE_API_VERSION}",
        body={
            "properties": {
                "displayName": site_name,
                "description": site_name,
                "labels": {"level": hierarchy_level or "line"},
            }
        },
        label="Site",
    )

    # Step 2: Create Configuration (regional endpoint)
    _put_resource(
        cli_ctx,
        url=f"{regional_base}{config_id}?api-version={CONFIGURATION_API_VERSION}",
        body={"location": location},
        label="Configuration",
    )

    # Step 3: Create Configuration Reference (links config → site)
    config_ref_url = (
        f"{ARM_ENDPOINT}{site_id}"
        f"/providers/Microsoft.Edge/configurationreferences/default"
        f"?api-version={CONFIG_REF_API_VERSION}"
    )
    _put_resource(
        cli_ctx,
        url=config_ref_url,
        body={"properties": {"configurationResourceId": config_id}},
        label="Configuration Reference",
    )

    # Step 4: Create Site Reference (links site → context)
    if context_id:
        _create_site_reference(context_id, site_name, site_id)

    print(f"[init-hierarchy] Site '{site_name}' + config + references created [OK]")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _put_resource(cli_ctx, url, body, label):
    """PUT a resource via send_raw_request. Logs on failure but doesn't crash."""
    try:
        resp = send_raw_request(
            cli_ctx,
            method="PUT",
            url=url,
            body=json.dumps(body),
            resource=ARM_ENDPOINT,
            headers=["Content-Type=application/json"],
        )
        if resp.status_code in (200, 201):
            logger.info("%s created/updated successfully", label)
        else:
            logger.warning("%s PUT returned %d: %s", label, resp.status_code, resp.text)
    except Exception as exc:
        logger.warning("%s creation failed: %s", label, exc)
        raise


def _create_site_reference(context_id, site_name, site_id):
    """Create a site-reference linking the site to the context.

    Name format: <siteName>-<7-char sha256(lower(site_arm_id))>.
    7-char hash matches the BVT/Git convention (see ContextExtension.cs).
    """
    import hashlib
    import re

    parts = parse_arm_id(context_id)
    ctx_rg = parts.get("resourcegroups", "")
    ctx_name = parts.get("contexts", "default")

    if not ctx_rg:
        return

    # Site-reference name must satisfy ^[a-zA-Z0-9-]{3,24}$ — cap site portion at 16 chars
    hash_suffix = hashlib.sha256(site_id.lower().encode("utf-8")).hexdigest()[:7]
    sanitized = re.sub(r'[^a-zA-Z0-9-]', '-', site_name)[:16].rstrip("-")
    ref_name = f"{sanitized}-{hash_suffix}"

    try:
        invoke_silent([
            "workload-orchestration", "context", "site-reference", "create",
            "-g", ctx_rg, "--context-name", ctx_name,
            "--name", ref_name,
            "--site-id", site_id,
            "-o", "none",
        ])
    except Exception:
        pass  # Site reference may already exist
