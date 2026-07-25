# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Table (``--output table``) transformers for runbook commands."""

from collections import OrderedDict

from azext_migrate.runbook import deps as dep_utils

# Placeholder shown for the "Applications" column, which the runbook
# definition does not currently model (steps carry entities, not apps).
_APPLICATIONS_PLACEHOLDER = '-'


def runbook_table(result):
    """Project a runbook (or a list of runbooks) into table rows."""
    if isinstance(result, list):
        return [_runbook_row(item) for item in result]
    return _runbook_row(result)


def _runbook_row(item):
    item = item or {}
    props = item.get('properties', {}) if isinstance(item, dict) else {}
    return OrderedDict([
        ('Name', item.get('name')),
        ('State', props.get('state')),
        ('ProvisioningState', props.get('provisioningState')),
    ])


def definition_table(result):
    """Project a runbook definition into one step row per definition step."""
    rows = []
    if isinstance(result, dict) and result.get('workstreams') is not None:
        for workstream in result.get('workstreams') or []:
            rows.extend(_step_rows(workstream))
    elif isinstance(result, dict) and result.get('steps') is not None:
        rows.extend(_step_rows(result))
    elif isinstance(result, dict) and _looks_like_step(result):
        rows.append(_step_row(result))
    return rows


def _looks_like_step(step):
    """True when a dict carries step-identifying keys (single-step show)."""
    return any(step.get(key) for key in
               ('stepId', 'id', 'displayName', 'stepName'))


def _step_rows(workstream):
    workstream = workstream or {}
    workstream_id = workstream.get('id')
    return [_step_row(step, workstream_id)
            for step in workstream.get('steps', []) or []]


def _step_row(step, workstream_id=None):
    step = step or {}
    return OrderedDict([
        ('Workstream Id', workstream_id),
        ('Step Id', step.get('stepId') or step.get('id')),
        ('Step Name', step.get('displayName') or step.get('stepName')),
        ('Depends On', ' '.join(dep_utils.merged_dep_ids(step))),
        ('Configuration Status', step.get('configurationStatus')),
        ('Workloads', len(step.get('entities') or [])),
        ('Applications', _APPLICATIONS_PLACEHOLDER),
    ])


def execution_table(result):
    """Project a runbook execution status into one row per step."""
    rows = []
    status = _execution_status(result)
    if isinstance(status, dict) and status.get('workstreams') is not None:
        for workstream in status.get('workstreams') or []:
            rows.extend(_exec_step_rows(workstream))
    elif isinstance(status, dict) and status.get('steps') is not None:
        rows.extend(_exec_step_rows(status))
    elif isinstance(status, dict) and status:
        rows.append(_exec_step_row(status))
    return rows


def _execution_status(result):
    """Unwrap an execution resource to its status document."""
    if (isinstance(result, dict)
            and result.get('properties') is not None
            and result.get('workstreams') is None
            and result.get('steps') is None):
        return result.get('properties') or {}
    return result or {}


def _exec_step_rows(workstream):
    workstream = workstream or {}
    return [_exec_step_row(step)
            for step in workstream.get('steps', []) or []]


def _exec_step_row(step):
    step = step or {}
    return OrderedDict([
        ('Id', step.get('id') or step.get('stepId')),
        ('Step Name', step.get('displayName') or step.get('stepName')),
        ('Step Status',
         step.get('status') or step.get('stepStatus') or step.get('state')),
        ('Depends On', _format_depends_on(step.get('dependsOn'))),
        ('Workload Progress', _workload_progress(step)),
    ])


def _format_depends_on(deps):
    """Render a step's ``dependsOn`` as a space-separated list of step ids.

    Handles both the execution ``status.json`` shape (a list of objects
    ``{"step": "<stepId>", "mode": ...}``) and a plain list of id strings.
    """
    if not deps:
        return ''
    ids = []
    for dep in deps:
        if isinstance(dep, dict):
            ids.append(dep.get('step') or dep.get('stepId') or '')
        elif dep:
            ids.append(str(dep))
    return ' '.join(dep_id for dep_id in ids if dep_id)


def _workload_progress(step):
    """Summarize per-entity progress from ``entityExecutions``.

    Falls back to an explicit ``workloadProgress`` scalar when present.
    """
    progress = step.get('workloadProgress')
    if progress is not None:
        return progress
    entities = step.get('entityExecutions')
    if not entities:
        return None
    total = len(entities)
    completed = sum(
        1 for entity in entities
        if str((entity or {}).get('state', '')).lower() == 'completed')
    return '%d/%d completed' % (completed, total)
