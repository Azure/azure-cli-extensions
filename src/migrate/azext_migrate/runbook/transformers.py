# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Table (``--output table``) transformers for runbook commands."""

from collections import OrderedDict

from azext_migrate.runbook import deps as dep_utils
from azext_migrate.runbook.constants import ENTITY_COMPLETED_STATES

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
    labels = dep_utils.build_dep_labels(result)
    rows = []
    if isinstance(result, dict) and result.get('workstreams') is not None:
        for workstream in result.get('workstreams') or []:
            rows.extend(_step_rows(workstream, labels))
    elif isinstance(result, dict) and result.get('steps') is not None:
        rows.extend(_step_rows(result, labels))
    elif isinstance(result, dict) and _looks_like_step(result):
        rows.append(_step_row(result, labels=labels))
    return rows


def _looks_like_step(step):
    """True when a dict carries step-identifying keys (single-step show)."""
    return any(step.get(key) for key in
               ('stepId', 'id', 'displayName', 'stepName'))


def _step_rows(workstream, labels):
    workstream = workstream or {}
    workstream_id = workstream.get('id')
    steps = workstream.get('steps', []) or []
    # Keep an empty workstream visible with a single placeholder row.
    if not steps:
        return [_empty_workstream_row(workstream_id)]
    return [_step_row(step, workstream_id, labels) for step in steps]


def _empty_workstream_row(workstream_id):
    return OrderedDict([
        ('Workstream Id', workstream_id),
        ('Step Id', ''),
        ('Step Name', '(no steps)'),
        ('Depends On', ''),
        ('Configuration Status', ''),
        ('Workloads', ''),
        ('Applications', _APPLICATIONS_PLACEHOLDER),
    ])


def _step_row(step, workstream_id=None, labels=None):
    step = step or {}
    return OrderedDict([
        ('Workstream Id', workstream_id),
        ('Step Id', step.get('stepId') or step.get('id')),
        ('Step Name', step.get('displayName') or step.get('stepName')),
        ('Depends On', '\n'.join(dep_utils.label_deps(step, labels or {}))),
        ('Configuration Status', step.get('configurationStatus')),
        ('Workloads', len(step.get('entities') or [])),
        ('Applications', _APPLICATIONS_PLACEHOLDER),
    ])


def executions_table(result):
    """Project a list of runbook executions into one row per execution."""
    items = result if isinstance(result, list) else [result]
    return [_execution_row(item) for item in items if item]


def _execution_row(item):
    item = item or {}
    props = item.get('properties', {}) if isinstance(item, dict) else {}
    return OrderedDict([
        ('Name', item.get('name')),
        ('Status', props.get('status') or props.get('state')),
        ('ProvisioningState', props.get('provisioningState')),
        ('StartTime', props.get('startTime') or props.get('jobStartTime')),
        ('EndTime', props.get('endTime')),
    ])


def execution_table(result):
    """Project a runbook execution status into one row per step."""
    rows = []
    status = _execution_status(result)
    labels = dep_utils.build_dep_labels(status)
    if isinstance(status, dict) and status.get('workstreams') is not None:
        for workstream in status.get('workstreams') or []:
            rows.extend(_exec_step_rows(workstream, labels))
    elif isinstance(status, dict) and status.get('steps') is not None:
        rows.extend(_exec_step_rows(status, labels))
    elif isinstance(status, dict) and status:
        rows.append(_exec_step_row(status, labels=labels))
    return rows


def _execution_status(result):
    """Unwrap an execution resource to its status document."""
    if (isinstance(result, dict)
            and result.get('properties') is not None
            and result.get('workstreams') is None
            and result.get('steps') is None):
        return result.get('properties') or {}
    return result or {}


def _exec_step_rows(workstream, labels):
    workstream = workstream or {}
    workstream_id = workstream.get('id')
    return [_exec_step_row(step, workstream_id, labels)
            for step in workstream.get('steps', []) or []]


def _exec_step_row(step, workstream_id=None, labels=None):
    step = step or {}
    return OrderedDict([
        ('Workstream Id', workstream_id),
        ('Step Id', step.get('id') or step.get('stepId')),
        ('Step Name', step.get('displayName') or step.get('stepName')),
        ('Step Status',
         step.get('status') or step.get('stepStatus') or step.get('state')),
        ('Depends On', '\n'.join(dep_utils.label_deps(step, labels or {}))),
        ('Workload Progress', _workload_progress(step)),
    ])


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
    completed = 0
    for entity in entities:
        value = (entity or {}).get('status') or (entity or {}).get('state')
        if str(value or '').lower() in ENTITY_COMPLETED_STATES:
            completed += 1
    return '%d/%d completed' % (completed, total)
