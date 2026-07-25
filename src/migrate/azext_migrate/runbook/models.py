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


# Service ``RunbookStepDependencyMode`` ordinal for a step-gate dependency
# (enum member ``Step`` == 0), used as the System.Text.Json ``"Mode"``
# polymorphic discriminator value on each ``dependsOn`` entry.
_DEPENDENCY_MODE_STEP = 0


def _depends_on_refs(depends_on):
    """Normalize ``--depends-on`` step ids into service dependency objects.

    The service models each ``dependsOn`` entry as a polymorphic
    ``RunbookStepDependency`` that System.Text.Json discriminates on a
    verbatim ``"Mode"`` property whose value is the integer enum ordinal
    (``0`` = step gate). A ``--depends-on`` step id is a step-gate
    dependency, serialized as ``{"Mode": 0, "stepId": "<id>"}`` with the
    discriminator first. Entries already shaped as dicts pass through.
    """
    refs = []
    for dep in depends_on or []:
        if isinstance(dep, dict):
            refs.append(dep)
        elif dep:
            refs.append({"Mode": _DEPENDENCY_MODE_STEP, "stepId": dep})
    return refs


def build_add_step_body(step_type, step_name, step_description=None,
                        depends_on=None, approval_type=None,
                        run_mode=None, execution_target=None):
    """Build the AddStep POST body for a single definition step.

    ``step_type`` selects the ``stepRef`` binding; the approval and
    custom-script parameter-sets are absorbed as optional properties so
    the same builder serves every step kind.
    """
    body = {
        "stepName": step_name,
        "displayName": step_name,
        "stepRef": STEP_REF_BY_TYPE.get(step_type, step_type),
        "migrationEntityIds": [],
        "dependsOn": _depends_on_refs(depends_on),
    }
    if step_description is not None:
        body["description"] = step_description
    if approval_type is not None:
        body["approvalType"] = approval_type
    if run_mode is not None:
        body["runMode"] = run_mode
    if execution_target is not None:
        body["executionTarget"] = execution_target
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
                                entities_to_move):
    """Build the SplitWorkstream POST body."""
    return {
        "sourceWorkstreamId": source_workstream_id,
        "stepIds": [],
        "migrationEntityIds": entities_to_move or [],
        "newWorkstreamName": new_workstream_name,
    }


def build_merge_workstreams_body(source_workstream_ids, new_workstream_name):
    """Build the MergeWorkstreams POST body.

    ``source_workstream_ids`` serializes as the ``workstreamId`` array.
    """
    return {
        "workstreamId": source_workstream_ids or [],
        "newWorkstreamName": new_workstream_name,
    }


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
