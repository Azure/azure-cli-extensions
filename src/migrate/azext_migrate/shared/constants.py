# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Constants shared across all migrate feature packages."""

# Resource provider namespace (canonical casing).
PROVIDER_NAMESPACE = "Microsoft.Migrate"

# API version for the Runbooks resource provider surface.
# NOTE: the migrateProjects/runbooks type is only registered at
# 2020-06-01-preview. Newer versions (2025/2026) are for the wave APIs
# and return NoRegisteredProviderFound on the runbooks path.
RUNBOOKS_API_VERSION = "2020-06-01-preview"

# Runbook create/delete are long-running operations whose async status
# is served by the migrateProjects/waveOperations type. That type is NOT
# registered at RUNBOOKS_API_VERSION; the async-operation status URL must
# be polled at this newer API version instead.
WAVE_OPERATIONS_API_VERSION = "2025-03-30-preview"

# Canonical ARM ID templates (camelCase per the confirmed spec):
#   /subscriptions/{s}/resourceGroups/{rg}/providers/Microsoft.Migrate
#     /migrateProjects/{p}/runbooks/{n}/executions/{e}
MIGRATE_PROJECT_ID_TEMPLATE = (
    "/subscriptions/{subscription_id}"
    "/resourceGroups/{resource_group}"
    "/providers/Microsoft.Migrate/migrateProjects/{project_name}"
)
RUNBOOK_ID_TEMPLATE = "{project_id}/runbooks/{runbook_name}"
EXECUTION_ID_TEMPLATE = "{runbook_id}/executions/{execution_id}"
