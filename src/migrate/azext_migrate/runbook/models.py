# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Request/response body builders for the runbook feature."""

from enum import IntEnum

from azext_migrate.runbook.constants import (
    SCOPE_TYPE_WAVE,
    WAVE_ID_TEMPLATE,
    STEP_REF_BY_TYPE,
    STEP_ACTION_APPROVE,
    STEP_ACTION_COMPLETE,
)


class ExecutionAction(IntEnum):
    """Service ``RunbookExecutionAction`` enum (0-based ordinal).

    ``PerformAction`` sends the integer code; ``ProvideApproval`` /
    ``UpdateStepStatus`` send the string member name.
    """

    START = 0
    PAUSE = 1
    RESUME = 2
    CANCEL = 3
    RETRY = 4
    COMPLETE = 5
    FAIL = 6
    SKIP = 7
    APPROVE = 8
    REJECT = 9


def wave_id(project_id, wave_name):
    """Build a wave ARM id relative to the migrate project id."""
    return WAVE_ID_TEMPLATE.format(
        project_id=project_id, wave_name=wave_name)


def build_generate_body(wave_resource_id):
    """Build the CreateRunbook (PUT) body scoped to a wave.

    The CreateRunbook write model binds the scope in PascalCase
    (``ScopeType``/``WaveId``). The GET read model echoes the same
    values in camelCase, but the create payload must use PascalCase.
    """
    return {
        "properties": {
            "scope": {
                "ScopeType": SCOPE_TYPE_WAVE,
                "WaveId": wave_resource_id,
            }
        }
    }


def build_update_body(description=None):
    """Build the runbook update (PATCH) body for editable metadata."""
    properties = {}
    if description is not None:
        properties["description"] = description
    return {"properties": properties}


def build_add_step_body(step_type, step_name, workstream_id,
                        step_description=None, depends_on=None,
                        migration_entity_ids=None):
    """Build the AddStep POST body for a single definition step.

    Mirrors the service ``RunbookStepAddRequest``. ``step_type`` selects
    the ``stepRef`` binding (Approval -> ``common.approval``, Manual ->
    ``custom.manual``); the step is added to ``workstream_id``.
    """
    return {
        "workstreamId": workstream_id,
        "stepName": step_name,
        "displayName": step_name,
        "description": step_description or "",
        "stepRef": STEP_REF_BY_TYPE.get(step_type, step_type),
        "migrationEntityIds": migration_entity_ids or [],
        "dependsOn": depends_on or [],
    }


def build_update_step_body(step_id, step_name=None, step_description=None,
                           depends_on=None):
    """Build the UpdateStep POST body; only provided fields are sent."""
    body = {"stepId": step_id}
    if step_name is not None:
        body["displayName"] = step_name
    if step_description is not None:
        body["description"] = step_description
    if depends_on is not None:
        body["dependsOn"] = depends_on
    return body


def build_delete_step_body(step_id):
    """Build the DeleteStep POST body."""
    return {"stepId": step_id}


def build_split_workstream_body(source_workstream_id, new_workstream_name,
                                step_ids):
    """Build the SplitWorkstream POST body.

    ``step_ids`` are the steps moved from the source workstream into the
    new one. Mirrors service ``RunbookWorkstreamSplitRequest``
    (sourceWorkstreamId / stepIds / newWorkstreamName).
    """
    return {
        "sourceWorkstreamId": source_workstream_id,
        "stepIds": step_ids or [],
        "newWorkstreamName": new_workstream_name,
    }


def build_merge_workstreams_body(source_workstream_ids,
                                 new_workstream_name=None):
    """Build the MergeWorkstreams POST body.

    ``source_workstream_ids`` serializes as the ``workstreamId`` array.
    ``new_workstream_name`` is optional; when omitted the service defaults
    it to the first workstream's name (service
    ``RunbookWorkstreamsMergeRequest``).
    """
    body = {"workstreamId": source_workstream_ids or []}
    if new_workstream_name:
        body["newWorkstreamName"] = new_workstream_name
    return body


def build_start_execution_body():
    """Build the StartRunbookExecution (PUT) body."""
    return {"properties": {}}


def build_perform_action_body(action, target_id=None, entity_ids=None):
    """Build the PerformAction POST body (integer action code)."""
    return {
        "action": int(action),
        "targetId": target_id or "",
        "migrationEntityIds": entity_ids or [],
    }


def build_retry_step_body(step_id, entity_ids=None):
    """Build the PerformAction POST body to retry a failed step.

    Retry reuses ``PerformAction`` with the integer ``RETRY`` (4) code and
    the step id as the ``targetId``.
    """
    return build_perform_action_body(
        ExecutionAction.RETRY, target_id=step_id, entity_ids=entity_ids)


def build_approve_step_body(step_id, entity_ids=None):
    """Build the ProvideApproval POST body for an approval step.

    ``ProvideApproval`` sends the PascalCase ``"Approve"`` action string.
    ``migrationEntityIds`` carries the per-entity approvals for a Partial
    step; a Full step (or ``--all-ready``) sends an empty list.
    """
    return {
        "action": STEP_ACTION_APPROVE,
        "targetId": step_id,
        "migrationEntityIds": entity_ids or [],
    }


def build_complete_step_body(step_id, comment, entity_ids=None):
    """Build the UpdateStepStatus POST body to complete a manual step.

    ``UpdateStepStatus`` sends the PascalCase ``"Complete"`` action string.
    ``comment`` is required by the service to record who/why the step was
    completed (captured in ``status.json``).
    """
    return {
        "action": STEP_ACTION_COMPLETE,
        "targetId": step_id,
        "migrationEntityIds": entity_ids or [],
        "comment": comment,
    }
