# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Hierarchy create command - creates Site + Configuration + ConfigurationReference.

Supports two hierarchy types:
  - ResourceGroup: Single site in a resource group (no children)
  - ServiceGroup: Nested sites under a service group (up to 3 levels)

For ResourceGroup:
    az workload-orchestration hierarchy create \\
        --resource-group rg --configuration-location eastus2euap \\
        --hierarchy-spec hierarchy.yaml

    hierarchy.yaml:
        name: Mehoopany
        level: factory

For ServiceGroup:
    az workload-orchestration hierarchy create \\
        --configuration-location eastus2euap \\
        --hierarchy-spec hierarchy.yaml

    hierarchy.yaml:
        type: ServiceGroup
        name: India
        level: country
        children:
          - name: Karnataka
            level: region
            children:
              - name: BangaloreSouth
                level: factory

Note: ``children`` MUST be a list (even for a single child).
"""

# pylint: disable=broad-exception-caught
# pylint: disable=too-many-locals

import json
import logging
import re
import sys

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
)

logger = logging.getLogger(__name__)


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


MAX_SG_DEPTH = 3


def hierarchy_create(cmd, resource_group=None, configuration_location=None, hierarchy_spec=None):
    """Create a hierarchy: Site + Configuration + ConfigurationReference.

    Parses the hierarchy spec (YAML/JSON or shorthand) and creates
    the full resource stack.
    """
    if not hierarchy_spec:
        raise ValidationError("--hierarchy-spec is required.")
    if not configuration_location:
        raise ValidationError("--configuration-location is required.")
    if not resource_group:
        raise ValidationError("--resource-group is required (used for Configuration resources).")

    # Parse spec (dict from shorthand/file parser in the CLI wrapper)
    spec = hierarchy_spec

    name = spec.get("name")
    level = spec.get("level")
    hierarchy_type = spec.get("type", "ResourceGroup")

    if not name:
        raise ValidationError("hierarchy-spec must include 'name'.")
    if not level:
        raise ValidationError("hierarchy-spec must include 'level'.")

    # Validate all names in the hierarchy
    _validate_hierarchy_names(spec)

    if hierarchy_type == "ServiceGroup":
        return _create_sg_hierarchy(cmd, spec, configuration_location, resource_group)
    return _create_rg_hierarchy(cmd, resource_group, configuration_location, name, level)


_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]$')


def _validate_hierarchy_names(node):
    """Validate resource names in hierarchy spec before making REST calls."""
    name = node.get("name", "")
    if len(name) < 2 or len(name) > 63:
        raise ValidationError(
            f"Name '{name}' must be between 2 and 63 characters."
        )
    if not _NAME_PATTERN.match(name):
        raise ValidationError(
            f"Name '{name}' contains invalid characters. "
            f"Use only letters, numbers, and hyphens. Must start and end with alphanumeric."
        )
    children = node.get("children")
    if children is None:
        return
    if not isinstance(children, list):
        raise ValidationError(
            f"'children' for '{name}' must be a list. "
            f"Got {type(children).__name__}. "
            f"Use YAML '- name: X' entries or JSON '[{{...}}]'."
        )
    for child in children:
        _validate_hierarchy_names(child)


# ---------------------------------------------------------------------------
# ResourceGroup hierarchy
# ---------------------------------------------------------------------------

def _create_rg_hierarchy(cmd, resource_group, config_location, name, level):
    """Create Site + Configuration + ConfigurationReference in a resource group.

    A ResourceGroup hierarchy supports exactly ONE site per RG. If a site
    already exists (any name), reuse it and create/refresh Config + ConfigRef
    on top. Otherwise create a new site with the requested name.
    """
    sub_id = _get_sub_id(cmd)

    _eprint(f"\nCreating Hierarchy in Resource Group '{resource_group}'...\n")

    # Find-or-create site at RG scope (1 site per RG max)
    existing = _find_existing_site_in_rg(cmd, sub_id, resource_group)
    if existing:
        site_name, site_id = existing
        if site_name != name:
            _eprint(
                f"[i] Reusing existing Site '{site_name}' in Resource Group '{resource_group}' "
                f"(requested name '{name}' ignored)."
            )
        else:
            _eprint(f"[i] Reusing existing Site '{site_name}'.")
        effective_name = site_name
    else:
        effective_name = name
        site_id = (
            f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
            f"/providers/{EDGE_RP_NAMESPACE}/sites/{effective_name}"
        )
        _eprint(f"{effective_name} ({level})")
        _arm_put(cmd, f"{ARM_ENDPOINT}{site_id}", {
            "properties": {
                "displayName": effective_name,
                "description": effective_name,
                "labels": {"level": level},
            }
        }, SITE_API_VERSION)
        _eprint(f"├── Site '{effective_name}' ✓")

    config_name = f"{effective_name}Config"
    config_id = (
        f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
        f"/providers/{EDGE_RP_NAMESPACE}/configurations/{config_name}"
    )

    # Step 2: Configuration — find-or-create
    config_url = f"{ARM_ENDPOINT}{config_id}"
    if existing and _arm_get(cmd, config_url, CONFIGURATION_API_VERSION):
        _eprint(f"├── Configuration '{config_name}' (reused) ✓")
    else:
        _arm_put(cmd, config_url, {
            "location": config_location,
        }, CONFIGURATION_API_VERSION)
        _eprint(f"├── Configuration '{config_name}' ✓")

    # Step 3: ConfigurationReference — find-or-create (warn on mismatch)
    config_ref_url = (
        f"{ARM_ENDPOINT}{site_id}/providers/"
        f"{EDGE_RP_NAMESPACE}/configurationReferences/default"
    )
    existing_ref = _arm_get(cmd, config_ref_url, CONFIG_REF_API_VERSION) if existing else None
    if existing_ref:
        existing_target = (
            existing_ref.get("properties", {}).get("configurationResourceId", "")
        )
        if existing_target and existing_target.lower() != config_id.lower():
            _eprint(
                f"└── ConfigurationReference (reused — already points to "
                f"'{existing_target.rsplit('/', 1)[-1]}', leaving as-is) ✓"
            )
        else:
            _eprint("└── ConfigurationReference (reused) ✓")
    else:
        _arm_put(cmd, config_ref_url, {
            "properties": {
                "configurationResourceId": config_id,
            }
        }, CONFIG_REF_API_VERSION)
        _eprint("└── ConfigurationReference ✓")

    _eprint("\n✅ Hierarchy created (3 resources)\n")

    return {
        "type": "ResourceGroup",
        "name": effective_name,
        "level": level,
        "resourceGroup": resource_group,
        "siteId": site_id,
        "configurationId": config_id,
    }


# ---------------------------------------------------------------------------
# ServiceGroup hierarchy (recursive, max 3 levels)
# ---------------------------------------------------------------------------

def _create_sg_hierarchy(cmd, spec, config_location, resource_group):
    """Create ServiceGroup + nested Sites + Configurations recursively."""
    sub_id = _get_sub_id(cmd)
    tenant_id = _get_tenant_id(cmd)

    # Count total nodes
    nodes = _count_nodes(spec)
    if nodes > MAX_SG_DEPTH:
        raise ValidationError(
            f"ServiceGroup hierarchy has {nodes} levels. Maximum is {MAX_SG_DEPTH}."
        )

    _eprint(f"\nCreating ServiceGroup hierarchy '{spec['name']}' ({nodes} levels)...\n")

    results = []
    _create_sg_level(cmd, spec, config_location, sub_id, tenant_id,
                     resource_group, parent_sg=None, results=results,
                     depth=0, is_last=True)

    _eprint(f"\n✅ Hierarchy created ({nodes} levels, {len(results)} resources)\n")

    return {
        "type": "ServiceGroup",
        "name": spec["name"],
        "levels": nodes,
        "resources": results,
    }


def _create_sg_level(  # pylint: disable=too-many-arguments
    cmd, node, config_location, sub_id, tenant_id,
    resource_group, parent_sg, results, depth,
    is_last=True, parent_prefix="",
):
    """Recursively create SG + Site + Config + ConfigRef at each level."""
    name = node["name"]
    level = node["level"]

    if parent_sg:
        parent_id = f"/providers/Microsoft.Management/serviceGroups/{parent_sg}"
    else:
        parent_id = f"/providers/Microsoft.Management/serviceGroups/{tenant_id}"

    sg_id = f"/providers/Microsoft.Management/serviceGroups/{name}"

    # Tree drawing
    connector = "└── " if is_last else "├── "
    child_prefix = parent_prefix + ("    " if is_last else "│   ")

    # 1. Create ServiceGroup
    _eprint(f"{parent_prefix}{connector}{name} ({level})")
    try:
        _arm_put(cmd, f"{ARM_ENDPOINT}{sg_id}", {
            "properties": {
                "displayName": name,
                "parent": {"resourceId": parent_id},
            }
        }, SERVICE_GROUP_API_VERSION)
        results.append({"type": "ServiceGroup", "name": name, "id": sg_id})
    except Exception as exc:
        logger.warning("ServiceGroup creation failed: %s", exc)
        raise CLIInternalError(f"ServiceGroup '{name}' creation failed: {exc}")

    # Wait for RBAC propagation silently
    _wait_for_sg_rbac(cmd, config_location, sg_id, name)

    # 2. Find-or-create Site under this SG (1 site per SG max)
    existing_sg_site = _find_existing_site_in_sg(cmd, config_location, sg_id)
    if existing_sg_site:
        site_name, site_id = existing_sg_site
        if site_name != name:
            _eprint(
                f"{child_prefix}[i] Reusing existing Site '{site_name}' under ServiceGroup '{name}' "
                f"(requested name '{name}' ignored)."
            )
        effective_site_name = site_name
    else:
        effective_site_name = name
        site_id = f"{sg_id}/providers/{EDGE_RP_NAMESPACE}/sites/{effective_site_name}"
        _arm_put_regional(cmd, config_location, site_id, {
            "properties": {
                "displayName": effective_site_name,
                "description": effective_site_name,
                "labels": {"level": level},
            }
        }, SITE_API_VERSION)
    results.append({"type": "Site", "name": effective_site_name, "level": level, "id": site_id})

    # 3. Configuration — find-or-create
    config_name = f"{effective_site_name}Config"
    config_id = (
        f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
        f"/providers/{EDGE_RP_NAMESPACE}/configurations/{config_name}"
    )
    config_url = f"{ARM_ENDPOINT}{config_id}"
    config_reused = bool(existing_sg_site) and bool(_arm_get(cmd, config_url, CONFIGURATION_API_VERSION))
    if not config_reused:
        _arm_put(cmd, config_url, {
            "location": config_location,
        }, CONFIGURATION_API_VERSION)
    results.append({"type": "Configuration", "name": config_name, "id": config_id})

    # 4. ConfigurationReference — find-or-create
    config_ref_id = f"{site_id}/providers/{EDGE_RP_NAMESPACE}/configurationReferences/default"
    existing_ref = (
        _arm_get_regional(cmd, config_location, config_ref_id, CONFIG_REF_API_VERSION)
        if existing_sg_site else None
    )
    ref_target_mismatch = False
    if existing_ref:
        existing_target = existing_ref.get("properties", {}).get("configurationResourceId", "")
        ref_target_mismatch = bool(
            existing_target and existing_target.lower() != config_id.lower()
        )
    if not existing_ref:
        _arm_put_regional(cmd, config_location, config_ref_id, {
            "properties": {
                "configurationResourceId": config_id,
            }
        }, CONFIG_REF_API_VERSION)
    results.append({"type": "ConfigurationReference", "siteId": site_id})

    # Show resources created/reused under this node
    children = node.get("children")
    has_children = children is not None
    site_label = "(reused) " if existing_sg_site else ""
    config_label = "(reused) " if config_reused else ""
    if existing_ref:
        if ref_target_mismatch:
            ref_label = "(reused — points to different config, leaving as-is) "
        else:
            ref_label = "(reused) "
    else:
        ref_label = ""
    _eprint(f"{child_prefix}├── Site '{effective_site_name}' {site_label}✓")
    _eprint(f"{child_prefix}├── Configuration '{config_name}' {config_label}✓")
    if has_children:
        _eprint(f"{child_prefix}├── ConfigurationReference {ref_label}✓")
    else:
        _eprint(f"{child_prefix}└── ConfigurationReference {ref_label}✓")

    # Recurse into children
    if children:
        if not isinstance(children, list):
            raise ValidationError(
                f"'children' for '{name}' must be a list. "
                f"Got {type(children).__name__}."
            )
        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            _create_sg_level(cmd, child, config_location, sub_id, tenant_id,
                             resource_group, parent_sg=name, results=results,
                             depth=depth + 1, is_last=child_is_last,
                             parent_prefix=child_prefix)


def _count_nodes(node):
    """Count total depth of hierarchy tree."""
    children = node.get("children")
    if not children:
        return 1
    if not isinstance(children, list):
        raise ValidationError(
            f"'children' for '{node.get('name', '?')}' must be a list."
        )
    return 1 + max(_count_nodes(c) for c in children)


# ---------------------------------------------------------------------------
# ARM helpers
# ---------------------------------------------------------------------------

def _arm_put(cmd, url, body, api_version):
    """PUT to ARM endpoint."""
    full_url = f"{url}?api-version={api_version}"
    send_raw_request(
        cmd.cli_ctx, "PUT", full_url,
        body=json.dumps(body),
        headers=["Content-Type=application/json"],
        resource=ARM_ENDPOINT,
    )


def _arm_get(cmd, url, api_version):
    """GET from (global) ARM endpoint and return parsed JSON, or None on 404."""
    full_url = f"{url}?api-version={api_version}"
    try:
        resp = send_raw_request(
            cmd.cli_ctx, "GET", full_url,
            resource=ARM_ENDPOINT,
        )
    except Exception as exc:  # pylint: disable=broad-except
        if "ResourceNotFound" in str(exc) or "404" in str(exc):
            return None
        logger.debug("GET %s failed: %s", full_url, exc)
        return None
    try:
        return resp.json()
    except Exception as exc:  # pylint: disable=broad-except
        logger.debug("GET %s json parse failed: %s", full_url, exc)
        try:
            return json.loads(resp.content)
        except Exception:  # pylint: disable=broad-except
            return None


def _check_rg_has_no_other_site(cmd, sub_id, resource_group, intended_name):  # legacy, kept for back-compat callers
    site = _find_existing_site_in_rg(cmd, sub_id, resource_group)
    if site and site[0] != intended_name:
        raise ValidationError(
            f"Resource group '{resource_group}' already contains site '{site[0]}'. "
            f"A ResourceGroup hierarchy supports only one site per RG."
        )


def _find_existing_site_in_rg(cmd, sub_id, resource_group):
    """Return (name, site_id) of the first site found in the RG, else None."""
    list_url = (
        f"{ARM_ENDPOINT}/subscriptions/{sub_id}/resourceGroups/{resource_group}"
        f"/providers/{EDGE_RP_NAMESPACE}/sites"
    )
    payload = _arm_get(cmd, list_url, SITE_API_VERSION)
    if not payload:
        return None
    items = payload.get("value", []) if isinstance(payload, dict) else []
    if not items:
        return None
    first = items[0]
    name = first.get("name")
    site_id = first.get("id") or (
        f"/subscriptions/{sub_id}/resourceGroups/{resource_group}"
        f"/providers/{EDGE_RP_NAMESPACE}/sites/{name}"
    )
    return (name, site_id) if name else None


def _find_existing_site_in_sg(cmd, location, sg_id):
    """Return (name, site_id) of the first site found under the SG, else None.

    Uses the regional management endpoint because Sites under a ServiceGroup
    are tenant-scoped resources accessed via the regional plane.
    """
    list_id = f"{sg_id}/providers/{EDGE_RP_NAMESPACE}/sites"
    full_url = f"https://{location}.management.azure.com{list_id}?api-version={SITE_API_VERSION}"
    token_type, token = _get_token(cmd)
    try:
        resp = send_raw_request(
            cmd.cli_ctx, "GET", full_url,
            headers=[f"Authorization={token_type} {token}"],
            skip_authorization_header=True,
        )
        payload = resp.json()
    except Exception as exc:  # pylint: disable=broad-except
        if "ResourceNotFound" in str(exc) or "404" in str(exc):
            return None
        # On any other transient error, fall through to create-path
        logger.debug("SG site list failed (%s); proceeding to create.", exc)
        return None
    items = payload.get("value", []) if isinstance(payload, dict) else []
    if not items:
        return None
    first = items[0]
    name = first.get("name")
    site_id = first.get("id") or f"{sg_id}/providers/{EDGE_RP_NAMESPACE}/sites/{name}"
    return (name, site_id) if name else None


def _arm_put_regional(cmd, location, resource_id, body, api_version):
    """PUT to regional ARM endpoint (for SG-scoped resources)."""
    full_url = f"https://{location}.management.azure.com{resource_id}?api-version={api_version}"
    body_str = json.dumps(body)

    token_type, token = _get_token(cmd)

    send_raw_request(
        cmd.cli_ctx, "PUT", full_url,
        body=body_str,
        headers=[
            f"Authorization={token_type} {token}",
            "Content-Type=application/json",
        ],
        skip_authorization_header=True,
    )


def _arm_get_regional(cmd, location, resource_id, api_version):
    """GET from regional ARM endpoint."""
    full_url = f"https://{location}.management.azure.com{resource_id}?api-version={api_version}"

    token_type, token = _get_token(cmd)

    resp = send_raw_request(
        cmd.cli_ctx, "GET", full_url,
        headers=[
            f"Authorization={token_type} {token}",
        ],
        skip_authorization_header=True,
    )
    return resp


def _wait_for_sg_rbac(cmd, location, sg_id, sg_name, max_retries=12, wait_sec=10):
    """Wait for RBAC to propagate on a newly created ServiceGroup.

    After SG creation, it takes time for permissions to propagate.
    We poll by trying to list sites under the SG until it succeeds.
    Waits up to 120s (12 x 10s).
    """
    import time

    site_list_id = f"{sg_id}/providers/{EDGE_RP_NAMESPACE}/sites"

    for attempt in range(max_retries):
        try:
            _arm_get_regional(cmd, location, site_list_id, SITE_API_VERSION)
            logger.info("RBAC propagated for SG '%s' after %ds", sg_name, attempt * wait_sec)
            return
        except Exception:
            if attempt < max_retries - 1:
                logger.debug("RBAC not ready (attempt %d/%d), waiting %ds...", attempt + 1, max_retries, wait_sec)
                time.sleep(wait_sec)
            else:
                raise CLIInternalError(
                    f"RBAC propagation timeout for ServiceGroup '{sg_name}' after {max_retries * wait_sec}s. "
                    f"Retry the command — the ServiceGroup exists, RBAC just needs more time."
                )


def _get_token(cmd):
    """Get ARM bearer token."""
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    token_info, _, _ = profile.get_raw_token(
        resource="https://management.azure.com",
        subscription=profile.get_subscription_id()
    )
    return token_info[0], token_info[1]  # token_type, token


def _get_sub_id(cmd):
    """Get subscription ID."""
    sub_id = cmd.cli_ctx.data.get('subscription_id')
    if not sub_id:
        from azure.cli.core._profile import Profile
        sub_id = Profile(cli_ctx=cmd.cli_ctx).get_subscription_id()
    return sub_id


def _get_tenant_id(cmd):
    """Get tenant ID."""
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    _, _, tenant_id = profile.get_raw_token(resource="https://management.azure.com")
    return tenant_id
