# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Delete policy values for an AI Manager resource.
DELETE_POLICY_KEEP = "Keep"
DELETE_POLICY_DELETE = "Delete"
DELETE_POLICIES = [DELETE_POLICY_KEEP, DELETE_POLICY_DELETE]

MODEL_DEPLOYMENT_PERFORMANCE_MODES = ["Balanced", "Latency", "Throughput"]

# Model source types. Constrains the legal authentication kinds for a model source.
MODEL_SOURCE_TYPE_HUGGING_FACE = "HuggingFace"
MODEL_SOURCE_TYPES = [MODEL_SOURCE_TYPE_HUGGING_FACE]
