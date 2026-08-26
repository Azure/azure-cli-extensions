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

# GenerateDownloadUrl ``mode`` (verified 2026-08-23): Directory returns the
# whole artifact as a ZIP (body ``{"mode": "Directory"}``); File returns a
# single blob by path (body ``{"mode": "File", "path": ...}``).
ARTIFACT_DOWNLOAD_MODE_FILE = "File"
ARTIFACT_DOWNLOAD_MODE_DIRECTORY = "Directory"

# Blob paths within an artifact, used for File-mode download/upload.
RUNBOOK_INPUT_FILE = "inputs.json"
RUNBOOK_STATUS_FILE = "executionStatus.json"

# ``stepRef`` value the AddStep body binds per step type. These correlate
# the CLI step with the partner runbook step used for execution.
STEP_REF_BY_TYPE = {
    STEP_TYPE_MANUAL: "common.manual",
    STEP_TYPE_APPROVAL: "common.approval",
}

# A step dependency in the AddStep/UpdateStep write model (service
# ``RunbookStepDependency``) is ``{"waitFor": <string>, "stepId": <step-id>}``.
# ``waitFor`` is the polymorphic discriminator (first key); its full enum is
# ``Step``/``Entity``/``MappedEntities`` (the latter two carry an
# ``entityPairs`` ``[{"dependentEntity", "waitsFor"}]`` list and are invalid
# for Manual steps). The CLI ``--depends-on`` authors ``Step`` gates only.
# NOTE (F-verify 2026-08-28): the WRITE enum (``Step``/``Entity``/
# ``MappedEntities``) is deliberately distinct from the READ projections the
# service emits — spec.json uses ``wholeStep``/``sameEntity``/``mappedEntities``
# and executionStatus.json uses ``step``/``entity``/``mappedEntities``. Read
# code maps those forms (see visualize/viewmodel ``_WAIT_FOR_LABELS``); do NOT
# "align" this write value to a read form.
STEP_WAITFOR_STEP = "Step"


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
