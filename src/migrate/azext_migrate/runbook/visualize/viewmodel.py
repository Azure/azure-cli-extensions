# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Build the *grid* view model for a runbook definition/execution.

This is the data model behind the portal-style grid (the default view in the
generated HTML), grouped by workstream. Like :mod:`graph`, this module is
**data only** — it contains no HTML and performs no I/O, so it is trivially
unit-testable. The renderer turns this model into offline, XSS-escaped markup.
"""

from azext_migrate.runbook import deps as dep_utils
from azext_migrate.runbook.constants import ENTITY_COMPLETED_STATES

KIND_DEFINITION = 'definition'
KIND_EXECUTION = 'execution'


class EntityProgress:
    """Per-entity execution state shown under an execution step."""

    # pylint: disable=too-few-public-methods,too-many-arguments
    def __init__(self, name, status, status_reason=None, error=None,
                 total_attempts=None, attempts=None, tool_status=None):
        self.name = name
        self.status = status
        self.status_reason = status_reason
        self.error = error
        self.total_attempts = total_attempts
        self.attempts = attempts or []
        # Tool-reported migration status (e.g. Replicating, Migrating) — a
        # finer-grained, tool-driven state than the orchestrator ``status``.
        self.tool_status = tool_status


class StepRow:
    """One row in the grid (a single runbook step)."""

    # pylint: disable=too-few-public-methods,too-many-arguments
    # pylint: disable=too-many-instance-attributes
    def __init__(self, step_id, name, deps=None, status=None,
                 workloads=None, workload_progress=None, entities=None,
                 step_ref=None, entity_names=None, prereqs=None,
                 dep_details=None, entity_groups=None, status_reason=None,
                 error=None, retry_count=0, attempts=None,
                 user_comment=None):
        self.id = step_id
        self.name = name
        self.deps = deps or []
        self.status = status
        self.workloads = workloads
        self.workload_progress = workload_progress
        self.entities = entities or []
        self.step_ref = step_ref
        # Detail-pane fields (definition): resolved entity display names and
        # the prerequisite / dependsOn edges labelled with their mode.
        self.entity_names = entity_names or []
        self.prereqs = prereqs or []
        self.dep_details = dep_details or []
        # Affected entity groups ("applications"), as display names.
        self.entity_groups = entity_groups or []
        # Execution detail: failure reason/error, retry (failed-attempt)
        # count, per-attempt history, and any manual sign-off comment.
        self.status_reason = status_reason
        self.error = error
        self.retry_count = retry_count
        self.attempts = attempts or []
        self.user_comment = user_comment


class Workstream:
    """A named group of step rows."""

    # pylint: disable=too-few-public-methods
    def __init__(self, name, steps, ws_id=None):
        self.name = name
        self.steps = steps
        self.id = ws_id


class RunbookView:
    """The full grid view model for one runbook."""

    # pylint: disable=too-few-public-methods,too-many-arguments
    def __init__(self, title, kind, workstreams, summary,
                 meta=None, generated=None):
        self.title = title
        self.kind = kind
        self.workstreams = workstreams
        self.summary = summary
        # ``meta`` is a list of (label, value) header fields (e.g. step
        # library version, wave id); ``generated`` is the source-declared
        # generation timestamp, if the document carried one.
        self.meta = meta or []
        self.generated = generated

    @property
    def step_count(self):
        return sum(len(ws.steps) for ws in self.workstreams)


def _unwrap(document):
    """Return the root object, unwrapping an execution ``properties`` envelope."""
    root = document or {}
    if isinstance(root, dict) and isinstance(root.get('properties'), dict):
        merged = dict(root)
        merged.update(root['properties'])
        return merged
    return root if isinstance(root, dict) else {}


def _step_id(step):
    return step.get('stepId') or step.get('id') or step.get('name')


def _step_name(step):
    return (step.get('displayName') or step.get('name')
            or step.get('stepName') or _step_id(step) or 'step')


def _iter_workstreams(root):
    """Yield ``(name, ws_id, [steps])`` triples, covering grouped/flat shapes."""
    workstreams = root.get('workstreams')
    if isinstance(workstreams, list) and workstreams:
        for workstream in workstreams:
            if not isinstance(workstream, dict):
                continue
            ws_id = workstream.get('id')
            name = (workstream.get('displayName') or workstream.get('name')
                    or ws_id or 'Workstream')
            steps = [s for s in workstream.get('steps') or []
                     if isinstance(s, dict)]
            yield name, ws_id, steps
        return
    flat = [s for s in root.get('steps') or [] if isinstance(s, dict)]
    if flat:
        yield None, None, flat


def _step_name_map(root):
    """Map every step id to its display name (for dependency labels)."""
    names = {}
    for _, _, steps in _iter_workstreams(root):
        for step in steps:
            names[_step_id(step)] = _step_name(step)
    return names


def _entity_name_map(root):
    """Map every entity id to its display name (for step detail panes)."""
    names = {}
    for entity in root.get('entities') or []:
        if isinstance(entity, dict):
            entity_id = entity.get('id') or entity.get('name')
            if entity_id:
                names[entity_id] = entity.get('displayName') or entity_id
    return names


def _entity_group_map(root):
    """Map every entity-group id to its display name (the "applications")."""
    names = {}
    for group in root.get('entityGroups') or []:
        if isinstance(group, dict):
            gid = group.get('id') or group.get('name')
            if gid:
                names[gid] = (
                    group.get('displayName') or group.get('name') or gid)
    return names


def _step_groups(step, group_map):
    """A step's ``affectedEntityGroups`` resolved to display names."""
    return [group_map.get(gid, gid)
            for gid in step.get('affectedEntityGroups') or []]


_WAIT_FOR_LABELS = {
    'wholeStep': 'Blocking',
    'sameEntity': 'Soft',
    'mappedEntities': 'Mapped',
}


def _dep_entries(raw, id_to_name):
    """Label a prerequisite/dependsOn list with resolved names and mode."""
    entries = []
    for dep in raw or []:
        if isinstance(dep, dict):
            dep_id = dep.get('stepId') or dep.get('step')
            mode = dep.get('waitFor') or dep.get('mode')
        else:
            dep_id, mode = dep, None
        if not dep_id:
            continue
        name = id_to_name.get(dep_id, dep_id)
        mode = _WAIT_FOR_LABELS.get(mode, mode)
        entries.append('%s (%s)' % (name, mode) if mode else name)
    return entries


def build_definition_view(document, title):
    """Build the grid view model for a runbook definition document."""
    root = _unwrap(document)
    id_to_name = _step_name_map(root)
    dep_labels = dep_utils.build_dep_labels(root)
    entity_map = _entity_name_map(root)
    group_map = _entity_group_map(root)
    workstreams = []
    status_counts = {}
    for name, ws_id, steps in _iter_workstreams(root):
        rows = []
        for step in steps:
            status = step.get('configurationStatus')
            if status:
                key = str(status).split(' ', 1)[0]
                status_counts[key] = status_counts.get(key, 0) + 1
            entity_ids = step.get('entities') or []
            rows.append(StepRow(
                step_id=_step_id(step),
                name=_step_name(step),
                deps=dep_utils.label_deps(step, dep_labels),
                status=status,
                workloads=len(entity_ids),
                step_ref=step.get('stepRef'),
                entity_names=[entity_map.get(eid, eid)
                              for eid in entity_ids],
                prereqs=_dep_entries(step.get('prerequisites'), id_to_name),
                dep_details=_dep_entries(step.get('dependsOn'), id_to_name),
                entity_groups=_step_groups(step, group_map)))
        workstreams.append(Workstream(name, rows, ws_id))

    step_total = sum(len(ws.steps) for ws in workstreams)
    summary = [('Workstreams', len(workstreams)), ('Steps', step_total),
               ('Entities', len(root.get('entities') or []))]
    summary.extend(sorted(status_counts.items()))
    meta, generated = _definition_meta(root)
    return RunbookView(title, KIND_DEFINITION, workstreams, summary,
                       meta=meta, generated=generated)


def _definition_meta(root):
    """Extract header metadata from a runbook definition document.

    Returns ``(meta, generated)`` where ``meta`` is a list of
    ``(label, value)`` header fields and ``generated`` is the
    source-declared generation timestamp (or ``None``). The identifiers
    (generatedAt / runbookId / waveId) live on the document envelope and are
    carried onto the payload by the loading command.
    """
    generated = root.get('generatedAt')
    meta = []
    versions = root.get('stepLibraryVersions')
    if isinstance(versions, list) and versions:
        meta.append(('Runbook version', ', '.join(
            '%s %s' % (v.get('namespace'), v.get('version'))
            for v in versions if isinstance(v, dict))))
    if generated:
        meta.append(('Generated', generated))
    meta.append(('Data source', 'spec.json'))
    resource_id = root.get('runbookId')
    if resource_id:
        meta.append(('Runbook resource id', resource_id))
    wave_id = root.get('waveId')
    if wave_id:
        meta.append(('Wave id', wave_id))
    return meta, generated


def _entity_status(entity):
    status = entity.get('status') or entity.get('state')
    if isinstance(status, dict):
        status = status.get('state') or status.get('status')
    return status


def _progress_text(step):
    """Return a "n/m completed" summary for an execution step."""
    explicit = step.get('workloadProgress')
    if explicit is not None:
        return str(explicit)
    total = len(step.get('entities') or [])
    done = step.get('entitiesCompleted')
    if isinstance(done, int) and total:
        return '%d/%d completed' % (done, total)
    entities = step.get('entityExecutions')
    if not isinstance(entities, list) or not entities:
        return None
    completed = sum(
        1 for entity in entities
        if isinstance(entity, dict)
        and str(_entity_status(entity) or '').lower()
        in ENTITY_COMPLETED_STATES)
    return '%d/%d completed' % (completed, len(entities))


def _exec_status(step):
    return (step.get('status') or step.get('stepStatus')
            or step.get('state'))


def _error_text(node):
    """Flatten an ``errorDetails`` object to "code: message (details)"."""
    err = node.get('errorDetails') if isinstance(node, dict) else None
    if not isinstance(err, dict):
        return None
    parts = [str(v) for v in (err.get('code'), err.get('message')) if v]
    text = ': '.join(parts) if parts else None
    details = err.get('details')
    if text and details:
        text = '%s (%s)' % (text, details)
    return text


def _failed_attempts(step):
    """Count failed attempts on a step and its per-entity executions."""
    def _failed(attempts):
        return sum(
            1 for a in attempts or []
            if str((a or {}).get('status') or '').lower() == 'failed')

    total = _failed(step.get('attempts'))
    for entity in step.get('entityExecutions') or []:
        total += _failed((entity or {}).get('attempts'))
    return total


def _attempt_views(attempts):
    """Project raw attempt objects to ``{number, status, error}`` dicts."""
    views = []
    for attempt in attempts or []:
        if not isinstance(attempt, dict):
            continue
        views.append({
            'number': attempt.get('attemptNumber'),
            'status': attempt.get('status'),
            'error': _error_text(attempt),
        })
    return views


def build_execution_view(document, title):
    """Build the grid view model for a runbook execution status document."""
    root = _unwrap(document)
    dep_labels = dep_utils.build_dep_labels(root)
    group_map = _entity_group_map(root)
    workstreams = []
    status_counts = {}
    for name, ws_id, steps in _iter_workstreams(root):
        rows = []
        for step in steps:
            status = _exec_status(step)
            if status:
                status_counts[str(status)] = \
                    status_counts.get(str(status), 0) + 1
            entity_execs = [e for e in step.get('entityExecutions') or []
                            if isinstance(e, dict)]
            entities = [
                EntityProgress(
                    e.get('entity') or e.get('displayName')
                    or e.get('entityId') or e.get('name'),
                    _entity_status(e),
                    status_reason=e.get('statusReason'),
                    error=_error_text(e),
                    total_attempts=(e.get('totalAttempts')
                                    or len(e.get('attempts') or [])),
                    attempts=_attempt_views(e.get('attempts')),
                    tool_status=e.get('toolReportedMigrationStatus'))
                for e in entity_execs]
            rows.append(StepRow(
                step_id=_step_id(step),
                name=_step_name(step),
                deps=dep_utils.label_deps(step, dep_labels),
                status=status,
                workload_progress=_progress_text(step),
                entities=entities,
                entity_groups=_step_groups(step, group_map),
                status_reason=step.get('statusReason'),
                error=_error_text(step),
                retry_count=_failed_attempts(step),
                attempts=_attempt_views(step.get('attempts')),
                user_comment=step.get('userComment')))
        workstreams.append(Workstream(name, rows, ws_id))

    summary = _execution_summary(root, status_counts)
    meta = [('Data source', 'executionStatus.json')]
    start_time = root.get('startTime')
    if start_time:
        meta.append(('Started', start_time))
    last_updated = root.get('lastUpdatedTime')
    if last_updated:
        meta.append(('Last updated', last_updated))
    return RunbookView(title, KIND_EXECUTION, workstreams, summary, meta=meta)


# Service-provided step aggregate counts, in display order (label, key).
_STEP_COUNT_FIELDS = (
    ('Completed', 'stepsCompleted'),
    ('In progress', 'stepsInProgress'),
    ('Awaiting action', 'stepsAwaitingUserAction'),
    ('Failed', 'stepsFailed'),
    ('Not started', 'stepsNotStarted'),
)


def _execution_summary(root, status_counts):
    """Build the summary cards for an execution.

    Prefer the service-supplied top-level step aggregates
    (``stepsCompleted`` etc.); only when the document carries none of them do
    we fall back to counting the steps ourselves.
    """
    summary = []
    overall = root.get('status') or root.get('state')
    if overall:
        summary.append(('State', overall))
    provided = [(label, root.get(key)) for label, key in _STEP_COUNT_FIELDS
                if isinstance(root.get(key), int)]
    if provided:
        summary.extend(provided)
    else:
        summary.extend(sorted(status_counts.items()))
    return summary
