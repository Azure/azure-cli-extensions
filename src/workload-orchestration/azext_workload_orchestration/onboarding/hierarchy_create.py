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
        --hierarchy-spec "@hierarchy.yaml"

    hierarchy.yaml:
        name: Mehoopany
        level: factory

For ServiceGroup:
    az workload-orchestration hierarchy create \\
        --configuration-location eastus2euap \\
        --hierarchy-spec "@hierarchy.yaml"

    hierarchy.yaml:
        type: ServiceGroup
        name: India
        level: country
        children:
          name: Karnataka
          level: region
          children:
            - name: BangaloreSouth
              level: factory
"""

# pylint: disable=broad-exception-caught
# pylint: disable=too-many-locals

import json
import logging

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

    # Parse spec (could be dict from shorthand or file)
    spec = hierarchy_spec if isinstance(hierarchy_spec, dict) else hierarchy_spec

    name = spec.get("name")
    level = spec.get("level")
    hierarchy_type = spec.get("type", "ResourceGroup")

    if not name:
        raise ValidationError("hierarchy-spec must include 'name'.")
    if not level:
        raise ValidationError("hierarchy-spec must include 'level'.")

    if hierarchy_type == "ServiceGroup":
        return _create_sg_hierarchy(cmd, spec, configuration_location, resource_group)
    else:
        return _create_rg_hierarchy(cmd, resource_group, configuration_location, name, level)


# ---------------------------------------------------------------------------
# ResourceGroup hierarchy
# ---------------------------------------------------------------------------

def _create_rg_hierarchy(cmd, resource_group, config_location, name, level):
    """Create Site + Configuration + ConfigurationReference in a resource group."""
    sub_id = _get_sub_id(cmd)
    total = 3
    step = [0]

    def _log(msg, status=""):
        if status:
            print(f"[{step[0]}/{total}] {msg}... {status}")
        else:
            step[0] += 1
            print(f"[{step[0]}/{total}] {msg}...")

    site_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/{EDGE_RP_NAMESPACE}/sites/{name}"
    config_name = f"{name}Config"
    config_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/{EDGE_RP_NAMESPACE}/configurations/{config_name}"

    print(f"\nCreating hierarchy '{name}' (level: {level}) in RG '{resource_group}'...\n")

    # Step 1: Create Site
    _log(f"Site '{name}' ({level})")
    _arm_put(cmd, f"{ARM_ENDPOINT}{site_id}", {
        "properties": {
            "displayName": name,
            "description": name,
            "labels": {"level": level},
        }
    }, SITE_API_VERSION)
    _log(f"Site '{name}'", "[OK]")

    # Step 2: Create Configuration
    _log(f"Configuration '{config_name}'")
    _arm_put(cmd, f"{ARM_ENDPOINT}{config_id}", {
        "location": config_location,
    }, CONFIGURATION_API_VERSION)
    _log(f"Configuration '{config_name}'", "[OK]")

    # Step 3: Create ConfigurationReference (links site → config)
    config_ref_url = f"{ARM_ENDPOINT}{site_id}/providers/{EDGE_RP_NAMESPACE}/configurationReferences/default"
    _log("ConfigurationReference")
    _arm_put(cmd, config_ref_url, {
        "properties": {
            "configurationResourceId": config_id,
        }
    }, CONFIG_REF_API_VERSION)
    _log("ConfigurationReference", "[OK]")

    print(f"\nHierarchy '{name}' created successfully (3 resources).\n")

    return {
        "type": "ResourceGroup",
        "name": name,
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

    print(f"\nCreating ServiceGroup hierarchy '{spec['name']}' ({nodes} levels)...\n")

    results = []
    _create_sg_level(cmd, spec, config_location, sub_id, tenant_id,
                     resource_group, parent_sg=None, results=results, depth=0)

    print(f"\nHierarchy created successfully ({nodes} levels, {len(results)} resources).\n")

    return {
        "type": "ServiceGroup",
        "name": spec["name"],
        "levels": nodes,
        "resources": results,
    }


def _create_sg_level(cmd, node, config_location, sub_id, tenant_id, resource_group, parent_sg, results, depth):
    """Recursively create SG + Site + Config + ConfigRef at each level."""
    import time

    name = node["name"]
    level = node["level"]

    # Create or reference the ServiceGroup
    if parent_sg:
        parent_id = f"/providers/Microsoft.Management/serviceGroups/{parent_sg}"
    else:
        parent_id = f"/providers/Microsoft.Management/serviceGroups/{tenant_id}"

    sg_id = f"/providers/Microsoft.Management/serviceGroups/{name}"
    indent = "  " * depth

    # 1. Create ServiceGroup
    print(f"{indent}[+] ServiceGroup '{name}'...")
    try:
        _arm_put(cmd, f"{ARM_ENDPOINT}{sg_id}", {
            "properties": {
                "displayName": name,
                "parent": {"resourceId": parent_id},
            }
        }, SERVICE_GROUP_API_VERSION)
        print(f"{indent}[+] ServiceGroup '{name}'... [OK]")
        results.append({"type": "ServiceGroup", "name": name, "id": sg_id})
    except Exception as exc:
        logger.warning("ServiceGroup creation failed: %s", exc)
        raise CLIInternalError(f"ServiceGroup '{name}' creation failed: {exc}")

    # Wait for RBAC propagation on new SG scope
    print(f"{indent}    Waiting for RBAC propagation...")
    _wait_for_sg_rbac(cmd, config_location, sg_id, name)

    # 2. Create Site under ServiceGroup (regional endpoint)
    site_id = f"{sg_id}/providers/{EDGE_RP_NAMESPACE}/sites/{name}"
    print(f"{indent}  [+] Site '{name}' ({level})...")
    _arm_put_regional(cmd, config_location, site_id, {
        "properties": {
            "displayName": name,
            "description": name,
            "labels": {"level": level},
        }
    }, SITE_API_VERSION)
    print(f"{indent}  [+] Site '{name}'... [OK]")
    results.append({"type": "Site", "name": name, "level": level, "id": site_id})

    # 3. Create Configuration (RG-scoped, NOT under SG)
    config_name = f"{name}Config"
    config_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/{EDGE_RP_NAMESPACE}/configurations/{config_name}"
    print(f"{indent}  [+] Configuration '{config_name}' (in RG: {resource_group})...")
    _arm_put(cmd, f"{ARM_ENDPOINT}{config_id}", {
        "location": config_location,
    }, CONFIGURATION_API_VERSION)
    print(f"{indent}  [+] Configuration '{config_name}'... [OK]")
    results.append({"type": "Configuration", "name": config_name, "id": config_id})

    # 4. Create ConfigurationReference on Site (regional, links site -> RG config)
    config_ref_id = f"{site_id}/providers/{EDGE_RP_NAMESPACE}/configurationReferences/default"
    print(f"{indent}  [+] ConfigurationReference...")
    _arm_put_regional(cmd, config_location, config_ref_id, {
        "properties": {
            "configurationResourceId": config_id,
        }
    }, CONFIG_REF_API_VERSION)
    print(f"{indent}  [+] ConfigurationReference... [OK]")
    results.append({"type": "ConfigurationReference", "siteId": site_id})

    # Recurse into children
    children = node.get("children")
    if children:
        if isinstance(children, dict):
            children = [children]
        for child in children:
            _create_sg_level(cmd, child, config_location, sub_id, tenant_id,
                             resource_group, parent_sg=name, results=results, depth=depth + 1)


def _count_nodes(node):
    """Count total depth of hierarchy tree."""
    children = node.get("children")
    if not children:
        return 1
    if isinstance(children, dict):
        return 1 + _count_nodes(children)
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


def _wait_for_sg_rbac(cmd, location, sg_id, sg_name, max_retries=18, wait_sec=10):
    """Wait for RBAC to propagate on a newly created ServiceGroup.

    After SG creation, it takes time for permissions to propagate.
    We poll by trying to list sites under the SG until it succeeds.
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
                logger.warning(
                    "RBAC propagation timeout for SG '%s' after %ds. Continuing anyway...",
                    sg_name, max_retries * wait_sec
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
