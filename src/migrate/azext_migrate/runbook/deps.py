# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Shared dependency-resolution helpers for runbook definition/execution.

A runbook step declares its upstream steps through two sibling lists:

* ``prerequisite`` — hard ordering constraints, and
* ``dependsOn`` — soft/gate dependencies (e.g. approval gates).

Both are lists of objects shaped like ``{"step": "<stepId>", "mode": ...}``
(and, defensively, plain id strings). The dependency graph and the table
projection must consider *both* lists, so the merge logic lives here in one
place rather than being duplicated (and drifting) across modules.
"""


def _dep_id(dep):
    """Extract the referenced step id from one dependency entry."""
    if isinstance(dep, dict):
        return dep.get('step') or dep.get('stepId')
    if dep:
        return str(dep)
    return None


def merged_dep_ids(step):
    """Return the ordered, de-duplicated upstream step ids for ``step``.

    Merges the ``prerequisite`` and ``dependsOn`` lists (in that order),
    dropping blanks and duplicates while preserving first-seen order.
    """
    step = step or {}
    ids = []
    seen = set()
    for key in ('prerequisite', 'dependsOn'):
        for dep in step.get(key) or []:
            dep_id = _dep_id(dep)
            if dep_id and dep_id not in seen:
                seen.add(dep_id)
                ids.append(dep_id)
    return ids


def _step_id(step):
    return step.get('stepId') or step.get('id') or step.get('name')


def _step_name(step):
    return (step.get('displayName') or step.get('name')
            or step.get('stepName') or _step_id(step) or 'step')


def _iter_ws_steps(document):
    """Yield ``(workstream_name, step)`` for every step in a definition or
    execution document.

    Unwraps an execution ``properties`` envelope and covers both the grouped
    ``workstreams[].steps[]`` and flat ``steps[]`` shapes. Steps that live
    outside any workstream yield a ``None`` workstream name.
    """
    root = document or {}
    if isinstance(root, dict) and isinstance(root.get('properties'), dict):
        merged = dict(root)
        merged.update(root['properties'])
        root = merged
    if not isinstance(root, dict):
        return
    workstreams = root.get('workstreams')
    if isinstance(workstreams, list) and workstreams:
        for workstream in workstreams:
            if not isinstance(workstream, dict):
                continue
            name = (workstream.get('displayName') or workstream.get('name')
                    or workstream.get('id'))
            for step in workstream.get('steps') or []:
                if isinstance(step, dict):
                    yield name, step
        return
    for step in root.get('steps') or []:
        if isinstance(step, dict):
            yield None, step


def build_dep_labels(document):
    """Map each step id to a readable ``"Workstream:Step name"`` label.

    A dependency is stored as a step id, which is opaque to a reader. This
    builds a single lookup (one per document) so every surface -- the
    ``--output table`` views and the visualize grid -- can render dependency
    references as ``workstream:step name`` instead of the raw id. Steps
    outside any workstream map to just their display name; ids not present
    here (e.g. dangling references) fall back to the raw id via
    :func:`label_deps`.
    """
    labels = {}
    for ws_name, step in _iter_ws_steps(document):
        step_id = _step_id(step)
        if not step_id:
            continue
        name = _step_name(step)
        labels[step_id] = '%s:%s' % (ws_name, name) if ws_name else name
    return labels


def label_deps(step, labels):
    """Return ``step``'s merged dependency ids mapped through ``labels``.

    Ids missing from ``labels`` (dangling references, or a single-step
    projection with no sibling context) fall back to the raw id.
    """
    return [labels.get(dep_id, dep_id) for dep_id in merged_dep_ids(step)]
