# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Delete policy values for an AI Manager resource.
DELETE_POLICY_KEEP = "Keep"
DELETE_POLICY_DELETE = "Delete"
DELETE_POLICIES = [DELETE_POLICY_KEEP, DELETE_POLICY_DELETE]

# Built-in role definition GUIDs granted to the caller when they create an AI Manager or a
# namespace, so the creator can immediately manage (ARM) and read (K8S) the resource.
AIMANAGER_CONTRIBUTOR_ROLE_ID = "413f2675-4911-4010-be3b-c720b43a3c59"  # Azure AIManager Contributor
AIMANAGER_RBAC_READER_ROLE_ID = "9c77f8a7-b0b9-4462-844c-de6e66add8ba"  # Azure AIManager and namespace RBAC Reader
AIMANAGER_CALLER_ROLE_IDS = [AIMANAGER_CONTRIBUTOR_ROLE_ID, AIMANAGER_RBAC_READER_ROLE_ID]
AIMANAGER_ROLE_NAMES = {
    AIMANAGER_CONTRIBUTOR_ROLE_ID: "Azure AIManager Contributor",
    AIMANAGER_RBAC_READER_ROLE_ID: "Azure AIManager and namespace RBAC Reader",
}

MODEL_DEPLOYMENT_PERFORMANCE_MODES = ["Balanced", "Latency", "Throughput"]

# Table output projections for the 'az aimanager model' commands.
AI_MODEL_TABLE_TRANSFORMER = (
    "[].{Name:name, ModelId:properties.modelId, Description:properties.description}"
)

CALCULATE_COST_TABLE_TRANSFORMER = (
    "plans[].{VmSize:vmSize, Feasible:feasible, VmsPerReplica:vmsPerReplica, "
    "VmHourlyPrice:vmHourlyPrice, TotalHourlyPrice:totalHourlyPrice, "
    "MaxAvailableReplicas:maxAvailableReplicas, Quantization:quantization}"
)

# Supported model source types for an AI Manager model source.
MODEL_SOURCE_TYPES = ["HuggingFace"]
