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
STEP_TYPE_VALUES = [
    STEP_TYPE_MANUAL,
    STEP_TYPE_APPROVAL,
]

# String action codes sent by the execution-step action endpoints.
# ``PerformAction`` (retry) sends the integer ``ExecutionAction`` code,
# but ``ProvideApproval`` / ``UpdateStepStatus`` send these PascalCase
# strings.
STEP_ACTION_APPROVE = "Approve"
STEP_ACTION_COMPLETE = "Complete"

# ``DownloadMode`` for the Artifact Service GenerateDownloadUrl request:
# a single file or a whole directory (subtree) of the artifact.
ARTIFACT_DOWNLOAD_MODE_FILE = "file"
ARTIFACT_DOWNLOAD_MODE_DIRECTORY = "directory"

# Runbook definition artifact fetch strategy. The service currently returns
# individual blobs (file mode, raw JSON). Set this True once the service
# packages the whole artifact as a downloadable ZIP so the CLI switches to
# directory mode without touching call sites.
RUNBOOK_ARTIFACT_DOWNLOAD_AS_ZIP = True
RUNBOOK_DEFINITION_FILE = "runbook.json"
RUNBOOK_INPUT_FILE = "input.json"

# ``stepRef`` value the AddStep body binds per step type. These correlate
# the CLI step with the partner runbook step used for execution.
STEP_REF_BY_TYPE = {
    STEP_TYPE_MANUAL: "common.manual",
    STEP_TYPE_APPROVAL: "common.approval",
}

# A step dependency in the AddStep/UpdateStep write model (service
# ``RunbookStepDependency``) is ``{"mode": <string>, "stepId": <step-id>}``.
# ``mode`` is the ``RunbookStepDependencyMode`` enum (string values). The
# CLI ``--depends-on`` takes step ids only and maps each to a Step gate.
STEP_DEPENDENCY_MODE_STEP = "Step"
STEP_DEPENDENCY_MODE_MIGRATION_ENTITY = "MigrationEntity"


class RunbookStatus(str, Enum):
    """Runbook lifecycle status values (GetRunbook properties.status)."""

    GENERATING = "Generating"
    NOT_CONFIGURED = "NotConfigured"
    READY_TO_START = "ReadyToStart"
    IN_EXECUTION = "InExecution"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    FAILED = "Failed"


# Ordered choices for the ``--status`` filter on ``runbook list``.
RUNBOOK_STATUS_VALUES = [member.value for member in RunbookStatus]


class RunbookExecutionStatus(str, Enum):
    """Execution ARM resource status (GetRunbookExecution properties.status).

    Source of truth: service enum ``RunbookExecutionStatus``
    (Microsoft.Azure.Migrate.MgmtSvcs.Constants).
    """

    QUEUED = "Queued"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    FAILED = "Failed"
    PAUSING = "Pausing"
    PAUSED = "Paused"
    RESUMING = "Resuming"
    CANCELLING = "Cancelling"
    CANCELLED = "Cancelled"


class ExecutionState(str, Enum):
    """Per-node state in the execution ``status.json`` document.

    Source of truth: service enum ``ExecutionState``
    (MigrationOrchestrator.Engine.Models.ExecutionStatus). Coordinator
    nodes (runbook, workstream) use ``Completed``; steps report
    ``Succeeded``/``PartiallySucceeded``.
    """

    NOT_STARTED = "NotStarted"
    IN_PROGRESS = "InProgress"
    AWAITING_USER_ACTION = "AwaitingUserAction"
    COMPLETED = "Completed"
    SUCCEEDED = "Succeeded"
    PARTIALLY_SUCCEEDED = "PartiallySucceeded"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    PAUSED = "Paused"
    PAUSING = "Pausing"
    RESUMING = "Resuming"
    CANCELLING = "Cancelling"
    SKIPPED = "Skipped"


# Telemetry fault types for this feature.
RUNBOOK_ARM_ERROR = "RUNBOOK_ARM_ERROR"
RUNBOOK_VALIDATION_ERROR = "RUNBOOK_VALIDATION_ERROR"
RUNBOOK_FILE_ERROR = "RUNBOOK_FILE_ERROR"
RUNBOOK_VISUALIZE_ERROR = "RUNBOOK_VISUALIZE_ERROR"

# Terminal execution states that stop a ``--watch`` polling loop, compared
# case-insensitively. Sourced from the two authoritative service enums:
#   * RunbookExecutionStatus (execution ARM resource properties.status) -->
#     Completed / Failed / Cancelled.
#   * ExecutionState (status.json node state) --> adds the step-level finals
#     Succeeded / PartiallySucceeded / Skipped.
# Confirmed against the live API.
_EXECUTION_TERMINAL_MEMBERS = (
    RunbookExecutionStatus.COMPLETED,
    RunbookExecutionStatus.FAILED,
    RunbookExecutionStatus.CANCELLED,
    ExecutionState.COMPLETED,
    ExecutionState.SUCCEEDED,
    ExecutionState.PARTIALLY_SUCCEEDED,
    ExecutionState.FAILED,
    ExecutionState.CANCELLED,
    ExecutionState.SKIPPED,
)
EXECUTION_TERMINAL_STATES = frozenset(
    member.value.lower() for member in _EXECUTION_TERMINAL_MEMBERS)

# Per-entity status values that count as successfully finished when
# summarizing a step's workload progress ("n/m completed"). The status.json
# schema reports entity success as ``Succeeded``; ``Completed`` is kept for
# backward compatibility with the earlier ``state`` field.
ENTITY_COMPLETED_STATES = frozenset({
    ExecutionState.SUCCEEDED.value.lower(),
    ExecutionState.COMPLETED.value.lower(),
})
