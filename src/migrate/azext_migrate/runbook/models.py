# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Request/response body builders for the runbook feature."""

from enum import Enum

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_migrate.runbook.constants import (
    SCOPE_TYPE_WAVE,
    WAVE_ID_TEMPLATE,
    STEP_TYPE_APPROVAL,
    STEP_REF_BY_TYPE,
    STEP_WAITFOR_STEP,
    STEP_WAITFOR_ENTITY,
    STEP_WAITFOR_MAPPED,
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


def _step_dep(step_id, wait_for):
    return {"waitFor": wait_for, "stepId": step_id}


def _mapped_dep(token):
    """Parse a ``--depends-on-mapped-entities`` token into a dependency.

    Token form: ``<stepId>=<dependentEntity>:<waitsForEntity>,...`` (e.g.
    ``enable-1=e1:f1,e2:f2``); entity ids are bare GUIDs.
    """
    step_id, sep, pairs = token.partition('=')
    step_id = step_id.strip()
    if not step_id or sep != '=' or not pairs.strip():
        raise InvalidArgumentValueError(
            "Invalid --depends-on-mapped-entities value '%s'. Expected "
            "'<stepId>=<dependentEntity>:<waitsForEntity>,...'." % token)
    entity_pairs = []
    for pair in pairs.split(','):
        dependent, psep, waits_for = pair.partition(':')
        dependent, waits_for = dependent.strip(), waits_for.strip()
        if not dependent or psep != ':' or not waits_for:
            raise InvalidArgumentValueError(
                "Invalid entity pair '%s' in --depends-on-mapped-entities "
                "'%s'. Expected '<dependentEntity>:<waitsForEntity>'."
                % (pair, token))
        entity_pairs.append(
            {"dependentEntity": dependent, "waitsFor": waits_for})
    return {"waitFor": STEP_WAITFOR_MAPPED, "stepId": step_id,
            "entityPairs": entity_pairs}


def build_step_dependencies(whole_step=None, per_entity=None,
                            mapped_entities=None):
    """Combine the three CLI dependency lists into a ``dependsOn`` list.

    Returns ``None`` when none of the three flags were provided so
    ``UpdateStep`` can send ``dependsOn: null`` and the service preserves the
    step's existing dependencies. When any flag is provided the returned list
    is the complete replacement (modes not supplied are dropped).
    """
    if whole_step is None and per_entity is None and mapped_entities is None:
        return None
    refs = [_step_dep(s, STEP_WAITFOR_STEP) for s in whole_step or []]
    refs += [_step_dep(s, STEP_WAITFOR_ENTITY) for s in per_entity or []]
    refs += [_mapped_dep(t) for t in mapped_entities or []]
    return refs


def build_add_step_body(step_type, step_name, workstream_id,
                        step_description=None, depends_on_whole_step=None,
                        depends_on_per_entity=None,
                        depends_on_mapped_entities=None,
                        migration_entity_ids=None):
    """Build the AddStep POST body for a single definition step.

    Mirrors the service ``RunbookStepAddRequest``. ``step_type`` selects
    the ``stepRef`` binding (Approval -> ``common.approval``, Manual ->
    ``common.manual``); the step is added to ``workstream_id``.
    ``entities`` (bare migration-entity GUIDs) is only carried by the
    Approval step variant. ``dependsOn`` is the combined dependency list
    (empty when no dependency flags are given — a new step has nothing to
    preserve).
    """
    deps = build_step_dependencies(
        depends_on_whole_step, depends_on_per_entity,
        depends_on_mapped_entities)
    body = {
        "workstreamId": workstream_id,
        "displayName": step_name,
        "description": step_description or "",
        "stepRef": STEP_REF_BY_TYPE.get(step_type, step_type),
        "dependsOn": deps if deps is not None else [],
    }
    if step_type == STEP_TYPE_APPROVAL:
        body["entities"] = migration_entity_ids or []
    return body


def build_update_step_body(step_id, step_name=None, step_description=None,
                           depends_on_whole_step=None,
                           depends_on_per_entity=None,
                           depends_on_mapped_entities=None):
    """Build the UpdateStep POST body.

    ``dependsOn`` is always sent: the combined list when any dependency flag
    is provided (a full replacement of the step's dependencies), or ``null``
    when none are — the service preserves the existing dependencies for the
    ``null`` case.
    """
    body = {"stepId": step_id}
    if step_name is not None:
        body["displayName"] = step_name
    if step_description is not None:
        body["description"] = step_description
    body["dependsOn"] = build_step_dependencies(
        depends_on_whole_step, depends_on_per_entity,
        depends_on_mapped_entities)
    return body


def build_delete_step_body(step_id):
    """Build the DeleteStep POST body."""
    return {"stepId": step_id}


def build_split_workstream_body(source_workstream_id, new_workstream_name,
                                step_ids):
    """Build the SplitWorkstream POST body.

    ``step_ids`` are the steps moved from the source workstream into the
    new one. Mirrors service ``RunbookWorkstreamSplitRequest``
    (sourceWorkstreamId / stepIds / displayName).
    """
    return {
        "sourceWorkstreamId": source_workstream_id,
        "stepIds": step_ids or [],
        "displayName": new_workstream_name,
    }


def build_merge_workstreams_body(source_workstream_ids,
                                 new_workstream_name):
    """Build the MergeWorkstreams POST body.

    ``source_workstream_ids`` serializes as the ``workstreamIds`` array and
    ``new_workstream_name`` as ``displayName``; both are required by
    the service ``RunbookWorkstreamsMergeRequest``.
    """
    return {
        "workstreamIds": source_workstream_ids or [],
        "displayName": new_workstream_name,
    }


def build_artifact_download_url_body(mode, path=None):
    """Build the GenerateDownloadUrl request body.

    Directory mode returns the whole artifact as a ZIP and takes no path;
    File mode targets a single blob within the artifact by ``path``.
    """
    body = {"mode": mode}
    if mode == ARTIFACT_DOWNLOAD_MODE_FILE:
        body["path"] = path
    return body


def build_artifact_upload_url_body(path):
    """Build the GenerateUploadUrl request body (single file by ``path``)."""
    return {"path": path}


def build_perform_action_body(action, target_id=None, entity_ids=None):
    """Build the PerformAction POST body (string action value)."""
    return {
        "action": action.value if isinstance(action, ExecutionAction)
        else action,
        "targetId": target_id or "",
        "entities": entity_ids or [],
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
    ``entities`` carries the per-entity approval GUIDs for a Partial
    step; a Full step (or ``--all-ready``) sends an empty list.
    """
    return {
        "action": STEP_ACTION_APPROVE,
        "targetId": step_id,
        "entities": entity_ids or [],
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
        "entities": entity_ids or [],
        "comment": comment,
    }
