# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Constants for workload orchestration CLI commands."""

# pylint: disable=line-too-long

# ---------------------------------------------------------------------------
# API Versions
# ---------------------------------------------------------------------------
SERVICE_GROUP_API_VERSION = "2024-02-01-preview"
SITE_API_VERSION = "2025-06-01"
CONFIGURATION_API_VERSION = "2025-08-01"
CONFIG_REF_API_VERSION = "2025-08-01"
TARGET_API_VERSION = "2025-08-01"
SG_MEMBER_API_VERSION = "2023-09-01-preview"
CONTEXT_API_VERSION = "2025-08-01"

# ---------------------------------------------------------------------------
# ARM Endpoints
# ---------------------------------------------------------------------------
ARM_ENDPOINT = "https://management.azure.com"  # fallback default


def get_arm_endpoint(cmd_or_cli_ctx):
    """Get ARM endpoint from active cloud configuration.

    Accepts either a cmd object (cmd.cli_ctx) or a cli_ctx directly.
    Returns the resource_manager endpoint configured via
    ``az cloud update --endpoint-resource-manager``.
    """
    try:
        cli_ctx = getattr(cmd_or_cli_ctx, "cli_ctx", cmd_or_cli_ctx)
        return cli_ctx.cloud.endpoints.resource_manager.rstrip("/")
    except AttributeError:
        return ARM_ENDPOINT


def get_regional_arm_endpoint(cmd_or_cli_ctx, location):
    """Build the regional ARM endpoint URL prefix.

    Constructs ``https://{location}.{domain}`` from the active cloud config,
    so it works across sovereign clouds and custom endpoints.
    """
    from urllib.parse import urlparse
    base = get_arm_endpoint(cmd_or_cli_ctx)
    hostname = urlparse(base).hostname or "management.azure.com"
    return f"https://{location}.{hostname}"


# ---------------------------------------------------------------------------
# Resource Providers
# ---------------------------------------------------------------------------
EDGE_RP_NAMESPACE = "Microsoft.Edge"

# ---------------------------------------------------------------------------
# cert-manager + trust-manager Defaults (installed via AIO Platform extension)
# ---------------------------------------------------------------------------
DEFAULT_CERT_MANAGER_VERSION = None  # None = AIO extension default

# Registry of extension dependencies for `--extension-dependency-version`.
# Keys are the user-facing names; values configure the Arc extension install.
EXTENSION_DEPENDENCIES = {
    "iotplatform": {
        "extension_type": "microsoft.iotoperations.platform",
        "extension_name": "aio-certmgr",
        "namespace": "cert-manager",
        "scope": "cluster",
        "default_version": None,
    },
}

# ---------------------------------------------------------------------------
# AIO Platform Extension (bundles cert-manager + trust-manager)
# ---------------------------------------------------------------------------
AIO_PLATFORM_EXTENSION_TYPE = "microsoft.iotoperations.platform"
AIO_PLATFORM_EXTENSION_NAME = "aio-certmgr"
AIO_PLATFORM_EXTENSION_NAMESPACE = "cert-manager"
AIO_PLATFORM_EXTENSION_SCOPE = "cluster"

# ---------------------------------------------------------------------------
# WO Extension Defaults
# ---------------------------------------------------------------------------
DEFAULT_EXTENSION_TYPE = "Microsoft.workloadorchestration"
DEFAULT_EXTENSION_NAME = "wo-extension"
DEFAULT_RELEASE_TRAIN = "stable"
DEFAULT_EXTENSION_NAMESPACE = "workloadorchestration"
DEFAULT_EXTENSION_SCOPE = "cluster"
DEFAULT_STORAGE_SIZE = "20Gi"
