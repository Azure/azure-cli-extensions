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

    # pylint: disable=too-few-public-methods
    def __init__(self, name, status):
        self.name = name
        self.status = status


class StepRow:
    """One row in the grid (a single runbook step)."""

    # pylint: disable=too-few-public-methods,too-many-arguments
    # pylint: disable=too-many-instance-attributes
    def __init__(self, step_id, name, deps=None, status=None,
                 workloads=None, workload_progress=None, entities=None,
                 step_ref=None, entity_names=None, prereqs=None,
                 dep_details=None):
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


def _dep_entries(raw, id_to_name):
    """Label a prerequisite/dependsOn list with resolved names and mode."""
    entries = []
    for dep in raw or []:
        if isinstance(dep, dict):
            dep_id = dep.get('step') or dep.get('stepId')
            mode = dep.get('mode')
        else:
            dep_id, mode = dep, None
        if not dep_id:
            continue
        name = id_to_name.get(dep_id, dep_id)
        entries.append('%s (%s)' % (name, mode) if mode else name)
    return entries


def build_definition_view(document, title):
    """Build the grid view model for a runbook definition document."""
    root = _unwrap(document)
    id_to_name = _step_name_map(root)
    dep_labels = dep_utils.build_dep_labels(root)
    entity_map = _entity_name_map(root)
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
                prereqs=_dep_entries(step.get('prerequisite'), id_to_name),
                dep_details=_dep_entries(step.get('dependsOn'), id_to_name)))
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
    source-declared generation timestamp (or ``None``).
    """
    metadata = root.get('metadata') if isinstance(
        root.get('metadata'), dict) else {}
    generated = metadata.get('generatedAt')
    meta = []
    versions = root.get('stepLibraryVersions')
    if isinstance(versions, dict) and versions:
        meta.append(('Runbook version', ', '.join(
            '%s %s' % (name, ver) for name, ver in sorted(versions.items()))))
    if generated:
        meta.append(('Generated', generated))
    meta.append(('Data source', 'runbook.json'))
    resource_id = root.get('runbookResourceId')
    if resource_id:
        meta.append(('Runbook resource id', resource_id))
    wave_id = metadata.get('waveId')
    if wave_id:
        meta.append(('Wave id', wave_id))
    return meta, generated


def _entity_status(entity):
    status = entity.get('status') or entity.get('state')
    if isinstance(status, dict):
        status = status.get('state') or status.get('status')
    return status


def _progress_text(step):
    """Return a "n/m completed" summary from ``entityExecutions``."""
    explicit = step.get('workloadProgress')
    if explicit is not None:
        return str(explicit)
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


def build_execution_view(document, title):
    """Build the grid view model for a runbook execution status document."""
    root = _unwrap(document)
    dep_labels = dep_utils.build_dep_labels(root)
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
                    e.get('displayName') or e.get('entityId') or e.get('name'),
                    _entity_status(e))
                for e in entity_execs]
            rows.append(StepRow(
                step_id=_step_id(step),
                name=_step_name(step),
                deps=dep_utils.label_deps(step, dep_labels),
                status=status,
                workload_progress=_progress_text(step),
                entities=entities))
        workstreams.append(Workstream(name, rows, ws_id))

    summary = []
    overall = root.get('state') or root.get('status')
    if overall:
        summary.append(('State', overall))
    summary.extend(sorted(status_counts.items()))
    meta = [('Data source', 'status.json')]
    return RunbookView(title, KIND_EXECUTION, workstreams, summary, meta=meta)
