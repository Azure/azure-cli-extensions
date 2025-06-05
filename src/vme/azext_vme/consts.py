# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

HELM_MCR_URL = "mcr.microsoft.com/azurearck8s/helm"
HELM_VERSION = "v3.12.2"
CONNECTEDCLUSTER_RP = "Microsoft.Kubernetes"
CONNECTEDCLUSTER_TYPE = "connectedClusters"
ArcAgentProfile = "arcAgentProfile"
ArcAgentAutoUpgrade = "agentAutoUpgrade"
ArcAgentryConfigurations = "arcAgentryConfigurations"
ArcAgentryBundleFeatureName = "extensionSets"
ArcAgentryBundleSettingsName = "versionManagedExtensions"
ARC_UPDATE_PREFIX = "Arc-Update-"
AGENT_VERSION_TAG = "AgentVersion"
FAILED = "Failed"
SUCCEEDED = "Succeeded"
CANCELLED = "Cancelled"
Bundle_FeatureFlag_NotEnabled = "Bundle feature flag is not enabled."
UPGRADE_IN_PROGRESS_MSG = "Version managed extensions upgrade is in progress..."
UPGRADE_SUCCEEDED_MSG = "Version managed extensions upgrade completed!"
UPGRADE_FAILED_MSG = "Version managed extensions upgrade failed. Error: "
UPGRADE_CANCELED_MSG = "Version managed extensions upgrade is canceled."
UPGRADE_NOTSTARTED_MSG = "Waiting for version managed extensions upgrade to start..."
UPGRADE_TIMEOUT_MSG = """
Error: version managed extensions upgrade could not start in {0} seconds. Check out common issues here: <url>
"""
UPGRADE_CHECK_INTERVAL = 5
BundleExtensionTypes = [
    "microsoft.arc.containerstorage",
    "microsoft.azure.secretstore"
]

BundleExtensionTypeNames = {
    "microsoft.arc.containerstorage": "azure-arc-containerstorage",
    "microsoft.azure.secretstore": "azure-secret-store",
}

IncludedExtensionTypes = BundleExtensionTypes + ["all"]
BundleExtensionNames = [
    "azure-arc-containerstorage",
    "azure-secret-store",
    "microsoft.extensiondiagnostics-v0"
]
