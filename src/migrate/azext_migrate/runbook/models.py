# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Request/response body builders for the runbook feature."""

from enum import Enum

from azext_migrate.runbook.constants import (
    SCOPE_TYPE_WAVE,
    WAVE_ID_TEMPLATE,
    STEP_TYPE_APPROVAL,
    STEP_REF_BY_TYPE,
    STEP_DEPENDENCY_MODE_STEP,
    STEP_ACTION_APPROVE,
    STEP_ACTION_COMPLETE,
    ARTIFACT_DOWNLOAD_MODE_FILE,
)


class ExecutionAction(str, Enum):
    """Service ``RunbookExecutionAction`` enum (string values).

    ``PerformAction`` / ``ProvideApproval`` / ``UpdateStepStatus`` all send
    the string member value.
    """

    START = "Start"
    PAUSE = "Pause"
    RESUME = "Resume"
    CANCEL = "Cancel"
    RETRY = "Retry"
    COMPLETE = "Complete"
    FAIL = "Fail"
    SKIP = "Skip"
    APPROVE = "Approve"
    REJECT = "Reject"


def wave_id(project_id, wave_name):
    """Build a wave ARM id relative to the migrate project id."""
    return WAVE_ID_TEMPLATE.format(
        project_id=project_id, wave_name=wave_name)


def build_generate_body(wave_resource_id):
    """Build the CreateRunbook (PUT) body scoped to a wave.

    The scope is a polymorphic type on the service; its discriminator
    property (``scopeType``) is matched case-sensitively, so the payload
    must use camelCase keys (``scopeType``/``waveId``) to bind to the
    concrete wave scope. The GET read model echoes the same camelCase
    values.
    """
    return {
        "properties": {
            "scope": {
                "scopeType": SCOPE_TYPE_WAVE,
                "waveId": wave_resource_id,
            }
        }
    }


def build_update_body(description=None):
    """Build the runbook update (PATCH) body for editable metadata."""
    properties = {}
    if description is not None:
        properties["description"] = description
    return {"properties": properties}


def _depends_on_refs(depends_on):
    """Map CLI ``--depends-on`` entries to write-model dependency objects.

    The AddStep/UpdateStep write model expects a list of
    ``RunbookStepDependency`` objects ``{"mode": <string>, "stepId": <id>}``.
    ``mode`` is the ``RunbookStepDependencyMode`` string; a plain
    ``--depends-on <stepId>`` maps to a Step gate. Entries that are already
    dicts (e.g. carrying an ``entityMap``) are passed through unchanged.
    """
    refs = []
    for entry in depends_on or []:
        if isinstance(entry, dict):
            refs.append(entry)
        else:
            refs.append(
                {"mode": STEP_DEPENDENCY_MODE_STEP, "stepId": entry})
    return refs


def build_add_step_body(step_type, step_name, workstream_id,
                        step_description=None, depends_on=None,
                        migration_entity_ids=None):
    """Build the AddStep POST body for a single definition step.

    Mirrors the service ``RunbookStepAddRequest``. ``step_type`` selects
    the ``stepRef`` binding (Approval -> ``common.approval``, Manual ->
    ``common.manual``); the step is added to ``workstream_id``.
    ``migrationEntityIds`` is only carried by the Approval step variant.
    """
    body = {
        "workstreamId": workstream_id,
        "displayName": step_name,
        "description": step_description or "",
        "stepRef": STEP_REF_BY_TYPE.get(step_type, step_type),
        "dependsOn": _depends_on_refs(depends_on),
    }
    if step_type == STEP_TYPE_APPROVAL:
        body["migrationEntityIds"] = migration_entity_ids or []
    return body


def build_update_step_body(step_id, step_name=None, step_description=None,
                           depends_on=None):
    """Build the UpdateStep POST body; only provided fields are sent."""
    body = {"stepId": step_id}
    if step_name is not None:
        body["displayName"] = step_name
    if step_description is not None:
        body["description"] = step_description
    if depends_on is not None:
        body["dependsOn"] = _depends_on_refs(depends_on)
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
                                 new_workstream_name):
    """Build the MergeWorkstreams POST body.

    ``source_workstream_ids`` serializes as the ``workstreamIds`` array and
    ``new_workstream_name`` as ``newWorkstreamName``; both are required by
    the service ``RunbookWorkstreamsMergeRequest``.
    """
    return {
        "workstreamIds": source_workstream_ids or [],
        "newWorkstreamName": new_workstream_name,
    }


def build_start_execution_body():
    """Build the StartRunbookExecution (PUT) body."""
    return {"properties": {}}


def build_artifact_download_url_body(
        path="runbook.json", mode=ARTIFACT_DOWNLOAD_MODE_FILE,
        include_metadata=True):
    """Build the Artifact Service GenerateDownloadUrl request body.

    Omitting ``version``/``versionId`` requests the latest committed
    version. File mode targets a single blob within the artifact by
    ``path``.
    """
    body = {"mode": mode, "path": path}
    if include_metadata is not None:
        body["includeMetadata"] = include_metadata
    return body


def build_perform_action_body(action, target_id=None, entity_ids=None):
    """Build the PerformAction POST body (string action value)."""
    return {
        "action": action.value if isinstance(action, ExecutionAction)
        else action,
        "targetId": target_id or "",
        "migrationEntityIds": entity_ids or [],
    }


def build_retry_step_body(step_id, entity_ids=None):
    """Build the PerformAction POST body to retry a failed step.

    Retry reuses ``PerformAction`` with the ``Retry`` action and the step
    id as the ``targetId``.
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
