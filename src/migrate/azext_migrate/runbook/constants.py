# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Runbook-feature constants (extends the shared api-version registry)."""

from enum import Enum

# Scope type used by CreateRunbook (generate).
SCOPE_TYPE_WAVE = "Wave"

# Wave ARM id template (relative to the migrate project id).
WAVE_ID_TEMPLATE = "{project_id}/waves/{wave_name}"

# Step types accepted by ``definition step add``.
STEP_TYPE_MANUAL = "Manual"
STEP_TYPE_APPROVAL = "Approval"
STEP_TYPE_CUSTOM_SCRIPT = "CustomScript"
STEP_TYPE_VALUES = [
    STEP_TYPE_MANUAL,
    STEP_TYPE_APPROVAL,
    STEP_TYPE_CUSTOM_SCRIPT,
]

# Enumerations for the step parameter-sets.
APPROVAL_TYPE_VALUES = ["Partial", "Full"]
RUN_MODE_VALUES = ["Once", "PerEntity"]
EXECUTION_TARGET_VALUES = ["Appliance", "SourceVm", "TargetVm"]

# String action codes sent by the execution-step action endpoints.
# ``PerformAction`` (retry) sends the integer ``ExecutionAction`` code,
# but ``ProvideApproval`` / ``UpdateStepStatus`` send these PascalCase
# strings.
STEP_ACTION_APPROVE = "Approve"
STEP_ACTION_COMPLETE = "Complete"

# Opaque ``stepRef`` value the AddStep body binds per step type.
# TODO(confirm): replace with the authoritative per-type refs from the
# service spec; the current values mirror the step type as a stable stub.
STEP_REF_BY_TYPE = {
    STEP_TYPE_MANUAL: STEP_TYPE_MANUAL,
    STEP_TYPE_APPROVAL: STEP_TYPE_APPROVAL,
    STEP_TYPE_CUSTOM_SCRIPT: STEP_TYPE_CUSTOM_SCRIPT,
}


class RunbookStatus(str, Enum):
    """Runbook lifecycle status values (GetRunbook properties.status)."""

    GENERATING = "Generating"
    NEW = "New"
    READY_TO_START = "ReadyToStart"
    IN_EXECUTION = "InExecution"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    FAILED = "Failed"


# Ordered choices for the ``--status`` filter on ``runbook list``.
RUNBOOK_STATUS_VALUES = [member.value for member in RunbookStatus]


# Telemetry fault types for this feature.
RUNBOOK_ARM_ERROR = "RUNBOOK_ARM_ERROR"
RUNBOOK_VALIDATION_ERROR = "RUNBOOK_VALIDATION_ERROR"
RUNBOOK_FILE_ERROR = "RUNBOOK_FILE_ERROR"
RUNBOOK_VISUALIZE_ERROR = "RUNBOOK_VISUALIZE_ERROR"

# Terminal execution states that stop a ``--watch`` polling loop.
# TODO(confirm): reconcile with the service status.json enum; these
# cover the observed/expected terminal states case-insensitively.
EXECUTION_TERMINAL_STATES = frozenset({
    "succeeded",
    "executionsucceeded",
    "completed",
    "failed",
    "canceled",
    "cancelled",
})
