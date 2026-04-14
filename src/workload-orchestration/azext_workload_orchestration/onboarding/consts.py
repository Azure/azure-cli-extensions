# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Constants for onboarding simplification commands."""

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
ARM_ENDPOINT = "https://management.azure.com"
ARM_RESOURCE = "https://management.azure.com"

# ---------------------------------------------------------------------------
# Resource Providers
# ---------------------------------------------------------------------------
EDGE_RP_NAMESPACE = "Microsoft.Edge"
SERVICE_GROUP_RP = "Microsoft.Management"
RELATIONSHIPS_RP = "Microsoft.Relationships"

# ---------------------------------------------------------------------------
# cert-manager Defaults
# ---------------------------------------------------------------------------
DEFAULT_CERT_MANAGER_VERSION = "v1.15.3"
CERT_MANAGER_MANIFEST_URL = (
    "https://github.com/cert-manager/cert-manager/releases/download"
    "/{version}/cert-manager.yaml"
)
CERT_MANAGER_NAMESPACE = "cert-manager"
CERT_MANAGER_WEBHOOK_DEPLOYMENT = "cert-manager-webhook"
CERT_MANAGER_MIN_PODS = 3  # webhook, controller, cainjector

# ---------------------------------------------------------------------------
# trust-manager Defaults
# ---------------------------------------------------------------------------
TRUST_MANAGER_DEPLOYMENT = "trust-manager"
TRUST_MANAGER_HELM_REPO = "https://charts.jetstack.io"
TRUST_MANAGER_HELM_REPO_NAME = "jetstack"
TRUST_MANAGER_HELM_CHART = "jetstack/trust-manager"

# ---------------------------------------------------------------------------
# WO Extension Defaults
# ---------------------------------------------------------------------------
DEFAULT_EXTENSION_TYPE = "Microsoft.workloadorchestration"
DEFAULT_EXTENSION_NAME = "wo-extension"
DEFAULT_RELEASE_TRAIN = "stable"
DEFAULT_EXTENSION_NAMESPACE = "workloadorchestration"
DEFAULT_EXTENSION_SCOPE = "cluster"

# ---------------------------------------------------------------------------
# Limits & Timeouts
# ---------------------------------------------------------------------------
MAX_HIERARCHY_NAME_LENGTH = 24  # Configuration resource name limit
LRO_TIMEOUT_SECONDS = 600  # 10 minutes per LRO step
LRO_DEFAULT_POLL_INTERVAL = 15  # seconds, overridden by Retry-After header
CERT_MANAGER_WAIT_TIMEOUT = "300s"

# ---------------------------------------------------------------------------
# Default Target Specification (helm.v3)
# ---------------------------------------------------------------------------
DEFAULT_TARGET_SPECIFICATION = {
    "topologies": [{
        "bindings": [{
            "role": "helm.v3",
            "provider": "providers.target.helm",
            "config": {"inCluster": "true"}
        }]
    }]
}
